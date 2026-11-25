# Power analysis — how long a sample before the gate can see anything?

**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/power_analysis.py` · every number below is printed by that script.

Three reviewers (Claude 5.1, Claude 5.2, Qwen4 Max) asked for the same missing measurement: **a power statement.** This is it.
Nothing here is a market claim — it is arithmetic from `SE(mean annual return) = vol / sqrt(T)`.

## The headline

> **"Every strategy failed" was close to guaranteed before the study started.**

At **10% volatility over 5 years**, the gate can only resolve an effect larger than **8.9% per year**. Everything smaller —
including a genuine 3%/yr value premium — is **invisible**. The audit pronounced on effects it could not see.

## 1. What +0.11% actually supports

The page said the value strategy *"lost because the effect was not there."* Here is the interval that sentence rests on:

| book vol | years | 95% CI on +0.11% | width |
|---|---|---|---|
| 6% | 3 | [−6.7%, +6.9%] | 13.6 pp |
| 6% | 10 | [−3.6%, +3.8%] | 7.4 pp |
| **10%** | **5** | **[−8.7%, +8.9%]** | **17.5 pp** |
| **10%** | **10** | **[−6.1%, +6.3%]** | **12.4 pp** |
| 15% | 5 | [−13.0%, +13.3%] | 26.3 pp |

**Every row straddles zero, and the intervals are enormous.** At 10% vol over 10 years the estimate is consistent with a true
premium anywhere from **−6.1% to +6.3%**. The data cannot distinguish "no effect" from "large effect, unresolvable sample."

The correct sentence was: **"we could not resolve the effect."** Not "it was not there."

## 2. How long would you need?

Years of data required for a given effect to reach t = 2:

| effect/yr | vol 6% | vol 10% | vol 15% | vol 20% |
|---|---|---|---|---|
| 0.5% | 576 | 1,600 | 3,600 | 6,400 |
| 1.0% | 144 | 400 | 900 | 1,600 |
| 2.0% | 36 | 100 | 225 | 400 |
| **3.0%** | 16 | **44** | 100 | 178 |
| 5.0% | 6 | 16 | 36 | 64 |

**Academic HML is ~3–5%/yr.** At 10% vol that needs **16–44 years** just to reach t = 2. A few-year sample **cannot pronounce a
factor dead** — and that is the factor this page used as its showcase "best-measured" result.

## 3. What could this sample have detected at all?

Minimum detectable effect (t = 2):

| years | vol 10% MDE | vol 15% MDE |
|---|---|---|
| 2 | **14.1%/yr** | 21.2%/yr |
| 3 | 11.5%/yr | 17.3%/yr |
| 5 | **8.9%/yr** | 13.4%/yr |
| 10 | 6.3%/yr | 9.5%/yr |
| 20 | 4.5%/yr | 6.7%/yr |
| 44 | 3.0%/yr | 4.5%/yr |

A 2-year sample at 10% vol can only see effects **above 14%/yr**. No real strategy cleans that bar. **The study was designed to
return a null**, not by bias but by sample length.

## 4. The 9 bp gap says the "value" strategy wasn't value

Gross +0.11% → net +0.02% = **9 bp/yr of cost**. Implied turnover:

| cost per round trip | round trips/yr | annual turnover |
|---|---|---|
| 1 bp (mega-cap) | 9.0 | **1,800%** |
| 6.71 bp (ETF) | 1.3 | 268% |
| 12.07 bp (equity) | 0.7 | 149% |
| 52 bp (crypto) | 0.2 | 35% |

**At 1 bp, that is 1,800% annual turnover — that is not a value strategy.** So one of two things is true: the cost assumption
is far too low (likely, if the universe includes anything below mega-cap), or the implementation is not value. Either way the
label is doing work the numbers don't support.

## 5. There is no positive control — the deepest problem

A long/short value book earning **+0.11% gross** is not a null result for value. It is an **anomalous** result. Academic HML
is 3–5%/yr over long samples; it weakened after 2007 and through 2018–2020, but a well-built value book does not come out at
eleven basis points gross.

> **When a pipeline fails to reproduce a known, heavily-documented effect, the correct inference is "the apparatus may be
> broken," not "the effect is absent." And if it cannot find value, its nine other nulls carry almost no information.**

**Concrete suspects, in the order to check them:**

1. **Price-return vs total-return series.** Value tilts hard into high-dividend names. A price-only feed erases ~2–3%/yr
   specifically from the value leg. **This alone could explain the whole result.** Check first.
2. **Sample window.** 2018–2021 produces near-zero or negative value by construction. State the window.
3. **Universe and weighting.** Microcaps, equal- vs cap-weight, sector neutrality. Unneutralized "value" is a
   short-tech/long-financials bet.
4. **Point-in-time fundamentals.** Restated book values leak lookahead — that inflates rather than deflates, but it tells you
   whether the pipeline is trustworthy at all.
5. **Hedging.** A beta estimated on the same window can subtract the very premium being measured.

**The fix is a positive control:** inject synthetic alpha of known magnitude into real price series and confirm the harness
recovers it at the right size and significance; then reproduce one cheap known anomaly **gross of costs** (12-1 momentum,
short-term reversal). **If the harness cannot pass those, the entire ledger is provisional** and must be labelled so.

## 6. The harness is testing the least powerful statistic available

A single portfolio's annual return throws away almost all the information. A cross-sectional test uses every name on every
day: `t ≈ IC · sqrt(n)`.

| IC | observations for t=3 | at 250 names/day |
|---|---|---|
| 0.01 | 90,000 | 360 y |
| 0.02 | 22,500 | 90 y |
| **0.03** | **10,000** | **40 y** |
| 0.05 | 3,600 | 14.4 y |
| 0.10 | 900 | 3.6 y |

**191 names × 250 days = 47,750 observations per year — about 40× the power of one equity curve's annual return.** The audit
measured the noisiest possible statistic and then treated its noise as a verdict.

## What the page now says instead

Replaced: *"It lost because the effect was not there."*
With: **"No effect was detectable at this sample size — and here is the smallest effect this sample could have detected."**

That is a weaker sentence. It is also the true one.

*Paper only. No live orders, no credentials. Not investment advice.*

---

## 7. Per-class MDE table (t = 2)

Each class below is evaluated at the same sample length as the SPY positive control (33.8 years) so the MDEs are directly comparable. Volatilities are representative assumptions, not measured from class-specific return series — where a class has no return history, the MDE is a lower-bound estimate.

| Class | Vol (assumed) | Sample length | MDE at t=2 | Meaning |
|---|---|---|---|---|
| bond | 5%/yr | 33.8 y | **1.72%/yr** | A bond strategy needs >1.7%/yr alpha to be detectable |
| etf | 15%/yr | 33.8 y | **5.16%/yr** | ETF alpha below ~5%/yr is invisible at this sample |
| equity | 16%/yr | 33.8 y | **5.50%/yr** | Equity alpha below ~5.5%/yr is invisible |
| fund | 10%/yr | 33.8 y | **3.44%/yr** | Fund alpha below ~3.4%/yr is invisible |
| fx | 10%/yr | 33.8 y | **3.44%/yr** | FX alpha below ~3.4%/yr is invisible |
| commodity | 20%/yr | 33.8 y | **6.88%/yr** | Commodity alpha below ~6.9%/yr is invisible |
| futures | 22%/yr | 33.8 y | **7.57%/yr** | Futures alpha below ~7.6%/yr is invisible |
| option | 25%/yr | 33.8 y | **8.60%/yr** | Option alpha below ~8.6%/yr is invisible |
| crypto | 80%/yr | 33.8 y | **27.52%/yr** | Crypto alpha below ~27.5%/yr is invisible |
| prediction | 30%/yr | 33.8 y | **10.32%/yr** | Prediction-market alpha below ~10.3%/yr is invisible |

**Formula:** MDE(t=2) = 2 × vol / √T, where T = 33.8 years.

**Read:** At 33.8 years of data, even a low-vol bond strategy needs nearly 2%/yr of alpha just to reach t=2. Crypto needs 27.5%/yr. **Most classes in this audit cannot have their alpha detected at any realistic sample length** — the gate was guaranteed to return null for high-vol classes.

**Volatility assumptions:** bond 5%, etf 15%, equity 16%, fund 10%, fx 10%, commodity 20%, futures 22%, option 25%, crypto 80%, prediction 30%. These are illustrative; measured vols per class would tighten or loosen the MDEs proportionally.

*Paper only. No live orders, no credentials. Not investment advice.*

---

## 8. The MDE every verdict must quote

For the **actual sample in use** — the audit's own SPY series, **33.8 years (406 months), annualised vol 14.77%** — the
minimum detectable effect at t = 2 is:

> **MDE = 5.08%/yr.**

From the same arithmetic as §3: `MDE(t=2) = 2 × vol / √T = 2 × 0.1477 / √33.8 = 2 × 0.1477 / 5.813 ≈ 0.0508`, i.e. **5.08%/yr**.

**Every verdict in this audit must quote this number.** Any "the effect was not there" statement drawn from this sample is
a statement about the gate's power, not about the market: an effect smaller than 5.08%/yr cannot be resolved here and must
not be reported as absent. The per-class table in §7 scales this same rule by each class's volatility; the SPY figure here
(14.77% vol → 5.08%/yr) is the headline every verdict must be measured against.

**Cross-check against the positive control** (`POSITIVE_CONTROL.md`, same gate, tool `CONTEST/tools/positive_control.py`,
real SPY monthly, demeaned so the 0% case is a true null):

- A **genuine injected 3%/yr alpha is statistically invisible** over 33.8 years at 14.8% vol — recovered at exactly 3%,
  but **t = 1.18 < 2**, 95% CI [−1.98%, +7.98%]. A real effect the gate cannot see.
- A **10%/yr** injected alpha **is** detected (t = 3.94, 95% CI [+5.02%, +14.98%]) — the harness works *above* the MDE.
- The 0% null reports nothing (t = 0.00) — no false positive.

The MDE is therefore not hypothetical: an effect 2.5× finer than the gate's resolution (3% vs 5.08%) vanished over 33.8
years of the audit's own data — the same failure mode as calling a live factor "dead" from a few-year sample.

*Paper only. No live orders, no credentials. Not investment advice.*
