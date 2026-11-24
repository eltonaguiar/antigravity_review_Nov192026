# EVALUATION_HARNESS task queue — verification run 2026-11-24

Cron run, Tue 2026-11-24 14:06 EST (UTC-05). Repo: antigravity_review, main.
CDP healthy on 127.0.0.1:9333 (Chrome/150.0.7871.250). All three VS Code AI panels
(kilo, zoo, copilot) in thinking/RUNNING state — left alone, no nudges.

## 1. Experiment schema — `docs/experiment_schema.sql` (commit 206a2e8)

Executed the DDL in an in-memory SQLite database -> 12 tables confirmed:
runs, run_params, market_events, signals, orders, fills, positions,
portfolio_snapshots, risk_events, metrics, trials, artifacts.

Command (exit 0) -> `12`

## 2. `CONTEST/tools/trial_log.py` — append-only trial ledger

Already present and tracked; columns match the schema's `trials` table exactly
(trial_id, run_id, family, variant, sharpe_is, sharpe_oos, kept, ts_logged).
Append-only: INSERT only, no DELETE path. Ran once on two dummy variants into a
scratch db in TMPDIR (not the real ledger — the real ledgers are fixture-polluted
and must not be degraded further):
- dummy_var_A: sharpe_is=1.2, sharpe_oos=0.9, kept=0 -> row_count=1
- dummy_var_B: sharpe_is=0.8, sharpe_oos=1.1, kept=1 -> row_count=2

## 3. `CONTEST/tools/dsr.py` — Deflated Sharpe Ratio

Already present and tracked. Formula source:
Bailey & Lopez de Prado, "The Deflated Sharpe Ratio," Journal of Investment
Management, 2014. PSR (Lo 2002) adjusts a single trial's Sharpe SE for
skew/kurtosis; DSR deflates the best-of-N trial Sharpe using the cross-trial
variance of trial Sharpes: z = (SR_best - SR_bench) / s_trials, DSR = Phi(z).

Ran on the dummy log -> REFUSED, exit 2:
"REFUSED: 2 of 2 ledger rows are fixtures (e.g. run_id='run-dummy-1'
family='dummy_family'). DSR on synthetic trials is not a measurement - refusing
to emit one."
"No DSR number is emitted — this is the intended guard (DSR_GUARD /
DSR_VOID_9c9eda3): a DSR on fixture rows or n < MIN_TRIALS_FOR_DSR (30) is not
a measurement. The voided commit 9c9eda3 (DSR=0.999983991176608 on 4 fixture
rows) is the defect this guard prevents from recurring."

## 4. `CONTEST/tools/cpcv.py` — Combinatorial Purged Cross-Validation

Already present and tracked (Lopez de Prado, AFML Ch. 7). Ran on SPY monthly
(PRICE panel: PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT/data/market_prices.csv,
SPY_adj, resampled to monthly by last close of each YYYY-MM):
n_months=60, groups=6, embargo=1, horizon=1 -> n_paths=6.

OOS Sharpe distribution (annualised, sqrt(12)):
- mean = 1.2940
- std = 1.4815
- min = -1.1967
- max = 3.6650
- median = 1.0871
- p5 = -1.1967, p95 = 3.6650

## 5. `POWER_ANALYSIS.md` — MDE every verdict must quote

Already contains the required statement; no edit needed.
- Actual sample: SPY monthly adjusted close (Yahoo), 406 monthly returns =
  33.8 years, annualised vol 14.77% -> MDE at t=2 = 2*0.1477/sqrt(33.8) =
  5.08%/yr. Every PASS/WATCH/FAIL verdict on this sample must quote it.
- Cross-check vs `CONTEST/ROUND_01_2026-11-23/POSITIVE_CONTROL.md` (same gate,
  real SPY monthly): injected 3.00%/yr alpha -> recovered 3.00%, t=1.18, CI
  [-1.98,+7.98], not significant — a genuine 3%/yr premium is invisible over
  33.8 years at 14.8% vol (below MDE 5.08%). Injected 10.00%/yr -> t=3.94,
  significant. Gate is correct and unbiased; the limit is power, not the gate.

## 6. Commit

This verification record committed to main. No source deliverables were missing
— trial_log.py, dsr.py, cpcv.py, POWER_ANALYSIS.md, and the schema all pre-existed
at HEAD and were verified in this run.
