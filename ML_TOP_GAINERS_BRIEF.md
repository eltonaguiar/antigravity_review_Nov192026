# ML_TOP_GAINERS_BRIEF — can we predict tomorrow's top gainers, or only explain yesterday's?

**Status:** pre-registered brief. Assignable as of 2026-11-23. **No result exists yet** — this file is the question
and the rules, deliberately written before any model is fitted.

> **Read alongside [`35_TOP_GAINERS_HARVEST_2026-11-23/SYNTHESIS.md`](35_TOP_GAINERS_HARVEST_2026-11-23/SYNTHESIS.md)** —
> the merged answers from four agents asked the same question on 2026-11-23, plus the power arithmetic that changes the
> design (synthesis §5: an IC of 0.03 is unprovable — 10,000 observations — while a 2× lift over a 5% base rate needs 150).

## 0.1 The framing the operator actually asked, and why it is better than a plain "predict gainers" brief

The question put to the four agents was sharper than "can you predict gainers". It asked for **four separate
determinations**, and each one needs its own estimator:

1. **Which asset class is more predictable?** — a *comparative* claim. Requires the same protocol run per class and a
   ranking of the results, not five independent studies reported separately.
2. **Is a particular symbol more predictable, or is it symbol × direction?** — the decomposition matters because the long
   and short sides are different economic problems (ERP drift on one side, borrow and negative skew on the other).
   **Never pool long and short.**
3. **What counts as "proven"?** — operational definition in §9 of the synthesis; short version: pre-registered, out-of-
   sample, net of measured cost, deflated for the trials actually run, then replicated.
4. **Backtest how, forward-test how, and which metrics?** — §7 and §6 of the synthesis, merged and deduplicated.

**The first deliverable is therefore not a model. It is a base-rate table by class × horizon × direction** — how often a
random K-name draw from that class contains a top-20 gainer at 1d / 5d / 21d. Without it, no later number is
interpretable.

## 0.2 Predictability is not tradability — the organising principle

A class can be predictable and unprofitable (FX carry: mechanism known in advance, Sharpe **−0.126** vs the 4.32% hurdle)
and unpredictable and profitable (index ETF: daily direction near coin-flip, positive over decades at 6.7122 bp/yr of
cost). **So classes are ranked on net expectancy per unit of cost, with predictability as a screen — never on hit rate.**

## 0.3 Two numbers that set the scale of this study

**Expected IC is 0.02–0.05, and anything above 0.1 is a bug or leakage** (Claude Opus 5.5, §2.7 of the synthesis). That
calibrates §5's power table rather than defeating it: IC 0.03 needing ~10,000 observations is not a reason to abandon the
study, it is the *specification* of it. **A reported IC above 0.1 is rejected on sight and audited for leakage before it is
discussed.**

**The mandatory baseline is a complete strategy, not a base rate:**

> **Buy the previous day's top-10 gainers, hold 5 days, with a 2-ATR stop.**

Any candidate must beat that **after measured costs**, on the same universe, same holding period, same stop (Grok 4.6,
§2.7). Comparing to a base rate tells you whether the *signal* carries information; comparing to this tells you whether the
*strategy* carries value. Both are required, and this one is reported first because it is the number a reader can act on.

Two supporting rules from the same panel: **keep the full ranked list, not just the top 10**, so the whole distribution is
inspectable; and **include a "do-nothing" class**, because *"most days the correct action is to sit out."*


---

## 0. The claim we are and are not testing

Two claims look identical in a deck and are not:

| Claim | What it means | Value |
|---|---|---|
| **Explanatory** | "The top 20 gainers today all had high volume and small float" | **near zero** — you found them by their outcome |
| **Predictive** | "At 15:55 on Monday, using only data up to 15:55, these 10 names will be in Wednesday's top 20" | the only claim worth money |

This brief tests **only the second**. Every rule must be frozen and timestamped *before* the scoring window opens, and
the scoring window must be data the rule author has never inspected.

**Why this matters more here than anywhere else.** A "top gainers" list is a selection of the 20 best outcomes from
thousands of candidates. Any feature search conditioned on that selection will find a pattern with near-certainty. The
mechanism, the feature set, and the horizon must be declared first, or the exercise measures nothing but the searcher's
ingenuity.

---

## 1. Required mechanism statement (before any modelling)

One paragraph answering: **why would a name appear on tomorrow's gainer list, and who is on the other side?**

Acceptable mechanisms name a *payer*: forced buying (index inclusion, ETF rebalance, fund flow), information diffusion
lag (news that predictably propagates), liquidity provision (someone must absorb impatient flow), or a known
underreaction (post-earnings drift). "The model found a pattern" is not a mechanism and is rejected at filing.

---

## 2. Pre-registration template (freeze and hash before scoring)

```
BRIEF_ID:            TG-<horizon>-<yyyymmdd>
HORIZON:             daily | weekly | monthly        (test separately — never pooled)
MARKET:              stocks | crypto | both          (separate runs)
DECISION_TIMESTAMP:  exact bar at which the prediction is made (e.g. 15:55 ET, 23:55 UTC)
UNIVERSE:            exact rule + data source + minimum liquidity, as of DECISION_TIMESTAMP
EXCLUSIONS:          price < $X | ADV < $Y | first N days of listing | halted | non-common
FEATURES:            full frozen list, with each feature's computation window ending AT OR BEFORE decision
RANKING_FORMULA:     exact expression, no fitted weights chosen after seeing results
K_SELECTED:          how many names the rule names per period (e.g. 10)
TOP_GAINER_DEF:      exact definition of the target (top 20 by close-to-close % over the horizon, min price filter)
BASE_RATE:           P(random K-name draw from UNIVERSE contains ≥1 top-gainer)  -- must be computed FIRST
PRIMARY_METRIC:      precision@K  and  lift over BASE_RATE
SECONDARY:           hit at 1 / 3 / 5 / 10 ranks; mean rank of the first hit; turnover
KILL_RULE:           lift CI-LB ≤ 1.0  OR  precision@K ≤ BASE_RATE at n ≥ 30 periods
SCORING_WINDOW:      start date .. end date, untouched by feature or threshold selection
```

**The base rate is mandatory and comes first.** Without it, "we found a gainer in 40% of our picks" is a number with no
meaning — if a random draw hits 38% of the time, 40% is noise.

---

## 3. Horizons, tested separately

| Horizon | Decision bar | Target | Why it is a separate study |
|---|---|---|---|
| **Daily** | close of day *t−1* (or 5 min before close) | top 20 gainers of day *t* | dominated by microstructure, news shocks, and gap opens — the hardest and the most crowded |
| **Weekly** | Friday close | top 20 gainers of the next 5 sessions | where momentum and post-earnings drift actually live |
| **Monthly** | month-end close | top 20 gainers of the next month | where the literature is strongest (momentum, PEAD) and where our own data has the most history |

**A rule that works monthly will usually fail daily, and a rule that works daily is usually a liquidity artefact.**
Reporting one number across all three horizons is a rejection criterion.

---

## 4. Both directions — winners *and* losers

The brief requires the loser study run alongside the winner study:

- **Winner task:** predict top-decile forward returns.
- **Loser task:** predict bottom-decile forward returns.

A short-side or avoid-list signal is frequently far more robust than a winner-picking signal, because the mechanism
(deterioration, forced selling, overpricing) is easier to name. **Report both.** A model that predicts losers well and
winners poorly is a useful result, not a failure.

---

## 5. No-look-ahead audit (mandatory, five tests)

| Test | Pass condition |
|---|---|
| **Timestamp assert** | every feature's last input bar ≤ decision timestamp, asserted in code, not by inspection |
| **Progressive rebuild** | recompute the feature set at three historical decision points using only data available then; the values must match what the live rule would have produced |
| **Shuffle placebo** | shuffle the target labels within period; the strategy must collapse to the base rate |
| **Close-to-close check** | if the rule uses the close of the day it predicts, it is a lookup, not a prediction — automatic fail |
| **Universe placebo** | re-run on a universe with the top and bottom liquidity deciles removed; a signal that dies is a microstructure artefact |

---

## 6. Reporting format

Every run reports, per horizon and per direction:

| Metric | Value | CI |
|---|---|---|
| Base rate (random K-draw hits a top gainer) | | |
| Precision@K | | |
| **Lift over base rate** | | **CI required — this is the headline** |
| Mean rank of first hit | | |
| Periods scored | | |
| Turnover and cost at the class band | | |
| Verdict vs the kill rule | | |

**The headline number is the lift with a confidence interval.** Not the hit rate, not the Sharpe of a long-only portfolio
built from the picks, and not an equity curve.

---

## 7. What the honest outcomes look like

- **Lift CI contains 1.0** → no predictive power. This is the *most likely* result and it is a real finding; it kills a
  question instead of leaving it open.
- **Lift CI-LB > 1.0 but below the class cost band** → statistically real, economically dead. Publishable, uninvestable.
- **Lift CI-LB > 1.0 and net of cost above 4.32%** → a genuine candidate. It then faces the full 17-gate sheet, and the
  pre-registered window is spent — no re-tuning on it.
- **Only the loser task works** → useful: an avoid-list is a risk tool even when it is not an alpha source.

---

## 8. Assignment

| Agent | Task | Notes |
|---|---|---|
| GitHub Copilot | data layer: PIT universe, forward-return computation, base-rate calculation | must run before any modelling |
| Zoo Code | daily horizon, winner and loser tasks | the hardest; expects a null |
| Kilo Code | weekly horizon, winner task | where momentum/PEAD live |
| Antigravity swarm | monthly horizon | most history, most literature |
| Operator | pre-registration review + audit of every lift claim | rejects any run without a base rate |

**One rule before anyone starts:** the base rate is computed and filed **first**, in its own commit. A run that reports a
hit rate without a base rate is not reviewed.

*Paper only. Zero capital. Not investment advice.*
