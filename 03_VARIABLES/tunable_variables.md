# Variables — what can be toggled and observed

The owner asked for "the potential available variables where we could try to switch it and
see if we would've made a profit with some minor adjustments." Here they are, grouped by
layer. Each is a knob the audit system (or a counterfactual re-run) can turn **and
measure** — provided the forward ledge exists.

## A. Measurement / gate variables (fix first — cheapest, highest leverage)

| # | Variable | Current value | Suggested experiment |
|---|---|---|---|
| A1 | Edge gate | G1 `WR > 50%` (binomial) | Switch primary test to **G2 bootstrap net-expectancy CI > 0**; demote WR to a descriptor |
| A2 | Multiplicity family | all 45 cells BH'd together | Split **confirmatory vs discovery** namespaces; BH per namespace. Confirmatory pods get fixed α |
| A3 | Slippage constants | flat per class (CRYPTO 0.15%, EQ 0.10%, FX 0.05%) | Add **2× stress column** and a "net CI at 2×" gate; validate against `now_history` realized fills |
| A4 | Stability test | split-half (2 windows) | Roll 4–8 weekly cohort means; add turnover-adjusted capacity note |
| A5 | Window | recent-biased (3,500 rows) | Declare window; publish full-history companion (e.g. 21,988 policy-clean CRYPTO) |
| A6 | Provenance | `/tmp` source path | Embed commit SHA + file SHA-256 + generator version |
| A7 | Scoring coverage | 21.4% | Raise to >90% before any promotion decision |

## B. Resolver / labeling variables (the artifact factory)

| # | Variable | Current | Experiment |
|---|---|---|---|
| B1 | Win definition | `net pnl_pct > 0` after slippage | Keep, but fix `EXPIRED → WON` mislabel; use SL-wins-ties intrabar first-touch |
| B2 | Fixed TP vs time/vol exit | fixed TP/SL picks | Re-express pods as **premia-style sizing**: exit on time/vol (2–3 ATR trail or 10–20d), symmetric, no fixed TP; size by inverse realized vol to portfolio vol target |
| B3 | Intrabar vs bar-close | resolver version drift | Pin `resolver_version`; enforce idempotent re-resolve; enforce `pnl_pct` NOT NULL on resolved rows |

## C. Emission / production variables

| # | Variable | Current | Experiment |
|---|---|---|---|
| C1 | Tribunal → emitter wiring | none (output is a page) | Wire KILL cells → scanner **denylist**; KILL symbols → drop dominance. Re-review only on forward evidence |
| C2 | Promotion path | none | Add `PROVEN_T2`: n≥100 forward rows with net CI-LB>0 (or IR≥0.5) → small-size production cap (≤1% NAV/trade) + forward-clock review at 30/60/90d |
| C3 | Concentration | 7 classes, ~47 strategies active | **3 pods max, 2 classes** (CRYPTO SHORT + EQUITY/ETF LONG); pause emission elsewhere |
| C4 | Source concentration cap | `max_source_share = 0.9` | Candidate is 98% single-source — require a second independent source or a different venue before promotion |

## D. Class / strategy variables

| # | Variable | Experiment |
|---|---|---|
| D1 | CRYPTO ensemble-grade LONG | Pre-register pod: LONG when ensemble grade ∈ {A,B}/score ≥60, symmetric vol-scaled exit, no fixed TP; dedup A⊂B; forward-shadow 90d |
| D2 | `luxalgo_confluence SHORT` | Pre-register SHORT-only pod with BTC-regression + funding covariates; require second source; kill if forward CI-LB ≤ 0 at day 60 |
| D3 | Equity/ETF breakout family | One family-level test vs a **random-entry timing null** (`daily_prices` 66k rows + `benchmark_closed_ledger.py`); 30-day decision |
| D4 | Prediction markets | Only as maker ≥85¢ with Brier tracking, or pure probability oracle; retag rows out of CRYPTO |
| D5 | Carry (H-024) | Re-test as vol-targeted long/short basket with trend overlay — not TP/SL picks |

## E. Data / infrastructure variables

| # | Variable | Experiment |
|---|---|---|
| E1 | System of record | Declare `at_signal_outcomes` canonical; define the other two ledgers as views/derived |
| E2 | Forward-observation table | Add `forward_observations(id, hypothesis_id, opened_at, closed_at, symbol, class, side, entry_px, exit_px, qty, fees, funding, slippage_bps, resolver_version, intrabar_first_touch, benchmark_leg_ret, regime_ok, created_at)` |
| E3 | Backtest dedup | One canonical `bt_backtest_trades`; drop/mirror-less the stocks copy after row-count parity; pre-aggregate to (strategy, symbol, class, month) |
| E4 | Ghost rows | Resolve the 3-way contradiction at the data layer; make ghost-row count live, not hardcoded |
| E5 | Staleness assertions | Per-table freshness budgets with **workflow failure** (e.g. `portfolio_snapshots` > 7d → red) |
| E6 | Benchmark legs | Every pod card requires excess vs matched-exposure benchmark (BTC-hold for crypto SHORT, SPY for equity/ETF LONG), IR, down-capture |
| E7 | Backups | run+record quarterly restore test; row-count/checksum parity job; document RPO/RTO |
| E8 | Empty tables | decision-log + silence the 110+20+9 empty tables & dormant clusters to shrink agent search space |

> **Note:** many of these knobs already exist as *reported* columns in audit3 (e.g. the
> 2× slippage CI is computed but report-only). The work is to promote them from
> report-only to **gates**, and to wire a forward ledger so the counterfactual is actually
> observable.
