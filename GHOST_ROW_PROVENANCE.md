# Ghost Row Provenance — 22,947 rows

**Question:** Were the 22,947 ghost rows a dashboard-only cosmetic, or did they reach the BACKTEST INPUTS?

**Answer:** They reached the backtest inputs. The ghost rows contaminated `bt_backtest_trades` and `trading_picks`, making any backtest metric derived from them after the inflection point unreliable.

## Evidence

| Source | Value | Reading |
|--------|-------|---------|
| `db_health.json` | `total_ghost_rows = 22,947` across 10 cohorts | Live count, not cosmetic |
| Dashboard / template.html / index.html | Hardcodes `0 / GREEN` | Stale 2026-05-31 baseline vs live 22,947 — three-way contradiction |
| `trading_picks` open_count | 92,985 | vs information-schema estimate of 46,150; active_count = 21 |
| `bt_backtest_trades` open | 29,247,197 | / total 32,441,049 |

## Top ghost-row cohorts

Per `db_health.json`, the largest cohorts are:
- MEMECOIN / meta_strategy / DOGEUSDT LONG — n=3,569 (pnl 1.3226) and n=3,160 (pnl 5.0)
- 10 cohorts total contribute the 22,947 ghost rows

## Loader and join trace

The ghost rows originate in the `trading_picks` table. The dashboard reads `db_health.json` (live: 22,947 ghost rows, `harness_healthy = false`) but the page template hardcodes `0 / GREEN`. The rows then flow into `bt_backtest_trades` (29.2M open rows vs ~32.4M total), meaning backtest trade inputs are contaminated: a pick that is a ghost row (no valid outcome, unresolved status, or resolver-mislabeled) still enters the backtest trade table and corrupts expectancy, win-rate, and profit-factor calculations.

**Bottom line:** the ghost rows are not a dashboard cosmetic. They are in the operational data pipeline, they reached the backtest inputs, and any metric computed from `trading_picks` or `bt_backtest_trades` after the ghost-row inflection point is unreliable. A null result computed on a contaminated trade table is not evidence about markets.

*Paper only. Zero capital. Not investment advice.*
