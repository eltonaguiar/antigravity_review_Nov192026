# PRE-REGISTRATION — do ANY brokerage's upgrades predict forward returns?

Status: **PROPOSED, NOT YET RUN.** Locked before any return is computed, which is the point.
Source of design: four independent models (ChatGPT-6 Luna, Claude, Qwen3.6 Flash, GLM 5.3 Flash)
answered the same prompt independently. Consensus is recorded as consensus; splits are resolved
below with a stated reason, and two of their claims are corrected by arithmetic.

---

## 0. THE FEASIBILITY FACT THAT CONSTRAINS EVERYTHING

All four designs specify a minimum event count (300 / 500 / 750 per brokerage) and none checked
whether the data can supply it. Measured, via Yahoo `upgradeDowngradeHistory`, **30 mega-caps,
30/30 responded**:

| measure | value |
|---|---|
| distinct firms | **175** |
| total actions | **19,880** |
| changes only (`up`/`down`/`init`/`reit`) | **5,220** |
| firms reaching 300 changes | **0** |
| firms reaching 500 changes | **0** |
| firms reaching 750 changes | **0** |
| highest single firm | RBC Capital, 234 changes (of 603 actions) |

**The binding constraint is ticker breadth, not history length.** Per-ticker rate for the top
firms is ~7–8 changes per ticker:

| firm | changes | changes / ticker | tickers needed for 300 | for 750 |
|---|---|---|---|---|
| RBC Capital | 234 | 7.8 | ~39 | ~96 |
| Wedbush | 230 | 7.7 | ~39 | ~98 |
| Cantor Fitzgerald | 215 | 7.2 | ~42 | ~105 |
| Needham | 211 | 7.0 | ~43 | ~107 |
| Morgan Stanley | 164 | 5.5 | ~55 | ~137 |
| Goldman Sachs | 115 | 3.8 | ~78 | ~196 |

Consequence: **a 30-name universe cannot clear any floor.** A run must ingest several hundred
tickers from each broker's actual coverage before the question is even askable. Any analysis
published before that is a statement about 30 large caps, not about the broker.

Second consequence, and it cuts against the obvious choice: the bulge-bracket names the models
favoured most (Goldman, Morgan Stanley, JPMorgan) have among the **lowest** event counts here —
Goldman 115 changes against RBC's 234 on the same 30 names. Naming only GS/MS/JPM tests the
hardest case twice and the most-likely case not at all.

---

## 1. WHAT ALL FOUR AGREED ON (adopted as-is)

1. **Entry at the NEXT session's open** after the action date — lag-1, never same-close.
2. **Exclude initiations, reiterations, and target-price-only changes.** An upgrade is a strict
   ordinal rank increase on that broker's own scale.
3. **Freeze the grade→ordinal mapping before looking at returns.** Record the mapping as an artifact.
4. **Dedup overlapping events** per broker-ticker (Luna 126 sessions, Claude 30 days, GLM 21 days).
5. **A characteristic-matched benchmark, not a single index.** Unanimous — none used SPY.
6. **Two-way clustering**: ticker/issuer × calendar date-or-month. Unanimous.
7. **Cost is deducted before the statistic**; the decision variable is net, never gross.
8. **Pass = one-sided 95% lower confidence bound > 0.**
9. **"Insufficient sample" is a distinct outcome from "no effect."** Never report one as the other.
10. **Pre-register, then evaluate on a holdout** that was not used to choose anything.

Note that item 5 is a rejection of our own house convention: every mark in `picktrack_marks` is
measured against a single benchmark, which cannot separate "this broker adds information" from
"this broker covers high-beta names."

---

## 2. WHERE THEY SPLIT, AND HOW IT IS RESOLVED

### 2.1 Horizon — 21 trading days primary; 5 and 63 reported, not decision-bearing
Luna said 126 sessions; the other three said 20–21 days. Majority wins on the argument, not the
vote: a single rating change is a discrete information event, and a 6-month window accumulates
unrelated factor and news exposure that cannot be attributed to the grade. 21d primary,
secondary horizons reported for shape but never used to pass or fail.

### 2.2 Minimum sample — 750 events per broker
Claude's figure is the only one derived rather than asserted, and the arithmetic reproduces:

```
n = (z_0.995 + z_0.80)^2 * sd^2 / delta^2
  = (2.576 + 0.842)^2 * 8^2 / 1^2
  = 747.5   -> Claude said "about 750"   REPRODUCES
```

GLM's stated "~1.5–2%" minimum detectable effect at n=300 with sd=12% does **not** reproduce:
the actual MDE is **2.19%** (one-sided p<0.01, 80% power) or 2.37% two-sided. So GLM's own floor
would let through effects twice the size it claimed to detect. Using sd=12% uniformly:

| floor | MDE at sd=12% |
|---|---|
| 300 (GLM) | 2.19% |
| 500 (Luna, Qwen) | 1.70% |
| 750 (Claude) | 1.39% |

Adopted: **750 events, 150+ distinct entry dates, ≥24 months**, with the MDE published alongside
whatever is found, so a null is quantified rather than asserted.

### 2.3 Cost — spread-based, with a floor
Luna's flat 50bp and Qwen's flat 30bp are both guesses. Claude's `max(10bp, 0.5 × median quoted
spread over days −20..−1)` and GLM's `Corwin–Schultz effective spread + 10bp impact` are measured.
Adopted: **Corwin–Schultz high-low estimator + 10bp impact**, falling back to Claude's
half-spread rule when the estimator is undefined. Rationale: we already know a flat constant
distorts by class — the flat 26bp overcharged BOND by 42× and undercharged CRYPTO 2× — so a flat
50bp would repeat a mistake we have already measured.

### 2.4 The falsifier — GLM's within-ticker placebo, adopted as primary
| model | falsifier | verdict |
|---|---|---|
| Luna | simultaneous 95% UCB of the **best** broker ≤ 0 kills "any works" | good, but only tests the best |
| Claude | holdout UCB of net alpha ≤ 0 | equivalent to Luna's |
| Qwen | clustered t < 1.96 | **far weaker** — no placebo, α=2.5% on one coefficient |
| GLM | **within-ticker date-swap placebo, 1,000 pseudo-dates, kill if actual ≤ p95** | **strictest** |

Adopted: GLM's placebo as the primary falsifier, Luna's UCB rule as the reported secondary.
The reason is specific: the placebo draws pseudo entry dates **for the same ticker**, so it
contains that stock's own drift, seasonality, and characteristic exposure. If knowing *that this
broker acted on this day* does not beat the stock's ordinary behaviour on random days of the same
calendar months, then the "prediction" was stock selection the placebo already contains. That is
the same confound our selection-null gate was built to catch, expressed better.

---

## 3. DEFECTS FOUND IN THEIR ANSWERS

1. **Qwen3.6 reintroduces lookahead.** "Enter at the closing price on `date`" — if the rating
   moved during the session, the closing price is not an executable entry given date-only
   granularity. This is the exact defect our house rule forbids. Its entry rule is **rejected**.
2. **Qwen3.6's cost is internally inconsistent.** "30 basis points one-way" then "deducted once
   from the holding-period return" — 30bp one-way is 60bp round turn, not 30bp.
3. **GLM's MDE is overstated**, as shown in 2.2.
4. **All four assumed event counts exist.** Section 0 measures that they do not at 30 tickers.
5. **None specified what happens when a broker changes its scale mid-sample.** GLM alone addressed
   it (drop days where >20% of coverage is re-graded); adopted.

---

## 4. THE SPEC, FROZEN

- **Universe:** each broker's real coverage, several hundred tickers, US common stock, price ≥ $5,
  60-day median dollar volume ≥ $5M, not halted at entry.
- **Event:** strict ordinal upgrade on the broker's frozen scale; `action` in `up` only;
  no `init`/`reit`/target-only. Drop re-grading days (>20% of coverage changed same day).
- **Dedup:** one event per broker-ticker per rolling 21 trading days, first wins; skip if that
  broker changed the rating either direction within the prior 10 trading days.
- **Entry:** open of the first session **strictly after** the action date. Non-negotiable.
- **Horizon:** 21 trading days, entry open → exit close. 5d and 63d reported only.
- **Benchmark:** DGTW-style characteristic match, size × industry-adjusted book/market × 12-2
  momentum, identical calendar window; BHAR winsorized 1%/99%. FF5+momentum residual as robustness.
- **Cost:** Corwin–Schultz effective spread + 10bp impact, subtracted from every BHAR. No
  gap-size exclusions — you buy the open you get.
- **Inference:** two-way clustered SEs on net BHAR, by entry date and by ticker; day-block bootstrap
  cross-check; one active event per ticker at a time.
- **Minimum:** 750 clean events, 150+ distinct entry dates, ≥24 months. Otherwise **underpowered**,
  with equivalence bounds reported.
- **Pass (all three):** mean net BHAR ≥ +1.0%; one-sided clustered p < 0.01; actual mean exceeds
  the 95th percentile of the within-ticker date-swap placebo.
- **First three brokers:** one bulge bracket for volume and hardest-case honesty (**Goldman Sachs**
  or **Morgan Stanley**), one high-cadence mid-cap house for event count (**RBC Capital**, **Wedbush**,
  or **Cantor Fitzgerald** — the three highest measured change counts), and one small-cap specialist
  where an effect is most plausible and most likely to be underpowered (**Needham**, 211 measured
  changes, named by Claude). Testing only the three largest firms answers the question for the
  three firms least likely to differ from the market.

---

## 5. WHAT WOULD MAKE ME REPORT A POSITIVE

Only a net-of-cost, characteristic-adjusted, placebo-beating result on a holdout the design never
touched, at n ≥ 750, with the MDE published. Anything less is reported as underpowered or negative.
A clean negative here is a real result: it would say that a dated, public, widely-distributed
rating change carries no tradable information at 21 days after cost — which is worth knowing and
is the prior I would bet on.
