# audit3 — code-level review + next-gen enhancements/fixes (Kilo, `universal-pisces`)

**Date:** 2026-11-19 · **Reviewer:** Kilo, `universal-pisces`
**Scope:** review of the audit3 implementation (code, not just ledger) with
concrete, code-grounded fix/enhancement recommendations. Line references are to
`alpha_engine/` and `.github/workflows/` in the source repo.

---

## 1. What I reviewed (code-verified)

| Component | File | Status |
|---|---|---|
| Tribunal / ledger | `alpha_engine/audit3_tribunal.py` (1,311 lines) | mature, expectancy-primary |
| Edge hunt (alpha vs beta, PIT) | `alpha_engine/audit3_edge_hunt.py` (553) | great science, separate manual CLI |
| Selection alpha (M1b) | `alpha_engine/audit3_selection_alpha.py` (245) | **optional** in workflow; needs MySQL price tables |
| Denylist enforcement | `alpha_engine/audit3_denylist.py` (271) | wired, fail-open, health-asserted |
| Evidence registry | `alpha_engine/audit3_evidence.py` (830) | backtest/evidence ingestion |
| Scheduled pipeline | `.github/workflows/audit3-ledger.yml` | 6-hourly cron; selection-alpha optional |

Strengths confirmed in code: hash-verified canonical sidecar reconciliation
(`tribunal.py:368–435`), measured-cost application (`_apply_measured_costs`),
DSR/PBO/BH/split-half, 2×-cost stress column, provenance (git SHA + input
SHA-256), denylist health gate.

---

## 2. The five highest-value next-gen enhancements

### E1. Make selection alpha a required gate, not an optional step (fix the biggest hole)
- **Now:** `audit3_selection_alpha.py` runs only under an "optional — needs the
  price tables" step (`audit3-ledger.yml:78–91`); the ledger verdicts do not
  consume it. So a cell can be positive-expectancy yet still be beta, not skill.
- **Fix:** fold alpha (pick net − direction-adjusted hold) into `evaluate_cell`
  as a required column and a hard gate for PROVEN_T2. When price tables are
  unavailable, **fall back to the random-entry timing null** from
  `alpha_engine/benchmark_closed_ledger.py` (same-asset, direction-aware) instead
  of skipping. Never let a cell promote without an alpha-vs-hold figure.
- **Why:** this is the literal "did we beat holding" test the user asked about;
  audit3 currently can't answer it on its own.

### E2. Score the whole book — add a full-book reconciled companion ledger
- **Now:** audit3 scores the export slice (3,500 / 16,330 = 21.4%). The 7,502
  integrity-excluded and 9,100 auto-expired cohorts are never scored, which biases
  the retained slice optimistic.
- **Fix:** produce a second `audit3_fullbook_ledger.json` that scores **all**
  resolvable rows, tagging integrity-excluded / auto-expired rows with a flag so
  they are counted and reported, not discarded. State both denominators on the
  page. This converts "21.4%" from a coverage excuse into a full population view.

### E3. Wire the existing power function into per-cell output
- **Now:** `audit3_edge_hunt.py:161` already defines `required_n(effect, sd, z)`
  — but it is used only in the ad-hoc battery, not surfaced per cell.
- **Fix:** have the tribunal emit `required_n_for_gate` per cell so "n≥100" is
  replaced by a **power-based target n** (effect size from the cell, sd from its
  rows, 2× cost). Also expose `power` / `MDE` per cell in the ledger + UI. This
  makes "how many forward rows before we can know" an honest, computed number.

### E4. Add a forward-observation clock (the single biggest missing item)
- **Now:** there is no forward table. PROVEN_T2 cannot accrue because nothing
  records a hypothesis's future resolutions over time.
- **Fix:** add a `forward_observations` table and a scheduled shadow pilot that
  emits the candidate pods (from the audit2 spec) as **paper** legs and returns
  their resolutions to the next ledger build. This is what turns audit3 from a
  static falsifier into a certification engine.
- **Coordinate with:** `05_AUDIT2_SPEC.md` pods P1–P8; keep every cell, including
  KILL cells, emitting shadow controls so the forward ledger accrues negatives.

### E5. Promote the 2×-cost stress from "report-only" to a gate
- **Now:** `net_ci_pct_2x` / `stress_2x_ok` are computed and displayed but
  report-only (`tribunal.py:715`).
- **Fix:** make `stress_2x_ok == True` a **required** condition for PROVEN_T2
  (and for CANDIDATE promotion). This is the cheapest robustness win and closes
  the "single flat slippage constant" criticism.

---

## 3. Smaller fixes (targeted)

| # | Fix | Where | Why |
|---|---|---|---|
| F1 | Denylist staleness must **alert**, not just fail-open | `audit3_denylist.py` + health job | A stale (>14d) ledger currently silently disables the gate; add a loud CI-fail/notification, keep fail-open for scans |
| F2 | Log `denied_reason()` hits | `feed_hygiene.py:194`, `forward_validator.py:763` | We need a post-merge record of what the denylist actually blocked, to verify it works (one-week shadow review) |
| F3 | Never emit a `/tmp` path in the ledger | `build_report` / `load_rows` | Replace `source: /tmp/audit3/dashboard_data.json` with the committed canonical path + SHA (provenance already has SHA; pin the path) |
| F4 | Reconcile `bt_backtest_runs.asset_class` mislabel at the source | `audit3_evidence.py` inference | Evidence registry infers symbol→class correctly but the source table still says CRYPTO for `NZDUSD=X`; fix the source row, don't just patch the view |
| F5 | Single bootstrap engine | `tribunal.py` vs `benchmark_closed_ledger.py` | Two bootstrap implementations exist; unify so CIs are consistent across surfaces |
| F6 | Confirmation of pre-registration should hard-fail, not flag | `load_confirmatory` / `_pod_for` | A discovery namespace cell must never reach PROVEN_T2; make it a hard rule with a test |

---

## 4. Next-gen architecture (target state)

```
daily/hourly
   emit shadow pods (forward_observations)
        │
        ▼
audit3-ledger.yml (6-hourly)
   load canonical resolved view (hash-verified)
   evaluate_cell ──► net expectancy CI + alpha-vs-hold + 2x gate + required_n
   full-book reconciled view (integrity-tagged)
   denylist rebuild + health assert + hit-log
        │
        ▼
/audit3 page (live) + forward_observations feed-back
```

---

## 5. Evidence index

| Claim | Source |
|---|---|
| Selection alpha optional in workflow | `.github/workflows/audit3-ledger.yml:78–91` |
| 2×-cost report-only | `alpha_engine/audit3_tribunal.py:715` |
| Power function exists but not per-cell | `alpha_engine/audit3_edge_hunt.py:161` |
| Canonical sidecar reconciliation | `alpha_engine/audit3_tribunal.py:368–435` |
| Denylist wiring + fail-open | `alpha_engine/audit3_denylist.py`; `feed_hygiene.py:194`; `forward_validator.py:763` |
| Coverage 21.4% / integrity cohorts | `audit_dashboard/data/audit3_ledger.json` → `coverage` |

---

## 6. Bottom line

audit3 is already the correct statistical core. The leap to "next-gen" is not a
new page — it is **making the code close its own loops**: selection alpha as a
gate, full-book coverage, power-based target-n, a forward-observation clock, and
promoting the 2×-cost stress to a blocker. E1, E4, and E5 are the three highest
leverage items.

*Not investment advice.*
