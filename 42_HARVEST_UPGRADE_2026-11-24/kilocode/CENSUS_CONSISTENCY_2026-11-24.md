# 1000-cell census consistency check (2026-11-24T13:16Z)

Source: `findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw`
(`1000_TODOS.json`, `results/CENSUS_ROLLUP.json`, `results/cells/*.json`).

## Source-of-truth counts
- 1,000 cells; composite key `symbol_strategy_horizon` is **unique 1000/1000**.
- Status: **107 killed / 893 blocked_no_data / 0 open / 0 claimed**.
- Result artifacts: **966 files** → **34 cells have no artifact**.

## Missing artifacts (all `blocked_no_data`)
| Strategy | Missing |
|---|---|
| `rsi2_pullback` | 15 |
| `ma_cross` | 15 |
| `trend_pullback` | 4 |
Symbols: BTC 2, ETH 1, SOL 1, ADA 2, LINK 2, and 2 each for SPY/QQQ/IWM/AAPL/MSFT/NVDA/JPM/XLE/GLD/TLT/EURUSD/USDJPY/GBPUSD.
Every blocked cell should still emit a result JSON quoting the bar count
(the repo’s own convention); these 34 do not.

## Rollup contradicts the source
`results/CENSUS_ROLLUP.json` reports:
`{claimed: 3, measured_kill: 96, blocked: 861, insufficient: 40}` (sums to 1000).

`1000_TODOS.json` reports: `{killed: 107, blocked_no_data: 893}`.

Differences: 11 kills missing, 32 blocked re-bucketed, 3 “claimed” that no TODO
claims, 40 “insufficient” not present in the source statuses. The rollup has **no
cell array or digest**, so its classification cannot be recomputed — the same
unrecomputable-counter problem flagged earlier for 362/361.

## Recommendation
1. Regenerate `CENSUS_ROLLUP.json` **from** `1000_TODOS.json` (status counts and
   artifact presence), with a cell list + SHA-256 of the input.
2. Emit the 34 missing blocked artifacts (bar count + reason code) so the
   census is complete and auditable.
3. Add a CI check: `count(cells) == 1000`, `statuses ⊆ {killed, blocked_no_data}`,
   `artifacts == cells`, and rollup counts equal source counts.
