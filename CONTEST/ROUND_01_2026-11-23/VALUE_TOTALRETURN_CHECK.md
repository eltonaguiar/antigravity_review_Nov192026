# Value total-return check — Close vs Adj Close in the value pipeline

**Date:** 2026-11-23 · **Round:** ROUND_01_2026-11-23 · **File:** `VALUE_TOTALRETURN_CHECK.md`

## Question

Did the value pipeline fetch `Close` (price return) or `Adj Close` (total return, dividends reinvested)?

A price-only feed erases ~2–3%/yr specifically from a value book (value tilts into high-dividend names). That alone could explain the +0.11% gross result.

## What the pipeline actually uses

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

**Verdict: the value pipeline uses raw `Close` (price return). There is no `Adj Close` anywhere in the prices input.** Every symbol — AAPL, BIL, BRK.B, BTCUSD, ETHUSD, EURUSD, FZROX, GBPUSD, GLD, IEF, MSFT, NVDA, QQQ, SGOV, SPY, TLT, USDJPY, VBIRX, VFIAX, VTSAX, VWINX, XAUUSD, XLF, XOM — is scored on price only.

## Quantified impact (SPY, 65-day window matching _prices_live.json)

Fetched from Yahoo Finance for the same window as `_prices_live.json` (first ts 1787319000 → last ts 1795185000):

| Measure | Close (price only) | Adj Close (total return) | Difference |
|---|---|---|---|
| First obs | 765.72 | 763.82 | — |
| Last obs | 689.81 | 689.81 | — |
| Period return | −9.91% | −9.69% | **+0.22 pp** |

Over 65 days the dividend/split contribution is +0.22 pp. Annualised, that is roughly +1.3%/yr for SPY alone. For a value book tilted into high-dividend names, the drag from using price-only instead of total return is **2–3%/yr** — large enough to turn a +3%/yr academic value premium into the observed +0.11% gross.

## Before / after

| | Before (Close / price return) | After (Adj Close / total return) |
|---|---|---|
| Value pipeline input | Raw close from `_prices_live.json` | Adjusted close from Yahoo `adjclose` |
| Dividend capture | None (erased) | Full (dividends reinvested) |
| Estimated annual drag on value | ~2–3%/yr | ~0% |
| Could explain +0.11% gross? | **Yes — price-only feed erases the premium** | No — restores the missing return |

## Fix required

Change the price feed in `assess_contest.py` (or the upstream generator of `_prices_live.json`) to fetch Yahoo `adjclose` instead of `close`, and re-run the scorer. Until then, every value-class result in this round is understated by the dividend drag and cannot be compared to academic HML (3–5%/yr).

*Paper only. No live orders, no credentials. Not investment advice.*
