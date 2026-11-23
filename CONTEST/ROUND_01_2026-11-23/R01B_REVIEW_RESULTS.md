# R01b reviewed by four models — and the strongest finding takes the most damage

Four models read the actual `#eli5` + `#r01b` page text (8,156 characters pasted; they had refused the bare URL because none
of them can browse). Verdict matrix on my six findings:

| model | F1 recall | F2 thin bracket | F3 unresolvable | F4 fund/ETF | F5 power | F6 rule-understanding |
|---|---|---|---|---|---|---|
| ChatGPT-6 Luna | OVERSTATED | OVERSTATED | OVERSTATED | OVERSTATED | UNVERIFIABLE | **WRONG** |
| Claude (Latest) | SOLID | OVERSTATED | OVERSTATED | **WRONG** | OVERSTATED | UNVERIFIABLE |
| Qwen3.6 Flash | OVERSTATED | *(no verdict)* | **WRONG** | SOLID | **WRONG** | SOLID |
| GLM 5.3 Flash | *(prose, no verdict lines)* | | | | | |

The spread is almost total — F3 is called OVERSTATED twice and WRONG once; F4 is called WRONG, SOLID and OVERSTATED by
different models in the same hour. **No finding has a consensus**, which is itself the result: six prose claims about a
contest cannot be adjudicated by vote, only by measuring the thing each one asserts.

## The four criticisms that landed, in order of damage

### 1. **F1 is pseudoreplication** — 18 entrants are not 18 independent observations

> ChatGPT-6 Luna: *"Treating 18 entrants as 18 independent observations; models may share training data, prompts, or price
> sources, so their errors can be highly correlated."*

I published F1 as *"the most robust finding in the programme"* because it reproduced *"across 18 entrants on two different
surfaces."* If those eighteen share training corpora and price priors, then eighteen models making the same stale recall is
**one observation repeated eighteen times**, not eighteen tests. That is textbook pseudoreplication and it inflates
confidence exactly the way a duplicated paste does.

**Adopted:** F1's replication count is not evidence of robustness. The honest statement is that *many models asked to recall
a price from memory produce stale prices* — a fact about training data, measured once, with eighteen sightings.

### 2. **F1 may be a harness failure, not a recall failure** — and the separating experiment is cheap

> Claude (Latest): *"the exact price and timestamp each entrant was given … re-run five entrants with a stamped quote
> included and compare void counts. This costs nothing and separates recall failure from harness failure."*

This is the sharpest point in the batch. **I never tested whether including a live quote removes the void.** I asked models
for "realistic price levels near the current market", got stale anchors, and concluded the models fail at recall — without
running the arm where the price is supplied. It is entirely possible the void rate collapses to near zero and the finding
is about my prompt, not about the models.

**Adopted as the next experiment:** re-run five entrants with a stamped quote in the prompt and compare void counts. If
voids vanish, F1 is a harness finding and must be rewritten.

### 3. **F2, F3 and the entire leaderboard sit on an unstated settlement convention**

> GLM 5.3 Flash: *"what a void scores, what an unresolved bracket marks to, and whether round-trip cost enters the R
> numerator or only USD P&L. Every one of F2, F3, and the leaderboard itself is downstream of unstated answers. Cheapest
> way: publish the settlement function — one page of code and one worked example per branch, zero new data required."*

Correct and embarrassing: `RULES.md` defines the inputs but not the **settlement**. Whether a void scores 0, is excluded, or
is penalised decides who wins; whether cost enters the R numerator or only the USD P&L changes every bracket's
classification. I asserted two pathologies about scoring while the scoring function was never written down.

**Adopted:** publish the settlement function with a worked example per branch **before** any further scoring claim.

### 4. Two smaller ones, both correct

- **Every price check rests on one vendor at one timestamp.** SPY 689.81, gold 3,620, EURUSD 1.0973 all came from Yahoo at a
  single moment. A second source, or a second timestamp, was never compared.
- **Transaction costs are treated as static class constants** (crypto 52 bp, FX 7.53 bp). Real costs depend on size,
  spread, and regime; a fixed constant makes every pick look equally executable.

## What they still endorsed, and it is the right thing to endorse

> GLM 5.3 Flash: *"F4 — buy the cheapest same-index vehicle and keep the ~8bp/yr; it is the only finding that converts into
> an action with capital, and **it survives its own overstatement**."*

That is exactly the position after `TRACKING_ERROR_CORRECTION.md`: the fee gap is **contractual**, not measured, so it needs
no backtest and survives every statistical attack on the backtests.

## The three things these reviews say to do next, ranked by cost

1. **Publish the settlement function** — zero new data. (GLM 5.3)
2. **Re-run five entrants with a stamped quote** — zero new data, ~5 API calls. (Claude)
3. **Stop counting entrants as independent trials** — a rewrite, not an experiment. (ChatGPT-6 Luna)

*Paper only. No live orders, no credentials. Not investment advice.*
