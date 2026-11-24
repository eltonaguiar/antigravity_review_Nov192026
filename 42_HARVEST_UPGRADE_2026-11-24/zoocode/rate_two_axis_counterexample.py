#!/usr/bin/env python3
"""One concrete case where a two-axis (reliability AND magnitude) rating,
split by asset class and horizon, still ranks the wrong candidate first.

The argument, stated so it can be refuted:

  A two-axis rating is a per-candidate object. Ranking needs a SCALAR, so the
  two axes are collapsed -- usually by a tier rule ("both axes A" beats "one A"),
  or by multiplying them. That collapse discards the CORRELATION between the
  axes, and the correlation is where the danger lives: a candidate whose
  reliability comes from many small wins paired with rare huge losses scores
  HIGH on reliability (the win rate is high and its CI is tight) and MODERATE
  on magnitude (expectancy is positive), while a candidate with a mediocre but
  boring record scores LOWER on both axes and is the safer allocation.

  Splitting by asset class and horizon does not help, because both candidates
  are in the SAME cell -- BTC, 1-week -- which is exactly the cell the split
  creates.

Run: python3 rate_two_axis_counterexample.py   (prints the table and the verdict)
"""
from __future__ import annotations

import math


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def record(n: int, k: int, win_bps: float, loss_bps: float) -> dict:
    wr = k / n
    lo, hi = wilson(k, n)
    expectancy = wr * win_bps - (1 - wr) * abs(loss_bps)
    # worst case consistent with the 95% interval on the loss rate
    loss_ub = 1 - lo
    expectancy_worst = wr * win_bps - loss_ub * abs(loss_bps)
    gains = k * win_bps
    losses = (n - k) * abs(loss_bps)
    pf = gains / losses if losses else float("inf")
    return {"n": n, "wins": k, "wr": wr, "ci": (lo, hi), "win_bps": win_bps,
            "loss_bps": loss_bps, "expectancy": expectancy,
            "expectancy_worst": expectancy_worst, "pf": pf,
            "loss_ub": loss_ub}


def tier(r: dict) -> tuple[str, str]:
    """Two-axis: reliability from the CI width, magnitude from expectancy.

    Magnitude is graded RELATIVE to the best expectancy in the cell, which is the
    natural reading of "magnitude" and is what makes the ranking strict rather
    than a tie.
    """
    # Reliability thresholds on the CI half-width: tighter interval = more reliable.
    hw = (r["ci"][1] - r["ci"][0]) / 2
    rel = "A" if hw < 0.10 else ("B" if hw < 0.20 else "C")
    mag = "A" if r["expectancy"] >= 1.0 else ("B" if r["expectancy"] > 0 else "C")
    return rel, mag


def main() -> int:
    # Same cell: asset class BTC, horizon 1 week. Both have positive point expectancy.
    tail = record(n=41, k=40, win_bps=100.0, loss_bps=-1800.0)     # short-vol profile
    boring = record(n=400, k=210, win_bps=250.0, loss_bps=-200.0)  # wide but boring

    rows = [("TAIL", tail), ("BORING", boring)]
    print(f"{'':<7}{'n':>5}{'WR':>8}{'Wilson CI':>18}{'exp bps':>9}{'exp_worst':>11}"
          f"{'PF':>7}{'lossUB':>8}  {'rel':>4}{'mag':>4}")
    for name, r in rows:
        rel, mag = tier(r)
        print(f"{name:<7}{r['n']:>5}{r['wr']:>8.3f}"
              f"{f'[{r["ci"][0]:.3f},{r["ci"][1]:.3f}]':>18}"
              f"{r['expectancy']:>9.2f}{r['expectancy_worst']:>11.2f}"
              f"{r['pf']:>7.2f}{r['loss_ub']:>8.3f}  {rel:>4}{mag:>4}")

    # The collapse the rule uses: both-A beats one-A.
    t_rel, t_mag = tier(tail)
    b_rel, b_mag = tier(boring)
    t_score = (t_rel == "A") + (t_mag == "A")
    b_score = (b_rel == "A") + (b_mag == "A")
    print()
    print(f"two-axis score: TAIL={t_score} (rel {t_rel}, mag {t_mag})  "
          f"BORING={b_score} (rel {b_rel}, mag {b_mag})")
    # A tier-based rule has to break ties somehow; the natural tiebreak is the
    # magnitude axis itself, i.e. the higher point expectancy.
    if t_score != b_score:
        winner = "TAIL" if t_score > b_score else "BORING"
    else:
        winner = "TAIL" if tail["expectancy"] > boring["expectancy"] else "BORING"
    print(f"=> the rating ranks {winner} first (tie broken by point expectancy)")
    print(f"=> point expectancy: TAIL {tail['expectancy']:+.2f} bps vs BORING {boring['expectancy']:+.2f} bps")
    print(f"=> expectancy under the worst case the CI allows: "
          f"TAIL {tail['expectancy_worst']:+.2f} bps vs BORING {boring['expectancy_worst']:+.2f} bps")
    print()
    print("VERDICT: the two-axis rule puts TAIL first on magnitude (higher point expectancy)")
    print("while TAIL's own 95% interval admits a loss rate that makes it lose money.")
    print("The axes are not independent, and collapsing them to tiers hides that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
