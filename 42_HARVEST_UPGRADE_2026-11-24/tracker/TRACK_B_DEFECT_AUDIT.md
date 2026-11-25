# Track B defect audit -- design_effect 0.38, mde_pct 18.868, SPY gate

Consolidation audit. Author: hermes coordinator, 2026-11-25.
Reason: the copilot panel composer refused a poke on three consecutive ticks, so
the named deliverable tracker/TRACK_B_DEFECT_AUDIT.md is written here by the
coordinator from content already verified on origin/main. This file consolidates
and cites; it does not re-run the study.

Primary sources (all on origin/main, 2026-11-25):
- tracker/class_calibration.md -- its 2026-11-25 defect ledger (Track B self-audit)
- tracker/score_inversion_test.md -- section 3 (independent design-effect check)
- ghcopilot/AUDIT_OF_TRACK_B.md -- Track C audit (counts 1-7)

## Defect 1 -- design_effect = 0.38 below 1 -- REPRODUCED, interpretation wrong

- Arithmetic reproduces exactly: (t_raw / t_cluster)^2 = (4.117 / 6.709)^2 = 0.3766.
- A sub-1 design effect means clustering REDUCED the variance estimate; that is plausible
  when within-symbol correlation is negligible with ~1.99 observations per symbol
  (n=963 over 485 symbols).
- The defect is interpretive, not arithmetic: a design effect of 0.38 is an estimate from
  485 clusters, NOT a licence to quote the larger t. Quote t_cluster with an interval;
  treat sub-1 as "no measurable inflation", not "the clustered test is more powerful".
- The inverted verdict does NOT depend on it: it rests on rho and its permutation p.
- Cross-check: score_inversion_test.md section 3 independently measures symbol-cluster
  design effects of 1.31 (HOLD), 1.36 (BUY), 0.99 (STRONG_BUY) on a different event set;
  it does NOT reproduce 0.38, so Track B 0.38 is not a universal constant.

## Defect 2 -- mde_pct = 18.868 as a units error -- REFUTED, units are consistent

- MDE = 2.80 * sigma_symbol_mean / sqrt(n_symbols) at 80 percent power gives 18.868
  percent with sigma_symbol_mean ~ 148.5 percent annualised over 485 symbols. That is a
  per-symbol mean dispersion, not per-trade; the percent label is correct.
- The real concern is magnitude, not units: an 18.9 percent/yr MDE cannot resolve any
  plausible equity premium, so the null is UNINFORMATIVE rather than negative. The
  artifact already publishes the MDE beside the null, which is the right discipline.

## Defect 3 -- benchmark SPY fails the characteristic-matched gate -- REPRODUCED

- class_calibration.json records benchmark = "SPY (characteristic-matched on the only
  available characteristic: all rows are US equities)". Being a US equity is not a match
  on beta, size, sector or valuation; none are used.
- Corrected label: SPY is a single-index market benchmark and gate 2 is UNMET.
- The gate failure changes bucket LEVELS (magnitudes), not the sign of rho; bucket levels
  must not be quoted until a real ADV/momentum-matched benchmark is built.

## Provenance limitation -- arithmetic only, not a raw re-run

class_calibration.json holds aggregates only (no row-level records), and the stated raw
input ZOOCODE/harvest/*.json is absent from origin (ghcopilot/AUDIT_OF_TRACK_B.md count 2;
504 excluded rows never disclosed). So this audit reproduces the PUBLISHED arithmetic; it
cannot re-derive the aggregates from raw data. The correct remedy remains: commit the
row-level input or a per-row checksum.

## Inversion is NOT established -- do not call the ordering monotone or real

- class_calibration.md itself says monotone across buckets: False.
- The bucket ordering HOLD +2.8798 (n=164) > BUY +1.6708 (n=579) > STRONG_BUY +1.2818
  (n=207) is NOT a demonstrated inversion. Independent pairwise tests:
  HOLD-STRONG_BUY p=0.099, HOLD-BUY p=0.124, BUY-STRONG_BUY p=0.597 -- all above 0.05,
  and the per-bucket confidence intervals overlap.
  score_inversion_test.md verdict: UNDERDETERMINED.
- What stands is the rho sign from the permutation placebo (rho -0.0467, perm p 0.9995),
  which is a different claim from a bucket ordering.

## Verdict

| defect | status |
|---|---|
| 1 design_effect 0.38 | REPRODUCED arithmetically; interpretation corrected (no t inflation) |
| 2 mde_pct 18.868 | REFUTED as units error; MDE too large to be informative |
| 3 SPY gate 2 | REPRODUCED; label corrected, gate 2 UNMET |

None of the three restores monotonicity or a positive rho. No gate was lowered.

next_probe: commit the row-level input (ZOOCODE/harvest export or per-row checksum) so the
963 included and 504 excluded rows are auditable, then rebuild a genuine
ADV/momentum-matched benchmark.

## MDE CORRECTION 2026-11-25

**Supersedes the two lines in "Defect 2" above** (kept for the record, not deleted):

> "MDE = 2.80 * sigma_symbol_mean / sqrt(n_symbols) at 80 percent power gives 18.868
> percent with sigma_symbol_mean ~ 148.5 percent annualised over 485 symbols. That is a
> per-symbol mean dispersion, not per-trade; the percent label is correct."

**The 148.5 percent sigma is not measured by anything in the repo and is WITHDRAWN.**
Measured from `tracker/CLASS_CALIBRATION_PRICE_PANEL.csv` (963 included rows, 485
symbols, gross excess = `(exit/entry - 1) - (bench_exit/bench_entry - 1)`):

| quantity | measured |
|---|---|
| row-level SD | 13.293 pp |
| per-symbol mean SD | **5.751 pp per monthly hold** |
| annualised, x12 | **69.01 pp/yr** |

The same formula on the measured sigma gives
`2.802 * 5.751 / sqrt(485) = 0.732 pp/month = ` **8.78 pp/yr**.
18.868 is therefore **2.15x** the measured MDE, and is consistent only with a sigma of
148.3 pp/yr -- most plausibly the row-level SD annualised (159.5 pp/yr), which is the
wrong unit for a formula that already divides by `sqrt(n_symbols)`.

**Does the magnitude concern survive? YES.** An MDE of about **8.8 percent/yr** against a
plausible equity premium of a few percent per year still leaves the null weak: the test
cannot resolve the size of edge it is being asked about, so "no effect detected" remains
UNINFORMATIVE rather than negative. The concern is smaller than stated (8.8, not 18.9) but
it is not resolved, and the conclusion is unchanged.

next_probe: replace every remaining citation of 18.868 / 148.5 with the measured
8.78 pp/yr and 69.01 pp/yr.
