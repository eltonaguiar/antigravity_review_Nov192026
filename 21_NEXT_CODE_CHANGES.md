# 21 — Queued code changes with precise diffs (2026-11-19)

Verified against `main` and `rescue/coms-handoff-2026-11-19`.

## 1. DSR must use the global trial count (P0-5) — one line

`alpha_engine/audit3_tribunal.py`, in `build_report`, ~line 1362.

- main:   `n_trials = sum(1 for g in strat_groups.values() if len(g) >= WR_MIN_N)`
- rescue: `n_trials = len(strat_groups)`

Why: DSR's `SR0` is the expected maximum Sharpe across **all** configurations
tried, not just those that cleared the reporting floor. Using tested-only cells
understates the multiple-testing correction (the review's P0-5: "DSR n_trials =
global N (658), not tested cells (45)").

Effect: DSR falls (stricter), which can demote PROVEN_T2/CANDIDATE cells. That is
the intended direction. Test after applying:

```bash
python3 -m pytest tests/test_audit3_tribunal.py tests/test_audit3_expectancy_gates.py -q
# then rebuild the ledger and diff verdicts:
python3 -m alpha_engine.audit3_tribunal --picks /tmp/audit3/dashboard_data.json \
  --out /tmp/audit3/ledger_dsr.json
```

## 2. G9 selection-alpha gate — reconcile, do not duplicate

Main already demotes a PROVEN_T2 cell to CANDIDATE when its class
`alpha_ci[0] <= 0` (the June post-pass in `build_report`). The rescue branch adds
a `beta_dominant` G9 variant. Keep main's implementation and, if desired, adopt
only the `beta_dominant` *reason label* so the ledger names the clause.

## 3. H-144 POSITION pod wiring (rescue commit 38691c3)

Wires `H-144 position_timeframe_selection` into
`alpha_engine/forward_observations_ingest.py` with the strategy-keyed condition
(`H-BABY-EQUITY-VT-PATTERN-SWEEP-001` / POD-EQUITY-BREAKOUT). Take as-is if
`forward_observations_ingest.py` on main is unchanged; otherwise re-port.

## 4. Pre-existing CI red (not ours)

`CI Tests` on `main` has been red since 06:11 (before the 08:50 consolidation):
`test_feed_hygiene_*`, `test_polymarket_volume_filter`,
`test_prediction_market_shadow_pin`, `test_tier2_hero_cards`. Investigate with:

```bash
gh run list -R eltonaguiar/findtorontoevents_antigravity.ca --workflow="CI Tests" --limit 10
gh run view <id> -R ... --log-failed | grep -E "FAILED|short test summary"
```
Suspect: the audit3 denylist wiring in `feed_hygiene.is_valid_active_pick`
(direction-aware cell kills could be rejecting fixtures the tests expect to pass).
If confirmed, the fix is to scope the denylist to picks that carry a KQ/strategy
identity, not every synthetic test fixture.

*Not investment advice.*
