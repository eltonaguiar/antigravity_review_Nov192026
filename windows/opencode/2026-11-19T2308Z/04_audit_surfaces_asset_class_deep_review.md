# Deep review — findtorontoevents.ca `/audit`, `/audit2`, `/audit3` + per-asset-class methodology

**Author:** opencode (Windows seat `desktop-081g9oh/findtorontoevents_antigravity-ca`)
**Date:** 2026-11-19
**Live data:** `/audit` `money_ready_verdict.json` 18:47Z; `/audit3` ledger 18:32Z (source 16:05Z); `/audit` `db_health.json` 18:32Z; `intrabar_truth_by_class.json` 18:43Z; fund/ETF/crypto market data via Yahoo daily adj-close through 2026-11-19.
**Scope:** every visible section and metric on the three audit surfaces; the repo's backtesting/validation stack; per-asset-class picking methodologies; a concrete permutation/test plan; and a research method for cyclical/“skyrocket” questions.
**Not investment advice.** This is a review + test plan. Nothing here is a guarantee.

---

## 0. Executive findings (read this first)

1. **No surface currently has a money-ready pick.** `/audit` says **0/11 money-ready, WATCH=COMMODITY**. `/audit3` says **0 PROVEN, 0 strategy CANDIDATE, 59 WEAK, 8 KILL**. `/audit2` says **“Nothing here is money-ready.”** That is consistent and correct.
2. **The surfaces disagree on the same asset classes.** EQUITY is `+0.184%/trade, PF 1.089, n=939, WEAK` on `/audit3`, but `PF 0.602, n=115, NOT_READY` in `/audit` money-ready, and `WR 60.3%, PF 0.975, n=257, FAIL` in intrabar truth. That is a **denominator/policy/cost-model reconciliation bug**, not three independent opinions.
3. **The only credible future route is a forward-gated pod, not a hot cell.** `POD-EQUITY-BREAKOUT` is the only `pre_registered` pod. EQUITY is the only class with a positive point estimate in `/audit3` (still not significant; `required_n≈7,389`). But the pod is credited **0 forward rows** while `H-119` has **430** — a mapping gap. `H-119` fails the gate: PF CI-LB 0.921 (needs >1), IR 0.043 (needs ≥0.5), benchmark coverage 79.8% (needs ≥90%).
4. **CRYPTO is a proven loss at class level** (`/audit3` KILL: n=6,740, net −0.309%/trade, CI entirely below zero; policy-clean PF 0.234 on n=24,528). Do not size on the shiny crypto cells: `strong consensus SHORT` is n=24, WR 91.7%, PF **1,099** — a fixed-TP/data-artifact fingerprint, and it is WEAK.
5. **If the goal is “a professional manager, likely break-even or better,” the base-rate answer is low-cost diversified funds/ETFs, not the trading ledger.** S&P 500 10-year rolling windows since 1937: **88.8% positive**, median **7.5%/yr**, worst **−9.9%/yr**; but 2000–2009 was **−1.9%/yr**. Our fund sample is survivorship-biased.
6. **The best risk-adjusted “had to pick” ETF result is not stock-picking; it is cheap core + diversifiers + risk overlays.** In-sample: SPY 14.7% CAGR / 0.66 Sharpe / −33.7% MDD; 15% vol-target SPY 15.1% / 0.66 / −23.4%; 60 SPY/20 SCHD/20 DBMF 12.4% / 0.99 / −16.1%; 50 SPY/20 QQQ/15 SCHD/15 DBMF 13.8% / 1.01 / −17.5%. These are in-sample and must be walk-forwarded before belief.
7. **You can “predict” a new BTC ATH near the ATH; you cannot predict a +30% month from these technicals.** Logistic time-split: ATH-within-90d AUC 0.899 (mostly mechanical proximity), +30%-in-30d AUC **0.505** (base rate 4.9%, top-decile precision 7.3%). Current BTC state (2026-11-19): −49.7% from ATH, below 200d, RSI 21.6; the deep-drawdown quartile hit ATH within 90d only **9.7%** of the time historically.
8. **Fix the measurement layer before adding strategies.** 58.8% coverage on `/audit3`; 22,947 ghost rows; 94,606 open vs 21 active; cost models vary 4/10/15 bps; PBO reports 0.0 vs 0.82 vs threshold 0.55; class-level DSR uses `n_trials=1`. Any “money-ready” claim on top of that is not yet auditable.

---

## 1. What each surface actually is

| Surface | Purpose | Data source | What it is good at | What it cannot do |
|---|---|---|---|---|
| `/audit` | Unified operator dashboard (active/closed picks, leaderboard, ML, IC, theory, backtest-vs-forward) | `dashboard_data.json` (25 MB), `money_ready_verdict.json`, `pf_registry.json`, `intrabar_truth_by_class.json`, `db_health.json`, IC/theory sidecars | Breadth, live pick flow, data-health alarms, per-class policy verdicts | Not a single statistical model; mixes raw, policy-clean, intrabar, and legacy views |
| `/audit2` | Positive-side library: pods, forward clock, measures, traps, benchmarks | Same `../audit3/audit3_ledger.json`, `audit2_forward.json`, static `audit2.js` registry | Pre-registered pod watchlist, forward evidence clock, methodology literacy | `audit2_forward.json` has only `H-119` (`pods: []`); its own header says nothing is money-ready |
| `/audit3` | Quant kill tribunal: cells, symbols, segments, families, forward gate, evidence registry | One `audit3_ledger.json` from `alpha_engine/audit3_tribunal.py` | The only path to PROVEN/CANDIDATE; explicit gates; reproducible cell math | Single ledger; 58.8% coverage; 0 promotions today |

**Key structural fact:** `/audit2` renders the same ledger as `/audit3` (it tries `../audit3/audit3_ledger.json`). They are not two models. `/audit2` adds the pod/forward layer; `/audit3` owns the verdicts.

### 1.1 `/audit3` tabs and metrics (reviewed every tab)

| Tab | Metrics / content | Gaps found |
|---|---|---|
| Overview | KPIs (closed picks, share judged, tested, PROVEN, CANDIDATE, kills), per-class table with selection alpha, coverage table, G0–G9 gates | Denominator says 58.8% of book; excluded cohorts (integrity 5,933; auto-expired 9,257) overlap and their PnL is not exported; no per-class coverage split |
| Kill Tribunal | 8 KILL entries with n/WR/PF/net/mutation | Kill reasons include 8 “net expectancy CI below zero”; no economic harm model beyond expectancy; CRYPTO/COMMODITY class kills are large-n and credible |
| Strategy Cells | 359 cells; `q_value`, `dsr`, `dsr_local`, WR Wilson, net CI, reasons | 292 are INSUFFICIENT_N; only 66 DSR-scored; `dsr_local` currently changes no outcome; several WEAK cells have empty `reasons` (e.g., PF 1099 crypto cell) |
| Symbols | 359 symbol cells (n≥20) | 1 CANDIDATE: FOREX AUDJPY n=33, +0.64%, CI [0.24,0.94], q=0.136, DSR 0.901 — but 96% single-symbol concentration at the strategy level and class WEAK |
| Sections × Class | Reconstructed section proxies, positive CI first | Zero positive-CI segment at review time; every segment is capped at CANDIDATE; reconstruction is not the live gate |
| Source Families | BH/DSR/harm applied to name-based families | `mega_mutation` is the only 2×-cost-positive family (n=112, net +1.39%, CI [0.57,2.27], q=0.002) but DSR 0.487, 94% single source, no pod/class mapping; `copytrader` PF 0.386 |
| Evidence Registry | Backtests already in repo/DB; provenance, class mismatches, known gaps | Explicitly **evidence, not verdicts**; no trade log/price series for most; cannot promote |
| Hypotheses | 106 hypotheses, status taxonomy | Many spellings/canonical states; `open: []` despite 20 PRE_REGISTERED states — the tracker’s “open” view under-reports |
| Forward Evidence | 430 rows, fingerprint, pods, hypothesis clocks | Only H-119 has rows; `POD-EQUITY-BREAKOUT` shows 0; H-119 fails PF/IR/benchmark coverage |
| Method & Limits | One-sided tests, slippage, DSR, coverage caveats | Good; but no explicit reconciliation with `/audit` money-ready numbers |

### 1.2 `/audit2` sections (reviewed every section)

- **Doctrine:** public OHLCV is arbitraged; remaining edges are risk premia and microstructure/flow; volatility scaling is “free alpha.” Reasonable framing.
- **Verdicts:** same ledger; class table shows the mixed picture above.
- **Candidate & observe pods:** 1 `pre_registered` (EQUITY/ETF breakout), 5 `observe`, 2 declined/retired. This is the correct place to hunt future money-ready picks.
- **Forward evidence clock:** H-119 430 rows; benchmark leg 343 (80%); intrabar 430; status “accruing,” not gate-ready (needs benchmark ≥387).
- **Trial budget & benchmarks:** 67 tested / 359 total; 0 proven / 0 candidate / 59 weak / 8 kill.
- **Measures library / traps / retired:** good institutional memory; `CRYPTO SWING`, copy-trading, COT, fixed-TP milestones are already trapped.
- **Provenance:** source file is `/tmp/audit3/dashboard_data.json` (a build path, not a committed file) — a reproducibility gap the page itself flags.

### 1.3 `/audit` tabs/sections (reviewed every visible one)

Tabs: active, closed, dashboards, leaderboard, links, long-term, mlhealth, overview, performance, permutations, scoretracker, smartpicks, swing, ueps, verifiedalpha (+ aibattle/audit/bundles/portfolios/research/systems/warnings sections).
Metrics include: active/closed picks, risk/reward, TP-hit state, system leaderboard composite, backtest-vs-forward, score tracker, decile/IC analysis, ML health, theory tracker, DB health, permutations, per-class money-ready verdicts.

**Cross-surface contradictions to reconcile**

| Class | `/audit3` (cell ledger) | `/audit` money-ready | `/audit` intrabar truth | `pf_registry` policy-clean |
|---|---|---|---|---|
| EQUITY | +0.184%, PF 1.089, n=939, WEAK | PF 0.602, n=115, NOT_READY | WR 60.3%, PF 0.975, n=257, FAIL | PF 0.501, n=247 |
| CRYPTO | −0.309%, PF 0.838, n=6,740, KILL | PF 0.262, n=21,860, NOT_READY | WR 35.8%, PF 0.917, n=3,726, FAIL | PF 0.234, n=24,528 (single-source artifact flagged) |
| COMMODITY | −3.51%, PF 0.096, n=51, KILL | WATCH (n=28, PF 0.361; sizing PF 1.031) | WR 40.2%, PF 1.031, n=234, FAIL | PF 0.590, n=114 |
| ETF | +0.006%, PF 1.005, n=586, WEAK | INSUFFICIENT (n=29, PF 1.823; sizing PF 0.020) | not in file | PF 1.693, n=36 |
| FOREX | −0.024%, PF 0.920, n=258, WEAK | PF 0.257, n=456, NOT_READY | WR 31.5%, PF 0.640, n=634, FAIL | PF 0.344, n=490 |

These are not reconcilable by “different samples” alone. They differ by **row set** (canonical vs export slice vs policy-clean), **cost model** (4/10/15 bps), **win definition**, and **intrabar vs daily**. The review must pick one canonical denominator/cost/win definition and make every surface state it.

---

## 2. Data quality and coverage (the binding constraint)

From `/audit/data/db_health.json` (18:32Z):
- **22,947 ghost rows** in 10 MEMECOIN/meta_strategy cohorts (quarantined from canonical).
- **94,606 open rows vs 21 active** (`trading_picks` total 147,611) — tier red.
- **PnL integrity:** 130/24,158 sign mismatches (0.54%, green) but 6,535/24,158 naive magnitude mismatches (27.1%).
- `/audit3` coverage: **8,613 of 14,637** closed picks (58.8%); excluded: integrity 5,933, auto-expired 9,257 (overlapping).
- `/audit3` provenance: `/tmp/audit3/dashboard_data.json`, input sha, git sha — but a transient path.
- `pf_registry`: raw 33,637 → closed 27,733 → flicker-filtered 25,618 → deduped 25,477 → policy-clean 23,321; 2,156 policy-excluded; 10 impossible-winrate cohorts.
- IC analysis: 3,444 decisive picks, 118 strategies, **43 negative IC vs 35 positive**; CRYPTO 20 with IC, 5 positive/15 negative; FOREX 1/7 positive. Most strategies do not rank future returns.
- Class labels: `bt_backtest_runs.asset_class` all CRYPTO; EURUSDT filed as FOREX; 4 BOND strategies tagged CRYPTO (repo inventory). This contaminates every per-class aggregate.

**Verdict:** the ledger is not yet a clean measuring instrument. Fix coverage, ghosts, class labels, cost model, and one canonical denominator before adding strategies.

---

## 3. Per-asset-class deep research (data-backed where possible)

### 3.1 Mutual funds — the “professional manager, likely break-even” question

15-year daily data (Yahoo adj-close), annualized, risk-free = 13-week T-bill. **Survivorship-biased sample** (we chose funds that still exist and are well known).

| Fund | 15y CAGR | Vol | Sharpe | Sortino | MaxDD | Worst 12m | ER≈ |
|---|---:|---:|---:|---:|---:|---:|---:|
| FCNTX (Fidelity Contrafund) | 16.2% | 15.5% | 0.68 | 0.85 | −32.6% | −28.7% | 0.39% |
| VFIAX / FXAIX / SWPPX (S&P 500 index) | 14.9% | 14.3% | 0.66 | 0.83 | −33.8% | −24.8% | 0.015–0.04% |
| VTSAX (total US) | 14.5% | 14.5% | 0.63 | 0.80 | −35.0% | −26.4% | 0.04% |
| DODGX (Dodge & Cox Stock) | 13.8% | 15.2% | 0.59 | 0.75 | −40.4% | −33.7% | 0.51% |
| PRWCX (T. Rowe Price Capital Appreciation) | 11.8% | 9.3% | **0.74** | **0.96** | −26.9% | −19.8% | 0.70% |
| VFIFX (Vanguard Target 2050) | 11.0% | 12.2% | 0.55 | 0.74 | −31.4% | −24.6% | 0.08% |
| VWELX (Wellington) | 10.0% | 9.1% | 0.62 | 0.85 | −25.3% | −18.3% | 0.26% |
| VBIAX (Balanced Index 60/40) | 9.5% | 8.8% | 0.61 | 0.85 | −22.8% | −18.2% | 0.07% |
| VWINX (Wellesley Income) | 6.4% | 5.3% | 0.56 | 0.92 | −17.4% | −14.2% | 0.23% |

Rolling **10-year** windows (monthly, 61 overlapping windows, 2011–2026): every fund above was positive in 100% of windows and above 3%/yr in 100% — but that is the post-2011 US bull market. The S&P 500 since 1937: **88.8% of 10y windows positive, 11.2% negative, median 7.5%/yr, worst −9.9%/yr**; 2000–2009 was **−1.86%/yr**. So “likely break-even/profit over 10+ years” is historically true for diversified funds, but not guaranteed; the bad decades are real.

**If you had to pick (not advice):**
1. **Core (lowest cost, highest odds):** VFIAX/FXAIX/SWPPX or VTSAX; ETF equivalents VOO/VTI.
2. **Professional management with lower drawdown:** PRWCX (best Sharpe/Calmar in this sample) and VWELX; both are active/style bets, higher fees, manager risk.
3. **Set-and-forget balanced:** VBIAX (0.07% ER) or VFIFX (target date); VWINX for conservative income.
4. **Avoid as a “money-maker”:** long-duration bonds/TLT (0.1% CAGR, −48% MDD over 15y), commodity ETFs (DBC 1.7%, −64% MDD), sector concentration (XLE −71% MDD).

**Caveats:** survivorship, US bias, fees/taxes, 2022 bond drawdown, active funds’ capacity/closure, and the fact that a random fund can underperform its index for a decade.

### 3.2 ETFs — low-hanging fruit and what can actually be proven

| ETF | 15y CAGR | Vol | Sharpe | MaxDD | ER≈ | Note |
|---|---:|---:|---:|---:|---:|---|
| VOO / SPY / VTI | 14.7 / 14.7 / 14.4% | 14.2–14.5% | 0.66 / 0.66 / 0.63 | −34% | 0.03–0.09% | Core beta; cheapest at VOO/VTI |
| QQQ | 19.0% | 17.7% | 0.71 | −35.1% | 0.20% | Growth/tech concentration |
| SMH / SOXX | 27.0 / 25.4% | 25.8–26.9% | 0.74 / 0.69 | −45% | 0.35% | Highest return, highest drawdown; semis cycle |
| SCHD | 13.5% | 13.1% | 0.64 | −33.4% | 0.06% | Dividend quality, beta 0.80 |
| USMV | 11.7% | 11.4% | 0.62 | −33.1% | 0.15% | Low-vol, beta 0.71 |
| XLV | 14.0% | 13.8% | 0.64 | −28.4% | 0.08% | Defensive sector |
| DBMF | 9.3% | 10.3% | 0.38 | −20.4% | 0.85% | Managed futures, beta 0.12 — diversifier |
| GLD | 4.9% | 14.3% | 0.20 | −42.1% | 0.40% | Crisis hedge, not compounder |
| TLT | 0.1% | 12.3% | −0.07 | −48.4% | 0.15% | Duration risk |
| BND | 1.8% | 4.2% | −0.08 | −18.6% | 0.03% | Ballast, low return |

**Backtested overlays** (daily, signal lagged 1 day, 5 bps turnover):
- SPY: buy&hold 14.7% CAGR / 0.66 Sharpe / −33.7% MDD; **15% vol target** 15.1% / 0.66 / −23.4% (Calmar 0.64 vs 0.44); 200d trend 8.2% / 0.47 / −22.5%.
- QQQ: buy&hold 19.0% / 0.71 / −35.1%; vol target 18.0% / 0.73 / −27.0%; 200d trend 13.8% / 0.67 / −21.3%.
- Static monthly portfolios (5 bps): 60/40 SPY/BND 9.4% / 0.90 / −20.1%; 80/20 11.9% / 0.89 / −22.0%; 60 SPY/20 SCHD/20 DBMF 12.4% / **0.99** / −16.1%; 50 SPY/20 QQQ/15 SCHD/15 DBMF 13.8% / **1.01** / −17.5%.
- Sector 12-1 momentum top3: 12.9% / 0.87 / −18.1% vs SPY 14.4% / 0.92 / −23.9% (lower return, lower drawdown, Calmar 0.72 vs 0.60).

**Answer to “can it be proven?”** Yes for a *rule* (trend/vol target/diversified static portfolio) if you use walk-forward + purged CV + costs + multiple-testing correction. No for “this ETF will beat the market” from a survivor list; that is selection bias. The honest low-hanging fruit is **cheap core + diversifiers + risk management**, not sector calls.

**If you had to pick (not advice):** VOO/VTI as core; QQQ or SMH only as a sized satellite (drawdowns −35%/−45%); SCHD/USMV as lower-beta equity; DBMF as a diversifier; BND/SHY as ballast, not return. A 60/20/20 or 50/20/15/15 mix above is the kind of thing to paper-forward, not to assume.

### 3.3 EQUITY (stocks) — the only positive class on `/audit3`, still not money-ready

- `/audit3`: n=939, net +0.184%, CI [−0.395, +0.747], PF 1.089, DSR 0.016, `required_n≈7,389`, WEAK. Alpha −0.008% (CI [−0.361,+0.338]), i.e., no selection skill vs holding.
- Confirmatory cell `vol-contraction-scout` (n=62): alpha CI-LB +0.1745 (proven), but split-half +1.76 → −0.48, last-25% −0.79 → WEAK.
- Intrabar truth: n=257, WR 60.3%, PF 0.975, avg −0.03% → FAIL (high win rate, no expectancy).
- Pod: `POD-EQUITY-BREAKOUT` pre_registered; forward rows 0 (mapping issue); H-119 forward 430 rows, PF 1.115, IR 0.043, benchmark coverage 80%.
- **Method:** PEAD/earnings drift, 52-week breakout, RS breakout, gap-and-go, vol contraction; value/quality screens (`value_screener_runner.py`, `growth_stock_screener.py`, `equity_pead_strategy.py`). Data gaps: fundamentals/earnings frozen ~2026-04-27; delisted list static; daily_prices freshness conflicts.
- **What to test next:** breakout + volume confirmation (RVOL≥1.5, volume z-score), PEAD with earnings-surprise sign, value+quality with 12-1 momentum, sector-neutral construction; exact tests in §6.

### 3.4 CRYPTO — proven loss as a class; “skyrocket” is not forecastable from technicals

- `/audit3` class KILL: n=6,740, net −0.309%, CI [−0.570,−0.046], PF 0.838. `/audit` policy-clean: n=21,860, PF 0.262, expectancy −5.7%, top source 99.7%, MDD 100%, CVaR −94.9. Intrabar: n=3,726, WR 35.8%, PF 0.917, FAIL.
- Best-looking cell: `strong consensus SHORT` n=24, WR 91.7%, PF 1,099, q=0.015, DSR 0.9998 — WEAK, alpha unproven, class proxy. PF 1,099 is a **label/exit artifact** (fixed TP, tiny losses), not evidence.
- `crypto_rsi5070_us` forward: n=431, net PF 1.119, net CI-LB 0.916 (<1), WR 42.7%, status SHADOW_TRACKING, not promotable.
- **BTC event study (2014–2026, daily):**
  - Base rates: new ATH within 90d **35.1%**; +30% in 30d **12.4%**; P(fwd30>0) **56.7%**.
  - ATH-within-90d by drawdown quartile: −83…−55% → **0%**; −55…−38% → **9.7%**; −38…−12% → **50.9%**; −12…0% → **79.9%** (mechanical).
  - Logistic time-split (train <2022, test ≥2022): ATH90 AUC **0.899**, top-decile precision **87.1%** vs base 27.8% (mostly proximity, not alpha); +30%/30d AUC **0.505**, top-decile precision **7.3%** vs base 4.9% (no real edge).
  - Halving phases (overlapping daily obs): 0–6m +41% mean, 6–12m +48%, 12–24m +10%, 24m+ +17% — n=4 halvings; treat as narrative, not a signal.
  - Current state 2026-11-19: **−49.7% from ATH, below 200d, RSI 21.6, 30d vol 36%, 30d return −24%, 90d −20%**. Bootstrap fwd90: P(>0)=59%, median +8.7%, p10 −27%, p90 +83%; but deep-drawdown ATH probability is ~9.7%.
- **What people actually use to “reverse engineer” a sky move:** on-chain (MVRV, SOPR, NUPL, realized cap, exchange netflow), derivatives (funding, OI, basis, liquidations), ETF/fund flows, stablecoin supply, macro liquidity, halving supply, and trend/volume regime. None of these are in the repo ledger; all require point-in-time data and event studies, and none is a reliable point predictor. Use probabilistic scenarios + risk sizing.

### 3.5 FOREX — blocked, data-broken, one thin CANDIDATE

- `/audit3`: n=258, net −0.024%, PF 0.920, WEAK; `/audit`: PF 0.257, n=456, NOT_READY; intrabar n=634, WR 31.5%, PF 0.64, FAIL.
- `fx_prices` ends **2026-02-09**; symbol naming mismatch (`AUDCAD` vs `AUDJPY=X`/`AUD-USD`) → 211 picks unmeasurable (repo inventory). Bar coverage now shows FOREX last bar 2026-11-18, 12/17 symbols (backfill partly landed; verify).
- Only CANDIDATE symbol: **AUDJPY LONG** n=33, +0.64%, CI [0.242,0.941], q=0.136, DSR 0.901, but 96% single-symbol at the strategy level and class WEAK. Paper only.

### 3.6 COMMODITY — WATCH vs KILL; COT was falsified

- `/audit3` KILL: n=51, net −3.51%, PF 0.096. `/audit` says WATCH (n=28, PF 0.361, sizing PF 1.031) — **reconcile before trusting either**.
- Repo history: COT `DSR=1.0` was **falsified** (6.33× over-emission: 38 signals from 6 unique CFTC weeks); dedup pilot WR 33.3% on n=6; COT needs a 3-day publication lag and dedup.
- Bar coverage: 8/9 symbols priced; last bar 2026-11-19. Only 51 class rows; WF fold sizes 10/5/3 — statistically thin.
- **Method:** term-structure carry/roll yield, COT positioning (lagged/deduped), seasonality (crop/inventory), gold/silver ratio. Test with event-time and commodity-specific costs (6 bps one-way) before any class claim.

### 3.7 BOND — ballast, not a return engine

- BND/AGG 15y: 1.8–1.9% CAGR, −18% MDD, negative Sharpe; TLT 0.1%, −48% MDD. `/audit` BOND INSUFFICIENT (n=2 policy-clean); repo has 3/2/1 WF folds (meaningless).
- The only honest use is duration ballast / crisis hedge; a 60/40 or 80/20 mix is a base-rate portfolio, not alpha.
- Data gaps: dedicated bond DB unreadable (1045), backup snapshots stale, 4 bond strategies mis-tagged CRYPTO.

### 3.8 FUTURES — thin, but trend/CTA is a real diversifier

- `/audit` FUTURES INSUFFICIENT (n=17); `/audit3` n=4. Repo: 12 closed picks, 91.7% single-source; WF folds tiny; yfinance `=F` contracts + COT.
- Public proxies: DBMF 9.3% CAGR, 0.38 Sharpe, −20.4% MDD, beta 0.12; KMLM 6.1%, 0.14, −31%. Trend following is a legitimate diversifier, not a high-Sharpe standalone.
- Test: TSMOM across ES/NQ/YM/ZN/GC/CL with vol targeting, roll costs, 1-day lag, 12-1 momentum; expect modest Sharpe and crisis convexity.

### 3.9 Prediction markets and copytrading — shadow only

- PM: no dedicated DB table; Kalshi snapshot ~7 months stale; PBO 0.603; only n=1 resolved; PnL derived from spot-proxy TP/SL, not contract payoff. Keep shadow until binary payoff is modeled on contract prices.
- Copytrading: 74/87 feeds silent >48h; family PF 0.386 (n=86); dead sources (MyFXBook 66d, Binance/Bitget 67d). The bottleneck is freshness/verification, not source count.

---

## 4. Backtesting/validation stack — what exists and what is missing

**Canonical docs:** `TESTING_PROTOCOL.MD` (5 hard gates, 10-step admissibility), `docs/TESTING_PROTOCOL_SUMMARY.md` (8 layers), `docs/BACKTEST_ADMISSIBILITY_STANDARD.md` (Stage 0–6), `docs/STRATEGY_VALIDATION_GATES.md`, `docs/PERFORMANCE_CHARTER.md`, `docs/PAPER_PILOT_HARNESS.md`, `docs/PROVEN_TIER_VALIDATION_PROTOCOL.md`.

**Code:** walk-forward (`alpha_engine/validation/walk_forward.py`, `walkforward_validator.py`, `walk_forward_backtester.py`), purged K-fold/embargo (`validation/purged_cv.py`, `rigorous_backtest_harness.purged_walkforward`), CPCV/PBO (`anti_overfit_validator.cpcv_pbo`, `tools/pbo_cscv.py`, `tools/cpcv_overfit_detector.py`), Monte Carlo/bootstrap (`validation/monte_carlo.py`, `benchmark_closed_ledger.py`, `monte_carlo_validator.py`), DSR/multiple testing (`validation/statistical_gates.py`, `validation/promotion_gate.py`, `deflated_sharpe.py`), intrabar first-touch (`intrabar_resolver.py`), costs (`charter_slippage.py`, `backtest/costs.py`, `transaction_costs.py`), and tests pinning these.

**Top gaps (from the repo inventory + live review):**
1. **PBO contradictions:** docs PBO≤0.05; `money_ready_verdict.py` PBO_THRESHOLD=0.55; `tools/cpcv_pbo_results.json` global PBO **0.8222**; `anti_overfit_audit.json` **0.0**. Pick one canonical implementation and threshold.
2. **Class-level DSR undeflated:** `_dsr_gate()` uses `nb_trials=1`; only `rigorous_backtest_harness` uses the true N. This inflates class DSR.
3. **Cost model fragmentation:** CRYPTO 4 bps (`charter_slippage`), 10 bps (admissibility doc), 15 bps (`money_ready_verdict`), 10+5 bps (rigorous harness). PF/verdict flips by importer.
4. **Intrabar not universal:** daily close-only engine with 90-day max hold; same-bar ties stop-first; large historical rows lack `intrabar_first_touch`.
5. **Synthetic/stub fallbacks:** `_load_from_json()` synthesizes picks; `p3_backtest_runner._stub_metrics()` returns pseudo-metrics; `evaluate_strategy()` synthesizes peers; `monte_carlo_edge_audit.py` is deprecated winsorized (2–5× PF inflation).
6. **No direct tests for validation package:** no test imports `validation.walk_forward`, `purged_cv`, `monte_carlo`, `statistical_gates`, `institutional_backtest_suite`, `promotion_gate`.
7. **Look-ahead/survivorship:** static delisted list only; current-symbol universes; COT lag handled, generic next-bar lag not.
8. **Class-label contamination:** `bt_backtest_runs.asset_class` all CRYPTO; EURUSDT as FOREX; 4 BOND strategies as CRYPTO.
9. **Forward coverage:** only H-119; pod mapping gap; benchmark coverage 80%.
10. **Reproducibility:** `/audit3` source file under `/tmp`; paper-pilot harness sourced from `/tmp/strategy_builds_2026-05-31/` (absent).

---

## 5. A proper methodology to find money-ready picks (apply to every class)

**Stage 0 — Universe and data (point-in-time).** Include delisted/closed instruments; adjusted prices; corporate actions; borrow/funding; no current-universe survivorship. One canonical denominator per surface. Precompute costs per class.

**Stage 1 — Hypothesis pre-registration.** Write the rule, universe, entry/exit, sizing, costs, sample window, and the exact failure threshold before looking. One hypothesis per test; log it (`tools/experiment_log.py`).

**Stage 2 — Signal hygiene.** Use only information available at decision time; lag by one bar; normalize by ATR/vol; avoid fixed-TP labels; handle same-bar TP/SL with intrabar first-touch (stop-first).

**Stage 3 — Base rates first.** Compute the unconditional probability of the target event (win, +X%, ATH, drawdown) before any model. If the base rate is good enough, you may not need a model. Report n_eff (distinct days/symbols), not just n.

**Stage 4 — Event study / conditional edges.** Bucket by regime, trend, vol, volume, funding, on-chain, earnings; report conditional probabilities, lift over base, Wilson CI, and calibration. Time-split (train/valid/test) or purged CV; never random K-fold on time series.

**Stage 5 — Walk-forward + purged CV/embargo.** Expanding or rolling windows, purge/embargo, report IS vs OOS, WF efficiency, % windows positive. Minimum OOS trades per class (EQUITY≥100, CRYPTO≥100, ETF≥50, FOREX≥30, BOND/FUTURES≥20, etc.).

**Stage 6 — Costs and stress.** Net of class slippage/fees/funding; 2× and 3× cost stress; capacity and concentration caps (symbol ≤60%, source ≤90% for a cell; tighter for a portfolio).

**Stage 7 — Multiplicity.** BH FDR across all tested cells; DSR with the **trial count actually searched** (not 1, not the slice); PBO/CSCV with a documented implementation; SPA/Reality Check. Pre-register the family.

**Stage 8 — Portfolio construction.** Vol targeting, inverse-vol or risk parity, correlation caps, max position, rebalance frequency; measure turnover and tax/cost drag. A high-Sharpe single asset is not a portfolio.

**Stage 9 — Forward/paper.** Forward rows after registration only; intrabar-true; n≥100 (or class floor); PF CI-LB>1 after 2× costs; IR≥0.5 vs matched benchmark; concentration caps; 2 consecutive runs/persistence.

**Stage 10 — Decision and monitoring.** Small real-money pilot only after 9; define kill/demote triggers (churn, drawdown, source death, regime break); review monthly; retire with reason.

**Apply to the current system:** the fastest legitimate path is EQUITY via `POD-EQUITY-BREAKOUT` (fix mapping, pass the forward gate, stabilize split-half), not a new hot cell. For mutual funds/ETFs, the “edge” is cost/diversification/behavior, not alpha; use the base-rate portfolio and risk overlays, and prove the rules with walk-forward.

---

## 6. Permutation / configuration experiments (explicit test plan)

Pre-register each grid; report all trials; use nested walk-forward; net of 2× class costs; require OOS + PBO/DSR. Do not optimize on the full sample.

| Experiment | Variants | Primary metric | Acceptance (paper) | Where |
|---|---|---|---|---|
| TP/SL geometry | ATR stop 0.5/1/1.5/2×; RR 1/1.5/2/3; trailing vs fixed; time stop 1/5/10/20d | Net expectancy CI-LB, PF, MDD, turnover | OOS CI-LB>0 at 2× cost; PBO<0.2; n≥100 | `tpsl_policy.py`, `tp_sl_optimizer.py`, `backtest_swarm_param_robustness.py` |
| Volume confirmation | RVOL 1.0/1.5/2.0; volume z-score 0/0.5/1; dollar-volume floor; OBV divergence | Incremental IC, net PF, hit rate, trade count | Adds OOS net PF without n collapse; survives 2× cost | `features/volume.py`, strategy `vol_mult` params |
| Entry lag | 0/1/2 bars; next-open vs next-close | Net PF, slippage sensitivity | Edge survives 1-bar lag; if not, it is leakage | custom harness (no generic knob today) |
| Session/time | all hours; US/EU/Asia; first/last hour; day-of-week | Net expectancy by bucket | Bucket edge stable across halves; no single-hour dependence | `btc_hour_filter.py`, `session_breakout.py` |
| Vol targeting | 10/15/20% target; 20/60d vol; cap 1.0/1.5/2.0 | Sharpe, Calmar, MDD | Improves Calmar without OOS Sharpe collapse | `risk/vol_target.py`, `vol_target_sizer.py` |
| Holding period | 1/5/10/20/60d; monthly rebalance | CAGR, turnover, net Sharpe | Net of costs; no single-period dependence | `hold_duration_optimizer.py` |
| Cost stress | 1×/2×/3×/5× slippage; funding; borrow | Net PF, break-even cost | Positive at 2×; report break-even bps | `slippage_stress_test.py` |
| Portfolio weights | equal / inverse-vol / risk parity / momentum top-N | Sharpe, MDD, turnover, concentration | OOS Calmar improvement; caps respected | `tools/parameter_sweep.py`, `incubator/permutation_engine.py` |
| Class universe | current vs PIT delisted-inclusive | Return/Sharpe delta | Report survivorship delta; use PIT for decisions | needs delisted data |

**Volume specifically:** test it as a *filter* and as a *feature*: (a) require prior-bar RVOL≥1.5, (b) continuous volume z-score, (c) dollar-volume floor for liquidity. Measure incremental IC and net PF after costs; avoid using same-bar volume (look-ahead). For crypto, use exchange volume (wash-trading risk) and prefer perp funding/OI as confirmation.

**TP/SL caution:** fixed-TP “milestones” manufacture high WR (the PF 1,099 cell is the canonical warning). Always resolve intrabar first-touch with stop-first ties; report expectancy, not WR.

---

## 7. Cyclical patterns and “before a skyrocket” research

**What is testable:** seasonality (monthly), halving/event phases, sector rotation, commodity carry/seasonality, earnings/PEAD cycles. **What is not:** a reliable point prediction of an ATH or a +30% month from public technicals.

Evidence from this review:
- SPY monthly (15y): Jul +2.84% (93% hit), Nov +3.00% (87%), Sep −0.72%; n=15, overlapping → weak; test with block bootstrap/permutation.
- BTC monthly (12–13y): Oct +14.8%, Feb/Apr +10.2%, Jul +8.9%; n small; not a standalone edge.
- BTC halving phases: 0–6m +41%, 6–12m +48%, 12–24m +10%, 24m+ +17%; n=4 events, overlapping daily observations → narrative, not proof.
- BTC ATH-within-90d is mechanically driven by distance from ATH (AUC 0.899), not a “skyrocket” signal; +30%/30d is not predictable from these features (AUC 0.505).
- Sector 12-1 momentum: lower return, lower drawdown than SPY (12.9% vs 14.4%, −18.1% vs −23.9%); a risk-management overlay, not alpha.

**Method for crypto “skyrocket” questions:**
1. Define the event precisely (new ATH within 90d; +30% in 30d; +50% in 90d; drawdown recovery).
2. Compute the base rate and n_eff (distinct days); report Wilson CI.
3. Build point-in-time features: distance from ATH, 200d trend, realized vol, volume z-score, funding/OI, MVRV/SOPR/NUPL, exchange netflow, ETF flows, stablecoin supply, macro liquidity.
4. Time-split/event-time evaluation; calibrate probabilities; report lift, AUC, Brier, precision@top-decile vs base.
5. Economic backtest: enter/exit rules, costs (16 bps round-trip as the repo uses), slippage, funding, sizing; 2× stress.
6. Paper/forward only; no real money until the forward gate passes.

**Current BTC read (2026-11-19):** deeply drawn down (−49.7% from ATH), below 200d, RSI 21.6, 30d vol 36%; historically the deepest drawdown quartile hit ATH within 90d **0–9.7%** of the time. Unconditional bootstrap fwd90 P(>0)=59%, median +8.7%, p10 −27%. That is a distribution, not a prediction.

---

## 8. Concrete recommendations

**Immediate (P0):**
1. Reconcile EQUITY/CRYPTO/COMMODITY/ETF numbers across `/audit`, `/audit2`, `/audit3` with one canonical denominator, cost model, win definition, and intrabar rule. Publish the reconciliation table.
2. Fix `POD-EQUITY-BREAKOUT` ↔ H-119 mapping; report the 430 forward rows to the pod; re-run the forward gate.
3. Make intrabar truth the sizing source or explicitly label daily-close results as non-sizing.
4. Fix PBO/DSR consistency: one implementation, one threshold, class-level trial count >1.
5. Fix data: 22,947 ghosts, 94,606 open bloat, class-label contamination, `/tmp` provenance.

**Research (P1):**
6. Pre-register and run the TP/SL × volume × entry-lag grid on EQUITY breakout + PEAD and on the best crypto conditional cohort; report all trials.
7. Run a PIT, delisted-inclusive ETF/fund study; separate beta from selection alpha.
8. Build a crypto event-study pipeline with on-chain/funding/flows; treat ATH as a probability, not a forecast.
9. Paper-forward the 60/20/20 and 50/20/15/15 ETF mixes and the SPY/QQQ vol-target overlays with costs; compare to buy&hold OOS.

**Do not:**
- Do not size on the PF 1,099 crypto cell, the 430-row H-119 cohort before it passes, the 33-row AUDJPY CANDIDATE, or any class-level aggregate without reconciled data.
- Do not quote mutual-fund/ETF 15y returns as expected future returns; survivorship and the 2011–2026 US bull market dominate.

**What would change the answer:** H-119 forward gate passes (PF CI-LB>1, IR≥0.5, benchmark≥90%) on 2 consecutive runs; EQUITY split-half/recency stabilizes; coverage >80% with reconciled costs; then a small EQUITY paper pilot, and only later real money.

---

## 9. Questions for other agents (critique request)

1. Are the cross-surface class differences fully explained by row-set/cost/win-definition, or is one surface wrong? Show the reconciliation.
2. Is `GLOBAL_TRIAL_FLOOR=658` the right multiplicity floor for every class, or should it be family/class-specific? Is class-level DSR with `n_trials=1` acceptable?
3. Which PBO implementation is canonical (timeseriescv CPCV, CSCV, block-bootstrap, synthetic perturbations)? What threshold — 0.05, 0.2, 0.55 — and why do the artifacts report 0.0 and 0.82?
4. Should intrabar truth be the only sizing source? How should rows missing intrabar be handled — excluded, down-weighted, or flagged?
5. Which asset class deserves the first forward pilot, and what is the falsification criterion? (Current vote: EQUITY via POD-EQUITY-BREAKOUT; CRYPTO is a class-level KILL.)
6. Is the proposed TP/SL × volume × entry-lag grid pre-registered enough? What confounders (regime, symbol mix, source) must be controlled?
7. How do we obtain point-in-time delisted data and on-chain/funding data without look-ahead? What is the minimum viable dataset for a credible crypto event study?
8. What evidence would make you put real money into EQUITY, and what would make you kill the pod?

---

## Appendix A — Reproduction commands

```powershell
# live ledger + audit data
Invoke-WebRequest https://findtorontoevents.ca/audit3/audit3_ledger.json -OutFile audit3_ledger.json
Invoke-WebRequest https://findtorontoevents.ca/audit/data/money_ready_verdict.json -OutFile money_ready_verdict.json
Invoke-WebRequest https://findtorontoevents.ca/audit/data/intrabar_truth_by_class.json -OutFile intrabar_truth_by_class.json
Invoke-WebRequest https://findtorontoevents.ca/audit/data/pf_registry.json -OutFile pf_registry.json
Invoke-WebRequest https://findtorontoevents.ca/audit/data/db_health.json -OutFile db_health.json
Invoke-WebRequest https://findtorontoevents.ca/audit/data/strategy_ic_analysis.json -OutFile strategy_ic_analysis.json
# funds/ETFs/crypto: Yahoo daily adj-close via yfinance, 15y, metrics in the review script
```

## Appendix B — Key numbers (one screen)

- `/audit`: **0/11 money-ready**, WATCH COMMODITY; db health 22,947 ghosts, 94,606 open vs 21 active, tier red.
- `/audit3`: **0 PROVEN / 0 strategy CANDIDATE / 59 WEAK / 8 KILL**; 359 cells; 58.8% coverage; 430 forward rows; H-119 PF CI-LB 0.921, IR 0.043, benchmark 79.8%; EQUITY +0.184% PF 1.089 n=939 (required_n 7,389); CRYPTO KILL n=6,740.
- Funds (15y): FCNTX 16.2% / 0.68; VFIAX 14.9% / 0.66; PRWCX 11.8% / **0.74**; VWELX 10.0% / 0.62; VBIAX 9.5% / 0.61; VWINX 6.4% / 0.56.
- ETFs (15y): VOO 14.7% / 0.66; QQQ 19.0% / 0.71; SMH 27.0% / 0.74; SCHD 13.5% / 0.64; DBMF 9.3% / 0.38 (beta 0.12).
- Overlays: SPY vol-target 15.1% / 0.66 / −23.4% MDD; QQQ vol-target 18.0% / 0.73 / −27.0%; 60 SPY/20 SCHD/20 DBMF 12.4% / 0.99 / −16.1%.
- S&P 500 10y windows since 1937: 88.8% positive, median 7.5%/yr, worst −9.9%/yr; 2000–2009 −1.86%/yr.
- BTC: 35.1% ATH-within-90d base; +30%/30d 12.4%; ATH AUC 0.899 (mechanical), +30% AUC 0.505; current −49.7% from ATH, below 200d, RSI 21.6.
