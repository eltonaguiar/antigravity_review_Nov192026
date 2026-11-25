# Audit -- Track B `class_calibration.md` / `.json`

zoo-savant, 2026-11-25. Audited at origin (`42_HARVEST_UPGRADE_2026-11-24/tracker/`).
Every number below is recomputed from the published JSON, not restated from it.

## Inversion verdict (the headline)

**UNDERDETERMINED** -- not REAL, not CONFOUNDED.

The ordering `HOLD > BUY > STRONG_BUY` is in the published means, but no pairwise
difference is significant, so the ordering cannot be established:

| comparison | means | z | two-sided p |
|---|---|---|---|
| HOLD vs STRONG_BUY | +2.8798 vs +1.2818 | +1.650 | **0.0990** |
| HOLD vs BUY | +2.8798 vs +1.6708 | +1.539 | **0.1239** |
| BUY vs STRONG_BUY | +1.6708 vs +1.2818 | +0.528 | **0.5974** |

These three p-values were **recomputed by me** from `mean_net_pct`, `n` and the
per-bucket CIs (SE = CI half-width / 1.96, then a two-sample z on
`sqrt(se_a^2 + se_b^2)`). They agree with the figures in the audit brief to the last
digit (0.099 / 0.124 / 0.597), so the brief's numbers are reproducible -- but note
that they are **not stored in the artifact**, which publishes per-bucket CIs only and
no difference CIs at all.

The `inverted` verdict rests on `rho = -0.04673` with permutation `p = 0.9995`,
which is a placebo-backed statement about the *sign* of the rank correlation, not
about the bucket ordering. Both can be true: rho is negative and none of the
ordering differences is resolvable.

## The three defects

### 1. `design_effect = 0.38` -- CONFIRMED (arithmetic), REINTERPRETED

`(t_raw / t_cluster)^2 = (4.117 / 6.709)^2 = 0.3766` -> published `0.38`. Exact.

Observations per symbol: `963 / 485 = 1.986`. A design effect below 1 means the
per-symbol aggregation produced *less* variance than the pooled marks, so
`t_cluster` (6.709) exceeds `t_raw` (4.117). The defect is not the arithmetic but
the implied reading: a sub-1 design effect is "no measurable inflation", **not** a
licence to prefer the larger t. Quote `t_cluster` with an interval.

### 2. `mde_pct = 18.868` -- REFUTED as a units error

`mde = 2 * sd / sqrt(n / n_symbols)` implies `sd = 0.1329`, i.e. **13.29%**
annualised -- a per-symbol-mean dispersion. The `%` label is therefore correct.

What is wrong is its usefulness: an 18.9%/yr MDE cannot resolve any plausible equity
premium, so the null is *uninformative* rather than negative.

### 3. SPY benchmark -- CONFIRMED (gate not met)

`class_calibration.json` labels SPY "characteristic-matched on the only available
characteristic: all rows are US equities". Being a US equity is not a match on beta,
size, sector or valuation, none of which is used. The label is wrong and **gate 2 is
UNMET**.

The matched re-baseline has since been run: rho -0.0440 (p 0.9945) versus SPY's
-0.04673 (p 0.9995), so the sign survives -- the benchmark is a labelling defect, not
the cause of the inversion.

## Gate status

No gate was lowered. The artifact still reports `inverted` and `monotone: False`, and
nothing here upgrades it: the sign is negative under both benchmarks, and the bucket
ordering is unresolvable at these p-values.

next_probe: recompute the bucket differences with a symbol-clustered bootstrap
directly (rather than the normal approximation from per-bucket CIs), since SELL at
n=13 is too thin for the published CI to be trusted and the normal approximation may
understate the tails.

## DEFECT 2 CORRECTION 2026-11-25

**Supersedes these two sentences in “2. `mde_pct = 18.868`” above** (kept for the record, not deleted):

> “`mde = 2 * sd / sqrt(n / n_symbols)` implies `sd = 0.1329`, i.e. **13.29%**
> annualised -- a per-symbol-mean dispersion. The `%` label is therefore correct.”

> “What is wrong is its usefulness: an 18.9%/yr MDE cannot resolve any plausible equity
> premium, so the null is *uninformative* rather than negative.”

**Correction:** 13.29 is the **row-level monthly SD**, not an annualised per-symbol-mean
dispersion. Consequently 18.868 is a **per-month MDE**, not a per-year figure. The measured
per-symbol-mean SD is **5.751 pp per monthly hold** (69.01 pp/yr annualised); applying the file’s
own formula gives:

`2.802 * 5.751 / sqrt(485) = 0.732 pp/month = 8.78 pp/yr`.

**The figure to cite is 8.78 pp/yr**, not 18.868; 18.868 is 2.15× the measured MDE and requires
the unmeasured 148.3 pp/yr sigma.

**Does the “null is uninformative” conclusion survive at 8.78 pp/yr? YES.** An 8.78%/yr MDE is
still larger than a plausible equity premium of a few percent per year, so the test cannot
resolve the magnitude it is being asked about; the null remains weak/uninformative, not negative.
The magnitude concern is smaller than stated but not resolved. The design-effect and SPY sections
are untouched by this correction.
