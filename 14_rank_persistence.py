#!/usr/bin/env python3
"""
rank_persistence.py - does portfolio skill persist?

Rank all portfolios by return in the FIRST half of the window, then measure the SECOND half.
Persistence = skill. Mean reversion = the top performer was luck.

This is the test that decides whether +7.58% means anything, and it needs no new data.

Method, fixed before running:
  - window split at the median snapshot date (equal calendar halves)
  - return per portfolio per half, from NAV snapshots (first and last in each half)
  - exclude portfolios with < 8 snapshots in either half, and any with non-positive NAV
  - Spearman rank correlation between halves, with a permutation p-value
  - top-quartile vs bottom-quartile mean return in the second half
  - every result also expressed against CASH (+2.2% over the full window, prorated)
"""
import math
import os
import random
import statistics

import pymysql

VAULT = os.path.expanduser("~/dbpasses.txt")
HOST, DB = "mysql.50webs.com", "ejaguiar1_stocks"
PW = [l.strip() for l in open(VAULT, encoding="utf-8", errors="replace").read().splitlines()][82]
c = pymysql.connect(host=HOST, user="ejaguiar1_stocks", password=PW, database=DB, connect_timeout=30)
cur = c.cursor()


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def spearman(a, b):
    """Spearman rho via ranks, with average ranks for ties."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((x - mb) ** 2 for x in rb))
    return num / den if den else 0.0


# ---- pull snapshots -------------------------------------------------------
cur.execute("""SELECT portfolio_id, asof_date, nav_usd FROM PF_NAV_SNAPSHOT
               ORDER BY portfolio_id, asof_date""")
rows = cur.fetchall()
print(f"snapshots pulled: {len(rows)}")

by_pf = {}
dates = set()
for pid, d, nav in rows:
    v = f(nav)
    if v is None:
        continue
    by_pf.setdefault(pid, []).append((str(d), v))
    dates.add(str(d))

dates = sorted(dates)
mid = dates[len(dates) // 2]
print(f"window: {dates[0]} .. {dates[-1]}  ({len(dates)} distinct dates)")
print(f"split at: {mid}")

H1, H2 = [], []
for pid, pts in by_pf.items():
    pts.sort()
    a = [p for p in pts if p[0] <= mid]
    b = [p for p in pts if p[0] > mid]
    if len(a) < 8 or len(b) < 8:
        continue
    if a[0][1] <= 0 or b[0][1] <= 0:
        continue          # ruined portfolios cannot be ranked
    r1 = (a[-1][1] / a[0][1] - 1) * 100
    r2 = (b[-1][1] / b[0][1] - 1) * 100
    H1.append((pid, r1))
    H2.append((pid, r2))

pids = [p for p, _ in H1]
r1 = [v for _, v in H1]
r2 = dict(H2)
r2v = [r2[p] for p in pids]

print(f"\nportfolios ranked in both halves: {len(pids)}")

if len(pids) >= 5:
    rho = spearman(r1, r2v)
    random.seed(7)
    N = 5000
    perm = []
    for _ in range(N):
        s = r2v[:]
        random.shuffle(s)
        perm.append(spearman(r1, s))
    p = sum(1 for x in perm if abs(x) >= abs(rho)) / N

    print("\n" + "=" * 70)
    print("RANK PERSISTENCE (Spearman rho between first-half and second-half return)")
    print("=" * 70)
    print(f"  rho = {rho:+.4f}   permutation p = {p:.4f}   n = {len(pids)}")

    order = sorted(range(len(pids)), key=lambda i: r1[i])
    q = max(1, len(order) // 4)
    bottom = [pids[i] for i in order[:q]]
    top = [pids[i] for i in order[-q:]]
    mt, mb = statistics.mean([r2[p] for p in top]), statistics.mean([r2[p] for p in bottom])
    print(f"\n  top quartile in H1 (n={len(top)}): mean H2 return = {mt:+.2f}%")
    print(f"  bot quartile in H1 (n={len(bottom)}): mean H2 return = {mb:+.2f}%")
    print(f"  spread = {mt - mb:+.2f} pp")
    print(f"\n  CASH comparator over the full window: +2.2%")
    print(f"  top-quartile H2 mean vs cash: {mt - 2.2:+.2f} pp")
    print(f"  all-portfolio H2 mean vs cash: {statistics.mean(r2v) - 2.2:+.2f} pp")

    print("\n  -- top 5 by H1, with their H2 result --")
    for i in order[-5:][::-1]:
        print(f"    pf{pids[i]:<4} H1 {r1[i]:+7.2f}%  ->  H2 {r2v[i]:+7.2f}%")
    print("\n  -- bottom 5 by H1, with their H2 result --")
    for i in order[:5]:
        print(f"    pf{pids[i]:<4} H1 {r1[i]:+7.2f}%  ->  H2 {r2v[i]:+7.2f}%")

    print("\n  INTERPRETATION KEY")
    print("    rho > 0 with p < 0.05  -> skill persists, the top cohort is real")
    print("    rho ~ 0                -> half a year of NAV contains no rank information")
    print("    rho < 0 significant    -> mean reversion; the winners were variance")

c.close()
