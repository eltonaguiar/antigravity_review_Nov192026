# TOP RANKED PICKS PER ASSET CLASS + OVERALL — KILOCODE_VSCODE

**As of:** 2026-11-23T03:12Z · **Author:** Kilo (vanilla-handsaw / VS Code) · **Paper only, zero capital, not investment advice.**
**Ledger:** audit3 (2026-11-20T01:57Z), 69 instruments · **Costs:** operator COST_OF_RECORD · **Gate:** G1–G5, DSR at N=658.

## How this was produced (what we tested against)
69 instruments drawn from the live audit3 ledger. Each was tested against:
class-measured round-trip cost (equity 12.07 / ETF 6.71 / FOREX 7.53 / bond-ETF 0.61 / crypto 20–52 bp);
holding-period availability (G2); **deflated Sharpe at N=658** (G3, bar ≈0.49 at n=100, 0.94 at n=30);
net return on **committed capital vs a 4.32% T-bill** (G4, not notional); and pre-registration timing (G5).
Backtests used the 430-row forward ledger and walk-forward cells, with a **two-hurdle** test (paired CI vs the
instrument's own buy-and-hold, on mean **and** median) and explicit survivorship / PIT checks.

**Result: 0 of 69 instruments pass all five gates; 0 of 6 classes is investable.** Numbers below are net bp at a
$25,000 ticket. Every row is labelled with the gate(s) it fails — none is a recommendation.

## Ranking per asset class (top 5)

### STOCKS (17 tested) — class DEAD
| # | Pick | n | net bp | DSR/N | fails |
|---|---|---:|---:|---|---|
| 1 | CVX long | 35 | +168.1 | 0.318/658 | G2,G3,G4,G5 |
| 2 | AMD long | 83 | +108.4 | 0.033/658 | G2,G3,G4,G5 |
| 3 | AMC long | 22 | +74.2 | 0.004/658 | G2,G3,G4,G5 |
| 4 | AAPL long | 81 | +48.3 | 0.106/658 | G2,G3,G4,G5 |
| 5 | BAC long | 25 | +41.3 | 0.020/658 | G2,G3,G4,G5 |

### ETF (9 tested) — class DEAD
| # | Pick | n | net bp | DSR/N | fails |
|---|---|---:|---:|---|---|
| 1 | SOXX long | 37 | +28.9 | 0.004/658 | G2,G3,G4,G5 |
| 2 | XLE long | 61 | +22.9 | 0.007/658 | G2,G3,G4,G5 |
| 3 | XLF long | 48 | +16.9 | 0.010/658 | G2,G3,G4,G5 |
| 4 | XLK long | 64 | +8.0 | 0.002/658 | G2,G3,G4,G5 |
| 5 | QQQ long | 81 | +6.0 | 0.003/658 | G1,G2,G3,G4,G5 |

### CRYPTO (40 tested; includes meme coins) — class DEAD
| # | Pick | n | net bp | DSR/N | fails |
|---|---|---:|---:|---|---|
| 1 | ENJ long | 30 | +93.0 | 0.005/658 | G2,G3,G4,G5 |
| 2 | ETH long | 155 | +18.2 | 0.064/658 | G1,G2,G3,G4,G5 |
| 3 | WIF long (meme) | 146 | +13.4 | 0.067/658 | G1,G2,G3,G4,G5 |
| 4 | NEAR long | 219 | −3.0 | 0.013/658 | G1,G2,G3,G4,G5 |
| 5 | JUP long | 162 | −4.6 | 0.026/658 | G1,G2,G3,G4,G5 |

### FOREX (2 tested) — class DEAD
| # | Pick | n | net bp | DSR/N | fails |
|---|---|---:|---:|---|---|
| 1 | AUDJPY long | 34 | +51.3 | **0.815**/658 | G2,G3,G4,G5 |
| 2 | EURUSDT long | 20 | −170.8 | 0.001/658 | G1,G2,G3,G4,G5 |

### BONDS (1 tested) — class DEAD
| # | Pick | n | net bp | DSR/N | fails |
|---|---|---:|---:|---|---|
| 1 | TLT long | 31 | −12.4 | 0.000/658 | G1,G2,G3,G4,G5 |

### MUTUAL FUNDS — UNMEASURED (no instrument-level series)
No pick. Fee drag measured as an assumption only (see below). Class is `UNKNOWN`, not `DEAD`.

### COMMODITIES — class DEAD (negative-expectancy, 0 usable rows)
### OPTIONS — UNMEASURED (no options data layer)
### PREDICTION MARKETS — UNMEASURED (maker-only evidence, no measured OOS edge)
### PRIVATE CREDIT — UNMEASURED (no data)

## Overall ranking — across all asset classes
Ranked by evidence quality (DSR first, then net bp), **not** by return alone. Every one fails at least one gate.

| # | Pick | Class | DSR/N | net bp | Why it sits here |
|---|---|---|---:|---:|---|
| 1 | **AUDJPY long** | FOREX | **0.815**/658 | +51.3 | Highest credible DSR anywhere; only ~14 trades from clearing G3 — but FX historical feed ends 2026-02-09 |
| 2 | **CVX long** | STOCKS | 0.318/658 | +168.1 | Highest net bp with real n; ~83 trades from G3; STOCKS have no hold-times so G2/G4 unmeasurable |
| 3 | **AAPL long** | STOCKS | 0.106/658 | +48.3 | Largest n among STOCKS leaders (81); DSR still 9× below the bar |
| 4 | **ETH long** | CRYPTO | 0.064/658 | +18.2 | Best large-n crypto (155) but net only clears cost at the major band |
| 5 | **SOXX long** | ETF | 0.004/658 | +28.9 | Cheapest execution (6.71 bp) and sector momentum, but no deflated edge |

## THE ANSWER — where money is actually worth spending
**None of the 69 strategy picks is worth real money.** The only defensible real-money action is a
**broad, low-cost index ETF held long** — a *buying* decision (beta), not an *edge*.

**Why (the reason):**
1. **No pick clears the deflation gate.** Best credible DSR is 0.815 (AUDJPY) and 0.318 (CVX) against a 0.95 bar;
   everything else is <0.11. An edge that cannot beat the best of 658 trials is indistinguishable from luck.
2. **The two near-misses are unmeasurable.** AUDJPY's class feed is dead; STOCKS have no entry→exit hold-times, so
   G2/G4 cannot be evaluated. We cannot promote what we cannot measure.
3. **Costs eat the rest.** At the cost of record, 49/69 instruments go net ≤ 0; only ENJ, ETH, WIF remain positive,
   and all fail DSR.
4. **The universe is survivorship-biased** (0 delisted names), which biases STOCKS/ETF *upward* — so even these
   numbers are optimistic.

**Bar any active strategy must clear to be worth it:** beat the index ETF by **+3.34%/yr at $1k tickets** or
**+0.80%/yr at $25k tickets** (measured fees + turnover), with a paired CI on net return vs the ETF that excludes zero.

## Mutual funds — you flagged them as likely winners; here is the fee arithmetic
10-year cost on $100,000 (implied MER, **assumed**, sector-typical not fund-specific):

| Vehicle | 10-y cost | implied/yr | vs ETF |
|---|---:|---:|---:|
| Direct holdings | $50 | 0.005% | 0.05× |
| **Broad index ETF** | **$1,050** | **0.105%** | **1×** |
| Index mutual fund | $4,520 | 0.452% | 4.3× |
| Active mutual fund | $18,520 | 1.852% | **17.6×** |

Mutual funds win on **access and automation** (no ticket minimum on many platforms, automatic contributions,
no bid/ask), and a *low-MER index mutual fund* is a legitimate default for a small, recurring account. But the fee
gap is decisive over long horizons: an active fund must beat the index by **~1.75%/yr net** just to break even on
fees, which our deflation work shows almost nothing achieves. **Verdict: index ETF if you can; index mutual fund
only when minimums/friction make the ETF impractical; avoid active funds on cost grounds.**

## Meme coins (you asked specifically)
Meme coins (WIF, FLOKI, etc.) sit in the crypto-alt band at a **52 bp** round-trip cost — the highest in the estate.
WIF is the only meme coin net-positive in this scan (+13.4 bp, n=146) and its DSR is 0.067, i.e. noise. Meme coins are
the **worst cost-to-edge ratio** in the entire study. Not investable.

## Honest headline
Across every asset class we have a ranking; the overall picks worth spending money on are **none of the strategies —
the money belongs in a low-cost broad index ETF.** The reason is that no strategy survives deflation at the honest
trial count, the two nearest candidates are unmeasurable, and measured costs plus survivorship bias remove the rest.

*Paper only. Zero capital. Not investment advice.*
