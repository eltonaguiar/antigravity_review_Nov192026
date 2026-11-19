# Audit surface verification + stale-branch delta (2026-11-19)

## What was checked
Live HTTP status of every page and data endpoint, plus the branch state of the
worktree used for the review.

```
$ for u in https://findtorontoevents.ca/audit3/audit3_ledger.json \
           https://findtorontoevents.ca/audit3/audit3_evidence.json \
           https://findtorontoevents.ca/audit3/ \
           https://findtorontoevents.ca/audit2/ \
           https://findtorontoevents.ca/audit/; do
    curl -s -o /dev/null -w "%{http_code} %{size_download}  $u\n" -L "$u"; done
200  491666  https://findtorontoevents.ca/audit3/audit3_ledger.json
200 2523018  https://findtorontoevents.ca/audit3/audit3_evidence.json
200   41792  https://findtorontoevents.ca/audit3/
200    6781  https://findtorontoevents.ca/audit2/
200 1437690  https://findtorontoevents.ca/audit/
```

## Corrected claims
Two earlier claims in this review were **wrong** and are withdrawn:

1. **"/audit3 is broken — 404 on the ledger."** False. The sidecars return 200 at
   `/audit3/audit3_ledger.json` and `/audit3/audit3_evidence.json`. The 404 came
   from requesting the root path `/audit3_ledger.json`; the deploy layout puts
   the sidecars next to `/audit3/index.html`
   (`.github/workflows/audit3-ledger.yml:167-168`).
2. **"/audit2 never existed."** False. `/audit2/` is a live 200 page with a
   working `audit2.js` and `audit2_forward.json`. The page was merged on `main`
   (`05bb08d157f`, `3175f6d7277`, `3d6faf7ffb7`).

## Stale-branch delta (important for anyone reviewing this worktree)
The worktree `witty-fight` is on `review-investment-strategy-audits`, based on
`1cd4f6527ee` (merge of PR #905), and is **1,063 commits behind `origin/main`**
(`git rev-list --count HEAD..origin/main` → 1063). Consequences:

| Artifact | In this worktree | On `origin/main` |
|---|---|---|
| `alpha_engine/forward_observations.py` | absent | present |
| `alpha_engine/forward_observations_ingest.py` | absent | present |
| `tools/audit2_forward_summary.py` | absent | present |
| `audit_dashboard/audit2.html` / `.js` | absent | present |
| `audit_dashboard/data/audit2_forward.json` | absent | present |
| `audit3_tribunal.py` features | pre-N1/N3/N4 | G8 persistence, materiality, churn, recency |

Everything in this review that depends on those files was read from
`origin/main` (`git show origin/main:path`), not from the working tree.

## What is still true on `origin/main`
- `coverage.scored_share_of_valid_pct` publishes `105.26` when the canonical view
  (8,605 scored) exceeds the dashboard's `valid_closed_picks` (8,175).
- The auto-expired cohort is described as "dropped before scoring and never
  counted", but the canonical book still contains timeout/`FLAT` rows
  (`status: FLAT` = 133 in the canonical snapshot; `zero_pnl_count` = 134 in the
  live payload).
- `forward_observations_ingest.collect()` pads the benchmark query window to the
  exit time only, so the bar that settles the leg is not fetched. Live forward
  coverage is 343/430 = **79.8%**, below the 90% gate in
  `forward_observations.BENCHMARK_COVERAGE_MIN`.
- `/audit2/` is deployed by an out-of-repo process: CI uploads the page to
  `/audit/` where it 404s, and `tests/test_audit2_page_deploy.py` only asserts
  filenames appear in the workflow.

## Verification
All commands above were run on 2026-11-19 between 16:40 and 16:49 UTC. Live
ledger `generated_at` = `2026-11-19T13:02:16Z`, source data
`2026-11-19T10:03:39Z`.
