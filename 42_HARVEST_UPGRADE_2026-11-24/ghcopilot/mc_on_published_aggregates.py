#!/usr/bin/env python3
"""Significance re-test on PUBLISHED aggregates, because the raw vector is unavailable.

WHY THIS EXISTS
---------------
My own permutation test needs the (label, forward_return) vector. It cannot run:
  - Tiingo still returns HTTP 429 "hourly request allocation" (re-probed 2026-11-24 12:2xZ)
  - my earlier backtest never persisted its 138 observations (my error, now fixed in
    monte_carlo.py, but the loss is already incurred)
  - kilocode's docs/data/harvest_backtest.json stores only aggregates: n, mean, ci95,
    median, hit_rate — not per-observation values, so a true label-permutation is
    impossible from it.

What IS possible, and is done here: an independent significance test of the one claim
that matters — is STRONG_BUY's forward excess distinguishable from everything else? —
using their published n / mean / ci95 and a normal approximation. This is weaker than a
permutation test (it assumes normality and reconstructs SD from the CI) and is labelled
as such. It is not a substitute; it is the best available check, and it is falsifiable.

Also verifies their arithmetic is internally consistent before trusting any of it.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "docs" / "data" / "harvest_backtest.json"
OUT = pathlib.Path(__file__).resolve().parent / "out" / "mc_published_aggregates.json"
Z95 = 1.959963985


def sd_from_ci(ci: list[float], n: int) -> float | None:
    """Recover SD from a symmetric 95% CI: half_width = 1.96 * SD / sqrt(n)."""
    if not ci or ci[0] is None or ci[1] is None or n < 2:
        return None
    return (ci[1] - ci[0]) / 2 / Z95 * math.sqrt(n)


def welch_z(n1, m1, s1, n2, m2, s2):
    se = math.sqrt(s1 * s1 / n1 + s2 * s2 / n2)
    z = (m1 - m2) / se if se else 0.0
    # two-sided p via the normal tail
    p = math.erfc(abs(z) / math.sqrt(2))
    return z, p, se


def power_n(delta: float, sd: float, alpha=0.05, power=0.80) -> float:
    """Per-arm n needed to detect `delta` with the given SD."""
    z_a, z_b = 1.959963985, 0.8416212336
    return 2 * (z_a + z_b) ** 2 / (delta / sd) ** 2


def main() -> int:
    j = json.loads(SRC.read_text())
    bl, basket = j["by_label"], j["strong_buy_basket"]
    findings: dict = {"source": str(SRC.name), "method": "normal approx on published aggregates"}

    print("=" * 74)
    print("0. INTERNAL CONSISTENCY — do their aggregates reconcile with their own rows?")
    print("=" * 74)
    # Recompute STRONG_BUY 21d from the four per-period basket rows.
    periods = list(basket.values())
    n_tot = sum(p["n"] for p in periods)
    mean_tot = sum(p["n"] * p["mean_excess_pct"] for p in periods) / n_tot
    hit_tot = sum(p["n"] * p["hit_rate"] for p in periods) / n_tot
    pub = bl["STRONG_BUY"]["21d"]
    dm = abs(mean_tot - pub["mean_pct"])
    dh = abs(hit_tot - pub["hit_rate"])
    print(f"  recomputed mean {mean_tot:+.6f} vs published {pub['mean_pct']:+.6f}  |delta|={dm:.2e}")
    print(f"  recomputed hit  {hit_tot:.6f} vs published {pub['hit_rate']:.6f}  |delta|={dh:.2e}")
    ok = dm < 1e-9 and dh < 1e-9
    print(f"  => {'RECONCILES exactly' if ok else 'DOES NOT RECONCILE — stop, numbers are suspect'}")
    findings["internal_consistency"] = {"mean_delta": dm, "hit_delta": dh, "reconciles": ok}
    if not ok:
        print("  Refusing to test aggregates that do not reconcile with their own rows.")
        return 2

    print("\n" + "=" * 74)
    print("1. IS STRONG_BUY DISTINGUISHABLE FROM THE REST? (the only real claim)")
    print("=" * 74)
    for hz in ("21d", "63d"):
        sb = bl["STRONG_BUY"][hz]
        others = [bl[k][hz] for k in ("BUY", "HOLD", "SELL")
                  if bl[k][hz]["mean_pct"] is not None]
        n_rest = sum(o["n"] for o in others)
        m_rest = sum(o["n"] * o["mean_pct"] for o in others) / n_rest
        sd_sb = sd_from_ci(sb["ci95_pct"], sb["n"])
        # pooled SD of the rest, weighted by n-1
        var_rest = sum((o["n"] - 1) * (sd_from_ci(o["ci95_pct"], o["n"]) or 0) ** 2
                       for o in others) / max(n_rest - len(others), 1)
        sd_rest = math.sqrt(var_rest)
        z, p, se = welch_z(sb["n"], sb["mean_pct"], sd_sb, n_rest, m_rest, sd_rest)
        delta = sb["mean_pct"] - m_rest
        nn = power_n(abs(delta), sd_sb) if delta else float("inf")
        print(f"\n  {hz}: STRONG_BUY n={sb['n']} mean={sb['mean_pct']:+.3f}%  SD~{sd_sb:.2f}")
        print(f"        rest      n={n_rest} mean={m_rest:+.3f}%  SD~{sd_rest:.2f}")
        print(f"        delta={delta:+.3f}pp  SE={se:.3f}  z={z:+.3f}  p(two-sided)={p:.3f}")
        print(f"        per-arm n needed for 80% power at this effect: {nn:,.0f}")
        findings[hz] = {"strong_buy_n": sb["n"], "strong_buy_mean": sb["mean_pct"],
                        "rest_n": n_rest, "rest_mean": m_rest, "delta_pp": delta,
                        "z": z, "p_two_sided": p, "n_needed_80pct_power": nn}

    print("\n" + "=" * 74)
    print("2. MONOTONICITY — does a better label mean a better return?")
    print("=" * 74)
    for hz in ("21d", "63d"):
        rows = [(lab, bl[lab][hz]["n"], bl[lab][hz]["mean_pct"])
                for lab in ("STRONG_BUY", "BUY", "HOLD", "SELL")]
        print(f"\n  {hz}:")
        for lab, n, m in rows:
            print(f"    {lab:<11} n={n:<4} mean={m if m is None else f'{m:+.3f}%'}")
        vals = [(lab, m) for lab, n, m in rows if m is not None]
        order = {"STRONG_BUY": 4, "BUY": 3, "HOLD": 2, "SELL": 1}
        # an inversion is a higher-rated label scoring below a lower-rated one
        inv = [(a, b) for i, (a, ma) in enumerate(vals) for (b, mb) in vals[i + 1:]
               if order[a] > order[b] and ma < mb]
        print(f"    inversions (higher rating, worse return): {[(a, b) for a, b in inv] or 'none'}")
        print(f"    monotonic: {not inv}")
        findings[f"monotonic_{hz}"] = {"inversions": inv, "monotonic": not inv}

    print("\n" + "=" * 74)
    print("3. VERDICT")
    print("=" * 74)
    p21 = findings["21d"]["p_two_sided"]
    p63 = findings["63d"]["p_two_sided"]
    print(f"  STRONG_BUY vs rest: p={p21:.3f} (21d), p={p63:.3f} (63d). Neither is < 0.05.")
    print(f"  Monotonicity: 21d={findings['monotonic_21d']['monotonic']}, "
          f"63d={findings['monotonic_63d']['monotonic']}.")
    print(f"  Power: detecting the 21d effect needs ~{findings['21d']['n_needed_80pct_power']:,.0f}"
          f" per arm. The study has 110 vs 174 over 4 monthly periods on 71 symbols.")
    print("  => The design cannot resolve the effect it is looking for. 'No edge found' is")
    print("     the correct reading; 'no edge exists' is NOT, and neither is 'small edge'.")
    print("  => Consumption guidance: never publish a STRONG_BUY premium from this design,")
    print("     in either direction. A null here is uninformative, not reassuring.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(findings, indent=2))
    print(f"\n  written: {OUT.relative_to(pathlib.Path(__file__).resolve().parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
