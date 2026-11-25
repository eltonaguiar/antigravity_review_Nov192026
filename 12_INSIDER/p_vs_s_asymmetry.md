# Insider P vs S asymmetry

zoo-savant, 2026-11-25T00:16:49Z. Source `form4_events_wide.csv`.

**Cluster unit:** issuer symbol (insiders, not brokers), 21 symbols.
**Entry:** next session open after `filing_date`. **Benchmark:** ADV x momentum tercile cell mean, same date.
**Costs reported at:** 0.98, 4.01, 12.07 bp.

**ADV distribution (USD):** {'n': 979, 'min': 22963888, 'median': 1232185209, 'p90': 26611694552, 'max': 26611694552}

| H | P n | P excess | S n | S excess | design effect | MDE80 | placebo p95 | asymmetry holds |
|---|---|---|---|---|---|---|---|---|
| 21d | 46 | 10.7873% | 865 | -0.5737% | 0.0 | 42.7384% | -4.6515% | True |
| 63d | 44 | 7.2321% | 690 | -0.4612% | 0.0 | 18.0284% | 1.7091% | True |
| 126d | 35 | 10.3969% | 277 | -1.3137% | 0.0 | 39.5876% | 13.5985% | True |

**Owner-row counts (this file):** {"P": 52, "S": 927, "P_officer_or_director": 6, "P_officer_dir_not_10pct": 3}
