# What I would actually do at four different horizons

You asked four concrete questions, not "should I buy an ETF." Here are the answers, and the arithmetic that produces them
rather than a slogan.

**Everything rests on one equation:**

> **annual P&L ≈ (gross edge per trade − round-trip cost) × trades per year**

Three of the four questions are therefore questions about **frequency versus cost**, not about prediction. Our measured
round-trip costs (this programme, not assumed): **equity 12.07 bp · ETF 6.71 bp · crypto 52.0 bp · FX 7.53 bp · bond
0.61 bp.**

## The same signal is fine at 4 trades a year and fatal at 1,250

| horizon | trades/yr | cost load (% of traded capital/yr) | P&L at 1 bp edge | at 3 bp | at 10 bp |
|---|---|---|---|---|---|
| **long-term stocks** | 4 | **0.5 %** | −0.4 % | −0.4 % | −0.4 % |
| swing | 50 | 6.0 % | −6 % | −5 % | −1 % |
| **daytrading** 5/day | 1,250 | **151 %** | −138 % | **−113 %** | −26 % |
| daytrading 20/day | 5,000 | 604 % | −554 % | −454 % | −104 % |
| **scalping** 50/day | 12,500 | **1,509 %** | −1,384 % | **−1,134 %** | −259 % |
| crypto swing | 50 | 26 % | −26 % | −24 % | −21 % |
| **crypto daytrading** 5/day | 1,250 | **650 %** | −638 % | −612 % | −525 % |

**Read the 3 bp column.** A genuine 3 bp gross edge per trade — which is *better than most retail signals achieve* — loses
about 0.4 % a year at long-term frequency, 5 % at swing frequency, **113 % a year daytrading**, and **1,134 % a year
scalping.**

The signal didn't change. **The frequency did.** Cost is charged per trade; edge is earned per trade; so the ratio that
matters is *how often you pay*.

---

## 1. Long-term stocks — what I would do

**Cost is not the problem here (0.5 %/yr), so this is the one horizon where the answer is structural, not tactical.**

- **Core: the cheapest broad index you can actually hold.** S&P 500 or total-market, whatever the account supports. Our
  measurement is unambiguous: vehicle differences are **contractually** driven by expense ratio (7.95 bp/yr FXAIX vs SPY),
  and *statistically undetectable* in returns (tracking error ~1 %/yr swamps an 8 bp signal — 546 years of data would be
  needed to prove it). So: **choose on fee and account fit, never on trailing performance.**
- **Rebalance on a rule, not a feeling.** Annually, or at a 5 % band. The evidence converges that *frequency* barely matters
  and *having a policy* does. Without a rule you are just drifting into whatever won last.
- **Individual stocks: only as a deliberate concentration bet, sized so being wrong is survivable.** The persistence
  evidence is brutal — SPIVA has ~92 % of large-cap active funds underperforming over 20 years. That does not mean no stock
  ever beats; it means **you cannot identify the winner in advance with the tools available here.**
- **What would make me change my mind:** a stock-selection rule that survives walk-forward with costs and beats the index
  out-of-sample. Nothing in this estate has, across 69 picks and 0 endorsements.

## 2. Daytrading — what I would do

**I would not, and the reason is arithmetic rather than opinion.**

At 5 round trips a day (1,250/yr) the cost load is **151 % of your traded capital per year**. To merely break even you need
**> 12.07 bp of gross edge on every single trade, forever.** A realistic retail gross edge is **1–3 bp**. At 3 bp you lose
about **113 % of capital a year**, and leverage accelerates it.

What *would* make daytrading work — and this is the honest version:

1. **Being paid to provide liquidity.** Rebates and spread capture turn you from a cost-payer into a fee-earner. That
   requires exchange/volume arrangements a retail account does not have.
2. **A genuine information edge measured in seconds** — order flow, latency, or a newsfeed you act on before it is priced.
   An LLM reading the same public page as everyone else does not have this.
3. **A verified per-trade edge above cost, measured out-of-sample with commissions included.** Our own contest could not
   even get a *price* right: 41 of 69 picks were void at the fill because the recalled anchor was already outside the
   bracket. The information problem is upstream of the execution problem.

**What would change my mind:** a documented, cost-inclusive, out-of-sample track record showing > 12 bp gross per trade at
that frequency. Nobody here has one, and the burden is on the strategy, not on the skeptic.

## 3. Scalping — what I would do

**Structurally impossible as a directional retail activity, and the numbers are not close.**

At 50 trades a day the cost load is **1,509 % a year**. To beat cash plus a 10 % target you would need **> 20 bp of gross
edge per trade, sustained indefinitely** — against a realistic 1–3 bp. That is a **17 bp per trade gap**, and it does not
close with better indicators.

Scalping is profitable only for participants who **capture the spread instead of paying it** — market makers, HFT firms with
colocation and rebate tiers. A directional scalper pays the spread twice per round trip and donates the difference. This is
not a claim about skill; it is the sign of the term.

**What would change my mind:** evidence that you are on the *receiving* side of the spread (rebates, maker fees, or a
liquidity-provider tier). Absent that, the answer is no at any skill level.

## 4. A rare crypto signal with high certainty of profit

**The highest-certainty crypto edges are structural, not predictive — and that distinction is the whole answer.**

Our measured crypto round-trip cost is **52 bp**, so any signal must clear 52 bp before it earns a cent. Six times the equity
cost. That kills most predictive signals outright.

What is genuinely high-certainty in crypto:

| edge | certainty | why it is not free money |
|---|---|---|
| **Perpetual funding-rate carry** | high — the rate is published and paid on a schedule | crowded, compresses to nothing in calm markets, and the tail is a liquidation cascade |
| **Spot–perp basis** | high | requires holding both legs; capital-inefficient and it is an arb, not a forecast |
| **Stablecoin depeg restoration** | high *conditional on a credible issuer* | rare, brief, and a **total-loss** outcome if the peg is actually broken |
| **Exchange listing effects** | measurable, decays in minutes | you are competing with bots; by the time you read it, it is priced |
| **Token unlock supply shocks** | dates are public | direction is knowable, magnitude is not, and the market front-runs it |

Three honest rules about "high certainty" in crypto:

1. **If a signal predicts direction with high certainty, it is one of three things:** not actually high-certainty, **capacity
   limited to dust**, or **front-running you**. The market does not leave certain profit sitting at a size you can access.
2. **Certainty and size trade off directly.** The more certain an edge, the less capital it absorbs before it disappears.
3. **Custody and counterparty risk dominates every one of these** — 52 bp of cost is irrelevant next to the chance that the
   venue or the stablecoin does not exist next month.

**What I would actually do for crypto exposure:** treat it as a **position** (small, sized like a venture bet, held at a
custodian you would trust with the amount), not as a signal stream. If you want the carry trade, run it on a venue you have
stress-tested, expect it to compress, and size for the cascade.

---

## The one-line answer to all four

**Edge per trade is small and roughly fixed; cost per trade is large and roughly fixed; therefore frequency decides
everything.** Long-term ownership pays a rounding error in cost. Daytrading pays 151 % a year. Scalping pays 1,509 %. No
amount of prediction quality at the small edges available closes that gap — which is why the honest answers to questions 2
and 3 are "no," and the honest answer to question 4 is "the certain edges are structural, small-capacity, and not
predictions."

*Paper only. No live orders, no credentials. Educational analysis, not individualized advice. Costs are measured round-trip
figures from this programme; your broker's real costs will differ, and at high frequency that difference is the whole
result.*
