# Review: `AUDIT2_3_REVIEW_KILO_VANILLAHANDSAW_2026-11-19.md`

Reviewed 2026-11-19T17:15Z. Sources: the handoff and review docs in
`vanilla-handsaw`, its working tree, and the live ledger
(`audit3_ledger.json`, generated 2026-11-19T13:02:16Z).

## Verdict
The statistical direction is sound and three of the claims are independently
confirmed. But the document overstates two numbers, presents code-only work as
done, and its own coverage arithmetic repeats the denominator error it criticises.
Do not merge as-is; correct §0.3, §2 test counts, and §2.7 before landing.

---

## 1. Confirmed (verified, not taken on trust)

| Claim | Evidence |
|---|---|
| Persistence gate is wired and live | Ledger `persistence`: `runs_required 2`, `n_promoted_this_run 1`, `n_demoted_this_run 0`, `history_cells 446`. Exactly the "promoted this run but not granted" case the gate exists for. |
| Churn monitor is live and quiet | Ledger `verdict_churn`: `n_tracked 438`, `n_flipped 0`, `churn_rate 0.0`, `alert false`. |
| Workflow passes the flags | `vanilla-handsaw/.github/workflows/audit3-ledger.yml:104-107` has `--history`, `--history-write`, `--prev-ledger`, `--max-churn 0.30`. |
| Freeze gate enforced | `forward-test-new-strategies.yml:34` runs `tools/strategy_freeze_gate.py`; `reports/strategy_freeze.json` lists P0 = E11/E13/E14 with unfreeze criteria. |
| `required_n` is circular | `audit3_edge_hunt.py:366` calls `required_n(mean, sd)` with the **observed** mean. Live output proves the pathology: ETF `required_n = 1,745,345`; FOREX 25,756; CRYPTO 1,638. |
| audit2 pod registry is static | Live footer says so; `reports/` is not web-served. Matches this worktree's finding. |
| audit2-page-* branches carry no unique code | Both remaining worktrees are `ahead=0`; the only dirt is docs (`updates/…coms-*`, `COMS/`). |

## 2. Contradicted or overstated

### 2.1 "86 tests pass" — wrong
`34 + 11 + 4 = 49`, and running the three files gives **49 passed in 1.42s**:
```
python3 -m pytest tests/test_audit3_tribunal.py \
  tests/test_audit3_selection_alpha.py \
  tests/test_strategy_freeze_gate.py -q
49 passed
```
The 86 figure appears in both the review (§2) and the handoff. Fix before merge;
a false test count is exactly the kind of claim this project is trying to stop
publishing.

### 2.2 "46% of book dropped before scoring" — wrong, and it is the same error the doc criticises
Live coverage: `scored_rows 8,605 / total_closed_picks 14,632` = **58.8% scored**,
so **41.2%** is not scored, not 46%. The cited cohorts (`integrity 5,935` +
`auto_expired 9,110` = 15,045) exceed the whole book and overlap each other; the
canonical exclusion list sums to 6,027:
`invalid_row 5,802 + mirror_duplicate 92 + non_performance_exit 43 +
resolver_breakeven_fallback 90`.
Also, auto-expired rows are **not** cleanly dropped: the live payload reports
`zero_pnl_count 134`, and the canonical rows include timeout/flat exits. N6 must
start from the reconciled denominator, not from a sum of overlapping cohorts.

### 2.3 N5 selection alpha cannot be verified in the published ledger
`selection_alpha.available = false` and **0 of 7** class rows carry `alpha_pct`,
`hold_days_mean`, `alpha_per_day_pct` or `min_hold_participation`. The claim that
"the live selection_alpha block is the evidence behind 'crypto longs destroy
value'" is not supported by this artifact. The fields exist in
`audit3_selection_alpha.py`, but the generator published only the explanatory
block. Until the ledger emits them, N5 is code-only; label it that way.

### 2.4 The branch changes are uncommitted working-tree edits
`git rev-list --count HEAD ^origin/main` = **0**; the worktree is **1,109 behind**
`origin/main` and shows modified `audit3_tribunal.py`,
`audit3_selection_alpha.py`, both workflows, plus data files. There is no commit
history for F1/F2/N1–N5/N7, so "land this branch" is not a real operation — a
reviewer has to reconstruct the diff. Commit the gates (only your own files) or
attach a patch before calling them landable.

### 2.5 Cost figures are slightly stale
Doc says CRYPTO `0.0996`, FOREX `0.02`. Live: CRYPTO **0.0993**, FOREX **0.0291**.
The "5× spread" conclusion still holds (COMMODITY/FUTURES 0.15 vs FOREX 0.0291).

## 3. Interaction with this worktree's fixes

| Item | vanilla-handsaw | witty-fight |
|---|---|---|
| Coverage denominator | Flags the 105.26% contradiction; leaves it to "reconcile before publishing" | **Implemented**: nulls the headline ratio above 100, keeps raw 105.26, adds `valid_denominator_inconsistent` and `scored_but_not_dashboard_valid = 430` |
| Auto-expired | "dropped before scoring" | **Corrected**: mode-aware wording; canonical timeouts are retained; cites `zero_pnl_count` |
| Candidate counters | Not addressed | Adds `n_candidate_symbols` / `n_candidate_segments`; page labels "Candidate cells" vs "Candidate symbols" |
| Forward coverage | Notes the pod/H-119 mapping gap | **Root-caused** the 79.8% coverage: benchmark query stopped at exit; padded 6h; 2 regression tests |
| audit2 deploy | Correctly says `reports/` is not served | Found the P0: CI deploys to `/audit/` (404); live page is `/audit2/` |

**Recommendation:** land the witty-fight coverage reconciliation first, then build
N6 on top of it. Otherwise N6 will encode the 41.2%/46% confusion it is meant to
remove.

## 4. Required corrections before merge
1. Change "86" to **49** in the review and handoff (§2, §Verification).
2. Change "46%" to **41.2% not scored (58.8% scored)** and stop summing
   overlapping cohorts; use the 6,027 canonical exclusion list.
3. Mark N5 as **code-only, not published** until the ledger emits the fields.
4. Commit the gate changes, or attach a patch; the worktree diff is not a
   landable branch.
5. Refresh the cost numbers (0.0993 / 0.0291).
6. Adopt the audit3 coverage fix so N6 has a non-contradictory denominator.

## 5. Open questions — data-grounded position
- **E8 vs E3:** choose **E3 (equity breakout)**. It already has a pre-registered
  pod (`POD-EQUITY-BREAKOUT`) and does not depend on the broken FX feed. E8 adds
  a new surface before the measurement holes close.
- **FX backfill budget:** bounded by the freeze's own criterion — backfill until
  `fx_prices` covers **≥90% of the ledger span**, then stop. Do not fund beyond
  the criterion.
- **E12 clock, 30 vs 90 days:** **90 days**. H-119 accumulated 430 rows over
  ~9 months (~1.6/day). A 100-row forward floor therefore takes ~60 days at the
  current rate; a 30-day clock cannot reach n=100 for most pods and would fail
  them for lack of time, not lack of edge.

## 6. What still stands
F1 block bootstrap, F2 materiality-aware split-half, N1 persistence, N2 churn,
N3 recency, N4 cost-scaled floor, N7 freeze — all defensible and, where visible
in the live ledger, operating as described. The doctrine ("innocent until proven
guilty", gates fail closed, no demotion without proof) is consistent with the
audit3 review here.
