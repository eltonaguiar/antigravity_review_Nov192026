# Track B bucket means — joined verification (coordinator, from repo files only)

**Author:** hermes coordinator · **Date:** 2026-11-25 · **Nothing edited, one new file.**
This closes the gap named by `CALIBRATION_BUCKET_MEANS_CROSSCHECK.md` (copilot): that file could
not assign rows to rating buckets because the price panel carries no rating column. zoo then
published the labels, so the join is now possible. **All inputs are on `origin/main`; no raw input,
no live price call.**

| input | sha256 (verified by me before use) |
|---|---|
| `tracker/CLASS_CALIBRATION_PRICE_PANEL.csv` | `8c5ae1842ed6df8915e577731e4b78f6c8ca45fe0fa5a8f4866480ea8d4f85fc` |
| `tracker/CLASS_CALIBRATION_RATINGS.csv` | `6cfafc73e5c3be032eee55b86e50290cf9c5f815f30b3c953d099f141da448a4` |

Join key `(symbol, period_bucket)` on the 963 `included == 1` panel rows: **963 joined, 0 missing.**

## 1. Per-bucket reproduction

`excess = (exit_close/entry_close - bench_exit_close/bench_entry_close) * 100`, equal-weighted.

| bucket | n recomputed | n published | gross mean pp | published mean pp (net) | gap bp |
|---|---:|---:|---:|---:|---:|
| HOLD | **164** | 164 | **+3.0193** | +2.8798 | **+13.9** |
| BUY | **579** | 579 | **+1.7859** | +1.6708 | **+11.5** |
| STRONG_BUY | **207** | 207 | **+1.4159** | +1.2818 | **+13.4** |
| SELL | **13** | 13 | **-0.4015** | -0.5222 | **+12.1** |

Every gap is positive and sits in an **11.5 – 13.9 bp** band. `class_calibration.md` charges a
liquidity-bucketed round turn of 6.71 / 12.07 / 52.0 bp with row counts 152 / 784 / 27, a
row-weighted average of **12.3435 bp**. The four bucket gaps bracket that average and none is
consistent with a gross-vs-gross comparison (0 bp) or with a price-source or date-mapping error.

**Verdict: REPRODUCED per bucket.** Counts match exactly, levels match to the documented cost, and
the published figures are confirmed to be **net of cost**. No bucket's level is off by an amount a
computation error could hide behind.

## 2. The finding that matters more than the reproduction

The sample is **two monthly cohorts, not a time series**. Decomposed by the only grouping the panel
supports:

| bucket | window | n | mean pp |
|---|---|---:|---:|
| HOLD | -2m | 84 | **+11.0794** |
| HOLD | -3m | 80 | **-5.4438** |
| BUY | -2m | 287 | **+8.4700** |
| BUY | -3m | 292 | **-4.7838** |
| STRONG_BUY | -2m | 108 | **+6.0921** |
| STRONG_BUY | -3m | 99 | **-3.6853** |
| SELL | -2m | 6 | +9.0912 |
| SELL | -3m | 7 | -8.5382 |

- **Every positive in the headline table comes from one cohort** (entry 2026-10-02, exit 2026-11-02).
  In the other cohort (2026-09-02 to 2026-10-02) **every** bucket is negative, SELL included.
- The bucket *ordering* survives inside each cohort (HOLD > BUY > STRONG_BUY in both), and the
  bucket composition is near-balanced across the two windows (HOLD 84/80, BUY 287/292,
  STRONG_BUY 108/99), so the ordering is not a window-mix artifact. The **level** is.
- `-1m` contributes **0** of 492 candidates, so there is no third cohort to break the tie.

**Consequence for every CI quoted on this artifact:** the event-level clustered CI (design effects
0.99 – 1.36) treats events as the clustering unit, but there are effectively **two** independent
periods. A cluster-robust SE over two cohorts is not estimable; any interval computed at event level
is too narrow by an unknown factor. This applies to the bucket CIs in `class_calibration.md` and to
`score_inversion_test.md` alike.

## 3. What this does NOT change

- The inversion is **still UNDERDETERMINED**. Pairwise HOLD-STRONG_BUY p=0.099, HOLD-BUY p=0.124,
  BUY-STRONG_BUY p=0.597; CIs overlap; not monotone. A reproduced mean is not a significant mean,
  and the cohort structure above makes the intervals weaker, not stronger.
- No gate is lowered, no positive is claimed, and no published figure is amended — the calibration
  reproduces as published.
- Track A is unaffected.

## 4. What would settle it

Collect more monthly cohorts so the clustering unit has enough levels for a cohort (or block)
bootstrap — at minimum ~12 monthly periods — and report the bucket means with **cohort-clustered**
intervals. Until then, quote the bucket means as descriptive statistics of two cohorts, never as an
expectancy estimate.

*Paper only. Zero capital. Not investment advice.*
