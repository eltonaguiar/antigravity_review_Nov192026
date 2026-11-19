# Proof — commands and outputs

Commit tested: `eltonaguiar/findtorontoevents_antigravity.ca` `origin/main` @
`e2d552093172` (contains `6abfa22364e` + `77718be66922`). Handoff reviewed:
`AGENT_FOLDERFRAMEWORK` `eef9e9d`.

## 1. Landed commits are on main

```
git -C E:\findtorontoevents_antigravity.ca merge-base --is-ancestor 6abfa22364e origin/main
git -C E:\findtorontoevents_antigravity.ca merge-base --is-ancestor 77718be66922 origin/main
```

both return true (exit 0). `git show --stat 6abfa22364e`:

```
 .github/workflows/forward-observations-ingest.yml | 113 ++++++
 alpha_engine/audit3_selection_alpha.py             |  38 ++-
 alpha_engine/audit3_tribunal.py                    | 232 +++++++---
 tests/test_audit3_expectancy_gates.py              |   9 +-
 tests/test_audit3_selection_alpha.py               |  31 ++-
 tests/test_audit3_tribunal.py                      | 132 ++++++
 updates/2026-11-19-audit3-g8-scope-...-forward-schedule.md | 97 +++
 7 files changed, 582 insertions(+), 70 deletions(-)
```

## 2. Isolated test worktree

A sparse, detached worktree was used so the live checkout's local modifications were not
touched:

```
git -C E:\findtorontoevents_antigravity.ca worktree add --no-checkout --detach \
    C:\Users\zerou\AppData\Local\Temp\opencode\fe-review-main origin/main
git -C <wt> sparse-checkout init --cone
git -C <wt> sparse-checkout set alpha_engine tests tools .github docs reports audit_dashboard/data
git -C <wt> checkout
# HEAD=e2d552093172
```

## 3. Focused suite (the handoff's six files)

```
python -m pytest tests/test_audit3_tribunal.py tests/test_audit3_expectancy_gates.py \
  tests/test_audit3_edge_hunt.py tests/test_audit3_selection_alpha.py \
  tests/test_forward_observations_ingest.py tests/test_audit3_cost_basis.py -q
```

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 7.13s
```

Relevant tests that pin the four decisions (`tests/test_audit3_tribunal.py`):
`:531` class proxy rejected for a strategy cell, `:546` strategy proof accepted,
`:560` CANDIDATE kept but flagged, `:570`/`:575` gate-not-run reporting,
`:588` trial count floor, `:606` PROVEN pays global DSR, `:629` require_alpha demotion,
`:641` alpha coverage floor.

## 4. DSR floor behaviour on the live ledger

```python
cells = json.load(open("audit_dashboard/data/audit3_ledger.json"))["cells"]
g = [c for c in cells if c.get("dsr") is not None]
l = [c for c in cells if c.get("dsr_local") is not None]
```

```
cells 359 dsr_scored 66 dsr_local_scored 66
dsr>=0.95 2
dsr_local>=0.5 2
local passes but global fails 0
max dsr 0.9998 max local 0.9999
n>=200 with dsr<0.95 4 of 4
```

Interpretation: with this payload the tier split changes no outcome (no cell is
CANDIDATE-eligible only under the local width), and every cell with n>=200 still fails the
global 0.95 bar.

Code path: `alpha_engine/audit3_tribunal.py:137` (`GLOBAL_TRIAL_FLOOR = 658`,
`global_trial_count`), `:1016-1030` (`dsr` from `n_trials`, `dsr_local` from
`n_trials_local`), `:1036` (`_promote`: PROVEN checks `dsr`, CANDIDATE checks
`dsr_local >= 0.50`).

## 5. Live ledger facts (same file)

```
summary = {n_rows: 8613, n_cells_total: 359, n_cells_tested: 67,
           n_cells_dsr_scored: 66, n_proven: 0, n_candidate: 0,
           n_kill: 8, n_insufficient: 292}
selection_alpha.gate = {applied: true, tested: 434, demoted: 0,
                        scopes: {strategy: 37, class_proxy: 390, class: 7}}
alpha status = {beta_dominant: 357, proven: 1, unmeasured: 1}
proven-status cell: EQUITY / vol-contraction-scout / LONG, n=62,
                    alpha_ci_lo=0.1745, alpha_n=61, need_n=31, verdict=WEAK
```

Code path for decision 1: `alpha_engine/audit3_tribunal.py:1310`
(`apply_selection_alpha_gate`; strategy -> slice -> class lookup, `class_proxy` never
proves, coverage `max(20, 0.5*n)`), and
`alpha_engine/audit3_selection_alpha.py` (`by_strategy` emitted keyed
`CLASS/STRATEGY/DIRECTION`; `t0 >= t1` degenerate rows skipped).

Direction keys match on both sides: `audit3_tribunal._direction` calls
`symbol_identity.direction_key`, and the sidecar imports the same function.

## 6. Decision 3: require_alpha

- CLI: `alpha_engine/audit3_tribunal.py:2004` passes `require_alpha=True`.
- Fallback: `:1730` calls `demote_proven_without_alpha((cells, symbols, classes))` when
  `alpha_gate_report["applied"]` is false, and publishes `require_alpha: true`.
- Test: `tests/test_audit3_tribunal.py:629`.
- Live ledger has `gate.applied=true`, so the fallback is not currently firing.

Secret risk, verified by reading:

```
tools/db_env.py   : prefers DB_PASSWORDS_JSON["stocks"], then MYSQL_PASSWORD,
                    DB_STOCKS_PASSWORD, DB_PASS_STOCKS (comment says individual
                    vars "may be stale")
audit3-ledger.yml :104,157 export only DB_PASS_STOCKS; both steps skip when it is empty
```

So a repo where only `DB_PASSWORDS_JSON` is set would skip price backfill and selection
alpha, and `require_alpha` would demote every PROVEN. Passing both env vars and gating on
either is the same pattern the new ingest workflow already uses.

## 7. Decision 4: forward ingest mismatches

`.github/workflows/forward-observations-ingest.yml`:

- line 39 `uses: actions/checkout@v4` — **no `ref: main`**. On `workflow_dispatch` this
  checks out the selected ref but still pushes `HEAD:main` (line 87).
- line 57 runs `python3 -m alpha_engine.forward_observations_ingest --apply ...`
- line 71 prints `admissible={rep.get('n_admissible')}` but never asserts it
- line 76 `assert rows, "forward ledger is empty after an --apply run"` — checks the whole
  ledger, not this run's admissibility

`alpha_engine/forward_observations_ingest.py`:

- `main()` at `:438`; returns `3` only when ingestion raises (no DB / no creds)
- returns `0` at `:466` for a successful run, including `n_admissible == 0`

Consequence: a run with zero admissible rows prints `admissible=0`, appends nothing,
passes the non-empty-ledger assert because 430 historical rows exist, and stays green.
