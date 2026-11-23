# CORRECTION — my "3.5× the noise floor" claim was wrong

**Date:** 2026-11-23 · **Status:** supersedes the noise-floor conclusion in `FUND_ANALYSIS_DEFECT_LEDGER.md` and in commit
`db2d783`.

A reviewer noted the one thing thirteen reviewers asked for and nobody had computed:

> "Tracking error is listed as a todo but never computed — yet the whole FXAIX-vs-SPY argument **is a tracking-error
> argument**."

It was right, and computing it destroys my own most recent conclusion.

---

## What I claimed

> VTSAX and VTI are share classes of one fund, so their measured difference is the noise floor. They differ by **−2.5 bp/yr**.
> Against that floor, FXAIX − SPY = **+8.7 bp/yr = 3.5× noise**, and the fee gap is 7.95 bp — therefore *on CAGR the fee
> effect is real and measurable*.

## Why it is wrong

**I compared two point estimates and called their difference a noise floor.** A 2.5 bp difference between two series is
itself a *noisy estimate*, not a threshold. To test whether a difference is real you need the standard error **of that
difference** — which means tracking error, not a second point estimate.

## The correct test

`tracking difference (TD)` = annualised mean of the daily return difference; `tracking error (TE)` = its annualised
standard deviation. Window 2020-11-23 → 2026-11-20, 1,506 sessions, 5.97 years.

| pair | design | TD (bp/yr) | **TE (%/yr)** | TD/TE | t | fee gap |
|---|---|---|---|---|---|---|
| **VTSAX − VTI** | **share classes of ONE fund — control** | −2.7 | **1.074** | −0.03 | **−0.1** | ~1 bp |
| FXAIX − SPY | same index | +5.7 | 0.950 | 0.06 | **0.1** | 7.95 bp |
| VOO − SPY | same index | +7.0 | 0.763 | 0.09 | **0.2** | 6.45 bp |
| FZROX − VTI | **different** indexes (Fidelity vs CRSP) | +14.0 | 0.951 | 0.15 | **0.4** | 3 bp |

### The control is the finding

**Two share classes of the same fund — same portfolio, same manager, same everything — have *more* tracking error
(1.074 %) than FXAIX-versus-SPY (0.950 %).**

So the ~1 %/yr is **not** a measure of vehicle quality. It is **timing noise**: a mutual fund strikes NAV once at 4 pm while
an ETF trades to the close, dividends are reinvested at NAV on one side and at the ex-date price on the other, and the two
series are adjusted on different conventions. That noise is roughly **5× larger than the largest fee gap in the table.**

## The arithmetic that ends the argument

`SE(TD) = TE / √years`. With TE ≈ 0.94 %/yr, years = 5.97 → **SE(TD) ≈ 38 bp/yr**. The observed FXAIX − SPY TD of 5.7 bp
gives **t ≈ 0.1**.

How much data to establish a fee-sized difference at t = 2?

| claimed difference | years of data required |
|---|---|
| 8.0 bp/yr | **546 years** |
| 7.95 bp/yr | **553 years** |
| 6.45 bp/yr | **840 years** |
| 3.0 bp/yr | **3,883 years** |
| 1.0 bp/yr | **34,943 years** |

**Every pairwise difference in this analysis is inside noise, including the ones I called real an hour ago.**

## What actually survives — and it is a stronger claim

1. **The fee gap is contractual, not measured.** Expense ratios are published terms of the fund, not an estimate from a
   return series. 7.95 bp/yr between FXAIX and SPY is **known with certainty**; it does not need a backtest and cannot be
   refuted by one.
2. **Therefore the recommendation is unchanged but rests on a different footing:** buy the cheapest share class because the
   fee is a **certain, compounding, contractual cost** — **not** because a six-year backtest demonstrated outperformance.
   No amount of historical data was ever needed for that conclusion, and none can confirm it.
3. **Any claim that one of these vehicles "won" over five years is unfalsifiable noise.** Anyone reporting that — including
   me, twice today — was reporting timing noise of ~1 %/yr against a signal of ~8 bp/yr.
4. **FZROX vs VTI is worse than noise:** TD 14 bp against a 3 bp fee gap means an 11 bp residual from index construction,
   and its t is 0.4 — so even that residual is unproven.

## The lesson, third edition

**A control is not a noise floor unless you compute its standard error.** I found the right control and then used it
backwards: instead of asking "how much does this difference fluctuate?", I asked "how big is this difference?" — and a
difference between two estimates always looks precise when you write it to one decimal place.

The rule now: **for any pairwise comparison, report TD, TE and t together, or report nothing.** A difference without its
own dispersion is not evidence.

*Paper only. No live orders, no credentials. Not investment advice.*
