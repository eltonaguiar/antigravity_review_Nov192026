#!/usr/bin/env python3
"""Parameter sweep -- does any (TP, SL, cost) combination make a scenario PROVEN?

The point is robustness, not the best cell. With 4 scenarios x 3 TP/SL pairs x 2
costs = 24 trials, a single lucky cell is expected by chance: at 5% each, ~1.2
false positives. So a cell is only interesting if it survives the WHOLE
neighbourhood, and the deflated-Sharpe lesson from the programme applies -- a raw
positive is not evidence.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import proveit as P

CASES = {
    "no_bracket": (None, None),
    "tp5_sl3": (5.0, 3.0),
    "tp2_sl1": (2.0, 1.0),
}
COSTS = ["retail_crypto", "programme_sweep"]
CASHES = [300, 500, 2000, 10000]


def run_one(cash, tp, sl, cost_profile, sims=400):
    cost_bp = P.COST_PROFILES_BP[cost_profile]
    allocs = P.portfolio_allocations(cash)
    key = [k for k in allocs if k.endswith(str(cash))][0]
    import statistics as st
    runs = []
    for s in range(sims):
        tp_trades = {}
        for i, (c, m) in enumerate(P.CLASS_INPUTS.items()):
            if m["expectancy_pct"] is None:
                continue
            n = min(m["n"], 200)
            tp_trades[c] = P.simulate_class(c, n, m["expectancy_pct"], P.SIGMA_PCT[c],
                                           cost_bp, 365, tp_pct=tp, sl_pct=sl, seed=s * 977 + i)
        runs.append(P.run_scenario(cash, allocs[key], tp_trades, 1.0, 0.0)["apr"])
    med = st.median(runs)
    ci = P.percentile_ci(runs)
    exc = (P.excess_apr(ci[0]), P.excess_apr(ci[1]))
    return dict(median=med, ci=ci, verdict=P.verdict_from_ci(exc),
                beat_hurdle=sum(1 for a in runs if a > P.HURDLE_APR) / len(runs))


def main() -> int:
    rows = []
    for cash, (name, (tp, sl)), cost in itertools.product(CASHES, CASES.items(), COSTS):
        r = run_one(cash, tp, sl, cost)
        rows.append(dict(cash=cash, bracket=name, tp=tp, sl=sl, cost=cost, **r))
        print("%6d %-11s %-16s med=%+7.2f%% ci=[%+7.2f%%,%+7.2f%%] beatH=%5.1f%% %s" % (
            cash, name, cost, r["median"] * 100, r["ci"][0] * 100, r["ci"][1] * 100,
            r["beat_hurdle"] * 100, r["verdict"]))
    # HEADLINE is the no-bracket case only. A bracket changes the return
    # distribution (first-touch exits truncate a skewed process), so a bracketed
    # PROVEN cell is a property of the RULE, not of the measured edge, and is
    # reported separately -- the programme's bracket identity says a bracket
    # cannot create an edge, only reshape it.
    unbracketed = [r for r in rows if r["bracket"] == "no_bracket"]
    print("\nHEADLINE (no bracket, the measured edge as-is):")
    for r in unbracketed:
        print("  %6d %-16s med=%+7.2f%% ci=[%+7.2f%%,%+7.2f%%] %s" % (
            r["cash"], r["cost"], r["median"] * 100, r["ci"][0] * 100,
            r["ci"][1] * 100, r["verdict"]))
    proven = [r for r in rows if r["verdict"] == "PROVEN_EDGE"]
    print("\ncells: %d | PROVEN_EDGE: %d | KILLED: %d | INCONCLUSIVE: %d" % (
        len(rows), len(proven), sum(r["verdict"] == "KILLED" for r in rows),
        sum(r["verdict"] == "INCONCLUSIVE" for r in rows)))
    # robustness: how often does the SAME scenario beat the hurdle across all its variations?
    print("\nrobustness -- share of a scenario's 6 variations that beat the hurdle on median:")
    for cash in CASHES:
        sub = [r for r in rows if r["cash"] == cash]
        print("  %6d  %d/%d" % (cash, sum(r["median"] > P.HURDLE_APR for r in sub), len(sub)))
    Path("results/sweep_2026-11-24.json").write_text(json.dumps(rows, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
