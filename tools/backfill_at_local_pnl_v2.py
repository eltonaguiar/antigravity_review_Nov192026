#!/usr/bin/env python3
"""Backfill pnl_pct on at_local_picks rows resolved by a TP/SL touch (v2).

Honest by construction: when exit_reason says TP_HIT/SL_HIT the writer already
established which boundary was reached, so the realised return is the boundary
distance from entry. Time exits and reason-less rows are never touched - those
are where EXPIRED->WON inflation lives.

LIVE-WRITER SAFE: the table receives ~2.2k rows/min, so one 14k-row transaction
deadlocks (MySQL 1205 lock wait timeout, observed). This commits per row with a
short innodb_lock_wait_timeout, retries on contention, and skips rows that stay
locked rather than holding locks. Every change is appended to a JSONL audit file
that gets committed - no CREATE TABLE required.

Usage: DB_PASS=... python3 backfill_at_local_pnl_v2.py [--apply] [--hours 24]
"""
import argparse, datetime, json, os, sys

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")

NOW = datetime.datetime.now(datetime.timezone.utc)
REASONS = "('TP_HIT','TP','SL_HIT','SL')"

ELIGIBLE = f"""
SELECT id, symbol, direction, entry_price, take_profit, stop_loss, status, exit_reason, pnl_pct
FROM at_local_picks
WHERE id >= %s AND status IN ('WON','LOST')
  AND (pnl_pct IS NULL OR pnl_pct = 0)
  AND exit_reason IN {REASONS}
  AND entry_price IS NOT NULL AND take_profit IS NOT NULL AND stop_loss IS NOT NULL AND entry_price > 0
  AND ((direction='LONG'  AND stop_loss < entry_price AND entry_price < take_profit)
    OR (direction='SHORT' AND take_profit < entry_price AND entry_price < stop_loss))
"""


def connect():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    c = pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                        user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                        password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"),
                        autocommit=True)
    cur = c.cursor()
    cur.execute("SET SESSION innodb_lock_wait_timeout=4")
    cur.execute("SET SESSION max_execution_time=25000")
    return c, cur


def id_floor(cur, hours):
    cur.execute("SELECT MAX(id) FROM at_local_picks"); hi = cur.fetchone()[0]
    cutoff = NOW.replace(tzinfo=None) - datetime.timedelta(hours=hours)
    lo, best = 0, hi
    for _ in range(30):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        cur.execute("SELECT created_at FROM at_local_picks WHERE id >= %s ORDER BY id ASC LIMIT 1", (mid,))
        r = cur.fetchone()
        if r is None:
            hi = mid; continue
        if r[0] and r[0] >= cutoff:
            best, hi = mid, mid
        else:
            lo = mid
    return best


def compute(row):
    _id, _sym, d, e, tp, sl, st, _reason, _old = row
    e, tp, sl = float(e), float(tp), float(sl)
    exit_price = tp if st == "WON" else sl
    pnl = (exit_price - e) / e * 100.0 if d == "LONG" else (e - exit_price) / e * 100.0
    return pnl, exit_price


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--audit", default="pnl_backfill_audit.jsonl")
    a = ap.parse_args()

    c, cur = connect()
    lo = id_floor(cur, a.hours)
    cur.execute(ELIGIBLE, (lo,))
    rows = cur.fetchall()
    print(f"window last {a.hours}h (id>={lo}) | eligible: {len(rows):,}")

    todo, skipped = [], {"out_of_band": 0, "sign_error": 0}
    for r in rows:
        pnl, xp = compute(r)
        if abs(pnl) > 50: skipped["out_of_band"] += 1; continue
        if (r[6] == "WON" and pnl <= 0) or (r[6] == "LOST" and pnl >= 0): skipped["sign_error"] += 1; continue
        todo.append((r, pnl, xp))
    ps = [t[1] for t in todo]
    if ps:
        print(f"plan: {len(todo):,} rows | mean {sum(ps)/len(ps):+.3f}% | min {min(ps):+.3f}% | max {max(ps):+.3f}% | skipped {skipped}")
    if not a.apply:
        print("DRY RUN - nothing written.")
        return

    out = open(a.audit, "a", encoding="utf-8")
    written = locked = 0
    for r, pnl, xp in todo:
        for attempt in range(3):
            try:
                cur.execute("""UPDATE at_local_picks SET pnl_pct=%s, exit_price=%s
                               WHERE id=%s AND status=%s
                                 AND (pnl_pct IS NULL OR pnl_pct=0)""",
                            (round(pnl, 4), xp, r[0], r[6]))
                if cur.rowcount:
                    written += 1
                    out.write(json.dumps({"id": int(r[0]), "symbol": r[1], "dir": r[2],
                                          "status": r[6], "reason": r[7],
                                          "old": (float(r[8]) if r[8] is not None else None),
                                          "new": round(pnl, 4), "method": "tp_sl_boundary",
                                          "at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ")}) + "\n")
                break
            except Exception as e:
                if "1205" in str(e) or "Lock wait" in str(e):
                    continue
                print("  row error", r[0], str(e)[:80]); break
        else:
            locked += 1
    out.close()
    print(f"APPLIED | updated: {written:,} | left locked: {locked:,} | audit rows: {written:,} -> {a.audit}")
    c.close()


if __name__ == "__main__":
    main()
