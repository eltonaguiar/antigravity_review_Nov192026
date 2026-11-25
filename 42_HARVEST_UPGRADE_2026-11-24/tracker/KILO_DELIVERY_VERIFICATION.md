# KILO delivery verification

**Verified against `origin/main` at `c575c01`** using `git cat-file -e` per exact path; line count from `git show` (splitlines).

| path | lines | status |
|---|---:|---|
| `42_HARVEST_UPGRADE_2026-11-24/tracker/grade_ordinals_draft.csv` | 638 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/grade_ordinals_frozen.csv` | 612 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` | 222 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/AUDIT_OF_TRACK_A.md` | 74 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/AUDIT_OF_TRACK_C.md` | 34 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/score_inversion_test.md` | 62 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/score_inversion_test.json` | 88 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/target_bundle_test.md` | 55 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/target_bundle_test.json` | 53 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/input_assertions.py` | 135 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/DENOMINATOR_AUDIT.md` | 49 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/PLACEBO_AUDIT.md` | 62 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/pattern_tests.md` | 31 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/pattern_tests.json` | 31 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/DATA_MANIFEST_2026-11-24.json` | 31 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/EDGE_SEARCH_PLAN.md` | 90 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/polymarket_leaderboard_snapshot.py` | 49 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/COST_GATE_BY_CLASS.md` | 92 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/COST_GATE_BY_CLASS.json` | 1955 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/cost_gate_by_class.py` | 83 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/EXPIRED_ROOT_CAUSE.md` | 97 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/EXPIRY_MARK_TO_MARKET.md` | 86 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/RESOLVE_FAILED_RECOMPUTE.md` | 49 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/RESOLVE_FAILED_RECOMPUTE.json` | 16663 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/recompute_resolve_failed.py` | 64 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_COVERAGE_TABLE.md` | 40 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_COVERAGE_TABLE.json` | 85 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/class_coverage_table.py` | 40 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/TWO_TABLE_RECONCILIATION.md` | 85 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/EXPECTANCY_CORRECTED.md` | 42 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/DILUTION_SENSITIVITY.md` | 35 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/DILUTION_SENSITIVITY.json` | 122 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/dilution_sensitivity.py` | 21 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/COVERAGE_BIAS_CHECK.md` | 69 | **PRESENT** |
| `12_INSIDER/collect_form4.py` | 257 | **PRESENT** |
| `12_INSIDER/form4_events_wide.csv` | 2641 | **PRESENT** |
| `12_INSIDER/form4_summary_wide.md` | 34 | **PRESENT** |
| `12_INSIDER/H260_CORRECT_SIZING.md` | 53 | **PRESENT** |
| `12_INSIDER/h260_correct_sizing.json` | 56 | **PRESENT** |
| `12_INSIDER/h260_correct_sizing.py` | 104 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/DEPLOYMENT_LOG.md` | 69 | **PRESENT** |
| `CONTEST/trials/README.md` | 11 | **PRESENT** |
| `CONTEST/trials/trials_union.jsonl` | 19 | **PRESENT** |
| `docs/ledger.html` | 23 | **PRESENT** |
| `docs/CROWD_SOURCE_PROFITABILITY_AUDIT.md` | 229 | **PRESENT** |
| `docs/SPECULATIVE_PROFITABILITY_AND_RISK.md` | 122 | **PRESENT** |
| `docs/speculative-markets.html` | 135 | **PRESENT** |
| `docs/harvest.html` | 558 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/UP_ONLY_MDE.md` | 61 | **PRESENT** |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/UP_ONLY_MDE_PRICE_GAP.md` | 58 | **PRESENT** |

**Total artifacts: 50. Present: 50. Missing: 0.**

Path-case note: the H260 JSON is `12_INSIDER/h260_correct_sizing.json` (lowercase h); an uppercase `H260_CORRECT_SIZING.json` does not exist and was not counted.

All listed paths are independently checkable with the exact `git cat-file -e origin/main:<path>` command.

## Re-verification — 2026-11-25T07:26:49Z

Exact-path re-run against `origin/main` at **d6a0a28** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T07:32:50Z

Exact-path re-run against `origin/main` at **9fdcceb** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T07:38:49Z

Exact-path re-run against `origin/main` at **702e00f** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T07:44:49Z

Exact-path re-run against `origin/main` at **8592609** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T07:50:49Z

Exact-path re-run against `origin/main` at **858f6c6** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T07:56:49Z

Exact-path re-run against `origin/main` at **8ed1d10** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:02:49Z

Exact-path re-run against `origin/main` at **916d1d3** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:08:49Z

Exact-path re-run against `origin/main` at **f33a927** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:14:40Z

Exact-path re-run against `origin/main` at **d63b9c7** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:20:50Z

Exact-path re-run against `origin/main` at **0ccd4ff** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:26:51Z

Exact-path re-run against `origin/main` at **b67ef66** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:32:49Z

Exact-path re-run against `origin/main` at **470fbf4** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:38:48Z

Exact-path re-run against `origin/main` at **5578adb** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:44:50Z

Exact-path re-run against `origin/main` at **c0e01fd** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:50:49Z

Exact-path re-run against `origin/main` at **e571559** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T08:56:40Z

Exact-path re-run against `origin/main` at **5ceb504** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:02:49Z

Exact-path re-run against `origin/main` at **6358861** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:08:48Z

Exact-path re-run against `origin/main` at **0d25c82** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:14:49Z

Exact-path re-run against `origin/main` at **35dea02** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:20:48Z

Exact-path re-run against `origin/main` at **3e85995** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:26:51Z

Exact-path re-run against `origin/main` at **8cd6c79** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:32:49Z

Exact-path re-run against `origin/main` at **274a00b** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:38:42Z

Exact-path re-run against `origin/main` at **e872845** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:44:48Z

Exact-path re-run against `origin/main` at **9d4a650** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:50:49Z

Exact-path re-run against `origin/main` at **b388f09** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T09:56:41Z

Exact-path re-run against `origin/main` at **0dfcf1b** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:02:40Z

Exact-path re-run against `origin/main` at **fda0fa6** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:08:49Z

Exact-path re-run against `origin/main` at **bd96d8c** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:14:49Z

Exact-path re-run against `origin/main` at **f20c63b** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:20:49Z

Exact-path re-run against `origin/main` at **8210370** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:26:49Z

Exact-path re-run against `origin/main` at **e51bf7a** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:32:49Z

Exact-path re-run against `origin/main` at **4297fd7** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:38:50Z

Exact-path re-run against `origin/main` at **0904105** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:44:50Z

Exact-path re-run against `origin/main` at **28006fc** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:50:50Z

Exact-path re-run against `origin/main` at **6b2e11c** using
`git cat-file -e origin/main:<path>` for all **48** paths listed above.

- **PRESENT: 48/48**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T10:56:43Z

Exact-path re-run against `origin/main` at **ea1aa68** using
`git cat-file -e origin/main:<path>` for all **49** paths (the 48 prior artifacts plus
`UP_ONLY_MDE.md`).

- **PRESENT: 49/49**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:02:50Z

Exact-path re-run against `origin/main` at **27cb325** using
`git cat-file -e origin/main:<path>` for all **50** paths (the 49 prior artifacts plus
`UP_ONLY_MDE_PRICE_GAP.md`).

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:08:49Z

Exact-path re-run against `origin/main` at **61c0d91** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:14:49Z

Exact-path re-run against `origin/main` at **5d3f08f** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:20:49Z

Exact-path re-run against `origin/main` at **a57421d** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:26:49Z

Exact-path re-run against `origin/main` at **cc94277** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:32:50Z

Exact-path re-run against `origin/main` at **362d3b3** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:38:49Z

Exact-path re-run against `origin/main` at **e9a781f** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:44:49Z

Exact-path re-run against `origin/main` at **677a254** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:50:50Z

Exact-path re-run against `origin/main` at **d205306** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T11:56:50Z

Exact-path re-run against `origin/main` at **ac92baa** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:02:40Z

Exact-path re-run against `origin/main` at **85ec07d** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:08:49Z

Exact-path re-run against `origin/main` at **d795f53** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:14:49Z

Exact-path re-run against `origin/main` at **cd66b90** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:20:49Z

Exact-path re-run against `origin/main` at **b3317f6** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:26:48Z

Exact-path re-run against `origin/main` at **125ede1** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:32:50Z

Exact-path re-run against `origin/main` at **baeb7a7** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:38:49Z

Exact-path re-run against `origin/main` at **ce14c2e** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:44:49Z

Exact-path re-run against `origin/main` at **14dbbaf** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:50:49Z

Exact-path re-run against `origin/main` at **387ac22** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T12:56:49Z

Exact-path re-run against `origin/main` at **cf60703** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:08:49Z

Exact-path re-run against `origin/main` at **c6471e0** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:14:49Z

Exact-path re-run against `origin/main` at **35ff4c0** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:20:49Z

Exact-path re-run against `origin/main` at **0dc5d9a** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:26:48Z

Exact-path re-run against `origin/main` at **f7a1776** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:32:49Z

Exact-path re-run against `origin/main` at **69c17e9** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:38:49Z

Exact-path re-run against `origin/main` at **392ce4a** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:44:49Z

Exact-path re-run against `origin/main` at **3897fb3** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:50:41Z

Exact-path re-run against `origin/main` at **d2c935e** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T13:56:48Z

Exact-path re-run against `origin/main` at **0c893b0** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:02:49Z

Exact-path re-run against `origin/main` at **3697021** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:08:49Z

Exact-path re-run against `origin/main` at **e9236ba** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:14:49Z

Exact-path re-run against `origin/main` at **ba5eaaf** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:20:49Z

Exact-path re-run against `origin/main` at **8c7f721** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:26:49Z

Exact-path re-run against `origin/main` at **6cdc76d** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.

## Re-verification — 2026-11-25T14:32:49Z

Exact-path re-run against `origin/main` at **7d0543e** using
`git cat-file -e origin/main:<path>` for all **50** paths listed above.

- **PRESENT: 50/50**
- **MISSING: 0**
- No path was rebuilt; no missing-path rebuild was attempted.
