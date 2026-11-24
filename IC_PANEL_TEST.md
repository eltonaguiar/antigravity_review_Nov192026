# IC Panel Test — Cross-Sectional Information Coefficient

**Question:** Does cross-sectional breadth buy time-series power? Honest answer: no. The panel uses n_periods, not n_obs. Within-period observations are correlated, so naive pooling inflates t illusorily.

**Method:** Each month, score every symbol by a signal (prior 12-month momentum, skipping the most recent month) and pair it with next month's return. Two tests:
1. **Time-series panel (honest):** IC per period = Pearson(signal, forward return) across symbols; t = mean_IC * sqrt(n_periods) / sd(IC)
2. **Pooled naive (upper bound):** one IC across all symbol-period pairs; t = IC * sqrt(n_obs)

**Data:** Yahoo Finance monthly adjusted close, 24 symbols, 120 months (10 years), 106 valid IC periods, 2,544 observations.

## Results

| Metric | Value |
|--------|-------|
| Mean IC | 0.0118 |
| SD(IC) | 0.3664 |
| SE(IC) | 0.0356 |
| Panel t (time-series, n_periods) | 0.33 — not significant |
| IC hit rate (positive IC months) | 52.8% |
| Pooled naive IC | 0.0395 |
| Pooled naive t (t = IC * sqrt(n_obs)) | 1.99 |
| Naive pooling power gain | 6.01x |

## Interpretation

- **Honest panel t = 0.33:** The cross-sectional momentum signal has no detectable predictive power in this sample. The panel t uses n_periods = 106, not n_obs = 2,544.
- **Naive pooled t = 1.99:** Treating all 2,544 symbol-period pairs as independent inflates t by 6.01x. This is illusory — observations within a period share the same forward-return month and are not independent.
- **Power gain claim vs reality:** Naive pooling claims 6x the power of the honest panel. The honest answer is that cross-sectional breadth does not buy time-series power when within-period observations are correlated.

**Conclusion:** The harness tests the least powerful statistic available. A single equity curve has ~10 years of annual observations; the IC panel has ~106 monthly periods. Neither can reliably detect small edges.

*Source:* `CONTEST/tools/ic_panel_test.py` → `CONTEST/tools/reports/ic_panel_test.json`

*Paper only. Zero capital. Not investment advice.*
