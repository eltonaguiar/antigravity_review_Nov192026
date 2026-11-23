# Testing and backtesting, per class — what was run, what it proved, what it did not

**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL.** Nothing here is a buy list. Read this as the audit
trail of a negative result set.

Every figure carries `[SRC: path:line]` or is written `UNMEASURED`. Where I could not re-derive a
number because its artifact is git-ignored and absent from `origin/main`, I say so and quote the
number from the document that carries it, labelled as second-hand rather than re-verified.

`COMMISSION_UNKNOWN` for every class: no cost below includes commission
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:562]`.

---

## 0. Why no NEW backtest was run this round

This window was spent **verifying existing results, measuring costs, and closing provenance gaps**,
not generating new strategies. Doc 24 declares **N = 0 new variants** for every class it re-visits
(e.g. `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:80-81]` for EQUITY, `:124` for ETF,
`:160-161` for INDEX, `:191-192` for BOND, `:234-235` for COMMODITY, `:276` for FOREX, `:466-467` for FX CARRY).

**The cost of that choice, stated plainly:** there is no new evidence about any new strategy. The
programme's picture of *which strategies work* is exactly what it was before this window, and the
only thing that improved is how well its existing claims are sourced and how well its costs are
measured. That is a real trade, not a free lunch.

**Why running a new backtest would have been worse than not running one:** on the series that exist,
a new run would have produced a number that cannot be trusted.

- The commodity series are **roll-corrupted**: CL=F prints a negative close of **−37.63** on
  2020-04-20, so `pct_change` is meaningless; ZC=F prints ≈−23.6% on 07-15 in three separate years;
  NG=F has **92** moves > 8% `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:49]`,
  `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:112-116]`.
- The equity universe is **backfilled** by construction: every list is a today's-constituents list,
  and the measured **0.0 pp/yr** survivorship gap is zero because both ends are the same 79-symbol
  set. It is a **lower bound, not a null** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:565]`.
- The HML value test is pre-registered but **blocked**: B1 (no point-in-time universe) and B2
  (equity cost) are uncleared, and the document itself says running on the static snapshot would
  bias the result toward a positive finding `[SRC: docs/preregistration/HML_VALUE_TEST_2026-11-22.md:5,33-38]`.

A new number from any of those three would be a number I would have to un-believe. So none was produced.

---

## 1. EQUITY

**What was actually backtested.** Equity breakout (donchian / VT pattern sweep), **1,935 trades** in the sweep and 1,941 in the published-cost run `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]`; the published claim covers **2021-04..2026-04 (n=245)** with a pre-2021 OOS segment `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:70-73]`. Plus HML value (pre-registered, NOT RUN) and N1 R1/R2/R3. Instrument set: equity panel from yfinance 1-min + cached CSVs, **2021-11-22..2026-11-19** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:91-92]`. Artifact: `reports/pod_equity_breakout/pod_equity_breakout_backtest.json`, `reports/pod_equity_breakout/breakout_cost_sweep.json` `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]` — **both git-ignored, absent from origin/main**; I read them only through doc 15.

**What the test proved.**
- Breakout PF **0.9917 @25 bp/side**; PF **1.2206 @5 bp/side**; PF **1.2865 @0 bp/side**; net
  −0.0168%/trade at 25 bp `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]`.
- Break-even **24.5945 bp/side** all-history, **23.91 bp/side** pre-2021 OOS `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:96]`.
- Published PF **1.479 was not reproduced**; measured ≈ 1.00 `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:74-75]`.
- Excess-CAGR CI at measured cost **[−46.32%, +32.31%]**, alpha CI-LB **−0.285%** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:89-90]`.

**What the test did NOT prove.**
- *Sample:* the published claim (n=245) is a small window against a grid whose size is **not recorded** (`UNMEASURED`) `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:72-73,80-81]`.
- *Data quality:* survivorship. *PIT status:* **NO** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:91]`.
- *Look-ahead:* `UNMEASURED` for the breakout sweep, no execution-lag statement recorded `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:74-75]`.
- *Multiple comparison / deflated Sharpe:* `UNMEASURED`; PBO `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:85-86]`.
- *The specific reason it cannot be promoted:* it fails at 0 bp/side (PF 1.2865 is above 1, but the null percentile and negative alpha decision are the binding ones), and no fill improvement can flip a rule whose measured PF is ~1.00 at 25 bp while its own published claim was 1.479 `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:107-109]`.

## 2. ETF

**What was actually backtested: NOTHING.** No ETF strategy has ever been specified; N = 0
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:122-124]`. Only cost was measured, on 14
names, yfinance 1-min, 2026-11-16..20 `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:59-62]`.

**What the test proved.** Cost only: **6.7122 bp** RT median over 14 names (SHY 0.6144 … SOXX 22.9049)
`[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:29]`.

**What the test did NOT prove.** Everything about edge. There is no strategy, hence no PF, no Sharpe,
no CI, no deflated Sharpe, no PBO `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:125-131]`.
*The specific reason it cannot be promoted:* there is nothing to promote. Cost without a strategy is a
price, not a pick.

## 3. INDEX

**What was actually backtested.** One rule, N1 R3 SPY 200-day trend, **1 variant**, on SPY/QQQ/IWM/DIA.
Sample window `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:156-161]`.

**What it proved.** Null percentile **53.4** (bar ≥ 95), excess vs SPY **−6.8 pp**, cost
**8.0325 bp** `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:193,56]`.

**What it did NOT prove.** Sharpe, maxDD, PF, DSR, PBO, WFE, 2×-cost survival and CI on net return
are all `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:162-167]`. Look-ahead
`UNMEASURED`: a 200-day average is only lag-safe if it executes next bar, and no such statement is
recorded `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:157-159]`. PIT: **NO**.
*Cannot be promoted:* it underperforms SPY before cost is charged.

## 4. BOND / MUTUAL_FUND

**What was actually backtested.** B1 time-series long-only, B2 cross-sectional L/S, B3 duration timing
via TLT, on **10 bond ETFs**, **49 monthly rebalances**, counted as **ONE row** (one dataset, one
artifact, one verdict) `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:37]`,
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:191-193]`. Artifact:
`reports/bond_momentum_20261122.json` (line 183 carries `breakeven_bp_per_side_sharpe_zero`)
`[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:88,96]` — **git-ignored, absent from
origin/main**; read through docs 25/26.

**What the test proved** (verified against the JSON by doc 25; I could not re-open the JSON on main):

| variant | PF | Sharpe vs rf | maxDD | CAGR | skew |
|---|---|---|---|---|---|
| B1 | **1.3121** | **−0.5497** | **−5.81%** | **+1.631%** | −0.2413 |
| B2 | **0.7431** | **−1.6985** | −5.31% | **−1.28%** | −0.5028 |
| B3 | **0.7366** | **−1.0628** | −11.64% | **−2.05%** | **−1.4523** |

`[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:90-96]`

**What the test did NOT prove.**
- *Sample window, rebalance, look-ahead:* all `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:189-190]`.
- *Data quality:* the ETF return series is suspect. The `Close` behaves as dividend-adjusted (SHY
  gained +10.4% over 5 years while rates rose ~4%, only possible with coupons reinvested) and the
  dividend-adjustment method is flagged `UNMEASURED` `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:37,63]`.
- *Multiple comparison:* N=3, DSR `UNMEASURED`, PBO `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:195-197]`.
- *PIT:* **NO** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:200]`.
- *Why it cannot be promoted:* break-even is 0 bp/side, so it loses with free trading (§ below).

**MUTUAL_FUND leg: no backtest at all.** No instrument, no fee schedule, no return series;
`INSUFFICIENT_MEASUREMENT` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:126]`.

## 5. COMMODITY / FUTURES

**What was actually backtested.** V1 L/S, V2 long-only, V3 long-only + filter, on **7 futures
front-month series**, **48 monthly rebalances**, one row for the family
`[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:36]`,
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:234-235]`. Term-structure carry: **no backtest**,
zero second-month contract series on disk `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:123-125]`.
Artifact: `reports/commodity_momentum_20261122.json` `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:187]`
(git-ignored / absent from origin/main).

**What the test proved.**
- V1 PF **0.757**, CAGR **−7.13%**; V2 PF **1.114**, CAGR **+0.47%**; V3 PF **1.074**, CAGR **−0.67%**,
  all against 4.32% `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:36]`.
- Break-even **0 bp/side**; Sharpe vs rf −0.627 / −0.038 / −0.089 `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:47]`.
- Null percentiles 30.2 / 33.1 / 25.2 `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:36]`.

**What it did NOT prove.**
- *Data quality:* the series are roll-corrupted (§0), so the numbers are on wrong prices.
- *Sample window, rebalance, look-ahead:* `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:227-229]`.
- *PIT:* **NO**. *DSR / PBO:* `UNMEASURED`.
- *Why it cannot be promoted:* the row's verdict is UNKNOWN *because* the data is not a price history, not because the strategy is promising. `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:187]`

**FUTURES (financial)**: no backtest with a net-of-cost result recorded; cost UNMEASURED.

## 6. FOREX

**What was actually backtested.**
- FX momentum 63d/21d: **n = 4,092** pair-rebalances, quintile L/S, 21-day hold
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:29]`.
- FX mean-reversion 5d/5d: **55 dedup pairs, 403 windows, 8,866 pair-rebalances**
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`.
- FX carry: **95 months, 11 currencies** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:463]`.
- Artifacts: `reports/forex_carry_trend_20261122.json`, `reports/fx_meanrev_cost_sweep/sweep.json`,
  `reports/fx_carry_20261122.json` `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:25-31]`
  (git-ignored / absent from origin/main; read through docs 22/26).

**What the test proved.**
- Momentum: gross **−26.88 bp**, net **−36.88 bp**, null **0.0** percentile `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:29]`.
- Mean-reversion: gross **+4.30 bp**, net **−5.70 bp @10bp**, break-even **4.3038 bp**, window-clustered CI at 1 bp **[−4.32, +11.09]** `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`.
- Carry: Sharpe **−0.126**, CAGR **+3.38%**, vol **7.43%**, worst month **−7.55%**, null **98.2**, break-even **468.5 bp** `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:36]`.

**What it did NOT prove.**
- *Cost is a Sunday-reopen upper bound*, not a representative session; `COMMISSION_UNKNOWN`
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:131]`.
- *Sample window* for the momentum run `UNMEASURED`; *look-ahead* `UNMEASURED`
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:272-274]`.
- *Multiple comparison:* variant count `UNMEASURED` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:275-276]`.
- *PIT:* **NO** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:284]`.
- *Why it cannot be promoted:* mean-reversion's break-even sits below the measured cost **and** its CI includes zero at every cost tested; momentum is negative gross; carry fails on Sharpe.

## 7. CRYPTO

**What was actually backtested.**
- Crypto intraday mean-reversion: **5,400 trades**, 4h bars, 10 symbols, artifact
  `reports/crypto_meanrev_intraday_20261122.json` `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:40]`.
- Cross-venue basis: **720 minutes**, 3-way overlap `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:37]`.
- Funding-basis carry: 5 symbols, **214 BTC episodes** `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:35]`.
- **Paper pod** (`crypto_intraday_sim`): 3 pre-registered slots on real 4h bars, paper only
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim.py:1-23]`. Log:
  `verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl` — **this one IS on origin/main**.

**What the test proved.**
- Mean-rev PF **0.815 @0 bp**, **0.691 @20 bp**, break-even **0 bp**, all 10 symbols negative `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:40]`.
- Cross-venue: **0.00%** of minutes above the 40.48 bp threshold `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:37]`.
- Funding carry: **82/2,838 (2.889%)** of episodes reach the 16.398-day break-even; pair RT 45.524 bp `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:83]`.
- Pod: **5 closed** rows (bollinger_mr 3, vwap_reversion 2, btc_4h_rsi_macd 0) and 2 open, read from my own count of the CLOSE events in the log `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl]`; `bollinger_mr` cum **+5.1063%**, `vwap_reversion` cum **−11.5229%** and **HALTED** at 11.5% vs the 10% limit `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:3-32]`.

**What it did NOT prove.**
- The pod has **no CI, no PF, no IR** on its own hypothesis: 0 forward rows in the confirmatory ledger (430 of 432 lines are non-pod H-119) `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:106]`.
- *Sample too small:* every guardrail reads `no_judgment: n<20` `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:6,16,26]`.
- *Lag:* the lab evidence does not survive the 1-bar lag (PF 0.957, PBO 0.84–0.97) `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:322-324]`.
- *PIT:* not established `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:329]`.
- *Why it cannot be promoted:* 0 closed forward rows on the pod's hypothesis and a lag-adjusted PF below 1.

## 8. MEME

**What was actually backtested: NOTHING.** No meme strategy was specified; N = 0
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:350-351]`.

**What the test proved.** Cost only: DOGE-USD **6.7938 bp**; SHIB-USD 0.00 bp is tick-truncated
(84.3% zero-range bars, 53/55 distinct values) and must not be quoted as zero; PEPE-USD empty
`[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:118-121]`.

**What it did NOT prove.** Any edge. 1 quotable name of 3 against a rule needing ≥ 2. *Cannot be
promoted:* there is no strategy and no usable second instrument.

## 9. PENNY_STOCK

**What was actually backtested: NOTHING.** No penny strategy exists; N = 0, `aggregate: null`,
universe `[]` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:372-376]`.

**What the test proved.** A cost sample now exists: **21.2974 bp** RT median, 7/8 names, survivor-biased
convenience sample `[SRC: updates/2026-11-23-stale-cost-status-corrections.md:13]`.

**What it did NOT prove.** Anything about edge, and the cost itself is not representative. *Cannot be
promoted:* with N = 0 there is nothing to evaluate the cost against `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:157-163]`.

## 10. SPORTS

**What was actually backtested: nothing in this programme.** No sports dataset, no cost measurement,
no strategy `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:397-401]`. The one study that
exists ran elsewhere: n=1,039 +EV bets over 46 events `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:77]`.

**What it proved.** No confirmable edge: ROI +8.68% point but **event-clustered CI-LB −9.1%** with
n_events 46 < 100 and stale-snapshot odds `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:138]`.

**What it did NOT prove.** A measured price of participation: bookmaker margin or exchange fee counts in
the manual-verification JSONs are all **0** `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:136]`.

## 11. FUNDING-BASIS CARRY (crypto) / FX CARRY

**FUNDING-BASIS CARRY.** Backtested: delta-neutral perp basis, 6 hold-period variants (1/3/7/14/30/90 d),
one row, 5 symbols `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:426-430]`. Proved:
Sharpe −61.23 (1d) / +0.555 (30d) / +0.740 (90d), maxDD −1077.4% / −24.19% / −17.11%, net APR +2.42%
(30d) / +6.24% (90d) `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:35]`. Did NOT
prove: capacity beyond XRP $29,438; PIT ("not established"); DSR/PBO `UNMEASURED`. Cannot be promoted:
only 2.889% of episodes reach the break-even hold, and at XRP capacity the ceiling ($699–1,837/yr) is
below the $1,272 T-bill `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:189]`.

**FX CARRY.** Backtested: 95 months, 11 currencies, monthly rebalance, cost sweep 0–10 bp/month
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:463-464]`. Proved: Sharpe −0.126, gross CAGR
+3.38%, vol 7.43%, worst month −7.55%, skew −0.63, maxDD −11.71%, null 98.2, excess-vs-SPY CI
[−8.28%, +2.29%] `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:36]`. Did NOT prove:
PF (not reported), PBO, WFE, DSR. Cannot be promoted: Sharpe ≤ 0 is the kill rule.

---

## The cost overlay method

Every net figure in this programme is a **gross figure minus the round trip**, applied per side:

```
net = gross − 2 × cost_per_side          (round trip = 2 sides)
```
This is how the programme states it: cost is **round-trip (RT)** unless a per-side figure is stated, and
the equity figure is **12.0749 bp RT = 6.0375 bp/side** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:29-30,64-65]`.
The 2×-cost gate is therefore `2 × cost_RT` per round trip (e.g. `2 × 6.7122 = 13.4244 bp` for ETF
`[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:129]`, `2 × 8.0325 = 16.065` for INDEX `:166`,
`2 × 12.0749 = 24.1498` for EQUITY `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:25]`).

**Every cost is an upper bound.** These are medians of 1-minute bar ranges, `median((high − low)/close)`,
so the RT quoted spread cannot exceed them because bid and ask both lie inside `[low, high]`
`[SRC: updates/2026-11-23-cost-estimator-description-correction.md:19-31]`. They are **not NBBO**, and
they are **not Corwin-Schultz**; the Corwin-Schultz field is a separate, less reliable number in the
same artifact (BOND 0.0724, COMMODITY_FUTURES 0.0, PENNY_STOCK 8.7933) `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:41-45]`.
No commission is included anywhere.

## The gate arithmetic: why `c* ≤ 0` makes the cost overlay irrelevant

If a strategy's break-even cost is `c* ≤ 0`, then for **any** positive cost `cost > 0 ≥ c*` the net
return is negative. A smaller (tighter, more accurate, even hypothetical zero) cost estimate moves
the number toward zero but can never cross a non-positive break-even
`[SRC: updates/2026-11-23-nbbo-measurability-probe.md:149-155]`.

**Classes this kills outright, at any cost:**
- **BOND** momentum B1/B2/B3 — break-even **0 bp/side** on all three `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:96]`.
- **COMMODITY** momentum V1/V2/V3 — break-even **0 bp/side** `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:47]`.
- **CRYPTO intraday mean-reversion** — break-even **0 bp**, PF 0.815 at zero cost `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:40,99]`.
- **FX momentum** is killed before cost too: gross itself is **−26.88 bp** `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:29]`.

So for BOND and COMMODITY, further cost refinement cannot change the verdict. That is why cost
refinement is not on the next-steps list.

---

## The unmeasured register (what a reader should assume missing)

| Item | Status |
|---|---|
| NBBO for any class | never measured; all costs are 1-min bar-range upper bounds `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:41-45]` |
| Commission | `COMMISSION_UNKNOWN` everywhere `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:562]` |
| Point-in-time universe | missing for every class `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:563-565]` |
| Deflated Sharpe / PBO for any class | `UNMEASURED` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:198]` |
| Capacity at intended size | only one datapoint in the programme, XRP $29,438 `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:192]` |
| Benchmark-matched information ratio | none for any class `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:198]` |
| Mutual-fund fee data | none at all `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:195]` |

---

PROVENANCE: repo `eltonaguiar/antigravity_review_Nov192026`, branch `main`; all figures read from
`eltonaguiar/findtorontoevents_antigravity.ca` at `origin/main` =
`b508d25cd52eef7165499c1616b48f30e1169946` via `git show`. Backtest artifacts under `reports/` are
git-ignored on that branch; where I could not open one I say so and attribute the number to the
document that carries it. Date 2026-11-23.
