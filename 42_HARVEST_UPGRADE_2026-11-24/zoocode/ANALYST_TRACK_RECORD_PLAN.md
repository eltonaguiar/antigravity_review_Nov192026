# Plan: harvesting analyst picks per asset class, and rating their track record

zoo-savant · 2026-11-24 · companion to `suggested_tracking_schema.sql` and
`free_data_sources_by_asset_class.md`

## 0. The principle

**Win rate is not skill, and it is not profit.** A record is a *distribution*
conditional on (firm, symbol, class, horizon), and it can only be judged against
(a) the base rate for that condition, (b) its own sample size, and (c) its
expectancy under the worst loss rate the data still allows.

The two examples in the request are exactly the case that needs this:

| | A: "97.6% success on BTCUSDT, 1-week holds" | B: "49.4% win rate overall, huge P/L" |
|---|---|---|
observed win rate | 0.976 | 0.494 |
Wilson 95% CI | **[0.874, 0.996]** | [0.450, 0.538] |
loss-rate upper bound (95%, exact) | **0.111** | 1.000 |
expectancy at observed rates | +0.341% per trade | +1.446% per trade |
expectancy if the true loss rate sits at that upper bound | **−1.209% per trade** | −0.036% per trade |
one average loss costs | **22.5 wins** | 0.5 wins |

A's headline is 41 trades with at most a few losses, and if the true loss rate is
11% (still inside the CI) A **loses money**. B has 500 trades, its CI is tight
around 50%, and its expectancy barely moves under the same stress. **B is the more
trustworthy record even though A's number looks better.** A high win rate with a
tiny average win is a short-volatility profile: it looks excellent until one tail
event, and the sample is too small to rule that event out.

So the rating is a **vector, never a single star**, and the UI must show the
sample size next to every number.

## 1. Harvest pipeline (per asset class)

```
source probe ──▶ raw landing (immutable JSON) ──▶ normalise ──▶ action rows
                                                                   │
                                             ┌─────────────────────┤
                                             ▼                     ▼
                                    forward outcomes        source_status
                                 (next-open entry,         (OK / NOT_APPLICABLE /
                                  +21/63/126d, excess)      PLAN_LIMITED / SOURCE_ERROR)
                                             │
                                             ▼
                                   scorecard per (firm, class, symbol, horizon)
```

1. **Probe, don't assume.** Each source is hit once per run and its exact status
   recorded (`source_status`). `No fundamentals data` is `NOT_APPLICABLE`; a 403
   is `PLAN_LIMITED`; a timeout is `SOURCE_ERROR`. These are never collapsed.
2. **Land raw first.** The vendor response is written verbatim (`raw_json`)
   before parsing. Parsing bugs are then re-derivable without refetching.
3. **Normalise grades.** Map Buy/Outperform/Overweight/Accumulate → +1 tier,
   Hold/Neutral/Market Perform → 0, Sell/Underperform/Underweight → −1. Keep the
   vendor's own string too; the mapping is a judgement and must be visible.
4. **Resolve outcomes only from real bars**, at the next open after the action
   date (never the same close), split/dividend adjusted, with the class
   benchmark for excess return. A pick with no bar is `UNRESOLVED`, not skipped.
5. **Per asset class, the signal differs** (see the sources doc): sell-side
   consensus for equities; holdings-weighted for ETFs; credit spread for bonds;
   funding for crypto. Each row carries `metric_type` so a bond's spread is never
   shown in an analyst column.

Coverage today: equities only, firm-level only. **No free source names the
individual analyst** (measured), so the unit of record is the firm until a
licensed feed exists. Store `analyst_name` as NULL, never guessed.

## 2. Rating criteria (what the scorecard shows)

Per `(firm, asset_class, symbol, horizon)` and per `(firm, asset_class, horizon)`:

| Metric | Why | Guard |
|---|---|---|
`n_calls` | everything below is conditional on it | **rank only when n ≥ 30**; below that show "insufficient" |
`hit_rate` + Wilson CI | the raw number and its uncertainty | never show the point estimate alone |
`mean_excess_pct` + bootstrap CI | return vs benchmark, not raw return | a bull market gives everyone a high hit rate |
`expectancy` = p·Ēw − (1−p)·Ēl | the number that decides money | also report `expectancy_worst` using the exact upper bound on the loss rate |
`profit_factor` = Σwins / \|Σlosses\| | B's "gigantic P/L" made concrete | report with n, and cap display when losses are 0 |
`max_dd_pct`, `avg_hold_days` | risk and the horizon actually realised | a "1-week" claim is checked against bars held |
`specificity_z` | is the symbol record better than the firm's own overall? A does well on BTCUSDT -- but how many symbols did the firm call? Multiply it in (Bonferroni / BH) |

**Composite tier** (only computed when n ≥ 30 and the CI lower bound of excess
return > 0):
`TIER-A` = expectancy_worst > 0 and excess CI-low > 0 · `TIER-B` = expectancy > 0
but CI straddles 0 · `TIER-C` = expectancy ≤ 0 or CI-low < 0 · `INSUFFICIENT` otherwise.
A single high-win-rate cell can therefore never be A on its own.

**The pattern table** (`analyst_pattern`): one row per (firm, symbol, class,
horizon_bucket) with `n`, `hit_rate`, `ci`, `avg_hold`, `expectancy`. This is what
"97.6% on BTCUSDT, 1-week holds" actually is -- a *cell*, not a person's skill,
and it is displayed with its n and its multiple-testing-corrected p-value.

## 3. Guardrails learned the hard way

- **Selection effect.** Ranking firms then evaluating the winners on the same data is circular. Rank on a trailing window, evaluate on the next one (`PBO` tooling already exists in the repo).
- **Multiple testing.** With 7 classes × 6 horizons × dozens of firms, some cell will look brilliant by chance. My own HARVEST check found **0 of 71** monthly "revisions" surviving BH at 5%, so the bar must be high.
- **Survivorship.** Firms that stopped covering drop out; keep delisted symbols and dead firms.
- **Look-ahead.** Entry at next open, and the outcome window must not overlap the rating's own revision.
- **Horizon honesty.** Normalise per-day or per-trade before comparing a 1-week BTC call with a 6-month bond call.
- **Base rate.** Sell-side is structurally bullish (~70% buy). Judge against `P(up | class, horizon)`, not against 50%.

## 4. Worked example: A vs B, as stored

```
analyst_scorecard(firm=A, horizon=7d,  n_calls=41,  hit_rate=0.976, mean_excess_pct=?, suppressed=0)
  expectancy 0.341, expectancy_worst -1.209, tier=TIER-B   -- positive point estimate, stress-negative
analyst_scorecard(firm=B, horizon=7d,  n_calls=500, hit_rate=0.494, mean_excess_pct=?, suppressed=0)
  expectancy 1.446, expectancy_worst -0.036, tier=TIER-B   -- near break-even under stress, far tighter
analyst_pattern(firm=A, symbol=BTCUSDT, horizon=7d, n=41, hit_rate=0.976, bh_q=? )
  -- shown with q_value; it is one of many cells, so it is not "A is great at BTC"
```

Both are B-tier on these assumptions, and the display must say so: A's advantage
is unproven at n=41, and B's edge is small but stable. Neither is a person to copy.

## 5. Open questions for the owner

1. Is `success` a winner by price, or a pick closed by the firm? These differ, and the plan above assumes the former.
2. Should the rating cover *firms* or *named analysts*? Free data only supports firms today.
3. Which horizon is the product's default: the firm's stated horizon, or a fixed one?
