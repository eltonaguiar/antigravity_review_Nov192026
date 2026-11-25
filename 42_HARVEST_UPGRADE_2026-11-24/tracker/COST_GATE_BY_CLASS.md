# Cost gate by asset class and symbol — resolved trades only

Read-only query of `ejaguiar1_stocks.at_pick_outcomes`, 2026-11-25. Credentials read at runtime; never printed or committed.

## Before vs after the EXPIRED/FLAT exclusion

| stage | rows |
|---|---:|
| raw at_pick_outcomes | 63,792 |
| pnl_pct exactly 0 | 29,577 |
| EXPIRED | 29,654 |
| FLAT | 1,046 |
| excluded (EXPIRED + FLAT) | 30,700 |
| WON | 13,654 |
| LOST | 19,438 |
| **resolved after exclusion** | **33,092** |

**Overall resolved:** n=33,092, mean **+6.34 bp**, median **-38.98 bp**, WR 41.2%, avg win +302.40 bp, avg loss -201.36 bp. The earlier report's median 0.00 was the EXPIRED/FLAT pile.

EXPIRED/FLAT are not resolutions: EXPIRED stores zero on 28,531/29,654 rows; FLAT is 1,046/1,046 zero. The brief's “+0.065%” is **6.34 bp** here (not 2.5 bp) against a 26 bp round turn.

## Cost assumptions (unchanged from 71d1733)

Crypto 36 bp midpoint of measured 20-52; FOREX 7.53 upper-bound; commodity 20 assumed; equity 4.01 central (12.07 stress); futures 12.07 proxy; index/ETF 6.71; bond 0.61; meme 52; unknown 12.07. The coverage/class mapping is an assumption; the bp values are measured.

## Asset-class table

| class | n | mean bp | median bp | cost bp | mean net | median net | WR | mean > cost | median > cost | powered (n>=100) | breakeven cost | verdict | payoff flag |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---|---|
| CRYPTO | 28,677 | +8.85 | -100.00 | 36.00 | -27.15 | -136.00 | 41.6% | False | False | True | 8.8461 | BREAKEVEN-COST-NEEDED 8.85 bp | True |
| FOREX | 2,789 | +32.45 | -0.69 | 7.53 | +24.92 | -8.22 | 39.7% | True | False | True | 32.4536 | CLEARS-COST | True |
| COMMODITY | 891 | -70.11 | -13.08 | 20.00 | -90.11 | -33.08 | 37.1% | False | False | True | none | FAILS-COST | False |
| EQUITY | 233 | -80.72 | -150.00 | 4.01 | -84.73 | -154.01 | 36.9% | False | False | True | none | FAILS-COST | False |
| FUTURES | 29 | +88.03 | -87.89 | 12.07 | +75.96 | -99.96 | 41.4% | True | False | False | 88.0293 | CLEARS-COST | True |
| INDEX | 3 | +5.37 | +5.94 | 6.71 | -1.34 | -0.77 | 100.0% | False | False | False | 5.3733 | BREAKEVEN-COST-NEEDED 5.37 bp | False |
| ETF | 23 | +27.07 | -291.91 | 6.71 | +20.36 | -298.62 | 17.4% | True | False | False | 27.0709 | CLEARS-COST | True |
| BOND | 16 | +21.03 | -58.31 | 0.61 | +20.42 | -58.92 | 25.0% | True | False | False | 21.0331 | CLEARS-COST | True |
| MEME | 70 | -304.05 | -163.69 | 52.00 | -356.05 | -215.69 | 30.0% | False | False | False | none | FAILS-COST | False |
| UNKNOWN | 141 | -202.10 | -515.00 | 12.07 | -214.17 | -527.07 | 37.6% | False | False | True | none | FAILS-COST | False |
| BLANK | 189 | +8.61 | -501.00 | 12.07 | -3.46 | -513.07 | 46.0% | False | False | True | 8.606 | BREAKEVEN-COST-NEEDED 8.61 bp | True |
| STOCKS | 11 | -188.30 | +21.35 | 4.01 | -192.31 | +17.34 | 63.6% | False | True | False | none | FAILS-COST | False |
| STOCK | 14 | -24.00 | -0.45 | 4.01 | -28.01 | -4.46 | 35.7% | False | False | False | none | FAILS-COST | False |
| PENNY | 2 | -360.00 | -360.00 | 52.00 | -412.00 | -412.00 | 0.0% | False | False | False | none | FAILS-COST | False |
| PENNYSTOCK | 4 | -1321.20 | -1321.20 | 52.00 | -1373.20 | -1373.20 | 0.0% | False | False | False | none | FAILS-COST | False |

**Class-level:** mean beats own cost in **4/10** known classes all-in, but only **1/10** with n>=100 (FOREX). Median beats own cost in **0/10**. Small-n CLEARS (FUTURES 29, ETF 23, BOND 16) are **underpowered/nominal**, not deployable.

## Findings

- **FOREX:** mean **+32.45 bp** vs 7.53 cost, but median **−0.69 bp**, WR 39.7% and payoff-shape flag; 1,185 wins/+135.93 vs 1,762 losses/−40.14 in the old all-status view — now resolved-only. Mean clear does **not** survive the median/payoff-shape check.
- **CRYPTO:** mean **+8.85 bp** vs 36 cost, median **−100 bp**; BREAKEVEN-COST-NEEDED 8.85 bp; not close to current cost.
- **FUTURES/ETF/BOND/INDEX:** nominal mean clears/breakeven at n=29/23/16/3; all **below the 100 floor**, so UNDERDETERMINED, not endorsements.
- **COMMODITY/EQUITY/MEME/UNKNOWN:** fail at the mean (−70.11/−80.72/−304.05/−202.10 bp).
- **No class clears on both mean and median.** The only powered mean-clear class (FOREX) has a negative median and payoff-shape signature.

## What EXPIRED should mean

An EXPIRED row with pnl_pct=0 is not a resolution. It should be resolved against the price at expiry (or removed from the table); 29,654 picks (46.5%) reaching neither TP nor SL is an exit-logic finding. `trading_picks` shows **31,421 TIME_EXIT_MAX_HOLD** rows, consistent with a system that runs out of time rather than resolving P&L. Do not treat zeros as flat outcomes.

## Per-symbol detail

Full machine-readable table in `COST_GATE_BY_CLASS.json` (`symbols`, 88 rows with n>=30). Top rows by n:

| class | symbol | n | mean bp | median bp | cost bp | mean > cost | median > cost | verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| CRYPTO | BTCUSDT | 2670 | +3.75 | -114.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 3.75 bp |
| CRYPTO | SOLUSDT | 2229 | +30.92 | -85.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 30.92 bp |
| CRYPTO | ETHUSDT | 2156 | +42.32 | -5.51 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | DOGEUSDT | 1797 | +71.16 | -6.79 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | AVAXUSDT | 1624 | +69.43 | +1.72 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | ADAUSDT | 1297 | -9.88 | -18.55 | 36.00 | False | False | FAILS-COST |
| CRYPTO | DOTUSDT | 1056 | +45.13 | -6.17 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | NEARUSDT | 1009 | -2.48 | -160.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | XRPUSDT | 972 | -11.47 | -24.89 | 36.00 | False | False | FAILS-COST |
| CRYPTO | LINKUSDT | 744 | -6.85 | -103.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | BNBUSDT | 726 | +20.04 | +0.04 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 20.04 bp |
| CRYPTO | JUPUSDT | 710 | +65.60 | +2.55 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | SUIUSDT | 659 | +12.39 | -100.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 12.39 bp |
| CRYPTO | SAND-USD | 621 | -98.35 | -200.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | RENDERUSDT | 564 | +92.70 | +1.21 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | ENAUSDT | 560 | +14.58 | +3.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 14.58 bp |
| CRYPTO | ARBUSDT | 508 | +81.40 | -100.00 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | DOT-USD | 406 | -3.45 | -150.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | WIFUSDT | 400 | +33.70 | +0.68 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 33.70 bp |
| CRYPTO | APTUSDT | 395 | -32.17 | -150.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | MANA-USD | 384 | -69.87 | -200.00 | 36.00 | False | False | FAILS-COST |
| FOREX | USDJPY=X | 381 | -17.19 | -0.56 | 7.53 | False | False | FAILS-COST |
| FOREX | EURJPY=X | 366 | -26.29 | -7.76 | 7.53 | False | False | FAILS-COST |
| FOREX | AUDJPY=X | 350 | -9.40 | -2.77 | 7.53 | False | False | FAILS-COST |
| FOREX | GBPJPY=X | 328 | +15.99 | -1.58 | 7.53 | True | False | CLEARS-COST |

next_probe: resolve EXPIRED picks against the expiry price, then rerun this table on true resolutions; do not turn the 29,654 zero rows into flat outcomes.
