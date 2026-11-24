# PROVEIT — KILOCODE trading-philosophy proof (fee-aware, scenario portfolios)

**Agent:** KILO CODE · **Sim run:** 2026-11-24T0322Z UTC · **Data:** `data/market_prices.csv` (adjusted + close, ~1254 daily bars, 2021-11→2026-11)
**Sim engine:** `simulate_proveit.py` → `SIM_*.json` (re-runnable; each run drops a new date-time-stamped dump).
**Paper only. Zero capital. Not investment advice.**

## The philosophy (rules)
- **Core:** buy a broad, low-cost index fund and **hold** (no TP/SL on the core; TP/SL adds turnover cost and foregoes upside — tested earlier, it destroys edge).
- **60/40 variant:** 60% equity / 40% bonds, **monthly rebalance** (set a calendar alert; rebalancing is the only "management").
- **Timing variant (risk control, optional):** long equity while price > 200-day MA, else cash; monthly check with an alert. **Not a return enhancer** (see proof).
- **Hold horizon:** indefinitely for the core (≥1 year minimum to avoid short-term tax/commissions); rebalance annually (or monthly for 60/40).
- **Fees used:** zero-commission base; **1.5% one-time FX** for USD holdings by a Canadian; **$5/trade** alternative broker; index MF MER (FXAIX 0.015%); crypto traded at **26 bp** round-turn (COST_OF_RECORD).

## Backtest (COMMON window — all philosophies start at bar 200 so the comparison is fair)
| philosophy | net CAGR | max drawdown | excess-of-cash Sharpe |
|---|---:|---:|---:|
| **Buy & hold 100% equity (FXAIX)** | **18.30%** | −18.76% | **0.859** |
| 60/40 (monthly rebalance) | 11.96% | −11.20% | 0.710 |
| 200d-MA timing (cash when below) | 13.76% | **−9.39%** | 0.779 |

**Read it honestly:** buy-and-hold **wins on return and Sharpe**; the 200-day-MA "timing" rule **loses ~4.5%/yr of return** and only wins on **drawdown** — it is **risk control, not alpha** (a previous version of this test wrongly showed timing ahead because it started 200 bars later and skipped the 2021-22 crash; the window is now aligned).

## Scenario portfolios — $300 / $500 / $2,000 / $10,000 (buy & hold equity, terminal value)
| account | zero-comm + CAD | +1.5% FX | +1.5% FX & $5/trade | fee drag on start |
|---|---:|---:|---:|---:|
| $300 | $693 | $688 | **$678** | **2.09%** |
| $500 | $1,155 | $1,147 | $1,137 | 1.52% |
| $2,000 | $4,618 | $4,588 | $4,578 | 0.87% |
| $10,000 | $23,092 | $22,942 | $22,932 | 0.69% |

**Fees hit small accounts hardest:** the same philosophy costs **2.09% of a $300 account** but **0.69% of a $10,000 account**. → small accounts must use **zero-commission, no-FX** vehicles.

## What I endorse by scenario (per asset class)
| account | endorsed | vehicle / rules | why |
|---|---|---|---|
| **$300** | **100% one broad index fund** | FXAIX (S&P500, $0 min) or FZROX (total mkt, 0.00%); or CAD **VFV** fractional | fixed fees dominate; one fund avoids minimums/diversification cost |
| **$500** | 100% one total-market index fund | FZROX / VTI (fractional) / **VEQT** | same; keep it one position |
| **$2,000** | **all-in-one index ETF (XEQT/VEQT)** or a simple **60/40** | buy & hold; annual rebalance alert | enough capital to diversify cheaply |
| **$10,000** | **60/40** or XEQT; optional 5-10% bond sleeve | monthly/quarterly rebalance alerts | drawdown control matters at size |
| **All sizes** | **Cash (SGOV)** as the hurdle (~3.8%), not an edge | — | the risk-free bar |
| **Not endorsed** | active "5 value stocks", timing-as-alpha, crypto/FX strategies | — | **0 demonstrated alpha** (grid: 0/362 cells; census 96/96 measured killed); individual value stocks not measurable from local data |

## The proof (what the math actually shows)
1. **Cheap beta is reliably powerful, active alpha is not.** Buy-and-hold equity compounded **18.3%/yr** over this window with a Sharpe of **0.86**; every active strategy family in the 1000-cell sweep failed (0 survivors), and the median cell has **negative gross** edge.
2. **Risk is real and manageable:** −18.8% drawdown for 100% equity, −11.2% for 60/40, −9.4% for timing — you trade return for a shallower hole.
3. **Fees are the great separator:** a 1.8% fund vs 0.03% ends ~39% lower over 30y; and fixed fees cost a $300 account **3× more** (as % of capital) than a $10,000 account.
4. **Therefore the defensible "proof" is a NEGATIVE one for active trading, POSITIVE for low-cost beta:** the powerful, provable thing is *cheap, diversified, patient* — not clever picking.

## Forward / paper tracking (continues)
Contest entry (`CONTEST/_incoming/KILOCODE_VSCODE/picks.json`) tracks the beta answer forward; the R-bootstrap falsifier will score it when fills exist. Each re-run of `simulate_proveit.py` appends a new `SIM_<timestamp>.json` and I will append further date-stamped `PROVEIT_REPORT_*` updates.

*Paper only. Not investment advice.*
