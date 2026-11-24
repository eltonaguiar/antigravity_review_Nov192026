# DSR on pure noise — the expected values any implementation must reproduce

**Purpose.** Two independent implementations of a Deflated Sharpe Ratio have now failed, so the
next attempt needs a reference to be checked against rather than an opinion. These numbers were
computed here, from first principles, and anyone can re-derive them in one command.

**Setup that produces them:** each trial is `T = 1000` iid `N(0,1)` draws, so the TRUE Sharpe is
exactly 0. `N` trials per run. `SR_best` is the highest per-trial Sharpe. `sd_SR` is the standard
deviation of the per-trial Sharpe estimates **across trials** — this is the quantity that must scale
the null benchmark and is the most common place to go wrong.

```
SR0 = sd_SR * ( (1 - gamma) * Phi_inv(1 - 1/N) + gamma * Phi_inv(1 - 1/(N*e)) )
DSR = Phi( (SR_best - SR0) * sqrt(T - 1) / sqrt(1 - skew*SR_best + ((kurt - 1)/4)*SR_best^2) )
```

`gamma` = 0.5772156649 (Euler–Mascheroni), `e` = Euler's number, `Phi` = standard normal CDF.
For normal returns the denominator is 1, so it drops out of this particular proof — but it must be
present, because a real trial set is rarely normal.

## Expected result — 200 seeds per row

| N | mean DSR | sd | min | max |
|---:|---:|---:|---:|---:|
| 10 | 0.5178 | 0.168 | 0.108 | 0.927 |
| 30 | 0.4990 | 0.144 | 0.204 | 0.837 |
| 100 | 0.5126 | 0.146 | 0.219 | 0.956 |
| 300 | 0.4984 | 0.133 | 0.247 | 0.924 |
| 1000 | 0.4987 | 0.139 | 0.266 | 0.958 |
| 2000 | 0.5048 | 0.129 | 0.255 | 0.926 |

## What this means for acceptance — and a criterion I got wrong

The correct statistic is **flat at chance (~0.50) at every N**. It is *not* monotonically decreasing:
seed-to-seed noise moves the mean by about ±0.02 in either direction. **Strict monotonicity is
therefore the wrong test**, and asking for it invites an implementation that is tuned to pass rather
than one that is correct. (I asked an agent for exactly that. It is recorded here so the mistake is
not repeated.)

Accept an implementation only if all three hold:

1. **Mean DSR stays near 0.5 at every N** — no upward trend, no drift toward 1.
2. **It does not approach 1 as N grows.** This is the property the defect violates most visibly.
3. **A genuinely strong trial still scores high.** On noise, DSR must stay at chance; on a real
   signal (e.g. one trial with annualised Sharpe 1.5 over 1000 days) DSR must rise toward 1. A
   function that returns 0.5 for everything fails this check just as badly as one that returns 1.

## Why this matters — the measured contrast

| N | `dsr.py` (the defect) | correct implementation |
|---:|---:|---:|
| 10 | 0.931952 | **0.518** |
| 30 | 0.991424 | **0.499** |
| 100 | 0.994558 | **0.513** |
| 2000 | **0.999858** | **0.505** |

The broken one **climbs to near-certainty on data with no edge whatsoever**. The correct one sits at
a coin flip. That single column is the whole argument for not quoting a DSR computed by the current
implementation.

**Direction of the error, which matters for the published pages:** this defect only ever *inflates*.
So a published DSR of 0.318 or 0.815 against a 0.95 gate is a **rejection that stays rejected** if the
formula is fixed — the true value would be lower still. No published acceptance exists (14 numeric
DSRs live, max 0.815, zero at or above the gate), and none needs pulling. The exposure is the *next*
acceptance computed before this is fixed.

## Reproduce it

```python
import math, statistics as st, random
Phi      = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
GAMMA, T = 0.5772156649, 1000
# Phi_inv via bisection on Phi; then for each N and each seed:
#   draw N trials of T normals, take SR_best = max(mean/sd),
#   sd_SR = pstdev(all per-trial Sharpes), SR0 as above, DSR = Phi((SR_best - SR0)*sqrt(T-1))
```

Five seeds is not enough to see the flatness — the sd column above is 0.13–0.17, so a five-seed mean
carries roughly ±0.06 of noise. Use 200 seeds when judging an implementation, or a 5-seed run can read
as "monotone" or "not monotone" purely by luck.
