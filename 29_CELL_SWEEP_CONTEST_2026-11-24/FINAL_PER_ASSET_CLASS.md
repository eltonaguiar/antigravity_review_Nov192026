# Final findings per asset class — cell sweep 2026-11-24

Source: `results/cells/*.json` cross-referenced against `1000_TODOS.json`. Every number below is read from those files, not retyped.

## COVERAGE WARNING — read before the table

The sweep ran **crypto-first**. Of 1000 ledger cells, the crypto class is the only one with measured artifacts. **EQUITY, FOREX, BOND_ETF and COMMODITY_ETF have zero measured cells and therefore no findings.** The table's `in ledger` column makes this explicit; the `measured` column would otherwise read as 'measured and empty', which is a different and false claim.

**Headline: 0 PASS across all measured classes.** Not one cell met the pre-declared bar (CI excluding zero *and* DSR > 0.95 at 1000 trials).

| asset class | in ledger | resolved | measured | KILL | PASS | median net bp | best cell |
|---|---:|---:|---:|---:|---:|---:|---|
| **CRYPTO** | 350 | 107 | 28 | 12 | 0 | -31.09 | `SOLUSDT/breakout/1d` +71.90 |
| **BOND_ETF** | 50 | 0 | 0 | 0 | 0 | n/a | — |
| **COMMODITY_ETF** | 50 | 0 | 0 | 0 | 0 | n/a | — |
| **EQUITY** | 400 | 1 | 0 | 0 | 0 | n/a | — |
| **FOREX** | 150 | 1 | 0 | 0 | 0 | n/a | — |

## Per-class commentary

### CRYPTO

- Cells measured: 28 (38 more had n<30, 38 blocked)
- Verdicts: **12 KILL**, **0 PASS**
- Median net bp/trade after 26bp: **-31.09**
- Best: `SOLUSDT/breakout/1d` +71.90bp (DSR 0.0045, p 0.013)
- Worst: `SOLUSDT/vol_compression/1d` -153.85bp
- **The best cell is not a PASS.** Its DSR is 0.0045 against 1000 trials; a positive point estimate selected from 1000 tries carries essentially no evidential weight.

### BOND_ETF

No measurable cells (0 blocked, 0 insufficient trades). **No finding is possible for this class** — stating otherwise would be fabrication.

### COMMODITY_ETF

No measurable cells (0 blocked, 0 insufficient trades). **No finding is possible for this class** — stating otherwise would be fabrication.

### EQUITY

No measurable cells (0 blocked, 1 insufficient trades). **No finding is possible for this class** — stating otherwise would be fabrication.

### FOREX

No measurable cells (0 blocked, 1 insufficient trades). **No finding is possible for this class** — stating otherwise would be fabrication.

