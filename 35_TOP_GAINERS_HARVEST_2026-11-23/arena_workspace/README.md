# Reverse-Engineering Daily/Weekly Top Gainers
### A research playbook: asset-class → symbol → symbol×direction predictability, with TP/SL signals, backtesting, forward-testing and the metrics that actually decide go/no-go

*Prepared 2026-11-22. Companion code + a runnable demo study live in this workspace (see §12).*

---

## 0. The one framing that matters

"Reverse engineer the top gainers list" is **not** a data problem, it's a **search problem with a tax**. You will generate hundreds of candidate rules (which class, which symbol, which side, which lookback, which TP/SL, which horizon). The moment you do that, the best rule you find is *guaranteed* to look good — that's arithmetic, not skill. So the entire methodology below is built around two questions:

1. **Is the thing I found bigger than what my search process manufactures from pure noise?** (§6)
2. **Does it survive contact with costs, fills and out-of-sample time?** (§4, §7)

The most common failure mode in this niche isn't a bad model. It's an unadjusted p-value on a lucky slice of a 500-cell grid.

---

## 1. Step 0 — Define the event, the trade and the label *before* touching data

Ninety percent of "top gainer" research is unfalsifiable because the event, the entry and the exit are all defined after seeing the result. Fix them in writing first (a one-page pre-registration — see §7.1).

| Decision | What to pin down | Why it bites |
|---|---|---|
| **Event** | e.g. *close-to-close daily return in the top 1% of its class that day* **and** `close > $1` **and** `RVOL > 5× 20d median` | "Top 10 gainers" from a website is a *narrative*; it is usually 5–10 illiquid microcaps where the gain happened on $200k of volume. RVOL + price floors remove most of the untradeable noise. |
| **Universe / point-in-time** | Every symbol that existed on that date, including ones later delisted; index membership as of that date | Survivorship bias alone can generate a fake 2%/month in small-cap momentum studies. |
| **Entry** | Next bar's open (or next bar's close). Never the signal bar's close | The gainer list is published *after* the move. If your fill is at the signal close, you bought the thing you already know went up. |
| **Exit / label** | TP and SL **in ATR or vol units**, plus a vertical time barrier | Fixed % TP/SL silently changes your holding period and risk-per-trade across volatility regimes. |
| **Costs** | per-side bps + spread + slippage + borrow/funding | Costs, not signal, kill most of these strategies (§3.3). |
| **Sizing** | Fixed fractional risk per trade (R = 0.5–1% of equity) | So every result is expressible in **R-multiples**, which are comparable across symbols and volatility. |

**Label the trade, not the return.** Use the *triple-barrier* label (López de Prado, AFML ch. 3): for each event, look forward and record **which barrier is touched first** — profit target, stop, or time. The output per trade is an R-multiple ("+0.16R"), which is exactly what a TP/SL signal promises and exactly what you can aggregate.

---

## 2. Step 1 — Data plumbing and the traps that fake results

| Class | Sources that are usable for this | Traps |
|---|---|---|
| **Equities** | Polygon/Databento/Alpaca (bars), Sharadar or CRSP (point-in-time fundamentals + delistings), Norgate (survivorship-bias-free daily) | Delisted tickers missing; splits/dividends; **pre-market gaps** (the gainer usually gapped before the open — your daily bar hides the fill you'd actually get); halts/LULD; low-float names where a market order moves 5%; borrow cost & hard-to-borrow for shorts; short-sale restriction (SSR) days |
| **Crypto** | Exchange klines (Binance/Bybit/Coinbase), CoinGecko for listings | 24/7 calendar (365 days — don't annualize with 252); exchange listing dates (new listings are the actual "gainers" and have no history); wick-only moves on thin books; perp funding costs; exchange outages on the exact days that matter |
| **FX** | Dukascopy / broker tick data, central-bank reference rates | No consolidated volume (so RVOL features don't exist); 5-day-per-week calendar with Sunday reopens; rollover/swap costs; broker-specific spreads blow out at 17:00 NY and around NFP/CPI — a 1-pip backtest becomes 5 pips live |
| **Mutual funds** | Fund NAV history, dividends | **You cannot trade a NAV.** Orders execute at *that day's* close NAV, unknown at decision time. Stale/smoothed NAVs create fake autocorrelation and fake low vol (my demo reproduces this: an NAV-smoothed series has spurious IC unless you unsmooth it). Redemptions settle T+1/T+2; round-trip cost is often 100–500 bps. Treatment: usable only for weekly/monthly *allocation* work, never for a daily TP/SL signal. |
| **ETFs** | As equities, plus creation/redemption | Leveraged/inverse ETFs decay; the "top gainer" is often a 3× product whose move is mechanical. |

Two rules that save months: **(a)** build a `is_tradable(date)` mask per symbol (price floor, ADV floor, halt flag, listing age) and apply it *before* ranking; **(b)** store everything in a single long panel `[date, symbol, class, open, high, low, close, volume]` so every study slices the same way.

---

## 3. Step 2 — Decompose "predictability" into three nested questions

You asked exactly the right question: *class → symbol → symbol×direction*. Here is the design that answers all three with one pass.

### 3.1 The measurement
For each event (top-gainer day), compute the forward return and **subtract that day's class (or universe) mean forward return**:

```
excess_fwd(i,t) = fwd_ret(i,t) − mean_j∈class fwd_ret(j,t)
```

This is non-negotiable. Without it you're measuring "stocks went up in 2019", not skill. Demeaning removes class drift and market beta in one shot; it also makes a *short* signal's edge visible (a top-gainer that merely matches its class earns exactly 0 excess).

Then estimate the conditional mean of `excess_fwd` for the LONG leg and the SHORT leg, per class, per symbol, per symbol×direction, with a **block bootstrap CI** (blocks of 5–10 days, because the observations overlap and are serially dependent), and a t-stat using the *non-overlapping* sample count.

### 3.2 The slice hierarchy to test — and count
| Level | Slice | # slices (example: 8 symbols, 4 classes) | Question answered |
|---|---|---|---|
| 1 | asset class × long/short | 4 × 2 = 8 | *Which asset class is more predictable?* |
| 2 | symbol × long/short | 8 × 2 = 16 | *Is a particular symbol more predictable?* |
| 3 | symbol × direction × regime (vol tercile / trend) | 16 × 3 = 48 | *Does the edge only exist in some states?* |
| 4 | symbol × direction × TP/SL grid | +24–48 | *Is the R-multiple optimizable?* |

That's 100+ tests. **Log every one of them** (including the failures) — that log *is* your multiple-testing denominator in §6. If you don't count your trials, you cannot deflate your Sharpe.

### 3.3 What the demo study found (synthetic data — method demonstration, not market claims)

I built a 2,200-day, 9-symbol, 4-class universe with vol clustering, fat tails, jumps and *deliberately planted* edges in exactly two places (a momentum symbol, a reversal symbol) — so the harness can be verified to *find* edges when they exist, and to reject noise when they don't.

**Top-gainer → next-5-day class-excess return (36 slices):**

| Slice | n | mean excess | 95% block-bootstrap CI | raw p | BH-FDR p |
|---|---|---|---|---|---|
| crypto: LONG top-gainer | 2194 | **+91 bps** | −37 … +232 | 0.020 | 0.091 ✗ |
| equity: LONG top-gainer | 2194 | −7 bps | −52 … +43 | 0.70 | 1.00 ✗ |
| fx: LONG top-gainer | 2194 | **−12 bps** | −21 … −3 | **3e-5** | **0.0002 ✓** |
| fx: SHORT top-gainer | 2194 | **+12 bps** | +3 … +21 | **3e-5** | **0.0002 ✓** |

`raw p<0.05: 8 of 36 → survive BH-FDR at 5%: 4`. **Note the crypto row**: the biggest point estimate in the table, and the *least* reliable — CI straddles zero, because crypto vol is huge. Rank your results by **signal-to-noise (t-stat), never by point estimate.** This single habit removes most self-deception.

**Per-symbol rank IC** (trailing 5-day z-score → forward 5-day excess return, non-overlapping samples): BTCUSD **+0.166** (t 3.47, BH p 0.005), EURUSD **−0.130** (t −2.69, BH p 0.033), everything else indistinguishable from zero (|IC| < 0.09, BH p > 0.2).

**Symbol × direction, best TP/SL from a 3×3 grid, net of per-class costs, Deflated-Sharpe haircut for 24 trials:**

| Symbol | Side | Horizon | TP/SL (ATR) | n | Hit | Expectancy | PF | MaxDD (R) | DSR | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSD | long | 5d | 2 / 2 | 1267 | 61% | **+0.165R** | 1.84 | −22 | 1.00 | pass |
| EURUSD | short | 5d | 2 / 2 | 1107 | 56% | **+0.067R** | 1.36 | −17 | 1.00 | pass |
| AAA | long | 10d | 3 / 3 | 1189 | 52% | +0.052R | 1.25 | −33 | 1.00 | pass |
| CCC | long | 20d | 4 / 4 | 1188 | 51% | +0.038R | 1.17 | −49 | 0.50 | fail |
| SOLUSD | long | 10d | 3 / 3 | 1168 | 52% | +0.024R | 1.11 | −31 | 0.00 | fail |
| ETHUSD | long | 5d | 2 / 2 | 1196 | 54% | +0.020R | 1.08 | −39 | 0.00 | fail |
| …9 more | | | | | | ≤ +0.01R | ≈1 | | 0.00 | fail |
| AAA | short | 20d | 4/4 | 1189 | 47% | −0.060R | 0.78 | −93 | 0.00 | fail |
| BTCUSD | short | 20d | 4/4 | 1267 | 46% | −0.076R | 0.78 | −115 | 0.00 | fail |

Four lessons, all of them general:

1. **The class ranking is "crypto > fx > equity" but only because of *one* symbol each.** Rank by *breadth* too: crypto scored 3 symbols → 1 usable; fx 2 → 1; equity 3 → 1. A class with one great symbol is a *symbol* finding, not a class finding (which is why you need 20–100 names per class before claiming class-level predictability).
2. **Symbol×direction is the real unit.** BTCUSD-long makes +0.165R/trade; BTCUSD-short makes −0.076R. Same symbol, same features, opposite sign. Any model without an explicit side is averaging a coin flip. My prior for real markets: in equities, the *short* side of the extreme-gainer slice is the more robust (the MAX / lottery-demand anomaly), while in large-cap crypto the *long* side of time-series momentum has been the more robust.
3. **Mutual funds drop out on tradability, not on statistics.** NAV-only + ~500 bps costs → the whole asset class is untestable at daily frequency. This is a *finding*, and reporting it as such is better than reporting a number.
4. **Costs truncate the whole thing.** Same EURUSD reversal signal: **+0.0885R** at 0 bps/side → +0.067R at 2 bps → **+0.005R at 8 bps → −0.037R at 12 bps.** A real, statistically strong edge (t = 5.1) is *dead* by 10 bps. This is why "predictability" and "tradability" are different words.

### 3.4 "Is it more predictable?" — the honest summary statistic
Report, per level, a single number that is comparable across levels and classes:

```
Predictability Score = IC_nonoverlap × sqrt(n_nonoverlap)     # = t-stat
```
…plus **breadth** (% of symbols in the class with the same sign and |t| > 2) and **capacity** (how much $ you can push at 10 bps impact). A class is "more predictable" if it wins on *all three*, not on its best symbol.

---

## 4. Step 3 — Designing the TP/SL so the signal is falsifiable

A TP/SL is not an afterthought; it *is* the hypothesis. Specify it in **volatility units** and make the mechanics honest:

* **Barriers:** `TP = entry + k_tp · ATR14`, `SL = entry − k_sl · ATR14`, **vertical barrier** = `h` bars. Grid `k_tp,k_sl ∈ {1,2,3,4}`, `h ∈ {1,3,5,10,20}` — and **count every cell** as a trial in §6.
* **Risk-normalized outcome:** `R = side·(exit − entry)/(k_sl·ATR) − costs`, so 1R is always the same dollar risk.
* **Intrabar ambiguity:** if a bar's range covers both TP and SL, **assume the stop** was hit first. Conservative assumption; the alternative inflates results by 10–30% on daily bars. If you must resolve it, use 1-minute data, not hope.
* **Time stop is mandatory.** Gap-and-fade gainer names often drift for weeks; without a vertical barrier you can't tell a signal from a bag-holding.
* **Slippage that scales with the event:** the day after a +40% move the spread is 3–10× normal. Model `cost = base_bps + k·(daily_range% )` or you'll backtest a market that doesn't exist.
* **Hit rate is not a result.** With TP/SL = 1:1 you need >50% *plus* costs; with 2:1 you break even at 33%. Always report **expectancy in R, profit factor, and the payoff ratio** — never hit rate alone.
* **Optional but powerful: meta-labeling.** Let a primary rule (e.g. "top gainer + RVOL>5") set the *side*, then train a second model to predict *whether that primary signal will work* (binary). Use it to size and to filter — it decouples "which way" from "how much", which is far easier to learn.

---

## 5. Step 4 — The backtest engine (the non-negotiables)

1. **Event-driven, bar-by-bar**, with state: one position per symbol, no pyramiding, no simultaneous contradictory signals.
2. **Next-bar entry**, on the *tradable* bar. Signal computed on bar `t` close → fill at bar `t+1` open (or VWAP with slippage).
3. **Point-in-time universe.** Delisted names included; listing-age filter; price/ADV floor applied at decision time, not at study-end.
4. **Costs:** commission + spread/2 + slippage + financing (crypto funding/futures roll, equity borrow, FX swap). Charge them **per side**, and re-run the whole study at 1×, 2×, 3× your estimate. If the strategy dies at 2×, you don't have a strategy.
5. **Capacity:** position size ≤ x% of the symbol's ADV; report the AUM at which expectancy → 0.
6. **No parameter peeking:** the TP/SL grid is chosen on train, evaluated on test. Never report in-sample best as the result.
7. **Synthetic control run** (the trick that keeps you honest): run the identical pipeline on **shuffled / bootstrapped / simulated** price paths with the same vol, autocorrelation and cross-correlation as the real data. Whatever expectancy the pipeline "finds" on pure noise is your **noise floor**. The real result must beat it. (My demo is built this way: two planted edges, seven null symbols — and only the planted ones pass.)

---

## 6. Step 5 — What is actually "proven"? The evidence hierarchy

Be ruthless about the difference between *published*, *replicated*, and *tradable*.

| Tier | Meaning | Examples relevant to "top gainers" |
|---|---|---|
| **A. Robust, replicated, economically motivated** | Survives many samples, markets, decades; has a risk- or behaviour-based story | **(i) Volatility is far more predictable than direction** — vol clustering is universal (this is the one thing you can rely on: it's what makes ATR-based TP/SL sane). **(ii) Short-horizon reversal** in equities (1–5 days, gross of costs, strongest in illiquid names) and in FX majors (overreaction to flows). **(iii) Time-series momentum** at 1–12 month horizons across futures/FX/crypto. **(iv) Cross-sectional momentum** in crypto (market, size, momentum are the standard crypto factors — Liu, Tsyvinski & Wu). **(v) The MAX / lottery-demand effect**: stocks with the most extreme recent daily returns underperform over the following month — i.e. the *short* side of a gainer list — documented in the US and replicated in many markets; note the mechanism itself is contested (recent work argues plain MAX is contaminated by beta/issuance and only the cleaned-up retail-heavy version is a lottery effect). |
| **B. Published but fragile** | Real in-sample, decays or disappears after publication, or is cost-sensitive | Short-term reversal *net of costs* in liquid names; intraday seasonality; most "gap-and-go" rules; most single-symbol technical rules. |
| **C. Not proven / folklore** | No credible OOS evidence | "Buy the day's #1 gainer because momentum"; most newsletter/screener signals; anything whose backtest you cannot reproduce bar-by-bar with costs. |

**My honest answer to "is the top-gainers list predictive?"** At daily frequency in liquid equities: mostly **no** — the list is largely a *selection* of names that gapped on news/attention, and the tradeable version of that is a liquidity/impact problem, not an alpha. Where a real effect exists it is (a) **short-side and slow** (the lottery/overpricing effect, measured over weeks, not hours), (b) **microcap-and-catalyst-specific** (offerings, reverse splits, promotion campaigns — where shorting is expensive or impossible), or (c) **crypto cross-sectional momentum**, which is genuinely strong in-sample and has survived out-of-sample so far but with brutal drawdowns. Anything that only exists in the *first hour* after the move is an execution/HFT problem, not a signal problem.

**Corollary that will save you the most money:** spend your modelling effort on **volatility and cost forecasting** (predictable, stable) and use the TP/SL + sizing machinery to convert a weak directional edge (IC of 0.02–0.05, which is realistic) into positive expectancy. That's how the demo's +0.165R happens with a 61% hit rate on a 2:2 barrier — the edge is small; the R-normalization is what makes it bankable.

---

## 7. Step 6 — How to prove it: the statistics of "I found something"

This is where 95% of retail research fails. Run these in order.

### 7.1 Pre-registration (free, and the single highest-alpha activity)
Write down, before running: hypothesis, universe, event definition, entry/exit, cost model, number of variants you will try, success threshold, and kill criteria. Date-stamp it in the repo. It converts "I found a pattern" into a testable claim, and it makes your trial count honest.

### 7.2 Multiple-testing corrections
| Tool | What it answers | Threshold |
|---|---|---|
| **Benjamini–Hochberg FDR** | Of my "significant" slices, what fraction are false? | q = 0.05–0.10 |
| **Deflated Sharpe Ratio (DSR)** | Given N trials and non-normal returns, P(true SR > 0)? | **DSR > 0.95** |
| **Harvey–Liu haircut** | How much of my Sharpe is search? | report the haircut % |
| **White's Reality Check / SPA** | Is the *best* strategy better than the best of N nulls (bootstrap)? | p < 0.05 |
| **PBO (CSCV)** | Probability the in-sample winner is OOS-losing | < 0.3 |

Calibration numbers worth internalizing (from Harvey–Liu and the DSR literature): with **N=200 trials**, a Sharpe of 0.75 haircuts to **~0.32 (−60%)**; **7 trials are enough** to manufacture a spurious 2-year backtest with in-sample Sharpe > 1.0 and zero true OOS Sharpe; a backtest needs ~**5 years** of data before 50 trials stop manufacturing a Sharpe of 1.0 by luck (MinBTL). In my demo, 36 slices produced 8 raw p<0.05 — *the null rate for 36 tests is ~2*, so 6 of those 8 were noise until BH removed them.

**Effective number of trials ≠ number of cells.** Correlated parameter grids over-deflate. Estimate the effective trial count from the correlation of your strategy return streams (or run the DSR across a band of trial counts and report the worst case).

### 7.3 Resampling for the estimates themselves
* **Block bootstrap** (5–20 day blocks) for CIs on expectancy and hit rate — never use i.i.d. bootstrap on overlapping trades.
* **Non-overlapping sampling** for IC t-stats (use every h-th observation when h = the forward horizon). This can cut your "n" by 5–20×; that's the point.
* **Stationary bootstrap / Monte Carlo trade reshuffling** for drawdown distribution: you care about the *worst* 5% path, not the average one.

### 7.4 Purging and embargoing (if you fit *any* model)
Chronological walk-forward with a **purge** (drop training samples whose label window overlaps the test window) and an **embargo** (drop the bars immediately after each test fold). Standard k-fold with overlapping triple-barrier labels leaks information and will show you a beautiful, fake 2.0 Sharpe. Also apply **uniqueness weights** when labels overlap.

---

## 8. Step 7 — Forward-testing: how you actually earn the right to trade it

Backtest = *plausibility*. Forward test = *evidence*. Sequence:

1. **Freeze the model.** Version-tag params + code hash. Any change resets the clock.
2. **Shadow/paper trading, signal-level.** Log the signal, the intended fill (bid/ask at signal time), the realized fill, and the outcome — every day, into an append-only file. Paper trading's *only* purpose is execution analysis; its P&L is meaningless if you can't fill it.
3. **Minimum sample size.** Solve for it before you start:
   * Hit-rate precision: to distinguish 55% from 50% at 95% confidence you need **n ≈ 1000 trades** (SE ≈ 1.6%). At 20 trades/day across a universe, that's ~10 weeks; at 2 trades/day, two years.
   * Expectancy precision: `n ≥ (t_crit · σ_R / ΔR)²`; with σ_R ≈ 1.2R and a target detectable edge of 0.10R → **n ≈ 550 trades**.
   * Or use **MinTRL** (minimum track record length) on daily returns: how many days until SR is distinguishable from a benchmark, given skew/kurtosis. Report it; it's usually longer than the patience of whoever asked for the strategy.
4. **Sequential testing, not peek-and-decide.** If you must check early, use an alpha-spending (O'Brien–Fleming) plan so interim looks don't inflate false positives.
5. **Champion/challenger** with a pre-set promotion rule (e.g. challenger must beat champion on 3-month rolling expectancy with a block-bootstrap CI excluding zero, *and* not be worse on max DD).
6. **Decay monitoring:** rolling 60-trade IC and expectancy, plus a CUSUM on R-multiples for structural breaks. Pre-register kill rules: *"stop if rolling-100 expectancy < 0 for 2 consecutive months"*, *"stop if realized slippage > 2× model"*.
7. **Track the gap:** model expectancy vs realized, decomposed into signal decay vs execution slippage vs regime. If it's slippage, it's fixable; if it's decay, it's over.
8. **Statistical honesty about forward tests:** 3 months of live trading on a 0.15R/trade edge is **noise**. Never "confirm" a strategy with a forward test shorter than the MinTRL computed in step 3. Forward testing's real job is to catch *execution* lies and *operational* failures — data outages, API limits, funding costs, borrow recall, corporate actions — not to re-prove the edge.

---

## 9. The metrics dashboard (what to measure, and the bar for each)

**A. Signal quality** (is there information, before costs?)
| Metric | Bar |
|---|---|
| Rank IC per slice (non-overlapping) | \|IC\| > 0.03, t > 2 |
| IC stability (rolling 60d, % of periods same sign) | > 60% |
| Hit rate vs 50% with CI | CI excludes 0.5 |
| Decile monotonicity (does edge scale with signal strength?) | monotone, not just top decile |
| R² of best model vs noise floor (synthetic control) | must exceed floor |

**B. Trade quality** (is it bankable?)
| Metric | Bar |
|---|---|
| Expectancy (R/trade, net) | > 0.05R after all costs |
| Profit factor | > 1.2 net |
| Payoff ratio (avg win / avg loss) | consistent with barrier geometry |
| Trade count & trades/year | enough for §8.3 sample size |
| Cost sensitivity | survives 2× assumed costs |

**C. Risk** (can you hold it?)
| Metric | Bar |
|---|---|
| Max drawdown (R and %) | < 15–20% for a 1%-risk book |
| Sharpe (annualized, net) | > 1.0 *after* haircut |
| Sortino, Calmar | report both |
| Skew / kurtosis | know them: TP/SL systems are usually negatively skewed — Sharpe overstates them |
| Worst 20-trade streak (Monte Carlo) | must be survivable at your risk-per-trade |
| Exposure/concentration | max % equity in one name/sector; correlation to BTC or SPX |

**D. Robustness** (would I bet on it?)
| Metric | Bar |
|---|---|
| PSR (prob. true SR > 0) | > 0.95 |
| **Deflated Sharpe** (N trials) | **> 0.95** |
| BH-FDR q-value across all slices | < 0.05–0.10 |
| Harvey–Liu haircut | report; treat > 50% as a fail for low-Sharpe systems |
| PBO (CSCV) | < 0.3 |
| Parameter-plateau check | neighbours of the chosen TP/SL must also work (a lone spike = noise) |
| Sub-period stability (year-by-year, regime-by-regime) | positive in the majority; no single year > 50% of total P&L |
| Cross-symbol breadth | the *same* rule works on ≥ 3–5 uncorrelated symbols |

**E. Execution & economics**
| Metric | Bar |
|---|---|
| Realized slippage vs model | < 1.5×, monitored daily |
| Fill rate / miss rate on signals | miss rate < 20% |
| Capacity (AUM where expectancy → 0) | ≥ 5–10× your intended size |
| Funding/borrow drag | < 20% of gross edge |

---

## 10. Go / no-go gates (the checklist I'd actually use)

- [ ] Pre-registered hypothesis with a trial count.
- [ ] Point-in-time universe, delistings included, next-bar fills.
- [ ] Synthetic-control noise floor beaten.
- [ ] Slices count ≥ 100 logged; BH-FDR + DSR applied; DSR > 0.95 survives.
- [ ] Expectancy > 0.05R net at **2×** modelled costs.
- [ ] Same-sign results on ≥ 3 uncorrelated symbols (breadth) — else it's one lucky symbol.
- [ ] Parameter neighbourhood works (plateau, not spike).
- [ ] Purged walk-forward OOS results consistent with in-sample.
- [ ] Capacity ≥ 5× intended AUM.
- [ ] Written kill rules + monitoring dashboard live before the first dollar.

Fail any of the starred ones and you have a research artifact, not a strategy.

---

## 11. What I'd actually do first (30/60/90)

**Days 1–10 — infrastructure, not models.** Panel data with point-in-time tradability masks for 3 classes (equities: 500–1000 names; crypto: top 50; FX: 8 majors). Cost model per class. Barrier backtester with next-bar fills, intrabar-stop assumption, block bootstrap + DSR + BH built into the report from day one.

**Days 11–30 — the descriptive study.** Run the §3 decomposition on *every* combination of {class} × {symbol} × {side} × {horizon} × {TP/SL}. Log all of it. Expect (a) vol predictability to be the only universal finding, (b) reversal at 1–5 days in equities/FX, (c) crypto momentum to be the widest-spread signal, (d) mutual funds to be untestable.

**Days 31–60 — one strategy, one rule.** Take the single best *breadth* result. Add meta-labeling for sizing/filtering. Purged walk-forward. Cost stress to 3×. Capacity. Then paper-trade it with full execution logging.

**Days 61–90 — decide.** Compare live-vs-model, run the MinTRL math, and either scale in slowly at 1% risk/trade or kill it. Start the second strategy only after the first is instrumented — the portfolio effect (low correlation between a crypto-momentum long and a small-cap lottery short) is a bigger lever than a better single model.

**On asset-class ranking, my prior before data:** *daily-horizon predictability* ranks roughly **crypto ≈ single-name equity events > FX majors >> mutual funds**, but *tradability* ranks **FX majors ≈ mega-cap/liquid equity > crypto >> mutual funds > microcap gainers**, because impact and borrow costs eat the places where the signal is strongest. That inversion — signal where liquidity isn't, liquidity where signal isn't — is the actual problem to solve, and it's why cost modelling deserves as much effort as signal research.

---

## 12. Files in this workspace

| File | What it is |
|---|---|
| `gainers_research/src/engine.py` | The harness: synthetic regime-switching universe with *planted* edges, ATR/triple-barrier TP/SL backtester (next-bar fills, per-side costs, conservative intrabar-stop assumption), metrics (expectancy, PF, Sharpe/Sortino/Calmar, max DD, **PSR, Deflated Sharpe, block-bootstrap CI, MinTRL**), the top-gainer slice study with **Benjamini–Hochberg FDR**, and purged walk-forward with embargo |
| `gainers_research/run_study.py` | Runs the whole study end-to-end (~30s): class → symbol → symbol×direction predictability, cost sensitivity, charts |
| `gainers_research/out/1_top_gainer_slices.csv` | 36 slices, excess returns, bootstrap CIs, raw + BH-adjusted p-values |
| `gainers_research/out/2_predictability_ic.csv` | Rank IC per symbol, overlapping vs non-overlapping t-stats |
| `gainers_research/out/3_predictability_tpsl.csv` | Symbol×direction TP/SL grid results with DSR |
| `gainers_research/out/4_class_ranking.csv` | Class-level summary (breadth + best + DSR pass count) |
| `gainers_research/out/study_charts.png` | 4-panel figure: per-class excess returns, IC per symbol, expectancy by symbol×side, p-value distribution vs the null |

**Important caveat:** the data is *synthetic by design* — the numbers above demonstrate the *method* (and prove the harness can detect a planted edge and reject noise), not the real market's predictability. Swap `make_synthetic_universe()` for your vendor panel in `build_panel()` and every table regenerates on real data unchanged.

---

## 13. References / further reading

- Bali, Cakici & Whitelaw (2011), *Maxing Out: Stocks as Lotteries and the Cross-Section of Expected Returns*, JFE 99(2) — the MAX effect (short side of gainer lists). Mechanism contested by Bali, Ince & Ozsoylev (2026), *MAX on Steroids*.
- Liu, Tsyvinski & Wu (2022), *Common Risk Factors in Cryptocurrency*, J. Finance — market, size, momentum; Liu & Tsyvinski (2021), *Risks and Returns of Cryptocurrency*, RFS — time-series momentum + investor attention.
- López de Prado (2018), *Advances in Financial Machine Learning* — triple-barrier labeling, meta-labeling, uniqueness weights, purged k-fold + embargo, PBO.
- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*; Bailey, Borwein, López de Prado & Zhu, *Pseudo-Mathematics and Financial Charlatanism* (MinBTL / minimum backtest length).
- Harvey & Liu (2015), *Backtesting*, JPM — haircut Sharpe ratios; Harvey, Liu & Zhu (2016), *…and the Cross-Section of Expected Returns*, RFS — t > 3 hurdle.
- White (2000), *A Reality Check for Data Snooping*; Hansen (2005), SPA test.
