# Harvesting analyst & trader picks per asset class — rating criteria and plan

**Status:** SPEC · 2026-11-24 · paper research only, not investment advice
**Companion:** `DATABASE_SCHEMA.md` (the tables this populates)

---

## 0. The problem this solves

Two performers, presented as one leaderboard, are not comparable:

| Profile | Example | What it actually is |
|---|---|---|
| **A** | 97.6% success on BTCUSDT, holds < 1 week | high hit rate, small wins, **negative skew** — one bad tail erases months |
| **B** | 49.4% win rate overall, huge P/L | low hit rate, large wins, **positive skew** — survivable drawdowns, needs patience |

A single "success rate" ranks A above B and is **wrong for almost every purpose**. A single
"P/L %" ranks B above A and hides that B may have made one lucky trade. Neither number is
sufficient, and averaging them produces something that means nothing.

**Rule: rating is two-axis and horizon-specific. Never collapse it to one score.**

---

## 1. Rating model — five dimensions, reported separately

Every rating carries all five. A composite badge is assigned **only** after all five are visible.

| # | Dimension | Metric | Why it exists |
|---|---|---|---|
| 1 | **Reliability** | hit rate with **Wilson 95% CI** | a bare 97.6% on n=41 has a CI of ~86–99.6%; on n=6 it is meaningless |
| 2 | **Magnitude** | expectancy per trade (mean and median), profit factor, payoff ratio (avg win / avg loss) | this is what separates A from B |
| 3 | **Skew / tail** | worst trade, 5% CVaR, max drawdown, longest losing streak, tail ratio | 97.6% hit rate profiles die from one trade; 49.4% profiles die from impatience |
| 4 | **Stability** | expectancy by rolling 6-month window; sign consistency across periods; regime split (high/low vol) | an edge that only exists in one regime is a regime, not an edge |
| 5 | **Sample power** | n, average hold, coverage of the claimed horizon, **number of candidates screened** | screening 5,000 traders manufactures geniuses |

### 1.1 Horizon is a hard partition, not a filter

A 1-week BTC call and a 12-month equity call are **not the same skill** and must never be pooled.

| Bucket | Hold | Minimum n for any badge |
|---|---|---|
| `intraday` | < 1 day | 100 |
| `short` | 1 day – 1 week | 60 |
| `swing` | 1 week – 1 month | 40 |
| `position` | 1 – 3 months | 30 |
| `long` | > 3 months | 20 |

A trader rated on `short` carries **no** rating in `long`. Reporting "97.6% BTCUSDT" without
"1-week horizon, n=41" is the exact misstatement this spec prevents.

### 1.2 Per-asset-class cohorts are mandatory

Statistics are computed **within** `(asset_class, horizon)`. Pooling a crypto scalper with an
equity swing trader means the pool average describes nobody. The database enforces this: a rating
row is keyed on `(trader, asset_class, horizon)`.

### 1.3 The two profiles, scored properly

**Profile A — 97.6% / 1 week / BTCUSDT**
- Reliability: hit 97.6%, Wilson CI depends on n — report it.
- Magnitude: expect payoff ratio **< 0.3** (wins are small). If expectancy is positive but the
  worst trade is −8× average win, the strategy has **negative skew** and a finite risk of ruin.
- Required disclosures: longest losing streak, single worst trade, drawdown, and **what one tail
  event does to the equity curve**.
- Correct label: *high-reliability, negative-skew* — suitable only with strict tail limits.

**Profile B — 49.4% / overall / large P/L**
- Reliability: hit 49.4% is *below* a coin flip; that is normal and not disqualifying.
- Magnitude: payoff ratio must be **> ~2.1** for expectancy to be positive at 49.4%.
- Required disclosures: fraction of total P/L from the top 3 trades. If > 60%, the record is
  **one or two good calls**, not a repeatable method.
- Correct label: *low-reliability, positive-skew* — must survive a "remove the top 3 trades" test.

**Both are legitimate; neither is better without knowing the use case.** The page must show the
profile, not a rank.

### 1.4 Badge ladder (gated, not scored)

| Badge | Requirement |
|---|---|
| **A** | n ≥ bucket minimum · expectancy CI excludes 0 after **Benjamini-Hochberg** · ≥ 2 out-of-sample periods with the same sign · top-3-trade removal still positive |
| **B** | n ≥ bucket minimum · expectancy CI excludes 0 |
| **C** | n ≥ bucket minimum · positive expectancy, not yet significant |
| `INSUFFICIENT_DATA` | below n — **never** a verdict, never ranked |

Additional automatic disqualifiers: undisclosed survivorship (leaderboard-only history), hold time
outside the claimed bucket, or a record that cannot be reconstructed from individual trades.

---

## 2. Where usable histories actually exist, per asset class

The honest map. **Sell-side analyst names exist only for equities** — every other class needs a
different kind of source, and most of them have a survivorship problem.

| Class | Named sell-side? | What can actually be harvested | Bias to disclose |
|---|---|---|---|
| **Equities** | **Yes, paid** (Benzinga, TipRanks, StarMine, Finnhub premium, FactSet) | dated rating actions with firm + analyst, price targets | coverage termination, look-ahead on revisions |
| **Equities (positions)** | No | SEC **13F** quarterly, **Form 4** insider, 13D/G activists | 45-day lag, long-only, $100M threshold |
| **Crypto** | **No sell-side at all** | perp/DEX leaderboards (Hyperliquid, dYdX, CEX copy-trading), on-chain addresses | **leaderboard survivorship is severe** — only winners stay visible and public |
| **FX** | No free names | bank forecast surveys (paid), CFTC COT (aggregate, not named) | COT is not attributable to a person |
| **Bonds / credit** | Issuer-level credit ratings only | ratings migrations, spreads | no per-analyst history |
| **ETFs / funds** | No | holdings-weighted look-through (see `fund_lookthrough`) | derived, not a published rating |
| **Commodities** | No per-commodity analyst | COT, inventories, bank forecasts (paid) | — |
| **Prediction markets** | n/a | resolved market history → **Brier score, log loss, calibration** per participant | thin markets, self-selection |
| **Options** | No | IV rank, skew, flow (aggregate) | not attributable |

**Consequence:** the "97.6% on BTCUSDT" example is not an analyst at all — it is a **trader** from a
leaderboard or on-chain. That source class must be modelled separately from sell-side analysts,
because its biases are different (disclosed positions vs. self-reported performance).

---

## 3. Harvest pipeline

```
ingest trades/actions  ->  normalise to one schema  ->  bucket by (asset_class, horizon)
        ->  compute the five dimensions per (trader, class, horizon)
        ->  shrink small samples, correct for multiple testing
        ->  assign badge or INSUFFICIENT_DATA
        ->  publish profile (never a bare rank)  ->  track forward in picktrack_*
```

**Normalisation record** (one row per action, from any source):

```
{source, source_type: sell_side|13f|insider|leaderboard|onchain|prediction,
 trader_id, firm, symbol, asset_class, side,
 entry_ts, entry_price, exit_ts, exit_price, hold_seconds,
 size, fees_bps, disclosed_at, retrieved_at, source_url, survivorship_flag}
```

**Small-sample shrinkage** (mandatory below n=100):
`alpha_shrunk = (n*alpha_raw + k*alpha_universe) / (n + k)`, `k ≈ 30`.

**Multiple testing**: rank N candidates → require BH correction at q=0.05 and report
`DSR = f(sharpe, n, trials)`. State the trial count out loud; it is the penalty input.

---

## 4. The "reverse-engineer a pattern" question — how to do it without fooling yourself

Feasible, but only as **hypothesis generation** with a control group.

1. Take a trader's entries and label each with features knowable **at entry time** (time of day,
   volatility regime, distance from VWAP, funding rate, recent return, volume percentile).
2. Build a **control set**: random entries in the same symbol, same regime, same hours, same
   frequency.
3. Test whether the trader's feature distribution separates from control (KS test / classifier AUC
   with purged CV). If AUC ≈ 0.5, there is no pattern to reverse-engineer — they may simply have
   been right.
4. Any extracted rule must then be **forward-tested** on unseen data, with the trial count from
   step 1 declared up front, and must clear DSR + PBO + a permutation control before it is called
   anything other than a description of the past.

**Hard limit:** 13F gives 4 snapshots a year. Mining a "pattern" from quarterly long-only filings
is describing the past with a 45-day lag. It cannot honestly be called an edge.

---

## 5. What the page shows

Per trader/analyst row: **name · source · class · horizon · n · hit rate ± CI · expectancy ·
payoff ratio · max drawdown · badge**. Expandable to: best and worst trade, top-3-trade dependency,
regime breakdown, and the raw action list with timestamps.

Above the table, permanently:

> Ratings are per asset class **and** per holding period. A high hit rate with small wins and a low
> hit rate with large wins are different products, not better and worse ones. Sample size below the
> bucket minimum is `INSUFFICIENT_DATA` and is never ranked.

---

## 6. Acceptance gates before anything is published

- [ ] every rating row carries `asset_class` + `horizon` + `n`
- [ ] hit rate always shown with a Wilson CI
- [ ] expectancy shown with median and profit factor, never hit rate alone
- [ ] top-3-trade dependency computed; > 60% flags the row
- [ ] survivor flag set for leaderboard-only histories
- [ ] badge requires BH-corrected significance **and** stability across ≥ 2 periods
- [ ] trial/screening count recorded and used in the DSR penalty
- [ ] a clean `INSUFFICIENT_DATA` result is published as such, not hidden

---

## 7. Build order (cheapest evidence first)

1. **Freeze the schema** — `trader`, `trader_action`, `trader_rating(class, horizon)`.
   *(The DB already has `analyst_registry` / `analyst_actions`; extend with `horizon` and the
   five dimension columns rather than adding parallel tables.)*
2. **Crypto leaderboard prototype** — it is the only class where a per-trader history is obtainable
   without a paid licence, and it directly serves the BTCUSDT example. Ingest one venue, compute the
   five dimensions on one horizon, publish with the survivorship flag set.
3. **Equity sell-side** — blocked on a paid-feed + redistribution decision. Do not build on
   assumed access.
4. **13F / Form 4** — free, but lagged; use for hypothesis generation, label the lag on every row.
5. **Prediction markets** — resolved history gives a genuinely clean scoring surface (Brier,
   calibration) with no survivorship in the scoring itself.

---

## 8. Reconciliation with Kilo's rating vector (2026-11-24)

Kilo published an independent rating vector (branch work `b49ae2d`). Two of its ideas are
**strictly better than mine and have been adopted** into `trader_rating`:

| Their idea | Why it beats what I had | Column added |
|---|---|---|
| `expectancy_worst` - recompute expectancy at the **Wilson upper bound of the loss rate**, not the point estimate | My "remove the top 3 trades" test was a heuristic. Theirs attacks the real uncertainty: with few trades you do not know your loss rate, and the worst plausible rate is what decides survival. | `loss_rate_upper`, `expectancy_worst_bps` |
| Survival tiers instead of letter grades | `A_SURVIVES_STRESS / B_POSITIVE_BUT_TAIL_UNPROVEN / C_NO_EDGE / INSUFFICIENT_N` names the **failure mode** rather than grading the performer | `tier`, `tier_score` |

Kept from my spec: the hard `(asset_class, horizon)` partition, the Wilson CI on hit rate, the five
separate dimensions, `top3_dependency_pct`, and the per-pick-type minimum n.

### 8.1 Independent check of their worked example

The conclusion reproduces. Verified here from first principles:

**Profile A - 97.6% on n=41 (one loss in 41), one average loss ~22 average wins**
- point loss rate 2.44%; Wilson 95% CI **[0.43%, 12.60%]**
- break-even loss rate implied by a 22:1 loss/win ratio = **1/(1+22) = 4.35%**
- the point estimate sits *below* break-even, the **upper bound sits far above it**
- therefore at n=41 the record **cannot statistically distinguish a winning strategy from a losing
  one**. Tail stress fails. Kilo's `WATCH` tier is correct.

**Profile B - 49.4% on n=500, profit factor 2.03**
- implied payoff ratio (avg win / avg loss) = **2.079**
- loss-rate CI **[46.2%, 55.0%]**; expectancy at the upper bound = `(1-0.55) - 0.55/2.079 = +0.186`
  in units of average win, so it stays **positive**. Kilo's `A_SURVIVES_STRESS` is correct.

Their exact percentages (-1.57% / +1.23% per trade) depend on the win/loss magnitudes in their
ledger, which has not been published with a hash. **Direction and tiering confirmed; the point
figures remain unverified** until that ledger is shared - the same request made to Zoo.

### 8.2 The rule this section adds

> A hit rate is uninterpretable without the loss magnitude. Test survival at the **upper** bound of
> the loss rate, never the observed rate. If the bound crosses break-even the record is
> `B_POSITIVE_BUT_TAIL_UNPROVEN` at best, however good the point estimate looks.

---

## 9. Ranking rule — correcting my own tie-break (Zoo's counterexample, 2026-11-24)

Zoo constructed a case that **breaks the design as originally written**, and it reproduces:

| Candidate | n | win rate | point expectancy | expectancy at loss-rate upper bound | two-axis tiers |
|---|---|---|---|---|---|
| **TAIL** | 41 | 97.6% | **+53.66 bps** | **−129.16 bps** | A / A |
| **BORING** | 400 | 52.5% | +36.25 bps | **+26.46 bps** | A / A |

Both score "A on both axes", so the rule ties and breaks the tie on point expectancy — which puts
**TAIL first**, even though TAIL's own 95% interval admits a loss rate that makes it lose money and
BORING survives its worst case. The two axes are not independent, and any tier collapse discards
that correlation.

**The correction:** the ordering key is `expectancy_worst_bps` — the stress-case number — and
**never** point expectancy. Specifically:

1. Never tie-break on point expectancy. Ever.
2. Where a single order is required, sort by `expectancy_worst_bps` descending.
3. Where possible, do not collapse at all: present the Pareto frontier of
   (reliability, expectancy_worst) and let the reader see both numbers.
4. A candidate whose `expectancy_worst_bps` is negative is **not rankable**, whatever its badges
   say. It is reported as `B_POSITIVE_BUT_TAIL_UNPROVEN` with the stress number visible.

This is a better rule than the one I wrote, and it came from peer review rather than from me.
