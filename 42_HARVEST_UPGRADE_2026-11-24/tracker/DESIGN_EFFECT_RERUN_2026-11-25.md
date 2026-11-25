# Design effect -- raw re-run (2026-11-25)

zoo-savant. Script: `tracker/rerun_design_effect.py` (seed 20261124, 2000 symbol-cluster
bootstrap replicates). `class_calibration.md` and `.json` were NOT edited.

## Inputs, measured

| | value |
|---|---|
| included rows (`included == 1`) | **963** |
| symbols | **485** |
| return | `(exit_close/entry_close - 1) - (bench_exit_close/bench_entry_close - 1)` |
| mean EQUITY excess | **0.018869** (1.887 pp) |

Note: the task brief said 492 symbols; the committed panel actually has **485**, which
matches `class_calibration.json`. I report the measured 485.

## Bootstrap result

| quantity | value |
|---|---|
| `SE_iid` (analytic `sqrt(var/n)`) | **0.004284** |
| `SE_cluster` (SD of 2000 resampled means) | **0.002562** |
| **DE = (SE_cluster / SE_iid)^2** | **0.3578** |
| ratio DE / 0.3766 | **0.950** |

## Verdict: REPRODUCED

The number that decides it is the ratio **0.950**: a raw re-run that never saw the
published figure lands within 5% of `0.3766` (from `(4.117/6.709)^2`). So `design_effect
= 0.38` is a genuine property of this sample, not an artefact of the arithmetic -- the
per-symbol means really are less dispersed than 963 independent rows would be.

Two caveats, both already recorded in the MDE audit:
- A sub-1 design effect means *no measurable inflation*, NOT that the clustered test is
  more powerful. With 963 rows over 485 symbols (1.99 per symbol) there is little
  clustering left to inflate.
- It does not restore monotonicity: STRONG_BUY 1.2818 < BUY 1.6708 < HOLD 2.8798.

next_probe: repeat the bootstrap with the 2 monthly cohorts resampled instead of symbols
(there are only two, so it will be unresolvable) to see how much of the sub-1 DE is the
cohort structure rather than genuine within-symbol correlation.
