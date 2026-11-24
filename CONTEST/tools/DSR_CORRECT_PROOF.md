# DSR_CORRECT proof -- pure noise, scaled SR0

Each trial is 1000 iid N(0,1) draws, so the TRUE Sharpe is 0. N trials per row, 5 seeds, DSR averaged across seeds.

Formula under test:

    SR0 = sd_SR * E[max of N standard normals]
    DSR = Phi( (SR_best - SR0) * sqrt(n_obs - 1)
               / sqrt(1 - g3*SR_best + ((g4-1)/4)*SR_best^2) )

g3/g4 are the skewness and kurtosis of the BEST trial's returns.

| N | E[max] | mean sd_SR | mean SR0 | mean DSR | min | max |
|---|---|---|---|---|---|---|
| 10 | 1.5746 | 0.0252 | 0.0398 | 0.5056 | 0.4333 | 0.5735 |
| 30 | 2.0734 | 0.0282 | 0.0584 | 0.5107 | 0.3633 | 0.6704 |
| 100 | 2.5306 | 0.0299 | 0.0756 | 0.5281 | 0.4141 | 0.7245 |
| 300 | 2.8955 | 0.0310 | 0.0898 | 0.5348 | 0.3893 | 0.7503 |
| 1000 | 3.2551 | 0.0314 | 0.1022 | 0.6035 | 0.4329 | 0.7300 |
| 2000 | 3.4473 | 0.0314 | 0.1082 | 0.5653 | 0.4350 | 0.6787 |

**Monotone non-increasing in N: False**
**DSR at N=10: 0.5056**
**DSR at N=2000: 0.5653**

**It still fails, and the mechanism is structural, not a scaling bug.**
The proof draws a FRESH max for every N. Under the null, E[SR_best] = sd_SR * E[max]
by construction, so DSR is calibrated to ~0.5 at every N; the residual is sampling
noise in the max, not a trend. Monotonicity is a property of a FIXED observed SR_best
compared against a growing N. Recomputing the best Sharpe at each N tests calibration,
not monotonicity. To test monotonicity, hold SR_best fixed (e.g. 0.10 with sd_SR 0.03)
and raise N: DSR must fall. That is stated here rather than loosening the criterion.

The correct null claim is: noise is not certified (DSR stays near 0.5, not 0.95).
The monotonicity claim, as written with a resampled best, is refuted.
## Control: hold SR_best fixed, raise N

The property the criterion intends is visible only when the observed best Sharpe is fixed.
With SR_best = 0.10, sd_SR = 0.03, n_obs = 1000, g3 = 0, g4 = 3:

| N | SR0 | DSR |
|---|---|---|
| 10 | 0.0472 | 0.9523 |
| 30 | 0.0622 | 0.8839 |
| 100 | 0.0759 | 0.7767 |
| 300 | 0.0869 | 0.6610 |
| 1000 | 0.0977 | 0.5296 |
| 2000 | 0.1034 | 0.4570 |

Monotone decreasing, as a deflated Sharpe must be. The failing table above recomputes the
maximum at every N, so it tests calibration under the null, not monotonicity.
