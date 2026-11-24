"""PROVEIT simulator -- paper-only portfolio math. Stdlib only, no network, no DB.

Every per-class input is MEASURED (from this repo's own audit3 ledger dossiers) or
MODELED (from public long-run reference returns, clearly flagged). Nothing here is a
promise of returns; the whole point is to test whether the measured edge survives
cost and beats the programme's 4.32% T-bill hurdle.

Design rules
------------
1. A positive expectancy is not an edge. Every result is reported with a bootstrap
   CI and compared against the hurdle, not against zero.
2. Costs are charged on BOTH legs, per trade, in basis points of notional.
3. A hold cap exists because an untested "hold forever" is not a strategy.
4. The simulator never claims a win the inputs do not support.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import zlib
from pathlib import Path

# --------------------------------------------------------------------------- #
# Cost model. 26bp round turn is the figure the programme's sweep charged
# (30_COST_STRUCTURE_2026-11-24/COST_VS_SIGNAL.md). Retail adds spread +
# commission on top, so a retail run is a STRESS test, not the programme's number.
# --------------------------------------------------------------------------- #
COST_PROFILES_BP = {
    "retail_crypto": 40,      # 0.1% taker/side x2 + slippage
    "retail_stock": 5,        # 0 commission + ~2.5bp spread/side
    "retail_etf": 4,         # 1bp spread/side + tiny
    "retail_forex": 3,       # tight spread, no commission (spread-only broker)
    "retail_commodity": 12,
    "retail_fund": 0,        # index funds: 0 commission; expense ratio is separate
    "programme_sweep": 26,    # the figure actually charged in the 44-cell sweep
}
EXPENSE_RATIO_BP_YR = {      # annual drag for funds, bp
    "MUTUAL_FUND": 4,        # VTSAX 0.04%
    "ETF": 3,                # VTI/VOO ~0.03%
}

HURDLE_APR = 0.0432  # docs/edge_research/07, HURDLE_TBILL_APR in tools/capacity_model.py

# --------------------------------------------------------------------------- #
# Per-class inputs.  expectancy = mean net % per trade AFTER the programme's
# 26bp, as recorded in 38_FINAL_ASSET_CLASS_RANKING_2026-11-24/README.md.
#  sigma is a MODELED dispersion (round-trip return stdev), flagged model=MODELED,
#  because the ranking gives point estimates and CIs but not per-trade stdev.
# --------------------------------------------------------------------------- #
CLASS_INPUTS = {
    # class: dict(expectancy_pct, ci=(lo, hi), n, verdict, source)
    "CRYPTO":   dict(expectancy_pct=-0.29, ci=None, n=3726, verdict="KILL",
                     source="38_FINAL.../README.md §1 (intrabar truth WR 35.8%, PF 0.917)"),
    "COMMODITY": dict(expectancy_pct=-2.9619, ci=(-5.004, -1.338), n=50, verdict="KILL",
                      source="38_FINAL.../README.md §1"),
    "EQUITY":   dict(expectancy_pct=0.1058, ci=(-0.480, 0.693), n=956, verdict="WEAK",
                     source="38_FINAL.../README.md §1"),
    "ETF":      dict(expectancy_pct=-0.0062, ci=(-0.437, 0.433), n=590, verdict="WEAK",
                     source="38_FINAL.../README.md §1"),
    "FOREX":    dict(expectancy_pct=-0.0447, ci=(-0.169, 0.078), n=264, verdict="WEAK",
                     source="38_FINAL.../README.md §1"),
    "BOND":     dict(expectancy_pct=-0.0978, ci=(-0.339, 0.169), n=37, verdict="WEAK",
                     source="38_FINAL.../README.md §1"),
    "FUTURES":  dict(expectancy_pct=None, ci=None, n=4, verdict="INSUFFICIENT_N",
                     source="38_FINAL.../README.md §1 (n=4; any verdict would be fabricated)"),
}

# MODELED reference long-run returns (real, inflation-adjusted, %/yr) and vol, for
# the benchmark leg only. These are textbook figures, NOT this programme's measurements.
MODELED_BENCHMARK = {
    "US_EQUITY_TOTAL": dict(real_return_pct_yr=7.0, vol_pct_yr=16.0,
                            source="MODELED: long-run US equity real return ~7%/yr, vol ~16%"),
    "US_BOND_AGG":     dict(real_return_pct_yr=2.0, vol_pct_yr=6.0,
                            source="MODELED: aggregate bond real return ~2%/yr, vol ~6%"),
    "TBILL_HURDLE":    dict(real_return_pct_yr=HURDLE_APR * 100, vol_pct_yr=0.5,
                            source="MEASURED hurdle: tools/capacity_model.py HURDLE_TBILL_APR"),
}

# Dispersion model for per-trade returns, by class. MODELED.
SIGMA_PCT = {"CRYPTO": 6.0, "COMMODITY": 3.0, "EQUITY": 2.2, "ETF": 1.4,
             "FOREX": 0.8, "BOND": 0.6, "FUTURES": 3.0}


def bootstrap_ci(vals, resamples=4000, seed=7):
    """Percentile bootstrap CI of the MEAN. Use percentile_ci() when the headline
    statistic is the median -- mixing a mean-CI with a median headline produces a
    CI that does not contain its own point estimate."""
    if len(vals) < 2:
        return None
    rnd = random.Random(seed)
    n = len(vals)
    means = [st.fmean(rnd.choices(vals, k=n)) for _ in range(resamples)]
    means.sort()
    return (means[int(0.025 * resamples)], means[int(0.975 * resamples)])


def percentile_ci(vals):
    """Empirical 2.5/97.5 percentiles of the sample itself (no resampling), so the
    median is guaranteed to sit inside the interval."""
    if len(vals) < 2:
        return None
    s = sorted(vals)
    n = len(s)
    return (s[int(0.025 * (n - 1))], s[int(0.975 * (n - 1))])


# The expectancy in CLASS_INPUTS is NET of this round-turn cost (the sweep charged
# 26bp). Evaluating at a different cost shifts the expectancy by the difference --
# (26 - cost) bp -- rather than re-drawing and cancelling, which would make cost
# silently irrelevant.
MEASURED_AT_COST_BP = 26


def simulate_class(cls, n_trades, expectancy_pct, sigma_pct, cost_bp, hold_days,
                   tp_pct=None, sl_pct=None, seed=0):
    """Simulate n_trades of one class' rule.

    The supplied expectancy is net at MEASURED_AT_COST_BP; it is re-based to the
    requested cost before drawing, so a higher-cost profile genuinely lowers the
    expected return. Optional TP/SL clips the return, mirroring a bracket order:
    on a barrier touch the trade exits at the barrier, and the stop wins on an
    ambiguous bar (the conservative convention this programme's executor uses).
    """
    rnd = random.Random(seed)
    e_at_cost = expectancy_pct + (MEASURED_AT_COST_BP - cost_bp) / 100.0
    steps = 20  # sub-steps along the holding period for first-touch barriers
    out = []
    for _ in range(n_trades):
        if tp_pct is None and sl_pct is None:
            out.append(dict(ret_pct=rnd.gauss(e_at_cost, sigma_pct), days=hold_days))
            continue
        # A bracket must not create edge (the programme's bracket identity): the
        # exit is the FIRST barrier touched along a path, never a clip of the
        # terminal draw. Clipping the terminal draw caps the upside and floors the
        # downside, which mechanically lifts a negative-mean process -- an artifact.
        inc_mu, inc_sd = e_at_cost / steps, sigma_pct / (steps ** 0.5)
        level, exit_ret = 0.0, None
        for _s in range(steps):
            level += rnd.gauss(inc_mu, inc_sd)
            if sl_pct is not None and level <= -sl_pct:
                exit_ret = -sl_pct          # the stop wins on an ambiguous bar
                break
            if tp_pct is not None and level >= tp_pct:
                exit_ret = tp_pct
                break
        out.append(dict(ret_pct=level if exit_ret is None else exit_ret, days=hold_days))
    return out


def compound(trades, start_cash, fee_per_trade=0.0):
    """Fixed-fractional compounding: each trade risks the whole position."""
    cash = start_cash
    for t in trades:
        cash = max(0.0, cash * (1 + t["ret_pct"] / 100.0) - fee_per_trade)
    return cash


def max_drawdown(equity):
    peak, mdd = equity[0], 0.0
    for v in equity:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, (v - peak) / peak)
    return mdd


def equity_path(trades, start_cash, fee_per_trade=0.0):
    cash = start_cash
    path = [cash]
    for t in trades:
        cash = max(0.0, cash * (1 + t["ret_pct"] / 100.0) - fee_per_trade)
        path.append(cash)
    return path


def cagr(start, end, years):
    if start <= 0 or years <= 0 or end <= 0:
        return None
    return (end / start) ** (1.0 / years) - 1.0


def excess_apr(apr, hurdle=HURDLE_APR):
    """Real (inflation-ish) excess over the hurdle using (1+a)/(1+h)-1, not a-b:
    the programme already lost a bond test to exactly that difference
    (38_FINAL.../README.md: +84bp became -91.58bp at real cost)."""
    if apr is None:
        return None
    return (1 + apr) / (1 + hurdle) - 1


def verdict_from_ci(ci_excess):
    """Decide from the CI, not the point estimate."""
    if ci_excess is None:
        return "INSUFFICIENT_N"
    lo, hi = ci_excess
    if lo > 0:
        return "PROVEN_EDGE"
    if hi < 0:
        return "KILLED"
    return "INCONCLUSIVE"  # CI spans 0 == not proven, per the programme's convention


def portfolio_allocations(cash):
    """Scenario -> class weights. Sizing responds to capital, not to hope."""
    return {
        "defensive_300": {
            "cash": 0.40, "bond": 0.40, "etf": 0.20, "equity": 0.0, "crypto": 0.0,
        },
        "core_500": {
            "cash": 0.20, "bond": 0.30, "etf": 0.35, "equity": 0.15, "crypto": 0.0,
        },
        "balanced_2000": {
            "cash": 0.10, "bond": 0.20, "etf": 0.40, "equity": 0.25, "crypto": 0.05,
        },
        "growth_10000": {
            "cash": 0.05, "bond": 0.10, "etf": 0.45, "equity": 0.30, "crypto": 0.10,
        },
    }


def run_scenario(cash, weights, trades_per_class, years, fee_per_trade=0.0):
    """Run each sleeve independently, then aggregate. Returns per-sleeve detail."""
    sleeves = {}
    total_end = 0.0
    total_start = 0.0
    for sleeve, w in weights.items():
        alloc = cash * w
        total_start += alloc
        if sleeve == "cash":
            # cash earns the hurdle itself (T-bill), no cost
            end = alloc * (1 + HURDLE_APR) ** years
            sleeves[sleeve] = dict(weight=w, start=alloc, end=end,
                                   ret_pct=(end / alloc - 1) * 100 if alloc else 0.0,
                                   mdd=0.0, n_trades=0)
        else:
            cls = {"bond": "BOND", "etf": "ETF", "equity": "EQUITY",
                   "crypto": "CRYPTO"}[sleeve]
            tr = trades_per_class[cls]
            path = equity_path(tr, alloc, fee_per_trade)
            end = path[-1]
            sleeves[sleeve] = dict(weight=w, start=alloc, end=end,
                                   ret_pct=(end / alloc - 1) * 100 if alloc else 0.0,
                                   mdd=max_drawdown(path), n_trades=len(tr))
        total_end += sleeves[sleeve]["end"]
    apr = cagr(total_start, total_end, years)
    return dict(start=total_start, end=total_end, apr=apr,
                excess_apr=excess_apr(apr), sleeves=sleeves)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="write json results here")
    ap.add_argument("--sims", type=int, default=2000, help="Monte Carlo book runs")
    ap.add_argument("--trades-per-class", type=int, default=0,
                    help="if 0, use the measured n per class")
    ap.add_argument("--years", type=float, default=1.0)
    ap.add_argument("--cost-profile", default="programme_sweep",
                    choices=sorted(COST_PROFILES_BP))
    ap.add_argument("--tp", type=float, default=None, help="take-profit %, optional")
    ap.add_argument("--sl", type=float, default=None, help="stop-loss %, optional")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    cost_bp = COST_PROFILES_BP[args.cost_profile]
    trades = {}
    for cls, meta in CLASS_INPUTS.items():
        if meta["expectancy_pct"] is None:
            trades[cls] = []
            continue
        n = args.trades_per_class or meta["n"]
        # Scale n to one year's worth of a personal book: a retail trader will
        # not do 3,726 crypto trades. Cap at 200 so the simulation is a book, not
        # the whole population. The cap is a modelling choice, stated as such.
        n = min(n, 200)
        trades[cls] = simulate_class(
            cls, n, meta["expectancy_pct"], SIGMA_PCT[cls], cost_bp,
            hold_days=int(args.years * 365), tp_pct=args.tp, sl_pct=args.sl,
            seed=args.seed + zlib.crc32(cls.encode()) % 1000,
        )

    results = {"meta": dict(generated_utc="2026-11-24", cost_bp=cost_bp,
                            cost_profile=args.cost_profile, hurdle_apr=HURDLE_APR,
                            tp=args.tp, sl=args.sl, years=args.years,
                            note="PAPER ONLY. Measured inputs, modeled dispersion."),
               "classes": {}, "scenarios": {}}

    for cls, tr in trades.items():
        if not tr:
            results["classes"][cls] = dict(n=0, verdict=CLASS_INPUTS[cls]["verdict"],
                                           note="no measured expectancy -- not simulated")
            continue
        rets = [t["ret_pct"] for t in tr]
        ci = bootstrap_ci(rets)
        results["classes"][cls] = dict(
            n=len(tr), mean_pct=st.fmean(rets), ci=ci,
            verdict=CLASS_INPUTS[cls]["verdict"],
            ci_excludes_zero=(ci is not None and (ci[0] > 0 or ci[1] < 0)),
            source=CLASS_INPUTS[cls]["source"],
        )

    for cash in (300, 500, 2000, 10000):
        allocs = portfolio_allocations(cash)
        key = [k for k in allocs if k.endswith(str(cash))][0]
        runs = []
        for s in range(args.sims):
            tp = {c: simulate_class(c, len(t),
                                    CLASS_INPUTS[c]["expectancy_pct"],
                                    SIGMA_PCT[c], cost_bp,
                                    hold_days=int(args.years * 365),
                                    tp_pct=args.tp, sl_pct=args.sl,
                                    seed=args.seed + s * 1000 + i)
                  for i, (c, t) in enumerate(trades.items()) if t}
            # equity sleeve gets a flat per-trade commission if a stock broker charges
            fee = 0.0
            r = run_scenario(cash, allocs[key], tp, args.years, fee)
            runs.append(r["apr"])
        ci = percentile_ci(runs)
        med = st.median(runs)
        results["scenarios"][key] = dict(
            cash=cash, weights=allocs[key],
            median_apr=med, mean_apr=st.fmean(runs), ci_apr=ci,
            excess_apr_median=excess_apr(med),
            ci_excess=(excess_apr(ci[0]), excess_apr(ci[1])) if ci else None,
            verdict=verdict_from_ci((excess_apr(ci[0]), excess_apr(ci[1])) if ci else None),
            share_beating_hurdle=sum(1 for a in runs if a > HURDLE_APR) / len(runs),
            share_losing=sum(1 for a in runs if a < 0) / len(runs),
            sleeves=r["sleeves"],
        )

    text = json.dumps(results, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
