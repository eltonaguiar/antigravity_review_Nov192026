# Breakeven costs — cost at which each candidate net expectancy crosses zero

**Date:** 2026-11-23 · **Round:** ROUND_01_2026-11-23 · **Tool:** `CONTEST/tools/breakeven_costs.py` · every number below is printed by that script.
**Data:** real Yahoo Finance monthly adjusted close, 24 symbols, 120 months (10.0 years). Nothing is fabricated; the script exits non-zero if the universe cannot be built.

## Question

What per-round-trip trading cost sets net expectancy to zero for each candidate? Below that cost the candidate is net-positive; above it, net-negative. A candidate whose gross expectancy is already <= 0 has breakeven cost 0 bps: it is losing before any trading cost.

## Method

Breakeven cost per round trip (bps) = gross annual expectancy (bps) divided by round trips per year. Net expectancy = gross minus cost(bps) times round trips divided by 10000. Candidates:

1. SPY buy-and-hold — gross equity premium, near-zero turnover, breakeven not binding.
2. 12-1 momentum long-short quintile — full long and short reconstitution monthly, 12 round trips per year.
3. 12-1 momentum long-only top quintile — top quintile only, monthly reconstitution, 12 round trips per year.

## Results — breakeven cost per round trip

| candidate | gross %/yr | round trips/yr | breakeven bps/rt | net @1bp | net @5bp | net @10bp |
|---|---:|---:|---:|---:|---:|---:|
| SPY buy-and-hold | 13.642 | 0.5 | 2728.40 | 13.637 | 13.617 | 13.592 |
| 12-1 momentum long-short quintile | -0.623 | 12.0 | 0.00 | -0.743 | -1.223 | -1.823 |
| 12-1 momentum long-only top quintile | 30.038 | 12.0 | 250.32 | 29.918 | 29.438 | 28.838 |

## Reading

- **12-1 momentum long-short quintile:** gross is already negative (-0.623%/yr), so breakeven cost is 0 bps. It loses before any trading cost is applied.
- **12-1 momentum long-only top quintile:** gross 30.038%/yr; breakeven 250 bps per round trip. Even at 5 bp per round trip net expectancy is 29.44%/yr, so cost is not the binding constraint here.
- **SPY buy-and-hold:** gross 13.642%/yr; breakeven 2728 bps per round trip. With near-zero turnover this is not binding — buy-and-hold is cost-insensitive.

## Verdict

Breakeven cost separates the candidates that costs can kill from those they cannot. The long-short momentum candidate is already dead before costs (breakeven 0). The long-only momentum candidate and SPY buy-and-hold have breakeven costs far above realistic trading costs, so cost assumptions do not change their sign. Gross expectancy, not cost, is the binding constraint for these candidates.

*Paper only. No live orders, no credentials. Not investment advice.*
