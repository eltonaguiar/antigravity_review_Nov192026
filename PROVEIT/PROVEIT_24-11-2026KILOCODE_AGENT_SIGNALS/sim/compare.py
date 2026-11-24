#!/usr/bin/env python3
"""Is the philosophy better than just buying an index? And what do commissions
do to a small account? Stdlib only.

The sharpest question about any trading philosophy is not "does it beat zero"
but "does it beat the boring alternative". So each portfolio is compared with
100% index ETF, and with 100% T-bill cash.
"""
from __future__ import annotations
import statistics as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import proveit as P

PORTFOLIOS = {
    "cash_only":      {"cash": 1.0},
    "index_only":     {"etf": 1.0},
    "equity_only":    {"equity": 1.0},
    "crypto_only":    {"crypto": 1.0},
    "diversified":    {"cash": 0.10, "bond": 0.20, "etf": 0.40, "equity": 0.25, "crypto": 0.05},
}


def run(cash, weights, sims=800, cost="retail_crypto", seed0=0):
    cost_bp = P.COST_PROFILES_BP[cost]
    aprs = []
    for s in range(sims):
        tp = {}
        for i, (c, m) in enumerate(P.CLASS_INPUTS.items()):
            if m["expectancy_pct"] is None:
                continue
            tp[c] = P.simulate_class(c, min(m["n"], 200), m["expectancy_pct"],
                                     P.SIGMA_PCT[c], cost_bp, 365, seed=seed0 + s * 131 + i)
        aprs.append(P.run_scenario(cash, weights, tp, 1.0, 0.0)["apr"])
    med = st.median(aprs)
    ci = P.percentile_ci(aprs)
    return dict(median=med, ci=ci, beat_hurdle=sum(a > P.HURDLE_APR for a in aprs) / len(aprs),
                lose=sum(a < 0 for a in aprs) / len(aprs))


def main() -> int:
    print("=== Portfolio comparison, $10,000, retail costs, 1 year, 800 sims ===\n")
    print("%-14s %9s %22s %8s %8s" % ("portfolio", "medAPR", "ciAPR", "beatH", "lose"))
    base = None
    for name, w in PORTFOLIOS.items():
        r = run(10000, w)
        if name == "index_only":
            base = r["median"]
        print("%-14s %8.2f%% [%7.2f%%,%7.2f%%] %7.1f%% %7.1f%%" % (
            name, r["median"] * 100, r["ci"][0] * 100, r["ci"][1] * 100,
            r["beat_hurdle"] * 100, r["lose"] * 100))
    div = run(10000, PORTFOLIOS["diversified"])["median"]
    print("\ndiversified minus index_only on the median: %+.2f pp" % ((div - base) * 100))

    print("\n=== Commission sensitivity: $5 vs $1 vs $0 per trade, 20 trades/yr ===\n")
    print("%-10s %10s %10s %10s %10s" % ("account", "$0/trade", "$1/trade", "$5/trade", "$5 drag"))
    for cash in (300, 500, 2000, 10000):
        row = []
        for fee in (0.0, 1.0, 5.0):
            # 20 trades: drag is compounded, not additive
            end = cash * (1.05) ** 1  # assume 5% gross on the account for the fee test
            for _ in range(20):
                end = max(0.0, end * (1 + 0.05 / 20) - fee)
            row.append(end)
        print("%-10d %10.0f %10.0f %10.0f %9.1f%%" % (
            cash, row[0], row[1], row[2], (row[0] - row[2]) / cash * 100))
    print("\n(fee test assumes a 5% gross return on the account and 20 round trips;")
    print(" the $5 column is the classic full-service-stock commission.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
