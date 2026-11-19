# Evidence index

Every quantitative claim in this review maps to a measured source. (Paths relative to
`eltonaguiar/findtorontoevents_antigravity.ca` unless stated.)

| Claim | Source |
|---|---|
| audit3 ledger verdicts (0 PROVEN, 1 CANDIDATE, 10 KILL, coverage 21.4%) | `audit_dashboard/data/audit3_ledger.json` (generated 2026-11-19T06:11Z) — summary/coverage/classes/kill_tribunal/cells |
| Candidate cell `luxalgo_confluence SHORT` (n=476, WR 54.4%, PF 1.61, net +0.72%, CI>0, single source 97.7%) | `audit3_ledger.json` → `cells` (verdict=CANDIDATE) |
| Kill criteria + sample kills | `audit3_ledger.json` → `kill_tribunal` |
| `/audit` live, `/audit2` 404, `/audit3` live | live probe 2026-11-19: HTTP 200/404/200 (sizes 1,437,176/992/36,331) |
| `audit_page.html` stale/orphan (2 tabs, May 25) | repo file + `AUDIT_PAGE_SECTIONS_2026-11-18.md` |
| Hypothesis registry 99 entries, 28 status spellings | `reports/hypothesis_registry.json`; prior review `AUDIT3_FEEDBACK_2026-11-19.md` §2.4 |
| Schema: 409 tables, 110 empty, bt_backtest_trades 32.7M + 27M mirror, per-DB users, credential leak | `docs/FINANCE_DB_SCHEMA_SPEC.md`; prior review §5 |
| Ghost rows 22,947; pnl sign/magnitude mismatches; open bloat | `audit_dashboard/data/db_health.json`; `corrections.md` (data_quality.baseline_2026_05_31) |
| Resolver anomalies (3,467 expired-zero-PnL etc.) | `audit3_ledger.json` → `coverage.resolver_anomalies` |
| Honesty layer / CRYPTO banner inflation (raw WR 33% vs 78–88%) | `audit_honesty_layer` memory; `audit_surface_truth_banner.js` |
| mega_mutation contradiction (PF 8.32/84% vs INSUFFICIENT_N) | `TRUE_PROFITABILITY_VALIDATED.md` (2026-11-14) vs `audit3_ledger.json` cells |
| Breakout family ≈364 trades net +0.46%/trade | prior review `AUDIT3_FEEDBACK_2026-11-19.md` §3.1 |
| Investment hub asset classes present (stocks/mutual/crypto/forex/goldmines/multi-asset/graveyard) | `TORONTOEVENTS_ANTIGRAVITY/index.html` grep hits; `audit3_ledger.json` classes |
| Staleness (hyro 157h, bt_backtest_runs frozen Mar, portfolio_snapshots frozen) | memory `audit_live_data_file_freshness_nov`; schema spec |
| Framework structure followed (charter/evidence-index) | `eltonaguiar/AGENT_FOLDERFRAMEWORK` folderframework-v4 (README, 00_CHARTER.md) |
| audit3 agent lineage (PRs #884–905) | `git log --all --grep=audit3`; PR merge commits (b5956d5…087acd4) |
| audit2 has no page (404), only helper scripts | live probe `/audit2` = 404; `git log --name-only` for audit2 → only `score_audit2.py`, `tmp/check_audit2.py`, `tmp/db_audit2.py` |
| Surface review (denominator disagreement, OOS Sharpe, measured slippage) | `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` (PR #891, commit 0a23cea6) |
| v3.1 feedback rewrite (39.5 KB) | `AUDIT3_FEEDBACK_2026-11-19.md` on branch `docs-audit3-feedback-v3` (PR #903, OPEN/unmerged) |
| Measured slippage: ETF 234% of PnL; FUTURES/COMMODITY flat < measured | `dashboard_data.json.slippage_validation`; v3.1 §1.5 |
| Walk-forward OOS Sharpe: EQUITY +0.608 (33f), CRYPTO −2.077 (32f) | `/audit` walk-forward panel; surface-review §3.2 |
| Smart-picks tile contradiction; dead tier2-proven panel | v3.1 §2; surface-review §4 |
