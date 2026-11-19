# Verification of the P0/P1 "correctness" commit (`3dfa66e`)

**Date:** 2026-11-19
**Commit under test:** `3dfa66e` — "feat(audit3): P0/P1 correctness — G8 alpha gate,
global-n DSR, G9 stress gate, blocklist wiring, forward shadow emission, denylist watchdog"
**Method:** three independent read-only agents traced each claim to file:line;
every line reference below was then re-grepped by the author. Claims that failed
were fixed in branch `fix/audit3-alpha-scope` (commit `b9dd4378e65`).

## Result at a glance

| Item | Peer claim | Verified at `3dfa66e` | Fixed |
|---|---|---|---|
| P0-2 blocklist → emission | fixed | **HOLDS** (both save paths filtered) | residual fail-open on import error, documented |
| P0-1 stop-fill overshoot | already implemented | **HOLDS** (`_check_tp_sl_intrabar` L722, `_gap_fill_price` L695) | — |
| P0-4 G8 alpha gate | implemented | **PARTIAL — does not meet its acceptance test** | yes |
| P0-5 DSR global-n | implemented | **PARTIAL** (payload slice, not registry) | yes |
| P1-1 denylist watchdog | implemented | **HOLDS** (hourly, fails red, file-age based) | — |
| P1-4 forward shadow emission | implemented | **FAILS** (no scheduled writer; one manual fill) | yes |
| P0-3 at-issue stamping | NOT implemented | confirmed absent (`at_issue_` not in `pick_schema.py`) | left open |
| source-family bucket | (not in the list) | **ungated: could reach PROVEN_T2 on raw stats** | yes |

## The three real gaps

### 1. G8 proves the class, not the strategy (`audit3_tribunal.py:940-994`)

`_alpha_lo(ac, direction)` reads `by_slice["CLASS/DIR"]` then `by_class["CLASS"]`.
`audit3_selection_alpha.py` emitted only those two maps. So every strategy cell
inside a class with positive alpha inherited the proof, and a strategy that
underperformed buy-and-hold inside an outperforming class still reached
`PROVEN_T2`. The acceptance criterion — "a beta-only 'profitable' cell cannot
reach PROVEN_T2" — was false.

**Fix:** the sidecar now emits `by_strategy` keyed `CLASS/STRATEGY/DIRECTION`;
the gate requires same-scope alpha for strategy cells and records anything
weaker as `class_proxy` (flagged, demoted). The gate also publishes whether it
ran, so an absent sidecar cannot read as "all passed" (`3dfa66e` silently
fail-opened and still printed the G8 convention string).

### 2. DSR corrected for the slice, not the search space (`audit3_tribunal.py:1119`)

`n_trials = len(strat_groups)` counts distinct cells in the loaded 3,500-row
slice. The registry is ~658 strategies (`MASTER_AUDIT.md`, 2026-11-14). The
stated done-when — "global trial counter fed into `deflated_sharpe`" — was not
met.

**Fix, with a caveat the peer plan missed:** applying 658 to *every* tier
demotes promising cells below the CANDIDATE `DSR >= 0.50` floor and empties the
forward queue — the ratchet-to-zero failure this review exists to flag.
PROVEN_T2 now pays the global null-max; CANDIDATE uses the observed bucket
width. Verified numerically: a thin n=120 cell scores DSR 0.95 at 45 trials,
0.80 at 658 — enough for CANDIDATE, not for PROVEN.

### 3. Forward ledger never accrues

`reports/forward_observations.jsonl` holds 430 rows, all `H-119`, last written
`2026-11-19T07:20Z` by the one-off commit `5c0c42d`. No workflow referenced
`forward_observations_ingest`, and it defaults to a dry run. "Shadow emission"
existed as a module, not as a running process — so P1-4's done-when ("the ledger
accrues rows") was false.

**Fix:** new `.github/workflows/forward-observations-ingest.yml`, cron
`41 */6 * * *`, runs `--apply`, commits the ledger, and prints every
PROVEN/CANDIDATE cell that has no forward instrument (rather than inventing
shadow trades for pods that have no registered condition).

### 4. Source families were the one ungated verdict bucket

`source_families` were emitted straight from `evaluate_cell()` — no BH, no
`_promote` (FDR/DSR/forward), no harm gate. They could reach `PROVEN_T2` on raw
statistics alone. Now gated like every other bucket.

## Fix commits

Two commits on `fix/audit3-alpha-scope` (worktree
`.kilo/worktrees/vanilla-handsaw-audit3`, based on `3dfa66e`). The second exists
because an adversarial review of the first found five defects, including one that
would have left G8 fail-open on the published path.

`b9dd4378e65` — first pass:

- `alpha_engine/audit3_selection_alpha.py` — emit `by_strategy`
- `alpha_engine/audit3_tribunal.py` — scope-aware G8, `GLOBAL_TRIAL_FLOOR`,
  `n_trials_local`/`dsr_local`, family gating, corrected G9 comment
- `.github/workflows/forward-observations-ingest.yml` — scheduled ingest
- `tests/test_audit3_tribunal.py` — 9 new tests
- `updates/2026-11-19-audit3-g8-scope-global-dsr-family-gates-forward-schedule.md`

`3844a4e34e2` — second pass, closing the review's findings:

- `require_alpha=True` on the CLI path + `demote_proven_without_alpha()`: a
  missing alpha sidecar (the ledger workflow tolerates one) now demotes
  `PROVEN_T2` instead of proving nothing.
- `direction_key` normalisation: `BUY` no longer becomes `"?"` (it produced an
  inverted benchmark and an unmatchable `by_strategy` key).
- Rows with `issued_at == closed_at` are skipped: that case fabricated a zero
  benchmark and `alpha == pnl`.
- Coverage floor: proof now requires `alpha_n >= max(20, 0.5 × cell.n)`, so a
  20-row sample cannot certify a 500-row cell.
- Workflow pins `ref: main`, refuses to commit off-main, and fails when
  `n_admissible == 0`.

Verification: `79 passed` across the six audit3/forward test files; workflow
YAML parses. Not pushed.

## Residual gaps (honest list)

1. **P0-3 at-issue stamping** remains unimplemented. It is a writer change, not
   a gate change, and stamping retroactively would recreate the leak.
2. **Symbol-level alpha** does not exist, so symbol cells are demoted by G8
   (fail-closed). A per-symbol alpha is the next measurement, not a code fix.
3. **Forward coverage** is one hypothesis wide (H-119). The new job reports the
   hole; filling it needs a registered condition per pod.
4. **Pre-existing test pollution:** `pytest tests/ -k "audit3 ..."` fails 3
   slippage tests that pass when their files run alone (a global constant is
   mutated by another test). Reproduces without these changes; recorded, not
   fixed.
5. **Blocklist fail-open:** `forward_validator.py:811` wraps the filter in
   `except Exception: pass`, and the scraper sets `_is_blocked_pick = None` on
   import failure. Cheap to make loud; not changed here.
6. **Alpha/tribunal row-set mismatch:** alpha is measured on
   `picks.recent_closed`, while the tribunal may score the hash-matched
   canonical view. The new `alpha_n` coverage floor makes the gap visible per
   cell but does not remove it; feeding both the same rows is a pipeline change.

## Reviewer note

This is the second consecutive commit labelled "P0/P1 correctness" whose done-when
criteria were only partly met. The pattern — a gate implemented at the wrong
scope, and a ledger written once by hand — is the same one the review named:
the machinery exists, but nothing verifies that the acceptance test is actually
satisfied. Each claim in a "done" commit needs a test that fails when the claim
is false; that is now true for the four items fixed here.
