# PLAN status — 2026-11-24

**Branch:** `proveit-extended-scenarios-2026-11-24` · **PR:** #5 (OPEN, MERGEABLE/CLEAN, 9 files)
**Review repo HEAD at time of writing:** `e80004e`

## Workstreams

| WS | Scope | State |
|---|---|---|
| A | PR #5 close-out | **done 8/8** — corrections committed `3070a95`, body replaced via REST, C1 audit `7940e8a` |
| B | Pages integrity | **done 7/7** — verifier `c21393e`, 0 broken internal links, `path: docs` confirmed |
| C | Cell sweep completion | **not started** — ~250 measurable cells outstanding |
| D | Defect-class lint | **done 7/7** — `e80004e` |
| E | Forward clocks / GHA | **not started** |
| F | Durability / handoff | **in progress** |
| G | Repo hygiene | **not started** |

## What is actually proven

- Live site serves **1 of 9** result files the README claims. Everything under
  `PROVEIT/` 404s because `pages.yml` uploads `path: docs` only.
- `9.18%` hold at $10K/$20K/$50K reproduces from `final/start` over the window
  (9.1571% calendar, 9.1817% trading-day).
- `+1.31/+1.42/+1.50pp` and `$44.61/$90.23/$226.80` reproduce exactly.
- `$374.84` is SPY's close on **2022-09-01**, bar 200, first tradeable bar after
  the SMA warm-up — generated in `provenance_2026-11-24T0350Z.json`, not typed.
- `n_days: 1255` is **trading** days. Divided by 365 it yields 13.58%, a 4.40pp error.

## What is NOT proven

- The new Pages paths are **404 until merge**. Do not claim otherwise.
- The forward clock has **0/30 trades**; it is not evidence of anything yet.
- The other three agents' `PROVEIT/` dirs remain unreachable and are not this
  PR's files to relocate.
- Classes 3 and 4 of `DEFECT_CLASSES.md` (data-source substitution, inert
  parameter) are **not caught by the linter at all**.

## Commits on this branch

| sha | what |
|---|---|
| `95452d2` | mirror results into `docs/PROVEIT` so Pages serves them |
| `3070a95` | correct the two-size range hiding the $10K loss; source the entry price |
| `7940e8a` | C1 claim-vs-committed audit |
| `c21393e` | A7 Pages cross-check + re-runnable verifier |
| `e80004e` | mechanise the defect class (lint, provenance, CI gates) |

## Next

1. WS-G hygiene: confirm no foreign files staged, retire `/tmp/fund-fix`.
2. WS-C: count measurable vs blocked cells from the ledger.
3. WS-E: forward clock — verify it counts, confirm GHA cannot fire off-branch.
