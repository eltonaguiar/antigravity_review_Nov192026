# Design — Simulation of endorsed picks from high-performing analysts

**Status:** SPEC (not built) · **2026-11-24** · hypothetical research only, not investment advice
**Owner:** to be assigned · **Depends on:** firm-level dated analyst actions (see §1)

---

## 0. The question this answers

> If we had only taken the most recent endorsed picks from the analysts who have actually been
> right, what would that portfolio have done?

That is a **track-record-filtered event-study portfolio**. It is different from everything the
harvest page currently does: today the page reports a consensus *snapshot* with no analyst
identity and no action dates. You cannot filter by track record without identities and dates.

---

## 1. Hard dependency — state this before building anything

| Tier | Data | What it enables | Cost |
|---|---|---|---|
| **T0** | Monthly consensus distribution per symbol (current feed) | Consensus-momentum simulation only. **No analyst identity, no action dates, no firm-level P/L.** | free |
| **T1** | Firm-level dated actions: `{symbol, firm, analyst, action, rating_from, rating_to, pt_from, pt_to, action_date, action_time, source}` | The analyst scorecard, the track-record filter, and the portfolio simulation | paid or one-time historical backfill |

**The free Finnhub recommendation-trend endpoint returns a four-month distribution. It cannot
produce a single firm-level action.** Any design that claims to filter "analysts with a track
record" from T0 data is fabricated. Ship T0 as an explicitly-labelled proxy, or buy T1.

---

## 2. Analyst scorecard — the filter

Computed per `(firm, analyst)` over a **point-in-time** trailing window (never future data):

```
r_i(h)   = total_return(symbol_i, t0 -> t0+h)
b_i(h)   = total_return(sector_ETF, same window)          # SPY fallback
alpha_i  = d_i * (r_i - b_i)      d_i = +1 upgrade/buy, -1 downgrade/sell, 0 reiterate
hit_i    = 1[alpha_i > 0]
```

Reported per horizon `h ∈ {1M, 3M, 6M, 12M}` and "to next action":

- `n_actions`, `hit_rate` **with Wilson 95% CI** (never a bare "83%" on n=6)
- mean / median `alpha`, t-stat, information ratio
- price-target skill: `PT_MAE% = |PT - P(t0+h)| / P(t0)`, `PT_hit_rate`, and optimism bias
- **calibration / monotonicity**: does Strong Buy beat Buy beat Hold beat Sell? Non-monotonic
  skill is noise.
- **shrunk alpha**: `alpha_shrunk = (n*alpha_raw + k*alpha_universe)/(n+k)`, `k≈30`
- percentile rank within sector and coverage bucket
- **reliability badge**, gated by n and by significance after multiple-testing correction:

| Badge | Requirement |
|---|---|
| **A** | n ≥ 50 and shrunk alpha CI excludes 0 after BH at q=0.05 |
| **B** | n ≥ 25 and CI excludes 0 |
| **C** | n ≥ 15, not yet significant |
| insufficient | n < 15 — renders as `INSUFFICIENT_DATA`, never as a verdict |

---

## 3. Portfolio construction (pre-registered, frozen before looking at results)

- **Eligibility:** analyst holds badge A or B **as of the action date** (no future knowledge).
- **Entry:** long the symbol on the next tradable open after a BUY/upgrade from an eligible
  analyst. **Lag-1, never the same close.**
- **Exit:** first of (a) a downgrade to Hold or below by any eligible analyst, (b) 12 months
  elapsed, (c) stop at -20% (pre-registered, not tuned).
- **Sizing:** equal weight across active names, **5% cap per name, 20% cap per sector**.
- **Overlap:** five analysts endorsing one name in one month is **one position**, not five.
  Record `endorsement_count` as a feature, not as extra size.
- **Rebalance:** monthly, on the first trading day of the month.
- **Costs:** **26 bps round turn** (the estate standard), applied on every entry and exit.
  Sensitivity at 52 and 78 bps must also be published.
- **Benchmark:** sector ETF (SPY fallback). Report both raw and excess.
- **Universe:** US large/mid cap with ≥ 20 covering analysts (same as the harvest page, so the
  two pages are comparable).

---

## 4. Validation gates — no exception, no lowered bar

1. **≥ 100 closed trades** before any performance claim.
2. **Stationary bootstrap** CI on mean alpha that **excludes zero**.
3. **Deflated Sharpe Ratio** with the trial count **pre-registered** — the number of variants
   actually run (badge threshold × horizon × sizing × stop) is the penalty input.
4. **PBO via CSCV** — the probability the in-sample best underperforms out of sample.
5. **Permutation control:** reassign the same actions to random symbols, preserving dates and
   counts, 1,000 draws. If the real result sits inside that null, there is no edge.
6. **Benjamini-Hochberg** across all variants evaluated.
7. Any walk-forward claim must carry `folds`, `split_basis`, `test_window_bars`, `purge_bars`.
8. **Split-half persistence** (the real test of "high-performing"): rank analysts on the first
   half of history, measure the A-badge group on the second half. If the ranking does not
   persist, the filter is measuring luck.

---

## 5. Monte Carlo programme

| # | Component | What it answers |
|---|---|---|
| MC1 | **Skill persistence** — bootstrap analyst histories, rank on half 1, score on half 2 | Is "high-performing" a stable property or one lucky month? |
| MC2 | **Entry jitter** — shift every entry ±1 trading day | Does the result depend on an unrepeatable fill? |
| MC3 | **Symbol luck** — resample symbols within sector | Is the P/L concentrated in one name? |
| MC4 | **Cost stress** — 26 / 52 / 78 bps | Does the edge survive realistic friction? |
| MC5 | **Null actions** — random ratings on the same dates | Is the signal distinguishable from random endorsement? |
| MC6 | **Coverage termination** — censor actions near coverage drop | Does survivorship of analysts create the result? |

Report every MC as a distribution (min / median / p95 / max), never a single point.

---

## 6. Biases that must be printed on the page

1. **Market beta** — excess returns and year fixed effects, or the number is just "the market went up".
2. **Analyst survivorship** — analysts quietly stop covering losers; terminated coverage must be included.
3. **Look-ahead** — as-published timestamps, as-of prices, never revised data; start the clock at the next print.
4. **Clustering** — 40 analysts on one name in one month is one bet; cluster SEs by symbol-month.
5. **Multiple testing** — ranking 5,000 analysts manufactures geniuses; FDR-correct and say "not distinguishable from luck" where true.
6. **Reiteration spam** — weight initiations and rating changes above maintenance notes.
7. **Costs** — every P/L must read "hypothetical, equal-weight, event-study, net of 26 bps, no slippage beyond that, no taxes".

---

## 7. What the page shows (new tab: "Endorsed picks — proven analysts")

**Filter bar:** reliability badge (A/B/C), min actions (≥ n), sector, horizon, min coverage,
and a `Show insufficient-data analysts` toggle (default off, count shown).

**Table:** analyst / firm · n · hit rate ± CI · avg excess alpha · PT skill · last action ·
badge chip. Every row expandable to its best and worst call with dates.

**Simulation panel:** equity curve vs benchmark, CAGR, Sharpe, max drawdown, turnover,
closed-trade count, cost drag, and a **gate status** row (`n trades`, `CI`, `DSR`, `PBO`) that
reads PASS / FAIL / INSUFFICIENT per gate rather than a single verdict.

**Empty state (T0 only):** *"No analyst-level track record is available from the current feed.
What we can show today is consensus momentum — see the proxy tab. Analyst identity and action
dates require a firm-level feed."* That is honest and still useful.

---

## 8. The cheap first experiment (buildable today, clearly labelled)

**T0 consensus-momentum proxy** — tests whether consensus *change* has signal, without
pretending to identify analysts:

- Signal: `Δ buy_side` between consecutive monthly snapshots, using the existing feed.
- Entry: long names in the top decile of improvement, next month's first open, hold one month.
- Benchmark: sector ETF; 26 bps round turn.
- Gates: the same §4 list, with the trial count declared up front (this is 1 trial, not 50).
- Label on the page: **"Consensus change, not analyst skill."**

This is a weekend of work on data already in the repo, and it either produces a defensible null
or the first real candidate. It does **not** answer the track-record question — nothing free does.

---

## 9. Definition of done

- [ ] T1 feed decision recorded (buy vs backfill vs skip), with the exact fields available
- [ ] scorecard computed point-in-time, badges assigned, split-half persistence measured
- [ ] simulation run under all six MC components, all gates reported honestly
- [ ] every number labelled hypothetical with costs stated
- [ ] page tab live with filters, gate row, and the honest empty state for T0
- [ ] a clean negative result is an acceptable outcome and is published as such
