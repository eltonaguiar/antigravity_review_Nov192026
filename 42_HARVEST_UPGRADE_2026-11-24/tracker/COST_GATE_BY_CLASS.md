# Cost gate by asset class and symbol

Read-only query of `ejaguiar1_stocks.at_pick_outcomes`, 2026-11-25. Credentials read at runtime; never printed or committed.

## Filter counts

- raw rows: **63,787**
- pnl_pct non-null: **63,787**
- WON/LOST/EXPIRED/FLAT: **63,787**
- class-known after uppercase normalisation: **63,787**

Known-class total is 63,482 (CRYPTO 38,208 vs the brief 38,204; 4-row difference). Extra 305 rows are BLANK/STOCKS/STOCK/PENNY/PENNYSTOCK; shown below, not pooled.

## Cost assumptions (round turn)

| class | cost bp | basis |
|---|---:|---|
| CRYPTO | 36.00 | midpoint of measured 20-52 bp; perp fees/spreads above equity |
| FOREX | 7.53 | upper-bound measured |
| COMMODITY | 20.00 | assumed 20 bp (not measured) |
| EQUITY | 4.01 | central measured bracket; ceiling 12.07 bp is stress |
| FUTURES | 12.07 | equity ceiling proxy; no roll-adjusted series |
| INDEX | 6.71 | ETF/index measured |
| ETF | 6.71 | measured |
| BOND | 0.61 | measured |
| MEME | 52.00 | widest measured crypto band |
| UNKNOWN | 12.07 | equity central proxy |
| BLANK | 12.07 | equity central proxy |
| STOCKS | 4.01 | equity central |
| STOCK | 4.01 | equity central |
| PENNY | 52.00 | crypto widest proxy |
| PENNYSTOCK | 52.00 | crypto widest proxy |

Crypto uses 36 bp (midpoint of measured 20-52 band); equity uses central measured 4.01 bp, with 12.07 bp as stress. Commodity is assumed; futures has no roll-adjusted series.

## Asset-class table

| class | n | mean bp | median bp | cost bp | mean net | median net | WR | mean > cost | median > cost | breakeven cost | verdict | payoff flag |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|---|
| CRYPTO | 38,208 | +2.87 | +0.00 | 36.00 | -33.13 | -36.00 | 32.2% | False | False | 2.8748 | BREAKEVEN-COST-NEEDED 2.87 bp | True |
| FOREX | 16,039 | +5.63 | +0.00 | 7.53 | -1.90 | -7.53 | 7.4% | False | False | 5.6329 | BREAKEVEN-COST-NEEDED 5.63 bp | True |
| COMMODITY | 5,882 | -10.32 | +0.00 | 20.00 | -30.32 | -20.00 | 5.9% | False | False | none | FAILS-COST | False |
| EQUITY | 1,984 | -8.84 | +0.00 | 4.01 | -12.85 | -4.01 | 4.6% | False | False | none | FAILS-COST | False |
| FUTURES | 473 | +6.84 | +0.00 | 12.07 | -5.23 | -12.07 | 3.4% | False | False | 6.839 | BREAKEVEN-COST-NEEDED 6.84 bp | True |
| INDEX | 314 | +0.05 | +0.00 | 6.71 | -6.66 | -6.71 | 1.0% | False | False | 0.0513 | BREAKEVEN-COST-NEEDED 0.05 bp | True |
| ETF | 181 | +5.88 | +0.00 | 6.71 | -0.83 | -6.71 | 5.5% | False | False | 5.8829 | BREAKEVEN-COST-NEEDED 5.88 bp | True |
| BOND | 154 | +2.19 | +0.00 | 0.61 | +1.58 | -0.61 | 2.6% | True | False | 2.1853 | CLEARS-COST | True |
| MEME | 106 | -200.79 | +0.00 | 52.00 | -252.79 | -52.00 | 21.7% | False | False | none | FAILS-COST | False |
| UNKNOWN | 141 | -202.10 | -515.00 | 12.07 | -214.17 | -527.07 | 37.6% | False | False | none | FAILS-COST | False |
| BLANK | 204 | +7.97 | -40.04 | 12.07 | -4.10 | -52.11 | 42.6% | False | False | 7.9732 | BREAKEVEN-COST-NEEDED 7.97 bp | True |
| STOCKS | 54 | -38.36 | +0.00 | 4.01 | -42.37 | -4.01 | 13.0% | False | False | none | FAILS-COST | False |
| STOCK | 33 | -9.90 | +0.01 | 4.01 | -13.91 | -4.00 | 51.5% | False | False | none | FAILS-COST | False |
| PENNY | 7 | -102.86 | +0.00 | 52.00 | -154.86 | -52.00 | 0.0% | False | False | none | FAILS-COST | False |
| PENNYSTOCK | 7 | -635.85 | -1179.70 | 52.00 | -687.85 | -1231.70 | 42.9% | False | False | none | FAILS-COST | False |

**Class-level share:** mean beats own cost in **1/10** known classes (BOND only); median beats own cost in **0/10**. BOND is a payoff-shape artifact (4 wins, 12 losses, median 0, 2.6% WR), not a tradable class.

## Per-class symbol shares (symbols with n>=30)

| class | symbols | mean > cost | median > cost |
|---|---:|---:|---:|
| CRYPTO | 80 | 21.2% | 7.5% |
| FOREX | 12 | 16.7% | 0.0% |
| COMMODITY | 11 | 0.0% | 0.0% |
| EQUITY | 23 | 30.4% | 0.0% |
| FUTURES | 4 | 25.0% | 0.0% |
| INDEX | 3 | 0.0% | 0.0% |
| BOND | 3 | 33.3% | 0.0% |
| UNKNOWN | 1 | 0.0% | 0.0% |

## Findings

- **No class clears cost on the median.** Every class median is 0.0 bp except UNKNOWN (-515.0), BLANK (-40.04) and PENNYSTOCK (-1179.7); the zero mass is EXPIRED/flat outcomes.
- **BOND is the only mean-clear class** (2.19 bp vs 0.61 bp), but 4 wins / 12 losses / 154 rows and median 0 -> payoff-shape artifact, not an edge.
- **FOREX is the textbook payoff-shape artifact:** 1,185 wins at +135.93 bp vs 1,762 losses at -40.14 bp, 7.4% WR, 13,092 flat/expired; median 0. Breakeven 5.63 bp vs 7.53 bp cost.
- **CRYPTO** mean 2.87 bp vs 36 bp cost; 32.2% WR; breakeven 2.87 bp. **FUTURES** 6.84 vs 12.07; **ETF** 5.88 vs 6.71; **INDEX** 0.05 vs 6.71 -- all need costs at/below breakeven, which current execution does not provide.
- **EQUITY, COMMODITY, MEME, UNKNOWN fail at the mean** before cost (-8.84, -10.32, -200.79, -202.10 bp).

## Verdicts (exact)
- **CRYPTO:** BREAKEVEN-COST-NEEDED 2.87 bp (mean +2.87 bp, median +0.00 bp, cost 36.00 bp).
- **FOREX:** BREAKEVEN-COST-NEEDED 5.63 bp (mean +5.63 bp, median +0.00 bp, cost 7.53 bp).
- **COMMODITY:** FAILS-COST (mean -10.32 bp, median +0.00 bp, cost 20.00 bp).
- **EQUITY:** FAILS-COST (mean -8.84 bp, median +0.00 bp, cost 4.01 bp).
- **FUTURES:** BREAKEVEN-COST-NEEDED 6.84 bp (mean +6.84 bp, median +0.00 bp, cost 12.07 bp).
- **INDEX:** BREAKEVEN-COST-NEEDED 0.05 bp (mean +0.05 bp, median +0.00 bp, cost 6.71 bp).
- **ETF:** BREAKEVEN-COST-NEEDED 5.88 bp (mean +5.88 bp, median +0.00 bp, cost 6.71 bp).
- **BOND:** CLEARS-COST (mean +2.19 bp, median +0.00 bp, cost 0.61 bp).
- **MEME:** FAILS-COST (mean -200.79 bp, median +0.00 bp, cost 52.00 bp).
- **UNKNOWN:** FAILS-COST (mean -202.10 bp, median -515.00 bp, cost 12.07 bp).

## Per-symbol detail (n>=30)

Full machine-readable table is in `COST_GATE_BY_CLASS.json` (`symbols`, 137 rows). Top rows by n:

| class | symbol | n | mean bp | median bp | cost bp | mean > cost | median > cost | verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| CRYPTO | BTCUSDT | 5352 | -2.49 | +0.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | ETHUSDT | 3543 | +21.69 | +0.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 21.69 bp |
| CRYPTO | SOLUSDT | 2785 | +25.08 | +0.00 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 25.08 bp |
| CRYPTO | DOGEUSDT | 2381 | +52.48 | +0.00 | 36.00 | True | False | CLEARS-COST |
| FOREX | EURJPY=X | 1893 | -5.08 | +0.00 | 7.53 | False | False | FAILS-COST |
| CRYPTO | AVAXUSDT | 1755 | +60.78 | +0.00 | 36.00 | True | False | CLEARS-COST |
| FOREX | GBPJPY=X | 1673 | +3.14 | +0.00 | 7.53 | False | False | BREAKEVEN-COST-NEEDED 3.14 bp |
| FOREX | USDCAD=X | 1630 | +2.88 | +0.00 | 7.53 | False | False | BREAKEVEN-COST-NEEDED 2.88 bp |
| FOREX | AUDUSD=X | 1618 | -2.88 | +0.00 | 7.53 | False | False | FAILS-COST |
| FOREX | AUDJPY=X | 1599 | -2.06 | +0.00 | 7.53 | False | False | FAILS-COST |
| CRYPTO | XRPUSDT | 1514 | -11.17 | +0.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | ADAUSDT | 1413 | -10.97 | -10.19 | 36.00 | False | False | FAILS-COST |
| FOREX | USDJPY=X | 1374 | -5.35 | +0.00 | 7.53 | False | False | FAILS-COST |
| FOREX | CADJPY=X | 1342 | +63.61 | +0.00 | 7.53 | True | False | CLEARS-COST |
| FOREX | EURGBP=X | 1309 | +0.90 | +0.00 | 7.53 | False | False | BREAKEVEN-COST-NEEDED 0.90 bp |
| CRYPTO | BNBUSDT | 1297 | -2.21 | +0.00 | 36.00 | False | False | FAILS-COST |
| COMMODITY | SI=F | 1158 | -21.67 | +0.00 | 20.00 | False | False | FAILS-COST |
| FOREX | NZDUSD=X | 1146 | +14.69 | +0.00 | 7.53 | True | False | CLEARS-COST |
| FOREX | GBPUSD=X | 1108 | +0.86 | +0.00 | 7.53 | False | False | BREAKEVEN-COST-NEEDED 0.86 bp |
| CRYPTO | DOTUSDT | 1096 | +42.27 | -3.42 | 36.00 | True | False | CLEARS-COST |
| CRYPTO | NEARUSDT | 1093 | -4.26 | -149.00 | 36.00 | False | False | FAILS-COST |
| COMMODITY | GC=F | 1048 | -2.86 | +0.00 | 20.00 | False | False | FAILS-COST |
| CRYPTO | LINKUSDT | 835 | -27.94 | -100.00 | 36.00 | False | False | FAILS-COST |
| CRYPTO | SUIUSDT | 755 | +13.57 | -0.04 | 36.00 | False | False | BREAKEVEN-COST-NEEDED 13.57 bp |
| COMMODITY | HG=F | 753 | -7.06 | +0.00 | 20.00 | False | False | FAILS-COST |

next_probe: rerun with symbol-clustered CIs and a cost-sensitivity column at the 12.07 bp equity ceiling; do not promote BOND or FOREX without a payoff-shape test.
