# PROVEIT -- which folder is which

Two folders use the same "PROVEIT_24-11-2026...KILOCODE_AGENT" stem. They are NOT duplicates: each
answers a different question with a different data source. One was renamed for clarity and one was merged in and removed (2026-11-24).

| folder | data source | question it answers | canonical for |
|---|---|---|---|
| `PROVEIT_24-11-2026_KILOCODE_AGENT/` | `data/market_prices.csv` (1255 real daily bars, 2021-11..2026-11) | Can a real portfolio be built, and does a philosophy beat holding, with whole shares and fees? | **scenario sizing, fees, buy-and-hold vs timing** |
| `PROVEIT_24-11-2026KILOCODE_AGENT_SIGNALS/` | this repo's own measured per-class expectancy (38_FINAL...) | Is the SYSTEM's OWN signal edge provable after cost, against the 4.32% hurdle? | **signal edge, bootstrap CIs, parameter sweep, forward-test log** |

Page counterpart: `PROVEIT_KILOCODE.html` (site root) renders the KILO scenario proof.

## Reading rule

A "proven" number from _MARKETS or _KILOCODE_AGENT is about **market beta** in a bull-heavy window.
A "proven" number from _SIGNALS is about **this system's picks**. Never quote one as the other: the
index-only row in _SIGNALS (-25.9%) and the buy-and-hold row in _KILOCODE_AGENT (+18.3%/yr) are the
same words for different things.

## Merge record (2026-11-24)

`PROVEIT_24-11-2026KILOCODE_AGENT/` (live-yfinance 60/40 + MA-timing variant) was
**merged into `PROVEIT_24-11-2026_KILOCODE_AGENT/`** under
`MERGE_FROM_MARKETS_2026-11-24/` and the source folder was deleted, per instruction.
Its findings were preserved in the canonical README, not discarded. The canonical
folder is the one with a committed price CSV, so it reproduces without network.
