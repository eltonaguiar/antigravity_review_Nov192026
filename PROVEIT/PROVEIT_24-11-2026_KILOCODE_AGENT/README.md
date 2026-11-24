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
Buy-and-hold low-cost equity: **18.3%/yr, −18.8% DD, Sharpe 0.86**. 60/40: 11.96%/−11.2%. 200d-MA timing: 13.76%/−9.4% (**risk control, not alpha**). Fees cost a $300 account **2.09%** vs $10,000 **0.69%** → small accounts must use zero-commission, no-FX index funds. **0 active-edge proof; the provable edge is cheap, patient, diversified beta.**

## Update protocol
Each revision appends a new `PROVEIT_REPORT_<utc>.md` (and optionally moves prior to `OLD/`); never silently overwrite — the date stamps are the audit trail.
