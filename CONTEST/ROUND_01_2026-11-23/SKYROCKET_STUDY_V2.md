# Skyrocket study v2 — both arms fail their own controls

**Date:** 2026-11-23 · **Script:** `skyrocket_study2.py` · v1 results are superseded by everything below.

v1 reported two striking numbers. v2 was built to attack the two confounds in v1 — **no market baseline** and **overlapping
windows**. Both attacks succeeded, and both findings died.

## v1's claims

| arm | v1 result |
|---|---|
| **A — lottery screen** | vol20 top decile hits P(+30% next month) at **5.28× base rate**, net **+381 bp** |
| **B — gap-up continuation (PEAD proxy)** | mean **+4.57% over 63 days**, **t = 48.76** |

## Arm A — the "5.28× lift" is variance selection, not a forecast

v2 replaces the raw hit rate with **excess return versus the cross-sectional mean for the same date**, and reports the median
alongside the mean.

| screen | v1 net bp | **excess mean** | **median** | **up-rate** | v2 net bp |
|---|---|---|---|---|---|
| **max5(h)** | +386 | **+1.21%** | **−0.19%** | **49.0%** | +109 |
| **vol20(h)** | +381 | **+1.26%** | **−0.25%** | **49.0%** | +106 |
| m3(l) | +361 | +0.98% | +0.31% | 51.3% | +86 |
| m12_1(l) | +278 | +0.74% | +0.05% | 50.2% | +62 |
| **vol20(l)** | +68 | −0.22% | −0.23% | 47.8% | **−34** |
| **max5(l)** | +90 | −0.33% | −0.36% | 47.1% | **−45** |
| **dist_hi(h)** | +25 | −0.29% | −0.49% | 46.3% | **−41** |

**Three things kill the headline:**

1. **The excess is in the mean, not the median.** Median excess for the winners is **negative** (−0.19%, −0.25%). The typical
   month is *slightly worse* than its peers; the mean is carried by a minority of right-tail events.
2. **The up-rate is below 50%** — 49.0% for both top screens. You lose more often than you win.
3. **The mechanism is obvious in hindsight:** `vol20` and `max5` select for **high volatility**, and high volatility mechanically
   selects for large positive outcomes in a rising market. **This is not a forecast. It is a variance filter.**

Seven of sixteen rows went **negative** once measured against peers. A screen that is negative in seven of sixteen cells is not
a screen.

## Arm B — the gap-up "edge" was the stock's own drift

v2 adds the correct baseline: **the same stock's returns on its own non-event days**, plus a non-overlapping event subset for
the t-statistic.

| horizon | v1 mean | v1 t (naive) | stock baseline | **excess vs baseline** | **net bp** | honest t (non-overlap) |
|---|---|---|---|---|---|---|
| 5 d | +0.16% | 4.85 | +0.34% | **−0.17%** | **−30** | 7.72 |
| 21 d | +1.29% | 23.10 | +1.41% | **−0.12%** | **−24** | 19.06 |
| 63 d | **+4.57%** | **48.76** | **+4.16%** | **+0.41%** | **+29** | 26.94 |

**The 63-day "+4.57%" was +4.16% of ordinary drift plus +0.41% of event effect.** At 5 and 21 days the excess is **negative**.
Once you compare a gap-up stock to itself, the signal disappears.

Also note the t-inflation: naive **48.76** versus honest non-overlapping **26.94** — the overlapping windows inflated t by
**1.81×**, not the √overlap I had assumed. Still large, but large *about nothing*, because the mean being tested was the
market's drift.

## What this means

| claim | status |
|---|---|
| "vol20 top decile: 5.28× base rate" | **RETRACTED** — variance selection, median excess negative, up-rate 49% |
| "gap-up: +4.57% over 63 days, t=48.76" | **RETRACTED** — 91% of it was the stock's own drift; excess is negative at 5d and 21d |
| "overlapping windows inflate t by ≈√overlap" | **CORRECTED** — measured **1.81×** on this panel |
| High-vol screens show higher forward returns in a rising market | **STANDS** — and is exactly why you need the excess-vs-peers control |

## The pattern this reinforces

Both v1 findings had the same shape: **a real-looking effect that a better baseline erased.** The number was not noisy — it was
*precisely wrong*. t = 48.76 is not a weak signal; it is a confident measurement of the wrong quantity.

That is the third instance today of the same failure:

1. **FXAIX − SPY = 8.7 bp** — real, but 3.5× the noise floor; tracking error was never computed.
2. **F1 void rate across 18 entrants** — reproduced, but it was my prompt, not a model property.
3. **"+4.57% over 63 days"** — huge t, but 91% of it was market drift.

**In all three, the missing control was a baseline, not more data.** And in all three I had the data to run the baseline on the
first pass.

*Paper only. No live orders, no credentials. Not investment advice.*
