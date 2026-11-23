# 12-1 momentum GROSS of costs — second positive control

**Date:** 2026-11-23 · **Round:** ROUND_01_2026-11-23 · **Tool:** `CONTEST/tools/momentum_gross.py` · every number below is printed by that script.

## Question

Can the audit's gate recover a KNOWN anomaly — 12-1 momentum — GROSS of costs? If the harness cannot recover momentum gross, it cannot be trusted on anything else it tests. This is the second positive control, after `POSITIVE_CONTROL.md` (injected alpha recovery).

## Method

Classic Jegadeesh/Titman 12-1 momentum, gross of all costs (no transaction costs, no borrow, no slippage):

1. **Universe:** 24 liquid US names (AAPL, MSFT, AMZN, GOOG, META, TSLA, NVDA, JPM, V, UNH, HD, PG, DIS, NFLX, ADBE, KO, PEP, COST, WMT, CSCO, TXN, AVGO, QCOM) plus SPY as context.
2. **Data:** Yahoo Finance monthly adjusted close (dividends/splits adjusted), same fetcher pattern as `positive_control.py`. **24/24 symbols fetched, 120 common months (~10 years), 106 formation months.**
3. **Formation:** at each month-end, momentum = 12-month return ending one month ago (`P[t-1]/P[t-13] - 1`), skipping the most recent month to avoid short-term reversal/microstructure.
4. **Sort:** rank symbols into quintiles; long top quintile, short bottom quintile, equal weight.
5. **Hold:** one month, then re-rank. Return = next-month simple return. Long-short = mean(long leg) − mean(short leg).
6. **Gate:** identical to `POWER_ANALYSIS.md` — `SE = vol/√T`, `t = mean/SE`, significant iff `|t| ≥ 2`.

## Results

| metric | value |
|---|---:|
| Symbols | 24 |
| Common months | 120 (~10 years) |
| Formation months | 106 |
| Long-short gross | **−0.62%/yr** |
| Long-short annualised vol | 30.21%/yr |
| t-stat | **−0.06** |
| Hit rate (months long-short > 0) | 48% |
| Long leg (top quintile) | +0.30%/yr |
| Short leg (bottom quintile) | +0.31%/yr |
| SPY CAGR over window | +13.64%/yr |

**Significant? No.** |t| = 0.06 ≪ 2. The long and short legs are both ≈ +0.3%/yr — no momentum premium in either leg over this window.

## Reading

**Verdict: POWER STATEMENT — momentum gross was NOT recovered as significant.**

The harness ran cleanly (real data, all symbols fetched, no fabrication) but returned a flat long-short: −0.62%/yr gross, t = −0.06. That is **not** evidence that momentum is dead; it is evidence that **this ~10-year sample did not resolve it**. Momentum's premium is time-varying and this window was a strong, trendless-to-up bull market (SPY +13.64%/yr) in which the short leg rose along with the long leg — exactly the regime where momentum goes dormant.

So the gate is **not manufacturing a false positive** (it returned null when the data is null), but on this sample it **lacks the power to confirm momentum gross**. By the same logic as `POSITIVE_CONTROL.md`: a "strategy failed" verdict from a sample that cannot resolve the effect is a statement about the sample's power, not about the market.

## What this proves (one paragraph)

The harness executes faithfully on real data and reports a null honestly when the data is null — but it could **not** recover 12-1 momentum gross as significant over this window. Until a sample on which momentum gross IS significant is demonstrated, the gate's ability to confirm a known anomaly is unproven, and any "no effect found" verdict from this harness must state the minimum detectable effect its sample can actually resolve.

*Paper only. No live orders, no credentials. Not investment advice.*
