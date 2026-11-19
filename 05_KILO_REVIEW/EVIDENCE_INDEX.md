# Evidence Index — Antigravity Financial-Prediction Review

Claim → evidence. Every finding in `FINDINGS_ROOT_CAUSE.md` maps to a file path,
commit SHA, or live URL below.

## Commits referenced

| SHA | Message | Files |
|---|---|---|
| `a191e67e484` | feat(audit3): prove the ledger has no positive selection alpha | `alpha_engine/audit3_edge_hunt.py`, `alpha_engine/audit3_selection_alpha.py`, `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` |
| `bbe69ec48c3` | fix(audit3): test expectancy instead of win rate, stop leaking DB host | `updates/2026-11-19-audit3-v2-expectancy-gates.md`, `docs/FINANCE_DB_SCHEMA_SPEC.md` |
| `8ae88ae02d7` | fix(audit3): require proven harm before killing a cell | `updates/2026-11-19-audit3-innocent-until-proven-guilty.md` |
| `b5956d55e59` | feat(audit3): quant kill-tribunal ledger, page, job | `updates/2026-11-19-audit3-quant-kill-tribunal.md` |
| `0a23cea60f9` | docs: review /audit vs /audit3 | `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` |
| `ca35475d7e8` | docs: merge finance DB schema spec + edge backlog | `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md`, `docs/FINANCE_DB_SCHEMA_SPEC.md` |
| `010e64344ef` | docs: add ML systems health/staleness audit (#899) | `docs/ML_SYSTEMS_HEALTH_AUDIT_2026-11-19.md` |
| `8805152dbfe` | docs: record the arena.ai v3 P0 delta | `docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md` |
| `53bd7766a07` | fix(audit): wr means the class rows, measured cost, one smart-picks def | `docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md` |

## Finding → evidence

| Finding | Primary evidence |
|---|---|
| F1 no positive alpha | `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` §1,§3; `alpha_engine/audit3_edge_hunt.py`; `alpha_engine/audit3_selection_alpha.py` |
| F2 cost/exit problem | `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` §3.1,§6; `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §1 |
| F3 leaky walk-forward gate | `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` §2 |
| F4 fragmented tracking | `docs/FINANCE_DB_SCHEMA_SPEC.md` §1,§2; `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` §1,§2,§3.3,§4 |
| F5 orphaned A/B infra | `schema-baseline.sql` (tables `whatif_scenarios`, `ml_ab_tests`, `simulation_grid`, `strategy_whatif_results`); `strategy_variation_generator.py`; `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §4 E14 |
| F6 backtest-n vs realized-n | `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §14 |
| F7 contradictory audits | `docs/ML_SYSTEMS_HEALTH_AUDIT_2026-11-19.md` §1,§3 vs `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` §1 |

## Key numeric facts (all reproducible from live payload `2026-11-19T04:04:16Z`)

| Fact | Value | Source |
|---|---|---|
| Whole book net/trade | −0.188% (n=3,500) | edge-hunt §1 |
| CRYPTO LONG alpha vs hold | −0.442%/pick [−0.892, −0.085] | edge-hunt §3 |
| ETF LONG alpha vs hold | −0.272%/pick [−0.504, −0.037] | edge-hunt §3 |
| wf_verdict raw vs PIT | +0.964% vs −0.187%/trade | edge-hunt §2 |
| at-issue snapshots | 215/3,500 (6%) | edge-hunt §2 |
| Closed picks total / scored | 16,330 / 3,500 (21.4%) | surface-review §1 |
| integrity-excluded | 7,502 (46%) | surface-review §1 |
| ETF slippage % of PnL | 234% | surface-review §3.1 |
| EQUITY OOS Sharpe | +0.61 (33 folds) | surface-review §3.2 |
| CRYPTO OOS Sharpe | −2.08 (32 folds) | surface-review §3.2 |
| money-ready classes | 0 of 10 | money-ready §1 |
| DB tables (stocks) | 409 | finance-db-schema §2 |
| resolved picks WR / avg PnL | 41.7% / +0.085% (n=32,352) | ML-health §3.1 |
| fx_prices span | ends 2026-02-09 | edge-ideas §6 |
| backtest vs realized (wick reversal) | n=4,904 vs n=43 | edge-ideas §14 |

## Live URLs

- https://findtorontoevents.ca/audit
- https://findtorontoevents.ca/audit2
- https://findtorontoevents.ca/audit3
- https://findtorontoevents.ca/audit/hyrotrader
- https://findtorontoevents.ca/findstocks/
- https://findtorontoevents.ca/audit/funds.html

## Verification status

Findings F1–F7 are sourced from documents already merged to `main` at the commit
range above; schema/table claims were re-verified against the working tree's
`schema-baseline.sql` (322 `CREATE TABLE` statements) and
`docs/FINANCE_DB_SCHEMA_SPEC.md`. Live DB row counts are quoted from the repo's
own docs (information_schema pulls), not independently re-queried in this review.
