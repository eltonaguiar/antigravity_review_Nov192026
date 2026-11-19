# Inventory — Data stores & key tables

Based on `docs/FINANCE_DB_SCHEMA_SPEC.md`, `schema-baseline.sql`, `schema-baseline.sql`
(256 KB), `audit_trail.db` (23 MB SQLite), and the audit payloads.

## MySQL (`stocks` + per-DB users)

- **409 tables in `stocks`**; **110 are empty** (inflate agent search space).
- **`bt_backtest_trades` ~32.7M rows**, with a **~27M-row duplicate mirror in `stocks`**.
- **`at_local_picks` ~76M rows**.
- **`bt_backtest_runs` stale since 2026-03-06** (backtest run metadata frozen).
- **Memecoin / sportsbet pipelines dormant since ~May 2026**.
- **`portfolio_snapshots` frozen March; `consensus_tracked` frozen April.**
- 414-table backup DB **never restore-tested**.
- **Cross-DB joins are impossible** — each DB has its own user (no shared grants).
- The spec leaks host `mysql.50webs.com`, the `ejaguiar1_<db>` naming map, and the
  credential-resolution path (`tools/db_env.py` + `~/dbpasses.txt`). **Redact before any
  web paste** (it was explicitly proposed to be pasted into a web AI).

## Three overlapping pick/outcome ledgers

| Ledger | Notes |
|---|---|
| `trading_picks` | main pick table; open bloat 92,985 vs info_schema_estimate 46,150 |
| `at_pick_outcomes` | outcomes ledger |
| `at_signal_outcomes` | carries intrabar fields — best candidate for canonical system of record |

No system of record is declared; `_is_valid_resolved_pick` filters are sprinkled across
the code instead of being enforced in one place.

## Coverage (the honest denominator)

`audit3_ledger.json` coverage block:

- `total_closed_picks = 16,330`; `valid_closed_picks = 7,901`; `scored_rows = 3,500`.
- **`scored_share_of_total_pct = 21.43`** · `scored_share_of_valid_pct = 44.3`.
- `unscored_rows = 12,830`.
- Resolver anomalies scanned 25,430 rows: `stale_exit_beyond_planned_stop = 44`,
  `clamped_loss_rows = 23`, `expired_zero_pnl_rows = 3,467`,
  `closed_rows_missing_closed_at = 3`.
- Window: first closed 2026-02-21, last closed 2026-11-19 (recent-biased window).

## Gaps that block measurement

- **No `forward_observations` table** → `PROVEN` can never be minted from live data.
- `bt_backtest_trades` is not pre-aggregated; the tribunal's evidence re-scoring and the
  "66,764 trades, only 11 retestable" gap in `audit3_evidence.json` are downstream of this.
- Selection alpha (`alpha_engine/audit3_selection_alpha.py`) is marked `available = False`
  (needs the price tables).
- Staleness budgets are assertions, not enforced (docs decay; assertions don't).
