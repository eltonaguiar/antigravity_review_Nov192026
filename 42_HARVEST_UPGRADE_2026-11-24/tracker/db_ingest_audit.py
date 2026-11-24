"""Ingest every ACTIVE pick from findtorontoevents.ca/audit into the tracker.

Source: /audit/data/dashboard_data.json -> picks.active_raw (4,210 rows as of 2026-11-24).
Each row already carries entry_price and current_price, so these picks can be marked immediately
without any market lookup — which is why they are worth ingesting first.

Mapping notes that matter:
  * published_at comes from entry_time/timestamp, NOT from ingest time.
  * entry_mode is 'already_open': the pick was already live when we started tracking, so we cannot
    claim a next-open fill. Recording it honestly matters — a later reader must know this row was
    joined mid-flight, not entered by us.
  * pnl_pct from the feed is gross; net subtracts the round-turn cost, same rule as every other row.
  * 'trust_label' and 'forward_validated' are copied into notes so a low-trust pick cannot be
    mistaken for an endorsed one.
"""
import json
import os
import sys
from datetime import datetime

import pymysql

DB = "ejaguiar1_stocks"
FEED = os.path.expanduser("~/dashboard_data.json")
COST_BPS = 26.0

BENCH = {"CRYPTO": "BTC-USD", "EQUITY": "SPY", "STOCK": "SPY", "ETF": "SPY",
         "FOREX": "CASH", "BOND": "CASH", "COMMODITY": "CASH", "FUTURES": "CASH"}


def main():
    d = json.load(open(FEED, encoding="utf-8"))
    picks = d.get("picks", {})
    active_raw = picks.get("active_raw") or []
    display = {p.get("id") for p in (picks.get("active") or [])}
    print(f"feed generated_at {d.get('generated_at')} | active_raw {len(active_raw)} | display {len(display)}")

    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    cur.execute("INSERT INTO source_run (source_system, endpoint, http_status, rows_returned, "
                "started_at, finished_at) VALUES (%s,%s,%s,%s,%s,%s)",
                ("audit_dashboard", "/audit/data/dashboard_data.json (picks.active_raw)",
                 200, len(active_raw), datetime.utcnow(), datetime.utcnow()))
    run_id = cur.lastrowid

    ins_pick = """INSERT IGNORE INTO picktrack_picks
        (id, source, source_detail, published_at, symbol, asset_class, direction, rule,
         conviction, entry_rule, cost_bps, benchmark, status, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    ins_entry = """INSERT IGNORE INTO picktrack_entries
        (pick_id, entry_mode, entry_date, entry_price) VALUES (%s,%s,%s,%s)"""
    ins_mark = """INSERT INTO picktrack_marks
        (pick_id, mark_date, last_price, raw_pct, net_bps, benchmark_net_bps, excess_bps, days_held)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE last_price=VALUES(last_price), raw_pct=VALUES(raw_pct),
          net_bps=VALUES(net_bps), days_held=VALUES(days_held)"""

    n_pick = n_entry = n_mark = skipped = 0
    by_class, by_tf = {}, {}
    for p in active_raw:
        pid = ("audit:" + str(p.get("id") or ""))[:80]
        sym = p.get("symbol")
        ts = (p.get("entry_time") or p.get("timestamp") or "")[:19].replace("T", " ")
        if not sym or not ts:
            skipped += 1
            continue
        cls = (p.get("asset_class") or "UNKNOWN").upper()
        tf = p.get("trade_timeframe") or "?"
        by_class[cls] = by_class.get(cls, 0) + 1
        by_tf[tf] = by_tf.get(tf, 0) + 1

        # The feed distinguishes OPEN from expired. Forcing every row to 'open' would have
        # counted 3,618 expired picks as live positions - a 7.5x overstatement of the book.
        # Kilo measured the exact split: 562 OPEN, 3,618 EXPIRED, 19 SL_HIT, 11 TP_HIT.
        # Terminal hits are resolved, not expired-and-unknown, and must not be counted as open.
        feed_status = (p.get("status") or "").upper()
        if feed_status == "OPEN":
            status = "open"
        elif feed_status in ("SL_HIT", "TP_HIT"):
            status = "closed"
        else:
            status = "expired"
        note = (f"timeframe={tf} feed_status={feed_status or '?'} trust={p.get('trust_label')} "
                f"score={p.get('trust_score')} forward_validated={p.get('forward_validated')} "
                f"display={p.get('id') in display}")
        cur.execute(ins_pick, (pid, "audit", f"{p.get('system') or ''}/{p.get('source') or ''}"[:200],
                               ts, sym, cls, (p.get("direction") or "").lower(),
                               (p.get("strategy") or "")[:64], p.get("score"), "already_open",
                               COST_BPS, BENCH.get(cls, "CASH"), status, note))
        n_pick += cur.rowcount

        ep = p.get("entry_price")
        if ep:
            cur.execute(ins_entry, (pid, "already_open", ts[:10], ep))
            n_entry += cur.rowcount

        cp, pnl = p.get("current_price"), p.get("pnl_pct")
        if ep and cp and pnl is not None:
            net = float(pnl) * 100 - COST_BPS
            cur.execute(ins_mark, (pid, datetime.utcnow().date(), cp, pnl, net, None, None,
                                   p.get("age_hours")))
            n_mark += 1

    cur.execute("SELECT COUNT(*) FROM picktrack_picks")
    total = cur.fetchone()[0]
    cur.execute("SELECT source, COUNT(*) FROM picktrack_picks GROUP BY source ORDER BY 2 DESC")
    src = cur.fetchall()
    c.close()

    print(f"inserted picks {n_pick} | entries {n_entry} | marks {n_mark} | skipped {skipped}")
    print("table now:", total, "rows")
    print("by source:", dict(src))
    print("by asset class:", by_class)
    print("by timeframe:", by_tf)


if __name__ == "__main__":
    main()
