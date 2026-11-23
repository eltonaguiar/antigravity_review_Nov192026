# Overall top picks — a WATCHLIST, 2026-11-23

**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL.**

**Zero of these five are investable.** The correct number of investable picks is **zero**, and
this is a research ordering by evidence quality and proximity to decidability, not an allocation.
No position, size, or order is implied anywhere in this file. `LB(c) = (LB95(NetCAGR_cc) − 4.32%) /
UB95(σ_net,cc)` `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:494-495]` is undefined for
every class because none has a CI on net return on committed capital
`[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:97-99]`; the ordering below is the
doc-24 tie-break spirit (money first, then cost exposure, then credibility, then size) applied
where the primary key does not exist.

Tally: `0 INVESTABLE / 11 NOT_INVESTABLE / 3 UNKNOWN (14 rows)`
`[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:195]`.

---

## 1. FX carry quintile — FX CARRY
**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL**

- **What it is:** long the high-yield currency quintile, short the low-yield quintile, monthly
  rebalance, 95 months, 11 currencies `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:463]`.
- **Why it ranks highest:** it is the only class where the deciding statistic is a *hurdle* rather
  than an absent measurement or a cost that swallows the edge, and it is the only class where
  `LB(c)` can be bounded numerically at all `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:13]`.
- **The number that decides it:** Sharpe vs the 4.32% T-bill **−0.126**, gross CAGR **+3.3817%**,
  vol **7.4329%**, worst month **−7.55%**, break-even cost **468.4739 bp**
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:89]`. The key: `LB(c) ≤
  (2.4777% − 4.32%) / 7.4329% = −0.248`, where `2.4777% = 3.3817% − 12 × 0.07533%`
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:109-111]`.
- **The gate it FAILS:** the per-class kill rule `Sharpe ≤ 0` (observed −0.126), and gate (4) in
  substance: excess CAGR vs SPY CI **[−8.28%, +2.29%]** spans zero with a point of −3.04%
  `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:90]`.
- **What would have to become true:** a net-return CI-LB above 4.32% while Sharpe is −0.126. That
  requires a different carry construction, not a cheaper cost.
- **What would go wrong:** carry is short-volatility by nature and the worst month (−7.55%) is a
  crash month; if the CI point is the whole story, this is a negative-expectancy strategy, not a
  near-miss. The 98.2nd-percentile random-ranking null says the *ranking* was lucky, which is the
  opposite of a reason for confidence.

## 2. FX mean-reversion 5d/5d (R22) — FOREX
**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL**

- **What it is:** 5-day formation, 5-day holding mean reversion over 55 dedup pairs, 403 windows,
  8,866 pair-rebalances `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`.
- **Why it ranks second:** it is the only row where the gap to a decision is a single measured
  number (a weekday spread) rather than a missing strategy or missing data, and it already has a
  CI.
- **The number that decides it:** gross **+4.30 bp**, net **−5.70 bp at 10 bp**, break-even
  **4.3038 bp**, measured cost **7.533 bp**, window-clustered CI at 1 bp **[−4.32, +11.09]**
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`.
- **The gate it FAILS:** kill rule `break-even ≤ measured cost` (4.3038 ≤ 7.533) and gate (3): at
  2 × 7.533 = 15.066 bp the shortfall is 10.76 bp `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:54]`.
- **What would have to become true:** a weekday London/NY-overlap spread below ~2.6 bp **and** a
  clustered CI-LB above zero `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:115]`.
- **What would go wrong:** even at 1 bp the clustered CI includes zero
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:59]`, so a cheaper spread alone may not
  close it; and the 4.30 bp gross is a thin edge over 8,866 overlapping rebalances, where the
  effective sample is far smaller than n.

## 3. Equity breakout / value family — EQUITY
**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL**

- **What it is:** donchian/VT-pattern breakout sweep (1,935 trades) and the HML value family
  `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]`,
  `[SRC: docs/preregistration/HML_VALUE_TEST_2026-11-22.md:1-5]`.
- **Why it ranks third:** it has a measured, non-trivial cost (12.0749 bp) and a CI, so the arithmetic is complete enough to show *how far* it is; it ranks below the FX rows because its point estimate is negative.
- **The number that decides it:** breakout PF **0.9917 @25 bp/side**, **1.2865 @0 bp/side**,
  published PF 1.479 **unreproduced** (measured ≈ 1.00); value **+0.11%/yr gross**
  `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]`,
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:74-76]`.
- **The gate it FAILS:** gate (2) and gate (3) at 1× cost; excess-CAGR CI **[−46.32%, +32.31%]**
  spans zero with a point of −14.25% vs SPY `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:24]`.
- **What would have to become true:** a strategy whose OOS net-return CI-LB clears 4.32% at
  24.1498 bp RT. It would also need a point-in-time universe: the current one is a
  today's-constituents list, and the 0.0 pp/yr survivorship gap is a lower bound by construction
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:565]`.
- **What would go wrong:** the HML preregistration is **PRE-REGISTERED, NOT YET RUN** and its own
  blockers B1 (no PIT universe) and B2 (equity cost) state that running it on the static snapshot
  would bias *toward* a positive result `[SRC: docs/preregistration/HML_VALUE_TEST_2026-11-22.md:5,33-38]`.
  Any value number produced now would be wrong in a known direction.

## 4. Bond momentum B1/B2/B3 → bond ETF universe (JNK … TLT) — BOND
**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL**

- **What it is:** B1 time-series long-only, B2 cross-sectional L/S, B3 duration timing via TLT, on
  10 bond ETFs, 49 monthly rebalances `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:37]`.
- **Why it ranks fourth:** the *cost* side is now among the best measured in the programme
  (1.2125 bp RT; SHY 0.6144 bp is the cheapest instrument measured anywhere), so it is the class where the remaining defect is most clearly the signal, not the execution.
- **The number that decides it:** break-even **0 bp/side**; B1 PF **1.3121** beside Sharpe
  **−0.5497**, maxDD −5.81%, CAGR +1.631%; B2 0.7431 / −1.6985 / −1.28%; B3 0.7366 / −1.0628 /
  −2.05% / skew −1.4523 `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:90-96]`.
- **The gate it FAILS:** gate (2) at *any* cost. With `c* = 0` and any `cost > 0`, `cost > 0 ≥ c*`
  ⇒ net < 0 `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:149-155]`.
- **What would have to become true:** a positive-Sharpe bond rule on a total-return series with one declared dividend method. A cheaper spread cannot help.
- **What would go wrong:** B1's PF of 1.3121 is the classic PF-inflation trap — it sits in cash
  10.2% of months and the denominator counts only closed losing positions `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:63]`.
  Quoting it without Sharpe −0.5497 would misrepresent the row.

## 5. Crypto VWAP-reversion paper pod (H-2026-11-19-01) + bollinger_mr sibling (H-2026-11-19-02) — CRYPTO
**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL**

- **What it is:** a live paper simulation, three pre-registered slots on real 4h bars, no live
  capital `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim.py:1-23]`.
- **Why it ranks fifth:** it is the only row producing *new* rows at all, so it is the only one whose verdict can change by waiting rather than by work.
- **The number that decides it:** **5 closed rows** (bollinger_mr 3, vwap_reversion 2,
  btc_4h_rsi_macd 0) and 2 open `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl]`,
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:3-32]`. `vwap_reversion` is
  **HALTED** at **11.5229%** trailing drawdown vs the 10% limit `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:29-30]`.
- **The gate it FAILS:** the lagged lab evidence already fails: PF **0.957** at the 1-bar lag, PBO
  **0.84–0.97** at the lag `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:322-324]`; and
  zero forward rows exist on the pod's own hypothesis in the confirmatory ledger
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:106]`.
- **What would have to become true:** 100 closed forward rows with net PF CI-LB > 1.0, IR ≥ 0.5 vs
  BTC/ETH and split-half stability. Earliest day-30 checkpoint **2026-12-19**, day-60 **2027-01-18**;
  the date for n ≥ 100 is **UNMEASURED** on main, because no close rate is recorded there
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:110]`. The log's 5 closes span
  2026-11-20..2026-11-22, which is far too few to call a rate.
- **What would go wrong:** a halted slot is a drawn-down slot; the 3 losses out of 5 closes
  (−4.0789, −5.2401, −6.2828) came from stops, and the 2 wins were TIME exits
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl]`. If the lag-adjusted
  PBO is the real number, this pod is expected to fail.

---

## Why the other rows are not in the top 5

- **INDEX** (SPY 200-day, null 53.4) and **ETF** (no strategy at all) have less to decide.
- **COMMODITY** and its two UNKNOWN rows are blocked on a roll-adjusted series, not on effort.
- **MEME, PENNY_STOCK, SPORTS** have no strategy; **MUTUAL_FUND** and **FUTURES** have no cost data.
- **Funding-basis carry** is NOT_INVESTABLE on opportunity frequency (2.889%), a number no cost or execution improvement changes `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:85]`.

## One-line summary a skimmer must not misread

Five names, zero investable, zero capital, all paper. The list is ordered by how close each is to a
*decision*, and every one of them is currently on the losing side of that decision.

---

PROVENANCE: repo `eltonaguiar/antigravity_review_Nov192026`, branch `main`; all figures read from
`eltonaguiar/findtorontoevents_antigravity.ca` at `origin/main` =
`b508d25cd52eef7165499c1616b48f30e1169946` via `git show`. Date 2026-11-23.
