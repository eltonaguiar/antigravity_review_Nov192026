# Review — "what would change these verdicts, is it possible?"

**Reviewed:** 2026-11-24 · Four-question answers from 5+ models (Gemini 3.1 Pro, Claude Opus 5.5,
Kimi K2.7, GLM 5.3 Flash, Qwen3.8 Max, ChatGPT-6 Luna, plus two Assistant A/B drafts).
Checked against this repo's measured artifacts rather than judged on plausibility.

---

## 0. What all of them get right — and it is most of it

Unanimous and correct: **buying data does not flip a verdict, it makes the claim testable.**
They also agree on the mechanics — point-in-time data, delisting treatment, pre-registration,
realistic fills, purged/combinatorial CV, Deflated Sharpe, and the fact that most strategies
should fail these bars. Nothing to add; the framework is sound.

Ranking by feasibility (penny hardest, futures easiest) is also directionally right, and I can
now put a number on why.

---

## 1. The one claim they all make that we have already failed

> "Maintain a trial registry from day one, or N is unknowable and DSR is meaningless." — GLM
> "Count every variant you tried, including the ones you abandoned." — Claude Opus 5.5

**We did not.** `README.md` line 271, on the record:

> *"the trial count **N** — six values in circulation (120, 154, 122, 362, 658, …)"*

Six values, not one. N is not merely unknown; it was never captured. This matters more than
any data purchase on their lists, because **it is a one-way ratchet**: you cannot retroactively
count trials you did not log. Every other gate on their list can be bought or waited for. This
one cannot.

**But the damage is smaller than "meaningless", and the models overstate it.** The
multiple-testing bar grows like $\sqrt{2\ln N}$, which is logarithmic:

| N | SR₀ bar |
|---:|---:|
| 120 | 3.09σ |
| 122 | 3.10σ |
| 154 | 3.17σ |
| 362 | 3.43σ |
| 658 | 3.60σ |

The full spread from our smallest to largest cited N is **3.09σ → 3.60σ, i.e. +16%** — not
5.5×. So the accurate statement is narrower and more useful than theirs:

> DSR cannot be *reported* without choosing an N arbitrarily, and the choice moves the
> significance bar by ~16%. It is not meaningless — it is **non-unique**, and must be published
> with the N it used and the range it would take under the other five.

That is a reporting requirement, and it costs nothing.

---

## 2. The consensus that futures are "easiest and cheapest" — right, and it exposes a defect in our own table

All of them rank futures first because the data is cheap. I checked the **trade** cost too,
since the gate explicitly names "costs", and futures turn out to be cheap there as well.
Round turn computed from standard contract specs (1 tick per side):

| instrument | tick value | notional | 1 tick | round turn |
|---|---:|---:|---:|---:|
| GC (gold) | $10.00 | $265,000 | 0.38 bp | **0.75 bp** |
| ES (S&P 500) | $12.50 | $250,000 | 0.50 bp | **1.00 bp** |
| MES (micro, same ratio) | $1.25 | $25,000 | 0.50 bp | **1.00 bp** |
| CL (crude) | $10.00 | $62,000 | 1.61 bp | **3.23 bp** |

Against our cost-of-record table — fund 0 · bond ETF 0.61 · **futures ≈ 0.75–3.23** · equity
central 4.01 · ETF 6.71 · FOREX 7.53 · **commodity 20** · crypto 20–52 bp — futures are the
second-cheapest tradable class, exactly as the models say.

**And that is the problem.** Our table costs commodity at **20 bp** while the same economic
exposure via **CL futures is 3.23 bp** — a **6.2× overstatement**. The two rows are measuring
different wrappers: 20 bp looks like a spot/CFD/spread-bet estimate, while futures are
per-contract. Anyone grading a commodity strategy against 20 bp is over-charging it by ~6×,
and that is a *conservative* error that has been quietly killing commodity candidates.

**Self-correction, recorded:** my first pass at this printed the conclusion *"futures sit
between equity central and commodity — not cheapest"* alongside arithmetic that showed
**1.00 bp**. The prose contradicted the numbers; the numbers win. Futures are cheaper than
equity, and the correction is the finding above, not the original claim.

Two shape differences the models miss: futures cost is **per contract**, not per % of capital,
so it does not scale with position size; and **every roll is a round turn**, so a strategy's
true turnover is (rebalances + rolls), which none of the five account for when estimating cost
drag.

---

## 3. The gate all of them underestimate: meme "n ≥ 100 independent bets"

Every answer says the same thing — pre-register, wait for 100 forward trades, compute the
CI and DSR. Two of the measurements from today make that necessary but **not sufficient**:

**(a) The category is not 100 independent bets.** Live CoinGecko: top-3 = **67.4%** of listed
meme cap, top-10 = **84.1%**, and **81 of 98** coins were negative on 7 days (median −6.73%).
They move as one trade. So 100 forward trades in this category are ~1 bet sampled 100 times,
and a DSR computed on them assumes an independence that does not exist. Kimi flags
"economically independent, not 100 overlapping positions" as a caveat; the measurement says
this is not a caveat, it is the binding constraint.

**(b) The fills are undefined without an intrabar rule.** Measured on 999 daily bars: **WIF
broke a −5% stop on 22.91% of days and closed back above it** (BTC: 4.00%). A forward meme
test that uses stops will therefore produce per-trade returns that depend on intrabar path,
which daily bars cannot observe. "Net CI-low > 0" is not computable until the fill convention
is specified — that is a *pre-registration* requirement the models do not name.

**(c) One answer proposes exactly the thing it forbids.** Assistant A: *"broaden your universe
to small/mid-cap retail attention spikes so you get 10–15 signals a month, hitting n=100 in ~8
months."* That is not passing the pre-registered meme gate — it is **replacing the hypothesis
to reach the sample size**, which the same answer elsewhere calls data-mining. Any n≥100
achieved by widening the universe post-hoc is a different claim and must be registered as a
new trial (which increments N, which raises the bar — see §1).

---

## 4. Where they are simply right and we have nothing

- **Options.** They say a snapshot cannot support a claim. Our repo has **zero** option-chain,
  implied-vol or greeks files — we do not even have the snapshot. Confirmed; the verdict is
  not close to changing.
- **Penny.** All rank it hardest and most expensive. Add the reason they miss: our only
  measured equity cost is the **191-large-cap bracket (floor 0.98 bp)**. OTC spreads are orders
  of magnitude wider, so **that bracket must not be reused** for penny work. No OTC cost
  measurement exists in the estate and none is planned — so "until then, no" is the correct
  verdict even if the data were free.

---

## 5. Shortest honest answer to "is it possible?"

- **Futures — yes, and it is under-priced by us, not over-priced.** ~1 bp round turn, data
  <$1k. But add rolls to turnover and register the trials.
- **Options — yes, at $100–400/mo (ORATS/ThetaData).** Requires a fill model calibrated from
  live fills; the mid-price assumption is the whole game.
- **Meme — the data problem is solved and the statistical problem is not.** n≥100 is
  reachable in DOGE/PEPE-class liquidity; independence and fill convention are not, until
  someone defines them. And **N is already lost**, which caps how strong any DSR can be.
- **Penny — no, and cheapness of data is not the blocker.** No OTC cost measurement exists, and
  the existing equity bracket does not transfer.

The one piece of work that changes the most for the least money: **reconstruct N as a bounded
range, publish every future DSR against that range, and start the trial registry now.** That is
free and it is the only gate that cannot be bought later.
