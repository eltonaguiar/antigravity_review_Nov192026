# PROVEIT — KILOCODE

Date-folder: `PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT/`
Agent: **KILO CODE** (Kilo VS Code) · Paper only, zero capital, not investment advice.

## Contents
| file | what |
|---|---|
| `simulate_proveit.py` | fee-aware simulation engine (buy&hold / 60-40 / 200d-MA timing) over `data/market_prices.csv` (adjusted). Re-runnable. |
| `SIM_<utc>.json` | date-time-stamped simulation dump (a new one per run). |
| `PROVEIT_REPORT_<utc>.md` | dated report: philosophy + rules, backtest (common window), $300/$500/$2000/$10000 scenarios with fee math, per-class endorsement, and the honest proof. |
| `data/market_prices.csv` | adjusted+close daily bars used (2021-11→2026-11). |

## How to reproduce
```
cd PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT
python3 simulate_proveit.py     # writes a new SIM_<timestamp>.json
```

## Headline (this run)
Buy-and-hold low-cost equity: **18.3%/yr, −18.8% DD, excess-of-cash Sharpe 0.86** (`sharpe_excess` = 0.859 in `SIM_2026-11-24T0321Z.json`; it is a Sharpe *over cash*, not a raw Sharpe). 60/40: 11.96%/−11.2%. 200d-MA timing: 13.76%/−9.4% (**risk control, not alpha**). Fees cost a $300 account **2.09%** vs $10,000 **0.69%** → small accounts must use zero-commission, no-FX index funds. **0 active-edge proof; the provable edge is cheap, patient, diversified beta.**

## Merged in: the scenario-portfolio findings (2026-11-24)

`MERGE_FROM_MARKETS_2026-11-24/` holds the simulator and README from the former
`PROVEIT_24-11-2026KILOCODE_AGENT/` folder, merged here and removed there. Its unique
findings, kept because they are not reproduced elsewhere:

- **At $300 the 60/40 cannot be built.** One SPY share cost about $374 at start
  (unsourced in this folder: `data/market_prices.csv` records SPY_adj 437.19 and
  SPY_close 467.43 on 2021-11-15, and no artifact contains 374.84), so with
  whole shares 72% of a $300 account is idle cash and the 5-year result is -0.92%/yr
  -- not because the market fell (SPY went 437 -> 754) but because the position was
  never expressible. Instrument choice (a low-share-price ETF or fractional shares),
  not strategy choice, fixes this.
- **Per-size endorsement:** $300/$500 -> low-price broad ETF or fractional broker;
  $2,000 -> 60/40 becomes buildable; $10,000 -> 60/40 or a 3-fund, cost not binding.
- **No philosophy beat holding.** At $10,000: buy-and-hold 9.18%/yr, rebalance 7.52%,
  TP/SL 8.56% (and it paid $44.61 in costs to land BELOW doing nothing), 200d trend
  10.49% (almost certainly a single-window artefact -- the sweep found 0 PASS).
- The merged README also keeps its own error log: an early engine passed a slice of
  cash into `buy()` and deleted the remainder, producing a nonsense -$72 result that
  looked like a finding.

## Update protocol
Each revision appends a new `PROVEIT_REPORT_<utc>.md` (and optionally moves prior to `OLD/`); never silently overwrite — the date stamps are the audit trail.
