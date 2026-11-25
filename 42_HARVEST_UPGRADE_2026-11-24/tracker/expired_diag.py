#!/usr/bin/env python3
"""expired_diag.py - the three distinguishing queries an independent model asked for."""
import os
import pymysql

PW = [l.strip() for l in open(os.path.expanduser("~/dbpasses.txt"), encoding="utf-8",
                              errors="replace").read().splitlines()][82]
c = pymysql.connect(host="mysql.50webs.com", user="ejaguiar1_stocks", password=PW,
                    database="ejaguiar1_stocks", connect_timeout=30)
cur = c.cursor()


def show(title, sql, args=None):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    try:
        cur.execute(sql, args or ())
        rows = cur.fetchall()
        if not rows:
            print("  (no rows)")
        for r in rows:
            print("  " + " | ".join(str(x)[:34] for x in r))
        return rows
    except Exception as e:
        print("  ERROR:", str(e)[:130])
        return []


show("Q1  zeros by resolver_version - one bad script, or systemic?",
     """SELECT resolver_version, COUNT(*) n,
               SUM(pnl_pct=0) zeros,
               ROUND(100*SUM(pnl_pct=0)/COUNT(*),1) pct_zero,
               SUM(resolution_method=%s) time_expired
        FROM at_pick_outcomes GROUP BY resolver_version ORDER BY n DESC LIMIT 10""",
     ("TIME_EXPIRED",))

show("Q1b zeros by resolution_method",
     """SELECT resolution_method, COUNT(*) n, SUM(pnl_pct=0) zeros,
               ROUND(100*SUM(pnl_pct=0)/COUNT(*),1) pct_zero
        FROM at_pick_outcomes GROUP BY resolution_method ORDER BY n DESC LIMIT 10""")

show("Q2  resolved_at coverage by status",
     """SELECT status, COUNT(*) n, SUM(resolved_at IS NULL) null_ts,
               COUNT(*)-SUM(resolved_at IS NULL) has_ts
        FROM at_pick_outcomes GROUP BY status ORDER BY n DESC""")

print("\n" + "=" * 78)
print("Q2b can pick_id join to a parent table that carries entry dates?")
print("=" * 78)
for tbl in ("trading_picks", "at_raw_picks", "at_local_picks", "at_signal_outcomes"):
    try:
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema=%s AND table_name=%s""",
                    ("ejaguiar1_stocks", tbl))
        cols = [x[0] for x in cur.fetchall()]
        has_pid = "pick_id" in cols
        dcols = [x for x in cols
                 if any(k in x.lower() for k in ("date", "created", "entry", "expir", "hold", "ts"))]
        cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
        n = cur.fetchone()[0]
        print(f"  {tbl:<22} rows={n:<12,} pick_id={has_pid}  date-cols={dcols[:6]}")
        if has_pid:
            cur.execute(f"""SELECT COUNT(*) FROM at_pick_outcomes o
                            LEFT JOIN `{tbl}` p ON p.pick_id = o.pick_id
                            WHERE p.pick_id IS NULL""")
            orph = cur.fetchone()[0]
            cur.execute(f"""SELECT COUNT(*) FROM at_pick_outcomes o
                            INNER JOIN `{tbl}` p ON p.pick_id = o.pick_id""")
            matched = cur.fetchone()[0]
            print(f"     -> matched {matched:,} / orphaned {orph:,} of 63,792")
    except Exception as e:
        print(f"  {tbl:<22} ERR {str(e)[:70]}")

show("Q3  what does trading_picks say about the 31,421 timed-out picks?",
     """SELECT exit_reason, COUNT(*) n, ROUND(AVG(entry_price),4) avg_entry,
               SUM(take_profit IS NOT NULL AND take_profit<>0) has_tp,
               SUM(stop_loss IS NOT NULL AND stop_loss<>0) has_sl
        FROM trading_picks GROUP BY exit_reason ORDER BY n DESC LIMIT 8""")

c.close()
