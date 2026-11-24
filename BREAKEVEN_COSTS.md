# Breakeven Costs — Cost per Trade at Zero Net Expectancy

**Method:** breakeven cost per round trip (bps) = gross annual expectancy (bps) / round trips per year; net = gross - cost(bps) * round trips / 10000.

**Universe:** 24 symbols (AAPL, MSFT, AMZN, GOOG, META, TSLA, NVDA, JPM, V, UNH, HD, PG, DIS, NFLX, ADBE, KO, PEP, COST, WMT, CSCO, TXN, AVGO, QCOM, SPY)
**Sample:** 120 months (10 years)

## Results

| Candidate | Gross %/yr | Round trips/yr | Breakeven bps/round trip | Net @ 1bp | Net @ 5bp | Net @ 10bp |
|-----------|-----------|----------------|--------------------------|-----------|-----------|------------|
| SPY buy-and-hold | 13.642 | 0.5 | 2,728.4 | 13.637% | 13.617% | 13.592% |
| 12-1 momentum long-short quintile | -0.623 | 12.0 | 0.0 | -0.743% | -1.223% | -1.823% |
| 12-1 momentum long-only top quintile | 30.038 | 12.0 | 250.3 | 29.918% | 29.438% | 28.838% |

## Interpretation

- **SPY buy-and-hold:** Turnover ~0 (buy once, hold ~10 years). Breakeven at 2,728 bps per round trip — effectively not binding. Costs are irrelevant for this strategy.
- **12-1 momentum long-short:** Gross is already negative (-0.623%/yr). Breakeven is 0 bps — the strategy is net-negative at zero cost. It cannot be rescued by lower costs.
- **12-1 momentum long-only top quintile:** Gross +30.04%/yr with 12 round trips/year. Breakeven at 250 bps per round trip (2.50%). At 1 bp net is ~29.9%; at 5 bp net is ~29.4%; at 10 bp net is ~28.8%. Costs are survivable but material.

**Source:** `CONTEST/tools/breakeven_costs.py` → `reports/breakeven_costs.json`

*Paper only. Zero capital. Not investment advice.*
