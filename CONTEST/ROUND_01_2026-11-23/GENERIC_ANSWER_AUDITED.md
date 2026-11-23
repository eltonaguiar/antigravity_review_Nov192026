# The generic answer, audited

**Date:** 2026-11-23 · **Subject:** a stock free-tier answer to *"what do you suggest, and what can you prove actually works"*
(free.ai, Qwen 3.6 35B, 818 tokens). **Test data:** SPY monthly adjusted close, 406 months, 1993-02 → 2026-11.

The answer is the one every model gives, and the one the operator explicitly asked to get past: *diversify, buy cheap index
funds, dollar-cost average, stay invested.* Three of those four survive measurement. **One is false.**

## Its four "proven by history" claims, scored

| claim | verdict | evidence |
|---|---|---|
| Broad diversification | **holds** | but correlations converge in a crisis; 2022 broke the stock/bond pair |
| Low fees / cheap index funds | **holds** | the one thing this audit independently concludes |
| Long-term holding (10+ years) | **holds** | the equity premium is the best-documented premium there is |
| **"Consistent contributions (DCA)"** | **FALSE as stated** | **measured below: DCA loses to lump-sum 78–80% of the time** |

## DCA: what the model called proven, measured

Same total ($12,000), same SPY, same terminal date. **Lump-sum** invests it all at month 0; **DCA** invests $1,000/month for
12 months. Every monthly start date from 1993 to 2026, ratio = DCA terminal value ÷ lump-sum terminal value.

| hold | start dates | **P(DCA > lump-sum)** | median DCA/LS | worst | best |
|---|---|---|---|---|---|
| 5 y | 346 | **21.4%** | **0.9472** | 0.764 | 1.399 |
| 10 y | 286 | **22.4%** | 0.9482 | 0.764 | 1.399 |
| 20 y | 166 | **19.9%** | 0.9478 | 0.793 | 1.216 |
| 30 y | 46 | **6.5%** | 0.9225 | 0.838 | 1.035 |

**Lump-sum wins roughly four times out of five**, by about **5%** over 10–20 years and **8%** over 30.

Widen the DCA window and it gets worse:

| DCA window | hold 10 y | hold 20 y | hold 30 y |
|---|---|---|---|
| 12 months | 22.4% | 19.9% | 6.5% |
| 24 months | 19.6% | 20.5% | **0.0%** (median **0.816**) |
| 36 months | 23.4% | 27.1% | **0.0%** (median **0.728**) |

**DCA over 36 months never beat lump-sum in any 30-year start date — 46 out of 46 — and ended with 27% less money.**

The mechanism is not subtle: markets trend up, so money that arrives later buys fewer shares. **DCA is a behavioural device** —
useful when you don't *have* the lump sum, or when you would panic and sell otherwise. It is **not** a return-enhancing strategy,
and calling it "proven by history" inverts the evidence.

## "Missing the best days" — true, fragile, and self-defeating as stated

Its fourth supporting fact: *"missing just a few of the best days can significantly reduce long-term returns."* Measured on 405
monthly returns:

| removed | share of months | 33-year multiple | CAGR |
|---|---|---|---|
| none | — | 28.38× | **10.42%** |
| best 5 | 1.2% | 16.85× | 8.84% |
| best 10 | 2.5% | 10.90× | 7.53% |
| best 20 | 4.9% | 5.00× | 5.15% |
| best 40 | 9.9% | 1.40× | **1.12%** |

Mechanically true — and **absurdly sensitive**: removing **10% of months** collapses a 10.42% CAGR to **1.12%**.

That concentration does not support "never sell." It shows that **returns live in a handful of periods**, which is precisely why
neither market timing nor this statistic is reliable. The honest form of the argument is the *other* direction: **the big up-months
cluster inside the scary periods, so you cannot dodge the drawdowns without also missing the recoveries.** The model stated the
scary half and dropped the half that makes it an argument.

## Two smaller errors

- **"Bonds: generally provide stability and income, often performing well when stocks are volatile."** 2022 is the counterexample:
  stocks and bonds fell together, and the 60/40 had its worst year in decades. "Generally" is doing a lot of work.
- **Crypto: "highly speculative and volatile"** — true, but it is one of the few asset classes where the *structural* edges are
  measured and real (funding carry, basis), just capacity-limited. "High-risk" is not the same as "no edge."

## Why this matters for the page

This is the answer a model gives when it has **no measurements** — and it is a good answer at that level. It is also the ceiling:
it can say *"buy cheap index funds"* but it **cannot** tell you

- what to do if you want individual stocks long-term (concentration sizing, not stock-picking),
- why daytrading at 5 round trips/day costs **151%/yr**,
- why scalping at 50/day costs **1,509%/yr**,
- what a *structural* crypto edge looks like versus a predictive one,
- or that its own DCA claim is **backwards**.

**That gap — between advice that is directionally right and advice that is quantified — is the whole reason `#horizons` exists.**
The generic answer is the floor, not the target.

*Paper only. No live orders, no credentials. Not investment advice.*
