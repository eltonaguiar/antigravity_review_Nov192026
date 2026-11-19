# Quant / Fund-Manager Playbook — per asset class, risk-tiered (2026-11-19)

**Role:** act as the portfolio manager for each asset class and answer: what is
the *fastest defensible* path to a viable sleeve, at conservative vs aggressive
risk, given the measured evidence in this repo. Every class is graded on the
same evidence: realized selection alpha (vs hold), OOS Sharpe, measured
slippage, and the audit3 verdicts.

---

## 0. The honest baseline (read this first)

The measured record says **no positive selection alpha in any slice**; the whole
book nets −0.188%/trade. So "quick viable strategies" cannot honestly mean "new
directional scanners." It means, in order:

1. **Fix the two mechanical leaks that are larger than any signal** (below) —
   these are "quick" because they are bug fixes, not research.
2. **Hold a low-cost beta core** — the only thing in the data with a positive
   expectation after costs.
3. **Pre-register ONE premium pod** in the one class with positive OOS Sharpe,
   and let the forward clock decide.

The barbell (from the repo's own reviewers) is the only structure the numbers
support: **70–85% beta core / 10–25% premia sleeve / ≤5% speculative.**

---

## 1. The method to get "quick viable" strategies (5 steps)

**M1 — Fix the fill model first (highest ROI, ~days, not weeks).**
Crypto's realized stop loss is 2.990% vs planned 1.919% — a **+1.071pp overshoot
per stopped trade = 98.8% of the entire crypto class loss**. Resolving stops
against intrabar OHLCV (fill at stop when the bar breaches; at close on gap)
moves crypto PF 0.768 → ≈1.00. No new signal required; this is the single
fastest "edge" in the repo.

**M2 — Stop the value-destroying expressions (also days, not weeks).**
- Stop crypto **longs under TP-first geometry** (−0.44%/pick vs hold).
- Stop intraday **ETF churn** (slippage = 234% of PnL).
- Stop the **SWING** timeframe (−1.31%/trade, n=389).

**M3 — Use only families with a century-scale economic prior.** Trend/TSMOM,
carry, value/quality, PEAD, mean-reversion. Directional prediction on public
daily bars is the low-probability path — the data confirms it.

**M4 — Pre-register, then test once.** Register the pod in
`reports/audit3_confirmatory.json` *before* its forward data exists; otherwise it
can never exceed CANDIDATE.

**M5 — Gate on the measurement stack, not a backtest.** Selection alpha vs hold,
DSR at true N, BH/FDR, 2×-cost stress, and a 90-day forward clock. No n<50
backtest winner qualifies.

---

## 2. Per asset class (conservative → aggressive)

### Stocks / Equity — the only class with positive OOS Sharpe (+0.61, 33 folds)
- **Conservative:** broad beta core — SPY / VTI / FXAIX. Reference baseline in
  the repo: FXAIX +73.05% (11.61% CAGR), SPY +72.38%, VTI +64.39%. No stock
  picking. This is the "boring, correct" sleeve.
- **Moderate:** the already-pre-registered `POD-EQUITY-BREAKOUT` (adx/donchian/
  rs-breakout/vol-contraction scouts). `rs-breakout-scout` is the only large-n
  walk-forward VIABLE (n=136). PEAD on large caps (Bernard–Thomas) as the second
  pod — needs 500+ names + SUE.
- **Aggressive:** single-name momentum/PEAD with **symmetric time/vol exits**
  (no fixed TP), sized ≤1% NAV/trade, only after the moderate pod clears gates.

### Crypto — directional longs are proven losers; only neutral/carry survive
- **Conservative:** minimal or zero directional. If any, BTC/ETH beta only; the
  class is KILL (n=1,851, −0.46%/trade) and longs underperform *holding* by
  0.44%/pick.
- **Moderate:** market-neutral cross-sectional momentum (E3 — 333 symbols × 1h
  bars already in DB; long top decile / short bottom, dollar-neutral); funding/
  basis carry (E7, capacity-capped).
- **Aggressive:** VWAP/mean-reversion (4h) — the one crypto family with in-repo
  walk-forward support — **only after M1 (fill fix)**, vol-scaled exits, no
  TP-first. Never invert the long book (flips beta sign, keeps the exit problem).

### Forex — unmeasurable today; retire from the money path
- **Conservative:** none. `fx_prices` ends 2026-02-09; symbol mapping broken
  (`AUDJPY=X` never maps to `AUDJPY`); 211 picks have **zero computable alpha**.
  Also `EURUSDT` is mis-filed as FOREX (it is crypto).
- **Moderate:** G10 FX carry + 200d trend overlay (E9) — **only after E11
  backfill** reaches ≥90% coverage. Otherwise retire.
- **Aggressive:** none — cannot be judged.
- **Note:** `forex_rsi2_mean_reversion` was already recommended for abandonment
  in a May 2026 audit (Connors RSI2 is sub-50% WR in trending forex); its
  realized n is 24, not the 523 some specs cite.

### Bonds — ballast only
- **Conservative:** BND / SGOV / low-duration as the portfolio's risk-free
  anchor (SGOV +20.86% over the reference window; BND −1.51%).
- **Moderate/Aggressive:** none — n=34, WEAK, PF 0.55; no forward plan.

### ETFs — monthly cadence only (intraday is a cost artefact)
- **Conservative:** no intraday. Monthly/quarterly rotation at most.
- **Moderate:** Faber 200d TAA / dual momentum (in-repo Sharpe 1.74, PF 5.69 —
  but treat as discovery, re-verify at 2× cost).
- **Aggressive:** none intraday — measured slippage eats 234% of per-trade PnL.

### Commodities — KILL class; avoid
- **Conservative/Moderate/Aggressive:** none. KILL (n=55, −3.20%/trade). Only
  roll-yield carry as a future research line, and only with price data.

### Futures — the strongest premium candidate, but thin data
- **Conservative:** none yet (INSUFFICIENT_N, n=4).
- **Moderate:** vol-targeted TSMOM across liquid futures/ETFs (E8 — ~140 yrs of
  evidence, crisis alpha, monthly rebalance, symmetric exits, 20–60 instruments,
  2× costs + 1-bar delay). This is the single best-researched premium in the
  repo.
- **Aggressive:** the same TSMOM at a higher vol target / longer lookback, after
  the moderate pod clears.

### Mutual funds — low-fee index wrappers beat active
- **Conservative:** broad index wrappers (FXAIX etc.); the repo's data already
  shows them tracking/beating the alternatives at ~5 bps.
- **Moderate:** factor tilts (value + momentum) via low-cost funds.
- **Aggressive:** none — active MF fees are a structural drag, not an edge.

---

## 3. The barbell, concretely

| Sleeve | % | Content | Risk |
|---|---|---|---|
| Beta core | 70–85% | SPY/VTI/FXAIX + BND/SGOV ballast | conservative |
| Premia | 10–25% | POD-EQUITY-BREAKOUT + one of (TSMOM, FX carry, cross-sectional crypto) | moderate |
| Speculative | ≤5% | only after a pod clears PROVEN_T2 | aggressive |

Decision rule (write it down now): at day 90, if no pod shows a positive net-CI
lower bound at 2× measured slippage and IR ≥ 0.5 vs SPY, declare **"no deployable
edge on available data"** — a citable result — and keep the capital in the beta
core.

---

## 4. Data-integrity prerequisites (must be true before any sleeve is sized)

1. **Resolve the two blocklists.** The audit3 KILL denylist *is* wired today
   (`feed_hygiene.py:194`, `forward_validator.py:763`), but the **older
   retired-strategy blocklist** (`strategy_blocklist.py` / `_RETIRED_STRATEGIES`)
   is still bypassed — `cohort_reconciliation.json` shows 165 retired picks
   emitting, incl. `forex_rsi2_mean_reversion` (reason "retired").
2. **Stamp at-issue inputs** on 100% of rows (today 6%) so the walk-forward gate
   stops peeking.
3. **One denominator** — `resolved_closed_picks_net`, not per-surface slices.
4. **No backtest-n vs realized-n** anywhere: `crypto_liquidity_wick_reversal_v1`
   is n=4,904 backtest vs n=43 realized; `forex_rsi2` is n=24, not 523.

*Not investment advice.*
