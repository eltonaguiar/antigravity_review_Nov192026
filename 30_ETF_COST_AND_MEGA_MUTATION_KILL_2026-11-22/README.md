# Round 30 — ETF cost, and the last candidate is dead (2026-11-22)

Author: `copilot-cli-deepseek-flash`. Source branch
`push/phase2-round-2026-11-22` (deliberately unpushed — carries other agents'
commits).

Zero capital. Not investment advice. `UNMEASURED` means unmeasured, not zero.

---

## Headline

**The programme has no established positive-expectancy emitter.** The one that
survived round 29 — `mega_mutation`, +135 bp, n=105 — was put through an 8-test
falsification battery and scored **4/6**. It is now **QUARANTINED**. The honest
deployment is T-bills at 3.5%.

**The one thing that could have changed that is still unmeasured.** The breakout
family's gross edge is +22.43 bp at t = +7.32 and breakeven sits at 20–24 bp round
trip. Three attempts to infer the ETF spread from daily OHLC all failed and were
deleted rather than tuned. A live NBBO sampler now accrues during market hours.

---

## mega_mutation: 4/6 → QUARANTINE

| # | test | result |
|---|---|---|
| 1 | max-statistic null (best of 20 random sources, 3,000 draws) | **PASS** — +134.98 vs null p99 +114.71, p=0.0010 |
| 2 | cluster bootstrap on the mean | **PASS** — [+40.90, +231.49] bp |
| 3 | out-of-sample clock | **PASS** — 73 OOS picks, +126.25 bp |
| 4 | breakeven vs measured cost | **PASS** — 135 bp ≫ 42 bp |
| 5 | **median CI** | **FAIL** — median +193.43, CI **[−224.38, +289.98]** |
| 6 | **duplicate re-emissions** | **FAIL** — 8 groups, **16/105 rows** |

Two duplicates are the **same position emitted twice on the same day**
(AVAXUSDT SHORT @9.409, JUPUSDT LONG @0.1698, both 2026-04-30).

The untestable one: TP-first rate **56.4%** vs **40.9%** implied by a driftless
random walk at the realised TP/SL distances (TP ~546 bp, SL ~378 bp),
binomial P(≥53 of 94 | p=0.409) = **1.7 × 10⁻³**. That is either real directional
skill or TP/SL placed with hindsight — and the resolved ledger has **no
`created_at`**, so it cannot distinguish them. Even a 6/6 pass could only have
reached CANDIDATE.

### My own tool overstated this first
The first version used 4 tests and printed **4/4 PASS**. The concentration output
in that same run already showed three single-trade days contributing 22% of the
P&L, and I had not turned it into a test. The tests were expanded to include ones
that can fail for reasons other than "the number is small" — median
disagreement with the mean, and duplicate rows — and the verdict inverted.

## ETF spread: three estimators failed, so it is a sampler now

| estimator | result |
|---|---|
| Corwin-Schultz | **0.00 on all 1,248 SPY pairs** — degenerate |
| Roll | 34.76 bp — `2·√(−autocov)` tracks volatility, not spread |
| Abdi-Ranaldo (2017) | **~100,000 bp on SPY** — my implementation was wrong |

The AR attempt is the instructive one: I wrote it from recollection of the algebra
and a **control check caught it instantly** (it could not recover a single-digit-bp
spread on the most liquid ETF on earth). I could not confirm the formula from a
trusted source, so **I deleted it rather than tune variants until one produced a
plausible number.** Tuning an estimator until it agrees with the answer you expect
is fitting to the prior, not measuring.

Replacement: live NBBO sampling on SPY/QQQ/GLD via IEX top-of-book.
`etf-spread-series.yml`, cron `35,05 13-19 * * 1-5`, 20-min minimum gap enforced
in code, `[skip ci]` commits, no push trigger. Current state: **UNMEASURED**, zero
samples, market closed. It records nothing rather than emitting a zero.

---

## Labels after round 30

| item | label |
|---|---|
| Live ledger, all classes | **REFUTED** (−15.24 bp, PF 0.90, t=−3.91, n=10,968) |
| CRYPTO / COMMODITY / FOREX / BOND / ETF | **REFUTED** |
| EQUITY | **NOT ESTABLISHED** (PF CI-LB 0.885) |
| H-119 | **REFUTED** (430/430 backfilled) |
| Funding carry | **REFUTED** (window-dependent) |
| Cross-venue funding arb | **REFUTED** |
| Vol risk premium | **ESTABLISHED** (t=+46.50) / harvest **RUINED** |
| GDX/SLV pairs | **REFUTED** (ADF OOS +0.15) |
| Polymarket calibration | **ESTABLISHED** (Brier skill +0.4956) |
| **`mega_mutation`** | **QUARANTINE** (4/6) |
| **Any positive-expectancy emitter** | **none established** |
| ETF effective spread | **UNMEASURED** (sampler live) |

## Ask for reviewers

Two specific things:

1. **Confirm or refute the duplicate finding.** If `mega_mutation`'s 16 duplicate
   rows are legitimate separate positions rather than re-emissions, re-run the
   battery — but note it still fails the median test.
2. **Anyone with historical NBBO for SPY/QQQ/GLD, share it.** That single number
   decides whether the programme's only real gross edge (+22.43 bp, t=7.32) is
   investable. It has been the binding unknown for the entire programme and no
   daily-OHLC estimator can supply it.
