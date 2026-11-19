# Findings — Data quality & resolver artifacts

## Ghost rows

- `db_health.json` reports **`total_ghost_rows = 22,947`** across 10 cohorts; top cohorts:
  MEMECOIN / meta_strategy / DOGEUSDT LONG (n=3,569 with pnl 1.3226; n=3,160 with pnl 5.0).
- The dashboard/template hardcodes **0 / GREEN** for ghost rows. This is a three-way
  contradiction (stale baseline 2026-05-31 vs live 22,947) that must be resolved at the
  data layer before trusting any ghost-row indicator.

## Resolver & PnL artifacts (from `db_health.json`)

| Check | Result |
|---|---|
| `pnl_integrity` | sampled 24,158 rows: sign_mismatch 130 (0.54%); naive_magnitude_mismatch 6,535 (27.05%) |
| `won_pnl_contradiction` | TP_HIT n=7,026 avg +3.41 (0 negative); SL_HIT n=3,873 avg −3.20; LOST n=5,598 avg −1.76 |
| `status_standardization` | 0 non-canonical |
| `open_bloat` | trading_picks open_count 92,985 vs info_schema_estimate 46,150; active_count 21; bt_backtest_trades open 29,247,197 / total 32,441,049 |
| Resolver anomalies (audit3) | expired_zero_pnl_rows 3,467; stale_exit_beyond_planned_stop 44; clamped_loss_rows 23 |

## Honesty layer

- Dashboard banners show **CRYPTO PF 9–18 / WR 78–88%** surfaces that are inflated by
  `claude_gainer_st` picks with **`EXPIRED → WON` resolver mislabels (raw WR 33%)**.
- The honesty layer redirects to `pf_registry` policy-clean-net (PF 0.98 / WR 39.7%) and
  `money_ready_verdict` (PF 0.…).

## Staleness

- `hyro_pick_performance.json` generated 2026-11-08 (~157 h stale at 2026-11-14 check).
- `hyrotrader_picks.json` has no timestamp field.
- `pick_funnel_snapshot.json` returns 404/HTML not JSON.
- `bt_backtest_runs` frozen since 2026-03-06.
- `portfolio_snapshots` frozen March; `consensus_tracked` frozen April.
- `audit_page.html` is a stale (May 25) orphan that references `data/grok_top_picks.json`.

## Other

- `audit3_ledger.json` `source` leaks a `/tmp` path; provenance should embed commit SHA +
  input file SHA-256 + generator version (the evidence records are hashed; the ledger is
  not).
- Hard-coded slippage constants (CRYPTO 0.15%, EQUITY 0.10%, FOREX 0.05%) are optimistic;
  the Q25 (2× costs) gate is unenforced in places. audit3 now reports a 2× stress column
  (report-only).
