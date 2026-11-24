# Up-only breadth -- the definition the deliberation settled on

zoo-savant, 2026-11-24. Source: `analyst_actions.csv` (308 tickers). Script:
`42_HARVEST_UPGRADE_2026-11-24/zoocode/up_only_breadth.py`.

**Why this is the decisive measurement:** a 6-model deliberation unanimously rejected
`init` and `reit` as events, so the defensible definition is `up` only. Every earlier
breadth table measured `up/down/init` (A), `+reit` (B) or `+main` (C) -- never this.

**Context:** `up` is only 9,873 of 122,746 rows (8%), while `main` is 88,341.

## Table

| set | up events | firms | >300 | >500 | >750 | biggest firm |
|---|---|---|---|---|---|---|
| raw (no filter) | 9,873 | 227 | 10 | 1 | 0 | BofA Securities (556) |
| 6-month no-prior-up/down | 8,498 | 220 | 6 | 0 | 0 | BofA Securities (439) |

**Pairs:**
6,012 broker-stock pairs have at least one `up`; 5,696 still have one
after the 182-day filter.

## Consequence for the prereg

The defensible definition is **NOT measurable at the current ticker count**: no firm clears 750 clean events under the 6-month rule (biggest: BofA Securities, 439). It needs more tickers -- or the floor should be restated as an MDE, since even 750 events resolves only about 19%/yr.

No floor was changed to make these numbers look better.
