# Contest design review — what the panel found wrong with my own scorer

**Date:** 2026-11-23 · **Method:** `ask4ais` (ChatPlayground, 4 panels) + `askpollinationsandothers`
(router alias `ULTRA_FREE_CLOUD_LARGE`, 2 runs). **Purpose:** double-check the R01 scoring rule before any
result is published, and find statistics the protocol omits.

Nothing here is a result. It is a review of the measuring instrument.

---

## 1. The defect two independent models found, unprompted

Both said the same thing in different words: **voiding a pick whose fill price is already outside its own
bracket removes the only penalty for submitting an untradeable bracket.**

`ULTRA_FREE_CLOUD_LARGE` (router, run 2), verbatim:

> *"The void rule hands the leaderboard to degenerate, zero-width brackets … The cheapest exploit is a bracket
> of essentially zero width: profit target one tick above, stop one tick below the expected fill. The fill almost
> always lands inside, so it is scored; the first tick move decides the outcome … A second exploit is a huge
> bracket (stop 50% away, target 50% away): it is never voided, never stopped, and is scored purely on whether
> the horizon-end price is above or below the fill — a free, cost-free, one-shot directional option on every
> pick. Either way, expected score per pick is set by bracket geometry, not by forecast skill."*

A second run described the same defect as a **non-monotonic payoff cliff**: wider brackets are disadvantaged
relative to narrower ones by a discontinuity, not by skill.

**This is correct, and it is a flaw in my rules, not in the entrants.** Two exploits, opposite directions:

| exploit | bracket | why it pays |
|---|---|---|
| degenerate | target 1 tick above fill, stop 1 tick below | fill is almost always "inside" → always scored; the first tick decides; nothing is void |
| free option | stop 50% away, target 50% away | never voided, never stopped in the horizon → scored on horizon-end price alone = a one-shot directional option at zero cost |

R01 measured 26 of 48 picks as void under this rule. **A rule that can be satisfied by an untradeable bracket is
measuring bracket geometry, not forecasting.**

### The fix adopted — clamp the geometry to the fill, don't void

The cheapest correct fix is not "score the void as a loss" or "score it as a win" (both were proposed); it is to
**re-anchor the entrant's intended risk geometry onto the price that actually traded**:

```
risk   = |stated_entry − stop|        reward = |target − stated_entry|
long : stop = fill − risk             target = fill + reward
short: stop = fill + risk             target = fill − reward
```

This keeps the entrant's own R multiple, makes every pick tradeable, removes both exploits (a zero-width bracket
now risks ~nothing and pays ~nothing; a huge bracket keeps its own R geometry instead of becoming a free option),
and — the point — **a stale anchor costs real R at the magnitude the entrant chose**, instead of being laundered
into a void.

Implemented as `assess_contest.py --fill-relative`. **R01 is NOT retro-scored.** Its rules were published and its
entries were frozen against them; changing the rule now would be moving the goalposts. R01 will be reported under
both, as a sensitivity, with the rule that was in force labelled on every number.

### Demonstration on one entry (stale panel — NOT a contest result)

Arena.ai's four picks, same price panel, both rules. The panel here is the 3-month series, so the fills are old
bars; this tests the *rule*, not the entrant.

| pick | void rule | clamped rule |
|---|---|---|
| USDJPY long | −0.0149 R | −0.0097 R |
| TLT short | **VOID** | +0.4835 R |
| XLF long | **VOID** | −1.7705 R |
| XOM long | **VOID** | −1.0516 R |
| **mean R** | **−0.0149** | **−0.5871** |

**The void rule flatters this entry by ~0.57 R per pick.** That is the size of the hole.

### What the void rule was hiding across the field

Of the 26 picks it voided, **15 were already past their stop and 11 already past their target** — i.e. the
field's anchors were biased in both directions, with a majority too high:

| entrant | past stop | past target |
|---|---|---|
| Qwen4 Max | **4** | 0 |
| GPT-5.3 Codex | 3 | 1 |
| GPT-4.1 mini | 3 | 1 |
| Claude 5.2 Fable | 2 | 0 |
| Qwen3.6 Flash | 1 | 3 |
| ChatGPT-6 Luna | 0 | 2 |
| GLM 5.3 · M365 Copilot · Claude Haiku | 1 each | 1–2 each |

---

## 2. Checks the panel says validation teams most often omit

Coverage across the ChatPlayground panels (✓ = named by that panel):

| omitted check | what it prevents | A1 | A2 | A3 |
|---|---|---|---|---|
| ambiguous-bar / intrabar resolution | "stops control risk" when both levels sit inside one bar | ✓ | ✓ | ✓ |
| block-bootstrap CI on returns | "the edge is reliable" when returns are autocorrelated | ✓ | · | ✓ |
| purge / embargo around splits | "it generalises" when labels leak across the split | ✓ | · | ✓ |
| effective sample size | "n is large" when observations are correlated | ✓ | ✓ | ✓ |
| CVaR / expected shortfall | judging risk by average return alone | ✓ | ✓ | ✓ |
| fill rate / partial fills | assuming every order fills in full | ✓ | · | · |
| venue / platform mismatch | pricing a strategy on a feed you cannot trade | · | ✓ | · |
| borrow / funding cost | shorts that look free and are not | ✓ | · | ✓ |
| gap risk | stops that do not stop across a gap | ✓ | · | ✓ |
| anchor / staleness map | a remembered price misread as a forecast | ✓ | ✓ | ✓ |
| multiple testing (DSR / PBO) | "impressive Sharpe" that was the luckiest of many | ✓ | ✓ | ✓ |
| regime split | an edge that exists in one regime only | ✓ | ✓ | ✓ |
| concentration / best-trade share | P&L from one name, day or outlier | ✓ | · | · |
| turnover | gross edge eaten by trading | ✓ | · | ✓ |
| underwater / recovery time | drawdown duration, not just depth | ✓ | · | · |
| fill-window / conditional entry | claiming a level that was never tradeable | · | · | ✓ |

**What this scorer already does:** per-class round-trip cost applied once, stop-wins on a double-touch bar, fill at
the first real bar open, bracket validated *against the fill* rather than the stated entry, funds scored on $ only.

**What it does not do, and should report from R02:** the **ambiguous-bar rate** (a headline number, not a footnote),
**fill rate**, a **block-bootstrap CI on mean R**, the **effective sample size** of a 48-pick round, **CVaR**, and
**concentration** (share of total R from the single best pick).

---

## 3. The R02 submission design the panel converged on

Two panels independently proposed the same structure: **stop submitting absolute levels; submit rules anchored to
the fill.**

> *"Do not submit guessed absolute prices. Specify a price-independent rule tied to the executor's actual fill …
> `stop_rule: fill_price × (1 − 0.01)` and `target_rule: fill_price × (1 + 0.02)`; or define stop and target as
> multiples of executor-calculated ATR at entry."*

A third proposed the same idea from the other direction — express the pick as a percentage move plus an admissible
fill window (`long, +24%/−14%, enter only if fill ∈ [lo, hi]`), so that **staleness becomes a visible void instead of
a fake win**, and cite the round-1 BTC pick as a failure of the absolute-level approach.

**R02 design (to adopt):**
1. `move_pct = +x%` and `risk_pct = −y%` (or ATR multiples), **not** absolute tp/sl.
2. `admissible_fill_window = [lo, hi]` — outside it the pick is void, by construction and disclosed up front.
3. Mandatory `net_edge_bp = gross_expected_bp − class_cost_bp`, checked against the executor's recomputation.
4. Report the ambiguous-bar rate, fill rate, block-bootstrap CI on mean R, effective n, and concentration.
5. Randomise the bar-resolution rule, cost band and tie-breaks per round so the contest cannot be won by reading
   the rules.

---

## 4. Failures recorded, including suggestions that were wrong

- **`ollama:qwen3:8b` — timeout, 300 s, 0 chars.** Recorded as a failed source, not an answer.
- **One panel's "Defect 2: fixed round-trip costs ignore position size" is wrong.** The costs in this contest are
  *basis points*, which are already proportional to notional; a $100k and a $10k trade pay the same bp. The
  critique would be right against a fixed per-ticket fee, and this rule does not use one. Recording it as a miss
  rather than quietly dropping it.
- **Two runs of the same alias produced two different but convergent answers** (void rule / non-monotonic cliff).
  Same defect, different framing — treated as convergence on the defect, not as independent corroboration of a
  specific fix, because the proposed fixes differed.

*Paper only. Not investment advice.*
