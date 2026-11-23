# The phased build plan, failure checklist, and six metric panels

**Source:** Qwen4 Max (Alibaba Cloud) final answer, 2026-11-23 — the most complete of eighteen answers.
Full text: `harvest_1min_qwen4max_final.txt`. Attribution: model identified by the operator; the earlier partial capture
(`harvest_1min_r2.txt`) is now superseded by this file for citation.

**Why this document exists:** the synthesis explains *what is true*. This explains *what to do, in what order, and what
would make each step invalid*. It is the document the agents execute against.

---

## 1. The build order — nine phases, each with a gate

| Phase | Duration | Deliverable | Gate to proceed |
|---|---|---|---|
| **0** | 2–3 wks | PIT data + universe + cost model per class | reproducible snapshot; survivorship handled |
| **1** | 2 wks | case-control study on historical gainers with **matched controls** | **≥ 2 features with meaningful odds ratios *and* a mechanism story** |
| **2** | 2 wks | model-free predictability surface: variance ratio, Hurst, vol-R², dispersion — by class / symbol / horizon / side | identifies where structure exists *at all* |
| **3** | 3–4 wks | labels (triple barrier + MFE/MAE), baseline models, purged CPCV | OOS IC / precision@K lift with **PBO < 0.3** |
| **4** | 2 wks | TP/SL surfaces from MFE/MAE; **synthetic-null control** | **plateau, not peak**; edge above the GBM null |
| **5** | 2 wks | full cost-aware backtest + robustness battery + DSR | survives 2× costs, execution delay, trade removal |
| **6** | 4–8 wks | pre-registered shadow trading, **hashed prediction log** | live ≈ shadow; calibration holds |
| **7** | 8–12 wks | micro-live, reconciliation, capacity curve | slippage within model; positive expectancy in R |
| **8** | ongoing | ramp + drift monitoring + kill switches | — |

**Note the Phase 1 gate:** it requires **a mechanism story alongside the odds ratios**. Statistics alone do not open the
gate. That is the same rule as our "name the loser", written as a build gate rather than a review comment.

---

## 2. The failure-mode checklist — 15 items, checked per study

- [ ] Sampling on the outcome (gainers-only datasets)
- [ ] Survivorship — delisted equities and dead tokens
- [ ] Retroactively adjusted price series creating look-ahead
- [ ] Non-point-in-time fundamentals
- [ ] Overlapping labels → inflated t-stats
- [ ] Ambiguous TP/SL bars resolved **optimistically**
- [ ] Stops assumed to fill **at the stop price** (ignores gaps, cascades, halts)
- [ ] Ignoring borrow fees, funding, financing
- [ ] **Unaccounted trial count** — *"the silent killer"*
- [ ] Timezone / timestamp misalignment across sources
- [ ] Trading at a price you cannot actually get (mutual-fund forward pricing; MOC assumptions)
- [ ] Crypto exchange outages during the modelled move
- [ ] Wash-traded volume treated as real liquidity
- [ ] Signal decays post-publication and you did not budget for it
- [ ] Sizing based on **uncalibrated** probabilities

---

## 3. The six metric panels — reported per class, per symbol tier, per direction

> *"Report all six panels per asset class, per symbol tier, per direction. **That table is the answer to 'which is more
> predictable'.**"*

### A. Prediction quality — is there information at all?

| Metric | Why |
|---|---|
| Spearman **IC** per period, and **ICIR** = mean(IC)/std(IC) | the workhorse for cross-sectional ranking |
| **Precision@K** and **lift** = precision@K ÷ (K/N) | *the* metric for top gainers — only the top K must be right |
| **PR-AUC** (preferred over ROC-AUC under heavy imbalance) | rare-event discrimination |
| Brier score / log loss, calibration curve, **ECE** | you cannot size from uncalibrated probabilities |
| Hit rate vs base rate, **per side** | skill ≠ accuracy |
| NDCG@K, decile monotonicity | ranking quality beyond the top bucket |
| conditional forward-return distribution of picks vs universe | does the *magnitude* differ, not just the frequency |

### B. Trade level — does the geometry work?

Expectancy in R; profit factor; payoff ratio; win rate; R-multiple distribution (fat left tail?); MAE/MFE distributions;
time-in-trade; % stopped vs timed-out vs TP; **gap-through frequency**; stop slippage.

### C. Portfolio — is it worth capital?

CAGR, vol, Sharpe, Sortino, Calmar/MAR, max DD and DD duration, Ulcer index, skew/kurtosis, tail ratio, Omega, turnover,
gross/net exposure, **beta and alpha vs a relevant benchmark — long signals vs the index, not vs cash**, correlation to
existing strategies.

### D. Statistical confidence — is it luck?

Deflated Sharpe, PSR, PBO, HAC t-stat, block-bootstrap CIs, MinTRL, **trial count N**, CPCV Sharpe distribution.

### E. Execution and operations

Implementation shortfall (bps), slippage vs model, fill rate, participation rate, **cost as % of gross alpha**, capacity
($ at which alpha halves), signal→order latency, data-staleness incidents, uptime.

### F. Stability

Rolling 3m/6m IC, per-regime breakdown, parameter drift across retraining, **alpha decay half-life**, performance by symbol
and by side.

---

## 4. The two artifacts that make self-deception impossible

> *"The single highest-value thing you can build first isn't a model — it's **the timestamped, hash-committed prediction
> log** and **the synthetic-null control**. Those two artifacts make it impossible to fool yourself, and self-deception, not
> lack of cleverness, is what defeats most attempts at this."*

**The prediction log.** Every signal is written to an **append-only** log *before the outcome is known*, recording:
timestamp · symbol · side · entry reference · TP · SL · time limit · predicted probability · **model hash** ·
**feature-snapshot hash**. Periodically publish the log's hash.

> *"This makes retrospective fitting impossible — **including by you, to yourself, which is the more common failure.**"*

**The synthetic-null control.** Run the entire TP/SL pipeline on shuffled/bootstrapped returns preserving vol clustering,
and on synthetic GBM matched to each symbol's σ. Whatever edge appears is the overfitting floor. Subtract it.

---

## 5. Forward testing as a clinical trial

**Pre-register**, then freeze and hash the model artifact. The document must state: hypothesis and mechanism, universe,
horizon, entry rule, TP/SL rule, sizing, primary metric, **minimum detectable effect**, required sample size, stopping rule,
kill criteria.

**Three phases:**
1. **Shadow, 4–8 weeks** — live data, real timestamps, no orders. *"This is where you discover your feature pipeline used a
   value that wasn't available yet."*
2. **Micro-live** — smallest viable size. Compare live fills to modelled fills; *"the gap is your backtest's bias, quantified."*
3. **Ramp** — increase along a measured capacity curve; stop when marginal impact eats a set fraction of gross alpha.

**No peeking.** Alpha-spending (O'Brien–Fleming), SPRT, or always-valid e-values. Pre-commit to the stopping rule.

**Drift monitoring in production:** PSI / KS on feature distributions · rolling IC and rolling calibration · realised vs
predicted slippage · CUSUM or Page–Hinkley on the P&L residual with automatic de-risking · hard kill switches (max daily
loss, max DD, max exposure, data-staleness timeout).

> *"If live and shadow diverge, the difference is **a bug or an unmodeled cost — not 'the market changed'**. Investigate
> before scaling."*

---

## 6. The robustness battery — six tests

| Test | What it proves |
|---|---|
| Parameter perturbation (±20% on every knob) | performance should degrade **smoothly** |
| Execution delay (1 bar, 5 min, next open) | *"a signal that only works at the exact close is suspect"* |
| Remove the top 5% of trades **and** the best 10 days | is the edge concentrated? |
| Stationary / block bootstrap CIs | returns are not IID |
| Newey–West HAC t-stats | overlapping returns |
| Regime slices: vol terciles, trend/range, bull/bear, pre/post-2020, rate regimes, liquidity regimes | regime dependence |

**Cost stress:** at 2× and 3×. And one threshold stricter than our protocol: *"if the edge dies at 1.5× costs, it isn't
real."*

---

## 7. Calibration targets — what "good" looks like

> Daily cross-sectional **IC 0.02–0.05** is a genuinely usable edge. Directional **hit rates 52–56%** are normal.
> **Precision@10 of 15–25% against a 2% base rate** is excellent lift. **Net Sharpe 1–2** at modest capacity is a real,
> deployable strategy.

> **"A backtest showing Sharpe 4, 85% win rate, and tiny drawdown is telling you there's a bug — most likely an
> ambiguous-bar resolution, a look-ahead feature, or an outcome-conditioned sample."**

That sentence is the acceptance test in reverse: **spectacular is a defect signal**, not a discovery.

---

## 8. The one-page conclusion

> *"Stop studying winners and start studying the full cross-section, using matched case-control to generate hypotheses and
> cohort studies to establish base rates. Encode TP/SL directly into your labels via triple barriers, and calibrate them
> from conditional MFE/MAE distributions rather than grid-searching for a peak — remembering that barriers alone cannot
> manufacture edge from a martingale. Treat predictability as a property of (symbol, horizon, features, costs, regime),
> measure it model-free before you measure it with models, and split by direction only when interactions and per-side
> calibration prove you should. 'Proven' means purged combinatorial CV, multiple-testing deflation across your entire trial
> history, a pre-registered hashed forward test, and live fills that reconcile with your model — with a mechanism story
> that makes the result plausible in the first place."*

*Research methodology, not investment advice. Paper only. Zero capital.*
