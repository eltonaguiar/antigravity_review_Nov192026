# NEXT_STEPS — consolidated action plan (2026-11-19)

Canonical, prioritized todo list derived from the converged review. Ordering is
by decision impact (P0 = changes what you believe, P1 = measurement depth, P2 =
research execution). Each item names the file to touch and the acceptance
criterion. Implementation happens in the **source repo**
(`eltonaguiar/findtorontoevents_antigravity.ca`), not here.

## P0 — correctness (do before any new strategy)

| # | Task | Files | Done when |
|---|---|---|---|
| P0-1 | Fix crypto stop-fill overshoot — resolve stops against intrabar OHLCV (fill at stop on breach, at close on gap) | `audit_trail/universal_pick_resolver.py`, `audit_trail/stop_fill.py` | crypto PF 0.768 → ≈1.00; overshoot +1.071pp/trade eliminated |
| P0-2 | Wire retired-strategy blocklist to emission (165 bypasses, incl `forex_rsi2_mean_reversion`) | `alpha_engine/strategy_blocklist.py` + scanner emit path | `blocklist_bypass.count == 0` on next `cohort_reconciliation.json` |
| P0-3 | Stamp at-issue gate inputs on 100% of rows (today 6%) | pick writer (`audit_trail/pick_schema.py`) | `at_issue_*` present on all rows; PIT replay shows no gate discrimination |
| P0-4 | Make selection alpha a **gate** (G8), not a display column | `alpha_engine/audit3_tribunal.py` (verdict logic ~775-785) | a beta-only "profitable" cell cannot reach PROVEN_T2 |
| P0-5 | DSR `n_trials` = global N (658), not tested cells (45) | `alpha_engine/audit3_tribunal.py:25,254-288` | global trial counter fed into `deflated_sharpe` |

## P1 — measurement depth

| # | Task | Files | Done when |
|---|---|---|---|
| P1-1 | Independent denylist-staleness watchdog (separate cron, fires even if `audit3-ledger` dies) | new workflow or `db-freshness-guardian.yml` + `tools/audit3_denylist_health.py` | stale (>14d) denylist is a loud CI failure, not silent |
| P1-2 | Full-book reconciled ledger + excluded-cohort panel | `alpha_engine/resolved_closed_view.py`, `audit3.html` | second ledger scores all resolvable rows, integrity-tagged |
| P1-3 | Power-based `required_n` per cell | `audit3_tribunal.py` + `audit3_edge_hunt.py:161 required_n()` | per-cell MDE/`required_n` replaces the flat n≥100 |
| P1-4 | Forward-observation clock + shadow emission for every cell (incl KILL) | `alpha_engine/forward_observations.py` (built, 0 rows) + MySQL adapter | `forward_observations.jsonl` accrues rows; KILL cells keep shadow legs |
| P1-5 | Promote 2×-cost stress from report-only to a hard gate | `audit3_tribunal.py:715` | `stress_2x_ok` required for PROVEN_T2/CANDIDATE |

## P2 — research execution

| # | Task | Files | Done when |
|---|---|---|---|
| P2-1 | Backfill FX prices or retire forex (E11) | `audit_trail/fetch_stock_prices.py` + `fx_prices` mapping | ≥90% FX coverage, or forex declared unmeasurable and stop emitting |
| P2-2 | Pre-register `POD-EQUITY-BREAKOUT` + start hold-benchmark pilot (E12) | `reports/audit3_confirmatory.json` (pod exists, no forward clock) | pod accrues forward rows under a 90-day clock; alpha-CI > 0 required to size |
| P2-3 | Resolve audit2: fold into audit3 "Method & Limits" or deploy `06_AUDIT2_PAGE/` prototype | deploy manifest + `audit3.html` | `/audit2` no longer 404; no second surface contradicting audit3 |
| P2-4 | Choose ONE premium pod: TSMOM (E8) **or** cross-sectional crypto (E3) | new `alpha_engine/` module + pod registration | one pod pre-registered, untouched holdout, kill criterion written |

## Decision rule (immutable)

At day 90 of the forward clock, if no pod shows a **positive net-CI lower bound at
2× measured slippage** and **IR ≥ 0.5 vs SPY**, the finding is **"no deployable
edge on available data"** — a citable result. Freeze (do not delete) the harness
and keep the capital in a ≤0.20%-fee beta core.

*Not investment advice.*
