# Evaluation harness and validation protocol

**Source:** operator specification, 2026-11-24. Encoded here so agents work against files, not prose.
**Schema:** `docs/experiment_schema.sql` (executable DDL, SQLite-compatible).

---

## 1. What the validation tools actually answer

These are anti-overfitting instruments. They are not interchangeable, and each one fails if its
precondition is missing.

| Term | What it is | Question it answers | Practical rule |
|---|---|---|---|
| **Walk-forward (WFA)** | Roll through time: fit on A, test on B, roll forward | Does it survive unseen periods? | Never retune on out-of-sample results. Judge consistency across windows, not the best window |
| **Purged K-fold** | Time-series CV that drops training samples whose labels overlap the test period | Am I leaking the future across folds? | Required whenever labels span time (5-day returns, triple-barrier) |
| **Embargo** | Buffer after each test set before training resumes | Is there residual leakage at fold edges? | Size it from the horizon and autocorrelation |
| **CPCV** | Combinatorial purged CV: split into N groups, test combinations, purge/embargo | How does it behave across *many* possible OOS histories? | Much stronger than one split; needs enough data |
| **PBO** | Probability the best in-sample config underperforms OOS (below median rank) | Did I pick a lucky winner? | Lower is better; high PBO = likely overfit |
| **PSR** | Probability the true Sharpe exceeds a benchmark, adjusting for skew/kurtosis and track length | Is this Sharpe better than the benchmark given the return *shape*? | Useful, but **insufficient** after many trials |
| **DSR** | PSR corrected for the number of trials and their variance | Is this Sharpe impressive *after* everything I tried? | The key anti-data-mining metric. **Meaningless without a complete trial log** |
| **Monte Carlo** | Resample or simulate to get a distribution | What range of outcomes and drawdowns is plausible? | Uncertainty tool, not proof of edge |
| **White's Reality Check / SPA** | Formal test that the best strategy beats benchmark after data snooping | Is the best performer significant after many tests? | Alternative or complement to DSR |

**The core idea:** a high backtest Sharpe is cheap when you ran 500 variants. DSR, PBO and CPCV make
you pay for the search.

### Why the trial log is load-bearing

`trials` exists in the schema because **DSR is arithmetic on the trial count.** A program that reports a
deflated Sharpe while logging only its winners has not computed a deflated Sharpe — it has computed PSR and
put a better name on it. Failed trials are data, not embarrassment.

---

## 2. Harness interfaces

One interface so backtest, paper and live are the same code path with different adapters.

```
DataFeed(point-in-time bars/ticks/fundamentals, calendar, tz, corporate actions)
   -> Strategy.on_data(ctx) -> signals | target weights | orders
   -> RiskManager(position limits, gross/net, leverage, drawdown kill switch)
   -> ExecutionSimulator(market/limit/stop, fees, spread, slippage, latency, partial fills)
   -> Portfolio(cash, positions, PnL, margin, funding)
   -> Metrics(returns, drawdown, turnover, exposure, regime diagnostics)
   -> ExperimentTracker(immutable run metadata + artifacts)
```

**What must stay identical across modes:** strategy logic, risk rules, metric definitions, logging.
**What changes:** only the data source and the broker adapter.

| Mode | Changes | Must stay identical |
|---|---|---|
| Backtest | simulated fills, replayed data | strategy, risk, metrics, logging |
| Monte Carlo | resampled paths or trades | risk and accounting rules, metric definitions |
| Paper | live data, simulated broker | same code path, same config, no silent manual tweaks |
| Live | real broker, real fills, real latency | same interfaces; stricter monitoring and kill switches |

---

## 3. Decision gates

Label every strategy **PASS (research)**, **WATCH** or **FAIL**.

PASS requires **all** of:

1. Beats a simple baseline **after** conservative costs (buy-and-hold, random, or class-appropriate).
2. OOS / walk-forward results are consistent across windows and regimes.
3. DSR / PBO / multiple-testing diagnostics do not indicate likely overfitting.
4. Robust under **2× cost** and small parameter perturbations.
5. Assumptions are realistic for the asset class.

**Add the gate this programme learned the hard way:** state the **minimum detectable effect** of the
sample you are judging. A "failed" verdict from a sample that could only resolve 9%/yr is a statement
about power, not about markets. See `POWER_ANALYSIS.md` and `POSITIVE_CONTROL.md`.

---

## 4. Monte Carlo — use the right type

| Type | How | Use for | Caution |
|---|---|---|---|
| Trade bootstrap | resample the trade sequence | drawdown distribution, ruin probability | assumes trade independence |
| Block bootstrap | resample blocks | preserves short-term autocorrelation | block size matters |
| Parametric | simulate from a fitted distribution | quick risk estimates | fat tails and regime shifts break it |
| Path MC | GBM / jump-diffusion / stochastic vol | scenario exploration | synthetic paths may not resemble real microstructure |
| Parameter perturbation | jitter parameters | robustness / plateau detection | **not** a substitute for OOS validation |

Store MC as first-class runs: `run_type='monte_carlo'`, with `parent_run_id`, `n_simulations`, `seed`,
and percentile outputs (P5/P50/P95 max drawdown, CAGR, ruin probability).

---

## 5. Per-class realism requirements

Costs and fidelity are not uniform, and the programme has **measured** costs per class
(`COST_OF_RECORD.md`): equity 12.07 bp, ETF 6.71 bp, index 8.03 bp, bond ETF 0.61 bp, FX 7.53 bp,
crypto 20–52 bp, futures unmeasured.

- **Penny stocks / meme coins:** model illiquidity, halt, rug and manipulation risk explicitly. If data
  and fill realism are insufficient, label **"not reliably backtestable"** rather than reporting a number.
- **Day trading:** 1-minute bars are usually insufficient for microstructure edges. Prefer tick / L1 / L2.
  Without them, label results **"low fidelity."** Add `signal_ts`, `order_submit_ts`, `ack_ts`, `fill_ts`.
- **Options:** spreads are frequently 5–20% of premium; greeks and assignment must be modelled.
- **Futures:** unfunded; collateral earns cash, so the excess-return hurdle is zero, not the cash rate.
- **Prediction markets:** a 2¢ spread on a $1 contract is ~200 bp. Model it or exclude the class.

---

## 6. Reproducibility checklist

- Version **code** (`git_commit`, full 40-char sha), **data** (`data_snapshot_id`), **config**
  (`config_hash`), **seed**.
- Raw data is immutable; derived results go to new run folders.
- Append-only event logs; never overwrite `orders` or `fills`.
- Save the exact environment (lockfile digest, OS, container image).
- Auto-generate a run report: config, metrics, charts, assumptions, **known limitations**.

> **Rule of thumb:** if you cannot replay a run exactly and explain every trade from signal to fill,
> you do not yet have a trustworthy simulation.

---

## 7. What this schema deliberately refuses

- **A metric without a scope.** `metrics.scope` is NOT NULL because an "overall" number that is really
  in-sample has manufactured more false confidence in this programme than any other single defect.
- **A trades table without an order.** Fills reference orders, orders reference signals, signals
  reference runs. An unattributable P&L row is how ghost rows entered the backtests here.
- **A run without a commit and a data snapshot.** A number you cannot re-derive is a claim, not a result.
- **A trial log that can be pruned.** There is no delete path. That is the point.

*Paper only. No live orders, no credentials. Not investment advice.*
