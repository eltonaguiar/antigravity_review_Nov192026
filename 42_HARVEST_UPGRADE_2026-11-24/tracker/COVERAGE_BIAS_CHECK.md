# Coverage-bias check — does priced_coverage recreate the class confound?

**Read-only** check of `CLASS_COVERAGE_TABLE.md`, 2026-11-25. No writes.

## Data used

Live-resolver rows only (`resolver_version NOT LIKE 'backfill%'`), priced means from
`CLASS_COVERAGE_TABLE.json`; published means from `DILUTION_SENSITIVITY.json`.

| class | n after filter | priced coverage | priced mean % | published mean % |
|---|---:|---:|---:|---:|
| CRYPTO | 25,488 | 99.47% | +0.1084 | +0.0285 |
| FOREX | 612 | 72.22% | +0.0732 | +0.0563 |
| EQUITY | 192 | 60.94% | −0.0791 | −0.0884 |
| COMMODITY | 161 | 40.99% | +0.0024 | −0.1032 |
| UNKNOWN | 141 | 100.00% | −2.0210 | −2.0210 |
| FUTURES | 69 | 39.13% | +0.5859 | +0.0684 |
| MEME | 13 | 100.00% | −9.5432 | −2.0079 |
| BOND | 4 | 25.00% | −0.0047 | +0.0219 |
| ETF | 2 | 50.00% | −0.0101 | +0.0588 |
| INDEX | 0 | — | — | — |

## Correlation

Across the nine classes with a priced mean:

| relationship | Pearson | Spearman |
|---|---:|---:|
| priced_coverage vs priced mean | **−0.5511** | **−0.4937** |
| priced_coverage vs published mean | **−0.6689** | **−0.5272** |

Sensitivity:
- Drop MEME + UNKNOWN (the two 100%-coverage extreme losers): **−0.1139**.
- n-weighted Pearson (CRYPTO dominates): **≈ +0.003** for priced mean, **+0.026** for published.
- Classes with n>=100: −0.509; classes with n>=30: −0.620 (still driven by UNKNOWN).

So the unweighted negative correlation exists, but it is **not stable**: it is driven by two extreme
high-coverage classes and disappears without them or when class size is weighted.

## Argument

1. **Coverage is class-structured.** It ranges from 0% (INDEX) to 99.5% (CRYPTO), and the low-coverage
   classes are also the small-n classes (BOND 4, ETF 2, FUTURES 69, COMMODITY 161). That is a
   comparability problem regardless of the correlation sign.
2. **It does not recreate the original dilution confound in a stable direction.** The original defect
   was low-coverage classes being dragged toward zero by placeholder rows, which made them look worse.
   After the live filter, the unweighted correlation is negative mainly because MEME and UNKNOWN are
   both fully covered and extremely negative; remove them and the relationship collapses to −0.11.
3. **A coverage multiplier is not a repair.** Dividing or covarying by coverage assumes missingness is
   random. It is not: unjoined rows average −0.0828 vs −0.0435 for joined rows. The measured correlation
   is a warning that class means are not comparable, not a coefficient that "corrects" them.
4. **The remaining bias is selection/small-n, not a fixed dilution factor.** CRYPTO supplies 95.5% of
   live rows; the other classes have 2–612 rows after filtering. Any class ranking is dominated by
   CRYPTO and by small-class noise.

**Finding:** priced_coverage is **not independent of class** (unweighted Pearson −0.55, Spearman −0.49),
so class means cannot be treated as exchangeable. But it does **not** stably recreate the original
dilution confound; the correlation is outlier-driven and vanishes under n-weighting or after removing
MEME/UNKNOWN. Do not apply a coverage correction, and do not rank classes on these means.

## What to do instead

- Report **n and priced coverage beside every class mean**, as the table already does.
- Compare within class over time or against a within-class benchmark; do not compare across classes.
- Resolve the missing/EXPIRED rows from prices; that, not division by coverage, removes the bias.
- Keep the cost gate and any class ranking behind a power floor; small-n CLEARS are not results.

next_probe: recompute this correlation after EXPIRED/price reconciliation; if it remains negative with
stable class sizes, revisit; do not use it as a correction factor.
