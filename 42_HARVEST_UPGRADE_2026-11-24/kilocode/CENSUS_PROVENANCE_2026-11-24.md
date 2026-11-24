# Census artifact provenance audit (2026-11-24T15:31Z)

Source: `results/cells/*.json` in the main worktree (966 files).

## Mixed runs
- **8 distinct `git_sha`** across 966 artifacts:
  `43833033…` 270, `0050bce0…` 269, `9ddb420c…` 220, `b9434122…` 120,
  `5396d13b…` 70, plus 3 smaller groups.
- `generated_at` spans **01:37:27 → 01:42:19Z** — the grid was produced by
  several processes/worktrees within five minutes. There is no manifest tying
  artifacts to one run.

## Schema defects
- **11 files are malformed** (missing required keys such as
  `symbol/strategy/horizon/bars/generated_at`). Examples:
  `DOGEUSDT_rsi2_pullback_1d.json`, `DOGEUSDT_ma_cross_1d.json`,
  `BTCUSDT_trend_pullback_1h.json` (missing `cell` and `verdict`).
- **One artifact has `verdict = null`**: `BTCUSDT_trend_pullback_1h.json`.
- **12 cells are `BLOCKED_NO_DATA` but have `bars > 0`** — all `gap_fade`
  (BTC 1w 53, SOL 1d 250, BTC 1h 2,161, BTC 1d 365, DOGE 1w 36, BTC 4h 541…).
  Blocked semantics say bars should be 0; either the classifier or the reason
  is wrong.

## Status drift
Artifacts: `{BLOCKED_NO_DATA: 859, KILLED: 96, INSUFFICIENT_TRADES: 10, null: 1}`.
`1000_TODOS.json`: `{blocked_no_data: 893, killed: 107}`. The artifact layer
therefore cannot be reconciled to the source without fixing the 11 malformed,
the 12 gap_fade, and the 10 INSUFFICIENT_TRADES/1 null discrepancies.

## Recommendation
1. Validate every artifact against the schema on write; reject malformed.
2. Write a per-run manifest (`run_id`, single `git_sha`, cell list, digest) and
   refuse mixed-sha directories.
3. Reclassify `gap_fade` (bars exist → not BLOCKED_NO_DATA) and the 10
   INSUFFICIENT_TRADES/1 null rows; then regenerate the rollup.
