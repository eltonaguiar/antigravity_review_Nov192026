# Pick Tracking Database — Schema & Methodology

**Database:** `ejaguiar1_stocks` (MySQL 8.4.7, shared host)
**Created:** 2026-11-24 · **Owner:** Hermes · **Status:** first build live, 16 objects, 4 schema versions
**Repo path:** `42_HARVEST_UPGRADE_2026-11-24/tracker/`

> **Credentials are deliberately absent from this document and from every file in this repo.**
> They live only in `~/dbpasses.txt` on the Linux host (`eltonsGX10`). Every script here reads the
> password from a shell variable at runtime; none of them contain, log, or echo it. The connection
> host and database name are recorded because they are not secrets; the user is the database name.

---

## 1. Why this exists

Every page in this estate publishes picks — the harvest consensus, the per-class "best candidate"
table, and the ranked picks from four agents. **None of them was tracked.** A pick was published,
argued about, and forgotten; the next round re-argued it from scratch.

This database makes a pick an **append-only fact with a timestamp**, so the question "what would
have happened if we had actually taken that?" becomes answerable with data instead of opinion.

---

## 2. Design principles

**1. Immutable observations, derived outcomes, provenance — three separate concerns.**
A pick row is never rewritten. What it returned lives in `picktrack_marks` / `pick_resolution`.
Which fetch produced it lives in `source_run`. Rescoring can therefore never rewrite history.

**2. A label must be reproducible from its own row.**
This is the direct fix for a defect measured on 2026-11-24: the published harvest labels were a
pure function of the raw counts (two-condition rule → **71/71 agree**), but the page's own
documented rule was a score-only rule that reproduced only **60/71**. Eleven rows were labelled in
a way the page's text could not explain. No amount of schema hygiene prevents that unless the row
stores *which rule version produced the label* — hence `consensus_snapshot.label_rule_version`
pointing at `rule_version.rule_hash`.

**3. A derived number is worthless without its coverage.**
`fund_lookthrough.weight_coverage_pct` is mandatory, not decorative. A holdings-weighted consensus
computed over 60% of AUM is a different claim from one computed over 96%.

**4. A block must be recorded, not described.**
`source_run` stores endpoint, HTTP status, rows returned and error text for every fetch. An
`ACCESS_DENIED_403` is a row with a status, not a sentence in a note.

**5. Never invent a field the source does not provide.**
`analyst_registry.analyst_name` is nullable and is NULL for every row obtainable today, because the
free feed returns counts with no name. It stays NULL rather than being guessed.

**6. n < 30 is not a verdict.**
`picktrack_scores.verdict` defaults to `INSUFFICIENT_N`. A source with a small sample is reported
as insufficient, never as a win rate.

---

## 3. Object reference

### 3.1 Tracking core

| Table | Purpose | Key columns |
|---|---|---|
| `picktrack_picks` | **Immutable.** One row per published pick. | `id`, `source`, `published_at`, `symbol`, `basket_json`, `asset_class`, `direction`, `rule`, `cost_bps`, `benchmark`, `status` |
| `picktrack_entries` | The actual fill, separate from the pick so it can never be rewritten. | `pick_id` (unique FK), `entry_mode`, `entry_date`, `entry_price` |
| `picktrack_marks` | Daily mark-to-market. | `(pick_id, mark_date)` unique, `raw_pct`, `net_bps`, `benchmark_net_bps`, `excess_bps` |
| `picktrack_scores` | Per-source aggregate snapshots. | `as_of`, `source`, `n_picks`, `mean_net_bps`, `verdict` |
| `picktrack_events` | Append-only audit log of every schema/data action. | `event`, `detail`, `at` |
| `v_picktrack_latest` | View: picks joined to their newest mark. | — |

**Three entry tiers, all labelled, none faked:**

| `entry_mode` | When | Meaning |
|---|---|---|
| `next_open` | a session traded strictly after `published_at` | the tradable fill |
| `same_day_fallback` | market open but the day already started | a mark, **not** a tradable fill |
| `pending_entry` | no bar exists at or after publication | nothing has happened yet; no number is reported |

### 3.2 Analyst attribution (the harvest layer)

| Table | Purpose |
|---|---|
| `analyst_registry` | Firm + analyst identity, Wilson 95% CI, shrunk alpha, badge A/B/C gated on **n and** significance |
| `analyst_actions` | Firm-level dated actions (`init/upgrade/downgrade/reiterate/pt_change`) with `pt_from`, `pt_to`, `action_date`, `source`, and a generated `dedupe_key` |

**Measured reality, 2026-11-24:** `/stock/recommendation` → HTTP 200, **counts only, no firm, no
analyst name, no dated event**. `/stock/upgrade-downgrade` → **HTTP 403**. `/stock/price-target` →
**HTTP 403**. FMP `/upgrades-downgrades` → **HTTP 429**. So a per-analyst track record is
**not obtainable at all on free data, for any asset class**, and these tables are correctly empty.

### 3.3 Provenance and reproducibility

| Table | Purpose |
|---|---|
| `source_run` | One row per fetch: `source_system`, `endpoint`, `http_status`, `rows_returned`, `error_text`, timings |
| `rule_version` | `rule_hash` (sha256) → `rule_text`. The rule JSON published in `harvest_signals.json` is hashed, so the stored version ties to the artefact readers actually see |
| `consensus_snapshot` | The 71 published consensus rows: counts, `share_buy_pct`, `consensus_score`, `consensus_label`, **`label_rule_version`**, `source_run_id` |
| `instrument` | Identifier crosswalk: `symbol`, `venue`, `figi`, `cusip`, `isin`, `instrument_type` |
| `price_bar` | OHLCV keyed `(instrument_id, d)` with its `source_run_id` |
| `pick_resolution` | One row per `(pick_id, horizon)` — replaces three competing outcome tables |

**Why `instrument` matters in practice:** SEC N-PORT identifies positions by **CUSIP**, and QQQ
carries a ticker on only **1 of 105** positions. Joining N-PORT on ticker silently returns zero
matches. A 1,621-entry CUSIP→ticker crosswalk had to be built from SSGA holdings files.

### 3.4 Fund look-through

| Table | Purpose |
|---|---|
| `fund_lookthrough` | Derived consensus per fund **with `weight_coverage_pct` mandatory**, plus `status` enum: `DERIVED_OK` / `NOT_APPLICABLE_BOND_FUND` / `BLOCKED_WRONG_SERIES` / `BLOCKED` |

Measured 2026-11-24: SPY **60.07%** coverage → derived share-buy 77.35 · XLK **65.46%** → 77.44 ·
QQQ **54.98%** → 75.95 · JNK `NOT_APPLICABLE` (a bond fund holds no equities — 0% is the correct
answer, not a failure) · VTI `BLOCKED_WRONG_SERIES` · EEM `BLOCKED`.

> **Warning carried from the measurement:** the three derived values agreeing within 2.5 points is
> **not** evidence of anything. All three are large-cap funds over a large-cap universe, so they
> regress to the universe average by construction. The coverage share is the informative column.

### 3.5 Crowd layer

| Table | Purpose |
|---|---|
| `crowd_markets` | `venue`, `market_id`, implied probability, bid/ask/**spread**, volume, liquidity, OI, resolution |
| `crowd_mappings` | Layer A direct vs Layer B event; `mechanism TEXT NOT NULL` enforces "never publish a bare correlation"; `expected_sign`, `historical_beta` with CI |

**Measured:** Polymarket Gamma HTTP 200 / 100 markets · Kalshi public HTTP 200 / 200 markets ·
**direct per-symbol matches: ZERO of 300.** That zero is the finding. An early matcher produced four
false positives by matching ticker `DE` inside the Spanish word *de* in tennis titles — matching must
be case-sensitive uppercase tokens only. Crowd data is therefore a macro/event layer exclusively.

---

## 4. Scoring rules (frozen before results existed)

```
entry   = open of the first trading day STRICTLY AFTER published_at   (lag-1, never same close)
raw     = last_close / entry_open - 1
net     = raw * 10000 - cost_bps                                       (round turn, per row)
excess  = net - benchmark_net                                          (same window, same rule)
CASH    = 4.32% annualised, pro-rated by calendar days  (the "bar" row)
BASKET  = equal-weight mean of members, entry-time weights
```

Every pick carries its own `cost_bps` and `benchmark`, so a number can never be read without its
assumptions.

---

## 5. Data review — actual state at first build

Verified against the live database, not asserted:

```
consensus_snapshot          71 rows  | re-derived from stored counts: 71 agree, 0 mismatch
                                     | snapshots missing label_rule_version: 0
                                     | distinct rule versions in use: 1
picktrack_marks              0 rows  | marks with no matching pick: 0
rule_version                 2 rows
source_run                   2 rows
picktrack_picks             31 rows  | 14 distinct asset classes
                                     | 9 strategy descriptors kept (not dropped)
                                     | picks with no cost basis: 0
```

Picks by source: `class_top` 12 (5 open / 7 unscored) · `harvest` 5 · `kilo` 5 · `buffy` 4 ·
`zoo` 3 (all unscored descriptors) · `bar` 1 · `copilot` 1.

**Live marks (2026-11-24):** AUDJPY −12.7 bp net (excess −12.7) · ENJ −121.2 bp net but **+185.4 bp
versus BTC**. US equities are `pending_entry` — the last bar is 2026-11-23 and the picks were
published 2026-11-24, so no session has traded since.

**Honest gaps, stated rather than hidden:** `analyst_registry`, `analyst_actions`,
`fund_lookthrough`, `crowd_markets`, `crowd_mappings`, `price_bar`, `pick_resolution` are all at
0 rows. The sources are reachable; the ingestion is not written yet. None of these is presented as
populated.

---

## 6. What is deliberately NOT in this database

- **No credentials.** Not in SQL, not in scripts, not in docs.
- **No invented analyst names.** The column exists and is NULL because the data does not exist.
- **No fabricated prices.** A symbol with no bar is `pending_entry`, never a zero return.
- **No verdict below n=30.** `INSUFFICIENT_N` is the default and the honest answer.
- **No touching production tables.** `picks_now_tracker` (5,172 rows), `trading_picks` (151,819),
  `stock_picks` (7,239) were left exactly as found; this schema is namespaced `picktrack_` because a
  `picks` table already existed with a different meaning (strategy/TP/SL, no provenance).

---

## 7. Reproducing the build

All scripts live in this directory and read the password from the environment at runtime.

| Script | Does |
|---|---|
| `db_init_picks.py` | v1: core tracking tables + view, loads `pick_ledger.jsonl` |
| `db_schema_v2.py` | v2: analyst, fund look-through, crowd tables |
| `db_schema_v3.py` | v3: `source_run`, `rule_version`, `instrument`, `consensus_snapshot`, `price_bar`, `pick_resolution` |
| `db_backfill_consensus.py` | Loads the 71 consensus snapshots with the published rule hash attached |
| `db_review.py` | Integrity review — the numbers in §5 |
| `score_picks.py` | Scores the ledger → `scorecard.json`, `SCORECARD.md` |

Every script is idempotent (`IF NOT EXISTS`, `INSERT IGNORE`, `ON DUPLICATE KEY UPDATE`).

---

## 8. Changelog

| Ver | Change | Trigger |
|---|---|---|
| v1 | Core tracking, 5 tables + view, 19 picks seeded | initial build |
| v2 | analyst, fund look-through, crowd | agent feedback on missing layers |
| v3 | `source_run`, `rule_version`, `instrument`, `consensus_snapshot`, `price_bar`, `pick_resolution` | ghcopilot design review: auditability, label reproducibility, CUSIP joins |
| v3.1 | 71 consensus snapshots backfilled, 71/71 labels reproducible | first data load |

---

## 9. Open decisions

1. **Named analyst track record** needs a paid feed (Finnhub premium, Benzinga, TipRanks, StarMine)
   *and* a redistribution decision, because this is a public Pages site. Nothing is built until that
   call is made.
2. **Ingest the three look-through funds** that ghcopilot already computed offline.
3. **Persist `price_bar`** so scoring stops depending on a live yfinance call.
4. **Crowd ingestion** — venues answer; the event→asset mapping needs an owner, and every row must
   carry a mechanism.
5. **Top-trader reverse engineering** — only disclosed positions exist (13F quarterly, Form 4, COT
   aggregate, on-chain). Four snapshots a year is hypothesis generation, not an edge.
