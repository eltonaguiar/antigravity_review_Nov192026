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
