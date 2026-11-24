"""Make risk explicit per pick (2026-11-24).

Before this script: `risk_profile` existed with 0 rows and `picktrack_picks` had no profile column,
so "risk profile" was a name in a schema, not a fact about any pick. This script makes it a fact.

Three profiles, each with numbers rather than adjectives. The numbers are the same ones a reader
would need to size a position, so the page can show them without translation:

  CONSERVATIVE 0.25% of equity risked per trade, 5 concurrent positions max, portfolio halt at 10% drawdown
  MODERATE     0.50% per trade, 10 concurrent, halt at 15%
  AGGRESSIVE   1.00% per trade, 20 concurrent, halt at 25%

Assignment is deterministic from the asset class, so any reader can recompute it:
  ETF, BOND, CASH                     -> CONSERVATIVE (fund wrappers, low idiosyncratic risk)
  EQUITY, STOCK, FOREX, INDEX         -> MODERATE
  CRYPTO, COMMODITY, FUTURES, MEME    -> AGGRESSIVE (gap risk, overnight risk, no circuit breakers)

Per-pick stop and target come from the source feed where present, so stop distance and reward:risk
are measured, not assumed. Where a pick carries no stop, stop_pct stays NULL rather than being
invented - a NULL here is information (the pick is unbounded), not a gap to be filled.
"""
import json
import os
import sys
from collections import Counter

import pymysql

DB = "ejaguiar1_stocks"
FEED = os.path.expanduser("~/dashboard_data.json")

PROFILES = [
    ("CONSERVATIVE", "Conservative",
     "0.25% of equity risked per trade, max 5 concurrent positions, halt at 10% portfolio drawdown.",
     "Slow bleed from many small losses that each look acceptable alone."),
    ("MODERATE", "Moderate",
     "0.50% of equity risked per trade, max 10 concurrent positions, halt at 15% portfolio drawdown.",
     "Correlated positions that behave as one large bet when the market moves as a block."),
    ("AGGRESSIVE", "Aggressive",
     "1.00% of equity risked per trade, max 20 concurrent positions, halt at 25% portfolio drawdown.",
     "Gap risk: the exit price you planned is not available, so a 1% risk becomes 8% overnight."),
]

CLASS_PROFILE = {
    "ETF": "CONSERVATIVE", "BOND": "CONSERVATIVE", "CASH": "CONSERVATIVE",
    "EQUITY": "MODERATE", "STOCK": "MODERATE", "FOREX": "MODERATE", "INDEX": "MODERATE",
    "CRYPTO": "AGGRESSIVE", "COMMODITY": "AGGRESSIVE", "FUTURES": "AGGRESSIVE",
    "MEME": "AGGRESSIVE", "PENNY_STOCK": "AGGRESSIVE", "SPORTS": "AGGRESSIVE",
}
RISK_PCT = {"CONSERVATIVE": 0.25, "MODERATE": 0.50, "AGGRESSIVE": 1.00}
MAX_POS = {"CONSERVATIVE": 5, "MODERATE": 10, "AGGRESSIVE": 20}
MAX_DD = {"CONSERVATIVE": 10.0, "MODERATE": 15.0, "AGGRESSIVE": 25.0}


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    # 1. give the profile table real numbers
    # The table shipped with only code/label/description/primary_failure - no numeric limits at all,
    # which is why "risk profile" could not be acted on. Add the numbers first.
    for col, ddl in [
        ("risk_pct_per_trade", "ALTER TABLE risk_profile ADD COLUMN risk_pct_per_trade DECIMAL(6,3) NULL"),
        ("max_concurrent",     "ALTER TABLE risk_profile ADD COLUMN max_concurrent INT NULL"),
        ("max_drawdown_pct",   "ALTER TABLE risk_profile ADD COLUMN max_drawdown_pct DECIMAL(6,2) NULL"),
    ]:
        cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                       WHERE table_schema=%s AND table_name='risk_profile' AND column_name=%s""",
                    (DB, col))
        if cur.fetchone()[0]:
            print(f"risk_profile.{col} already present")
        else:
            cur.execute(ddl)
            print(f"risk_profile.{col} added")
    cur.execute("""SHOW COLUMNS FROM risk_profile""")
    cols = [r[0] for r in cur.fetchall()]
    for code, label, desc, failure in PROFILES:
        cur.execute("DELETE FROM risk_profile WHERE code=%s", (code,))
        cur.execute(f"""INSERT INTO risk_profile ({', '.join(cols)})
                        VALUES ({', '.join(['%s'] * len(cols))})""",
                    tuple({"code": code, "label": label, "description": desc,
                           "primary_failure": failure,
                           "risk_pct_per_trade": RISK_PCT[code],
                           "max_concurrent": MAX_POS[code],
                           "max_drawdown_pct": MAX_DD[code]}.get(k) for k in cols))
    cur.execute("SELECT COUNT(*) FROM risk_profile")
    print("risk_profile rows:", cur.fetchone()[0])

    # 2. per-pick columns
    for col, ddl in [
        ("profile_code", "ALTER TABLE picktrack_picks ADD COLUMN profile_code VARCHAR(16) NULL"),
        ("stop_price",   "ALTER TABLE picktrack_picks ADD COLUMN stop_price DECIMAL(18,6) NULL"),
        ("target_price", "ALTER TABLE picktrack_picks ADD COLUMN target_price DECIMAL(18,6) NULL"),
        ("stop_pct",     "ALTER TABLE picktrack_picks ADD COLUMN stop_pct DECIMAL(10,4) NULL"),
        ("reward_risk",  "ALTER TABLE picktrack_picks ADD COLUMN reward_risk DECIMAL(10,4) NULL"),
    ]:
        cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                       WHERE table_schema=%s AND table_name='picktrack_picks' AND column_name=%s""",
                    (DB, col))
        if cur.fetchone()[0]:
            print(f"column {col:13} already present")
        else:
            cur.execute(ddl)
            print(f"column {col:13} added")

    # 3. attach stop/target from the feed, and the profile from the rule
    feed = {}
    if os.path.exists(FEED):
        d = json.load(open(FEED, encoding="utf-8"))
        for p in d.get("picks", {}).get("active_raw", []):
            feed[("audit:" + str(p.get("id")))[:80]] = p
    print("feed rows available:", len(feed))

    updated = Counter()
    for pid, p in feed.items():
        cls = (p.get("asset_class") or "").upper()
        prof = CLASS_PROFILE.get(cls, "MODERATE")
        entry, stop, tgt = p.get("entry_price"), p.get("stop_loss"), p.get("take_profit")
        stop_pct = rr = None
        try:
            if entry and stop and float(entry) != 0:
                stop_pct = abs(float(entry) - float(stop)) / float(entry) * 100
                if tgt:
                    rr = abs(float(tgt) - float(entry)) / abs(float(entry) - float(stop))
        except (TypeError, ValueError, ZeroDivisionError):
            pass
        cur.execute("""UPDATE picktrack_picks
                       SET profile_code=%s, stop_price=%s, target_price=%s,
                           stop_pct=%s, reward_risk=%s
                       WHERE id=%s""",
                    (prof, stop, tgt, stop_pct, rr, pid))
        if cur.rowcount:
            updated[prof] += cur.rowcount
    print("profile rows updated:", dict(updated))

    # unpicked rows still need a profile, derived from their own asset_class
    for cls, prof in CLASS_PROFILE.items():
        cur.execute("UPDATE picktrack_picks SET profile_code=%s WHERE asset_class=%s AND profile_code IS NULL",
                    (prof, cls))
    cur.execute("UPDATE picktrack_picks SET profile_code='MODERATE' WHERE profile_code IS NULL")

    # 4. a per-pick risk view a reader can actually check
    cur.execute("""CREATE OR REPLACE VIEW v_pick_risk AS
        SELECT p.id AS pick_id, p.symbol, p.asset_class, p.direction, p.status,
               p.published_at, p.profile_code, r.label AS profile_label,
               r.risk_pct_per_trade, r.max_concurrent, r.max_drawdown_pct,
               p.stop_price, p.target_price,
               ROUND(p.stop_pct, 2) AS stop_distance_pct,
               ROUND(p.reward_risk, 2) AS reward_risk_ratio,
               ROUND(r.risk_pct_per_trade / NULLIF(p.stop_pct, 0) * 100, 1) AS position_size_pct_of_equity,
               CASE WHEN p.stop_pct IS NULL THEN 'UNBOUNDED - no stop supplied by source'
                    WHEN p.stop_pct > 15 THEN 'WIDE - a normal stop would be a large loss'
                    WHEN p.reward_risk IS NOT NULL AND p.reward_risk < 1 THEN 'POOR PAYOFF - risking more than the target'
                    ELSE 'BOUNDED' END AS risk_flag
        FROM picktrack_picks p
        LEFT JOIN risk_profile r ON r.code = p.profile_code""")

    cur.execute("SELECT profile_code, COUNT(*) FROM picktrack_picks GROUP BY profile_code")
    print("\nprofile distribution:", dict(cur.fetchall()))
    cur.execute("SELECT risk_flag, COUNT(*) FROM v_pick_risk GROUP BY risk_flag ORDER BY 2 DESC")
    print("risk flags:", dict(cur.fetchall()))
    cur.execute("""SELECT COUNT(*) FROM picktrack_picks WHERE status='open'""")
    n_open = cur.fetchone()[0]
    cur.execute("""SELECT risk_flag, COUNT(*) FROM v_pick_risk WHERE status='open' GROUP BY risk_flag ORDER BY 2 DESC""")
    print(f"open picks ({n_open}) by risk flag:", dict(cur.fetchall()))
    cur.execute("""SELECT symbol, asset_class, profile_code, stop_distance_pct, reward_risk_ratio,
                          position_size_pct_of_equity, risk_flag
                   FROM v_pick_risk WHERE status='open' AND stop_distance_pct IS NOT NULL
                   ORDER BY stop_distance_pct DESC LIMIT 3""")
    print("\nwidest open stops:")
    for r in cur.fetchall():
        print("  ", r)
    c.close()


if __name__ == "__main__":
    main()
