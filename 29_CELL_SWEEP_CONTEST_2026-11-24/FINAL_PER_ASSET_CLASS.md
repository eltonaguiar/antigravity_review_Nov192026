# Final findings per asset class — cell sweep 2026-11-24

Source: `results/cells/*.json` cross-referenced against `1000_TODOS.json`. Every number below is read from those files, not retyped.

## COVERAGE WARNING — read before the table

The sweep ran **crypto-first**. Of 1000 ledger cells, the crypto class is the only one with measured artifacts. **EQUITY, FOREX, BOND_ETF and COMMODITY_ETF have zero measured cells and therefore no findings.** The table's `in ledger` column makes this explicit; the `measured` column would otherwise read as 'measured and empty', which is a different and false claim.

**Cross-reference:** `30_COST_STRUCTURE_2026-11-24/COST_VS_SIGNAL.md` splits this null into a *signal* problem (median gross <= 0) and a *cost* problem (gross edge exists but is below the 26bp round-turn). The `diagnosis` column below carries that verdict per class, so this table and that document cannot be read as disagreeing.

**Headline: 0 PASS across all measured classes.** Not one cell met the pre-declared bar (CI excluding zero *and* DSR > 0.95 at 1000 trials).

| asset class | in ledger | resolved | measured | KILL | PASS | median net bp | median gross bp | diagnosis | best cell |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| **EQUITY** | 400 | 12 | 6 | 4 | 0 | -20.69 | +5.31 | COST problem (gross edge < 26bp) | `SPY/donchian/1d` -14.86 |
| **FOREX** | 150 | 6 | 2 | 2 | 0 | -22.25 | +3.75 | COST problem (gross edge < 26bp) | `EURUSD/trend_pullback/1d` -21.66 |
| **COMMODITY_ETF** | 50 | 10 | 5 | 2 | 0 | -22.76 | +3.24 | COST problem (gross edge < 26bp) | `GLD/breakout/1w` -6.85 |
| **CRYPTO** | 350 | 107 | 28 | 12 | 0 | -31.09 | -5.10 | SIGNAL problem (no gross edge) | `SOLUSDT/breakout/1d` +71.90 |
| **BOND_ETF** | 50 | 10 | 3 | 3 | 0 | -43.29 | -17.29 | SIGNAL problem (no gross edge) | `TLT/breakout/1d` -34.83 |

## Per-class commentary

### EQUITY

- Cells measured: 6 (6 more had n<30, 0 blocked)
- Verdicts: **4 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-20.69**
- Best: `SPY/donchian/1d` -14.86bp (DSR 0.0, p 0.209)
- Worst: `SPY/trend_pullback/1d` -29.44bp

### FOREX

- Cells measured: 2 (5 more had n<30, 0 blocked)
- Verdicts: **2 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-22.25**
- Best: `EURUSD/trend_pullback/1d` -21.66bp (DSR 0.0, p 0.105)
- Worst: `EURUSD/vol_compression/1d` -22.84bp

### COMMODITY_ETF

- Cells measured: 5 (5 more had n<30, 0 blocked)
- Verdicts: **2 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-22.76**
- Best: `GLD/breakout/1w` -6.85bp (DSR 0.0001, p 0.697)
- Worst: `GLD/vol_compression/1d` -45.17bp

### CRYPTO

- Cells measured: 28 (38 more had n<30, 38 blocked)
- Verdicts: **12 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-31.09**
- Best: `SOLUSDT/breakout/1d` +71.90bp (DSR 0.0045, p 0.013)
- Worst: `SOLUSDT/vol_compression/1d` -153.85bp
- **The best cell is not a PASS.** Its DSR is 0.0045 against 1000 trials; a positive point estimate selected from 1000 tries carries essentially no evidential weight.

### BOND_ETF

- Cells measured: 3 (7 more had n<30, 0 blocked)
- Verdicts: **3 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-43.29**
- Best: `TLT/breakout/1d` -34.83bp (DSR 0.0, p 0.736)
- Worst: `TLT/donchian/1d` -60.05bp

