# Peer Review — of the shared review (`01–05`) by Kilo (worktree `universal-pisces`)

**Date:** 2026-11-19 · **Reviewer:** Kilo, `universal-pisces`.
**Scope:** this reviews the collective review artifacts in this repo:
`01_INVENTORY/`, `02_FINDINGS/`, `03_VARIABLES/`, `04_RECOMMENDATIONS/` (peer agent)
and `05_KILO_REVIEW/` (lapis-chronometer).
**Method:** every numeric claim below was **re-verified against the live source
repo** (head `f9e6c8202a1`) before it was used — not taken on trust.

---

## What I verified independently (and it checks out)

| Peer claim | My re-check | Verdict |
|---|---|---|
| Whole book net −0.188%/trade; CRYPTO LONG −0.442%/pick vs hold | `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` lines 17, 70 | ✅ |
| ETF 234% slippage of per-trade PnL | `AUDIT_SURFACE_REVIEW…md` line 76 | ✅ |
| ETF surface contradiction: 1.9% WR/PF 0.02 (n=52) vs 43.1%/0.98 (n=584) | surface-review line 55 | ✅ (with caveat, see below) |
| audit3 scores 3,500/16,330 (21.4%); 7,502 integrity-excluded; 9,100 auto-expired | surface-review lines 21–26 | ✅ |
| Leaky walk-forward gate: at-issue stamps on 215/3,500 (6%) | edge-hunt line 51 | ✅ |
| Hypothesis registry: 99 entries, 28 status spellings | `reports/hypothesis_registry.json` (len=99; Counter=28) | ✅ |
| Schema: 409 tables, 110 empty, `portfolio_snapshots` frozen Mar, `at_local_picks` ~76M | `docs/FINANCE_DB_SCHEMA_SPEC.md` lines 26, 106, 111, 156, 158 | ✅ |
| ML-health "healthy consensus" is backtest walk-forward lift, not realized beta-separated alpha | `docs/ML_SYSTEMS_HEALTH_AUDIT_2026-11-19.md` lines 23, 33 | ✅ |

The reference numbers in the shared review are accurate. It is not a numbers
review I am disputing.

---

## What I agree with

1. **The headline is correct and important:** there is no positive selection alpha in
   the measured ledger; 0 PROVEN, 1 CANDIDATE, 10 KILL (2 kill classes). This is the
   honest answer to "why no solid wins."
2. **The denominator honesty fix is the single most valuable framing.** Publishing
   "3,500 of 16,330 closed picks (21.4%)" on every render kills the inflated-WR
   problem at the root.
3. **The exit-geometry/cost diagnosis** (fixed TP/SL cuts winners short; ETF/forex
   cost artefacts) is the right explanation for "high WR but no profit" and is well
   evidenced.
4. **The leaky walk-forward gate** (rear-view mirror) is a subtle, correct catch that
   most outsiders would miss. The proposed P0-1 fix (stamp `at_issue_*` at
   creation) is the correct remedy.
5. **Fragmented tracking** (no single source of truth; 6+ registries; declared-but-
   missing files) matches my independent finding.
6. **The recommendation to stop generating new strategies and instead stop the bleed +
   build forward measurement** is the right strategic call, and the tunable-variable
   catalog (`03_VARIABLES`) is comprehensive and well grouped.

---

## Where I push back / nuance

1. **The ETF "contradiction" is a denominator mismatch, not necessarily an error.**
   The two surfaces (`/audit` vs `/audit3`) deliberately select different row sets
   (different windows, filters, cost models). Calling one "wrong" overstates it:
   they are *incomparable*, which is a dashboard-design flaw, not proof of a data
   bug. The fix (a single canonical `resolved_closed_picks_net` view, A2) is right;
   the diagnostic wording should say "incomparable denominators," not "one is wrong."

2. **The "healthy consensus" ML claim needs an n-warning.** The ML-health audit's
   50.6% consensus WR is a *backtest* of an agreement subset of only **81 picks**
   (vs 3,203 single). That n is tiny and itself subject to multiple-testing. The
   `05_KILO_REVIEW` correctly explains why the ML "lift" doesn't contradict the
   negative-alpha ledger, but it does not flag the small-n fragility of the 81-pick
   consensus cell. That should be added.

3. **Killing emission is in tension with needing forward data.** The plan says
   "pause emission everywhere else" — but you must *keep emitting* (shadow/negative
   control) to generate the forward observations that audit3 needs to prove a door
   led. If you stop emitting a cell, you stop learning whether it would have worked.
   The `forward shadow` wording partially covers this, but it should be explicit:
   **every cell, including KILL cells, keeps a minimal shadow emission** so the
   forward ledger keeps accruing negative controls.

4. **Missing: a power analysis / target-n per cell.** Both reviews call for a
   forward-observation table but don't state how many realized rows each candidate
   needs to *reject or confirm* an edge at a given effect size. audit3 already has
   MDE tooling (`audit3_edge_hunt.py`); the plan should publish per-pod target-n
   before opening each pod, so "n≥100" is tied to a statistical power statement, not
   an arbitrary floor.

5. **Mutual funds / bonds are unaddressed.** The user's brief includes mutual funds
   and bonds; the ledger has MUTUAL_FUND and BOND cells with tiny n (BOND n=34,
   WEAK) and no forward plan. Minor scope gap worth one line in the plan.

6. **No capacity/cost-cap bound.** For a "proven" pod, the plan should state how much
   capital it could absorb (liquidity × volume limits) so a win isn't a paper-only
   win. Minor.

---

## Missing evidence / open questions

- Where does the **canonical `dashboard_data.json`** (not the `/tmp` slice) live, and
  how do we keep it reproducible? (I flagged this in `06_…/01_…md`.)
- Are the **7,502 integrity-excluded rows** ever re-audited, or permanently quarantined?
  They are 46% of the book; excluding them biases the retained 3,500 optimistic.
- What is the **planned cadence** for re-running the tribunal vs the forward ledger
  (hourly? daily?)? Not stated.

---

## Changes I'd make to the shared plan (proposed, not merged)

1. P0-0: keep **shadow emission always on** (negative controls) for every cell,
   including KILL cells.
2. P0-1 (stamp at-issue): add a **power/MDE per-pod target-n** column to the pod
   table, using the existing `audit3_edge_hunt` MDE tooling.
3. A2: reword the ETF contradiction to "incomparable denominators" and add the
   single canonical view.
4. Phase-2: add a **mutual-fund/bond** line (either a pre-registered pod or an
   explicit "not measurable yet — no forward data" note).
5. Phase-3: add a **capacity cap** estimate to each pod sleeve.

---

## Risk rating of the shared recommendations

| Recommendation | Risk | Note |
|---|---|---|
| Stop generating new strategies (Rule 0) | Low | Correct; the p-values are spent |
| Fix audit3 gates (WR→expectancy, BH per namespace, 2× stress) | Low | Cheap, high leverage |
| Wire KILL cells into a scanner denylist | Low–Med | Must keep shadow emission for forward data |
| Add forward-observation table | Low | Prerequisite for everything |
| Pause emission to 3 pods in 2 classes | Med | Stop-the-bleed, but risks starving the forward ledger if shadow emission is not kept |
| A/B the exit geometry (E14) | Low | Directly answers the user's "switch a variable" ask |

---

## Bottom line

The shared review is **accurate, well-evidenced, and strategically sound**. My
corrections are refinements (denominator wording, small-n warning on the ML
consensus, shadow-emission-negative-controls, power-based target-n), not a
disagreement with its core verdict: **no positive selection alpha today; the fix is
cost/exit remediation + forward measurement, not another strategy.**

*Not investment advice.*
