# 05_KILO_REVIEW — Independent confirming review (Kilo)

This folder is a **parallel, independent review** by a second agent (Kilo,
worktree `lapis-chronometer`). It confirms the peer review in `02_FINDINGS/` /
`03_VARIABLES/` / `04_RECOMMENDATIONS/` and adds what that review did not carry:

- **Exact selection-alpha numbers** with confidence intervals (F1): crypto LONG
  −0.442%/pick and ETF LONG −0.272%/pick vs direction-adjusted hold.
- **The leaky walk-forward gate** (F3): `wf_verdict` +0.96%/trade raw vs
  −0.19%/trade under point-in-time replay; at-issue inputs stamped on 6% of rows.
- **Backtest-n vs realized-n confusion** (F6): `crypto_liquidity_wick_reversal_v1`
  cited n=4,904 (backtest) but realized n=43.
- **Contradictory internal audits** (F7): `ML_SYSTEMS_HEALTH_AUDIT` (optimistic,
  walk-forward lift) vs `audit3 edge hunt` (rigorous, beta-separated).
- **Commit-SHA-level evidence index** for every claim.

Files:
- [`FINDINGS_ROOT_CAUSE.md`](FINDINGS_ROOT_CAUSE.md) — findings F1–F7 + bottom line.
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) — claim → file / commit SHA / URL.
- [`PLAN.md`](PLAN.md) — sequenced recovery plan incl. the forward A/B (hold-benchmark) harness.
- [`PAGES_AUDIT2_AUDIT3.md`](PAGES_AUDIT2_AUDIT3.md) — review of the two pages:
  audit3 (honest, live, wired) vs audit2/v2 (stale baked data, undeployed,
  contradicts audit3).
- [`SWARM_AUDIT2_HISTORY.md`](SWARM_AUDIT2_HISTORY.md) — the Google/Gemini swarm
  "fix audit2 page": audit2 is a 404, pivoted to audit3, FTP-secret fix.
- [`MD_SURVEY_STRATEGIES_METHODOLOGIES.md`](MD_SURVEY_STRATEGIES_METHODOLOGIES.md)
  — survey of 3,951 MD files: statistical-measure vocabulary, strategy families
  vs small-sample illusions, what deserves to be in an audit2.
- [`PEER_REVIEW_ASSESSMENT.md`](PEER_REVIEW_ASSESSMENT.md) — assessment of the
  sibling agents' reviews + corrections I adopt from them.
- [`AUDIT3_NEXTGEN_ENHANCEMENTS.md`](AUDIT3_NEXTGEN_ENHANCEMENTS.md) — ranked
  fixes: selection-alpha-as-gate, true-n DSR, independent watchdog, plus depth.
- [`PEER_SYNTHESIS_FINAL.md`](PEER_SYNTHESIS_FINAL.md) — final peer-work review:
  converged consensus, new findings (crypto stop-fill overshoot = 98.8% of the
  class loss), merged next-gen list, and two discrepancies to resolve.
- [`QUANT_FUND_MANAGER_PLAYBOOK.md`](QUANT_FUND_MANAGER_PLAYBOOK.md) — per-asset-
  class, risk-tiered strategy playbook (conservative → aggressive) + the 5-step
  method to quick viable sleeves (fix fills, kill the bleed, premia pods, barbell).

## Relationship to the rest of the repo

| Folder | Author | Content |
|---|---|---|
| `01_INVENTORY/` … `04_RECOMMENDATIONS/` | peer agent | inventory, findings, tunable-variable table, forward path |
| `05_KILO_REVIEW/` | Kilo | confirming root-cause + evidence index + A/B-harness plan |

Both reviews reach the same conclusion: **no positive selection alpha; the fix is
stop-the-bleed + forward measurement, not another strategy.**
