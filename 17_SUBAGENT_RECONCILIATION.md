# 17 — Subagent reports reconciled (2026-11-19)

Every subagent report (strategy/hypothesis tracking, strategy catalog, statistical
methodology, per-asset-class research, pod registration, vanilla/lapis/witty-fight/
audit2 worktree reviews) was checked against the consolidated branch
(`audit3-consolidated`, PR #910).

## Resolved in the branch
- `observe` status defined; `_pod_for` accepts only `pre_registered` (test pins it).
- Real hypothesis ids `H-2026-11-19-01..05` filed; forward-obs FK passes.
- `trading/data/strategy_registry.json` materialized (17 strategies) from the pod
  manifest via `tools/seed_strategy_registry.py`.
- audit2 forward-evidence clock, trial budget, benchmark-leg table and 3× cost-gate
  note added (sidecar `audit_dashboard/data/audit2_forward.json`, built by
  `tools/audit2_forward_summary.py`, deployed with the page).
- N1–N4 + block bootstrap merged; persistence placed after the alpha gate; raw
  verdict stamping; legacy-row churn skip; atomic history write + seeded sidecar.
- Freeze gate + `audit3-health.yml` monitor added; peer-worktree snapshotter +
  first snapshot committed.

## Deferred (deliberate, needs its own reviewed change)
- Normalising the 141-entry hypothesis registry's 30+ status spellings and removing
  the duplicate archive tail.
- USDT→CRYPTO classification carve-out; `bt_backtest_runs.asset_class` source fix.
- Retiring `v2/index.html` (deploy decision).

## Not a defect
- `strategy_perf_by_class.json` small-n positives (n<30, PF 199) are already treated
  as traps; audit2 never headlines raw PF.
- Selection alpha is an optional sidecar; the ledger reports `available:false` and
  the gate only fires with data.

*Not investment advice.*
