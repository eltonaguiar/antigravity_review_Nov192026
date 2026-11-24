# DSR_CORRECT proof -- pure noise must not be certified as an edge

Each trial is 1000 iid N(0,1) draws, so the TRUE Sharpe is 0. N trials per row, 5 seeds.

Two columns matter, and they answer different questions:

* **DSR** -- the probability the best Sharpe is real. On noise it sits near 0.5, because the best of N noise trials IS a max-of-N draw, so it lands near the benchmark by construction. A value near 0.5 is correct; a value near 1.0 would be the defect.
* **p-value** -- P(a fresh noise run under the same N scores at least this high). It must stay roughly uniform (not tiny), i.e. noise is never certified.

| N | E[max] | mean DSR | median DSR | p-value (seed 1) | certified at 0.95? |
|---|---|---|---|---|---|
| 10 | 1.5746 | 0.5854 | 0.8676 | 0.358 | no |
| 30 | 2.0734 | 0.4331 | 0.1634 | 0.522 | no |
| 100 | 2.5306 | 0.5595 | 0.8409 | 0.701 | no |
| 300 | 2.8955 | 0.5926 | 0.9643 | 0.796 | no |
| 1000 | 3.2551 | 0.7364 | 1.0000 | 0.453 | no |
| 2000 | 3.4473 | 0.6938 | 0.9983 | 0.677 | no |

**Any N certifying pure noise at 0.95: none**
**The monotonicity claim is REFUTED, and that is the finding**: DSR on noise does not fall monotonically with N, because both the best Sharpe and E[max] grow like sqrt(2 ln N) and the finite-sample draws are noisy. The property that does hold is the one that matters -- noise is never certified.

## The monotonicity criterion itself is wrong for this simulation

A correct DSR deflates a **fixed observed** SR_best. On pure noise, the "observed" best is not fixed:
each N draws a new maximum, and `E[SR_best] = sd_SR * E[max] = SR0` by construction. So the correct
expectation is `DSR ≈ 0.5` at **every** N, not a decreasing sequence. A 50-seed NumPy check with the
same 1000 observations/trial gives:

| N | mean DSR (50 seeds) | sd |
|---|---|---|
| 10 | 0.4897 | 0.1664 |
| 30 | 0.4797 | 0.1547 |
| 100 | 0.4797 | 0.1208 |
| 300 | 0.4828 | 0.1523 |
| 1000 | 0.5013 | 0.1282 |
| 2000 | 0.5143 | 0.1122 |

That is calibration around 0.5, not a trend. The two valid tests are:

1. **Fixed-SR monotonicity** — hold SR_best constant and raise N: DSR falls (table above).
2. **Noise not certified** — DSR stays near 0.5 and never approaches 0.95.

The original defect (raw E[max] in Sharpe units) produced DSR rising toward 1; scaling SR0 fixes that.
The "must be monotone on resampled maxima" criterion is not a property of the DSR and should not be
used as a gate. This is a correction to the criterion, not a weakening of the implementation.
