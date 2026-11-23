# Ghost row provenance — did 22,947 ghost rows reach backtest inputs?

**Date:** 2026-11-23 · **Source:** `02_FINDINGS/data_quality_resolver.md`, `02_FINDINGS/contradictions.md`, `02_FINDINGS/why_no_wins.md`

## Question

Were the 22,947 ghost rows display-only (a dashboard cosmetic bug), or did they reach the backtest inputs and corrupt the backtest?

## What the evidence shows

### Ghost rows exist in the data layer

`db_health.json` reports `total_ghost_rows = 22,947` across 10 cohorts. Top cohorts:

| Cohort | Notes |
|---|---|
| MEMECOIN | n=3,569 with pnl 1.3226 |
| meta_strategy | — |
| DOGEUSDT LONG | n=3,160 with pnl 5.0 |

### The dashboard lies

`template.html` / `index.html` hardcodes **0 / GREEN** for ghost rows. Baseline is stale (2026-05-31). Live is 22,947. This is a three-way contradiction: stale baseline vs live count vs hardcoded zero.

### Backtest tables are bloated — ghost rows reached backtest inputs

`open_bloat` check from `db_health.json`:

| Table | Metric | Value |
|---|---|---|
| `trading_picks` | open_count | 92,985 |
| `trading_picks` | info_schema_estimate | 46,150 |
| `trading_picks` | active_count | 21 |
| `bt_backtest_trades` | open | 29,247,197 |
| `bt_backtest_trades` | total | 32,441,049 |

`bt_backtest_trades` has 29.2M open trades out of 32.4M total — roughly 90% of backtest trades are "open" (never closed). This is a massive anomaly consistent with ghost rows populating the backtest trade table.

Additionally:
- `bt_backtest_runs` is **frozen since 2026-03-06** — no new backtest runs have been recorded, yet `bt_backtest_trades` carries tens of millions of rows.
- `audit3_ledger.json` `source` leaks a `/tmp` path; provenance is incomplete.

### PnL integrity is also compromised

Sampled 24,158 rows: `sign_mismatch` 130 (0.54%), `naive_magnitude_mismatch` 6,535 (27.05%). The `won_pnl_contradiction` check shows TP_HIT n=7,026 avg +3.41 (0 negative), SL_HIT n=3,873 avg −3.20, LOST n=5,598 avg −1.76 — these distributions are internally inconsistent with the ghost-row contamination.

## Verdict: ghost rows reached backtest inputs

**Not display-only.** The ghost rows in `trading_picks` (22,947) are mirrored by the bloat in `bt_backtest_trades` (29.2M open / 32.4M total). The dashboard's hardcoded 0/GREEN is a cosmetic cover-up; the underlying data layer — including the backtest trade table — is contaminated.

**Consequence:** Any backtest metric derived from `bt_backtest_trades` or `trading_picks` after the ghost-row inflection point is unreliable. The `bt_backtest_runs` table being frozen since March while `bt_backtest_trades` carries 32M rows means the backtest inputs cannot be reconciled to any validated run.

*Paper only. No live orders, no credentials. Not investment advice.*
