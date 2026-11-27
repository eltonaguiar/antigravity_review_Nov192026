#!/usr/bin/env python3
"""Backfill pnl_pct on at_local_picks rows that were resolved by a TP/SL touch.

Why this is honest: on a TP_HIT / SL_HIT the writer already knows which boundary
was touched, so the realised return is the boundary distance from entry:
    LONG  WON  -> (take_profit - entry)/entry
    LONG  LOST -> (stop_loss  - entry)/entry
    SHORT WON  -> (entry - take_profit)/entry
    SHORT LOST -> (entry - stop_loss)/entry
It is NOT applied to time exits: `exit_reason IN ('TIME','TIME_EXIT','EXPIRED')`
or a resolved row with no reason is left alone, because there the outcome does not
imply the boundary was reached (that is exactly the EXPIRED->WON inflation).

Guards:
  * status IN ('WON','LOST') and (pnl_pct IS NULL OR pnl_pct = 0)
  * exit_reason IN ('TP_HIT','TP','SL_HIT','SL')
  * entry/take_profit/stop_loss all present, entry > 0
  * coherent sides: LONG stop<entry<tp ; SHORT tp<entry<stop
  * |computed| <= 50 (beyond that is an instrument error, not a win)

Every write is logged to at_local_pnl_backfill_log with the previous value and the
method, so the change is auditable and reversible by run_id.

Usage: DB_PASS=... python3 backfill_at_local_pnl.py [--apply] [--hours 24]
"""
import argparse, datetime, os, sys

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")

NOW = datetime.datetime.now(datetime.timezone.utc)
REASONS = ("TP_HIT", "TP", "SL_HIT", "SL")


def connect():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    return pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                           user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                           password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"))


def id_floor(cur, hours):
    cur.execute("SELECT MAX(id) FROM at_local_picks")
    hi = cur.fetchone()[0]
    cutoff = NOW.replace(tzinfo=None) - datetime.timedelta(hours=hours)
    lo, best = 0, hi
    for _ in range(30):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        cur.execute("SELECT created_at FROM at_local_picks WHERE id >= %s ORDER BY id ASC LIMIT 1", (mid,))
        r = cur.fetchone()
        if r is None:
            hi = mid
            continue
        if r[0] and r[0] >= cutoff:
            best, hi = mid, mid
        else:
            lo = mid
    return best


ELIGIBLE = """
SELECT id, symbol, direction, entry_price, take_profit, stop_loss, status, exit_reason, pnl_pct
FROM at_local_picks
WHERE id >= %s AND status IN ('WON','LOST')
  AND (pnl_pct IS NULL OR pnl_pct = 0)
  AND exit_reason IN ('TP_HIT','TP','SL_HIT','SL')
  AND entry_price IS NOT NULL AND take_profit IS NOT NULL AND stop_loss IS NOT NULL
  AND entry_price > 0
  AND ((direction='LONG'  AND stop_loss < entry_price AND entry_price < take_profit)
    OR (direction='SHORT' AND take_profit < entry_price AND entry_price < stop_loss))
"""


def boundary(row):
    _id, sym, d, e, tp, sl, st, reason, _old = row
    e, tp, sl = float(e), float(tp), float(sl)
    won = st == "WON"
    exit_price = tp if won else sl
    pnl = (exit_price - e) / e * 100.0 if d == "LONG" else (e - exit_price) / e * 100.0
    return pnl, exit_price


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()
    c = connect(); cur = c.cursor()
    cur.execute("SET SESSION max_execution_time=25000")
    lo = id_floor(cur, a.hours)
    cur.execute(ELIGIBLE, (lo,))
    rows = cur.fetchall()
    print(f"window: last {a.hours}h (id >= {lo}) | eligible rows: {len(rows):,}")

    planned, skipped = [], {"out_of_band": 0, "sign_error": 0}
    for r in rows:
        pnl, exit_price = boundary(r)
        if abs(pnl) > 50:
            skipped["out_of_band"] += 1; continue
        if (r[6] == "WON" and pnl <= 0) or (r[6] == "LOST" and pnl >= 0):
            skipped["sign_error"] += 1; continue
        planned.append((pnl, exit_price, r))
    print(f"would write: {len(planned):,} | skipped: {skipped}")
    if planned:
        ps = [p[0] for p in planned]
        print(f"computed pnl: mean {sum(ps)/len(ps):+.3f}%  min {min(ps):+.3f}%  max {max(ps):+.3f}%")
        by = {}
        for pnl, _x, r in planned:
            by.setdefault(r[6], []).append(pnl)
        for k, v in by.items():
            print(f"  {k}: n={len(v):,} mean {sum(v)/len(v):+.3f}%")
    if not a.apply:
        print("DRY RUN - nothing written. Re-run with --apply.")
        return

    cur.execute("""CREATE TABLE IF NOT EXISTS at_local_pnl_backfill_log (
        run_id VARCHAR(32) NOT NULL, pick_id BIGINT NOT NULL, symbol VARCHAR(24),
        status VARCHAR(12), exit_reason VARCHAR(16), old_pnl DECIMAL(12,4),
        new_pnl DECIMAL(12,4), exit_price DECIMAL(18,6), method VARCHAR(32),
        written_at DATETIME, PRIMARY KEY (run_id, pick_id))""")
    run_id = NOW.strftime("%Y%m%dT%H%M%SZ")
    written = 0
    for pnl, exit_price, r in planned:
        cur.execute("""UPDATE at_local_picks SET pnl_pct=%s, exit_price=%s
                       WHERE id=%s AND (pnl_pct IS NULL OR pnl_pct=0)""", (round(pnl, 4), exit_price, r[0]))
        written += cur.rowcount
        cur.execute("""INSERT IGNORE INTO at_local_pnl_backfill_log
                       (run_id,pick_id,symbol,status,exit_reason,old_pnl,new_pnl,exit_price,method,written_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (run_id, r[0], r[1], r[6], r[7], r[8], round(pnl, 4), exit_price, "tp_sl_boundary", NOW))
    c.commit()
    print(f"APPLIED run_id={run_id} | rows updated: {written:,} | log rows written to at_local_pnl_backfill_log")
    c.close()


if __name__ == "__main__":
    main()
