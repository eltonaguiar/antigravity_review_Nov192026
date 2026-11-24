# Target-bundle test — does an `up` action conflate rating migration with a target change?

**Owner:** Kilo · **Date:** 2026-11-24
**Source:** `ZOOCODE/harvest/2026-11-24T1942Z_earnings499.json` + Yahoo prices
**Comparable to:** `score_inversion_test.md` — same lag-1 entry, ADV/momentum matched control,
10/30/100 bp cost, 21-day exit, symbol-cluster bootstrap.

## 0. The objection

An `up` action may bundle a target-price/forecast change with the rating migration. If so, the
pooled programme estimates are averages over two signals. This tests that split directly.

## 1. Field coverage — the answer starts here

"Target changed" is defined against the **prior record for the same firm-symbol**: current `pt`
and the previous record's `pt` must both be present and positive; changed = |Δ|/|prior| > 0.1%.

| field / subset | count | share of 14,427 `up` rows |
|---|---:|---:|
| current `pt` present and positive | 9,676 | 67.1% |
| prior record `pt` present and positive | 10,784 | 74.8% |
| **both present (split is computable)** | **7,920** | **54.9%** |
| both present and target changed | 7,436 | 51.5% |
| both present and rating-only | 484 | 3.4% |
| tested after date + grade + price filters | 2,666 | 18.5% |

**The flag is usable for only 54.9% of `up` rows before price/date filters, and 18.5% after.**
Among usable rows the split is extremely imbalanced: 93.9% had a target change, 6.1% did not.
That imbalance is itself a finding: a "rating-only upgrade" is rare in this feed.

## 2. Subsets and forward net excess (matched, lag-1)

| subset | n | mean net excess | 95% clustered CI | symbols | largest share | design effect |
|---|---:|---:|---|---:|---:|---:|
| rating-only (no target change) | 161 | **+30.33 bps (+0.303%)** | [-95.9, +165.9] | 130 | 2.5% | 1.005 |
| upgrade + target change | 2,505 | **+28.53 bps (+0.285%)** | [-11.0, +70.7] | 458 | 0.9% | 1.476 |

Difference (target-change minus rating-only): **−1.8 bps**, 95% cluster-bootstrap CI
**[−144.2, +133.0]** — includes zero.

Both point estimates are positive and almost identical; neither CI excludes zero. The
rating-only subset is small (161) and concentrated enough to be noisy, though not in one symbol.

## 3. Verdict

**UNDERDETERMINED.** There is no evidence the two subsets are different signals — the difference
CI spans zero and the point estimates differ by 1.8 bps — but there is also not enough usable
target data (54.9% raw, 18.5% priced) to assert they are the same. The field-coverage limitation
is the primary result, not a footnote.

The one measurement that would settle it: backfill `pt` and prior `pt` from a PIT target feed for
the 6,507 `up` rows where either is missing, then rerun this exact split and bootstrap.

next_probe: PIT target backfill for the 6,507 missing-target `up` rows; same controls, 21d lag,
10/30/100 bp cost, symbol-cluster CI.
