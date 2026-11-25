#!/usr/bin/env python3
"""zero_mass_probe.py - why is the median pnl_pct exactly 0.00 in every asset class?

The cost-gate table reports median bp = 0.00 for 11 of 14 classes. A real return
distribution does not have its median pinned to exactly zero across every asset
class. That points at a mass point: some large share of rows carry pnl_pct = 0
exactly, probably picks that expired flat or were never resolved.

If half the sample is a synthetic zero, then every MEAN is diluted by half and
every MEDIAN is measuring the zero mass rather than the strategy. That would make
the entire cost-gate table uninterpretable - so measure the mass before quoting
any of it.
"""
import os
import pymysql

VAULT = os.path.expanduser("~/dbpasses.txt")
PW = [l.strip() for l in open(VAULT, encoding="utf-8", errors="replace").read().splitlines()][82]
c = pymysql.connect(host="mysql.50webs.com", user="ejaguiar1_stocks", password=PW,
                    database="ejaguiar1_stocks", connect_timeout=30)
cur = c.cursor()


def q(sql, a=None):
    cur.execute(sql, a or ())
    return cur.fetchall()


print("=" * 78)
print("A. HOW BIG IS THE EXACT-ZERO MASS?")
print("=" * 78)
r = q("""SELECT COUNT(*) n,
                SUM(pnl_pct = 0) exactly_zero,
                SUM(pnl_pct IS NULL) nulls,
                SUM(pnl_pct > 0) pos,
                SUM(pnl_pct < 0) neg
         FROM at_pick_outcomes""")
n, z, nl, p, ng = r[0]
print(f"  total rows      {n:,}")
print(f"  pnl_pct = 0     {z:,}  ({100*z/n:.1f}%)   <-- mass point")
print(f"  pnl_pct NULL    {nl or 0:,}")
print(f"  positive        {p:,}  ({100*p/n:.1f}%)")
print(f"  negative        {ng:,}  ({100*ng/n:.1f}%)")

print("\n" + "=" * 78)
print("B. IS THE MASS CONCENTRATED IN A STATUS OR EXIT REASON?")
print("=" * 78)
for col in ("status", "result", "outcome", "exit_reason"):
    try:
        for row in q(f"""SELECT `{col}`, COUNT(*) n, SUM(pnl_pct = 0) zeros,
                                ROUND(100*SUM(pnl_pct = 0)/COUNT(*),1) pct_zero
                         FROM at_pick_outcomes GROUP BY `{col}` ORDER BY n DESC LIMIT 6"""):
            print(f"  {col}={str(row[0])[:22]:<22} n={row[1]:<7} zeros={row[2]:<7} ({row[3]}%)")
        print()
    except Exception:
        continue

print("=" * 78)
print("C. WHAT DOES THE DISTRIBUTION LOOK LIKE WITH ZEROS REMOVED?")
print("=" * 78)
print(f"  {'class':<12} {'n_nonzero':>10} {'mean bp':>10} {'median bp':>11} {'WR':>7}")
for row in q("""
SELECT asset_class, COUNT(*) n, ROUND(AVG(pnl_pct)*10000,1) mean_bp,
       ROUND(SUM(pnl_pct>0)*100.0/COUNT(*),1) wr
FROM at_pick_outcomes
WHERE pnl_pct IS NOT NULL AND pnl_pct <> 0 AND asset_class IS NOT NULL AND asset_class<>''
GROUP BY asset_class HAVING n >= 50 ORDER BY n DESC"""):
    print(f"  {str(row[0])[:12]:<12} {row[1]:>10} {row[2]:>10} {'(see D)':>11} {row[3]:>7}")

print("\n" + "=" * 78)
print("D. MEDIAN PER CLASS, NON-ZERO ONLY (recomputed in python)")
print("=" * 78)
import statistics as st
for row in q("""SELECT asset_class, pnl_pct FROM at_pick_outcomes
                WHERE pnl_pct IS NOT NULL AND pnl_pct <> 0 AND asset_class IS NOT NULL
                  AND asset_class <> ''"""):
    pass
cur.execute("""SELECT asset_class, pnl_pct FROM at_pick_outcomes
               WHERE pnl_pct IS NOT NULL AND pnl_pct <> 0 AND asset_class IS NOT NULL
                 AND asset_class <> ''""")
from collections import defaultdict
by = defaultdict(list)
for cls, v in cur.fetchall():
    try:
        by[cls].append(float(v))
    except (TypeError, ValueError):
        continue
for cls in sorted(by, key=lambda k: -len(by[k])):
    v = by[cls]
    if len(v) < 50:
        continue
    print(f"  {cls[:12]:<12} n={len(v):<7} mean {st.mean(v)*10000:>+9.1f} bp   "
          f"median {st.median(v)*10000:>+9.1f} bp")

print("\n" + "=" * 78)
print("E. DO THE ZERO ROWS LOOK LIKE RESOLVED TRADES AT ALL?")
print("=" * 78)
try:
    for row in q("""SELECT COUNT(*) n, MIN(created_at), MAX(created_at)
                    FROM at_pick_outcomes WHERE pnl_pct = 0"""):
        print(f"  zero rows: {row[0]:,}  created {row[1]} .. {row[2]}")
except Exception as e:
    print(f"  (no created_at on this table: {str(e)[:70]})")

c.close()
