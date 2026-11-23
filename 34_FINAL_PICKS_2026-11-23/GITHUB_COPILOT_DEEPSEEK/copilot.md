# GITHUB COPILOT_DEEPSEEK — final picks, 2026-11-23

```
filed_utc:      2026-11-23T03:05Z
filed_local:    2026-11-23T03:05Z (host clock is UTC; no EST conversion applied — stated rather than guessed)
repo_at:        eltonaguiar/findtorontoevents_antigravity.ca : push/phase2-round-2026-11-22 @ 9ce382ebb5b (LOCAL ONLY, not on main — see §0)
ranked_list:    34_FINAL_PICKS_2026-11-23/GITHUB_COPILOT_DEEPSEEK/copilot.md (this file) + picks.json beside it
honest_headline: 0 of 10 classes are investable as an EDGE. Exactly one is actionable as a VEHICLE
                (broad-market index ETF, buy-and-hold); one is unresolved (FOREX, sign undetermined
                at -0.68bp); the other eight are DEAD, UNKNOWN, or REJECT for want of observations.
```

Paper only. Zero capital sanctioned. Not investment advice.

---

## §0 — Filing-location deviations, declared

1. **Subfolder, not flat file.** The folder README §1 prescribes one lowercase-slug file at the
   root (`copilot.md`). The operator instructed a subfolder identified as `GITHUB COPILOT_DEEPSEEK`.
   I followed the operator. A one-line pointer sits at `34_FINAL_PICKS_2026-11-23/copilot.md` so
   `STATUS.md` tooling can still resolve me, and it contains **no numbers** so it cannot drift.
2. **My source commits are not on main.** They are on `push/phase2-round-2026-11-22`, which carries
   81 commits from other desks, so I must not push it. The measurable content of this file is
   reproducible from paths in the upstream repo; the commits themselves are local-only and are
   named in §5 so they can be cherry-picked.

---

## §1 — Ranking criterion (stated before the ranking, as REQUIRED)

**Criterion:** distance-to-investable, i.e. (a) how many of the five admissibility questions in
`JUSTIFICATION_RULES.md` §A the class can actually answer, then (b) **risk-adjusted net return on
committed capital ranked on the 95% LOWER BOUND**, not the point estimate.

**Tie-breaks, named in advance:** (1) size of the margin over the 2× measured cost gate;
(2) turnover at measured cost; (3) deflated Sharpe at honest N.

**Why not just rank by net return:** every class's point estimate is a wide, mostly-noise interval.
Ranking on point estimates lets a lucky wide CI outrank a tight one. On the 95% lower bound there
is nothing to rank — which is the finding, not a failure of the ranking.

---

## §2 — Per-class table, all ten classes

House cost bands from `JUSTIFICATION_RULES.md` §C are used as the reference where I did not measure
the class myself. Where my own measurement disagrees with the house band, **both are shown** and the
disagreement is named in §4.

| CLASS | VERDICT | PICK | n | EDGE | DSR / N | PBO (vs 0.51) | COST | EXEC | KILL RULE | EVIDENCE |
|---|---|---|---|---|---|---|---|---|---|---|
| **ETF** | CANDIDATE | none (vehicle only: broad-market index ETF, buy-and-hold, no TP/SL) | 20 ETFs × 5y monthly | −0.40 bp/cycle net on breakout (4.70 gross − 5.10 cost); **buy-and-hold** pays cost once: 6.7122 bp/yr ⇒ ≈ −0.14%/yr drag at $25k | 0.3191 @ N=90; 0.9543 @ N=15 | **0.443** (better than noise) | measured 6.7122 bp RT (house band, 1-min upper bound) | BUY AND HOLD — 1 round trip/yr; turnover drag 0.99 bp/yr (lowest of all classes) | If realised net ≤ 4.32%/yr on committed capital **OR** beta-adjusted alpha CI contains 0 → do not trade it, only hold index | `reports/cost_of_record_2026-11-23.json`; `tools/etf_trend_forward_clock.py`; commit `cd44a8cab33` |
| **FOREX** | CANDIDATE | none — watch only, no position | 6 USD majors, 48 polls | −0.68 bp/trade at 4.98 bp cost of record; **−3.23 bp at 7.533 bp house band** | 0.0085 @ N=90 | 0.729 (worse than noise) | measured 7.533 bp RT (house, Tiingo top-of-book, thin Sunday reopen = UPPER BOUND); my cost of record 4.98 bp | ENTRY + TP/SL would be required for MR — turnover 7.6/yr × 7.533 = **56.93 bp/yr = 13.2% drag**, the highest of any class | If a weekday London/NY run prints RT ≥ 4.3038 bp → DEAD permanently; if < 4.3038 bp → re-open as CANDIDATE with a new prereg | `reports/fx_meanrev_cost_sweep/sweep.json`; `reports/cost_of_record_2026-11-23.json`; commit `0d7b1481966` |
| **STOCKS** | DEAD | none | 191 names / 238,810 daily + 356,271 1-min bars (cost); 186 names / 44 monthly rebalances (HML) | Breakout PF **0.9917** @ 25 bp/side. Value HML gross **+0.11%**, net **+0.02%**, SE 6.65%, 95% UB **+10.96%** vs 4.32% hurdle | 0.1139 @ N=90 | 0.600 (worse than noise) | measured 4.98 bp RT (my spread-only, **LOWER bound**) vs house 12.0749 bp — **disagreement, §4** | ENTRY + TP/SL; turnover 0.6/yr × 4.98 = 2.98 bp/yr | Already triggered. HML: net ≤ 4.32% or 95% UB ≤ 4.32% → KILL (fired). Breakout: PF CI-LB ≤ 1.0 → KILL (fired) | `docs/preregistration/HML_VALUE_TEST_2026-11-22.md`; commit `0b63ddb4b49` |
| **CRYPTO** | DEAD | none | 5 symbols, 4,235 intervals, 218 days (carry); 79 syms / 5y (risk) | Carry net **3.07%** (gross 3.57% − 0.50% cost) vs 4.32% hurdle | 0.0423 @ N=90 | 0.771 (worse than noise) | measured 20–52 bp band (house); 12.60 bp used in my turnover table | BUY AND HOLD would be 10.46 bp/yr (2.4%) but the drift is hostile: vol 68.5%, MDD **−87.8%** | net ≤ 4.32% on committed capital → KILL (fired). Also ledger integrity: 1,864 duplicate signal-ts groups | `reports/funding_carry_opportunity_frequency_20261122.json`; commit `0481cf081bc` |
| **BONDS** | UNKNOWN | none | 0 measured by me | UNMEASURED | 0.0006 @ N=90 | 0.614 (worse than noise) | **assumed** 42.64 bp RT / 94% fees — cited from another desk, **NOT reproduced by me** | BUY AND HOLD | If a reproduced round trip ≥ break-even → DEAD. No break-even of my own, so no kill rule I can defend | house note only; **no artifact of mine** |
| **COMMODITY** | DEAD | none | 40 obs (selection alpha) | PF **0.757 at ZERO cost** — fails with cost set to zero | 0.2423 @ N=90 | 0.586 (worse than noise) | **assumed** ~10 bp/side (house, explicitly not measured at size) | n/a — no viable strategy | cost-independent failure already fired | `reports/programme_scoreboard_20261122.json` |
| **MUTUAL_FUND** | DEAD | none | fee arithmetic only; n=0 for any strategy | Active MF **$18,520** vs index ETF **$1,050** per $100k/10yr = **17.6×**. Index MF $4,520 | n/a — no strategy, no DSR | n/a | measured (published expense ratios, not spread) | BUY AND HOLD only, and only the index variant | Any load or expense ratio > ~10 bp/yr → REJECT | `updates/2026-11-23-cost-of-record-reconciled.md` |
| **OPTIONS** | UNKNOWN | none | 0 | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | n/a | No kill rule possible without a cost | none |
| **PREDICTION_MARKET** | UNKNOWN | none | 0 | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED | n/a | No kill rule possible without a cost | none |
| **PRIVATE_CREDIT** | UNKNOWN | none | 0 | UNMEASURED — no data exists in the estate | UNMEASURED | UNMEASURED | UNMEASURED | n/a | n/a | none |

**Trial count used for every DSR above: N=90.** Declared honestly: the programme's trial count is
**disputed** — 120 (main-tree registry), 154 (all-lists distinct ids), 122 (ran+running), 362
(scored cells), 658 (symbols), ~25 (effective). N=90 is a mid-range figure, **not** a settled one.
Per README §5.3: if the operator cannot accept a ledger, the convention is `N unknown → deflated at
N=1000`; **nothing below survives at N=1000 either**, so the verdicts are robust to the choice.
Full reconciliation: `reports/TRIAL_N_RECONCILIATION_2026-11-23.md`.

---

## §3 — Per live class: why it ranks here / what would move it up / what would kill it

**ETF — rank 1 (criterion: fewest unanswered questions + tightest cost)**
- *Why here:* it is the only class where I have a measured cost (6.7122 bp), the lowest turnover drag
  (0.99 bp/yr), and a PBO **below** the 0.51 noise baseline (0.443). It answers Q1–Q5 only if you
  accept that the "mechanism" is **equity risk premium** and the "counterparty" is
  liquidity/patience-demanding sellers — i.e. it is **beta, not alpha**.
- *What would move it up:* a beta-adjusted Jensen-alpha CI excluding zero at net-of-measured-cost.
  Nothing in the estate has produced one.
- *What would kill it as a vehicle:* an expense ratio above ~10 bp/yr, or a rebalance rule that adds
  turnover at 6.7122 bp — which is exactly what a TP/SL execution style would do.

**FOREX — rank 2 (only genuinely open question in the programme)**
- *Why here:* the deciding number is a **cost**, not a signal. Gross 4.3038 bp against a claimed
  7.533 bp (upper bound) and my 4.98 bp (lower bound floor). The sign of net return is
  **undetermined** between those two, so declaring it DEAD would be an overclaim and declaring it
  ALIVE would be worse.
- *What would move it up:* one weekday London/NY top-of-book run. If RT < 4.3038 bp it becomes a
  live candidate; the 0 bp cost sweep already showed CI-LB +1.75.
- *What would kill it:* RT ≥ 4.3038 bp. Also turnover: mean-reversion needs TP/SL and pays 7.6×/yr.

**STOCKS — rank 3 (settled, and a settled NO has value)**
- *Why here:* it is dead in two independent ways and one is cost-robust — PF 0.9917 < 1 survives any
  cost reduction. Ranked above the other DEAD classes because the answer is *settled* rather than
  awaiting a measurement, and settled answers stop work being repeated.
- *What would move it up:* nothing on the current data axis. Only a **new** data axis (see
  `docs/BACKLOG_100_2026-11-23.md` items on options-implied skew, supplier graphs, borrow fees) with
  its own preregistration.
- *What would kill it further:* nothing — it is already dead.

---

## §4 — Unresolved disagreement I am flagging rather than smoothing over

**Direct-equity round trip: my 4.98 bp vs the house 12.0749 bp.**

- Mine: `tools/equity_cost_hml.py`, n=191 names, 238,810 daily + 356,271 one-minute bars;
  Corwin-Schultz median 0.77 bp (65/191 usable), Roll 4.77 bp (148/191). **Spread only** —
  commission/ECN/exchange fields are zero by construction, so **4.98 bp is a lower bound**.
- House: 12.0749 bp, described as a 1-min-bar upper bound, and its author states it is superseded
  for equity by the wider measurement.

These are a **floor and a ceiling**, not two estimates of the same thing. I used 4.98 bp for the
turnover arithmetic (favouring FOREX and EQUITY) and the house bands for the verdicts — so my
verdicts are **not** rescued by the lower number. That is deliberate: using the cheapest cost makes
kills *harder*, so a kill that survives it is stronger.

**Production default is neither of them.** `alpha_engine/backtest/engine.py:115` uses
`CostModel.interactive_brokers()` = **16.52 bp**, with 4 of 7 fields assumed and no cited source,
while the only measured model (`questrade_canada()`, 4.98 bp) has **zero call sites**. Five
verdict-grade costs span 4.98 → 50.00 bp (**10.04×**).

---

## §5 — How I tested this (harnesses, n, and what each one decides)

No result here is a scan hit. Every row traces to a committed tool with a stated n.

| Tool | What it decides | n | Result |
|---|---|---|---|
| `tools/equity_cost_hml.py` | EQUITY round trip | 191 names; 238,810 daily + 356,271 1-min bars | CS median 0.77 bp (65/191 usable), Roll 4.77 bp (148/191) ⇒ 4.98 bp **floor** |
| `tools/hml_pit_backtest.py` | value (HML) viability | 186 usable names, 44 monthly rebalances, turnover 14.8%/mo | gross +0.11%, net +0.02%, SE 6.65%, 95% UB +10.96% vs 4.32% ⇒ **KILL** |
| `tools/edgar_pit_fundamentals.py` + `tools/pit_lookahead_audit.py` | is the fundamentals backtest PIT-safe | **480 tickers, 32,049 periods, 30,332 usable** | median filing lag 35d, p10 25d, p90 54d; **0 exclusion + 0 visibility violations** |
| `tools/cross_class_momentum_backtest.py` | per-class momentum under identical entry criteria | 15-config grid × 6 instruments, IS 70% | best per class: ETF IS 0.98 / OOS 1.21; EQUITY 0.41/1.40; COMMODITY 1.29/0.63; CRYPTO 1.08/−1.05; FOREX 0.52/−0.87; BOND 0.14/−1.43 |
| `tools/quant_metrics_dsr_pbo.py` | deflation + overfit probability | N=15 per class and N=90 programme-level; CSCV 8 blocks, all 70 splits | ETF 0.9543@N15 → **0.3191@N90**; best PBO **0.443**; **0 of 6 survive** |
| `tools/paired_bootstrap_vs_benchmark.py` | is there alpha beyond beta | 13 unit tests | a **1.5× index fund passes a raw paired-difference hurdle** ⇒ hurdle replaced with Jensen alpha; zero-variance residual guard added |
| `tools/cost_of_record.py` | which cost is real | 5 costs in flight | 4.98 → 50.00 bp = **10.04×**; **no class flips** at the cost of record |
| `tools/trial_debt_audit.py` | the deflation denominator | 166 rows / 154 distinct / 19 lists / 7 registry copies | 94 ran, 28 running, 122 ran+running; registry copies hold **99–120** |
| `tools/etf_trend_forward_clock.py` | forward-only measurement (zero trial debt) | 20 ETFs, top-5 by 252d momentum, monthly | frozen from 2026-11-23; `n_records: 0` — a clock, **not** a claim |
| `tests/test_*` (6 suites) | that the above stay true | 8 + 13 + 13 + 10 + 8 + others | all passing as of `9ce382ebb5b` |

**What I did NOT test, stated plainly:** no live fills, no broker statements, no capacity coefficient
`k`, no options or prediction-market data, no private-credit data. Those are `UNMEASURED`, not zero.

---

## §6 — Top 3-5 picks (overall)

Ranked by the §1 criterion. **There is no 4th or 5th pick** — `JUSTIFICATION_RULES.md` §D says
"a pick that cannot be vetted is not ranked lower — it is not ranked", so padding to five would
violate the folder's own rule.

| # | Pick | Action | One-line justification |
|---|---|---|---|
| 1 | **Broad-market index ETF, buy and hold** (no TP/SL) | **TAKE — as a VEHICLE, not an edge** | Lowest measured cost (6.7122 bp), lowest turnover drag (0.99 bp/yr), only PBO below the 0.51 noise baseline (0.443). It is beta by construction and I say so: it fails G3 as a signal and passes only as a fee decision. |
| 2 | **FOREX mean-reversion, USD majors** | **HOLD FOR EVIDENCE — no position** | Only class whose sign is genuinely undetermined: −0.68 bp at my floor vs −3.23 bp at the house band. One weekday London/NY spread run decides it. Vetting item outstanding: measured cost within the 48-poll thin-book upper bound. |
| 3 | **Nothing in STOCKS / CRYPTO / BONDS / COMMODITY / OPTIONS / PREDICTION_MARKET / MUTUAL_FUND / PRIVATE_CREDIT** | **REJECT** | Each has a numeric killer in §2. Two are killed at **zero** cost (COMMODITY PF 0.757; CRYPTO carry 3.07% < 4.32%), which no cost assumption can rescue. |

**The honest headline: 1 actionable vehicle, 1 open question, 0 edges.** A list of five would be a
worse answer than a list of two plus a reason.

---

## §7 — Revision history

Revision 1 — 2026-11-23T03:05Z — initial filing.
