# PROVEIT — does rebalancing / a 5-pt drift band actually help? (VERIFYING my own claim)

**KILO CODE · 2026-11-24T0350Z · `simulate_rebalance_band.py` · 60/40 SPY/BND · total-return · paper only, not advice.**
I had written in MANAGED_PORTFOLIO_ALERTS that drift-band rebalancing beats calendar-only. **I measured it; that was overstated and is corrected.**

| rule | CAGR | max DD | excess Sharpe | # rebalances |
|---|---:|---:|---:|---:|
| buy & hold equity (ref) | 11.58% | — | — | — |
| 60/40 **monthly** | 6.91% | −20.73% | 0.313 | 59 |
| 60/40 **annual** | 6.91% | −20.92% | 0.312 | 4 |
| 60/40 **band ±5pt** | 6.95% | −20.92% | 0.315 | 2 |
| 60/40 **band ±10pt** | 7.19% | −20.92% | 0.330 | 1 |
| 60/40 **never rebalance** | **7.44%** | −20.92% | **0.346** | 0 |

## Findings (honest)
1. **Not rebalancing won this window** (7.44% vs 6.91% monthly) and had the best Sharpe (0.346 vs 0.313). Rebalancing sold the winning sleeve (equity) into the losing one (bonds) — **rebalancing drag** when one asset dominates.
2. **Rebalancing did NOT reduce drawdown here** — every rule ~−20.9% DD (2022 hit both sleeves; diversification failed in that regime).
3. **Band vs calendar is second-order** (6.95 vs 6.91); the band's real benefit is **far fewer trades (2 vs 59)** → less cost/friction — not more return.

## Corrected guidance
- **Rebalancing is optional, not a return enhancer.** Where equities dominate, it lowers return.
- **If you rebalance for risk discipline, use a WIDE band (±10pt, ~1 trade/5y)** — negligible return difference, minimal trades.
- **Do not market rebalancing as free alpha.** Its value is behavioural/risk and **regime-dependent**; this window it gave neither return nor drawdown relief.

*Paper only. Not investment advice.*
