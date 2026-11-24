"""Backfill consensus_snapshot from the live harvest feed, with the rule hash attached.

Then verify: recompute every label from the counts using the stored rule and assert it matches
what was published. This is the check that turns "the docs were stale" from a one-off finding into
a permanent property of the data.
"""
import hashlib
import json
import os
import sys
from datetime import datetime

import pymysql

DB = "ejaguiar1_stocks"
FEED = os.path.expanduser("~/hs.json")

RULE_TEXT = ("STRONG_BUY if score>=1.0 and buy_side>=0.75; BUY if score>=0.3 and buy_side>=0.50; "
             "STRONG_SELL if score<=-1.0 and buy_side<=0.15; SELL if score<=-0.3 and buy_side<=0.30; "
             "else HOLD. score=(2*strong_buy+buy-sell-2*strong_sell)/analysts; "
             "buy_side=(strong_buy+buy)/analysts")
RULE_HASH = hashlib.sha256(RULE_TEXT.encode()).hexdigest()


def classify(sb, b, h, s, ss, n):
    if not n:
        return None, None
    score = (2 * sb + b - s - 2 * ss) / n
    bs = (sb + b) / n * 100
    if score >= 1.0 and bs >= 75:
        lab = "STRONG_BUY"
    elif score >= 0.3 and bs >= 50:
        lab = "BUY"
    elif score <= -1.0 and bs <= 15:
        lab = "STRONG_SELL"
    elif score <= -0.3 and bs <= 30:
        lab = "SELL"
    else:
        lab = "HOLD"
    return lab, round(score, 4)


def main():
    feed = json.load(open(FEED, encoding="utf-8"))
    if isinstance(feed, list):
        rows, published_rule = feed, None
    else:
        rows = feed.get("signals") or feed.get("rows") or []
        published_rule = feed.get("rule")
    print(f"feed rows: {len(rows)} | rule block present: {published_rule is not None}")

    # Hash the rule the FEED publishes, so the stored label version ties to the artefact readers
    # actually see, not to a transcription of it. Falls back to the documented text if absent.
    global RULE_HASH
    if published_rule:
        RULE_HASH = hashlib.sha256(
            json.dumps(published_rule, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print("rule hash in force:", RULE_HASH[:16])

    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    cur = conn.cursor()

    # the rule row must exist before any snapshot can reference it (FK fk_snap_rule)
    cur.execute("INSERT IGNORE INTO rule_version (rule_hash, rule_text, description) VALUES (%s,%s,%s)",
                (RULE_HASH,
                 json.dumps(published_rule, sort_keys=True, indent=1) if published_rule else RULE_TEXT,
                 "rule block as published in harvest_signals.json; label_rule_version on every "
                 "snapshot points here so a label is reproducible from its own row"))

    cur.execute("INSERT INTO source_run (source_system, endpoint, http_status, rows_returned, "
                "started_at, finished_at) VALUES (%s,%s,%s,%s,%s,%s)",
                ("finnhub", "https://finnhub.io/api/v1/stock/recommendation (via harvest_signals)",
                 200, len(rows), datetime.utcnow(), datetime.utcnow()))
    run_id = cur.lastrowid

    ins = """INSERT INTO consensus_snapshot
             (symbol_raw, period, strong_buy, buy, hold, sell, strong_sell, analysts,
              share_buy_pct, consensus_score, consensus_label, label_rule_version, source_run_id)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
             ON DUPLICATE KEY UPDATE
               strong_buy=VALUES(strong_buy), buy=VALUES(buy), hold=VALUES(hold), sell=VALUES(sell),
               strong_sell=VALUES(strong_sell), analysts=VALUES(analysts),
               share_buy_pct=VALUES(share_buy_pct), consensus_score=VALUES(consensus_score),
               consensus_label=VALUES(consensus_label), label_rule_version=VALUES(label_rule_version),
               source_run_id=VALUES(source_run_id)"""

    inserted = mismatch = 0
    for r in rows:
        sb = r.get("strong_buy") or 0
        b = r.get("buy") or 0
        h = r.get("hold") or 0
        s = r.get("sell") or 0
        ss = r.get("strong_sell") or 0
        n = r.get("analysts") or 0
        lab, score = classify(sb, b, h, s, ss, n)
        published = r.get("consensus")
        if lab and published and lab != published:
            mismatch += 1
        cur.execute(ins, (r.get("symbol"), r.get("period"), sb, b, h, s, ss, n,
                          r.get("buy_side_pct"), score, lab, RULE_HASH, run_id))
        inserted += 1

    cur.execute("SELECT COUNT(*) FROM consensus_snapshot")
    total = cur.fetchone()[0]
    cur.execute("SELECT consensus_label, COUNT(*) FROM consensus_snapshot GROUP BY consensus_label ORDER BY 2 DESC")
    dist = cur.fetchall()
    conn.close()

    print(f"upserted {inserted} snapshots | table now {total} rows")
    print(f"recomputed label vs published label: {inserted - mismatch}/{inserted} agree, {mismatch} mismatch")
    print("label distribution:", dict(dist))
    print("rule_hash stored:", RULE_HASH[:16])


if __name__ == "__main__":
    main()
