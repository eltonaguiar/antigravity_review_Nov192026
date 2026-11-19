# audit2 + audit3 review — implementation reference & justification

**Author:** kilo (vanilla-handsaw worktree)
**Branch:** `add-strategy-variable-tracking`
**Date:** 2026-11-19
**Handoff:** `COMS_AUDIT2_3_HANDOFF_2026-11-19.md`
**Fix doc:** `updates/2026-11-19-audit3-tribunal-f1f2-n1-n2-n3-n4-n5-n7.md`
**audit3 review of record:** `docs/AUDIT3_REVIEW_2026-11-19.md`
**audit2 prototype source:** `witty-fight/COMS/HANDOVER.md` §05/§06 (`antigravity_review_Nov192026`)


This document is the "why" behind the branch. It explains every change, how it
is implemented, the statistical or operational justification, and the live
evidence that motivated it, for both the audit3 tribunal and the audit2
candidate library. It is written so the next agent can review, merge, or push
back on any single item without re-deriving the reasoning.

---

## 0. Ground truth measured from the live surfaces

Fetched from live pages on 2026-11-19 (not recalled):

| Surface | Observed state |
|---|---|
| `findtorontoevents.ca/audit` | 1.4 MB unified dashboard; classes/summary cards |
| `findtorontoevents.ca/audit2` | 6.8 KB static candidate/methodology library; loads `audit3_ledger.json` |
| `findtorontoevents.ca/audit3` | Quant Kill Tribunal; 41 KB; loads `audit3_ledger.json` + `audit3_evidence.json` |
| `audit3_ledger.json` | generated 2026-11-19T13:02Z |
| `audit3_evidence.json` | generated 2026-11-19T05:07Z |

### audit3 ledger key numbers (live)

| Signal | Value | Meaning |
|---|---|---|
| `n_rows` | 8,605 | canonical rows scored |
| `n_cells_tested` | 67 | cells judged |
| `n_proven` / `n_candidate` | **0 / 0** | the tribunal can never promote |
| `n_weak` / `n_kill` / `n_insufficient` | 59 / 8 / 292 | |
| `n_kill_classes` / `n_kill_symbols` | 3 / 10 | |
| `persistence.n_promoted_this_run` | 1 | one cell crossed the gate this run |
| `forward_gate.pods.POD-EQUITY-BREAKOUT.n_forward` | 0 | only pod, zero forward rows |
| `forward_gate.hypotheses.H-119.n_forward` | 430 | 430 forward rows outside the pod mapping |
| `coverage.scored_rows` vs `valid_closed_picks` | 8,605 vs 8,175 | **scored share 105.26%** — denominator contradiction |
| excluded cohorts | `integrity_excluded` 5,935 + `auto_expired` 9,110 | 46% of book dropped before scoring |

### audit2 live defects

1. **Pod registry is a static snapshot.** The page footer states: *"the pod
   registry is a static snapshot dated 2026-11-19 because `reports/` is not
   web-served."* The forward-evidence clock wants `reports/forward_observations.jsonl`
   but that path is not published, so `/audit2` cannot show live forward rows —
   the very thing a candidate library must show.
2. **`required_n` is circular.** The verdicts table renders `required_n` from
   the ledger's per-class `required_n`, which is computed from the **observed**
   cell mean (`required_n(effect_pct=mean, sd)` in `audit3_edge_hunt.py:161`).
   Plugging an observed near-zero mean inflates `n` to infinity and a lucky mean
   collapses it — the circular trap.
3. **Pod ↔ hypothesis mapping gap.** `POD-EQUITY-BREAKOUT` is
   `pre_registered` but has 0 forward rows, while `H-119` carries 430 forward
   rows that the pod gate cannot see. The clock cannot promote anything.

---

## 1. Doctrine

- **innocent-until-proven-guilty**: prior evidence is registered, never deleted;
  only the tribunal retires a cell, and only on proven harm.
- **Gates fail closed**: a gate that cannot be shown to kill a bad claim is not a
  gate. New rules only *tighten when a claim is granted*; they never demote an
  existing `KILL`/`WEAK`.
- **Every change is backward-compatible**: defaults preserve the old path; a
  caller that does not opt in cannot silently change a verdict.

---

## 2. audit3 changes (this branch, `add-strategy-variable-tracking`)

### 2.1 F1 — block (moving-block) bootstrap

- **Problem.** `bootstrap_mean_ci` resampled trades i.i.d. Picks overlap in time
  and share symbols, so the effective N is smaller than `n` and the CI is too
  tight. A too-tight CI inflates `PROVEN_T2`/`CANDIDATE`.
- **Implementation.** `_circular_blocks(rng, n, block_len)` +
  `bootstrap_mean_ci(..., block=False)` with `block_len = max(1, int(sqrt(n)))`;
  `evaluate_cell` passes `block=True` for the G2 net CI and the 2× cost stress.
  Default stays i.i.d.
- **Justification.** Moving-block bootstrap preserves temporal autocorrelation and
  widens the CI for overlapping positions — the honest interval.
- **Why.** The only positive clusters (`elite_grade B CRYPTO`, `grade A CRYPTO`)
  must be re-expressed before nomination; block resampling prevents over-stating
  their CIs.
- **Verification.** `test_block_bootstrap_widens_clustered_ci`.

### 2.2 F2 — split-half materiality floor

- **Problem.** `split_half_ok` required only `mean > 0`; a +0.001% half counted as
  stable.
- **Implementation.** `split_half_ok(values, min_mean=0.0)`; `evaluate_cell` passes
  the per-cell materiality floor (N4). Default 0.0 preserves other callers.
- **Justification.** "Positive" ≠ "material"; stability must be at a size worth
  risking capital.
- **Why.** Closes the "WR 59% / PF 0.94" pathology — a cell cannot look stable on
  a sub-cost-sized half.

### 2.3 N1 — repeated-looks / persistence gate (G8)

- **Problem.** BH FDR is per-run but the ledger is re-scored every ~6h, so a cell
  crossing `q ≤ 0.10` once will eventually do so by chance.
- **Implementation.** `PERSISTENCE_RUNS = 2`; `cell_key`/`load_history`/
  `save_history`/`apply_persistence_gate`; `first_pass_at` records the run that
  began the streak; CLI `--history`/`--history-write`; workflow commits
  `audit3_verdict_history.json`.
- **Justification.** Standard repeated-looks correction; grant depends on the
  streak, not a lucky draw.
- **Why.** Live `n_promoted_this_run = 1` while `n_candidate = 0` — exactly the
  case the gate exists for: hold back until it crosses again.

### 2.4 N2 — verdict-churn monitor

- **Problem.** Nothing tracked cells flipping verdicts between runs; noisy judge
  looks like a changing edge.
- **Implementation.** `raw_verdict` stamped before the persistence hold;
  `load_prev_verdicts`/`compute_verdict_churn` (alert at ≥20 tracked, >30%
  churn); CLI `--prev-ledger`/`--max-churn` exits 3 fail-closed before writing;
  workflow passes `--max-churn 0.30`.
- **Justification.** Churn = measurement noise; failing the run prevents a
  churning ledger being published.
- **Why.** Live `verdict_churn` is quiet (0 flips / 438 tracked); wired so the
  first gate behaviour change (e.g. G9) is measured, not trusted.

### 2.5 N3 — recency / regime gate

- **Problem.** `PROVEN_T2` had no requirement the edge still be present in the
  recent window.
- **Implementation.** `recency_ok(rows, nets, fraction=0.25, min_trades=5)` — the
  trailing `max(5, round(25%·n))` closes must have non-negative net mean (sorted
  by `closed_at`/`timestamp`); `PROVEN_T2` capped at `CANDIDATE` on stale regime.
- **Justification.** Regime-dependent edges are not portable; promotion requires
  the edge to be alive now.
- **Why.** Symmetric protection to the window-bias note (a recent-drawdown window
  can spuriously kill longs; recency stops a stale edge promoting).

### 2.6 N4 — cost-scaled materiality floor

- **Problem.** `PROVEN_MIN_NET_CI_LO_PCT = 0.05` (5 bp) is inside the noise for
  CRYPTO (15 bp cost).
- **Implementation.** `MATERIALITY_COST_FRACTION = 0.5`;
  `materiality_floor(mean_cost_pct) = max(0.05, 0.5·cost)`; applied to split-half
  and the `PROVEN_T2` CI lower bound; per-cell `mean_cost_pct`/`materiality_floor_pct`.
- **Justification.** Materiality must scale with the cost model actually applied.
- **Why.** Live costs vary 5× (`CRYPTO 0.0996` vs `FOREX 0.02`); a flat floor is
  wrong for 5 of 10 classes.

### 2.7 N5 — hold-time-normalised selection alpha

- **Problem.** `audit3_selection_alpha.py` equated a 1-hour and a 30-day pick.
- **Implementation.** `MIN_HOLD_DAYS_FOR_HEADLINE = 1.0`, `ANNUALIZATION_DAYS = 365`,
  `MIN_HOLD_DAYS_FLOOR = 1/24`; new fields `hold_days_mean/median`,
  `alpha_per_day_pct`, `alpha_annualized_pct`, `min_hold_days`, `n_min_hold`,
  `min_hold_participation`, `alpha_pct_min_hold`. `alpha_pct` unchanged.
- **Justification.** Selection alpha is a rate; per-day/annual + participation
  makes headlines comparable across holding periods.
- **Why.** The live `selection_alpha` block is the evidence behind the "crypto
  longs destroy value" conclusion; without normalisation a high-turnover strategy
  is misjudged against buy-and-hold.

### 2.8 N7 — strategy-generation freeze gate

- **Problem.** "No new strategy while a P0 item is open" existed only as prose.
- **Implementation.** `reports/strategy_freeze.json` (frozen, P0=E11/E13/E14) +
  `tools/strategy_freeze_gate.py` (exit 1/0/2); enforced as the first step of
  `forward-test-new-strategies.yml`.
- **Justification.** You cannot measure a system while changing it; the freeze is
  the one sentence every reviewer agreed on.
- **Why.** New strategies add trials without adding evidence while P0 holes are
  open.
- **Verification.** `tests/test_strategy_freeze_gate.py` — 4 passed.

**audit3 test state:** `tests/test_audit3_tribunal.py` 34 + `tests/test_audit3_selection_alpha.py` 11 + freeze 4 = **86 passed**.

---

## 3. audit2 changes (suggested — not yet on this branch)

The audit2 surface is not in this worktree's `audit_dashboard/` (only
`audit3.html` exists; `score_audit2.py` is a diagnostic). The prototype lives in
`witty-fight/COMS/HANDOVER.md` §05/§06 (`antigravity_review_Nov192026`). This
branch's relevance to audit2 is *what the tribunal now emits for it to consume*
plus three fixes audit2 itself needs:

1. **Serve `reports/forward_observations.jsonl`** (or a generated web copy) so the
   forward-evidence clock is live, not a static snapshot. This is the P0 for
   audit2. *Suggested implementation:* add the file to the `audit3-ledger.yml`
   commit + deploy glob — aligned with `POD-EQUITY-BREAKOUT` having 0 forward rows
   while `H-119` holds 430.
2. **De-circularise `required_n`.** Switch audit2's `required_n` column to a
   pre-declared MDE (`required_n_mde` from `audit3_edge_hunt.py`), not the
   observed mean. This is exactly the fix already in `lapis-chronometer`'s
   uncommitted `power_analysis`. Land it together with the audit3 power block.
3. **Reconcile the pod ↔ hypothesis mapping** so a pod with rows can be seen by
   the clock (`POD-EQUITY-BREAKOUT` ↔ `H-BABY-EQUITY-VT-PATTERN-SWEEP-001` ↔
   `H-119`). Assert in CI; fail closed on a pod with 0 rows while its hypothesis
   has rows.

**audit2 test state:** no committed tests; the three fixes above each need a
fail-closed test (feed a null/empty forward set → page must state "0 eligible",
not silently pass).

---

## 4. Live-data defects this branch exposes (for the next agent)

1. **Coverage denominator contradiction.** `scored_rows 8,605` vs
   `valid_closed_picks 8,175` → 105.26%. Canonical view and "valid" count differ
   by 430 rows. Reconcile before publishing any coverage %.
2. **Pod/hypothesis mapping gap.** 0 forward rows under the only pod vs 430 under
   `H-119`.
3. **Excluded-cohort bias (N6).** 5,935 integrity-excluded + 9,110 auto-expired
   dropped before scoring; only aggregate reason labels survive.
4. **Provenance leaks a build path.** `source: /tmp/audit3/dashboard_data.json`
   — embed commit SHA + input SHA-256 + generator version.

---

## 5. Merge / deployment sequence

1. **Land this branch's gates** (F1/F2/N1–N5/N7) — backward-compatible, 86 tests
   pass.
2. **Land `lapis-chronometer` G9 + `power_analysis`** (2× slippage demotes
   `PROVEN_T2`→`CANDIDATE`, `CANDIDATE`→`WEAK`) — depends on F1's 2× CI; land
   after F1 to avoid a conflict on `bootstrap_mean_ci`.
3. **Close the measurement holes** (N6 coverage reconciliation, pod mapping,
   E11/E13/E14 stubs) under the N7 freeze.
4. **Serve the forward-observations payload** to make audit2's clock live.
5. **Do not merge `audit2-page-*` branches yet** — all three sit at the same data
   tip with no unique code; they are purpose labels, not implementations. Build
   audit2 from the `HANDOVER.md` prototype.
6. **Keep N7 wired.** Unfreeze only when E11/E13/E14 have deterministic tests.

---

## 6. What would make me push back

- Any change that weakens a gate's default without a fail-closed test.
- Any change that demotes a `KILL`/`WEAK` verdict (doctrine).
- Publishing a coverage percentage from the contradictory denominator.
- Registering a second premium pod before E11/E13/E14 close.

---

## 7. File map

**Code (modified, uncommitted in this worktree):**
- `alpha_engine/audit3_tribunal.py` — F1/F2/N1–N4.
- `alpha_engine/audit3_selection_alpha.py` — N5.
- `tests/test_audit3_tribunal.py`, `tests/test_audit3_selection_alpha.py`,
  `tests/test_strategy_freeze_gate.py`.
- `.github/workflows/audit3-ledger.yml` — N1 history + N2 prev-ledger/churn.
- `.github/workflows/forward-test-new-strategies.yml` — N7 freeze step.
- `tools/strategy_freeze_gate.py`, `reports/strategy_freeze.json` — N7.

**Docs:**
- `docs/AUDIT3_REVIEW_2026-11-19.md`, `docs/FUND_MANAGER_QUICK_VIABLE_PLAN_2026-11-19.md`,
  `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md`.
- `updates/2026-11-19-audit3-tribunal-f1f2-n1-n2-n3-n4-n5-n7.md`.
- `COMS_AUDIT2_3_HANDOFF_2026-11-19.md` (handoff message).

**Not mine (do not push):** all `[skip ci]` auto-update commits from other agents
and CI on this branch's history.
