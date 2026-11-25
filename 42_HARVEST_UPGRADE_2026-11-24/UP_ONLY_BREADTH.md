# UP-ONLY BREADTH -- measured, not assumed

Measured 2026-11-25 by zoo (Zoo Code) on `origin/main` of this repo at
**f4ed281eeff8dbd81cec798ca8107ecb0a81f665**. Before this file, no such path existed on
`origin/main` (`git cat-file -e origin/main:42_HARVEST_UPGRADE_2026-11-24/UP_ONLY_BREADTH.md`
= MISSING), so Track A had never measured a single firm on that commit.

## Input (exact blob, not a worktree copy)

| field | value |
|---|---|
| source | `42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv` @ `origin/main` |
| blob | `b1f0cbbb485ea15d2a39f6c063b5f9783f0deb54` |
| sha256 | `9dd7d8cbf4ecd907e513422e157a96a5f3bcdde3cf0b48f66e6d9ea269a30f11` |
| rows | 122,746 |
| tickers | 308 |
| date span | 2011-12-08 .. 2026-11-12 |
| action mix | main 88,341 · up 9,873 · down 9,720 · init 8,812 · reit 6,000 |
| firm keys | 291 normalized firms (`firm_norm`), 293 raw names |

`firm_norm` merges exactly two raw-name groups: `B of A Securities` + `Bank of America`
-> BofA Securities, and `Deutsche Bank` + `Deutsche bank` -> Deutsche Bank. No blank
firm or symbol fields; no duplicate `(symbol, firm, date, action, grade, target)` tuples.

## Definitions

- **UP** = `action == 'up'` (a grade upgrade). `init`, `reit` and `main` are excluded --
  the deliberation rejected `init`/`reit` as events, and `main` is not a direction change.
- **NO FILTER** -- every UP row, counted per firm.
- **6-MONTH** -- a UP counts only if the most recent prior `up` *or* `down` for the same
  broker-stock pair is at least **182 days** earlier, or there is none. `init`/`reit`/`main`
  do not reset the window, because the rule is specifically "no prior up or down".
- **Pair** = one `(firm_norm, symbol)` combination. A firm with three UPs on one ticker is
  one pair and three events.

## Table

| set | UP events | firms | > 300 | > 500 | > 750 | biggest firm |
|---|---:|---:|---:|---:|---:|---|
| UP only, no filter | 9,873 | 227 | 10 | 1 | 0 | BofA Securities (556) |
| UP only, 6-month no-prior-up/down | 8,498 | 220 | 6 | 0 | 0 | BofA Securities (439) |

**Distinct broker-stock pairs:**

| set | pairs |
|---|---:|
| with at least one UP | 6,012 |
| surviving the 6-month filter | 5,696 |
| surviving a strict first-ever-UP rule (no prior up/down of any age) | 3,536 |

The strict variant is a sensitivity check, not the agreed definition: it drops any pair
that has ever been touched before, so it is dominated by history length. Under it no firm
clears even 300 (biggest: Goldman Sachs, 143).

## Top firms

| rank | no filter | events | 6-month | events |
|---:|---|---:|---|---:|
| 1 | BofA Securities | 556 | BofA Securities | 439 |
| 2 | Morgan Stanley | 481 | Morgan Stanley | 427 |
| 3 | Goldman Sachs | 462 | Goldman Sachs | 411 |
| 4 | J.P. Morgan | 456 | J.P. Morgan | 383 |
| 5 | UBS | 364 | UBS | 321 |
| 6 | Citi | 357 | Citi | 305 |
| 7 | Deutsche Bank | 334 | Deutsche Bank | 284 |
| 8 | Jefferies | 318 | Jefferies | 284 |
| 9 | Wells Fargo | 316 | Wells Fargo | 278 |
| 10 | Barclays | 301 | Barclays | 274 |

Seven firms with raw UPs drop to zero under the 6-month rule.

## What this means

- **No firm reaches 750 under either definition.** The 750 clean-event floor is unmet; the
  best firm has 439, i.e. 59% of the floor, so its interval is ~1.3x wider than the floor
  would give (`sqrt(750/439) = 1.31`).
- **The 500 floor is met by exactly one firm (BofA, 556) with no filter and by none with
  the 6-month rule.** Any per-firm skill claim at 500 therefore depends on not applying
  the clean-window filter.
- **Breadth is real but shallow:** 227 firms produce UPs, yet only 10 clear 300 raw and 6
  clear 300 clean. The distribution is a long tail, not a set of deep firms.
- UP is only 8.0% of all rows, and the 6-month rule removes 1,375 of 9,873 UPs (13.9%).

## Provenance

Every number above was re-derived in this session from the CSV blob `b1f0cbbb` on
`origin/main` with an independent script (counts of `action == 'up'` per `firm_norm`, and
the 182-day rule on `(firm_norm, symbol)` prior up/down timestamps). The same figures were
independently produced by `42_HARVEST_UPGRADE_2026-11-24/zoocode/up_only_breadth.py`
(output in `zoocode/up_only_breadth.json`, committed earlier): 9,873 / 227 / 10 / 1 / 0 and
8,498 / 220 / 6 / 0 / 0, pairs 6,012 -> 5,696. Both agree exactly.

Limits: this counts events, not returns. It says nothing about whether UPs predict
anything -- that is the separate preregistered test
(`tracker/PREREG_ANALYST_UPGRADE_TEST.md`). Coverage is 308 tickers of largely US equities
with analyst history; ETFs, bonds, crypto, forex and futures are not covered by the source.
