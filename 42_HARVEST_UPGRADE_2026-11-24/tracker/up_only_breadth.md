# UP-ONLY breadth

zoo-savant, 2026-11-25. Source `analyst_actions.csv` (122,746 rows, 308 tickers).
Event definition: **UP only** -- `init` and `reit` rejected, per the 6-model deliberation.

## Pairs

- distinct broker-stock pairs with at least one `up`: **6,012**
- survivors of a 6-month no-prior-up/down filter (182 days): **5,696**

## Firms above each floor

| set | 300 | 500 | 750 | biggest firm |
|---|---|---|---|---|
| raw (all `up`) | 10 | 1 | 0 | BofA Securities (556) |
| 6-month filtered | 6 | 0 | 0 | BofA Securities (439) |

## Does UP clear the 750-firm floor? **NO**

The best firm reaches 439 clean UP events under the 6-month rule, against a 750 floor.

## Context -- this is definition-specific, not a contradiction

My earlier breadth table (A = `up/down/init`) reported **28/18/11**. That is a *different
event definition*, so the two do not disagree: with UP only, `up` is 9,873 of 122,746 rows
(8%), while `main` alone is 88,341. Narrowing the definition from three actions to one
roughly halves the count at each floor (11 -> 0 at 750).

Consequence for the prereg: the defensible UP-only definition is not measurable at this ticker
count, so either the universe grows or the floor is restated as an MDE.
