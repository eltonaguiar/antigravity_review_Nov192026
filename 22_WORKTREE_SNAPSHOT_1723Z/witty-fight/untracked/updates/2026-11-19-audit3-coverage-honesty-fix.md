# audit3 coverage honesty: >100% share and the auto-expired claim (2026-11-19)

## What was broken
Two statements in the audit3 coverage block were not true of the live ledger,
which is built from the canonical full-book view.

1. **A share above 100%.** Live `audit3_ledger.json` reports
   `scored_rows = 8605` and `valid_closed_picks = 8175`, so
   `scored_share_of_valid_pct = 105.26`. A ratio above 100% is not a percentage
   of anything; it means the two denominators disagree and the canonical view is
   the larger set.
2. **A false exclusion claim.** `excluded_cohorts[auto_expired].reason` said
   timeouts are "dropped before scoring and never counted against the strategy",
   and the statement said exclusions are never scored. The canonical book still
   contains timeout and flat exits (`status: FLAT` = 133 rows in the canonical
   snapshot; `zero_pnl_count = 134` in the live payload). The cohort is a label,
   not a guarantee the rows are absent.

Both were present on `origin/main` as of `e48387f0fd9` (line 654 and the
`auto_expired` reason block in `payload_coverage`).

## What changed
`alpha_engine/audit3_tribunal.py`

- `_coverage_statement(..., valid=, flat_rows=, canonical_mode=)` now:
  - says auto-expired rows that survive integrity checks are **retained in the
    canonical view at their resolved exit**, and cites the zero-P&L count when
    present;
  - appends a "Denominator check" sentence when `scored > valid`, naming both
    numbers and the signed delta.
- `payload_coverage()`:
  - withholds `scored_share_of_valid_pct` (set `None`) when it would exceed 100,
    and keeps the raw number in `scored_share_of_valid_pct_raw`;
  - adds `valid_denominator_inconsistent` and a `denominator_reconciliation`
    block (`canonical_rows`, `dashboard_valid_closed_picks`, `delta`,
    `scored_but_not_dashboard_valid`, `consistent`, `note`); the 430-row
    scored-but-not-"valid" set is named instead of appearing as an unexplained
    arithmetic hole.
  - computes `canonical_mode` before building `excluded_cohorts`, so the
    auto-expired reason is worded for the mode actually used. Payload-slice mode
    keeps the strict "dropped before scoring" wording.

## Verification
```
$ python3 -m pytest tests/test_audit3_tribunal.py tests/test_audit3_coverage_alpha.py \
    tests/test_audit3_enforcement.py tests/test_audit3_selection_alpha.py \
    tests/test_audit3_expectancy_gates.py -q
57 passed in 6.61s
# after the candidate-counter fix: 11 passed in tests/test_audit3_coverage_alpha.py
```

Also fixed in the same module: `summary.n_candidate` counted strategy cells only
while the live ledger carried a symbol-level CANDIDATE (FOREX AUDJPY LONG, n=31),
so the KPI read 0 beside a non-empty candidate row. Added `n_candidate_symbols`
and `n_candidate_segments`, each from its own table.

New regression tests in `tests/test_audit3_coverage_alpha.py`:

- `test_scored_rows_above_valid_never_publish_over_100_pct` — reproduces the live
  8,605 / 8,175 case and asserts `None` + raw 105.26 + delta +43.
- `test_auto_expired_wording_matches_canonical_reality` — asserts the canonical
  wording and that "never counted" is gone.
- `test_payload_slice_mode_keeps_strict_auto_expired_wording` — no behaviour drift
  for the non-canonical path.
- `test_summary_candidate_counts_match_each_table` — each headline candidate count
  equals the count in its own table.

## Merge note
This worktree is 1,063 commits behind `origin/main`. The edited function region is
byte-identical to `origin/main`'s, so the same two hunks apply there; the rest of
the file in this worktree was deliberately left at HEAD so the diff is the fix
only.
