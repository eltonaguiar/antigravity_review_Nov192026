# DSR refusal guard — `dsr.py`

**Date:** 2026-11-24 · **Decision:** refuse below `n_min` (not "drop DSR from commit messages")
**File:** `CONTEST/tools/dsr.py` · **Author:** ghcopilot

## What was broken

Commit `9c9eda3` published `DSR = 0.999983991176608` in a commit message. It was computed on
`CONTEST/trial_ledger.db`, whose `trials` table contained **4 rows, all fixtures**:

| run_id | family | variant | sharpe_oos | kept |
|---|---|---|---:|---:|
| dummy-run-1 | dummy | dummy-A | 0.9 | 0 |
| dummy-run-1 | dummy | dummy-B | 1.1 | 0 |
| cron-run | cron_dummy | dummy-C | 1.4 | 0 |
| cron-run | cron_dummy | dummy-D | 0.6 | 0 |

The arithmetic was *correct*. With `mean = 1.0` and sample `sd = 0.3367`,
`z = (1.4 − 0) / 0.3367 = 4.16`, so `Φ(4.16) = 0.99998`. The number was **meaningless**, and it is
the most authoritative-looking wrong figure in the estate because a commit message is immutable and
the module docstring cites Bailey & López de Prado (2014).

## Why "refuse" rather than "drop it from commit messages"

1. **The commit-message generator is not in this repo.** There is no `EVALUATION_HARNESS` file and no
   workflow containing a `cron:` commit message, so that option is not implementable here.
2. **Refusal fixes the commit message anyway** as a side effect: a refusal emits *no number* for the
   message to quote.
3. Refusal protects **every** consumer (dashboard, report, API), not just one output channel. Hiding
   a number in one place leaves it quoted everywhere else.

## What changed

- `MIN_TRIALS_FOR_DSR = 30` — matches this estate's house `n < 30 = INSUFFICIENT` convention.
- `DSRNotComputable(RuntimeError)` — raised **instead of returning a float**.
- Fixture detection on `run_id` / `family` (`dummy|fixture|fake|synthetic|placeholder|sample`, or a
  leading `test`). Fixtures are refused because *n rows of a fixture is not an n*.
- `dsr_from_db(..., allow_fixtures=False, min_trials=None)` — the escape hatch exists **only** to
  unit-test the estimator; a reporting path must never set it.
- CLI prints `DSR=REFUSED source=… (no number emitted)` to **stderr** and exits **2**.

## Verification (measured, not asserted)

| case | ledger | result |
|---|---|---|
| real ledger | `CONTEST/tools/trial_ledger.db` (13 rows) | `REFUSED: 11 of 13 rows are fixtures`, exit 2 |
| 40 legit rows | temp db, `live-run-1`/`trend` | `DSR=0.992945034457317`, exit 0 |
| 40 fixture rows | temp db, `dummy-*` | `REFUSED: 40 of 40 … fixtures`, exit 2 |
| escape hatch | same fixture db, `--allow-fixtures` | number returned, exit 0 |
| **invariant** | real ledger | stdout contains **no** `DSR=<number>` — PASS |

`py_compile` clean.

## Known limitation (disclosed, not hidden)

The fixture filter is **name-based, so it is incomplete**: rows like `famA` / `var_alpha` / `r01` are
fixtures by any reasonable reading but contain none of the keywords — which is why the 13-row ledger
reports "11 of 13" rather than 13 of 13.

This is covered by the hard floor, not by the filter: `n = 13 < n_min = 30`, so that ledger is
refused **either way**. The two checks are OR'd. A future ledger with 30+ plausibly-named fixture
rows would still pass — the durable fix is to filter at the **write** (`trial_log.py`), not to
broaden a regex.

## Two divergent ledgers (found while verifying)

`CONTEST/trial_ledger.db` (4 rows, all `kept=0`) and `CONTEST/tools/trial_ledger.db` (13 rows,
`kept=1` on four) are **both live and different**. Any DSR therefore also depends on *which ledger*
is read — the same comparability break as the four different `n_trials` in circulation. Reconcile
these before any DSR is quoted. `42_HARVEST_UPGRADE_2026-11-24/zoocode/union_trial_ledgers.py`
appears to be an attempt at exactly that.
