# Fresh Tracking & Integrity Evidence (2026-11-19)

Companion tables to `00_INDEPENDENT_REVIEW.md`. All paths relative to
`eltonaguiar/findtorontoevents_antigravity.ca` unless stated.

## A. Class verdicts (audit3 ledger, `audit_dashboard/data/audit3_ledger.json` → `classes`)

| Asset class | Verdict | n | WR | PF | Net expectancy/trade | Net 95% CI | DSR |
|---|---|---|---|---|---|---|---|
| CRYPTO | KILL | 1,851 | 40.2% | 0.75 | −0.463% | [−0.642, −0.295] | 0.000 |
| EQUITY | WEAK | 761 | 45.9% | 1.08 | +0.167% | [−0.229, +0.570] | 0.277 |
| ETF | WEAK | 584 | 43.2% | 1.00 | +0.005% | [−0.234, +0.231] | 0.090 |
| FOREX | WEAK | 211 | 35.1% | 0.75 | −0.093% | [−0.222, +0.038] | 0.003 |
| COMMODITY | KILL | 55 | 14.6% | 0.12 | −3.200% | [−4.611, −2.090] | 0.000 |
| BOND | WEAK | 34 | 38.2% | 0.55 | −0.247% | [−0.529, +0.071] | 0.003 |
| FUTURES | INSUFFICIENT_N | 4 | 50% | 1.87 | +1.285% | [−2.948, +5.519] | — |

Kill tribunal: 23 kills total — 11 symbols, 2 classes (CRYPTO, COMMODITY), 10
strategy cells. Every kill ships a mutation instruction (invert/filter/second
source/retire).

## B. Walk-forward verdicts — `alpha_engine/data/walkforward_results.json` (2026-11-19)

52 strategies scored: **0 ELITE / 3 STRONG / 11 VIABLE / 3 MARGINAL / 35 FAILING.**
This is the freshest machine-generated current-status artifact in the repo, yet
none of the 6+ "current strategy" registries reference it.

## C. Per-class performance — `audit_dashboard/data/strategy_perf_by_class.json` (2026-11-18)

961 cells across 11 classes. Selected evidence (`avg_pnl_pct` = mean PnL/trade):

| Cell | Class | n | avg_pnl_pct | WR | PF |
|---|---|---|---|---|---|
| `ml_enhanced_ARBUSDT` | CRYPTO | 6 | +66.18% | 83.3% | 199.5 |
| `crypto_keltner_compression_expansion_v1` | CRYPTO | 23 | +20.78% | 73.9% | 3.79 |
| `forex_carry_momentum` | FOREX | 154 | +5.03% | 7.8% | 9.87 |
| `luxalgo_confluence` | CRYPTO | 5,505 | +0.18% | 47.7% | 1.21 |
| `unknown` | CRYPTO | 4,415 | −0.30% | 28.8% | — |
| `forex_rsi2_mean_reversion` | FOREX | 1,095 | −0.12% | — | — |
| `futures_momentum` | COMMODITY | 681 | −0.72% | — | — |
| `etf_sector_momentum` | EQUITY | 2 | −72.24% | — | — |
| `ml_enhanced_TRXUSDT_1d_B_lightgbm` | CRYPTO | 24 | −68.72% | — | — |

Pattern: high-n cells are near-zero or negative; eye-catching positives are almost
all n<30 (small-sample noise) or WR<10% with a single fat tail (carry). No cell
in this table is edge-proven by the audit3 gates.

## D. Declared-but-absent files (integrity gaps)

| Path | Expected | Reality |
|---|---|---|
| `audit_dashboard/data/dashboard_data.json` | canonical audit payload | **absent**; audit3 source is `/tmp/audit3/dashboard_data.json`; only stale copies elsewhere |
| `audit_trail/data/universal_resolved_picks.json` | resolver output (capped 5,000) | **absent** from disk |
| `trading/data/strategy_registry.json` | written by `trading/strategy_registry.py` | **absent** (declared, never materialized) |
| `paper_trading/data/paper.db` (+ `equity_snapshots`) | SQLite equity curve | **never created**; no persisted equity time series |

Consequence: downstream readers of the canonical payload get `{}`, and paper
trading has no track record beyond a point-in-time `portfolios.json` snapshot
(~17 closed trades across 3 portfolios).

## E. Hypothesis registry fragmentation

- `reports/hypothesis_registry.json`: ~141 ids, ~138 status values across **30+
  distinct spellings** (`KILLED`, `TESTED_KILL`, `PAPER_PILOT`, `FORWARD_SHADOW`,
  `REFUTED`, `NULL`, …). Tail ≈ lines 2337–3897 is an archive append re-scoring
  duplicate ids (H-005, H-017, H-034, …) under a different vocabulary.
- `audit_trail/data/hypothesis_registry.json`: **empty stub** (`{"hypotheses":
  {}, "last_updated": ""}`).

Status counts are therefore not reliable as-is.

## F. Freshness kernel

- `audit_dashboard/data/db_freshness.json`: generated **2026-05-23** (≈6 months
  stale); overall RED; `signal_outcomes` last resolved 2026-03-04 (121 rows).
- `audit_dashboard/data/db_health.json` (2026-11-19): ghost rows 22,947 (red),
  open_bloat 94,119 open / 29.2M open backtest rows (red), pnl_integrity GREEN,
  won_pnl_contradiction GREEN.

## Evidence index

| Claim | Source |
|---|---|
| Class verdicts table | `audit_dashboard/data/audit3_ledger.json` → `classes` |
| Kill counts (23: 11 sym, 2 classes, 10 strategy) | ledger → `kill_tribunal` + `summary` |
| Walk-forward 0/3/11/3/35 | `alpha_engine/data/walkforward_results.json` |
| Per-class 961 cells table | `audit_dashboard/data/strategy_perf_by_class.json` |
| Missing `dashboard_data.json` / `universal_resolved_picks.json` / `strategy_registry.json` / `paper.db` | directory listings + `trading/strategy_registry.py` + `audit_trail/dashboard_generator.py` + `paper_trading/db.py` |
| Hypothesis registry fragmentation / empty stub | `reports/hypothesis_registry.json`; `audit_trail/data/hypothesis_registry.json` |
| Freshness kernel | `audit_dashboard/data/db_freshness.json`; `audit_dashboard/data/db_health.json` |
