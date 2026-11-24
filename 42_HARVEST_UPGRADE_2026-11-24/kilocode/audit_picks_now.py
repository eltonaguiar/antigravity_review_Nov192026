#!/usr/bin/env python3
"""Audit the budget page's -1.41%/pick claim: net cost, symbol/date clustering,
cluster-robust CI, design effect, sign test, clustered win rate."""
import json, math, random, statistics, sys
from collections import defaultdict
from pathlib import Path

SRC = Path(__file__).resolve().parent / "picks_now_resolved_2026-11-24.json"
OUT = Path(__file__).resolve().parent / "picks_now_audit.json"
rows = json.loads(SRC.read_text())
for r in rows:
    r["pnl"] = float(r["exit_pnl_pct"])
    r["net"] = r["pnl"] - 0.26          # 26 bp round turn
    r["date"] = str(r["entry_date"])[:10]

def ci_boot(vals, groups, iters=4000, seed=7):
    rnd = random.Random(seed)
    keys = list(groups)
    means = []
    for _ in range(iters):
        samp = []
        for _ in range(len(keys)):
            samp.extend(groups[keys[rnd.randrange(len(keys))]])
        means.append(sum(samp)/len(samp))
    means.sort()
    return means[int(0.025*iters)], means[int(0.975*iters)]

def oneway_effect(key):
    n = len(rows); mean = sum(r["net"] for r in rows)/n
    g = defaultdict(float)
    for r in rows:
        g[r[key]] += r["net"] - mean
    G = len(g)
    V = sum(v*v for v in g.values()) / (n*n) * (G/(G-1))
    return V, G

y = [r["net"] for r in rows]; n = len(y); mean = sum(y)/n
Vs, Gs = oneway_effect("symbol")
Vd, Gd = oneway_effect("date")
Vinter = sum((v-mean)**2 for v in y)/(n*n)     # each row is its own symbol-day
Vtwo = Vs + Vd - Vinter
Viid = statistics.pvariance(y)/n
se = math.sqrt(max(Vtwo, 0))
# sign test on per-symbol means
bysym = defaultdict(list)
for r in rows: bysym[r["symbol"]].append(r["net"])
pos = sum(1 for v in bysym.values() if statistics.mean(v) > 0)
neg = sum(1 for v in bysym.values() if statistics.mean(v) < 0)
k, m = min(pos, neg), pos+neg
p_sign = min(1.0, 2*sum(math.comb(m, i) for i in range(k+1)) / (2**m))
# clustered win rates
def winstats(key):
    g = defaultdict(list)
    for r in rows: g[r[key]].append(1 if r["pnl"] > 0 else 0)
    per = [sum(v)/len(v) for v in g.values()]
    return {"clusters": len(g), "pooled_wr": sum(sum(v) for v in g.values())/n,
            "mean_of_cluster_wr": statistics.mean(per), "median_cluster_wr": statistics.median(per)}
sym_win = winstats("symbol"); date_win = winstats("date")
lo_s, hi_s = ci_boot(y, {k: [r["net"] for r in rows if r["symbol"] == k] for k in bysym})
bydate = defaultdict(list)
for r in rows: bydate[r["date"]].append(r["net"])
lo_d, hi_d = ci_boot(y, bydate)
res = {
 "n": n, "symbols": len(bysym), "entry_dates": len(bydate),
 "gross_mean_pct": statistics.mean([r["pnl"] for r in rows]),
 "net_mean_pct": mean, "ci_iid": [mean-1.96*math.sqrt(Viid), mean+1.96*math.sqrt(Viid)],
 "se_iid": math.sqrt(Viid), "se_two_way": se,
 "ci_two_way": [mean-1.96*se, mean+1.96*se],
 "design_effect_two_way": Vtwo/Viid, "design_effect_symbol": Vs/Viid, "design_effect_date": Vd/Viid,
 "symbol_bootstrap_ci": [lo_s, hi_s], "date_bootstrap_ci": [lo_d, hi_d],
 "sign_test_symbol_means": {"positive": pos, "negative": neg, "p_two_sided": p_sign},
 "win_rate": {"pooled": sym_win["pooled_wr"], "symbol_clusters": sym_win["clusters"],
              "mean_of_symbol_wr": sym_win["mean_of_cluster_wr"],
              "median_symbol_wr": sym_win["median_cluster_wr"],
              "mean_of_date_wr": date_win["mean_of_cluster_wr"],
              "median_date_wr": date_win["median_cluster_wr"]},
 "implication": "26bp cost + 2-way clustering; see ci_two_way",
}
OUT.write_text(json.dumps(res, indent=2)+"\n")
print(json.dumps(res, indent=2))
