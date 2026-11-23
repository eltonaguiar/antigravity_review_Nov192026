# Reverse-engineering daily/weekly top gainers — the four answers, and what the numbers say

**Question put to four agents (2026-11-23):**
> If you were tasked to reverse engineer the daily or weekly top gainers for stocks, crypto, mutual funds etc, how would
> you go about? i.e. you want to be able to give signals including a TP/SL for stocks/crypto, maybe forex, and determine
> first of all which asset class is more predictable. Is a particular "symbol" more predictable, or a symbol and a
> direction like long vs short? What is "proven" — would you backtest, and how can you forward-test, and which metrics
> would you need to measure?

**Answers harvested:** 1min.ai · arena.ai · AskAnyModel · ChatPlayground. Raw text in this folder
(`harvest_1min.txt`, `harvest_arena.txt`, `harvest_askanymodel.txt`, `harvest_chatplayground.txt`).

**Status:** arena.ai was still writing code at harvest time (`gainers_research/src/…`, a `Trade` dataclass with
`entry / exit / reason ∈ {tp, sl, time} / r / bars`). Its prose answer was captured; its code was not. Re-harvest before
citing it.

---

## 1. The one structural distinction all four converged on

**Predictability is not tradability.** Two of the four stated it, and **GPT-6.1 Terra (OpenAI, via AskAnyModel) put it
best** — as a three-rung ladder where each rung is strictly harder than the last:

> *"1. **Explaining winners after the fact:** what characteristics did past top gainers share?
> 2. **Predicting candidates in advance:** did those characteristics identify assets before they became winners?
> 3. **Trading profitably:** could you capture enough of the move, after costs and losses, with a feasible entry,
> take-profit and stop-loss?*
> *Those are progressively harder tests. A pattern can succeed at the first and fail at the other two."*

Arena stated the same split as a pair — *"separate 'predictability' (statistical) from 'tradability' (after costs,
capacity, slippage)"* — and added the search-space decomposition in §3.1. Terra's version is better because **"explaining"
is the failure mode we actually catch agents in**: a row that describes why last month's winners won, dressed as a
forecast.

A class can be highly predictable and lose money, or unpredictable and make money. Both happen in our own measurements:

| Case | Predictability | Profitability | Why |
|---|---|---|---|
| **FX carry** | High — the mechanism is a published rate differential, known in advance, no modelling needed | **Sharpe −0.126 vs the 4.32% hurdle**, break-even 468.47 bp vs a 7.53 bp cost | You are short crash risk. The forecast is right and the payoff is negative. |
| **Index ETF** | Near-zero daily — genuinely close to a coin flip | **Positive over decades**, 6.7122 bp/yr of cost, turnover drag 0.99 bp/yr | You are not forecasting. You are collecting beta and paying almost nothing. |

**So the ranking metric cannot be accuracy.** It has to be **net expectancy per unit of cost**, with predictability as a
*screen* rather than the goal. Any answer that ranks classes by hit rate is measuring the wrong thing.

---

## 2. Which asset class is more predictable — the honest position

We cannot rank predictability from our own estate, and saying so is the finding: predictability requires a
**timestamped forecast archive**, and we have none. Every number we hold is a *realised* performance of a strategy, which
conflates forecast quality with cost, capacity and luck.

What we can say, in order of confidence:

1. **Volatility is far more predictable than direction.** AskAnyModel said it plainly — *"Volatility is much more
   predictable than direction. This matters a lot for setting TP/SL."* This is the single most actionable line in the four
   answers, and it is correct in the literature (vol clusters; direction does not). **It reframes the task:** a TP/SL
   engine should be built on a vol forecast — which is achievable — and not on a direction forecast, which mostly is not.
2. **Horizon dominates class.** Our own cost-horizon ladder: monthly rebalancing **+24.21 bp** vs 15-minute **−0.57 bp**.
   Nothing about which asset you pick changes the sign as decisively as how often you trade it.
3. **Literature prior, haircut before use:** the strongest documented replication is cross-sectional momentum at
   weeks-to-months across stocks, crypto and commodities; short-term reversal at days-to-one-month, strongest in equities;
   time-series momentum in futures/FX/crypto. Per McLean–Pontiff, **haircut 30–60% before testing** — post-publication
   returns fall by roughly half.
4. **Measured performance of the classes we have:** bond ETF PF ≈ 1.00 (no edge), equity breakout PF 0.9917 @25 bp/side
   (no edge), FX carry Sharpe −0.126, crypto carry ≈ a T-bill. **Not one class shows a live edge at our measured cost.**

**Verdict: the question "which class is most predictable" has no admissible answer in this estate yet.** What it has is a
testable *prior* (monthly momentum, vol over direction) and a measurement gap that the base-rate-first protocol closes.

---

## 3. Symbol, or symbol × direction — the decomposition that matters

Arena decomposed the search space correctly: **class → symbol → symbol × direction**. Three facts from our own data:

- **Class-level has the sample size.** Aggregated across a class you can reach n in the hundreds or thousands.
- **Symbol-level does not, at our scale.** Our best per-name rows: CVX n=35, AAPL n=81, SOXL-family n=37–64. Deflated at an
  honest trial count, every one of those collapses (DSR 0.106–0.328 against a 0.95 gate). **Per-symbol ranking at n < 100
  is noise dressed as insight.** This is exactly why Kilo's 69 picks produced 0 passes.
- **Symbol × direction is not symmetric, by construction.** The long side inherits the equity risk premium — a real
  positive drift you get for free. The short side pays borrow, faces locate failures, and carries negative skew. So a
  symmetric model that predicts "up or down" is modelling two different economic problems as one.

**Recommendation:** test **long and short separately, never pooled**, and report the directional asymmetry. AskAnyModel's
observation that mutual funds are a poor fit for TP/SL belongs here too — daily pricing, no intraday stop, redemption
fees. **ETFs are the tradable equivalent of a mutual fund**, and that substitution alone removes the wrapper problem.

### 3.1 Arena's hierarchy — and the number that kills naive symbol-level search

Arena (round 2) nested the search space explicitly: **asset class → symbol → symbol × direction →
symbol × direction × regime/horizon**, and then did the arithmetic that we had only asserted qualitatively:

> *"With 5000 stocks × 2 directions × 5 horizons = 50,000 tests; at α=0.05 you get 2,500 false positives."*

That is the mechanism behind our per-symbol DSR collapse, stated as a count. At α=0.05 there are **2,500 "discoveries"**
in that grid that are pure noise, which is why deflation must use the *effective* trial count and why symbol-level
finders look extraordinary until they are deflated. Arena's escape route is the correct one: **nested/hierarchical
modelling with shrinkage**, not independent per-symbol searches.

It also implemented the split that prevents label leakage, and named the parameters:
`purged_walk_forward(panel, n_folds=5, embargo=10, horizon=5)` — a chronological walk-forward with an **embargo gap** so
that overlapping h-bar labels cannot span the train/test boundary. That embargo is the detail almost every retail
backtest omits.

---

## 4. What "proven" means — four answers, one definition

Arena: *"nothing is ever proven, you can only bound the probability that your result came from noise"* (deflated Sharpe,
PBO/CSCV, White's Reality Check, Hansen's SPA, Romano–Wolf). ChatPlayground: *"nothing in markets is proven
permanently."* 1min.ai answered with a method (ATR-based TP/SL) rather than a definition — the weakest of the four.

**Operational definition adopted here:**

> A signal is **proven** when it was pre-registered before the data was touched, evaluated on data the design never
> influenced, charged the measured cost of its own class, deflated for the number of trials actually run, and then
> **replicated on a second independent period** — and it clears every gate in `strategy_validation_protocol.md` §3.11
> without exception.

"Confirmed" is a smaller claim than "proven": confirmed means the primary endpoint was met on the pre-registered window.
Proven requires a replication.

---

## 5. The power arithmetic nobody in the four answers supplied

All four gave Sharpe-based power ("~2–5 years", "~100+ independent trades"). For a **top-gainer classifier** the right
lens is not Sharpe — it is the **information coefficient** and the **lift over a base rate**. Both are brutal:

### Detecting a rank correlation (IC) at t = 3

| IC | Observations needed |
|---|---|
| 0.02 | **22,500** |
| 0.03 | **10,000** |
| 0.05 | **3,600** |
| 0.10 | 900 |
| 0.15 | 400 |

### Detecting a lift in precision@K (one-sided α=0.05, 80% power)

| Base rate | Lift sought | Hit rate needed | Periods needed |
|---|---|---|---|
| 2% | 1.25× | 2.5% | **5,233** |
| 2% | 1.5× | 3.0% | 1,398 |
| **2%** | **2.0×** | **4.0%** | **391** |
| 5% | 1.5× | 7.5% | 539 |
| **5%** | **2.0×** | **10.0%** | **150** |
| 10% | 2.0× | 20.0% | 69 |

**The design consequence, and it is the most useful thing in this document:** a subtle signal is *unprovable*. An IC of
0.03 needs ten thousand observations — decades of daily data, or a cross-section of thousands of names. A **2× lift over
a 5% base rate needs 150 periods** — one year of daily signals.

So the protocol should **not** ask "does my model have a small edge?" It should ask **"does my model at least double the
base rate?"** If it cannot, it is not worth the decade of data it would take to distinguish it from zero. This single
choice turns an unanswerable question into a one-year experiment.

---

## 6. Metrics — merged list, deduplicated, with the estimator named

| Layer | Metric | Why | Source |
|---|---|---|---|
| **Forecast** | Precision@K, recall@K | the direct question: of the K names I named, how many were top gainers | AskAnyModel, ChatPlayground |
| | **Lift over base rate, with CI** | the headline. Raw hit rate is meaningless without it | operator |
| | Rank IC (Spearman) + Newey–West SE | more stable than hit rate, uses the whole ordering | ChatPlayground |
| | AUC / ROC | threshold-free discrimination | ChatPlayground |
| | Brier score and calibration | when the model says 60%, does it happen 60% of the time | AskAnyModel, ChatPlayground |
| | Directional accuracy **vs a base rate, per direction** | never against 50% — against the class's own up-rate | ChatPlayground |
| **Tradability** | Net expectancy per trade, at measured class cost | kills paper edges | all four |
| | Break-even cost multiple | how much cost can it absorb | arena |
| | Turnover × cost per year | the FOREX lesson: 56.93 bp/yr = 13.2% of the hurdle | our measurement |
| | Capacity at participation limit | a signal you cannot size is not a signal | arena |
| **Statistical** | DSR at honest N, PBO vs the **0.51** noise baseline, WFE, alpha t vs FF6 | the deflation layer | arena |
| | White's Reality Check / Hansen's SPA / Romano–Wolf | multiple-testing alternatives to CSCV | arena |
| **Forward** | SPRT / CUSUM drift detection, live IC vs backtest IC distribution | detects silent decay | arena |
| | Realised fill vs modelled fill (bp) | the one thing a backtest cannot tell you | operator |

---

## 7. Backtest and forward-test design (merged)

**Backtest:** point-in-time universe including delisted names, dead coins and dead exchanges (all four flagged
survivorship as the primary killer) · strict signal-to-execution lag · corporate actions and ticker changes via permanent
identifiers · full cost stack per class from `COST_OF_RECORD.md` · 2× cost stress · recorded trial count.

**Forward:** freeze the rule, then run **shadow → paper → micro-live** · pre-register the endpoint and the kill rule ·
sequential monitoring with alpha spending (O'Brien–Fleming 4.049 / 2.863 / 2.337 / 2.024 at 25/50/75/100%) · futility stop
if conditional power < 20% · drift detection by CUSUM/SPRT · the **base rate is computed and filed first, in its own
commit**.

---

## 8. What to actually build first

1. **A base-rate table, by class × horizon × direction.** No modelling. Just: how often does a random K-name draw from
   this class contain a top-20 gainer at 1d / 5d / 21d? *This is one day of work and it makes every later number
   interpretable.*
2. **A vol forecast, not a direction forecast**, used to set TP/SL (ATR- or realised-vol-scaled). This is the part of the
   task that is genuinely achievable.
3. **One 2×-lift test at 5% base rate** — 150 daily periods, pre-registered. If the model cannot double the base rate, stop;
   it is not a decade-worthy hypothesis.
4. **Long and short reported separately**, with the borrow and locate costs on the short side made explicit.
5. **Mutual funds excluded from the TP/SL study** entirely, replaced by their ETF equivalent. Justify any exception.

*Paper only. Zero capital. Not investment advice.*
