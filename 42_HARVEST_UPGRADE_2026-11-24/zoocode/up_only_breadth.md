# Up-only breadth -- the definition the deliberation settled on

zoo-savant, 2026-11-24. Measured from `analyst_actions.csv`
(122,746 rows, 308 tickers).

**Why this needed running:** the deliberation unanimously rejected `init` and `reit`,
so the defensible event is `up` only -- but every breadth table so far measured
`up/down/init` (A), `+reit` (B) or `+main` (C), never up-only.

**Context for reading it:** `up` is only 9,873 of 122,746 rows (8%), while `main` is 88,341. Up-only is therefore far below the 28/18/11 measured for A.

## Table

| column | up events | firms | 300 | 500 | 750 | biggest firm |
|---|---|---|---|---|---|---|
| up only, no filter | 9,873 | 227 | 10 | 1 | 0 | BofA Securities (556) |
| up only, 182-day clean window | 8,498 | 220 | 6 | 0 | 0 | BofA Securities (439) |

**Pairs:** 6,012 broker-stock pairs have at least one `up`; 5,696 of them still have one after the 182-day window.

No floor was changed to make the numbers look better.

## Consequence for the prereg

The defensible definition is **not measurable at the current ticker count**: nobody clears 750 clean events under the 6-month rule (the biggest firm has 439), so it needs more tickers -- or the floor should be restated as an MDE, since even 750 events still resolves only about 19%/yr.
