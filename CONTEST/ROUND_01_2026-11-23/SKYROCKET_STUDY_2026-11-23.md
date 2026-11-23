# Can the next skyrocket be reverse-engineered? — measured, 2026-11-23

**Universe:** 501 current S&P 500 constituents, 12 years of daily adjusted bars (Yahoo).
**Sample:** **62,583** month-end observations, **36,265** gap-up events.
**Bias, stated up front:** the universe is **current constituents only**, so it is survivorship-conditioned — every company
that was in the index and got acquired or collapsed is missing. Every number below is therefore **optimistic**, and the
conclusions that survive it are the ones that go *against* the optimism.

**Costs:** 12.07 bp round trip (this programme's measured direct-equity figure) deducted from every net figure.

---

## The short answer

**Yes, you can predict the probability of a skyrocket — by a factor of five — and no, it does not make money.**

The screen with the highest lift finds +30 % months at **5.28× the base rate**. The same screen's picks have a **negative
median excess return**, a **coin-flip** chance of beating their peers, and **four times** the base rate of a −30 % month.
The mean is positive because a small tail of winners drags it up. That is not an edge; it is a lottery ticket with a
measured price.

---

## Arm A — which features raise the odds of an extreme month?

Base rate: **P(+30 % next month) = 0.927 %** across 62,583 observations.

| screen (top decile) | P(+30 %) | lift vs base | excess mean vs peers | **excess MEDIAN** | beats peers | **P(−30 %)** |
|---|---|---|---|---|---|---|
| **120-day volatility, high** | **4.89 %** | **5.28×** | +1.18 % | **−0.25 %** | 49.0 % | **1.26 %** (4.0× base) |
| **MAX5 high** (mean of 5 biggest days) | 4.63 % | 5.00× | +1.21 % | **−0.19 %** | 49.0 % | 1.05 % (3.3× base) |
| distance from 52-week high, **low** | 4.15 % | 4.48× | +0.98 % | **+0.31 %** | 51.3 % | 1.21 % |
| 3-month momentum, **low** | 2.51 % | 2.71× | +0.72 % | **+0.38 %** | 51.8 % | 0.89 % |
| 12-1 momentum, high | 2.59 % | 2.79× | +0.83 % | 0.00 % | 50.0 % | 0.50 % |
| distance from 52-week high, **high** | 0.38 % | 0.41× | −0.29 % | −0.49 % | 46.3 % | 0.14 % |
| 120-day volatility, low | 0.00 % | 0.00× | −0.22 % | −0.23 % | 47.8 % | 0.00 % |

**Read the median, not the mean.** The two loudest lottery screens (volatility and MAX5) both have a **negative median
excess return** and a **49 % peer win rate** — a coin flip — while tripling or quadrupling the crash rate. You pay for the
5× lift in two currencies: a typical pick loses to its peers, and the left tail thickens more than the right.

**The only screens with a positive median are the opposite of a skyrocket screen**: names *far below* their 52-week high
(distance-from-high low, median **+0.31 %**, net **+86 bp**) and *weak* 3-month momentum (median **+0.38 %**, net
**+60 bp**). That is short-horizon mean reversion among laggards, not momentum among leaders. It is the mirror image of
the folklore.

## Arm B — gap-up continuation (post-earnings-drift proxy)

Event: a day opening **≥ +4 %** on **≥ 2×** its 50-day average volume. 36,265 events. Measured from the event close
against **the same stock's mean return on all non-event days** — the baseline v1 was missing.

| horizon | raw mean | stock baseline | **excess** | net after 12.07 bp | non-overlap t |
|---|---|---|---|---|---|
| 5 days | +0.16 % | +0.34 % | **−0.17 %** | **−30 bp** | 7.72 |
| 21 days | +1.29 % | +1.41 % | **−0.12 %** | **−24 bp** | 19.06 |
| 63 days | +4.57 % | +4.16 % | **+0.41 %** | **+29 bp** | 26.94 |

**The dramatic version of this result was market drift.** v1 reported +4.57 % over 63 days at t = 48.76 and it looked like
the answer to the question. Against the stock's own non-event baseline the excess is **+41 bp**, and at 5 and 21 days the
excess is **negative**. Gap-up continuation, as measured here, is not a strategy.

**And the t-statistics are still overstated even in the "honest" column.** Restricting to non-overlapping events per stock
removes serial overlap but not **cross-sectional clustering** — thousands of stocks gap up on the same days, so those
63-day windows share the same market path. A clustered or block-bootstrapped standard error would be wider again. I am
reporting the direction and refusing to call +41 bp significant.

## What this means, stated plainly

1. **Skyrocket prediction is real as a probability and worthless as a trade.** A 5.28× lift sounds like alpha until the
   median turns negative.
2. **The asymmetry is the finding.** Nothing here lets you buy the right tail without buying the left. Every screen that
   raised P(+30 %) raised P(−30 %) by 3–4×, and the left tail is what compounds.
3. **The one screen with a positive median is anti-momentum**, and it is worth roughly the round-trip cost plus 74–86 bp
   per month — small, survivorship-inflated, and not yet costed for slippage in the specific names it selects (laggards
   are often laggards for a reason: lower liquidity).
4. **Post-earnings drift, proxied by gaps, did not show up.** If it exists in this data it is smaller than the noise the
   clustering creates.
5. **Two of my own errors, corrected in public:** v1 had **no market baseline** (so beta looked like signal) and reported
   **t = 48.76** on overlapping windows (inflated by roughly √overlap). Both are in this file rather than deleted.

## The next test worth running

The laggard/mean-reversion screen is the only survivor and it is cheap to falsify: form the decile monthly, hold one
month, and check (a) liquidity — median dollar volume of the names selected, (b) whether the excess survives an
equal-weight universe benchmark *and* a value/size control, and (c) whether it is just the 2020 and 2022 recovery months
doing the work. If it dies on liquidity, it is dead.

*Paper only. No live orders, no credentials. Not investment advice. Survivorship-biased universe; treat every figure as an
upper bound.*
