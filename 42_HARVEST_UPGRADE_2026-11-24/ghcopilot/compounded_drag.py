#!/usr/bin/env python3
"""Linear vs compounded cost drag — and which question each one answers.

WHY
---
My published table computed "gross needed to net the hurdle" as
    hurdle + turns_per_year * round_trip_cost
which is a LINEAR approximation. Qwen3.6 Flash flagged that drag compounds. Their
conclusion was directionally right but their formula described the wrong quantity, so
both the original number and their correction need settling.

THE TWO QUESTIONS ARE DIFFERENT AND THEIR ANSWERS MOVE IN OPPOSITE DIRECTIONS:

  Q1 "What fraction of my capital does cost consume over the year?"
      = 1 - (1 - c)^N                <- COMPOUNDED, and it is SMALLER than N*c
      Linear N*c OVERSTATES this.

  Q2 "What gross return do I need to net a fixed hurdle?"
      Solve ((1+g_d)*(1-c))^N = 1+h  ->  g_ann = [(1+h)^(1/N)/(1-c)]^N - 1
      This is LARGER than h + N*c, because cost compounds against a growing base.
      Linear UNDERSTATES this.

So the linear figure was wrong in both directions depending on the question being asked.
The row that matters for a strategy-viability claim is Q2, and Q2 is WORSE than published.

HURDLE PROVENANCE (resolving a cross-check objection):
  tools/capacity_model.py  HURDLE_TBILL_APR = 0.0432, labelled MEASURED.
  Consumed at PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT_SIGNALS/sim/proveit.py:44.
  It is a T-bill APR. It is NOT the same quantity as the 5-year realised SGOV CAGR
  (3.89%) measured elsewhere, so the two are not in conflict - they are different
  measurements of different things over different windows. Both are reported below.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out" / "compounded_drag.json"

COST = {
    "fund":      (0.0,    0.0,    0.0),
    "bond ETF":  (0.6144, 0.6144, 0.6144),
    "ETF":       (6.7122, 6.7122, 6.7122),
    "FOREX":     (7.533,  7.533,  7.533),
    "equity":    (0.9756, 4.0124, 12.0749),
    "commodity": (20.0,   20.0,   20.0),
    "crypto":    (20.0,   36.0,   52.0),
}
HURDLE_TBILL = 0.0432          # tools/capacity_model.py HURDLE_TBILL_APR (MEASURED)
HURDLE_SGOV = 0.0389           # realised SGOV CAGR, 2021-11-15..2026-11-13
HOLDS = {"1d": 252.0, "1w": 252.0 / 5, "1m": 252.0 / 21}


def consumed(bp: float, n: float) -> float:
    """Q1: fraction of terminal wealth lost to cost, compounded."""
    return 1.0 - (1.0 - bp / 10000.0) ** n


def consumed_linear(bp: float, n: float) -> float:
    return n * bp / 100.0


def gross_needed_compounded(bp: float, n: float, h: float) -> float:
    """Q2: annual gross return required to net `h` after cost, compounded."""
    c = bp / 10000.0
    per = (1.0 + h) ** (1.0 / n) / (1.0 - c)
    return (per ** n - 1.0) * 100.0


def gross_needed_linear(bp: float, n: float, h: float) -> float:
    return (h * 100.0) + n * bp / 100.0


def main() -> int:
    print("=" * 84)
    print("Q2 — GROSS RETURN REQUIRED TO NET THE HURDLE (the viability question)")
    print("=" * 84)
    print(f"   hurdle = {HURDLE_TBILL*100:.2f}% (tools/capacity_model.py HURDLE_TBILL_APR, MEASURED)")
    print(f"\n   at 1-DAY turnover          linear      compounded      understated by")
    out = {}
    for cls, (lo, pt, hi) in COST.items():
        lin = gross_needed_linear(pt, HOLDS["1d"], HURDLE_TBILL)
        cmp_ = gross_needed_compounded(pt, HOLDS["1d"], HURDLE_TBILL)
        out[cls] = {"rt_bp": pt, "gross_1d_linear_pct": lin,
                    "gross_1d_compounded_pct": cmp_}
        print(f"   {cls:<12}{lin:>14.1f}%{cmp_:>16.1f}%{cmp_-lin:>17.1f}pp")

    print("\n   The published headline was 95.0% for crypto. Compounded it is 158.9%.")
    print("   The conclusion strengthens: this is not 'expensive', it is unreachable.")

    print("\n" + "=" * 84)
    print("Q1 — FRACTION OF CAPITAL CONSUMED (a different question, opposite direction)")
    print("=" * 84)
    print(f"   {'class':<12}{'rt bp':>8}{'1d linear':>12}{'1d compounded':>15}{'note':>12}")
    for cls, (lo, pt, hi) in COST.items():
        l, c_ = consumed_linear(pt, HOLDS["1d"]), consumed(pt, HOLDS["1d"])
        note = "linear OVERSTATES" if l > c_ else ""
        out[cls]["consumed_1d_linear_pct"] = l * 100
        out[cls]["consumed_1d_compounded_pct"] = c_ * 100
        print(f"   {cls:<12}{pt:>8.2f}{l:>11.1f}%{c_*100:>14.1f}%{note:>16}")

    print("\n   Crypto: linear says cost eats 90.7% of capital; compounded it eats 59.7%.")
    print("   Qwen's claim that compounded drag EXCEEDS the linear figure is backwards for")
    print("   this question - N*c is an upper bound on 1-(1-c)^N. But their instinct that the")
    print("   requirement gets worse is right, and it shows up in Q2 above, not in Q1.")

    print("\n" + "=" * 84)
    print("HURDLE SENSITIVITY — does 4.32% vs 3.89% change any verdict?")
    print("=" * 84)
    print(f"   {'class':<12}{'h=4.32%':>12}{'h=3.89%':>12}{'delta':>10}")
    for cls in ("equity", "ETF", "crypto"):
        a = gross_needed_compounded(COST[cls][1], HOLDS["1d"], HURDLE_TBILL)
        b = gross_needed_compounded(COST[cls][1], HOLDS["1d"], HURDLE_SGOV)
        print(f"   {cls:<12}{a:>11.1f}%{b:>11.1f}%{b-a:>9.1f}pp")
    print("   A 0.43pp hurdle change moves the 1-day requirement by ~1pp because the")
    print("   costly term is the compounding cost, not the hurdle. The verdicts are robust")
    print("   to the choice; the hurdle only matters in the low-cost rows.")

    print("\n" + "=" * 84)
    print("WHAT THE LINEAR FIGURES SHOULD HAVE BEEN LABELLED")
    print("=" * 84)
    print("   'hurdle + N*c' answers: rough cost as a share of ORIGINAL capital.")
    print("   It is NOT the gross return required. Publishing it as such understated every")
    print("   high-turnover row. Corrected table above uses the compounded solve.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"hurdle_tbill": HURDLE_TBILL, "hurdle_sgov": HURDLE_SGOV,
                               "rows": out}, indent=2))
    print(f"\n   written: {OUT.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
