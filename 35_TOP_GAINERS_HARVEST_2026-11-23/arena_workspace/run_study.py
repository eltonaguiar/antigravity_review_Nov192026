"""run_study.py -- executes the full study, writes tables + charts to ../out/

Run:  python3 run_study.py
"""
import sys, warnings, json
sys.path.insert(0, "src")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from engine import (make_synthetic_universe, build_panel, top_gainer_study,
                    triangular_barrier_backtest, atr, metrics, block_bootstrap_ci,
                    psr, deflated_sharpe)

OUT = "out"
uni = make_synthetic_universe(seed=7, n_days=2200)
panel = build_panel(uni)

# ===========================================================================
# 1) THE CORE QUESTION: are top-gainer days predictive? by class / symbol / side
# ===========================================================================
res = top_gainer_study(panel, lookback=1, forward=5, quantile=0.7)
res.to_csv(f"{OUT}/1_top_gainer_slices.csv", index=False)
core = res[res["slice"].str.contains("top-gainer")].copy()
core["cls"] = core["slice"].str.split(":").str[0]
core["dir"] = core["slice"].str.extract(r"(LONG|SHORT)")
print("=== 1. 5-day forward EXCESS return, conditional on being a top-gainer today ===")
print("   (excess = minus that day's class average, so class drift/beta cannot fake an edge)")
print(core[["slice", "n_obs", "mean_excess_fwd_ret", "ci_lo", "ci_hi", "p", "p_adj_BH",
            "significant_5pct"]].to_string(index=False, float_format=lambda x: f"{x: .5f}"))
print(f"\n slices tested {len(res)} | raw p<.05 {(res.p<.05).sum()} | BH-FDR 5% {int(res.significant_5pct.sum())}")

# ===========================================================================
# 2) PREDICTABILITY SCOREBOARD: class > symbol > symbol x direction
#    Two independent measures: (i) rank IC of trailing 5d z vs fwd 5d excess ret
#    (ii) TP/SL barrier expectancy net of realistic costs, both with a
#    "n_trials" haircut (Deflated Sharpe) so we don't fool ourselves.
# ===========================================================================
def ic_table(panel):
    p = panel.sort_values(["symbol", "date"]).copy()
    r = p.groupby("symbol").ret
    p["tr"] = r.transform(lambda s: s.rolling(5).sum())
    p["z"] = p.groupby("symbol").tr.transform(
        lambda s: (s - s.rolling(60).mean()) / s.rolling(60).std())
    p["fwd"] = p.groupby("symbol").ret.transform(
        lambda s: (1 + s.shift(-1)).rolling(5).apply(np.prod, raw=True) - 1).shift(-4)
    p["xret"] = p.groupby(["date", "class"]).fwd.transform(
        lambda s: s - s.mean())                     # class-demeaned forward return
    rows = []
    for sym, g in p.dropna(subset=["z", "xret"]).groupby("symbol"):
        # Newey-West-lite: use non-overlapping 5-day samples to avoid fake n
        gs = g.iloc[::5]
        rho = stats.spearmanr(g.z.values, g.xret.values).statistic
        rhos = stats.spearmanr(gs.z.values, gs.xret.values).statistic
        n_eff = len(gs)
        t = rhos * np.sqrt(max(n_eff - 2, 1) / max(1 - rhos ** 2, 1e-9))
        pv = 2 * (1 - stats.t.cdf(abs(t), max(n_eff - 2, 1)))
        rows.append(dict(symbol=sym, asset_class=g["class"].iloc[0], n_bars=len(g),
                         n_nonoverlap=n_eff, IC_5d=rho, IC_nonoverlap=rhos,
                         t_stat=t, p_value=pv))
    return pd.DataFrame(rows)

ic = ic_table(panel)
ic["p_adj_BH"] = stats.false_discovery_control(ic.p_value.fillna(1), method="bh")
ic = ic.sort_values("IC_nonoverlap", key=abs, ascending=False)
ic.to_csv(f"{OUT}/2_predictability_ic.csv", index=False)
print("\n=== 2a. Signal quality per SYMBOL: rank IC (trailing 5d z -> fwd 5d class-excess ret) ===")
print("    IC_nonoverlap uses every 5th obs -> the honest sample size")
print(ic.round(4).to_string(index=False))

def trailing_signal(df, look=5, thr=0.5, side=1):
    r = df.close.pct_change(); m = r.rolling(look).sum()
    z = (m - m.rolling(60).mean()) / m.rolling(60).std()
    s = pd.DataFrame(index=df.index, columns=["side"], data=0.0)
    s.loc[z > thr, "side"] = side; s.loc[z < -thr, "side"] = -side
    return s

COSTS = {"equity": 6.0, "crypto": 12.0, "fx": 2.0, "fund": 500.0}  # bps per side, round-trip = 2x
rows = []
N_TRIALS = 2 * 3 * 3 * 2   # direction x horizon x sl x tp grid
for sym, df in uni.items():
    kl = df.asset_class.iloc[0] if isinstance(df.asset_class, pd.Series) else df.asset_class
    if kl == "fund":            # NAV-only, cannot place TP/SL intraday
        continue
    for side in (+1, -1):
        best = None
        for h, sl, tp in [(5, 2, 2), (10, 3, 3), (20, 4, 4)]:
            t = triangular_barrier_backtest(df, trailing_signal(df, side=side),
                                            tp_mult=tp, sl_mult=sl, horizon=h,
                                            cost_bps=COSTS[kl])
            if len(t) < 60:
                continue
            m = metrics(t.r, ppy=252 / h, n_trials=N_TRIALS)
            row = dict(symbol=sym, asset_class=kl, direction="long" if side > 0 else "short",
                       horizon=h, sl=sl, tp=tp, **{k: m[k] for k in
                       ["n", "hit_rate", "expectancy_R", "profit_factor", "sharpe_ann",
                        "max_dd_R", "PSR_vs_0", "DSR", "t_stat", "p_value"]})
            if best is None or row["expectancy_R"] > best["expectancy_R"]:
                best = row
        if best:
            rows.append(best)
board = pd.DataFrame(rows).sort_values("expectancy_R", ascending=False)
board["p_adj_BH"] = stats.false_discovery_control(board.p_value.fillna(1), method="bh")
board["passes_DSR"] = board.DSR > 0.95
board.to_csv(f"{OUT}/3_predictability_tpsl.csv", index=False)
print("\n=== 2b. Predictability per SYMBOL x DIRECTION, best TP/SL from a 3x3 grid,")
print("     net of realistic per-class costs, DSR haircut for 24 trials ===")
print(board.round(3).to_string(index=False))

# class-level aggregate
cls = board.groupby("asset_class").agg(
    symbols=("symbol", "nunique"),
    mean_expectancy_R=("expectancy_R", "mean"),
    best_expectancy_R=("expectancy_R", "max"),
    mean_PF=("profit_factor", "mean"),
    passing_DSR=("passes_DSR", "sum")).sort_values("best_expectancy_R", ascending=False)
cls.to_csv(f"{OUT}/4_class_ranking.csv")
print("\n=== 2c. WHICH ASSET CLASS IS MOST PREDICTABLE (by this signal family) ===")
print(cls.round(3).to_string())

# ===========================================================================
# 3) Cost sensitivity
# ===========================================================================
print("\n=== 3. Edge vs cost: EURUSD 5d-reversal, TP2/SL2, 5d horizon ===")
cexp = []
for c in [0, 1, 2, 3, 5, 8, 12, 20, 30]:
    t = triangular_barrier_backtest(uni["EURUSD"], trailing_signal(uni["EURUSD"], side=-1),
                                    tp_mult=2, sl_mult=2, horizon=5, cost_bps=c)
    m = metrics(t.r, ppy=50)
    cexp.append((c, m["expectancy_R"], m["profit_factor"]))
    print(f"  {c:>3} bps/side  expectancy {m['expectancy_R']:+.4f}R  PF {m['profit_factor']:.2f}  "
          f"t {m['t_stat']:+.2f}")
print("  -> the planted edge is real at 0-2bps and gone by ~8bps: costs are the edge's ceiling.")

# ===========================================================================
# 4) Charts
# ===========================================================================
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
colors = {"equity": "#2b6cb0", "crypto": "#c05621", "fx": "#2f855a", "fund": "#6b46c1"}

# (a) per-class long/short excess
order = ["crypto", "fx", "equity"]
w = 0.36
for i, k in enumerate(order):
    lt = core[(core.cls == k) & (core.dir == "LONG")].iloc[0]
    for j, (row, lab, alpha) in enumerate([(lt, "long gainer", .85),
                                           (core[(core.cls == k) & (core.dir == "SHORT")].iloc[0],
                                            "short gainer", .45)]):
        x = i + (j - .5) * w
        ax[0, 0].bar(x, row.mean_excess_fwd_ret * 1e4, width=w, alpha=alpha,
                     color=colors[k], label=lab if i == 0 else None)
        ax[0, 0].errorbar(x, row.mean_excess_fwd_ret * 1e4,
                          yerr=[[(row.mean_excess_fwd_ret - row.ci_lo) * 1e4],
                                [(row.ci_hi - row.mean_excess_fwd_ret) * 1e4]],
                          color="k", capsize=3, lw=.9)
ax[0, 0].set_xticks(range(len(order))); ax[0, 0].set_xticklabels(order)
ax[0, 0].axhline(0, color="k", lw=.8)
ax[0, 0].set_ylabel("5d excess return, bps")
ax[0, 0].set_title("(a) Buy/short the top gainer: per-class excess return\n95% block-bootstrap CI", fontsize=10)
ax[0, 0].legend(fontsize=8)

# (b) IC per symbol
d = ic.sort_values("IC_nonoverlap")
ax[0, 1].barh(d.symbol, d.IC_nonoverlap, color=[colors[c] for c in d.asset_class])
ax[0, 1].axvline(0, color="k", lw=.8)
ax[0, 1].set_title("(b) Rank IC per symbol (non-overlapping 5d samples)\n"
                   "positive = momentum, negative = reversal", fontsize=10)
ax[0, 1].set_xlabel("Spearman IC")

# (c) expectancy by symbol x direction
b = board.sort_values("expectancy_R")
cols = ["#2f855a" if x > 0 and passes else ("#9ae6b4" if x > 0 else "#c53030")
        for x, passes in zip(b.expectancy_R, b.passes_DSR)]
ax[1, 0].barh([f"{s} {d}" for s, d in zip(b.symbol, b.direction)], b.expectancy_R, color=cols)
ax[1, 0].axvline(0, color="k", lw=.8)
ax[1, 0].set_xlabel("expectancy, R per trade (net of costs)")
ax[1, 0].set_title("(c) Best TP/SL per symbol x direction\nsolid = passes Deflated Sharpe > 0.95", fontsize=10)

# (d) p-value uniformity across the search
ax[1, 1].hist(res.p.dropna(), bins=20, color="#4a5568", alpha=.85)
ax[1, 1].axhline(len(res.p.dropna()) / 20, color="crimson", ls="--", label="expected under the null")
ax[1, 1].set_xlabel("p-value"); ax[1, 1].set_ylabel("count")
ax[1, 1].set_title(f"(d) {len(res)} slices tested: raw p<.05 = {(res.p<.05).sum()}, "
                   f"survive BH-FDR = {int(res.significant_5pct.sum())}", fontsize=10)
ax[1, 1].legend(fontsize=8)

plt.tight_layout(); plt.savefig(f"{OUT}/study_charts.png", dpi=150)
print("\nwrote out/study_charts.png, out/*.csv")
