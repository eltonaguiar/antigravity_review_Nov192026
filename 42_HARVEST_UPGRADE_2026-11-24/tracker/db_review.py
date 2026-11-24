"""Full integrity review of the pick-tracking schema. Evidence for the schema document.

Checks, in the order they matter:
  1. object inventory + row counts
  2. label reproducibility: every consensus label re-derived from its own stored counts
  3. FK integrity: no snapshot without a rule version, no mark without a pick
  4. pick status breakdown per source
  5. the honest gaps: which tables are still empty and why
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

OBJECTS = ["picktrack_picks", "picktrack_entries", "picktrack_marks", "picktrack_scores",
           "picktrack_events", "analyst_registry", "analyst_actions", "fund_lookthrough",
           "crowd_markets", "crowd_mappings", "source_run", "rule_version", "instrument",
           "consensus_snapshot", "price_bar", "pick_resolution"]


def classify(score, bs):
    if score >= 1.0 and bs >= 75:
        return "STRONG_BUY"
    if score >= 0.3 and bs >= 50:
        return "BUY"
    if score <= -1.0 and bs <= 15:
        return "STRONG_SELL"
    if score <= -0.3 and bs <= 30:
        return "SELL"
    return "HOLD"


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=15)
    cur = c.cursor()

    print("=== 1. OBJECT INVENTORY ===")
    for t in OBJECTS:
        try:
            cur.execute("SELECT COUNT(*) FROM `" + t + "`")
            print(f"  {t:22} {cur.fetchone()[0]:>7} rows")
        except Exception as e:
            print(f"  {t:22} ERROR {str(e)[:40]}")

    print("\n=== 2. LABEL REPRODUCIBILITY (the defect this schema exists to prevent) ===")
    cur.execute("""SELECT symbol_raw, consensus_score, share_buy_pct, consensus_label,
                          label_rule_version, analysts
                   FROM consensus_snapshot""")
    rows = cur.fetchall()
    mism, nullrule = [], []
    for sym, score, bs, lab, rv, n in rows:
        if rv is None:
            nullrule.append(sym)
        if score is None or bs is None or lab is None:
            continue
        if classify(float(score), float(bs)) != lab:
            mism.append(sym)
    print(f"  snapshots: {len(rows)} | re-derived from stored counts: {len(rows)-len(mism)} agree, "
          f"{len(mism)} mismatch")
    print(f"  snapshots missing label_rule_version: {len(nullrule)}")
    print(f"  distinct rule versions in use: ", end="")
    cur.execute("SELECT COUNT(DISTINCT label_rule_version) FROM consensus_snapshot")
    print(cur.fetchone()[0])

    print("\n=== 3. REFERENTIAL INTEGRITY ===")
    cur.execute("SELECT COUNT(*) FROM picktrack_marks m LEFT JOIN picktrack_picks p "
                "ON p.id = m.pick_id WHERE p.id IS NULL")
    print("  marks with no matching pick:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM consensus_snapshot WHERE label_rule_version IS NULL")
    print("  snapshots with no rule version:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM rule_version")
    print("  rule_version rows:", cur.fetchone()[0])

    print("\n=== 4. PICKS BY SOURCE AND STATUS ===")
    cur.execute("""SELECT source, COUNT(*) total,
                          SUM(status='open') open_rows,
                          SUM(status='unscored') unscored
                   FROM picktrack_picks GROUP BY source ORDER BY total DESC""")
    for r in cur.fetchall():
        print(f"  {r[0]:12} total={r[1]:>3} open={r[2] or 0:>3} unscored={r[3] or 0:>3}")

    print("\n=== 5. COVERAGE FACTS ===")
    cur.execute("SELECT COUNT(DISTINCT asset_class) FROM picktrack_picks")
    print("  distinct asset classes tracked:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM picktrack_picks WHERE symbol IS NULL")
    print("  strategy descriptors (no single symbol, kept not dropped):", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM picktrack_picks WHERE cost_bps IS NULL")
    print("  picks with no cost basis recorded (should be 0):", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM picktrack_picks WHERE benchmark IS NULL")
    print("  picks with no benchmark (cash/bar rows are legitimate):", cur.fetchone()[0])

    print("\n=== 6. KNOWN EMPTY LAYERS (honest gaps) ===")
    for t, why in [("analyst_registry", "requires paid firm-level feed; free tier is counts only"),
                   ("analyst_actions", "finnhub upgrade-downgrade HTTP 403 on free tier"),
                   ("fund_lookthrough", "ghcopilot produced 3 funds offline; not yet ingested"),
                   ("crowd_markets", "venues reachable; not yet ingested"),
                   ("price_bar", "scoring uses yfinance directly; not yet persisted")]:
        cur.execute("SELECT COUNT(*) FROM `" + t + "`")
        print(f"  {t:20} {cur.fetchone()[0]:>4} rows — {why}")
    c.close()


if __name__ == "__main__":
    main()
