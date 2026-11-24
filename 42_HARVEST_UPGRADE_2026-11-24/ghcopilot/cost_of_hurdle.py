#!/usr/bin/env python3
"""Cost of record -> annualised drag -> required gross edge, by asset class.

WHY
---
An external review (AskAnyModel / zoocode, 2026-11-24) correctly insists that cost is
the decisive number, then states: "At ~40 bp and weekly turnover that is ~2%/yr of drag."
That sentence is checkable, and it is wrong by an order of magnitude as written. This
script settles it from our own cost-of-record table instead of arguing.

COSTS ARE TAKEN FROM THIS REPO, NOT INVENTED:
  README.md  "Cost of record — measured, not assumed"
    fund 0 | bond ETF 0.6144 bp | ETF 6.7122 bp | FOREX 7.533 bp
    equity 12.0749 bp | commodity 20 bp | crypto 20-52 bp
  BUT 37_BUFFY_DRAFT_PATCHES_2026-11-23/03_equity_cost_settlement.md supersedes the
  single-number equity reading: 12.0749 is a CEILING (1-min bar range, 13 megacaps),
  4.0124 is the CENTRAL point estimate (Roll+SEC, 190/191 names), 0.9756 is the FLOOR,
  and 8.0248 is the gate. Quoting 12.0749 as "the cost" is explicitly named there as
  the error to stop making. So equity is carried as a bracket here.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out" / "cost_of_hurdle.json"
TRADING_DAYS = 252

# round-trip cost in bp. (low, point, high) — None where a single measured value exists.
COST_BP = {
    "fund":            (0.0,    0.0,    0.0),
    "bond ETF":        (0.6144, 0.6144, 0.6144),
    "ETF":             (6.7122, 6.7122, 6.7122),
    "FOREX":           (7.533,  7.533,  7.533),
    "equity":          (0.9756, 4.0124, 12.0749),   # floor / central(ceiling handled in note)
    "commodity":       (20.0,   20.0,   20.0),
    "crypto":          (20.0,   36.0,   52.0),      # band 20-52, point = midpoint
}

HOLDS = [("1 day", 1), ("1 week", 5), ("2 weeks", 10), ("1 month", 21),
         ("3 months", 63), ("1 year", 252)]


def drag_pct_per_year(bp: float, hold_days: int) -> float:
    """Annualised cost drag: turns/yr x round-trip cost."""
    return (TRADING_DAYS / hold_days) * bp / 100.0   # bp -> % is /100


def main() -> int:
    print("=" * 78)
    print("1. THE CLAIM UNDER TEST")
    print('   "At ~40 bp and weekly turnover that is ~2%/yr of drag."')
    print("=" * 78)
    for bp, label in ((40.0, "40 bp (as quoted)"), (36.0, "crypto point 36 bp"),
                      (4.0124, "equity central 4.0124 bp")):
        d = drag_pct_per_year(bp, 5)
        print(f"   {label:<28} weekly (5d) -> {d:6.2f}% per year")
    exact_2 = 2.0 * 100 / (TRADING_DAYS / 5)      # bp per round turn that yields 2%/yr weekly
    print(f"\n   2.0%/yr at weekly turnover requires a round trip of {exact_2:.2f} bp.")
    print(f"   equity central {COST_BP['equity'][1]} bp gives "
          f"{drag_pct_per_year(COST_BP['equity'][1],5):.2f}%/yr — that is where 2% comes from.")
    print(f"   40 bp at weekly gives {drag_pct_per_year(40.0,5):.2f}%/yr — "
          f"{drag_pct_per_year(40.0,5)/2.0:.1f}x the stated figure.")
    print("   => The 2%/yr number is RIGHT but belongs to EQUITY AT CENTRAL COST.")
    print("      Attaching it to 40 bp conflates the crypto band with the equity estimate.")
    verdict = {"claim_bp": 40.0, "claim_drag_pct_yr": drag_pct_per_year(40.0, 5),
               "bp_needed_for_2pct_weekly": exact_2,
               "equity_central_drag_pct_yr": drag_pct_per_year(COST_BP["equity"][1], 5)}

    print("\n" + "=" * 78)
    print("2. ANNUALISED DRAG BY CLASS x HOLDING PERIOD (point estimate)")
    print("=" * 78)
    hdr = f"   {'class':<12}{'rt bp':>8}" + "".join(f"{h:>12}" for h, _ in HOLDS)
    print(hdr)
    grid = {}
    for cls, (lo, pt, hi) in COST_BP.items():
        row = [drag_pct_per_year(pt, d) for _, d in HOLDS]
        grid[cls] = dict(zip([h for h, _ in HOLDS], row))
        print(f"   {cls:<12}{pt:>8.2f}" + "".join(f"{v:>11.1f}%" for v in row))

    print("\n" + "=" * 78)
    print("3. EQUITY BRACKET — why a single number must not be quoted")
    print("=" * 78)
    lo, pt, hi = COST_BP["equity"]
    for label, bp in (("floor 0.9756", lo), ("central 4.0124", pt), ("ceiling 12.0749", hi)):
        print(f"   {label:<18} weekly -> {drag_pct_per_year(bp,5):5.2f}%/yr   "
              f"monthly -> {drag_pct_per_year(bp,21):5.2f}%/yr")
    print(f"   ceiling/central = {hi/pt:.2f}x ; ceiling/floor = {hi/lo:.2f}x")
    print("   The external review quotes 12.07 as 'our measured round turn'.")
    print("   Our own settlement doc calls that quote THE error to stop making.")
    bracket = {"floor": lo, "central": pt, "ceiling": hi,
               "ceiling_over_central": hi / pt, "ceiling_over_floor": hi / lo}

    print("\n" + "=" * 78)
    print("4. WHAT GROSS EDGE IS REQUIRED TO NET A 4.32% HURDLE?")
    print("=" * 78)
    HURDLE = 4.32
    print(f"   {'class':<12}" + "".join(f"{h:>12}" for h, _ in HOLDS))
    req = {}
    for cls, (lo2, pt2, hi2) in COST_BP.items():
        vals = [HURDLE + drag_pct_per_year(pt2, d) for _, d in HOLDS]
        req[cls] = dict(zip([h for h, _ in HOLDS], vals))
        print(f"   {cls:<12}" + "".join(f"{v:>11.1f}%" for v in vals))
    print("\n   Reading: at 1-day turnover, crypto needs >100%/yr gross to net 4.32%.")
    print("   That is not a strategy-quality statement; it is arithmetic, and it is why")
    print("   any 'scalping' suggestion carrying this cost band is dead on arrival.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"claim_verdict": verdict, "drag_pct_per_year": grid,
                               "equity_bracket": bracket, "required_gross_pct": req,
                               "hurdle_pct": HURDLE,
                               "cost_bp_source": "README.md cost-of-record + "
                               "37_BUFFY_DRAFT_PATCHES_2026-11-23/03_equity_cost_settlement.md"},
                              indent=2))
    print(f"\n   written: {OUT.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
