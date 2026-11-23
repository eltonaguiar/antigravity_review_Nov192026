# IC panel test — cross-sectional information-coefficient test (t ~ IC*sqrt(n))

**Date:** 2026-11-23 · **Round:** ROUND_01_2026-11-23 · **Tool:** `CONTEST/tools/ic_panel_test.py` · every number below is printed by that script.
**Data:** real Yahoo Finance monthly adjusted close, 24 symbols, 120 months (10.0 years), 106 valid IC periods. Nothing is fabricated; the script exits non-zero if the universe cannot be built.

## Question

Does the panel cross-sectional IC test have the power to detect a signal that a single equity curve cannot? The test uses t ~ IC * sqrt(n) and shows where that power actually comes from.

## Method

Each month, score every symbol by a signal (prior 12-month momentum, skipping the most recent month to avoid short-term reversal) and pair it with the next-month return. Two tests:

1. TIME-SERIES PANEL (proper): IC per period = Pearson(signal, next-month return) across symbols. t = mean IC * sqrt(n_periods) / sd(IC). This is the honest test because observations inside a period share the same forward-return month, so they are not independent; the effective sample is n_periods.
2. POOLED (naive upper bound): treat all symbol-period pairs as independent, compute one IC across all n_obs = symbols * periods pairs, t = IC * sqrt(n_obs).

The gap between the two shows the power that naive pooling claims — but it is illusory because within-period observations are correlated. The honest answer is the panel t.

## Results

| metric | value |
|---|---|
| universe | 24 symbols |
| n_periods | 120 months (10.0 years) |
| n_ic_periods | 106 valid IC periods |
| n_observations (symbols x periods) | 2544 |
| mean IC | 0.0118 |
| sd(IC) | 0.3664 |
| SE(IC) | 0.0356 |
| panel t (time-series, n_periods) | 0.33 |
| panel significant? (|t| >= 2) | No |
| IC hit rate (positive IC months) | 52.8% |
| pooled naive IC | 0.0395 |
| t_pooled naive (IC * sqrt(n_obs)) | 1.99 |
| naive pooling claims x the panel t | 6.0x |

## Reading

- **Panel t = 0.33, not significant.** The cross-sectional momentum IC is not reliably different from zero over this sample. POWER_ANALYSIS.md section 5 gives t ~ IC * sqrt(n), but the n in the panel test is n_periods (120), not n_observations (2544).
- **Naive pooling inflates power.** Treating all 2544 symbol-period pairs as independent gives t = 1.99 and claims 6.0x the panel t, but within-period observations are correlated so that power is illusory.
- **Cross-sectional breadth does not buy time-series power.** A panel gives more observations per period, but the time-series test is still limited by n_periods. A single equity curve has only n_periods return observations; the panel IC test has only n_periods IC estimates. Neither gains power from n_symbols alone.

## Verdict

The honest IC panel test shows that the momentum cross-sectional IC (mean 0.0118) is not significant (t = 0.33) over 106 monthly periods. The apparent power gain from pooling symbols x periods is illusory. To detect a small but persistent IC you need more periods (longer sample), not more symbols per period.

*Paper only. No live orders, no credentials. Not investment advice.*
