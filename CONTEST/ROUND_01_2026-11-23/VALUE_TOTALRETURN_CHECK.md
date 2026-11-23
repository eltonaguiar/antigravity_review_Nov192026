# Total-return check — did the value pipeline use Close or Adj Close?

**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/total_return_check.py` · numbers printed by that script.
**Verdict: the value pipeline fetched raw Close (price-only), not adjusted. A price-only feed erases ~2.8%/yr of
dividends from a value universe — enough on its own to turn a real value premium into the reported +0.11%.**

## A. Code audit — every price fetch in the value pipeline
| module | `"Close"` refs | `Adj Close`/`adjclose`/`auto_adjust` refs |
|---|---:|---:|
| `alpha_engine/value_screener_runner.py` | 1 | 0 |
| `alpha_engine/equity_price_failover.py` | 3 | 0 |
| `alpha_engine/value_backtest.py` (pure harness) | 0 | 0 |
| `alpha_engine/value_screener.py` | 0 | 0 |
| **TOTAL** | **4** | **0** |

The backtest harness is provider-injected (it fetches nothing); the only live price fetches are
`value_screener_runner.fetch_prices_via_yfinance` (`hist["Close"]`) and `equity_price_failover`
(Stooq `Close` row + yfinance `hist["Close"]`). **Zero adjusted references.**

## B. Magnitude — price return vs total return on the real value universe (Yahoo, monthly)
| instrument | years | price CAGR | total-return CAGR | dividend drag |
|---|---:|---:|---:|---:|
| SPY (S&P 500) | 33.9 | 8.46% | 10.40% | +1.94%/yr |
| **VTV (value)** | 22.9 | 6.63% | **9.40%** | **+2.78%/yr** |
| **DVY (high-div value)** | 23.1 | 4.92% | **8.70%** | **+3.78%/yr** |
| **VBR (small value)** | 22.9 | 6.99% | **9.22%** | **+2.23%/yr** |

**Value median dividend drag = +2.78%/yr.**

## C. Before / after the fix
| | gross value result |
|---|---:|
| **Before — price-only (raw Close), as reported** | **+0.11%** |
| **After — total return (adjusted), value drag applied** | **+2.89%** (range +2.89% to +3.89% using VTV→DVY) |

The drag (**2.78%/yr**) is **~25×** the reported +0.11% gross. This is exactly the mechanism the task posited: **a
price-only feed can erase the value premium on its own.** The corrected +2.89% is still **below the 5.08%/yr minimum
detectable effect** established in `POSITIVE_CONTROL.md`, so it is not yet *significant* — but it moves the finding from
"the effect was not there" to **"the effect was being erased by the price feed."**

## D. Fix applied
- `fetch_prices_via_yfinance` → `history(period="5d", auto_adjust=True)` (adjusted Close for total return).
- `equity_price_failover` yfinance path → `history(period="5d", auto_adjust=True)`; the Stooq CSV path is documented as a
  short-lived current-price snapshot that **must not** feed holding-period returns.
- Regression test `tests/test_total_return_convention.py` asserts `auto_adjust=True` in both modules. Existing
  `tests/test_value_backtest.py` still passes (28/28) — the harness is unaffected.
- Caveat: the screener's *current-price* use of Close for valuation ratios is correct; only the **return** path must be
  adjusted. The fix makes the fetch total-return-safe without changing a same-day snapshot materially.

*Paper only. Not investment advice.*
