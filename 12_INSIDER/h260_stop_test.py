#!/usr/bin/env python3
"""h260_stop_test.py - rank-IC is real but copying LOSES. Does a stop rescue it?

Measured: top decile by prior RETURN earns mean future return -3.74% with median
+8.11% and 69% profitable. That is a positive-median, negative-mean distribution -
a few catastrophic blowups (leverage, liquidation) dominate the expectancy even
though the ranking is genuinely informative (rho +0.429 on returns).

This asks the honest follow-up: if the copy carries a stop, does expectancy turn
positive? Pre-registered thresholds, reported whatever they say.
"""
import glob
import json
import statistics as st

snap = json.load(open(sorted(glob.glob(
    "/home/eaguiar2015/findtorontoevents_antigravity.ca/reports/hl_leaderboard_snapshot_*.json"))[-1]))
elig = [r for r in snap["rows"]
        if (r.get("acct") or 0) >= 10000 and (r.get("wk_vlm") or 0) > 0 and (r.get("mo_vlm") or 0) > 0]

rows = []
for r in elig:
    a = float(r["acct"])
    rows.append({
        "ret_p": float(r["prior"]) / a,
        "ret_f": float(r["future"]) / a,
        "lev": float(r["mo_vlm"]) / a,
        "acct": a,
    })
rows.sort(key=lambda x: x["ret_p"], reverse=True)
dec = rows[:len(rows) // 10]

print(f"top decile by prior return: n={len(dec):,}\n")
raw = [r["ret_f"] for r in dec]
print("=" * 78)
print("UNSTOPPED COPY (baseline)")
print("=" * 78)
print(f"  mean   {st.mean(raw)*100:+8.2f}%   median {st.median(raw)*100:+8.2f}%")
print(f"  worst  {min(raw)*100:+8.1f}%   best {max(raw)*100:+8.1f}%")
worse = [x for x in raw if x < -1.0]
print(f"  wallets losing more than 100% of equity: {len(worse)} of {len(raw)} ({len(worse)/len(raw):.1%})")
print(f"  their total: {sum(worse)*100:+.0f}% of equity  <- this is what makes the mean negative")

print("\n" + "=" * 78)
print("WITH A STOP - equity floored at -X% (loss cannot exceed X)")
print("=" * 78)
print(f"  {'stop':>6} {'mean':>10} {'median':>10} {'net 26bp':>10}  verdict")
for stop in (0.05, 0.10, 0.20, 0.30, 0.50):
    capped = [max(x, -stop) for x in raw]
    m = st.mean(capped)
    net = (m - 0.0026) * 100
    print(f"  {-stop*100:>5.0f}% {m*100:>+9.2f}% {st.median(capped)*100:>+9.2f}% {net:>+9.2f}%  "
          f"{'CLEARS' if net > 0 else 'FAILS'}")

print("\n" + "=" * 78)
print("STOP + LEVERAGE FILTER (drop wallets above a turnover multiple)")
print("=" * 78)
print(f"  {'max lev':>8} {'n':>6} {'mean w/ 20% stop':>18} {'net 26bp':>10}  verdict")
for cap in (5, 20, 100, 1e9):
    g = [max(r["ret_f"], -0.20) for r in dec if r["lev"] <= cap]
    if len(g) < 50:
        print(f"  {cap:>8.0f} {len(g):>6}  too few")
        continue
    m = st.mean(g)
    net = (m - 0.0026) * 100
    print(f"  {cap:>8.0f} {len(g):>6} {m*100:>+17.2f}% {net:>+9.2f}%  {'CLEARS' if net > 0 else 'FAILS'}")

print("\n" + "=" * 78)
print("READ THIS BEFORE QUOTING ANYTHING ABOVE")
print("=" * 78)
print("  A stop changes the RESULT, not just the risk: the same ranking gives a")
print("  negative mean unstoppered and may give a positive one capped. That makes")
print("  the stop a PARAMETER of the tested strategy, so it must be pre-registered")
print("  and reported with the number of stops tried - otherwise choosing the best")
print("  stop after seeing the answer is the same sin as lowering a gate.")
print("  And it is still ONE snapshot pair. One draw.")
