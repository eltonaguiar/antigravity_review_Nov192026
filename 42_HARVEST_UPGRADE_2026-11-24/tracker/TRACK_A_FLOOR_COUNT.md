# Track A floor count -- is any firm measurable?

zoo-savant, 2026-11-25. Read from `42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv`
on origin/main. **`firm_skill_weights.csv` was not edited.** Only `n_clean_events` was used; the
effect columns were ignored (most are blank).

## (1) The largest record

| | value |
|---|---|
largest `n_clean_events` | **551** |
firm | **BofA Securities** |

## (2) Firms at or above each floor

| floor | firms |
|---|---|
>= 300 | **9** |
>= 500 | **1** |
>= 750 | **0** |

Of 221 rows, 219 carry an `n_clean_events` value (2 are blank).

## (3) Is any single firm measurable?

**Yes, but barely and only at the lowest bar: exactly one firm (BofA Securities, 551) clears 500
clean events and none clears 750, so Track A's null is mostly a data limit rather than a clean
negative** -- the nine firms above 300 can be measured, and the remaining 210 cannot be judged at
all from this file.

## What that means for the verdict

- A firm-level verdict is only meaningful for those nine firms; for the other 212 the honest
  output is `underpowered`, which is a statement about data, not about skill.
- The programme's own breadth work explains the fix: clean events scale with ticker breadth, and
  firms reaching 750 went from 0 at 155 tickers to 11 at 308 under a looser event definition. Under
  the stricter UP-only definition even the best firm reaches only 439, so the floor is not
  reachable at the current universe.
- No gate was lowered to produce a verdict here.

next_probe: recompute this count after the next breadth expansion, and report the ticker count at
which the first firm clears 750.
