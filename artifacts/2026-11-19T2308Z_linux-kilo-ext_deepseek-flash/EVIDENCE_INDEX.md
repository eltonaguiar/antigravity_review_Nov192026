# EVIDENCE INDEX — 10_KILO_VANILLA_HANDSAW

Every claim in `FINDINGS_MEASURED.md` → exact source. All paths relative to
`findtorontoevents_antigravity.ca` @ `f9e6c8202a1` unless noted. Re-verified
2026-11-19.

## A. Reproducibility gap

| Claim | Source | Location / value |
|---|---|---|
| `dashboard_data.json` absent from worktree | `ls audit_dashboard/data/dashboard_data.json` | "No such file or directory" |
| not git-tracked | `git ls-files --error-unmatch audit_dashboard/data/dashboard_data.json` | "did not match any file(s) known to git" |
| `/audit` fetches it at runtime | `audit_dashboard/index.html` | L953 `fetch('data/dashboard_data.json?...')` |
| live copy = 3,500 records @ 2026-11-19T04:04:16Z | `audit_dashboard/data/cohort_reconciliation.json` | `inputs.dashboard_data.records=3500`, `generated_utc=2026-11-19T04:04:16.807952+00:00` |
| published surfaces disagree (ETF) | same file | `published_disagreement.checks`: ETF 14d dashboard_pf 1.0158483 vs summary_pf 0.345, `disagree=true` |
| published surfaces disagree (EQUITY) | same file | EQUITY 14d dashboard_pf 0.6575944 vs summary_pf 0.3, `disagree=true` |
| surfaces disagree even when coverage complete | same file | checks marked `coverage_status="complete"` still `disagree=true` |
| audit3 uses a different denominator | `audit_dashboard/data/audit3_ledger.json` | `coverage.denominator.mode="payload_slice"`, `loaded_from_sidecar=false`, `fallback_reason="no_canonical_block"`, note "NOT the same denominator as /audit" |
| audit3 scores 21.43% of closed picks | same | `coverage.scored_rows=3500`,`total_closed_picks=16330`,`scored_share_of_total_pct=21.43`,`valid_closed_picks=7901` (44.3%) |
| excluded cohorts | same | `coverage.excluded_cohorts`: `integrity_excluded n=7502`, `auto_expired n=9100` |
| audit3 verdict counts | same | `summary`: 45/171 cells, `n_proven=0`,`n_candidate=1`,`n_weak=34`,`n_kill=10`,`n_insufficient=126`,`kill_rate_pct=22.22`,`n_kill_symbols=11`,`n_kill_classes=2` |
| CRYPTO verdict = KILL | same | `classes[0]`: n=1851, wr=0.4019 CI[0.3798,0.4245], pf=0.7474, net=−0.4632 CI[−0.6416,−0.2947], dsr=0.0, split-half unstable, p_value=1.0 |
| resolver anomalies | same | `coverage.resolver_anomalies`: `expired_zero_pnl_rows=3467`,`stale_exit_beyond_planned_stop=44`,`clamped_loss_rows=23`,`closed_rows_missing_closed_at=3`,`rows_scanned=25430` |

## B. Ghost rows / open bloat

| Claim | Source | Location / value |
|---|---|---|
| 5 checks, 3 pass, 2 fail, any_red, harness unhealthy, banner shown | `audit_dashboard/data/db_health.json` | `overall`: `checks_run=5`,`checks_passed=3`,`checks_failed=2`,`any_red=true`,`harness_healthy=false`,`banner_should_show=true` |
| 22,947 ghost rows, 10 cohorts | same | `checks.ghost_rows.data.total_ghost_rows=22947`,`cohort_count=10` |
| top cohort DOGEUSDT LONG n=3,569 / 1 distinct entry | same | `checks.ghost_rows.data.top_cohorts[0]` = MEMECOIN/`meta_strategy`/DOGEUSDT/LONG/`pnl_pct=1.3226`/`n=3569`/`distinct_entries=1` |
| WIFUSDT SHORT 2,763/3; PEPEUSDT LONG 2,052/1; FLOKIUSDT 2,043/1; BONKUSDT 2,043/1 | same | `top_cohorts[2..5]` |
| 94,119 open vs 21 active vs 147,059 total, tier red | same | `checks.open_bloat.data` (`open_count=94119`,`trading_picks.active_count=21`,`total_count=147059`,`tier="red"`) |
| 27.05% naive magnitude mismatch, 0.54% sign mismatch | same | `checks.pnl_integrity.data` (`sampled=24158`,`naive_magnitude_mismatch=6535`,`naive_magnitude_mismatch_pct=27.05`,`sign_mismatch=130`,`mismatch_pct=0.54`) |
| status labels internally consistent | same | `checks.won_pnl_contradiction.data` (`contradiction_detected=false`; TP_HIT n=7063 avg 3.409; SL_HIT n=3882 avg −3.197; LOST n=5634 avg −1.770) |

## C. Blocklist bypass

| Claim | Source | Location / value |
|---|---|---|
| 165 retired-strategy picks still emitting | `audit_dashboard/data/cohort_reconciliation.json` | `blocklist_bypass.flagged=true`, `count=165` |
| example | same | issue `pick_id="multi_asset_forex_rsi2_mean_reversion::AUDJPY=X::2026-11-19_0222"`, `reason="retired"`, `bypass="blocked_now_issue_time_unknown"` |

## D. Batch artefacts

| Claim | Source | Location / value |
|---|---|---|
| 7-row kimi batch swings PF 0.1246→0.2926 | `audit_dashboard/data/cohort_reconciliation.json` | `batch_artefact.clusters[0]`: `count=7`,`source_system="kimi_riseoftheclaw"`; `metrics_excl_batch.pf=0.1245706` vs `metrics.pf=0.2925823` |
| 6-row luxalgo batch is benign | same | `clusters[1]`: `count=6`,`n=1230` vs `1224`, PF 1.15010 vs 1.15067 |

## E. strategy_perf_by_class self-declares non-edge

| Claim | Source | Location / value |
|---|---|---|
| 961 cells, 11 classes | `audit_dashboard/data/strategy_perf_by_class.json` | `n_classes=11`,`n_cells=961` |
| own note: "NOT edge-proven" | same | `note` field |
| example absurd cell (n=5, PF 717) | same | BOND `futures_momentum` n=5 wins=4 `profit_factor=717.2411` |

## F. Multiple testing / gates off

| Claim | Source | Location / value |
|---|---|---|
| 658 strategies; 32.9 expected FPs; z_crit 3.788 | `2026-11-14/finpredict-v2_20261114-1602/MASTER_AUDIT.md` | §5 "Search space actually scored" / "Multiple-testing math" (L280–330) |
| 21 clear Bonferroni, all single-source artifacts | same | §5 (`single_source_pct=1.00`,`is_single_source_artifact=True`) |
| FDR gates disabled, not failing | same | §5 |
| PBO=0.0 degenerate; DSR n_trials=80 vs 658; Reality Check never ran | same | §5 "PBO / DSR / Reality Check" (L311) |
| fleet policy-clean n=22,941, WR 42.21%, PF 0.2657, z=−23.60 | same | §5 "Fleet truth" |
| 94/658 PF>1; 512/658 n<10 | same | §5 |
| per-class: none positive after correction; CRYPTO/FOREX/EQUITY significantly below 50% | same | §5 "Per-class significance" (L317) |

## G. Survivorship

| Claim | Source | Location / value |
|---|---|---|
| 63% never resolve (90,523/143,156) | `MASTER_AUDIT.md` | §5 "Survivorship" (L331) |
| 16,126→7,914 survive gates; 7,567 integrity-excluded; 8,888 auto-expired; 1,777 killer rows | same | §5 |
| only 10/3,500 closed rows <24h; 2,221 >30d; 582 >180d | same | §4 "Closed-pick age" (L257) |
| 42.2% WR, −469.5% sum on 3,500 rows | same | §4 (L232) |

## H. Hyrotrader staleness

| Claim | Source | Location / value |
|---|---|---|
| equity 4,929.34, PnL −70.66, HWM 5,070.3, 0 trading days, last session 2026-04-08 | `audit_dashboard/data/hyrotrader_picks.json` | `account_snapshot` |
| phase-1 target +10% = 500 USDT; daily 250; overall 500; risk 0.50% ($25) | same | `challenge` + `playbook.risk_per_trade_pct_account=0.5` |
| 48 signals, 20W/12L/1exp/15pending, WR 62.5% | `audit_dashboard/data/hyro_pick_performance.json` | `generated_at=2026-11-19T03:58:06Z`,`total_signals=48`,`summary` |
| backtests generated 2026-04-07; rsi2 long WR 33.3%, PnL −71.65 | `audit_dashboard/data/hyro_backtest_results.json` | `generated_at`; `results[0]` |
| short-term entries generated 2026-04-14, 8 actionable | `audit_dashboard/data/hyrotrader_short_term_entries.json` | `generated_at`,`total_actionable=8` |
| closed-picks ledger 359 B; journal 222 B | `ls -la audit_dashboard/data/hyrotrader_closed_picks.json audit_dashboard/data/hyrotrader_journal.json` | sizes |

## I. Paper trading

| Claim | Source | Location / value |
|---|---|---|
| 14 rows, 9 Filled / 5 Cancelled, all 2026-03-06 | `paper_trading.csv` | `csv.DictReader`: len=14, Counter Filled=9/Cancelled=5, dates={2026-03-06} |
| 6 symbols | same | {COINBASE:FILUSD, COINBASE:ETHUSD, BITSTAMP:BTCUSD, CRYPTO:NEARUSD, KRAKEN:WARUSD, OKX:COINUSDT.P} |
| buffy 38 trades, WR 52.63%, PF 1.725, p_coinflip 0.871, NOT_PROVEN | `audit_dashboard/data/buffy_paper_trades.json` | top-level summary fields |
| pilot forward dashboard 2026-06-06, any_promotion_ready=false | `audit_dashboard/data/pilot_forward_dashboard.json` | `timestamp`,`any_promotion_ready` |

## J. Schema

| Claim | Source | Location / value |
|---|---|---|
| 10 DBs; stocks 409 tables | `docs/FINANCE_DB_SCHEMA_SPEC.md` | L26; §2 L39 |
| trading_picks 147,127 @ 2026-11-19 04:48 | same | Appendix A L422 |
| at_pick_outcomes 63,108 @ 2026-11-19 03:24 | same | L423 |
| at_local_picks ~76M (largest) | same | L106 |
| bt_backtest_runs 285, stale since 2026-03-06 | same | L171, L424 |
| 110/409 tables empty | same | L158 |
| price tables exist but omitted from spec | same | Appendix A.1 (L425–447): crypto_ohlcv 1,708,142; stock_ohlcv 459,467; equity_daily_ohlcv 288,522; etf_daily_ohlcv 125,564; fx_prices 3,855; cp_prices 4,857; daily_prices 66,027 |
| fx_prices ends 2026-02-09 → 211 forex picks unmeasurable | same | A.4 (L462–468) |
| all 285 bt_backtest_runs tagged CRYPTO incl. FX symbols | same | A.2 (L449–455) |
| bt_backtest_trades ≈32.7M | same | A.3 (L457–461) |
| misclassification conventions (EURUSDT as FOREX) | same | A.5 |

## Cross-surface contradictions

| Claim | Source A | Source B |
|---|---|---|
| ETF WR/PF | `/audit` policy-clean: WR 1.9%, PF 0.0195, n=52 (`audit_dashboard/data/audit_surface_truth.json`) | `/audit3`: WR 43.15%, PF 1.0043, n=584 (`audit_dashboard/data/audit3_ledger.json`) |
| kill counts | `/audit` "42 kills" card | `/audit3` 11 kill symbols / 2 kill classes |
| money-ready | 0/9 classes (`audit_surface_truth.json`: `money_ready_count=0`; per class `tier2_pass=false`) | `money_ready_verdict.json`: `summary.money_ready=[]`, `watch=["COMMODITY"]`, 11 classes; optimistic `TRUE_PROFITABILITY_VALIDATED.md` (mega_mutation PF 8.32) |
| audit3 class count vs others | `audit3_ledger.json` scores **7** classes (CRYPTO, EQUITY, ETF, FOREX, COMMODITY, BOND, FUTURES) | `audit_surface_truth.json` headline "0/9" but `by_asset_class` has **11** entries; `money_ready_verdict.json` lists 11 |
| money-ready headline value | `audit_surface_truth.json` | `money_ready_count=0`,`money_ready_classes=[]`, headline "0/9 asset classes money-ready" |

## Checkout / date

- Worktree HEAD: `f9e6c8202a12c3be24664020e4f207390159da3f`, branch
  `add-strategy-variable-tracking`, 2026-11-19 06:13 UTC.
- Peer review `05_KILO_REVIEW` cites main tip `1cd4f6527ee`. Numbers above come
  from the worktree checkout named in each row; re-run this index against the
  tip you check out.
