#!/usr/bin/env python3
"""dsr_correct.py - Deflated Sharpe Ratio that gets HARSHER as trials grow.

The defect in dsr.py: it computes Phi(SR_best / s_trials), which RISES with N
because s_trials stabilises while the numerator does not shrink -- so screening
MORE variants makes the number look BETTER. That is backwards: more searching
means the best result is more likely to be luck.

This file implements the Bailey & Lopez de Prado (2014) form, whose null
benchmark is the EXPECTED MAXIMUM of N standard normals:

    E[max] = (1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e))
             (gamma = Euler-Mascheroni ~ 0.5772, e = Euler's number)

    DSR = Phi( (SR_star - E[max] * s_trials) * sqrt(n - 1)
               / sqrt( 1 - g3 * SR_star + ((g4 - 1) / 4) * SR_star^2 ) )

where SR_star = SR_best / s_trials (the best Sharpe in units of the cross-trial
sd), g3/g4 are the skewness and kurtosis of the RETURNS (not of the Sharpes),
and n is the number of return observations behind the best trial.

Two things make it harsher with N:
  * E[max] grows like sqrt(2 ln N), so the benchmark subtracted rises.
  * the denominator is the PSR standard error, which does not shrink with N.

If the return moments are unknown, pass them; with a single Sharpe and no
return series the honest default is g3=0, g4=3 (normal), stated explicitly.

Usage:
  python3 dsr_correct.py --db trial_ledger.db [--n 250]
  python3 dsr_correct.py --proof out.md     # the noise simulation
"""
from __future__ import annotations

import argparse
import math
import random
import sqlite3
from pathlib import Path

EULER_GAMMA = 0.5772156649015329


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def expected_max_of_n_normals(n_trials: int) -> float:
    """E[max of N iid standard normals] -- the null benchmark.

    n=1 is the degenerate case (no search), so there is nothing to deflate.
    """
    if n_trials < 2:
        return 0.0
    n = float(n_trials)
    return ((1 - EULER_GAMMA) * norm_ppf(1 - 1 / n)
            + EULER_GAMMA * norm_ppf(1 - 1 / (n * math.e)))


def dsr_correct(sharpes: list[float], n_obs: int,
                g3: float = 0.0, g4: float = 3.0) -> dict:
    """Deflated Sharpe Ratio over a set of trial Sharpes.

    sharpes : the per-trial Sharpe ratios (all of them -- a pruned log lies)
    n_obs   : return observations behind the BEST trial
    g3, g4  : skew and kurtosis of those returns (default: normal)
    """
    k = len(sharpes)
    if k == 0:
        return {"dsr": None, "n_trials": 0, "sr_best": None, "sr_star": None,
                "e_max": None}
    sr_best = max(sharpes)
    if k < 2:
        sd = 0.0
    else:
        m = sum(sharpes) / k
        sd = math.sqrt(sum((s - m) ** 2 for s in sharpes) / (k - 1))
    e_max = expected_max_of_n_normals(k)
    # The null benchmark is in the SAME units as SR_best, so it must be scaled
    # by the cross-trial standard deviation. Using E[max] raw is the defect:
    # it is a z-score, not a Sharpe ratio.
    sr0 = sd * e_max
    denom = 1 - g3 * sr_best + ((g4 - 1) / 4) * sr_best ** 2
    if denom <= 0 or n_obs < 2:
        return {"dsr": None, "n_trials": k, "sr_best": sr_best,
                "sr0": sr0, "e_max": e_max, "sd_sr": sd, "g3": g3, "g4": g4}
    z = (sr_best - sr0) * math.sqrt(n_obs - 1) / math.sqrt(denom)
    return {"dsr": norm_cdf(z), "n_trials": k, "sr_best": sr_best,
            "sr0": sr0, "e_max": e_max, "sd_sr": sd, "g3": g3, "g4": g4, "z": z}


def dsr_from_db(db: str, n_obs: int, use_oos: bool = True) -> dict:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        col = "sharpe_oos" if use_oos else "sharpe_is"
        rows = con.execute(
            f"select {col} from trials where {col} is not null").fetchall()
    finally:
        con.close()
    return dsr_correct([float(r[0]) for r in rows], n_obs)


# ---------------------------------------------------------------------------
# The proof: pure noise, true Sharpe 0, DSR must FALL as N rises.
# ---------------------------------------------------------------------------
def simulate_noise_best(n_trials: int, seed: int, n_obs: int = 1000):
    """N independent pure-noise trials -> (Sharpes, returns of the best trial)."""
    rng = random.Random(seed)
    sharpes = []
    best_sr = -1e9
    best_returns = None
    for _ in range(n_trials):
        xs = [rng.gauss(0.0, 1.0) for _ in range(n_obs)]
        m = sum(xs) / n_obs
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n_obs - 1))
        sr = m / sd if sd else 0.0
        sharpes.append(sr)
        if sr > best_sr:
            best_sr = sr
            best_returns = xs
    return sharpes, best_returns


def _moments(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    m = sum(xs) / n
    m2 = sum((x - m) ** 2 for x in xs) / n
    if m2 <= 0:
        return 0.0, 3.0
    g3 = (sum((x - m) ** 3 for x in xs) / n) / (m2 ** 1.5)
    g4 = (sum((x - m) ** 4 for x in xs) / n) / (m2 * m2)
    return g3, g4


def _mc_pvalue(n_trials: int, seed: int) -> float:
    """p = P(DSR of pure noise under the SAME N is at least as large as the observed one).

    This is the honest test for a NOISE sample. A noise simulation's own best
    Sharpe is itself a draw from the max-of-N distribution, so E[max] as a
    benchmark leaves a ~50% chance of exceeding it -- DSR near 0.5 on noise is
    CORRECT behaviour, not a defect. What must hold is that the p-value is
    roughly uniform, i.e. noise is not certified at 0.95.
    """
    rng = random.Random(seed)
    sharpes = simulate_noise(n_trials, seed, 1000)
    d = dsr_correct(sharpes, 1000)["dsr"] or 0.0
    hits, draws = 0, 200
    for _ in range(draws):
        null = simulate_noise(n_trials, rng.randrange(10 ** 9), 1000)
        nd = dsr_correct(null, 1000)["dsr"] or 0.0
        if nd >= d:
            hits += 1
    return (hits + 1) / (draws + 1)


def proof(out_path: Path, ns: list[int], seeds: list[int], n_obs: int) -> int:
    lines = ["# DSR_CORRECT proof -- pure noise, scaled SR0", "",
             f"Each trial is {n_obs} iid N(0,1) draws, so the TRUE Sharpe is 0. "
             f"N trials per row, {len(seeds)} seeds, DSR averaged across seeds.", "",
             "Formula under test:",
             "",
             "    SR0 = sd_SR * E[max of N standard normals]",
             "    DSR = Phi( (SR_best - SR0) * sqrt(n_obs - 1)",
             "               / sqrt(1 - g3*SR_best + ((g4-1)/4)*SR_best^2) )",
             "",
             "g3/g4 are the skewness and kurtosis of the BEST trial's returns.", "",
             "| N | E[max] | mean sd_SR | mean SR0 | mean DSR | min | max |",
             "|---|---|---|---|---|---|---|"]
    means = []
    for n in ns:
        vals, sds, sr0s = [], [], []
        for seed in seeds:
            sh, best = simulate_noise_best(n, seed, n_obs)
            g3, g4 = _moments(best)
            r = dsr_correct(sh, n_obs, g3=g3, g4=g4)
            if r["dsr"] is not None:
                vals.append(r["dsr"]); sds.append(r["sd_sr"]); sr0s.append(r["sr0"])
        m = sum(vals) / len(vals)
        means.append(m)
        lines.append(f"| {n} | {expected_max_of_n_normals(n):.4f} | "
                     f"{sum(sds)/len(sds):.4f} | {sum(sr0s)/len(sr0s):.4f} | "
                     f"{m:.4f} | {min(vals):.4f} | {max(vals):.4f} |")
    monotone = all(means[i] >= means[i+1] for i in range(len(means)-1))
    lines += ["", f"**Monotone non-increasing in N: {monotone}**",
              f"**DSR at N={ns[0]}: {means[0]:.4f}**",
              f"**DSR at N={ns[-1]}: {means[-1]:.4f}**", ""]
    if not monotone:
        lines += [
            "**It still fails, and the mechanism is structural, not a scaling bug.**",
            "The proof draws a FRESH max for every N. Under the null, E[SR_best] = sd_SR * E[max]",
            "by construction, so DSR is calibrated to ~0.5 at every N; the residual is sampling",
            "noise in the max, not a trend. Monotonicity is a property of a FIXED observed SR_best",
            "compared against a growing N. Recomputing the best Sharpe at each N tests calibration,",
            "not monotonicity. To test monotonicity, hold SR_best fixed (e.g. 0.10 with sd_SR 0.03)",
            "and raise N: DSR must fall. That is stated here rather than loosening the criterion.",
            "",
            "The correct null claim is: noise is not certified (DSR stays near 0.5, not 0.95).",
            "The monotonicity claim, as written with a resampled best, is refuted."]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if monotone else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db")
    ap.add_argument("--n", type=int, default=250, help="return observations behind the best trial")
    ap.add_argument("--is", action="store_true", help="use sharpe_is instead of sharpe_oos")
    ap.add_argument("--proof", help="write the noise-simulation proof to this path")
    a = ap.parse_args()
    if a.proof:
        return proof(Path(a.proof), ns=[10, 30, 100, 300, 1000, 2000],
                     seeds=[1, 2, 3, 4, 5], n_obs=1000)
    if not a.db:
        ap.error("give --db or --proof")
    r = dsr_from_db(a.db, a.n, use_oos=not a.is_)
    print(f"trials={r['n_trials']} best_sharpe={r['sr_best']} "
          f"sr_star={r['sr_star']} E[max]={r['e_max']}")
    print(f"DSR={r['dsr']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
