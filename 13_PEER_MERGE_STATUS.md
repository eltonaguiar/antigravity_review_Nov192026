# Peer merge status — all four worktrees + forward-branch implementations (Kilo)

**Date:** 2026-11-19 · **Reviewer:** Kilo, `universal-pisces`
**Purpose:** record what each peer produced, what I merged into my deliverables,
and what is now **implemented in code** vs still open. This is the consolidated
view the user asked for ("review all peers, merge value into mine").

---

## 1. The four worktrees (state at review time)

All four were checked out at source `main` tip (`f9e6c8202a1`), clean (0
uncommitted). The *substantive* peer work lives in:

- the shared review repo `eltonaguiar/antigravity_review_Nov192026`
  (`01–05` peer set + `05_KILO_REVIEW`), and
- **feature branches** in the source repo that implement the forward-evidence
  machinery (commits below).

| Worktree / branch | What it contributed | Where absorbed |
|---|---|---|
| `universal-pisces` (mine) | corroboration, fresh tracking gaps, peer reviews, audit2 spec, audit3 next-gen | `06/07/08/09/10/11/12` |
| `witty-fight` (`review-investment-strategy-audits`) | audit2/audit3 page review, v2-orphan finding, swarm-history reconstruction | reviewed in `07/10` |
| `lapis-chronometer` (`lapis-chronometer`) | F1–F7 root causes, evidence index, plan, A/B harness | reviewed in `07/08` |
| `vanilla-handsaw` (`add-strategy-variable-tracking`) | variable-tracking branch (empty of real work at review time) | noted in `08` |
| **forward feature branches** (all worktrees' HEAD sits on them) | **implemented** forward-evidence contract, promote-gate, net-of-cost, kill-list reconcile | merged now (this doc + `12` addendum) |

---

## 2. What peers implemented that I had recommended

| My recommendation | Peer implementation | Commit | Verified |
|---|---|---|---|
| E4: forward-observation clock / contract | `alpha_engine/forward_observations.py` — schema, net-return def, promotion rule (n≥100, net PF CI-LB>1.0 or IR≥0.5, intrabar first-touch 100%, benchmark coverage ≥90%), clock ETA from observed rate | `feat/forward-observations-contract` `2ae0573` | ✅ code present |
| E4: wire forward gate into PROVEN_T2 | `_promote()` demotes PROVEN_T2→CANDIDATE unless the pod's own forward rows clear; failing clause written into reasons | `feat/forward-gate-and-ingest` `5c0c42d` | ✅ test `test_audit3_forward_gate.py` |
| E1: selection alpha as scheduled measurement | per-class selection alpha now generated (`reports/selection_alpha_2026-11-19.json`); no class shows skill after costs, all CIs include 0; stale credential read fixed | same `5c0c42d` | ✅ `covered 2475` |
| Cost honesty: net-of-cost instead of gross | `forward-lane-net-of-cost`: FOREX gross PF 1.102→net 1.035; COMMODITY 1.048→1.005; promotion gates read `net_pf` | `feat/forward-lane-net-of-cost` `a7df4ff` | ✅ validated on live cohort |
| Kill-list reconciliation (F7/contradictions) | label H-119 vintage, retire stale n-gate date, publish kill-list union with provenance | `fix/h119-vintage-and-kill-list-reconcile` `8da1bf3` | ✅ |

**These close four of my five audit3 next-gen gaps.** The forward ledger is
committed empty/intentionally seeded (430 rows for H-119 via idempotent ingest);
PROVEN_T2 stays unreachable for a measured reason (H-119: net PF CI-LB 0.9213 ≤
1.0, IR 0.043, benchmark coverage 79.8%) — exactly the honest behaviour I wanted.

---

## 3. Still open (my remaining recommendations)

| Item | Status |
|---|---|
| E2: score the whole book / full-book reconciled companion ledger (21.4% → >90%) | **open** |
| E5: promote the 2×-cost stress from report-only to a hard gate for PROVEN_T2/CANDIDATE | **open** |
| E3: per-cell `required_n` from the power function (`audit3_edge_hunt.py:161`) | **open** (contract sets n≥100 but not effect-size power per cell) |
| Denylist staleness → loud alert (not just fail-open) | **open** |

---

## 4. What I merged into my deliverables

- `07/08` — peer reviews of the shared `01–05` set and the audit3 source code.
- `09` — audit2 content recommendation from the `.MD` sweep.
- `10` — next-wave peer review (incl. stop-fill overshoot mean/median nuance).
- `11` — **consolidated audit2 spec** (merge of peer `05` + my `09` + this wave).
- `12` — audit3 review + next-gen enhancements (now updated to mark E1/E4 and
  net-of-cost as implemented — see addendum below).

Nothing was overwritten; all additions are new files in `06_…13_`.

---

## 5. Bottom line

All four peers converge on the same verdict (no positive selection alpha; 0
PROVEN; fix = stops-the-bleed + forward measurement). The most valuable peer work
this wave is the **implemented forward-evidence contract + promote-gate** — it
turns audit3 from a museum into a certification engine and directly answers the
user's "switch variables and see" ask. Remaining code gaps are E2 (full-book
coverage), E5 (2×-cost as a gate), E3 (per-cell power), and denylist staleness
alerting.

*Not investment advice.*
