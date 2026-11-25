# Class coverage — live resolvers only

**Read-only** query of `ejaguiar1_stocks.at_pick_outcomes`, 2026-11-25. Credentials read at runtime; never printed or committed.

**Filter:** `resolver_version NOT LIKE 'backfill%'` (NULL included as non-backfill). A priced row has `pnl_pct` non-null and non-zero.

## Filter counts

| stage | n |
|---|---:|
| raw rows | 63,797 |
| backfill rows excluded | 37,115 |
| live-resolver rows | 26,682 |
| live priced rows | 26,161 |
| live share of raw | 41.8% |

## Per-class table after the live filter

| class | n after filter | % of all rows | priced | priced coverage | mean (priced) | median (priced) |
|---|---:|---:|---:|---:|---:|---:|
| CRYPTO | 25,488 | 39.95% | 25,353 | 99.47% | +0.1084% | -1.0000% |
| FOREX | 612 | 0.96% | 442 | 72.22% | +0.0732% | -0.0035% |
| EQUITY | 192 | 0.30% | 117 | 60.94% | -0.0791% | -1.5000% |
| COMMODITY | 161 | 0.25% | 66 | 40.99% | +0.0024% | -0.0034% |
| UNKNOWN | 141 | 0.22% | 141 | 100.00% | -2.0210% | -5.1500% |
| FUTURES | 69 | 0.11% | 27 | 39.13% | +0.5859% | +0.9600% |
| MEME | 13 | 0.02% | 13 | 100.00% | -9.5432% | -6.4062% |
| BOND | 4 | 0.01% | 1 | 25.00% | -0.0047% | -0.0047% |
| ETF | 2 | 0.00% | 1 | 50.00% | -0.0101% | -0.0101% |
| INDEX | 0 | 0.00% | 0 | -- | -- | -- |

## Findings

- **Backfill removal is large:** 37,115 of 63,797 rows (58.2%) are excluded; the live sample is 26,682 rows (41.8% of raw).
- **CRYPTO dominates the live sample:** 25,488 of 26,682 live rows (95.5%); every other class is 2–4% or less of its raw class. Cross-class comparisons are effectively CRYPTO vs small n.
- **Priced coverage is uneven:** CRYPTO 99.47%, UNKNOWN 100%, FOREX 72.22%, EQUITY 60.94%, COMMODITY 40.99%, FUTURES 39.13%, BOND 25.00%, ETF 50.00%, MEME 100% (n=13), INDEX 0 (all backfill).
- **Medians:** CRYPTO −1.00%, FOREX −0.0035%, EQUITY −1.50%, COMMODITY −0.0034%, FUTURES +0.96% (n=27), MEME −6.4062%, UNKNOWN −5.15%. Positive means with negative medians remain payoff-shape, not edge.
- **Do not compare these means to the cost gate directly:** this table is gross, priced-only, and class n is not powered; the cost gate applies costs and its own coverage caveats.

next_probe: run the cost-gate table on this live-only, priced-only sample with per-class n and a power floor; do not pool backfill rows.
