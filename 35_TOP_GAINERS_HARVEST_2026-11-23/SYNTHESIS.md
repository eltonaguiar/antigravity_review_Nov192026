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

### 2.1 The one answer that actually ranked the classes — and the tension it creates

**Gemini 4 Neon** (1min.ai) was the only respondent to commit to an explicit ordering, and it is the most useful single
paragraph in the five answers:

| Rank | Class | Its reasoning |
|---|---|---|
| **1** | **Crypto** | 24/7, retail-driven, structurally less efficient; narratives, liquidity rotation and momentum anomalies strongest here |
| **2** | **Small/mid-cap equities** | prone to retail frenzy, short squeezes and catalyst moves (earnings, FDA); predictable *around events*, high overnight gap risk |
| 3 | **Large-cap equities** | heavily efficient |
| 4 | **FX** | most liquid and efficient in the world, central-bank dominated; rarely produces explosive percentage moves, and mean-reverts rather than trends parabolically |
| — | **Mutual funds** | *"eliminate immediately"* — NAV prices once daily after the close, no viable intraday/weekly edge |

**And now the tension, which is the most instructive thing in this document.** If you rank the same classes by **net edge
after measured cost in our own estate**, the order inverts:

| Class | Gemini's predictability rank | Our measured net-edge rank |
|---|---|---|
| Crypto | **1st** | **last** — 20–52 bp round trip; **49 of 69** crypto picks go net ≤ 0 at the measured band |
| Small/mid-cap equity | 2nd | poor — smallest caps carry the highest measured friction |
| FX | 4th | 3rd — 7.533 bp upper-bound cost, and its best row (AUDJPY, DSR 0.815) is the nearest miss in the estate |
| Mutual funds | eliminated | eliminated — same verdict, for wrapper reasons (17.6× the index ETF) |

**Both rankings are correct, and they measure different things.** Crypto is genuinely the most *predictable* — and it is
also the most *expensive* to trade, which is exactly why our 69 picks died. This is the predictability-vs-tradability
split from §1, demonstrated on a single class: **being right more often is worthless if you pay 20–52 bp to be right.**

The practical consequence: **a predictable-and-expensive class is where a cost breakthrough converts a null into an edge.**
If crypto round trips can be brought from 20–52 bp to the 6.7 bp the ETF wrapper achieves, the crypto rows re-open. That
is a *measurable, testable* path — unlike hoping a signal improves.

### 2.2 The only concrete TP/SL design offered (Gemini 4 Neon)

Nobody else specified a trade construction. This one is complete enough to implement, and it rejects the naive version:

- **Never fixed percentages across assets** — *"a 5% move is normal daily noise for a memecoin, but a massive crash for a
  blue-chip stock."*
- **Volatility-scaled levels:** stop at **1.5 × ATR** below entry, target at **3 × ATR** above — a 2:1 structural ratio
  that adapts per instrument.
- **Trailing rather than fixed targets**, because the whole point is hunting outliers: take ~50% at a fixed target, then
  trail the remainder with a Chandelier Exit or a 10-day EMA close.
- **Time stops:** *"if an asset hasn't moved in your favour within X days, exit"* — dead capital carries opportunity cost.

**The requirement that makes this admissible under our protocol:** Gemini also demanded the modelling compare the setup
against **false positives** — *"assets that had the exact same footprint but dumped instead."* That is a base rate by
another name, and it is the same rule as §5. A TP/SL backtest that reports winners without the counter-example set is
reporting the survivors of its own selection.

Its feature set is also the most specific of the five: **volatility contraction** (tight Bollinger bands / low ATR) as the
precondition, **RVOL 3–5× the 20-day average while price is still flat** as accumulation, **relative strength while the
benchmark is dropping**, and for crypto **open-interest spikes, negative funding (short-squeeze fuel) and on-chain whale
accumulation**. Footprint window: **T−1 to T−14**.

### 2.3 GPT-4.1 mini — the most generic answer, but it asked the one question we could answer this afternoon

**Assessment:** clearly the weakest of the six substantively. It is a syllabus, not an answer — ten headings, no class
ranking, no threshold, no number, and it explicitly declines to commit (*"If you want, I can help detail out specific
methods or frameworks for any of these steps"*). Everything it proposes is correct and none of it is decisive.

**But it contains one genuinely novel, cheap, testable question that nobody else asked:**

> *"Do certain stocks or crypto tokens appear **frequently** as top gainers or losers? How do their historical return
> profiles look?"*

That is **repeat-gainer persistence** — and it is separable from the forecasting problem entirely. You do not need to
predict anything to answer it: just compute

> **P(a symbol appears in the top-20 gainer list within the next k days | it appeared today)**
> versus the unconditional base rate of appearing at all.

If that ratio is materially above 1, then gainer lists have **membership persistence** — a real, measurable phenomenon
that would explain why symbol-level searches feel productive, and it would give every later model a legitimate prior. If
it is ≈1, then each day's list is independent and the entire "find the footprint" programme loses its cheapest foothold.
Either answer is decisive, and both are computed from data we already have.

**Two metrics it named that the others under-weighted:** *"Accuracy per Direction"* (long and short success rates as
separate columns) and *"Signal Stability"* (consistency across periods and assets) — the latter being exactly the
walk-forward-efficiency idea in plainer language.

One further note in its favour: it was the only respondent to name **fund flows** as alternative data for mutual funds,
which is the one place a mutual fund *could* carry information — into the holdings it must buy, not into its own NAV.

**This is why §8 step 1 is now two steps:** the base-rate table, and immediately beside it the persistence test.

### 2.4 Mistral Small — the only respondent who said *how to measure* predictability, and one category error worth naming

**Mistral Small** (1min.ai, 25.4 s, **3,471 credits** — the cheapest answer in the set) contributed the one thing every
other answer lacked: **a measurement battery for the "which class is more predictable" question**, instead of an assertion
about it. It also decomposes predictability correctly into three separate properties:

| Property | Question | Why it is separate |
|---|---|---|
| **Directional accuracy** | can the model call up/down over the horizon? | what most people mean by "predictable" |
| **Magnitude accuracy** | can it size the move? | this is what TP/SL actually needs — a right direction with a wrong range stops out |
| **Volatility clustering** | is the *second moment* predictable? | achievable even when direction is not (§2, item 1) |

And it named the tests, which is the useful part because each is cheap to run:

- **Ljung–Box** on returns — serial autocorrelation. If returns are autocorrelated, a lagged-feature model has something
  to find; if not, the whole feature programme is decorative.
- **Hurst exponent** — **H ≈ 0.5 random, H > 0.5 trending/persistent, H < 0.5 mean-reverting.** This is the single most
  direct answer available to "is this symbol predictable", and it is computable per symbol in a few lines.
- **Approximate / sample entropy** — a randomness gauge that does not assume linear structure.
- **HMM or k-means regime clustering** — because predictability is regime-conditional: trending regimes favour momentum,
  ranging regimes favour reversion. A single unconditional number hides this.
- **A naive baseline** — *"compare accuracy to a naive benchmark (always predict up, or predict based on recent trend)."*

That last item is the most important sentence in its answer, and it is the same rule as §5 from a different direction:
**the naive benchmark IS the base rate.** In a market that rises 55% of days, a model at 54% accuracy is worse than doing
nothing. Any accuracy figure quoted against 50% rather than against the class's own up-rate is inadmissible.

**The category error, recorded because it is the most common one in this field:**

> *"If crypto has Sharpe = 1.2, stocks = 0.8, forex = 0.5, crypto is more predictable."*

**No.** That ranks classes by *risk-adjusted realised return*, which conflates predictability with cost, capacity, leverage
and luck. It is exactly the confusion §1 exists to prevent — and it is the practical version of it: an agent that ranks by
Sharpe will conclude crypto is most predictable precisely because crypto is most volatile, which says nothing about
whether any of it is forecastable. Predictability is measured by **Hurst, autocorrelation, entropy, IC and lift over base
rate** — never by Sharpe.

**And a direct factual conflict with Gemini 4 Neon, which is testable:**

| Claim | Gemini 4 Neon | Mistral Small |
|---|---|---|
| Large-cap equity | *"heavily efficient"* — least predictable | *"tend to be **more** predictable due to higher liquidity and institutional activity"* |
| Small/mid-cap equity | 2nd most predictable — frenzy, squeezes, catalysts | *"higher volatility but also higher noise"* |

Both cannot be right as stated. Liquidity plausibly makes a name *tradable*; it does not follow that it makes it
*forecastable* — if anything the efficient-market prior says the opposite. **This is resolvable this week** with the Hurst
exponent and lag-1 autocorrelation computed on large-cap versus small-cap panels: whichever group shows H further from 0.5
and larger |autocorrelation| is the more predictable one, by definition, with no model required.

Its other useful specifics: **TP at 1.5 × ATR with SL at 1 × ATR** (a 1.5:1 ratio — more conservative than Gemini's 3:1),
**trailing ATR or moving average** for trending assets, and **position sizing by inverse ATR** so that a memecoin and a
blue chip carry the same risk per trade. It also flagged **return smoothing in mutual funds** (NAV-based pricing) as a
reason their measured predictability is illusory — a distinct argument from the fee argument in §5, and a better one: the
series is smoothed, so autocorrelation is manufactured rather than real.

**Cost note:** at 3,471 credits it delivered the measurement methodology that the 105,111-credit answer did not. **Price
and usefulness were uncorrelated across this entire set.**

### 2.5 Claude 5.2 Fable — the best answer of the eight, and the one that changes the study's design

**Claude 5.2 Fable** (1min.ai, 71.4 s, **897,257 credits** — the most expensive answer by far). It is the only response
that (a) refused the question as posed, (b) replaced it with a better one, and (c) supplied the arithmetic that makes the
TP/SL question decidable.

#### (a) It identified the trap before answering

> *"Studying top gainers to see what they had in common is the classic trap, because it is selection bias. Every pattern
> you find in winners (volume spike, breakout, news) also appears in thousands of assets that went nowhere or crashed."*

And then restated the question in the only admissible form:

> ***"Given a set of conditions observable before the move, how does the distribution of forward returns differ from the
> base rate?"***

That is the same rule as §5 and §2.4's naive baseline, arrived at independently — but stated as a *distributional* question
rather than an accuracy question, which is strictly better: it forces a comparison against the base rate rather than
against zero.

#### (b) THE REFRAMING THAT MAKES THE STUDY FEASIBLE — trade the event, not the forecast

> *"Predicting gainers before they move. This is very hard, since the moves are mostly driven by news and tail events.
> **Trading what happens after an asset appears on the list (continuation or reversal). This is much more tractable,
> because the event is observable and the sample is large.**"*

**This should become the primary research question and it supersedes the brief's current framing.** The distinction:

| Problem | Information required | Sample | Verdict |
|---|---|---|---|
| Predict a gainer *before* the move | a forecast from features, against news and tail events | large but noisy; requires IC ≈ 0.05+ to be detectable (§5) | **stretch goal** |
| Trade *after* the name appears on the list | only the event, which is already observed | **large and clean** — every listed gainer is one observation by definition | **primary study** |

Choosing the second converts an unanswerable forecasting problem into an **event study**, which is why it also makes the
power arithmetic in §5 tractable: you need hundreds of *events*, not a model with a genuine 0.03 IC.

#### (c) The cited effects that bear directly on "top gainers" — including one that says *fade them*

Fable is the only respondent to cite the **MAX / lottery effect (Bali, Cakici & Whitelaw, 2011)**: *"stocks with extreme
recent daily gains underperform afterward, **which bears directly on 'top gainers'**."* That is a documented, replicated
result pointing the opposite way from the premise of this whole exercise — the list may be a *short* candidate set, not a
long one.

Its other citations, all of which survived this session's citation checks in spirit (real authors, real papers):

| Effect | Citation | Relevance here |
|---|---|---|
| Volatility clustering | canonical | *"volatility is far more predictable than direction, which is the basis for TP/SL sizing"* — corroborates §2 item 1 |
| Cross-sectional momentum, 3–12 months | Jegadeesh & Titman (1993), replicated globally | winners keep winning at *medium* horizons — not daily |
| Time-series momentum | Moskowitz, Ooi & Pedersen (2012) | across futures and FX |
| Short-term reversal, 1 wk–1 mo | Jegadeesh (1990); Lehmann (1990) | *"mostly in illiquid names, and costs eat much of it"* |
| **MAX / lottery** | **Bali, Cakici & Whitelaw (2011)** | **extreme recent gainers underperform afterward** |
| Post-earnings drift | Bernard & Thomas (1989) | *"gainers with fundamental catalysts drift; those without tend to fade"* |
| Crypto momentum & attention | Liu & Tsyvinski (2021) | stronger, but only ~10 years of data |
| FX carry & trend | extensive | works at longer horizons; short-term FX direction ≈ random walk (Meese & Rogoff) |
| Mutual fund persistence | Carhart (1997) | weak; mostly *bad* funds stay bad because of fees |

Two findings it flagged as *unhelpful to the premise*, and they belong in the record:

- **Sullivan, Timmermann & White (1999)** — classic chart patterns and indicator rules mostly fail after data-snooping
  corrections. That is the entire "find the footprint" family, written off by a paper from 1999.
- **Barber & Odean, and Chague et al. (Brazil)** — the large majority of retail day traders lose money.

Its governing insight, which resolves the §2.1 Gemini-vs-Mistral conflict without needing Hurst:

> *"The catalyst matters more than the move. A 20% gain on earnings behaves differently from a 20% gain on no news in a
> low-float stock."*

**That is the missing conditioning variable.** The large-cap-versus-small-cap argument both models had is probably a proxy
for *catalyst type and float*, not for size. Split the event study by catalyst and float and the dispute dissolves.

#### (d) The TP/SL arithmetic that corrects the other two answers

> *"TP/SL does not create edge; it only reshapes the return distribution. Under a random walk,
> **P(hit TP before SL) ≈ SL / (TP + SL)**, so expectancy is zero before costs and negative after. A 2:1 reward-to-risk
> ratio sounds good but just means you win about 33% of the time unless you have a real directional edge."*

This is decisive, and it invalidates the ATR-ratio proposals from §2.1 and §2.4 as *designs* rather than as arithmetic:

| Proposal | Ratio | Implied hit rate needed to break even (before costs) | Who proposed it |
|---|---|---|---|
| SL 1 × ATR, TP 1.5 × ATR | 1.5 : 1 | **40%** | Mistral Small (§2.4) |
| SL 1.5 × ATR, TP 3 × ATR | 2 : 1 | **33%** | Gemini 4 Neon (§2.1) |

Neither number is wrong; both were presented without the implied hit rate, which is the only number that matters. Its
formula for the honest version: **breakeven win rate = (SL + costs) / (TP + SL)** — costs in the numerator, always.

And the constructive part, which nobody else offered:

- **Triple-barrier method** (López de Prado): TP, SL and a **time-out** barrier; label each historical signal by which
  barrier is hit first. That is how you get a supervised learning target out of a trading rule.
- **MAE/MFE analysis** (maximum adverse / favourable excursion) on historical signals — *place stops and targets
  empirically instead of choosing a ratio and hoping.*
- **Conservative intrabar assumption:** *"if TP and SL both fall inside the same bar, assume the SL was hit first."*
  (Matches our existing `AMBIGUOUS` classification rule.)

#### (e) Two numbers that agree with a different model, independently

- **t-stat ≈ Sharpe × √years** — *"a Sharpe of 1 needs about 4 years to reach t = 2 and about 9 years to reach t = 3."*
  Our own toolkit produced **6.2 years** for a power-based test and **9.0 years** for t = 3 at SR 1.0. Two independent
  derivations, same answer.
- **Expect a 30–50% haircut** on backtest performance when going live. That is the same magnitude as the McLean–Pontiff
  post-publication decay, arriving from a different direction.

#### (f) Where it agrees with everything else, and refuses to rank

On classes it *declines to rank*, and says why — *"don't assume the ranking; measure it… run the identical pipeline on each
asset class and compare out-of-sample information coefficient and net-of-cost Sharpe."* Its one structural line is the best
summary of §2.1's inversion: ***"Inefficiency lives where trading is expensive, capacity is small, or risk is ugly."***

On symbols, it agrees with arena and with our own DSR collapse: *"one symbol gives you perhaps a few hundred independent
observations at a daily horizon. If you test 500 symbols and pick the 'most predictable' ones, you are selecting noise…
predictability belongs more to the setup, regime, and asset type than to the ticker."*

### 2.6 The ChatPlayground four — Luna, Claude, Qwen3.6 Flash, GLM 5.3 Flash

Four answers in one capture (full text now saved as `harvest_chatplayground_full.txt`; the earlier 32 KB capture was
partial and that page has since reset). Individually none beats Fable, but **together they supply the operational
machinery that "rank the classes" needs**, and they corroborate its two key claims independently.

#### The methodological answer to "which class is more predictable" — three models converge

Fable said *don't rank, measure with an identical pipeline*. **GLM 5.3 Flash and Luna said the same thing and made it
computable:**

- **GLM:** *"Rank asset classes and (symbol × direction) cells by **OOS ICIR and post-cost expectancy**. That ranking is
  your answer to 'which is more predictable'."* — and specified **ICIR = IC mean / IC std**, *"not average IC —
  consistency matters."* **ICIR is the metric nobody else named and it is the right one**: a class with IC 0.05 ± 0.02 beats
  one with IC 0.08 ± 0.20, because only the first is reliable.
- **Luna:** *"Raw 'accuracy' across classes isn't comparable because volatility and cost structures differ."* Report on
  the same risk basis, after costs, over multiple periods and regimes.
- **Claude:** *"measure each class on the same metrics, after costs, with the same methodology and comparable trade
  counts."*

**So the question is answered as a procedure, not an opinion: one pipeline, per class, ranked by OOS ICIR and net
expectancy.** That is now §8 step 1 and it is why the base-rate table comes first — ICIR is meaningless without it.

#### Luna: the cleanest statement of a distinction the others blurred

> *"Predicting the next week's top 10 gainers is a **cross-sectional ranking** problem. Predicting whether one symbol will
> rise over the next week is a **time-series direction** problem. You may want to test both."*

Those need different models, different baselines and different metrics (rank IC and precision@K for the first; directional
accuracy against the class's up-rate for the second). Everything downstream depends on picking one deliberately.

Its base-rate warning is the sharpest phrasing of the rule: ***"If top gainers are 1% of observations, a model that's
'right 60% of the time' may just be predicting 'not a gainer' poorly."*** And it offered the best one-sentence reframing of
the symbol question: *"for this symbol, **in this direction, over this horizon, under these conditions**, is the expected
net return positive and sufficiently reliable?"* — four qualifiers, none optional.

It also flagged that gainer lists are *"particularly vulnerable to low-liquidity spikes, stale prices, price limits, and
bad data"* — a data-quality hazard specific to this dataset, not generic survivorship.

#### Claude (latest): the payoff-arithmetic counterexample, and one caveat nobody else raised

> *"With symmetric TP/SL, a 50% hit rate is breakeven before costs. Your edge can come from payoff asymmetry **or** hit
> rate, but you must measure the combination. **A 35% hit rate at 3:1 reward/risk can be strong, and a 70% hit rate at
> 1:3 can be a loser.**"*

That is Fable's `P(TP) ≈ SL/(TP+SL)` arrived at independently, plus the counterexample that makes it intuitive — and it
explains why Qwen's and Gemini's ATR ratios are not comparable without their implied hit rates.

**The caveat that is unique in ten answers, and matters if this ever becomes a product:**

> *"If you plan to sell signals, providing trading recommendations for compensation can trigger regulatory requirements
> (e.g., investment adviser registration in the US), and selling performance claims without rigorous verification creates
> legal and reputational risk. Hypothetical or backtested results must be clearly disclosed as such."*

Nothing in the repo has said this before. **A backtested picks product is a regulated activity in the US**, and every
document in this folder should be labelled as hypothetical until a live, disclosed track record exists. Applies to this
site, the picks dossier, and anything published from it.

It also stated the study's purpose better than I had: ***"The most valuable outcome of this process is often knowing
reliably that a candidate edge is not real. Build the pipeline so that's easy to detect."***

#### Qwen3.6 Flash: the only explicit direction-bias table, and the staging numbers

| Class | Long vs short, its claim |
|---|---|
| Large-cap equity | **longs easier** — structural drift and buy-side pressure |
| Small/mid-cap, thematic | depends on catalyst; momentum works but *"reverses fast post-spike"* |
| Crypto | **trend-following longs historically stronger**; shorts need a volatility-regime filter |
| FX majors | roughly symmetric, heavily regime-dependent |
| Mutual funds | excluded from short-term signal engines |

Its quotable verdict: ***"'Top Gainer' is a mean-reversion trap. Daily winners often fade 2–5 days later."*** — the third
independent arrival at the MAX/fade hypothesis (Fable's citation, Claude's caveat, Qwen's assertion).

And it is the only answer with **concrete staging thresholds**, which the forward-test protocol needs: paper 2–4 weeks →
live simulation 1–3 months → small live capital 3–6 months, *"scale only if forward Sharpe > 0.5 and max DD < backtest DD
× 1.2"*, with gross expectancy needing to clear **1.5× costs** or the idea is discarded. (It also says *"if gross
expectancy < 0.8, it will fail live"* — two different cost rules in the same answer, a minor internal inconsistency worth
noting rather than adopting.)

#### GLM 5.3 Flash: three metrics and one warning that are genuinely new

- **ICIR** (above) — the ranking metric.
- **PR-AUC over ROC-AUC for rare events**: *"PR-AUC (better than ROC-AUC for rare 'big mover' events)."* Correct and
  important: with a ~1–2% base rate, ROC-AUC looks respectable for a useless model, while precision-recall collapses. **Any
  top-gainer classifier reported with ROC-AUC is reporting the flattering number.**
- **Drift monitoring by distribution shift**: *"Population Stability Index / KS-test on feature distributions; alert when
  the live regime leaves your training regime support."* That is the operational version of "regimes change", and it is
  implementable as a daily check rather than a monthly review.
- **MAE/MFE placement rule**, stated more precisely than Fable's: *"the SL belongs just beyond the MAE distribution of
  winners; TP near the upper quantile of the MFE distribution… 1.5–3× ATR stops and 2–4× ATR targets are common starting
  points, but let the data set them per symbol/horizon."*

**Its warning is the best line in the whole set about our actual cost problem:**

> *"The slippage on chasing movers is worst exactly when the signal is strongest — pumps are where retail gets filled
> worst. Your backtest must punish you for this."*

That is the mechanism behind our measured 20–52 bp crypto round trip. The cost is not a constant; it is **highest at the
moment the signal fires**, which is precisely why a static cost band still flatters the strategy.

#### Where these four are looser than our protocol — recorded, not adopted

| Gate | These four propose | Our adopted v1.0 | Note |
|---|---|---|---|
| **PBO** | GLM: **< ~30%** acceptable | **≤ 0.10** | 3× looser; and our noise baseline is 0.51, so 0.30 is barely better than chance |
| **t-stat on per-trade returns** | GLM/Qwen: **> 2** (ideally > 3) | **3.0 / 3.5 / 4.0** scaled by effective N | the 2.0 floor is the single most common softening across every panel |
| **OOS/IS Sharpe retention** | GLM: **≥ 50–60%** | WFE **≥ 0.60** | comparable, GLM slightly looser at the bottom |
| **Forward Sharpe to scale** | Qwen: **> 0.5** | not a gate; the gate is net expectancy vs the 4.32% hurdle | a 0.5 Sharpe is below the hurdle after costs |

They are all *credible* thresholds and none is *decisive* — the same pattern as the sixteen validation-protocol answers:
**no two sources agree on any single gate, and the loosest value always wins in practice if you let it.**

#### What the ten answers now agree on, and what remains open

**Agreement (unanimous or near):**
1. Predicting the raw gainer list is a selection trap; the admissible question is predictive and out-of-sample.
2. Survivorship-free, point-in-time data is the binding constraint — not model choice.
3. Volatility is more predictable than direction.
4. Long and short must be modelled separately; direction asymmetry is real.
5. Per-symbol models mostly overfit; pool, shrink, or condition on characteristics.
6. Triple-barrier labelling, not "up or down", when the output is a TP/SL trade.
7. TP/SL does not create edge; it reshapes the distribution — and the implied hit rate must be stated.
8. Compare against a base rate / naive benchmark, never against zero or 50%.
9. Report net of measured cost, with confidence intervals.
10. "Proven" is temporary; edges decay and monitoring is part of the system.

**Still open:** the ranking of classes — genuinely open, and now a *procedure* (identical pipeline, OOS ICIR, net
expectancy) rather than an argument. Nobody has run it.

### 2.7 The AskAnyModel six — Claude Opus 5.5, Grok 4.6, Command A+, Terra, Inkling Small, Gemini 3.5 Flash Lite

Full text saved as `harvest_askanymodel_full.txt`. **This panel contains the single most valuable sentence in the entire
harvest**, the best baseline definition, and one outright error.

#### THE number that calibrates the whole exercise — Claude Opus 5.5

> *"Information Coefficient (IC): the rank correlation between your signal at t and forward returns. **An IC of 0.02–0.05
> is realistic and can still be valuable. Anything above 0.1 is usually a bug or leakage.**"*

That single sentence resolves the tension in §5. Our power table says an IC of 0.03 needs **10,000 observations** to reach
t = 3 — which reads as "therefore don't bother." Opus supplies the missing half: **0.02–0.05 is what real edges actually
look like**, so the sample requirement is not a reason to abandon the study, it is the *specification* of the study. And its
second clause is a working fraud detector: **any reported IC above 0.1 should be treated as leakage until proven
otherwise.** Every "we predict top gainers with 70% accuracy" claim lives in that 0.1+ region.

It also supplied the test hierarchy I had as a list and it has as a discipline:

> **asset class → symbol → symbol × direction → symbol × direction × regime** — with the example *"BTC long only when above
> its 200-day MA and funding rate is not extreme."* And the warning: *"Test 500 symbols × 2 directions × 5 regimes and some
> will look brilliant by pure chance."*

Plus two refinements to §2.4's measurement battery:

- **Variance-ratio tests at multiple horizons** (1h, 1d, 1w) as the primary trend/reversion test — *"a variance ratio ≠ 1
  suggests trend or reversion."* It treats **Hurst with explicit caution** (*"it's noisy"*), which is a fair correction to
  how much weight §2.4 put on it.
- **"Requiring an economic reason for the effect"** listed *as* a multiple-testing defence — the same idea as our "name the
  loser", arrived at independently.
- **Meta-labeling** (a secondary model deciding whether to act on a primary rule) — mentioned as the natural next step, then
  truncated by the length limit.

#### THE baseline that should be mandatory — Grok 4.6

> *"If the strategy does not beat a naïve **'buy the previous day's top-10 and hold 5 days with a 2-ATR stop'** after
> costs, you have not found anything."*

That is the most implementable benchmark in fifteen answers, and it is now in `ML_TOP_GAINERS_BRIEF.md` as a required
comparison. It beats "compare to a base rate" because it is a *complete strategy* — same universe, same holding period, same
stop — so the comparison isolates the model's contribution rather than conflating it with the premise.

Grok's other two useful specifics: **keep the full ranked list, not just the top 10**, *"so you can study the whole
distribution"*; and **include a "do-nothing" class** because *"most days the correct action is to sit out."* It also proposed
filtering candidates by *"not already up 300% in 30 days"* to strip pump-and-dump artifacts.

#### The error worth naming — Command A+

> *"Cleaning: … apply **survivorship bias filters** (e.g., **keep only symbols that existed for the whole backtest
> period**)."*

**That is backwards.** Keeping only symbols that survived the whole period *is* survivorship bias — it is precisely the
defect every other model spends paragraphs warning against, and it is Gate 1 in our own protocol. Command A+ is also the
only answer to claim **large-cap equities are the *most* predictable class** ("highest risk-adjusted predictability for
short-term top-gainer signals"), and it justifies that with data quality and lower costs — which is a *tradability*
argument being used to answer a *predictability* question, the §1 confusion again.

#### The class-ranking scoreboard — a genuine six-to-two split

| Position | Models |
|---|---|
| **Crypto / small-cap most predictable** | Gemini 4 Neon · Gemini 3.5 Flash Lite · Grok 4.6 · GLM 5.3 Flash · Qwen3.6 Flash · Opus 5.5 (*"crypto and small caps show more raw predictability"*) |
| **Large-cap most predictable** | Command A+ · Mistral Small |
| **Refuse to rank — measure it** | Claude 5.2 Fable · Luna · Claude (latest) |

**Six to two, with three abstentions — and note how the six phrase it.** Nearly all qualify with *raw*, *pre-cost* or
*alpha potential*. Gemini 3.5 Flash Lite's reasoning is the clearest statement of the mechanism: crypto is *"heavily
retail-driven, highly emotional, structurally inefficient, and plagued by leverage… high-funding-rate shorts create massive
short squeezes"* — that is a real structural argument for raw predictability, and it does not contradict our measured
result that crypto has the worst **net** edge. **The split is not a disagreement about facts; it is two groups answering
different questions because nobody specified "predictable after cost".** That is the strongest possible justification for
§1 and for the ICIR procedure.

#### Two more things worth keeping

- **Gemini 3.5 Flash Lite overclaims** in a way that is instructive: *"three factors are **universally proven** — the
  volume/liquidity anomaly (accumulation), float and market-cap constraints, and the reflexive feedback loop."* Those are
  plausible mechanisms, but our own equity breakout — which is the volume/accumulation family — measured **PF 0.9917 at
  25 bp/side and 1.2865 at zero cost, break-even 24.59 bp/side**. "Universally proven" is exactly the language that gets a
  research programme funded and then killed. It also asserted that *"shorting top gainers after they exhaust is a very
  viable, highly profitable strategy"* with no number attached — the fade hypothesis is real (MAX effect), the *"highly
  profitable"* is not yet measured anywhere in this estate.
- **Inkling Small's cheap outlier filter** and driver clustering: *"is this symbol's behavior a 2-sigma outlier relative to
  its 90-day volatility? If yes, it's likely noise/catalyst-driven, not a repeatable pattern"* — a one-line screen for
  exactly the events that pollute a gainer sample. Its driver taxonomy (earnings surprise, M&A rumour, sector rotation,
  short squeeze via borrow cost and float %, crypto airdrop/liquidity) is the same conditioning Fable demanded, but easier
  to compute from data we hold.

### 2.8 Claude 5.1 Fable — the most expensive answer (1,511,466 credits) and the most complete research programme

Its thesis in three clauses, which is the best one-sentence framing in sixteen answers:

> *"Direction is weakly predictable, **volatility is strongly predictable**, and **the ranking of assets relative to each
> other is more predictable than the absolute path of any one asset**. Nearly everything below follows from that."*

#### (a) Three tasks, not two — and an explicit build order

Fable 5.2 split the problem in two (predict before the move / trade after the list). This split resolves it into three and
ranks them by difficulty — which is strictly more useful, because it tells you what to build *first*:

| Task | Question | Type | Difficulty |
|---|---|---|---|
| **A. Selection** | which symbols are in the next period's top-N movers? | cross-sectional ranking / rare-event classification | **moderate** |
| **B. Direction** | will symbol X go up or down over horizon H? | binary/ternary per symbol | hard |
| **C. Path** | given a long entry, does price hit +TP before −SL within H bars? | barrier / survival | hard, but tradeable |

> *"Most people jump straight to B. **You should build A first (it's where the real edge in 'top gainers' lives)**, use C as
> your label definition, and treat B as a derived quantity."*

And the reason A is more tractable is stated as a formula — the **Fundamental Law of Active Management, IR ≈ IC × √breadth**.
A cross-sectional strategy making 50 independent trades a day accumulates statistical evidence far faster than one making 50
a year, which is exactly the power problem in §5 dissolved by design rather than by patience.

#### (b) IT EXPOSES A DEFECT IN OUR OWN CRYPTO NUMBERS — BTC beta

> *"Correlation to BTC is so high that **most alt 'predictability' is just BTC beta — strip it out before you claim
> anything.**"*

**Our crypto rows never did this.** ENJ at +89.1 bp, WIF at +45.4, ETH at +29.2, NEAR at +29.1, JUP at +27.4 — measured
across the same window in which BTC moved. Any of those numbers may be **BTC beta with a symbol attached**, not an edge in
the symbol. The honest status of every crypto figure in `34_FINAL_PICKS_2026-11-23/` is therefore **unattributed until each
row is regressed against BTC and the residual is reported.**

This is the same class of error as the 175 bp FX defect and the "measured" cost bands: a number that looks like a
measurement of one thing and is actually a measurement of another. **It is now the top outstanding audit item in the estate**
and it does not require new data — only a re-run with BTC as a regressor.

#### (c) The 2×2 that settles the large-cap dispute

> *"**Small-cap 'top gainers' on no fundamental news mean-revert with high probability** — this is one of the most robust
> findings and is directly relevant to your target. **Large-cap gainers on earnings beats tend to drift further.**"*

That is the answer §2.1 and §2.4 were arguing around. The dispute was never large-cap versus small-cap; it is
**size × catalyst**, and both camps had one cell each:

| | Fundamental catalyst | No news |
|---|---|---|
| **Large cap** | **drift continues** (PEAD) | (unstated — thin evidence) |
| **Small cap** | (unstated — event-driven, capeable) | **mean-reverts with high probability** |

Gemini 4 Neon's "small/mid-cap predictable around events" and Mistral's "large caps more predictable" are **the same table
read from two different cells.** The event study must be split **size × catalyst** and report four cells, not two.

#### (d) The two numbers that agree — now independently confirmed twice

- **IC 0.02–0.05 realistic, 0.10+ suspicious** — identical to Claude Opus 5.5 (§2.7), from a different lab and a different
  platform. Two independent models, same calibration. That is settled.
- **ICIR = mean IC / std IC** — identical to GLM 5.3 Flash (§2.6). *"Tells you how stable the edge is, which matters more
  than its average."* Two independent models, same metric. Also settled.
- **Breakeven hit rate** `p* = (SL + costs)/(TP + SL)`: *"a 2:1 reward/risk needs ~34% wins plus costs; 1:2 needs ~67%."*
  Third independent derivation of §2.5's arithmetic (33.3% before costs, 34% with).

#### (e) Hurst is now settled as a diagnostic, not a signal — three models agree

*"Hurst exponent (rolling): ~0.5 random, >0.5 persistent, <0.5 anti-persistent. **Noisy on short windows; use it as a regime
descriptor, not a signal.**"* That is Opus 5.5's caution (*"it's noisy"*) and this module's, independently. §2.4's
Hurst-first framing is amended: **variance ratio (Lo–MacKinlay) is the primary test; Hurst is a regime descriptor.**

And it names the models that actually work on volatility, which is the achievable half of the task: *"autocorrelation of
absolute or squared returns… this is why **GARCH-family and HAR-RV** models work and directional models mostly don't."*

#### (f) Four operational rules we did not have

- **Reconstruct the gainer lists yourself from point-in-time OHLCV — do not scrape published lists.** *"They're
  inconsistent and incomplete."* This changes the data layer: the list is an *output to be computed*, not an input to be
  fetched.
- **Survivorship bias alone will fabricate a 2–4%/yr edge** — a magnitude for the defect that Gate 1 is red about.
- **Trailing stops must be measured, not assumed:** *"they often lower hit rate and raise payoff ratio, and the net effect
  is strategy-specific."* Directly contradicts the trailing-stop advice in §2.1 and §2.4, which were offered as
  improvements rather than hypotheses.
- **Cost ratio as a fragility test:** *"total costs / gross P&L — if above ~50%, the strategy is fragile."* And its sharper
  form of the baseline rule: *"if your model doesn't beat random entries with the same exit logic, your 'edge' is in the
  exits or in the asset's drift, not in the signal."*

#### (g) Its own class ranking — a third position

*"My honest ranking of practical directional-signal tractability for a solo/small team: **equities cross-section > crypto >
  FX > mutual funds**. For volatility prediction, all of the first three are good."*

Note what it ranked: **equities cross-section**, not large-cap specifically — and *tractability for a small team*, which is a
tradability-adjacent criterion. So the scoreboard is now **crypto-first 6 · equity-first 3 · abstain 3**, with the two
"equity" positions and most of the six both defensible once "predictable after cost" is specified — which remains the
missing clause in every disagreement.

### 2.9 Qwen4 Max — a **thinking trace**, not an answer. The most rigorous reasoning artifact in the set.

**Status: work in progress.** Qwen4 Max was still thinking when the capture was taken (`0s · 0 credits`, no final answer).
What follows is its *reasoning*, committed verbatim as `harvest_1min_qwen4max_thinking.txt`. **It is not citable as an
answer, but it contains three things no finished answer produced**, and one of them corrects my own §3.

#### (a) THE THEOREM the other sixteen answers only gestured at

> *"For a driftless martingale, **no combination of TP, SL, trailing stop, or breakeven move produces positive expectancy.**
> Optional stopping theorem: with bounded barriers and a time limit, E[P&L at stop] = 0, minus costs. **Barriers reshape the
> distribution — they trade win rate against payoff ratio — they do not create edge.**"*

That is the proof behind Fable 5.2's practical statement and Claude's counterexample. It also defines exactly where an edge
*must* come from, exhaustively:

> *(a) conditional drift — the signal genuinely shifts E[r]; (b) non-martingale path structure — autocorrelation, vol
> clustering, mean reversion; (c) a risk premium you're being paid to bear; (d) genuine convexity/optionality.*

Anything not on that list is a reshaped distribution with a hidden tail. And the corollary that kills most retail grid
searches: ***"every 'TP/SL optimizer' that shows a profitable grid on random-walk data is overfitting or leaking."***

#### (b) THE CONTROL EXPERIMENT that should be mandatory — the overfitting floor

> *"Run your entire TP/SL optimization pipeline on (i) bootstrapped/shuffled returns preserving vol clustering, and
> (ii) synthetic GBM matched to each symbol's σ. **Whatever 'edge' appears there is your overfitting floor. Subtract it.**
> This single control experiment is worth more than most indicator libraries."*

That is a cheaper, more general version of the random-signal 99th-percentile test already in our protocol, and it applies
**to the pipeline rather than to the strategy** — so it also catches defects in the harness, not just in the signal. It is
now in the brief.

#### (c) THE case-control design — the cleanest answer to "how would you reverse engineer it"

Nobody else named the correct study design. Qwen did, and supplied a worked number:

> *"A 'top gainers' list is a sample drawn on the dependent variable. If you collect 5,000 historical gainers and find 78%
> had a volume spike, a tight consolidation and a low float — you have learned **P(features | big move), not P(big move |
> features)**. […] If 1,500 of 3,000 names had a volume spike but only 200 became gainers, your '78% pattern' has a **~13%
> hit rate against a ~2% base rate**. That's a real **6× lift** — but it is not a 78% system."*

| Stage | Design | Output |
|---|---|---|
| **Reverse-engineering** | cases = historical top-N gainers; **controls = matched non-gainers** (match on date, market-cap bucket, sector, price level, trailing vol, liquidity) | conditional logistic regression → odds ratios per antecedent feature |
| **Cohort / prospective** | full point-in-time universe, every day, including losers and flat names | base rates, precision@K, lift, calibration |
| **Trading** | add costs, path, sizing, correlation | is it worth doing |

*"Matching controls is the step everyone skips. Without it, you'll 'discover' that gainers are volatile small caps — which is
a description of the universe, not an edge."*

#### (d) It corrects my §3 recommendation

§3 originally said **"test long and short separately, never pooled."** Qwen's version is statistically better:

> *"Don't reflexively split your data — **you halve your sample and double your variance.** Fit one pooled model with a side
> indicator and side × feature interactions. Test whether the interaction terms add OOS value. **Check calibration
> separately per side** — the most common real finding is that the model is well-calibrated for longs and systematically
> overconfident for shorts. Only split into separate models if there's evidence of parameter instability and enough samples
> per side (≥ a few hundred independent events per side)."*

§3 is amended accordingly: **pool with interactions, report per side, split only on evidence.** Fit TP/SL separately per
side regardless, *"because you're estimating distributions, not searching a parameter grid"* — which is the distinction that
makes it cheap rather than an overfitting risk.

#### (e) Concrete expectation numbers — the most useful calibration in the set

> *"IC 0.02–0.05 daily cross-sectional is real; hit rates **52–56%**; Sharpe **1–2** net for a decent retail-scale strategy;
> anything **>3** OOS with a high win rate on tiny samples is suspicious. **Precision@10 for top gainers maybe 15–25% vs a 2%
> base rate = huge lift, and that's enough.**"*

So the target is explicit: **P@10 of 15–25% against a 2% base rate** is a success, not a compromise. Anything claiming 60%+
precision on top-gainer selection is describing leakage. That number goes in the brief as the acceptance threshold.

#### (f) Predictability is a tuple, and a surface — not a scalar

> *"Predictability is a property of the tuple **(symbol, horizon, feature set, label, cost structure, regime)**. Change the
> horizon from 1 day to 20 days and momentum flips to reversal. Change costs from 1 bp to 30 bps and a real edge becomes
> unprofitable. **So measure it as a surface, not a scalar.**"*

That is the most compact statement of why the ICIR-per-cell procedure (§2.6) is the right shape: the answer is a surface over
that tuple, and any single ranking of classes is a projection of it.

#### (g) One look-ahead trap we had not logged

> *"**Retroactively adjusted price histories** — split/dividend adjustments silently change 'distance from 52w high' **as
> computed years ago**."*

Every price series we hold is back-adjusted, which means a feature computed today on 2015 prices is *not* the feature a
trader could have computed in 2015. That is a distinct defect from survivorship and from publication lag, and it applies to
any feature built from adjusted closes.

Also worth recording: on ambiguous intrabar barriers it says to assume **SL first** (*"assuming TP first is the single most
common inflator of TP/SL backtests"*) — third independent statement of our `AMBIGUOUS` rule. And on mutual funds it gives the
mechanism precisely: *"stale pricing of illiquid holdings creates artificial autocorrelation that looks like predictability
but isn't harvestable"* plus **forward pricing** — *"you can't actually trade a mutual fund at the price you see."*

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

**Recommendation (amended by §2.9):** pool long and short into **one model with a side indicator and side × feature
interactions**, then split only if you can demonstrate parameter instability. Splitting first halves your sample and doubles
your variance. But **report every metric per side regardless** — IC, precision@K and calibration separately — and fit TP/SL
separately, because the MFE/MAE distributions genuinely differ. AskAnyModel's observation that mutual funds are a poor fit
for TP/SL belongs here too — daily pricing, no intraday stop, redemption fees. **ETFs are the tradable equivalent of a
mutual fund**, and that substitution alone removes the wrapper problem.

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

**0. Reframe to the event study (Claude 5.2 Fable, §2.5b).** Stop asking "can we predict tomorrow's gainers" and start
asking **"what happens after a name appears on the list"** — continuation or reversal, conditioned on catalyst type,
liquidity and float, and regime. The event is observable, every listed gainer is one observation by definition, and the
sample is large. **This supersedes the forecasting framing**, and everything below is easier once it is adopted.

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
