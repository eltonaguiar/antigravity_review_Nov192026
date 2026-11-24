# HARVEST → /audit analyst bridge contract

The live `/audit` payload has `analyst_leaderboard = {total_analysts: 0, total_predictions: 0, leaderboard: []}`
and `analyst_active_calls = {total_active: 0, active_calls: []}` while HARVEST covers 71 symbols.
This is the contract for filling those objects without inventing firm/person attribution.

## Source of truth
`docs/data/harvest_signals.json` (HARVEST), which already carries
`source, published_at, rule, cost_bps, benchmark, analysts, buy_side_pct, consensus, consensus_score, direction`.

## Target shapes (dashboard_data.json)
```
analyst_active_calls = {updated_at, total_active, active_calls: [call, ...]}
analyst_leaderboard  = {updated_at, total_analysts, total_predictions, leaderboard: [entry, ...]}
```

## active_calls entry
| field | value |
|---|---|
| symbol | ticker |
| entity_type | `"sell_side_consensus"` (no person/firm name exists in the free feed) |
| firm | `null` — never infer a firm from a consensus |
| direction | LONG for STRONG_BUY/BUY, NEUTRAL for HOLD, SHORT for SELL/STRONG_SELL |
| consensus | label |
| consensus_score | derived score |
| buy_side_pct | share |
| analysts | count |
| period | snapshot month |
| source | `finnhub:/stock/recommendation` |
| published_at | period + `T00:00:00Z` |
| rule | `two_condition_v1_<hash>` |
| cost_bps | 6.7122 |
| benchmark | `SPY` |

Unique key: `(symbol, period, source)`.

## leaderboard entry
Because no per-firm actions are available free, publish **one aggregate row** and say so:
`{name: "SELL_SIDE_CONSENSUS", entity_type: "aggregate", n_symbols: 71, n_observations: 71,
 avg_buy_side_pct, pct_strong_buy, pct_hold, pct_sell, improved, deteriorated, last_period,
 source, rule}`. Do **not** fabricate firm names or hit rates.

## Totals
- `total_predictions` = number of consensus rows = 71 (one per symbol this run).
- `total_analysts` = sum of `analysts` across rows (covering-analyst instances, not unique people).
- `updated_at` = max `published_at` / generated timestamp.

## Freshness and rejection
Reject the bridge if `max(published_at)` is older than 45 days, any row lacks
`source|published_at|rule|cost_bps|benchmark`, or `total_analysts <= 0`.

## Validation
`python3 build_audit_analyst_bridge.py` emits `docs/data/audit_analyst_bridge.json`
and prints the totals; a join test asserts totals > 0 and that every active_call
has the five provenance fields.
