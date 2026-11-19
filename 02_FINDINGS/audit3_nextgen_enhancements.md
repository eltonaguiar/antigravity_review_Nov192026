# audit3 — current-state review and next-gen enhancements (2026-11-19)

Reviewed the **live** implementation on `main` (post-PR #904/#905), not a spec:
`alpha_engine/audit3_tribunal.py` (65 KB), `audit3_selection_alpha.py`,
`audit3_denylist.py`, `tools/audit3_denylist_health.py`, and the current ledger
(`audit3_ledger.json` → 0 PROVEN / 1 CANDIDATE / 10 KILL).

---

## 1. What is already in place (verified in code)

| Fix | Where | Status |
|---|---|---|
| WR demoted to a descriptor; **net-expectancy CI (G2)** is the edge gate | `evaluate_cell` (G1/G2/G7 doc block; "WR stays a reported descriptor") | ✅ done |
| **Confirmatory / discovery namespace split**; BH per namespace | `load_confirmatory`, `_promote` (discovery can reach CANDIDATE, never PROVEN) | ✅ done |
| **Provenance**: commit SHA + file SHA-256 embedded | `_git_sha`, `_sha256` | ✅ done |
| **Measured slippage** adopted from `slippage_validation` (per-strategy where available) | `_apply_measured_costs` | ✅ done |
| **2×-slippage stress CI** reported | `nets_2x` / `stress_2x_ok` | ✅ done |
| **Forward-gate block wired** (PROVEN_T2 requires the pod's own forward rows closed on/after `registered_at`) | `forward_gate_block` + `_promote` | ✅ done |
| **Source-concentration cap enforced** (downgrade when `top_source_share > MAX_SOURCE_SHARE`) | line 1174 | ✅ done |
| Kill requires proven harm (net-CI<0 **and** BH harm q ≤ 0.10) | `apply_harm_gate` | ✅ done |
| DSR gate on CANDIDATE (demote if DSR < 0.50) | `_promote` | ✅ done |

The audit3 design is now genuinely strong; nothing below implies redoing any of this.

## 2. The single biggest practical blocker

**The forward ledger is empty (0 rows) because there is no ingestion adapter.**
`alpha_engine/forward_observations.py` states it "cannot read MySQL here". So:

- `reports/forward_observations.jsonl` = 0 rows, by design.
- `PROVEN_T2` is **unreachable from forward evidence** (nothing can promote).
- audit3's `0 PROVEN` verdicts are *correct*, but the promotion path is dead until rows
  accrue.

**Next-gen #0:** ship a MySQL ingestion adapter that appends resolved, intrabar-true,
benchmarked rows from the live ledger into `forward_observations`. This is the difference
between a definition and a pipeline. Everything else below is impossible until this exists.

## 3. Next-gen enhancements (ordered by leverage)

### E1. Wire selection-alpha as an enforced gate (not a sidecar)
- `selection_alpha: available=false` today — computed in `audit3_selection_alpha.py` but
  not reachable in the runner (needs the price tables).
- **Do:** give the runner a bars source (DB or cached OHLCV store) so per-class selection
  alpha (`alpha = pick net return − direction-adjusted buy & hold`) computes and becomes a
  first-class column + kill filter. An alpha that is positive only because the direction
  happened to be long in a rising market is not edge.

### E2. Random-entry / timing-null MC per cell
- `benchmark_closed_ledger.py` already does same-asset random-entry MC on the closed
  ledger; audit3 does **not** run it per cell.
- **Do:** add a per-cell "does this beat random entry at the same symbol/window?" MC leg
  (direction-aware nulls). Survivorship + trend-beta cells will fail it; genuine timing
  edge will survive. This is the single best guard against the "positive CI but it's just
  beta/trend" failure mode (cf. the candidate's short-beta caveat).

### E3. Benchmark-relative legs enforced, not just specced
- `BENCHMARK_GATES.md` defines excess-vs-matched-exposure; the forward rule already insists
  on `IR >= 0.5` / benchmark coverage. But no live benchmark series (SPY/BTC/AGG/GSG) is
  wired into the ledger rows.
- **Do:** materialize benchmark legs per class into `forward_observations`
  (`benchmark_leg_ret`), and make excess-vs-benchmark an enforced promotion input, not a
  descriptor.

### E4. Edge-decay / stability monitor (beyond split-half)
- Split-half is only two windows. A cell can be "stable" across two halves yet decay
  monotonically after.
- **Do:** add a rolling 4–8 weekly/monthly cohort-mean panel with a slope/consistency
  check, and a `DECAY` verdict that pre-empts a KILL before the CI flips (retire on
  *decay*, not only on proven harm).

### E5. Backtest-vs-forward reconciliation flag
- When a pod's forward CI diverges from its own OOS backtest (the H10 case), flag it
  explicitly.
- **Do:** add an `oos_vs_forward` delta panel per pod; auto-flag on divergence > threshold;
  never let "it worked in backtest" override a failing forward CI.

### E6. Global trial counter / effective-N surfaced consistently
- One cumulative `cumulative_trials` counter must feed DSR, Bonferroni, BH, and the
  emitter. (Prior review noted three disagreeing counters.)
- **Do:** print it on the audit3 page and in `build_report`; ensure the ledger, 
  `money_ready_verdict.py`, and the emitter read the same value.

### E7. Data-integrity gate feeding audit3 (bad rows can't poison cells)
- Cross-vendor price sanity (e.g. CADJPY 611.23), duplicate-emission dedup (67 dup
  groups), zombie `_auto_expired` rows.
- **Do:** a pre-filter in `load_rows` that drops/annotates these before cell evaluation;
  surface a `rows_excluded_by_integrity` count.

### E8. Multi-source requirement for promotion (single-emitter caveat)
- A single emitter can currently be PROVEN on the ledger (code note at line ~777). With
  `MAX_SOURCE_SHARE` enforced that is reduced, but a one-source CANDIDATE should never
  graduate.
- **Do:** require ≥2 independent sources (or a stated venue/fill difference) for any
  PROVEN_T2, matching the candidate demotion rationale.

### E9. Economic-prior / "who loses and why" gating at entry
- Add a required `economic_prior` and "who is on the other side" field to every pod before
  it is accepted into the confirmatory manifest. This is the anti-p-hacking guard the
  external review (EDGE_REVIEW_2026-11-19) calls the real bottleneck — cheap to add now.

### E10. Graduation dashboard (PROVEN_T2 → small-size production cap)
- Turn the verdict into a *state machine*: `PROVEN_T2 → 30/60/90-day forward review at ≤1%
  NAV/trade → full size`. This closes the "ratchet to zero" criticism — a winning pod gets
  a defined path to capital, not just a label.

## 4. Priority order

| Priority | Item | Why |
|---|---|---|
| P0 | **Forward-ledger ingestion adapter** (E0) | unlock promotion entirely |
| P1 | **Random-entry MC per cell** (E2) | kills the beta/trend false-positive class |
| P1 | **Selection-alpha enforced** (E1) | separates beta from skill |
| P2 | **Benchmark legs live** (E3) | required by the forward rule already |
| P2 | **Trial counter unified** (E6) | correctness of every multiplicity stat |
| P2 | **Data-integrity pre-filter** (E7) | protects cell verdicts |
| P3 | Decay monitor (E4), OOS-vs-forward (E5), multi-source promotion (E8), economic prior (E9), graduation dashboard (E10) | robustness + anti-ratchet |

*Not personalized investment advice.*
