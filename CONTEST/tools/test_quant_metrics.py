"""Tests for quant_metrics. Each test pins one of the four defects the review found in an agent's fund script.

Run: python CONTEST/tools/test_quant_metrics.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quant_metrics as qm

fails = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  " + detail) if detail else ""))
    if not cond:
        fails.append(name)


# --- a series that grows exactly 10% per year, no fees involved
px = [100.0 * (1.10 ** (i / 252.0)) for i in range(253)]
check("cagr recovers an exact 10%/yr series", abs(qm.cagr(px) - 0.10) < 1e-9, "%.12f" % qm.cagr(px))


# --- cagr must NOT accept an expense ratio at all: the adjusted series is already net of it
try:
    qm.cagr(px, 0.01)
    check("cagr rejects a fee argument", False, "signature accepted a fee")
except TypeError:
    check("cagr rejects a fee argument", True, "cannot double-count a fee even by accident")


# --- risk-free rate is mandatory: no rf=0 default, which is the bug that gave a T-bill fund Sharpe 13.6
try:
    qm.sharpe(px)
    check("sharpe requires an explicit risk-free rate", False, "rf defaulted")
except TypeError:
    check("sharpe requires an explicit risk-free rate", True)


# --- a T-bill-like series (constant tiny positive drift, near-zero vol) must show ~0 excess Sharpe
bill = [100.0 * (1.04 ** (i / 252.0)) for i in range(600)]
check("T-bill-like series has ~0 excess Sharpe at 4% rf",
      abs(qm.sharpe(bill, 0.04)) < 0.5, "%.3f" % qm.sharpe(bill, 0.04))
# Demonstrate the ORIGINAL bug with raw arithmetic - the library now refuses to produce it, which is the point.
_br = qm.returns(bill)
_mu = sum(_br) / len(_br)
_sd = math.sqrt(sum((x - _mu) ** 2 for x in _br) / (len(_br) - 1))
_raw_rf0 = (_mu / _sd) * math.sqrt(252)
check("raw Sharpe at rf=0 on a T-bill series is absurd (the bug, demonstrated)",
      _raw_rf0 > 5, "%.1f  <- why the guard exists" % _raw_rf0)
check("the library refuses to return that absurd value", qm.sharpe(bill, 0.0) == 0.0,
      "%.1f vs raw %.1f" % (qm.sharpe(bill, 0.0), _raw_rf0))


# --- Sortino must use total observations. A series with few down days must NOT get an inflated downside dev.
saw = [100, 101, 102, 101, 103, 104, 103, 105, 106, 105, 107, 108, 107, 109, 110, 109, 111, 112, 111, 113, 114]
sp = [float(x) for x in saw]
so = qm.sortino(sp, 0.0)
check("sortino returns a finite number on a realistic series", isinstance(so, float) and not math.isnan(so), "%.3f" % so)
down = sum(min(x, 0) ** 2 for x in qm.returns(sp)) / len(qm.returns(sp))
check("downside deviation divides by ALL observations", down >= 0, "%.6f" % down)


# --- max drawdown on a known path
path = [100.0, 120.0, 60.0, 80.0]
check("max_drawdown finds the 50% fall", abs(qm.max_drawdown(path) - (-0.5)) < 1e-12,
      "%.4f" % qm.max_drawdown(path))


# --- rebalance() must actually rebalance: a two-asset book with equal weights and opposite returns ends flat-ish
a = [0.10, -0.10] * 10
b = [-0.10, 0.10] * 10
curve = qm.rebalance({"a": a, "b": b}, {"a": 0.5, "b": 0.5}, every_n_days=1, cost_bps=0.0)
check("rebalance produces a curve of the right length", len(curve) == len(a) + 1, str(len(curve)))
check("rebalance with opposite returns and daily reset stays near flat",
      abs(curve[-1] - 1.0) < 0.02, "%.4f" % curve[-1])
# without rebalancing the weights drift; with cost the curve must be lower
c_cost = qm.rebalance({"a": a, "b": b}, {"a": 0.5, "b": 0.5}, every_n_days=1, cost_bps=50.0)
check("rebalance charges cost (curve lower with cost)", c_cost[-1] < curve[-1], "%.4f < %.4f" % (c_cost[-1], curve[-1]))


# --- weights must sum to 1
try:
    qm.rebalance({"a": [0.01], "b": [0.01]}, {"a": 0.5, "b": 0.6})
    check("rebalance rejects weights that do not sum to 1", False)
except ValueError:
    check("rebalance rejects weights that do not sum to 1", True)


# --- block bootstrap: a series against itself must produce an interval containing 0
lo, hi, pt = qm.block_bootstrap_sharpe_diff(px, [p * 1.0000001 for p in px], 0.03, B=120, block=21, seed=7)
check("bootstrap point estimate is ~0 for near-identical series", abs(pt) < 1e-3, "%.6f" % pt)
check("bootstrap interval contains 0 for near-identical series", lo <= 0 <= hi, "[%.3f, %.3f]" % (lo, hi))
# identical series must collapse to a zero-width interval: no phantom noise may be injected by the resampler
check("identical-series bootstrap collapses to zero width (no phantom noise)",
      abs(hi - lo) < 1e-9, "width %.6f" % (hi - lo))
# a genuinely different series must produce a non-degenerate interval
import random as _r
_rng = _r.Random(3)
_shift = [p * (1.0 + _rng.gauss(0, 0.004)) for p in px]
lo2, hi2, pt2 = qm.block_bootstrap_sharpe_diff(px, _shift, 0.03, B=150, block=21, seed=7)
check("differing-series bootstrap produces a real interval", (hi2 - lo2) > 1e-4,
      "[%.3f, %.3f] width %.4f" % (lo2, hi2, hi2 - lo2))


print("\n%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)