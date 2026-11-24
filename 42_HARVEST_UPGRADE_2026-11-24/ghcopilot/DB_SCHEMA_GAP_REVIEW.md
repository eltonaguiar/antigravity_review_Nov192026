# Picktracking schema — gap review against my proposal

**Audited:** 2026-11-24 · **Database:** `ejaguiar1_stocks` (MySQL 8.4.7, `mysql.50webs.com`)
**Method:** live `information_schema` introspection (`db_schema_audit.py`), not the design document.
Reason: `DATABASE_SCHEMA.md` is authored by the same agent that wrote the DDL, so it cannot falsify it.

---

## 0. Measured inventory

21 tables present, 0 missing from the declared list. Row counts as measured:

| table | rows | | table | rows |
|---|---|---|---|---|
| `picktrack_picks` | **3,992** | | `source_run` | **3** |
| `picktrack_entries` | 3,882 | | `rule_version` | 2 |
| `picktrack_marks` | 494 | | `instrument` | **0** |
| `picktrack_scores` | **0** | | `consensus_snapshot` | 71 |
| `picktrack_events` | 8 | | `price_bar` | **0** |
| `pick_resolution` | **0** | | `trader` | **0** |
| `analyst_registry` | **0** | | `trader_action` | **0** |
| `analyst_actions` | **0** | | `trader_rating` | **0** |
| `fund_lookthrough` | 6 | | `risk_profile` | **0** |
| `crowd_markets` | 500 | | `pick_type_ref` | 6 |
| `crowd_mappings` | **0** | | | |

11 of 21 tables declare **no foreign key at all**. Views: 7 exist, of which 4 are
tracker-specific (`v_picktrack_latest`, `v_analyst_symbol_history`,
`v_trader_symbol_history`, `v_trader_symbol_stats`); the other 3
(`vw_all_enhancements`, `vw_all_incidents`, `vw_picks_now_dedup`) are pre-existing
repo views, not tracker objects.

`picktrack_picks.status` distribution: `open` 3,982 · `unscored` 10. **Zero resolved.**

---

## 1. My proposed objects/columns that are absent, and the consequence of each

**(a) `source_system` dimension table — absent.**
No table by that name exists; the only occurrence is the `varchar(48)` column on
`source_run`. Consequence: source-level attributes have nowhere to live — asset-class
scope, free/paid, licence, robots/ToS status, rate-limit window. This is why my
`REASON_CODES` (`ACCESS_DENIED_403`, `RATE_LIMITED_429`, `NO_COVERAGE_VENDOR`,
`SYMBOL_UNMAPPED`, …) exist only in Python (`kilocode/harvest_rules.py`) and cannot be
queried, joined, or counted from the database.

**(b) `source_run_id` on `picktrack_picks` — absent.**
Provenance reaches `consensus_snapshot` and `price_bar` only. Consequence: the 3,992
picks cannot be traced to the fetch that produced them. `source_run` id=3 records
`audit_dashboard / http_status 200 / rows_returned 4210` on 2026-11-24 11:27:17 — which
is almost certainly the run that inserted these picks — but no row can prove it. A bad
fetch therefore cannot be retracted as a batch.

**(c) `source_run_id` on `fund_lookthrough` — absent.**
It carries `source_file varchar(255)` free text instead. Consequence: my
`BLOCKED_WRONG_SERIES` (VTI) and `BLOCKED` (EEM) rows cannot be joined to the HTTP
status that caused them, so "why is this fund blocked" is unanswerable from the DB.

**(d) `instrument_id` on `picktrack_picks` — absent, and `instrument` has 0 rows.**
`consensus_snapshot.instrument_id` is a nullable FK into an empty table — the target is
a ghost. Consequence: symbol identity is free text in five differently-sized columns
(`symbol varchar(24)`, `symbol_raw varchar(32)`, `asset_symbol varchar(24)`,
`instrument.symbol varchar(32)`, `trader_action.symbol varchar(32)`). `BTCUSDT`,
`BTC-USD` and `BTCUSD` are three instruments. This is the same class of failure I
measured on N-PORT, where a naive ticker join matched 1 of 105 positions.

**(e) `asset_class` normalisation — absent, and the values are already fractured.**
16 raw values: `CRYPTO` 3,504 · `FOREX` 184 · `EQUITY` 160 · `ETF` 41 · `COMMODITY` 38 ·
`BOND` 34 · `FUTURES` 12 · **`STOCK` 11** · `SPORTS` 1 · `CASH` 1 · `BASKET` 1 ·
`FX_CARRY` 1 · `MUTUAL_FUND` 1 · `OPTIONS` 1 · `PREDICTION_MARKET` 1 · `PRIVATE_CREDIT` 1.
`EQUITY` and `STOCK` are the same class split in two; `ETF`/`BASKET` and
`FOREX`/`FX_CARRY` likewise. Consequence: every per-class verdict inherits a fragmented
denominator, and 8 classes sit at n=1 and will report `INSUFFICIENT_N` forever while
still occupying a row in any class report.

**(f) `asset_class` on `picktrack_scores` — absent.**
Columns are `as_of, source, n_picks, mean_net_bps, median_net_bps, mean_excess_bps,
beat_benchmark, n_with_bench, verdict`. Consequence: the scorecard can only be
source-level. It structurally cannot produce the repo's north-star metric — a Tier-1/
Tier-2 verdict *per asset class*.

**(g) `dsr` / `trials_screened` on `picktrack_scores` — absent.**
`trader_rating` has both (`dsr`, `trials_screened`, `bh_significant`); the pick-level
scorecard has neither. Consequence: the pick scorecard has no multiple-testing
correction, so it will reproduce the false-Tier-1 failure already on record (2 false
Tier-1 PASSes 2026-05-17, per `CLAUDE.md`: the concentration gate is not enforced
before DSR/SPA).

**(h) `benchmark_net_bps` / `excess_bps` computed on marks — columns exist, 494/494 NULL.**
Not a schema gap but the most consequential data gap: all 494 marks have
`excess_bps IS NULL`, while all 494 of their parent picks *do* have a `benchmark`
populated. So this is an unimplemented calculation, not missing data. Consequence:
`picktrack_scores.mean_excess_bps`, `beat_benchmark` and `n_with_bench` can never fill.
The one question the repo actually cares about — *did it beat buy-and-hold* — is
unanswerable from the schema even for the 494 picks that have been marked.

**(i) `price_bar` populated — 0 rows.**
PK `(instrument_id, d)`, and `instrument` is also empty, so this is a closed loop of
nothing. Consequence, measured today: marks store `last_price` with no provenance, so
re-deriving the return requires re-hitting the vendor. My own Monte Carlo re-fetch from
Tiingo returned HTTP 429 twice and the earlier backtest vector had not been persisted —
the test became unreproducible. Had `price_bar` been populated, the permutation test
would have been a local re-derivation with no network call.

**(j) `crowd_mappings` populated — 0 rows.**
Consequence: the layer-A/layer-B match has nowhere to live, so my measured result
("layer A matched 0 of 300 markets; the earlier 4 matches were all false positives from
the ticker `DE` inside Spanish prepositions") cannot be stored, versioned, or re-checked.

**(k) FK from `pick_resolution` → `picktrack_picks` — absent.**
`pick_resolution` has `pick_id varchar(80)` and no constraint; so do
`picktrack_scores` and `picktrack_events`. Consequence: the outcome table can hold an
outcome for a pick that does not exist, and deleting a pick silently orphans its
outcome. Note the asymmetry: FK discipline *was* applied to `picktrack_entries` and
`picktrack_marks` — the two tables easiest to populate — and withheld from the outcome
and scoring tables.

**Not a gap, recorded for accuracy:** `analyst_registry` and `analyst_actions` at 0 rows
is exactly what my own spec predicted — `ANALYST_SCORECARD_SPEC.md` line 103 states the
only computable scorecard today is consensus-level, not analyst-level, and per-analyst
scoring is blocked on a licensed event feed. `analyst_name` staying NULL rather than
guessed is correct. The only residue: `analyst_registry` has no licence/feed column, so
when a paid feed arrives there is nowhere to record which licence produced a name.

---

## 2. Was collapsing `source_system` + `source_run` into one table with a string mistake?

**Yes — but the damage is in a different place than the question assumes.**

`source_run` as a fact table of fetches is right, and the columns are right
(`source_system, endpoint, http_status, rows_returned, error_text, started_at,
finished_at`). Referential integrity is not the active injury either: `source` is clean
today — 8 distinct values, no case or whitespace anomalies, 99.2% in `audit`. The drift
this FK would have prevented has not happened yet.

**The real damage is that the dimension concept got split across two columns and neither
is usable as a key.**
- `picktrack_picks.source` = 8 values, 99.2% `'audit'` — near-constant, so
  `GROUP BY source` on the scorecard yields one row covering 3,961 of 3,992 picks.
- `picktrack_picks.source_detail` = **86 distinct values** — this is where the actual
  system identity lives (`inverse_mutations` 2,399 · `signal_validation` 398 ·
  `kimi_signal_tracking` 152 · …), in a `varchar(512)` free-text column with no index
  and no reference target.

So the column that is dimensioned is a constant, and the column that carries identity is
unreferenceable text. Per-system verdicts therefore require string parsing in Python —
which is precisely what I had to do today, grouping 4,287 `active_raw` rows across 76
systems out of `dashboard_data.json` instead of querying it. `source_system` on
`source_run` is a third vocabulary, `varchar(48)`, populated with vendor names
(`finnhub`, `audit_dashboard`) rather than system names — so it does not even join to
`picktrack_picks.source` semantically.

**What specifically breaks:**
1. `picktrack_scores` cannot aggregate at the system level that matters without parsing `source_detail`.
2. No source attributes can be stored (asset-class scope, licence, rate-limit window), so coverage claims on the HARVEST page have no DB backing.
3. `source_run` is orphaned: 3 rows, and **nothing references it by FK**. Provenance exists as a table and is disconnected from the 3,992 facts it should explain.
4. The three `source*` columns (`varchar(32)`, `varchar(512)`, `varchar(48)`) are cross-width and cross-meaning, so no join between picks, runs and vendors is well-defined.

**What proves the pattern was available and skipped:** `rule_version` is a correct
dimension — `char(64)` hash PK, real `description`, and a genuine FK from
`consensus_snapshot.label_rule_version`. The discipline was applied to rules and not to
sources.

---

## 3. Does `pick_resolution` + `picktrack_marks` repeat the three-competing-outcome-tables mistake?

**No.** The roles are genuinely distinct, and I checked the columns rather than the names:

- `picktrack_marks` = `id, pick_id, mark_date, last_price, raw_pct, net_bps,
  benchmark_net_bps, excess_bps, days_held`. **No outcome, status, won, or result
  column.** It is a valuation at time *t* — an observation, not a verdict.
- `pick_resolution` = `outcome, exit_reason, pnl_bps, bench_pnl_bps, horizon` — the
  terminal verdict, one row per (pick, horizon).
- `picktrack_picks.status` = lifecycle only (`open` 3,982 / `unscored` 10; **0 resolved**),
  not a verdict.

Two facts about the original failure that are absent here: that failure had three tables
each claiming to hold *the* outcome, and the labels diverged. Here there is exactly one
outcome column in the entire schema (`pick_resolution.outcome`). Mark vs resolution vs
lifecycle is the correct 3-way split.

**The condition it fails:** no arithmetic link between the terminal mark and the
resolution. Nothing enforces `pick_resolution.pnl_bps` = the final `mark.net_bps` for the
same pick and horizon, and nothing marks earlier marks as non-authoritative once a
resolution exists. That is harmless *today* only because `pick_resolution` is empty — the
divergence has no place to form. The moment resolution starts writing, two numbers will
exist for the same pick with no reconciliation, which is the same shape as the defect
already on record (EXPIRED→WON mislabels; 1,864 duplicate signal-ts groups). So: the
design mistake was not repeated; **the guard against it was not built.**

Secondary note: 494 marks across 494 distinct picks = 1 mark each. The table's own
justification — a time series — is not yet exercised, so marks are currently snapshots.

---

## 4. The one fix I would make first

**Populate `pick_resolution` and make it the single authoritative outcome, deriving it
from the 494 existing marks, carrying `bench_pnl_bps` — and add the reconciliation
constraint in the same migration.**

Why this one: everything downstream of it is zero. `picktrack_scores` 0 rows (needs
resolutions), `analyst_registry` 0 (needs resolved outcomes to compute `hit_rate`),
`trader_rating` 0. The database currently cannot answer its founding question — *what
would have happened if we had taken that?* — for even one of 3,992 picks. Provenance is
hygiene; an empty resolution path is a total functional gap, and no amount of FK work
fixes it.

Why it is cheap and correct: 494 marks already carry non-null `net_bps` (0 nulls), so the
outcome for 494 picks is already computed and merely unwritten. Forcing
`bench_pnl_bps` into the same migration also forces the currently-NULL `excess_bps`
calculation, which is what makes the mark set meaningful at all.

Guard to include, so this does not become the divergence it is meant to prevent:
`UNIQUE (pick_id, horizon)` on `pick_resolution`, an FK to `picktrack_picks.id`, and a
view or check asserting `pick_resolution.pnl_bps = MAX(mark.net_bps)` per (pick, horizon).

Cheap rider, if a second change is allowed in the same PR: `picktrack_picks.source_run_id
BIGINT NULL` plus the FK — one nullable column, no data migration, and it converts
`source_run` from an orphan into the provenance record the design claims.
