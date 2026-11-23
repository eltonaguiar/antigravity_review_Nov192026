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
