# VOID — DSR quoted in commit `9c9eda3`

**Status:** the number below is void. Do not cite it, and do not treat it as a prior art result.
**Recorded:** 2026-11-24 by ghcopilot · **Guard that now prevents a recurrence:** `dsr.py` +
`DSR_GUARD.md` (commit `b83911d`) · **Tests:** `test_dsr_guard.py` (5/5, with negative control)

## The void number

> `DSR = 0.999983991176608`

Quoted in the commit message of `9c9eda3` ("cron: EVALUATION_HARNESS task queue … DSR
0.999983991176608 on dummy log (Bailey & Lopez de Prado 2014) …").

## Why it is void

It was computed on `CONTEST/trial_ledger.db`, `trials` table, **4 rows, all fixtures**:

| run_id | family | variant | sharpe_oos | kept |
|---|---|---|---:|---:|
| dummy-run-1 | dummy | dummy-A | 0.9 | 0 |
| dummy-run-1 | dummy | dummy-B | 1.1 | 0 |
| cron-run | cron_dummy | dummy-C | 1.4 | 0 |
| cron-run | cron_dummy | dummy-D | 0.6 | 0 |

`mean = 1.0`, sample `sd = 0.3367`, so `z = (1.4 − 0) / 0.3367 = 4.16` and `Φ(4.16) = 0.99998`.
**The arithmetic is correct; the input is fabricated.** A DSR of 0.99998 asserts "almost certainly
not a false discovery" — computed on four synthetic rows, none of which was even kept.

The citation is what makes this dangerous: "Bailey & Lopez de Prado (2014)" lends the number an
authority it does not have. It is not a multiple-testing correction of anything.

## Why a file, when the commit message is immutable

A commit message cannot be edited, so the correction has to be *findable* from the wrong number
rather than replacing it. This file's commit message contains `RETRACTION`, `9c9eda3` and the
literal `0.999983991176608`, so all three of these locate the correction:

```
git log --oneline --grep=9c9eda3
git log --oneline --grep=RETRACTION
git log -S'0.999983991176608' --oneline
```

## What replaced it

Nothing. That is the point. `dsr.py` now **refuses** rather than emitting a number when the ledger
holds fixture rows or `n < MIN_TRIALS_FOR_DSR (30)`. There is no valid DSR for this estate yet,
because no clean trial ledger with n ≥ 30 exists.

## Standing instruction until two ledgers are reconciled

`CONTEST/trial_ledger.db` (4 rows) and `CONTEST/tools/trial_ledger.db` (13 rows, `kept=1` on four)
are **both live and different**. Any DSR also depends on *which one* is read — the same
comparability break as the four different `n_trials` in circulation. Do not quote a DSR from either
until they are reconciled (`zoocode/union_trial_ledgers.py` looks like the attempt).
