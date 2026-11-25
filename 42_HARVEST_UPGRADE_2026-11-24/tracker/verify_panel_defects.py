#!/usr/bin/env python3
"""verify_panel_defects.py - check each claimed defect against the live schema/data.

The panel produced 10 candidate defects. Agreement between a model and itself is not
corroboration, so each one gets tested here or dropped.
"""
import os
import pymysql

PW = [l.strip() for l in open(os.path.expanduser("~/dbpasses.txt"), encoding="utf-8",
                              errors="replace").read().splitlines()][82]
c = pymysql.connect(host="mysql.50webs.com", user="ejaguiar1_stocks", password=PW,
                    database="ejaguiar1_stocks", connect_timeout=30)
cur = c.cursor()


def q(sql, a=None):
    try:
        cur.execute(sql, a or ())
        return cur.fetchall()
    except Exception as e:
        return [("ERR", str(e)[:110])]


print("=" * 78)
print("D1  does trading_picks have asset_class?  (panel said NO -> my SQL fails)")
print("=" * 78)
cols = [r[0] for r in q("""SELECT column_name FROM information_schema.columns
                           WHERE table_schema=%s AND table_name='trading_picks'""",
                        ("ejaguiar1_stocks",))]
print(f"  columns: {cols}")
print(f"  asset_class present: {'asset_class' in cols}   -> { 'DEFECT CONFIRMED' if 'asset_class' not in cols else 'panel wrong'}")

print("\n" + "=" * 78)
print("D9  is trading_picks.id unique?  (fan-out would inflate n and the mean)")
print("=" * 78)
r = q("SELECT COUNT(*), COUNT(DISTINCT id) FROM trading_picks")
print(f"  rows={r[0][0]:,}  distinct id={r[0][1]:,}  -> {'UNIQUE' if r[0][0]==r[0][1] else 'DUPLICATES -> join fans out'}")

print("\n" + "=" * 78)
print("D7  can RESOLVE_FAILED rows be recomputed from exit_price / entry_price?")
print("=" * 78)
r = q("""SELECT COUNT(*) n,
                SUM(exit_price IS NOT NULL AND exit_price<>0) has_exit,
                SUM(entry_price IS NOT NULL AND entry_price<>0) has_entry,
                SUM(pnl_pct IS NULL OR pnl_pct=0) pnl_dead
         FROM trading_picks WHERE exit_reason='RESOLVE_FAILED_MAX_RETRIES'""")
n, he, hn, dead = r[0]
print(f"  n={n}  has_exit_price={he}  has_entry_price={hn}  pnl dead/null={dead}")
print(f"  -> computable from prices: {'YES' if he and hn else 'NO'}")

print("\n" + "=" * 78)
print("THE REAL TEST: where BOTH tables have a non-zero pnl, do they AGREE?")
print("=" * 78)
r = q("""SELECT COUNT(*) n,
                SUM(ABS(o.pnl_pct - t.pnl_pct) < 0.000001) agree,
                SUM(ABS(o.pnl_pct - t.pnl_pct) >= 0.000001) disagree,
                ROUND(AVG(o.pnl_pct),4) mean_o, ROUND(AVG(t.pnl_pct),4) mean_t,
                ROUND(MAX(ABS(o.pnl_pct-t.pnl_pct)),4) max_gap
         FROM at_pick_outcomes o
         JOIN trading_picks t ON t.id = o.pick_id
         WHERE o.pnl_pct <> 0 AND t.pnl_pct IS NOT NULL AND t.pnl_pct <> 0""")
n, ag, dis, mo, mt, gap = r[0]
print(f"  both non-zero: n={n:,}  agree={ag:,}  disagree={dis:,}  max gap={gap}")
if n:
    print(f"  mean from outcome table {mo}   mean from parent {mt}")
    print(f"  share disagreeing: {100*(dis or 0)/n:.2f}%")

print("\n" + "=" * 78)
print("D6  how biased is the dropped set? compare joined vs unjoined EXPIRED")
print("=" * 78)
r = q("""SELECT (t.id IS NOT NULL) AS joined, COUNT(*) n,
                ROUND(AVG(o.pnl_pct),4) mean_o_pnl,
                SUM(o.pnl_pct<>0) nonzero_in_o
         FROM at_pick_outcomes o
         LEFT JOIN trading_picks t ON t.id = o.pick_id
         WHERE o.status='EXPIRED' GROUP BY 1""")
for joined, n, m, nz in r:
    print(f"  joined={bool(joined)}  n={n:,}  mean_o_pnl={m}  non-zero in outcome={nz}")

print("\n" + "=" * 78)
print("D5  is resolver_version correlated with asset_class? (confound test)")
print("=" * 78)
r = q("""SELECT asset_class,
                SUM(resolver_version LIKE 'backfill%%') backfill_rows,
                SUM(resolver_version NOT LIKE 'backfill%%') other_rows,
                COUNT(*) n,
                ROUND(100*SUM(resolver_version LIKE 'backfill%%')/COUNT(*),1) pct_backfill
         FROM at_pick_outcomes GROUP BY asset_class HAVING n>=100 ORDER BY n DESC LIMIT 10""")
for ac, bf, ot, n, pct in r:
    print(f"  {str(ac)[:12]:<12} n={n:<7} backfill={bf:<7} other={ot:<7} ({pct}% backfill)")

print("\n" + "=" * 78)
print("CORRECTED per-class table, stratifying by resolver lineage and using prices")
print("=" * 78)
sql = """
SELECT o.asset_class,
       COUNT(*) n,
       ROUND(AVG(
         CASE WHEN o.pnl_pct <> 0 THEN o.pnl_pct
              WHEN t.pnl_pct IS NOT NULL AND t.pnl_pct <> 0 THEN t.pnl_pct
              WHEN t.exit_price IS NOT NULL AND t.exit_price <> 0
               AND t.entry_price IS NOT NULL AND t.entry_price <> 0
              THEN (t.exit_price - t.entry_price) / t.entry_price
              ELSE NULL END), 2) mean_pct,
       SUM(CASE WHEN o.pnl_pct <> 0 THEN 1 ELSE 0 END) from_outcome,
       SUM(CASE WHEN o.pnl_pct = 0 AND t.pnl_pct IS NOT NULL AND t.pnl_pct <> 0 THEN 1 ELSE 0 END) from_parent_pnl,
       SUM(CASE WHEN o.pnl_pct = 0 AND (t.pnl_pct IS NULL OR t.pnl_pct = 0)
                 AND t.exit_price IS NOT NULL AND t.exit_price <> 0
                 AND t.entry_price IS NOT NULL AND t.entry_price <> 0 THEN 1 ELSE 0 END) from_prices
FROM at_pick_outcomes o
LEFT JOIN trading_picks t ON t.id = o.pick_id
WHERE o.asset_class IS NOT NULL AND o.asset_class <> ''
GROUP BY o.asset_class HAVING n >= 50 ORDER BY n DESC
"""
print(f"  {'class':<12} {'n':>7} {'mean%':>8} {'from_o':>8} {'from_t':>8} {'from_px':>8}")
tot_n = tot_s = 0
for ac, n, m, fo, ft, fp in q(sql):
    if ac == "ERR":
        print("  ", m)
        break
    print(f"  {str(ac)[:12]:<12} {n:>7} {str(m):>8} {fo or 0:>8} {ft or 0:>8} {fp or 0:>8}")
c.close()
