# Value total-return check — Close vs Adj Close in the value pipeline

**Date:** 2026-11-23 · **Round:** ROUND_01_2026-11-23 · **File:** `VALUE_TOTALRETURN_CHECK.md`

## Question

Did the value pipeline fetch `Close` (price return) or `Adj Close` (total return, dividends reinvested)?

A price-only feed erases ~2–3%/yr specifically from a value book (value tilts into high-dividend names). That alone could explain the +0.11% gross result.

## A. Code audit — every price fetch in the value pipeline

The scorer is `CONTEST/tools/assess_contest.py` → `value_pick(p, bars)`. Entry = `series[0]["open"]`, exit = `series[-1]["close"]`. The bars come from a prices JSON supplied by the executor.

The live prices file is `CONTEST/ROUND_01_2026-11-23/_prices_live.json`:

| Metric | Value |
|---|---|
| Symbols | 24 |
| Total bars | 1,613 |
| Bars with `close` field | 1,613 |
| Bars with `adjclose` field | 0 |
| Bars with any adjusted/total-return field | 0 |
| Bar fields present | `close, high, low, open, ts` |

Every symbol — AAPL, BIL, BRK.B, BTCUSD, ETHUSD, EURUSD, FZROX, GBPUSD, GLD, IEF, MSFT, NVDA, QQQ, SGOV, SPY, TLT, USDJPY, VBIRX, VFIAX, VTSAX, VWINX, XAUUSD, XLF, XOM — is scored on price only.

**Verdict: the value pipeline uses raw `Close` (price return). There is no `Adj Close` anywhere in the prices input.** Zero adjusted references across all 24 symbols and 1,613 bars.

## B. Magnitude — price return vs total return on the real value universe (Yahoo, monthly)

| instrument | years | price CAGR | total-return CAGR | dividend drag |
|---|---:|---:|---:|---:|
| SPY (S&P 500) | 33.9 | 8.46% | 10.40% | +1.94%/yr |
| **VTV (value)** | 22.9 | 6.63% | **9.40%** | **+2.78%/yr** |
| **DVY (high-div value)** | 23.1 | 4.92% | **8.70%** | **+3.78%/yr** |
| **VBR (small value)** | 22.9 | 6.99% | **9.22%** | **+2.23%/yr** |

**Value median dividend drag = +2.78%/yr.**

Over a 65-day window matching `_prices_live.json`, SPY close vs adjclose diverges by +0.22 pp (roughly +1.3%/yr annualised for SPY). For a value book tilted into high-dividend names, the drag compounds to **2–3%/yr** — large enough to turn a +3%/yr academic value premium into the observed +0.11% gross.

## C. Before / after the fix

| | gross value result |
|---|---:|
| **Before — price-only (raw Close), as reported** | **+0.11%** |
| **After — total return (adjusted), value drag applied** | **+2.89%** (range +2.89% to +3.89% using VTV→DVY) |

The drag (**2.78%/yr**) is **~25×** the reported +0.11% gross. This is exactly the mechanism the task posited: **a price-only feed can erase the value premium on its own.** The corrected +2.89% is still **below the 5.08%/yr minimum detectable effect** established in `POSITIVE_CONTROL.md`, so it is not yet *significant* — but it moves the finding from "the effect was not there" to **"the effect was being erased by the price feed."**

## D. Fix required

Change the price feed in `assess_contest.py` (or the upstream generator of `_prices_live.json`) to fetch Yahoo `adjclose` instead of `close`, and re-run the scorer. Until then, every value-class result in this round is understated by the dividend drag and cannot be compared to academic HML (3–5%/yr).

*Paper only. No live orders, no credentials. Not investment advice.*

---

## CORRECTION 2026-11-23T21:37Z — does the pipeline actually use raw Close? Partly only
I re-verified the toolchain: **yfinance 1.3.0 `Ticker.history()` defaults to `auto_adjust=None` → True**, so
`history()["Close"]` is **ALREADY adjusted** (VTV first close 27.32 adjusted vs 49.25 raw). The value pipeline's fetch
used `history(period="5d")` with the default → **it was already total-return**, not price-only.

**So this changes the headline:**
- **Still true:** the measured dividend drag on a genuinely raw feed is **+2.78%/yr** (value universe), and there ARE
  **62 repo files** that explicitly use raw prices (`auto_adjust=False` / raw Stooq/chart-API Close) where it bites.
- **Retracted:** the specific **+0.11% → +2.89%** correction — it is valid **only if** the value *backtest* fetched raw
  prices. The pipeline's yfinance path did not. I cannot confirm the backtest's exact source, so the +2.89% is **unconfirmed**.
- The Stooq CSV path in `equity_price_failover` (raw `row["Close"]`) remains the genuine price-only route in that module.

Net: the dividend-drag arithmetic is correct and material, but my application of it to the +0.11% result **assumed a raw
feed the yfinance default does not use.** Corrected before it propagated.

---

## PROVENANCE 2026-11-23T23:45Z — the "+0.11% value strategy" was a MISLABEL (the deepest fix)
Tracing the number to its source:
- `05_KILO_REVIEW/PAGES_AUDIT2_AUDIT3.md:104` → **"EQUITY | PF 1.65 … alpha-neutral (+0.11%, CI spans 0), no positive
  alpha."** So **+0.11% is the EQUITY class *alpha* estimate (CI includes 0)**, not a value-strategy backtest.
- `WHAT_WORKS_PER_ASSET_CLASS.md:38` → the value screener has **"no committed backtest output"**; round-33
  (`33_VALUE_PEAD_AND_COST_GAPS`) says value/HML was **"never measured rather than measured and rejected"** (no book
  equity / shares outstanding in the repo).

**Therefore the entire "value strategy at +0.11% gross → correct to +2.89%" chain was wrong at the root:**
1. +0.11% is an **equity alpha**, not a value result (mislabel in `POWER_ANALYSIS.md` and my analysis).
2. Adding a *value* dividend drag to an *equity-alpha* number compounds the error.
3. And the yfinance-default-adjusted discovery means the drag only applies to raw feeds anyway.

**Corrected statement:** **there is no measured value result to correct.** Value/HML is **UNMEASURED** (needs
fundamentals); the +0.11% is the equity **class alpha, CI spanning zero (alpha-neutral)**. Neither "value failed"
nor "value corrects to +2.89%" is supported. The dividend-drag arithmetic (2.78%/yr for value ETFs) remains valid
**as a property of raw feeds**, but it was applied to the wrong number.
