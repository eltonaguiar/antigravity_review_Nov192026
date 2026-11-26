# Futures data feasibility — bounded note

**Kilo · 2026-11-26 · read-only desk review.** Question: can the event-study pipeline be extended
to futures under the existing cost model? **Answer: NO-GO on current assets — DATA LIMIT.** No
futures event-pair dataset and no continuous, roll-adjusted futures price history exist in the repo.
This note records what the sources do and do not provide; it does not claim coverage.

## 1. What the event study needs

The event-study spec (`ghcopilot/ANALYST_SCORECARD_SPEC.md`, §1) requires a dated event per
instrument, a price path from event to horizon, a benchmark, and an all-in round-turn cost. The only
populated event file is `tracker/analyst_actions.csv`: **122,747 rows**, and **0** symbols ending in
`=F`. Its instruments are US-listed equities. No futures contract is an event instrument in the
current study.

Futures therefore need their own dated event feed and their own price series. Neither is present.
Futures appear in the repo only as picks or failed picks, not as events.

## 2. Sources checked

| source | what it offers | what it does not establish |
|---|---|---|
| `kilocode/FREE_DATA_SOURCES.md`, §Futures | CME/ICE delayed settlements, CFTC COT, Yahoo `=F`, Stooq, Barchart (ToS) | no roll-adjusted continuous series; no history depth; no dated instrument-level event feed |
| `kilocode/DB_AND_HARVEST_DESIGN.md`, crowd layer | CFTC COT, free weekly, futures/FX/commodity positioning | positioning only; not prices and not per-contract events |
| `kilocode/ANALYST_HARVEST_PLAN.md`, class plan | futures: bank research is not machine-readable free; use COT + trend, 1w–3m | no instrument-level catalyst dates; no measurement of available history |
| `26_ASSET_CLASS_DOSSIERS/07_FUTURES.md` | futures have roll, margin and contract multipliers; ledger n=4; live `trading_picks` n=66; labels are contaminated; measured slippage UNMEASURED | no continuous series, no clean futures event set, no usable cost measurement |
| `tracker/CLASS_COVERAGE_TABLE.md` | FUTURES: 69 rows, 27 priced (39.13%) | pick rows, not event pairs; no price history |
| `tracker/COST_GATE_BY_CLASS.md` / `.json` | FUTURES 12.07 bp is explicitly an "equity ceiling proxy; no roll-adjusted series" | no measured futures cost; 6.71/12.07 are cash ETF/equity costs |
| `tracker/DATABASE_SCHEMA.md` | pick tracking stores entry, marks, and scores | no futures contract, roll, multiplier, or continuous-contract table |
| `tracker/RESOLVE_FAILED_RECOMPUTE.json` | 193 futures rows across 10 `=F` symbols; all 193 have `exit_price == entry_price` | failed resolutions, not a price series or usable event panel |

**History depth:** none of the cited sources records a first/last date for any `=F` series. CME/ICE
delayed settlements are recent-session pages, not deep history. Yahoo `=F` and Stooq may carry daily
bars, but a continuous contract requires an explicit front-month and roll rule; no such series or
depth measurement exists in the repo. **No depth figure is asserted here because none was measured.**

## 3. Does the 6.71 bp / 12.07 bp cost model extend to futures?

**No, not as a measured cost.** The cost table charges **6.71 bp** for the deep bucket and
**12.07 bp** for the normal bucket; those are measured cash ETF/index and equity round turns. The
futures entry is **12.07 bp only as a proxy**, and the artifact itself says
"equity ceiling proxy; no roll-adjusted series". Futures all-in cost is commission per contract plus
exchange/clearing/NFA fees, bid-ask spread, market impact, and roll slippage, and it is not a fixed
cash-equity bp charge. A futures result that uses 6.71 or 12.07 bp without a measured contract-level
schedule is **not cost-validated**.

## 4. Go / no-go

Pre-registered condition: **measurable only if there are at least 300 clean event pairs with
continuous futures prices.**

Current evidence:

- futures event pairs available: **0** (`analyst_actions.csv` has no `=F` symbols and no other
  dated futures event file was found);
- continuous, roll-adjusted futures series available: **0**;
- futures pick rows available: 69 raw / 27 priced; ledger n=4; live n=66 — none are event pairs;
- futures failed-price rows: 193 across 10 `=F` symbols, all `exit_price == entry_price` — unusable
  as a price path.

The 300-pair threshold is not close to being met. **Verdict: NO-GO / DATA LIMIT.** This is not a
claim that futures are unprofitable; it is a statement that the current assets cannot measure them.

## 5. Minimum evidence needed to revisit

1. A dated futures event feed with an unambiguous instrument-to-contract map.
2. A continuous front-month series with a documented roll rule (back-adjust or ratio), covering the
   same event/horizon pairs.
3. At least 300 clean event pairs after exclusions, with the exclusion count printed.
4. A measured contract-level round-turn cost schedule, including commission and roll.

Until all four exist, any futures event-study number would be fabricated. No gate is lowered and no
verdict beyond DATA LIMIT is issued.
