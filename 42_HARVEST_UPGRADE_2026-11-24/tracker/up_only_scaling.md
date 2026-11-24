# Up-only scaling: how many tickers to clear the 300 / 500 / 750 clean-event floors

**Question:** Zoo measured the up-only, 182-day-clean cohort at **8,498 events across 220 firms**, with
6 firms ≥300, **0 at 500 and 0 at 750**, the biggest being BofA Securities at **439**. How many tickers
must the collection cover for at least one firm to clear 300, 500 and 750 — and is that feasible?

**Short answer:** 300 is *already cleared* at the current 306 tickers. 500 needs **~349 (linear) to
~392 (sublinear)**. 750 needs **~523 (linear) to ~849 (central sublinear)**. Collection for the worst
case is **under 15 minutes**. The programme should continue — breadth, not authorisation, was the blocker.

---

## 1. Events per ticker and per firm, measured (not asserted)

Source: `tracker/analyst_actions.csv` — 122,746 rows, **14.93 years** (2011-12-08 → 2026-11-12).

| measure | all-UP | 182-day clean |
|---|---:|---:|
| events | 9,873 | 8,498 |
| distinct firms | 227 | 220 |
| distinct tickers | **306** | **306** |
| events / ticker | 32.26 | 27.77 |
| events / firm | 43.49 | 38.63 |
| events / (firm,ticker) pair | 1.64 | 1.49 |

Leader firm (BofA Securities, both columns):

| | all-UP | clean |
|---|---:|---:|
| events | 556 | **439** |
| tickers covered | 237 | 237 |
| coverage of the 306 | 77.5% | 77.5% |
| events / **covered** ticker | 2.347 | **1.852** |

Per-ticker clean counts: median 27, max 79. Top clean firms: 439, 427, 411, 383, 321, 305.

**Two facts that decide the arithmetic:**

1. **The depth lever is exhausted.** The dataset already spans 14.9 years and BofA already has 476
   distinct entry dates (requirement is 150+). BofA accrues ~37 UP events/year, so waiting for forward
   accretion to reach 750 would take **~8.4 more years**. Breadth is the *only* remaining lever.
2. **Coverage is concentrated.** BofA touches 77.5% of tickers but only 1.85 clean events per covered
   ticker. Halving coverage costs you half the events; it does not cost you a constant.

## 2. The scaling rule, and why the two candidate estimates disagree

Events do not obviously scale linearly in tickers, so I measured the exponent two ways.

### 2a. Two-point subsampling — the direct test of "do more tickers add events?"

For 200 random 30-ticker subsets of the measured 306, BofA's mean clean events were **42.92**
(uniform expectation 43.04, range 26–63).

```
alpha = ln(439 / 42.92) / ln(306 / 30) = 1.001
```

**Within the measured coverage class, scaling is LINEAR.** Random subsets behave exactly as
proportional sampling predicts.

### 2b. Rank-curve fit — the distribution *across* tickers

Fitting the sorted per-ticker clean counts, `count(rank) ∝ rank^(-0.475)`, gives a cumulative
exponent of **0.525**. This is sublinear, and it is the relevant number **only if** new tickers are
added worst-first (i.e. you exhaust the well-covered names before reaching the thin ones).

### 2c. Why they differ, and which to trust

2a answers "add more tickers *of the kind already measured*" → linear.
2b answers "keep adding tickers *after* the good ones run out" → sublinear.
**Extending from 306 large/mid caps into small caps is the 2b situation**, because a brokerage's
coverage fraction falls as market cap falls. But 2b is a lower bound on the yield curve, not a
measurement of the *next* 500 tickers — those are outside the collected set and cannot be measured
from it.

So: **α = 1.0 is the measured within-class value; α ≈ 0.5 is the pessimistic extrapolation; the truth
for small caps lies between and is not yet measured.** Both are reported.

## 3. Tickers needed, under both assumptions

`N(floor) = 306 × (floor / 439)^(1/α)`, anchored on BofA's measured 439 clean events at 306 tickers.

| α | assumption | floor 300 | floor 500 | floor 750 |
|---|---|---:|---:|---:|
| 1.00 | **linear** (measured within-class) | 209 | **349** | **523** |
| 0.75 | mild saturation | 184 | 364 | 625 |
| 0.525 | **sublinear** (fitted rank curve) | 148 | **392** | **849** |
| 0.40 | severe saturation | 118 | 424 | 1,167 |

Read the 300 column carefully: it is *back-extrapolated*, not a requirement. **At the current 306
tickers BofA already has 439 clean events, so the 300 floor is already met** and the 500 floor is
about **40–85 tickers away**.

### The floors in terms of *new* tickers to collect

| floor | linear (523/349) | sublinear (849/392) |
|---|---:|---:|
| 500 | +43 | +86 |
| 750 | +217 | +543 |

## 4. Cost of collection — and the SEC rate limit in context

The collector (`tracker/collect_analyst_history.py`) is **Yahoo-Finance** based and rate-limited to
**0.25 s per symbol** by default, resumable, one row per (firm, ticker, date, action).

| target | new tickers | wall-clock at 0.75 s/ticker (0.25 s sleep + fetch) |
|---|---:|---:|
| 500 floor, linear | 43 | **~32 seconds** |
| 500 floor, sublinear | 86 | ~65 seconds |
| 750 floor, linear | 217 | **~3 minutes** |
| 750 floor, sublinear | 543 | **~7 minutes** |
| worst case (α=0.40) | 861 | ~11 minutes |

**The SEC 10-requests/second limit is not the binding constraint and does not apply here.** Analyst
rating changes are not published on EDGAR; the data comes from the aggregator. Even if the whole run
were bound by a 10 req/s ceiling, 1,200 tickers would take **2 minutes**. The real limit is Yahoo
throttling, which the collector already paces at 4 req/s — comfortably inside it.

**Collection is not the constraint. It is a few minutes of work.**

## 5. What the floors actually buy you

Per `PREREG_ANALYST_UPGRADE_TEST.md` §2.2, adopted minimum is **750 clean events, 150+ distinct entry
dates, ≥24 months**, which reproduces an MDE of **1.39%** at sd=12% (80% power, one-sided p<0.01).
Floors below that underpower the test:

| floor | MDE at sd=12% |
|---|---:|
| 300 | 2.19% |
| 500 | 1.70% |
| 750 | **1.39%** |

Clustering check: 439 clean events across 237 tickers is **1.85 events per ticker**, so with even a
generous ICC of 0.15 the design effect is `1 + 0.85×0.15 ≈ 1.13` — mild. 750 nominal events is
roughly 665 effective, and the 1.39% MDE should be read as ~1.5%. Clustering is **not** the blocker here.

## 6. Sensitivity summary and recommendation

| | optimistic (α=1) | central (α=0.525) | pessimistic (α=0.40) |
|---|---:|---:|---:|
| tickers for 300 | 209 *(already met)* | 148 *(already met)* | 118 *(already met)* |
| tickers for 500 | 349 | 392 | 424 |
| tickers for 750 | 523 | 849 | 1,167 |
| collection time, 750 floor | 3 min | 7 min | 11 min |

**Recommendation: continue on analyst ratings.** The floor failure was never about the hypothesis —
it was that the universe covered 306 tickers when the arithmetic required roughly 350–850. That is a
collection gap measurable in minutes, not a finding about analyst behaviour. Stopping now would be
stopping because of a sampling artefact, which is the precise failure mode this programme keeps
repeating. The correct next action is one collector run to ~520 tickers (clears 500 under every
assumption and 750 under linear scaling, ~3 minutes), then re-measure before deciding whether the
sublinear case (849) is needed.

**One caution that survives regardless of α:** clearing 750 events makes the test *powered*, not
*positive*. If the result is null, the MDE must be published with it so the null is a quantified
statement ("no edge larger than ~1.5% at 80% power") rather than an assertion.

---

### Reproducer

```bash
python3 - <<'EOF'
# two-point exponent + floor arithmetic
# see §2a/§3; anchors: N0=306, E0=439 (BofA, clean, 182d)
for a in (1.0, 0.75, 0.525, 0.40):
    print(a, [round(306*(f/439)**(1/a)) for f in (300,500,750)])
EOF
```
