# UP-only MDE price gap — 11 known missing events

**Read-only follow-up to `UP_ONLY_MDE.md`, 2026-11-25.** No existing file edited; no prices invented.

## The gap

- Brief count: **439** clean UP-only events.
- Reconstruction: **436** events / 223 symbols.
- Usable in the MDE: **425** events.
- Known excluded: **11** (436 − 425). If the brief's 439 is taken literally, **3 further events**
  are not in the reconstruction and cannot be identified by symbol/date from the available file;
  the table below covers every event in the 436 that is not in the 425.

## Every event in the 436 but not the 425

| symbol | publication date | missing bar | exact fetch attempted | obtainable now |
|---|---|---|---|---|
| EA | 2012-08-01 | stock entry/exit (1 bar total in panel) | `yf.Ticker("EA").history(period="max", interval="1d")` | **No** — returned 1 bar (2026-08-04) |
| EA | 2014-01-29 | stock entry/exit | same | **No** — only 1 recent bar |
| EA | 2016-01-15 | stock entry/exit | same | **No** — only 1 recent bar |
| EA | 2017-07-26 | stock entry/exit | same | **No** — only 1 recent bar |
| EA | 2023-10-10 | stock entry/exit | same | **No** — only 1 recent bar |
| AVB | 2023-05-15 | stock entry/exit (1 bar total in panel) | `yf.Ticker("AVB").history(period="max", interval="1d")` | **No** — returned 2 bars (2026-08-14/10-05) |
| K | 2019-12-20 | stock entry/exit (0 bars) | `yf.Ticker("K").history(period="max", interval="1d")` | **No** — delisted/no price data |
| K | 2024-08-02 | stock entry/exit (0 bars) | same | **No** — delisted/no price data |
| BK | 2015-09-17 | stock entry/exit (0 bars) | `yf.Ticker("BK").history(period="max", interval="1d")` | **No** — delisted/no price data |
| BK | 2018-03-07 | stock entry/exit (0 bars) | same | **No** — delisted/no price data |
| BK | 2021-03-24 | stock entry/exit (0 bars) | same | **No** — delisted/no price data |

No event is missing only the SPY benchmark; SPY history is present. The missing side is the stock's
entry and/or +21-session exit bar.

## Can any be priced now?

**No.** The individual fetches returned only 1 bar for EA, 2 recent bars for AVB, and zero bars for
K/BK. No historical event-window prices are available from the exact symbols; substituting a different
ticker or a guessed price would violate the no-invention rule.

## Old vs new MDE

No event can be added, so the expanded set is identical to the old set:

| set | usable n | SD (bp) | MDE t=2 iid | MDE t=2 cluster DE 1.36 |
|---|---:|---:|---:|---:|
| old (`UP_ONLY_MDE.md`) | **425** | **1,036.94** | **100.60 bp** | **117.32 bp** |
| expanded attempt | **425** | 1,036.94 | 100.60 bp | 117.32 bp |

No recomputation is possible without 11 stock histories. The three unlocated events in the 439 count
would also need a symbol/date manifest before any fetch.

## Verdict

**GAP PERSISTS — 425 usable events; 11 known stock histories unobtainable (EA/AVB/K/BK), plus 3
brief-count events not located. MDE unchanged at 100.60 bp iid / 117.32 bp cluster-adjusted (DE 1.36).**

next_probe: obtain a survivorship-aware historical price source for EA (pre-2026), AVB (pre-2023),
K and BK (delisted), and reconcile the brief's 439 to a symbol/date manifest; do not substitute a
successor ticker.
