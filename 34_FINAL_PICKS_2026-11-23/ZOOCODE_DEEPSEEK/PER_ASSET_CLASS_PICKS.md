# Per-asset-class picks — 12 classes, 2026-11-23

**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL.** Every row below is a research ordering. No
allocation is implied, and the correct count of investable picks is **zero**.

**Ranking key, reproduced from doc 24:** `LB(c) = (LB95(NetCAGR_cc) − 4.32%) / UB95(σ_net,cc)`
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:494-495]`. Tie-breaks: (1) higher 95% LB on
net excess, (2) lower turnover, (3) larger margin under 2× costs, (4) larger deflated Sharpe,
(5) higher capacity headroom `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:529-536]`.

## 0. Why no class is ranked by `LB(c)`

**`LB(c)` is `UNMEASURED` for all 12 classes.** Gate (4) needs a CI on net return *on committed
capital*; none exists, so numerator and denominator are both undefined
`[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:97-99]`, and doc 25 prints
`n/a` in the rank-key column of all 12 rows `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:16-29]`.

What I can order is **proximity to decidability**: how many of the four eligibility gates are
*decidable* rather than missing, and whether any interval on return exists. The proximity score
below is mine, defined as:

| Score | Meaning |
|---|---|
| **P0** | no cost, no strategy, no data — nothing to decide |
| **P1** | cost measured (or partly), but no strategy to evaluate against it |
| **P2** | cost and a tested strategy, killed on cost-independent grounds, or pending n |
| **P3** | a CI on return exists (or a bound on `LB` can be computed) but includes zero and the kill rule fails |
| **P4** | CI excludes zero on the right side and only forward n is missing |
| **P5** | `LB(c) > 0` at 2× cost — investable |

**No class scores above P3. None is P4 or P5.**

## 1. The ordering, all 12 classes

| # | CLASS | VERDICT | COST (RT) | COST STATUS | PROXIMITY | CAN IT BE RANKED? |
|---|---|---|---|---|---|---|
| 1 | FOREX | NOT_INVESTABLE (FX carry) / UNKNOWN (FX mean-rev) | 7.533 bp | MEASURED (upper bound) | **P3** | no — no CI on net CAGR |
| 2 | EQUITY | NOT_INVESTABLE | 12.0749 bp | MEASURED (upper bound) | **P3** | no — CI is excess-vs-SPY, not net CAGR |
| 3 | INDEX | NOT_INVESTABLE | 8.0325 bp | MEASURED (upper bound) | **P2** | no |
| 4 | CRYPTO | PENDING (PENDING_N) | 20.0–52.0 bp all-in | MEASURED (fees+spread) | **P2** | no — 0 forward rows on the pod's hypothesis |
| 5 | BOND | NOT_INVESTABLE | 1.2125 bp | MEASURED (upper bound) | **P2** | no — break-even 0 bp |
| 6 | COMMODITY | UNKNOWN (BLOCKED_MISSING_DATA) | 6.3182 bp front-month; roll cost | MEASURED (front-month only) / roll UNMEASURED | **P1** | no |
| 7 | ETF | BLOCKED_MISSING_DATA (no strategy) | 6.7122 bp | MEASURED (upper bound) | **P1** | no |
| 8 | MEME | KILLED | 6.7938 bp (DOGE only) | MEASURED (1 of 3 names) | **P1** | no |
| 9 | PENNY_STOCK | KILLED | 21.2974 bp | MEASURED (upper bound, survivor-biased) | **P1** | no |
| 10 | FUTURES | UNKNOWN / UNMEASURED | UNMEASURED | UNMEASURED | **P0** | no |
| 11 | SPORTS | KILLED | UNMEASURED | UNMEASURED | **P0** | no |
| 12 | MUTUAL_FUND | UNKNOWN | UNMEASURED | UNMEASURED | **P0** | no |

The order is P3 → P2 → P1 → P0; within a score I break ties by "has a CI at all", then by how
many gates are decidable, which is the doc-24 tie-break spirit applied where its primary key is
undefined. It is an ordering of evidence, not of opportunity.

---

## 1. FOREX — P3

- **Verdict:** `NOT_INVESTABLE` for FX momentum and FX carry; `UNKNOWN` for FX mean-reversion
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:180-183]`.
- **Deciding numbers:** mean-reversion break-even **4.3038 bp** against measured cost **7.533 bp**
  (median of six USD-major medians; all-pairs median 7.99 bp) — a **3.23 bp shortfall**; FX momentum
  **−26.88 bp gross**, net −36.88 bp, n=4,092, null 0.0 percentile; FX carry Sharpe **−0.126** vs
  4.32% with break-even **468.4739 bp** `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:29-30]`,
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:53,89]`.
- **Cost provenance:** Tiingo top-of-book, sampled at the Sunday 22:00Z reopen, upper bound,
  `COMMISSION_UNKNOWN` `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:51-52]`.
- **Best in-class candidate:** FX carry quintile (95 months, 11 currencies, vol 7.4329%, worst month
  −7.55%) — the only class where `LB(c)` can be bounded at all: `LB(c) ≤ −0.248`
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:109,111]`. Its own pass/fail:
  **FAIL** on `Sharpe ≤ 0`, **FAIL** on excess-vs-SPY CI `[−8.28%, +2.29%]` spanning zero.
- **What would move it:** a weekday London/NY-overlap spread sample below ~2.6 bp *and* a
  window-clustered CI-LB above 0 for mean-reversion `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:115]`;
  for carry, a net-return CI-LB above 4.32% against a Sharpe of −0.126.

## 2. EQUITY — P3

- **Verdict:** `NOT_INVESTABLE` (doc 26: `DEAD-NOT-REOPENED`) `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:21]`.
- **Deciding number:** breakout profit factor **0.9917 at 25 bp/side** and **1.2865 at 0 bp/side**;
  value family **+0.11%/yr gross** `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]`,
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:108-109]`.
- **Cost provenance:** **12.0749 bp RT upper bound** (6.0375 bp/side, Corwin-Schultz 1.5033 bp,
  13 symbols, `provenance_self_check PASS`) `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:53-54]`.
  MEASURED, but a bar-range upper bound and not NBBO.
- **Best in-class candidate:** N1 R1 multi-asset momentum (79 symbols) — null percentile **61.2**,
  excess vs SPY **+0.97 pp**, the highest null percentile of any equity row
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:191]`. Its own pass/fail: **FAIL**,
  null 61.2 < 95 required.
- **What would move it:** an OOS net-return CI-LB on committed capital above 4.32% at
  2 × 12.0749 = 24.1498 bp RT `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:25]`; and it would
  still need a point-in-time universe with delisted names `[SRC: docs/preregistration/HML_VALUE_TEST_2026-11-22.md:21-38]`.

## 3. INDEX — P2

- **Verdict:** `NOT_INVESTABLE` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:33]`.
- **Deciding number:** SPY 200-day trend null percentile **53.4** (bar ≥ 95), excess vs SPY **−6.8 pp**
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:193]`.
- **Cost provenance:** **8.0325 bp** median over 4 names (SPY 8.3139, QQQ 12.0749, IWM 7.7512,
  DIA 5.5896) `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:56]`. MEASURED.
- **Best in-class candidate:** SPY 200-day trend (N1 R3), the only tested rule; 1 variant, trial
  count 1 declared up front `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:160-161]`.
  Pass/fail: **FAIL** on null percentile and on excess-vs-SPY sign.
- **What would move it:** a trend rule that beats SPY *before* cost and carries a net-return CI
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:37]`. INDEX is an alias of ETF
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:150-151]`, so it inherits ETF's answer.

## 4. CRYPTO — P2

- **Verdict:** `PENDING_N` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:57]`.
- **Deciding number:** **0 closed forward rows on the pod's own hypothesis** (H-2026-11-19-01) in
  the confirmatory ledger `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:106]`; all-in RT
  **20.0016 bp** at Binance rising to ~52 bp at Kraken `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:59]`.
- **Cost provenance:** taker fee 10 bp/side (Binance/BinanceUS/KuCoin), 26 bp (Kraken), plus spread;
  MEASURED `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:48-50]`.
- **Best in-class candidate:** the live paper pod `vwap_reversion` (H-2026-11-19-01), and its
  sibling slot `bollinger_mr` (H-2026-11-19-02), which is the only slot with positive cumulative
  paper P&L: **+5.1063%** over n=3 closed. `vwap_reversion` is **HALTED** at **11.5229%** trailing
  drawdown against a 10% limit (n=2 closed, −11.5229%). `btc_4h_rsi_macd` has n=0 closed
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:3-32]`. Pass/fail: **FAIL /
  not evaluable** — lab PF 0.957 at the 1-bar lag, PBO 0.84–0.97 at the lag
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:322-324]`.
- **Also a row: funding-basis carry** `NOT_INVESTABLE` — only **82 of 2,838 episodes (2.889%)** last
  the **16.398-day** break-even; pair RT 45.524 bp `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:83]`.
- **What would move it:** 100 closed forward rows on the pod's hypothesis with net PF CI-LB > 1.0,
  IR ≥ 0.5 and split-half stability; earliest day-30 checkpoint **2026-12-19**
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:47,110]`.

## 5. BOND — P2

- **Verdict:** `NOT_INVESTABLE` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:39]`.
- **Deciding number:** break-even **0 bp/side** on all three variants, with Sharpe **−0.5497 /
  −1.6985 / −1.0628** beside PF **1.3121 / 0.7431 / 0.7366** and maxDD **−5.81% / −5.31% / −11.64%**
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:90-96]`.
- **Cost provenance:** **1.2125 bp** RT median, 10/10 names (JNK 0.5442 … TLT 2.5126),
  `MEASURED_FROM_LAST_SESSION`, bar-range upper bound, NOT NBBO
  `[SRC: updates/2026-11-23-stale-cost-status-corrections.md:10]`. MEASURED. The backtest itself
  charged **5 bp/side ASSUMED**, not this number `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:96]`.
- **Best in-class candidate:** B1 time-series long-only bond momentum over the 10-ETF universe
  (TLT, IEF, SHY, TLH, AGG, BND, LQD, TIP, JNK, HYG) `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:93]`.
  Pass/fail: **FAIL** — PF 1.3121 sits beside Sharpe −0.5497, maxDD −5.81%, null percentile 2.0, and
  excess-vs-SPY bootstrap **[−30.00%, −4.14%]** `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:92,98]`.
  The cheapest instrument measured anywhere in the programme is the bond ETF **SHY 0.6144 bp**
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:204-205]` — labelled NOT INVESTABLE
  because cheap execution of a losing signal is still a losing signal.
- **What would move it:** a total-return series with one declared, reconciled dividend method plus a
  strategy with positive Sharpe at measured cost `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:37]`.

## 6. COMMODITY / FUTURES (commodity leg) — P1

- **Verdict:** `UNKNOWN` (`BLOCKED_MISSING_DATA`) for momentum V1/V2/V3 and term-structure carry
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:187,190]`.
- **Deciding number:** PF **0.757 / 1.114 / 1.074** at break-even **0 bp/side** (Sharpe vs rf
  −0.627 / −0.038 / −0.089) `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:47]`.
- **Cost provenance:** **6.3182 bp** RT median, 7/7 names, front-month `=F` only,
  `MEASURED_UPPER_BOUND` `[SRC: updates/2026-11-23-stale-cost-status-corrections.md:11]`. **Roll cost
  UNMEASURED** and no second-month series exists `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:123-125]`.
- **Best in-class candidate:** V2 long-only (PF 1.114, CAGR +0.47% vs 4.32%) `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:36]`.
  Pass/fail: **FAIL** as a family; its PF is the only one above 1 and it still loses to T-bills.
- **What would move it:** a roll-adjusted, back-adjusted continuous series from individual contract
  months with an explicit pre-declared roll rule, plus per-contract commission
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:119-121]`. The series on disk are
  roll-corrupted: CL=F has a negative close **−37.63** (2020-04-20), NG=F has **92** moves > 8%
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:49]`.

## 7. ETF — P1

- **Verdict:** `BLOCKED_MISSING_DATA` — **no ETF strategy has ever been specified**
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:27]`.
- **Deciding number:** **6.7122 bp** RT median over 14 names; `NO_STRATEGY_WITH_CI`
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:29-30]`.
- **Cost provenance:** MEASURED, yfinance 1-min bars, 2026-11-16..20; bar-range upper bound
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:55,59-62]`.
- **Best in-class candidate:** none by strategy (N = 0 `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:124]`).
  The per-name spreads, all labelled NOT INVESTABLE for lack of any strategy:
  **SHY 0.6144 · AGG 1.0507 · TLT 2.5126 · GLD 5.3234 · DIA 5.5896 · XLV 5.7847 · XLF 6.1146 ·
  XLY 7.3099 · XLE 7.3870 · IWM 7.7512 · SPY 8.3139 · QQQ 12.0749 · XLK 14.2149 · SOXX 22.9049**
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:62]`.
- **What would move it:** any specified ETF strategy with a forward ledger and a net-return CI
  clearing 4.32% at 2 × 6.7122 = 13.4244 bp `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:31]`.

## 8. MEME — P1

- **Verdict:** `KILLED` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:63]`.
- **Deciding number:** **1 quotable name of 3** against a frozen rule needing ≥ 2
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:118-123]`.
- **Cost provenance:** DOGE-USD **6.7938 bp** measured; SHIB-USD 0.00 bp is **tick-truncated**
  (84.3% zero-range bars) and must not be quoted as a zero spread; PEPE-USD has no data.
  MEASURED for 1 name only `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:56-58]`.
- **Best in-class candidate:** none. DOGE-USD buy-and-hold at 6.7938 bp is the only measured-cost
  action and it is not a strategy `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:359]`.
- **What would move it:** a second quotable meme name on a tick grid finer than its price moves,
  then a strategy with a CI `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:67]`.

## 9. PENNY_STOCK — P1

- **Verdict:** `KILLED` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:69]`.
- **Deciding number:** the strategy-side cost artifact has `classes.PENNY_STOCK.aggregate = null`,
  universe `[]`, blocked `NO_INSTRUMENT_IN_REPO` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:71]`.
- **Cost provenance:** a measured sample now exists at **21.2974 bp** RT median, 7/8 names
  (TELL empty), SIRI 6.2697 → PLUG 92.6440, `MEASURED_FROM_LAST_SESSION`, a convenience sample with
  survivor bias `[SRC: updates/2026-11-23-stale-cost-status-corrections.md:13]`,
  `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:35]`. MEASURED as an upper bound.
- **Best in-class candidate:** none. **No penny strategy and no penny backtest exist**; N = 0
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:375-376]`.
- **What would move it:** at least one penny instrument in a cost sample *and* a pre-registered
  strategy with a break-even to evaluate the cost against `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:73]`,
  `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:157-163]`.

## 10. FUTURES (financial, non-commodity) — P0

- **Verdict:** `UNMEASURED` on cost; the class has no independent edge proven in the repo's own
  record `[SRC: reports/asset_class_90day_plan_FUTURES_2026-05-15.md:9]`.
- **Deciding number:** UNMEASURED. No futures cost artifact exists in the 12-class taxonomy
  `[SRC: updates/2026-11-23-stale-cost-status-corrections.md:80-88]`.
- **Cost provenance:** UNMEASURED. The commodity front-month figure (6.3182 bp) is a different
  class and is not borrowed here `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:246-248]`.
- **Best in-class candidate:** none named with a net-of-cost result.
- **What would move it:** a futures cost measurement (per-contract commission + tick) and a strategy
  with a CI.

## 11. SPORTS — P0

- **Verdict:** `KILLED` (`KILLED_NO_COST`) `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:140]`.
- **Deciding number:** no measured margin or fee; the one study found n=1,039 +EV bets over 46
  events, ROI +8.68% point, but **event-clustered CI-LB −9.1%** (56 events short of 100)
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:77]`.
- **Cost provenance:** UNMEASURED. Field scan of the three manual-verification JSONs: counts of
  `spread`, `vig`, `margin`, `commission`, `cost` are all **0**
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:136]`.
- **Best in-class candidate:** none.
- **What would move it:** a measured bookmaker margin or exchange fee, closing-line capture, and
  settled outcomes `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:79]`.

## 12. MUTUAL_FUND — P0

- **Verdict:** `UNKNOWN` `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md` (mutual-fund leg of the BOND/MUTUAL_FUND row, `BLOCKED_MISSING_DATA`)].
- **Deciding number:** UNMEASURED — no expense ratio, no load, no 12b-1, no spread for any mutual
  fund `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:126]`.
- **Cost provenance:** UNMEASURED. `reports/capacity_20261122.json` records MUTUAL_FUND as
  `INSUFFICIENT_MEASUREMENT` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:126]`.
- **Best in-class candidate:** none. No expense ratio is assumed in either direction
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:134]`.
- **What would move it:** a fee schedule and a return series for at least one fund.

---

## What the 12 rows add up to

Zero classes at P4 or above. The only two classes with any interval on return are FOREX and EQUITY
(and FX CARRY inside FOREX), and all of those intervals include zero. The classes nearest a
decision are the ones where a *number for the denominator* could be produced cheaply, not the ones
with the best-looking point estimate.

---

PROVENANCE: repo `eltonaguiar/antigravity_review_Nov192026`, branch `main`; all figures read from
`eltonaguiar/findtorontoevents_antigravity.ca` at `origin/main` =
`b508d25cd52eef7165499c1616b48f30e1169946` via `git show`. Date 2026-11-23. The proximity score is
this agent's construction and is labelled as such; every underlying figure is sourced or
`UNMEASURED`.
