# Executive summary — database state and performance, 2026-11-24

Second programme, first read of the live database. Every number below comes from `ejaguiar1_stocks` on
`mysql.50webs.com` (**463 tables**), queried read-only today. Nothing here is a projection.

---

## 1. Do we already have edge?

**Not proven — but this is the first genuinely positive result in either programme, and it was invisible
until now because the benchmark was never computed.**

The portfolio engine ran **123 model portfolios** from **2026-05-29 to 2026-11-24** (179 days). To judge
them you have to know what the market did. Nobody had computed it: **`benchmark_series` has 0 rows.**

So I computed it from `daily_prices` over the exact same window:

| Benchmark | Return | Max drawdown |
|---|---:|---:|
| **SPY** | **−4.52%** | −7.29% |
| QQQ | −11.82% | −14.30% |
| IWM | −8.50% | −11.55% |
| TLT | −4.75% | −6.59% |
| GLD | **−20.16%** | −20.16% |

**The market fell.** Against that:

| Cohort | n | Median | Best | Worst | Positive |
|---|---:|---:|---:|---:|---:|
| All portfolios | 123 | **−0.52%** | **+7.58%** | −156.65% | **24 (20%)** |
| aggressive | 41 | −16.14% | +7.58% | −156.65% | 3/41 |
| balanced | 41 | −0.50% | +4.68% | −7.87% | 10/41 |
| conservative | 41 | −0.07% | +0.46% | −1.79% | 11/41 |

**Relative to SPY (−4.52%):** the median portfolio beat it by **+4.0 pp**, the best by **+12.1 pp**, and
24 of 123 were positive while every equity benchmark was negative.

**But do not call that an edge yet, for one arithmetic reason:** in a falling market, holding cash wins
without any skill. Cash (T-bills at ~4.4%) returned roughly **+2.2%** over these six months. So:

- best portfolio **+7.58%** → beats cash by **+5.4 pp** (real, but n=1)
- median portfolio **−0.52%** → **loses to cash by 2.7 pp**

**Verdict: relative outperformance versus equities, underperformance versus cash, one standout portfolio.**
The honest statement is "the ensemble is defensively positioned and that positioning paid off in a down
tape" — which is beta management, not demonstrated alpha. Whether the top decile's outperformance is
*persistent* is a testable question and the single most valuable next probe (see §7).

## 2. What is actually being tracked

| Thing | Count | Where |
|---|---:|---|
| Model portfolios | **123** | `PF_PORTFOLIO` |
| NAV snapshots | 14,839 | `PF_NAV_SNAPSHOT` (2026-05-29 → 2026-11-24) |
| Daily risk metrics | 14,839 | `PF_DAILY_METRICS` (14,641 have a computed profit factor) |
| Resolved pick outcomes | **63,783** | `at_pick_outcomes` |
| Pick signals | 152,136 | `trading_picks` |
| Portfolio positions | 5,843 (452 open across 97 portfolios) | `PF_POSITION` |
| Insider transactions | **10,735** across 119 tickers | `gm_sec_insider_trades` |
| Distinct symbols with outcomes | **533** | `at_pick_outcomes` |
| Distinct symbols with picks | 837 | `trading_picks` |

Asset classes covered: CRYPTO, FOREX, COMMODITY, EQUITY, FUTURES, INDEX, ETF, BOND, MEME, PENNY, STOCKS,
UNKNOWN. Open positions are currently bond-heavy: `^TNX` (25), `^TYX` (22), `IEF` (15), `BND` (13),
plus `IWM` (20), `GC=F` (15), `SI=F` (15).

## 3. Are the instruments performing well?

Resolved outcomes by asset class (`at_pick_outcomes`, pnl_pct not null):

| Class | n | Avg | Win rate | Total |
|---|---:|---:|---:|---:|
| CRYPTO | 38,204 | +0.029% | 32.3% | **+1,109.3** |
| FOREX | 16,039 | +0.056% | **7.4%** | **+903.5** |
| COMMODITY | 5,882 | −0.103% | 5.9% | −606.9 |
| EQUITY | 1,984 | −0.088% | 4.6% | −175.3 |
| FUTURES | 473 | +0.068% | 3.4% | +32.3 |
| MEME | 106 | −2.008% | 21.7% | −212.8 |
| UNKNOWN | 141 | −2.021% | 37.6% | −285.0 |

By resolution status: **WON 13,652 at +3.018%**, **LOST 19,426 at −2.012%**, **EXPIRED 29,659 at −0.047%**.

Per-trade expectancy on the WON/LOST population:
`0.413 × 3.018 − 0.587 × 2.012 = +0.066%` — **positive but thin**, and 46% of all outcomes are EXPIRED
(essentially a wash), so the tradable subset is a minority of the book.

**The FOREX row is a red flag, not a success.** A 7.4% win rate with a *positive* average return means the
rare winners are enormous relative to the frequent losers — the signature of a take-profit set far from
entry and a stop set very close. That is a payoff-skew configuration, not predictive skill, and it will
break the first time a winner does not arrive.

## 4. Was there a profit window?

Yes, and it has already closed.

| Month | n | Sum PnL | Avg | Win rate |
|---|---:|---:|---:|---:|
| 2026-11 | 5,120 | **−3,160.4** | −0.617% | **25.0%** |
| 2026-10 | 4,305 | +1,092.0 | +0.254% | 44.3% |
| **2026-09** | 4,776 | **+3,641.5** | **+0.762%** | **52.6%** |
| 2026-08 | 4,979 | +1,754.2 | +0.352% | 41.1% |
| 2026-07 | 3,208 | −928.4 | −0.289% | 29.3% |
| 2026-06 | 3,478 | +633.7 | +0.182% | 44.7% |
| 2026-05 | 1,900 | +241.2 | +0.127% | 39.8% |
| 2026-04 | 1,542 | +341.7 | +0.222% | 42.9% |
| 2026-03 | 918 | −460.6 | −0.502% | 36.8% |

**The window was August–October 2026, peaking in September (+3,641, 52.6% win rate).** November is the
worst month on record: **−3,160 at a 25.0% win rate**, giving back most of September in three weeks.

That is a regime-dependent edge — it worked while it worked. Nothing here shows persistence across regimes,
and the September peak followed by a November collapse is exactly the pattern that a single-regime backtest
mistakes for skill.

## 5. Is TP/SL working?

**Mechanically yes — the plumbing is sound.** From `trading_picks`:

| Exit | n | Avg PnL |
|---|---:|---:|
| TP_HIT | 2,361 | **+4.294%** |
| SL_HIT | 2,472 | **−3.869%** |
| TIME_EXIT_MAX_HOLD | 31,421 | +0.036% |
| TIME_EXIT | 460 | +0.699% |
| RESOLVE_FAILED_MAX_RETRIES | 1,664 | 0.000% |
| (still open) | 103,753 | — |

- **TP hit rate among resolved TP/SL pairs: 48.9%** (2,361 of 4,833)
- **Expectancy: 0.489 × 4.294 − 0.511 × 3.869 = +0.123% per trade** — positive, small, before fees
- **Stop-first discipline is being applied**: intrabar resolution records 8,755 `SL_HIT` against 5,400
  `TP_HIT`, i.e. when a bar contains both levels the stop is taken. That is the conservative and correct
  choice, and it is the reason the equity curve is not wildly optimistic.

At a 26 bp round turn, **+0.123% gross leaves ~−0.14% net** — the TP/SL structure is currently **below
its own cost of trading**. That, not signal quality, is why the equity curves are flat.

## 6. Defects found in the database (all verified today)

1. **`paper_trades` is dead.** 16,165 rows, **every one still `open`**, `return_pct = 0` on all, no
   `exit_reason`, `avg_hold = 0 days`. Nothing has ever resolved. Any report drawing on this table is
   drawing on nothing.
2. **`benchmark_series` is empty (0 rows)** — the reason no one could say whether performance was good.
   The comparison has to come from `daily_prices`, which does hold SPY/QQQ.
3. **NAV goes negative.** `pf15` (deepseek_r1 aggressive) ends at **−$501**, `pf54` (together_deepseek_v3
   aggressive) at **−$56,648**, a **−156.65%** return. Negative equity means the engine kept sizing after
   ruin — there is no liquidation floor.
4. **Yield indices are held as positions.** 47 open positions sit in `^TNX` (10-year yield) and `^TYX`
   (30-year yield). These are **quote indices, not tradable instruments**; a position in them cannot be
   executed or marked. `IEF`/`BND`/`TLT` are the tradeable equivalents.
5. **`PF_DAILY_METRICS` contains impossible values** — `max_dd = −6.2824` (i.e. −628%) and `cagr = 10.0`
   (1000%) on `pf59`. A drawdown cannot exceed 100%; these fields are unguarded.
6. **`analyst_actions` is empty (0 rows)** — the analyst data the research programme uses lives elsewhere
   (`at_local_picks`, 76.2 M rows), so the two programmes are reading different sources.

## 7. Does this make an edge more likely?

It changes the question from "is there any signal" to **"is the top cohort's outperformance persistent"** —
which is answerable with data already in the database:

1. **Rank all 123 portfolios by return in the first half of the window, then measure the second half.**
   If rank persists, the engine has skill. If rank mean-reverts, the +7.58% was luck. This is a
   cross-sectional persistence test, the same construct the analyst programme uses, and it needs no new
   data.
2. **Compare every portfolio to cash, not only to SPY.** Cash returned ~+2.2%. On that benchmark only
   **~10 of 123** portfolios did anything.
3. **Fix the four defects before any of it is quoted** — dead `paper_trades`, empty `benchmark_series`,
   negative NAV, yield-index positions.
4. **The insider data already exists here** (10,735 transactions, 119 tickers, 205 purchases, properly
   flagged `is_officer` 5,955 / `is_director` 3,309). The Form 4 probe should read this table rather than
   re-scrape SEC — it is cleaner and already point-in-time.

## Bottom line

- **Progress: substantial and real.** 123 portfolios, 63,783 resolved outcomes, 533 symbols, a fully
  instrumented TP/SL engine, and — for the first time — a measured benchmark showing the engine beat
  equities in a falling market.
- **Edge: not proven.** Versus cash the median loses. One portfolio (+7.58%) is a data point, not a track
  record. September's +3,641 collapsed to November's −3,160.
- **Cost is the binding constraint.** TP/SL expectancy +0.123% gross against a 26 bp round turn. No signal
  in this book is currently large enough to pay for its own trading.
- **The most valuable next test is rank persistence across the 123 portfolios**, because it converts six
  months of real NAV history into a falsifiable skill question — and requires no new data.
