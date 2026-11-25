# Adversarial critique: does reporting `priced_coverage` fix comparability?

zoo-savant, 2026-11-25. Measured from `ejaguiar1_stocks.at_pick_outcomes` (read-only).

## Short answer: it does not fix it -- it *relabels* it.

Reporting coverage converts one defect into a different one. It removes the *silent*
dilution (an aggregate that quietly mixes well-covered and barely-covered classes) and
replaces it with a *visible but unrepaired* weighting: the pooled number is still dominated
by whichever class has the most priced rows. Disclosure is necessary and not sufficient.

## The evidence: coverage is a function of class, measured

`priced_coverage` = resolved (WON/LOST) / all rows, per class:

| class | rows | resolved | priced_coverage |
|---|---|---|---|
| CRYPTO | 38,218 | 28,681 | 0.750 |
| BLANK | 204 | 189 | 0.926 |
| FOREX | 16,039 | 2,789 | 0.174 |
| COMMODITY | 5,882 | 891 | 0.151 |
| EQUITY | 1,984 | 233 | 0.117 |
| ETF | 181 | 23 | 0.127 |
| BOND | 154 | 16 | 0.104 |
| FUTURES | 473 | 29 | 0.061 |
| INDEX | 314 | 3 | 0.010 |
| UNKNOWN | 141 | 141 | 1.000 |

The spread is 0.010 to 0.750 -- a **75x** ratio between the best-covered real class and the
worst. Coverage is not a nuisance parameter that happens to vary; it is almost perfectly
confounded with the class label.

### The 'backfill' figures, checked

The brief cites 'CRYPTO 33.3% backfill versus INDEX 100%'. The INDEX 100% **reproduces**:
all 314 INDEX rows come from backfill passes. CRYPTO does not: 12,730 of its 16,360 rows
carrying a class label are backfilled, i.e. **77.8%**, not 33.3%. Across all rows, 37,115 of
63,792 (58.2%) are backfilled. The figures may be computed on a different denominator, so I
report mine with the query attached rather than claiming the brief is wrong.

## Why disclosure alone fails -- four ways it still misleads

1. **The pooled mean is a weighted average of incomparable populations.** With CRYPTO at
   75% and INDEX at 1%, a cross-class 'average' is mostly a crypto statistic. Reporting the
   coverage column does not reweight anything; a reader must do that themselves.
2. **A coverage figure invites the wrong inference: 'more coverage = more trustworthy'.**
   Here the most-covered class (CRYPTO 0.750) has a POSITIVE mean (+0.1681%) but a negative
   median (-1.3100%), and the least-covered (INDEX 0.010) has 3 resolved rows. High coverage
   does not make a class's estimate reliable, and low coverage does not make it wrong -- the
   two are different failure modes that a single percentage conflates.
3. **Coverage is measured on the same rows the estimate uses**, so it cannot detect the
   missingness MECHANISM. If rows are missing because they EXPIRED (the 29,654 EXPIRED rows
   store a placeholder 0), coverage is measuring a resolution policy, not data availability.
   The right question -- is missingness informative? -- is not answered by the fraction.
4. **Comparability needs a common unit, not a common caveat.** Classes differ in horizon,
   volatility and pick count, so even at equal coverage their means would not be comparable
   without standardising (per-day, per-trade, benchmark-adjusted).

## What would actually fix it, in order of strength

1. **Report only within-class**, with the across-class number suppressed until coverage within
   each class clears a floor (the programme already uses n>=30 or 100 elsewhere).
2. **Standardise before pooling**: per-trade excess vs a matched benchmark, expressed per
   day, so a 21-day crypto trade and a 126-day equity trade are in the same unit.
3. **Inverse-coverage weighting** if a pooled number is required, with the weights published
   -- this is the only way the pooled mean reflects classes in proportion to their real share
   rather than their priced share.
4. **Test whether missingness is informative**: compare the resolved-row characteristics
   (symbol, strategy, entry date) against the expired ones. If EXPIRED rows differ systematically,
   the resolved set is not a random sample and no coverage percentage repairs it.

## Verdict

**Disclosed, not fixed.** `priced_coverage` is worth publishing -- an unreported 75x
comparability gap is worse -- but it changes the *label* of the problem, not its magnitude.
Any cross-class conclusion drawn after it is published is still dominated by CRYPTO.

next_probe: compute the per-class mean and median on a per-day, matched-benchmark basis and
check whether the class ranking changes -- if it does, the pooled figure was an artefact of
horizon and coverage together, not of class skill.
