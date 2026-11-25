#!/usr/bin/env python3
"""h260_size_artifact.py - is H-260's rank-IC skill, or account size?

The snapshot stores DOLLAR PnL (prior = mo_pnl - wk_pnl, future = wk_pnl), not
percentage returns. Rank-correlating two dollar quantities across wallets of very
different equity is mostly a size correlation: a $100M account makes bigger dollars
than a $10k account in both windows mechanically.

Tests:
  1 rho(prior, acct) and rho(future, acct)      - does size drive the ranking?
  2 partial rho(prior, future | acct)            - what survives size control?
  3 rho on RETURN, not dollars                   - the actual skill test
  4 within-size-decile rho                       - skill inside homogeneous equity
"""
import glob
import json
import statistics as st

snap = json.load(open(sorted(glob.glob(
    "/home/eaguiar2015/findtorontoevents_antigravity.ca/reports/hl_leaderboard_snapshot_*.json"))[-1]))
elig = [r for r in snap["rows"]
        if (r.get("acct") or 0) >= 10000 and (r.get("wk_vlm") or 0) > 0 and (r.get("mo_vlm") or 0) > 0]
print(f"eligible wallets: {len(elig):,}\n")


def rankdata(x):
    xs = sorted(range(len(x)), key=lambda i: x[i])
    rk = [0.0] * len(x)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and x[xs[j + 1]] == x[xs[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            rk[xs[k]] = avg
        i = j + 1
    return rk


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** .5
    db = sum((y - mb) ** 2 for y in b) ** .5
    return num / (da * db) if da and db else float("nan")


def rho(a, b):
    return pearson(rankdata(a), rankdata(b))


def partial_rho(x, y, z):
    """rho(x,y) with rank(z) partialled out of both."""
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    n = len(rx)
    m = [sum(v) / n for v in (rx, ry, rz)]
    def resid(a, b, ma, mb):
        num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
        den = sum((q - mb) ** 2 for q in b)
        beta = num / den if den else 0.0
        return [p - ma - beta * (q - mb) for p, q in zip(a, b)]
    ex = resid(rx, rz, m[0], m[2])
    ey = resid(ry, rz, m[1], m[2])
    return pearson(ex, ey)


acct = [float(r["acct"]) for r in elig]
prior = [float(r["prior"]) for r in elig]
future = [float(r["future"]) for r in elig]
# returns on equity - the economically meaningful quantity
pr_ret = [p / a for p, a in zip(prior, acct)]
fu_ret = [f / a for f, a in zip(future, acct)]

print("=" * 78)
print("1. DOES SIZE DRIVE THE RANKING?")
print("=" * 78)
print(f"  rho(prior, acct)   {rho(prior, acct):+.4f}")
print(f"  rho(future, acct)  {rho(future, acct):+.4f}")
print(f"  rho(prior, future) {rho(prior, future):+.4f}   <- the H-260 headline (+0.4493)")

print("\n" + "=" * 78)
print("2. WHAT SURVIVES A SIZE CONTROL?")
print("=" * 78)
print(f"  partial rho(prior, future | acct)  {partial_rho(prior, future, acct):+.4f}")

print("\n" + "=" * 78)
print("3. THE ACTUAL SKILL TEST - rank on RETURN, not dollars")
print("=" * 78)
print(f"  rho(prior_ret, future_ret)         {rho(pr_ret, fu_ret):+.4f}   <- skill if real")

print("\n" + "=" * 78)
print("4. WITHIN-SIZE-DECILE rho ON RETURNS")
print("=" * 78)
order = sorted(elig, key=lambda r: float(r["acct"]))
d = len(order) // 10
for i in range(10):
    g = order[i * d:(i + 1) * d] if i < 9 else order[i * d:]
    if len(g) < 50:
        continue
    a = [float(r["acct"]) for r in g]
    pr = [float(r["prior"]) / x for r, x in zip(g, a)]
    fu = [float(r["future"]) / x for r, x in zip(g, a)]
    print(f"  decile {i+1:>2} median acct ${st.median(a)/1e3:>10,.0f}k  n={len(g):<5} rho(ret) {rho(pr,fu):+.4f}")

print("\n" + "=" * 78)
print("5. WHAT A COPY-TRADER WOULD ACTUALLY EARN (return basis)")
print("=" * 78)
pairs = sorted(zip(pr_ret, fu_ret), reverse=True)
top = pairs[:len(pairs) // 10]
mean_f = st.mean([y for _, y in top])
print(f"  top decile by prior RETURN, n={len(top):,}")
print(f"    mean future return  {mean_f*100:+.2f}%")
print(f"    median              {st.median([y for _, y in top])*100:+.2f}%")
print(f"    share positive      {sum(1 for _,y in top if y>0)/len(top):.1%}")
for gate in (0.09, 0.26):
    print(f"    net after {gate*100:.0f} bp      {(mean_f*100-gate*100):+.2f}%  "
          f"{'CLEARS' if mean_f*100 > gate*100 else 'FAILS'}")
