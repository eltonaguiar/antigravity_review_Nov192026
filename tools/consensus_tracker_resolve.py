#!/usr/bin/env python3
"""Resolve open rows in consensus_tracked against their own contract.

Contract (as recorded in the table itself): LONG, TP +8%, SL -4%, max hold 14 days.

Resolution is path-based, not "close price today":
  * look at daily_prices between entry_date and entry_date+max_hold_days
  * if any high >= entry*(1+TP)  -> closed_win,  exit_reason 'TP'
  * elif any low <= entry*(1-SL) -> closed_loss, exit_reason 'SL'
  * else exit at the close on/after entry+max_hold -> closed_neutral/win/loss by sign
Using "today's price" would book a 14-day rule against a 7-month-old entry, which is
how you manufacture a fake result.

Because final_return_pct is NOT NULL DEFAULT 0, every write here sets it explicitly,
and open rows keep final_return_pct = 0 while being distinguished by status='open'.

    DB_PASS=... python3 consensus_tracker_resolve.py --apply
"""
import argparse, datetime, os, sys

try:
    import pymysql
except ImportError:
    sys.exit("pip install pymysql")


def conn():
    pw = os.environ.get("DB_PASS")
    if not pw:
        sys.exit("DB_PASS not set")
    return pymysql.connect(host=os.environ.get("DB_HOST", "mysql.50webs.com"),
                           user=os.environ.get("DB_USER", "ejaguiar1_stocks"),
                           password=pw, database=os.environ.get("DB_NAME", "ejaguiar1_stocks"),
                           connect_timeout=25, read_timeout=180, charset="utf8mb4", autocommit=False)


def window(cur, ticker, start, end):
    """Bars STRICTLY AFTER the entry date.

    The entry bar itself must never be used to hit TP/SL: an entry taken at a close
    cannot also have traded +/-8% on that same close, and including it produced
    'closed_neutral 0.000%' on every fresh row during the first dry run.
    """
    cur.execute("""SELECT trade_date, high_price, low_price, close_price FROM daily_prices
                   WHERE ticker=%s AND trade_date > %s AND trade_date <= %s ORDER BY trade_date""",
                (ticker, start, end))
    return cur.fetchall()


def resolve(cur, row, apply):
    rid, ticker, entry_date, entry = row
    entry = float(entry)
    tp, sl, hold = 8.0, 4.0, 14
    end = entry_date + datetime.timedelta(days=hold + 5)   # +5d for holidays/weekends
    bars = window(cur, ticker, entry_date, end)
    if not bars:
        stale = entry_date < (datetime.date.today() - datetime.timedelta(days=hold + 7))
        return ("skip", ticker, "no daily_prices bars in window (data gap, not immaturity)"
                if stale else "not matured - no bars after entry yet", None)
    target = entry_date + datetime.timedelta(days=hold)
    if max(b[0] for b in bars) < target:
        return ("skip", ticker, f"not matured - only {len(bars)} bar(s) since entry, target {target}", None)
    tp_px, sl_px = entry * (1 + tp / 100.0), entry * (1 - sl / 100.0)
    status = reason = None
    exit_date = exit_px = None
    for d, hi, lo, cl in bars:
        if float(hi) >= tp_px:
            status, reason, exit_date, exit_px = "closed_win", "TP", d, tp_px
            break
        if float(lo) <= sl_px:
            status, reason, exit_date, exit_px = "closed_loss", "SL", d, sl_px
            break
    if status is None:
        after = [b for b in bars if b[0] >= target] or [bars[-1]]
        d, hi, lo, cl = after[0]
        exit_date, exit_px = d, float(cl)
        r = 100.0 * (exit_px - entry) / entry
        status = "closed_win" if r > 0 else ("closed_loss" if r < 0 else "closed_neutral")
        reason = "MAX_HOLD"
    final = round(100.0 * (exit_px - entry) / entry, 4)
    if apply:
        cur.execute("""UPDATE consensus_tracked SET status=%s, exit_date=%s, exit_price=%s,
                       exit_reason=%s, final_return_pct=%s, current_price=%s, current_return_pct=%s,
                       hold_days=%s, updated_at=NOW() WHERE id=%s""",
                    (status, exit_date, round(exit_px, 4), reason, final,
                     round(exit_px, 4), final, (exit_date - entry_date).days, rid))
    return (status, ticker, f"{reason} {exit_date} exit={exit_px:.4f} final={final:+.3f}%", final)


def refresh_open(cur, apply):
    """Update current_price for rows whose window has not closed yet."""
    cur.execute("""SELECT id, ticker, entry_price FROM consensus_tracked WHERE status='open'""")
    n = 0
    for rid, ticker, entry in cur.fetchall():
        cur.execute("""SELECT trade_date, close_price, high_price, low_price FROM daily_prices
                       WHERE ticker=%s ORDER BY trade_date DESC LIMIT 1""", (ticker,))
        r = cur.fetchone()
        if not r:
            continue
        d, cl, hi, lo = r
        ret = round(100.0 * (float(cl) - float(entry)) / float(entry), 4)
        if apply:
            cur.execute("""UPDATE consensus_tracked SET current_price=%s, current_return_pct=%s,
                peak_price=GREATEST(COALESCE(peak_price,0),%s),
                trough_price=LEAST(COALESCE(trough_price,999999),%s), updated_at=NOW()
                WHERE id=%s""", (cl, ret, hi, lo, rid))
        n += 1
    return n


def snapshot_day(cur, apply):
    cur.execute("""SELECT COUNT(*), SUM(status='open'), SUM(status IN ('closed_win','closed_loss','closed_neutral')),
                   SUM(status='closed_win'), SUM(status='closed_loss'), ROUND(SUM(final_return_pct),4),
                   ROUND(AVG(CASE WHEN status LIKE 'closed%' THEN final_return_pct END),4)
                   FROM consensus_tracked""")
    n, op, closed, wins, losses, tot, avg = cur.fetchone()
    win_rate = round(100.0 * float(wins or 0) / float(closed), 2) if closed else 0.0
    if apply:
        cur.execute("""INSERT INTO consensus_performance_daily
            (track_date, open_positions, total_closed, total_wins, total_losses, win_rate,
             total_pnl_pct, portfolio_value, created_at)
            VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (int(op or 0), int(closed or 0), int(wins or 0), int(losses or 0), win_rate,
             float(tot or 0), round(10000.0 * (1 + float(tot or 0) / 100.0), 2)))
    return dict(rows=int(n), open=int(op or 0), closed=int(closed or 0), wins=int(wins or 0),
                losses=int(losses or 0), win_rate=win_rate, sum_pct=float(tot or 0), mean_pct=float(avg or 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    c = conn(); cur = c.cursor()
    cur.execute("""SELECT id, ticker, entry_date, entry_price FROM consensus_tracked
                   WHERE status='open' ORDER BY entry_date""")
    rows = cur.fetchall()
    if a.limit:
        rows = rows[:a.limit]
    print(f"open rows: {len(rows)} | mode={'APPLY' if a.apply else 'DRY-RUN'}")
    done = 0
    for r in rows:
        st, tk, note, _ = resolve(cur, r, a.apply)
        if st == "skip":
            print(f"  skip {tk}: {note}")
        else:
            done += 1
            print(f"  {st:<14} {tk:<7} {note}")
    refreshed = refresh_open(cur, a.apply)
    print(f"refreshed current_price on {refreshed} open rows; resolved {done}")
    s = snapshot_day(cur, a.apply)
    print("book:", s)
    if a.apply:
        c.commit(); print("committed")
    else:
        c.rollback(); print("rolled back (dry run)")
    c.close()


if __name__ == "__main__":
    main()
