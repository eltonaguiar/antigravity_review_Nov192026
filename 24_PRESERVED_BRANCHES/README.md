# Preserved branches (not merged) — 2026-11-19T18:22Z

## `fix/audit3-alpha-scope` @ `7ba21e9` (4 commits)
From worktree `vanilla-handsaw-audit3`. PR #952 was opened and **closed unmerged**.

Why not merged: the branch predates **N4** (cost-scaled materiality floor). Its
`split_half_ok(values)` has no `min_mean=` parameter, so merging would silently
revert the promotion floor that now gates PROVEN_T2/CANDIDATE. The real delta vs
current main is ~141 added lines (G8 strategy-scope alpha, source-family gates,
forward-ingest hardening); `forward-observations-ingest.yml` and part of the alpha
gate already exist on main.

**Next step for the owner:** rebase `fix/audit3-alpha-scope` onto current `main`
(preserving `split_half_ok(..., min_mean=…)` and the 2x-cost gate), re-run the
audit3 suites, then re-open a PR.

Handoff: `COMS_HANDOFF_2026-11-19_AUDIT3_G8_SCOPE.md` in this folder.
