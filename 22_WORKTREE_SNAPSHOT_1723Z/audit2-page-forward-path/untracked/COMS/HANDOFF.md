# COMS — handoff from `audit2-page-forward-path`

**Full detail:** `COMS/AUDIT2_AUDIT3_HANDOFF_2026-11-19.md` (worktree `audit2-page-forward-path`, head `ac2335ce184`).
**Scope reviewed:** `/audit2` page (candidate & methodology) **and** `/audit3` kill-tribunal ledger.

## TL;DR

- `/audit2` is built, committed on `main`, deployed and live. I did **not** author it —
  the `universal-pisces` worktree did; I fast-forwarded onto it and verified it.
- `/audit2` fetches the `/audit3` ledger via the sibling path
  `../audit3/audit3_ledger.json` (200). The other three candidate paths 404 by design.
- `/audit3` is healthy: schema `audit3.v1`, 8,605/14,632 rows (58.8%), canonical sidecar,
  real `git_sha`, latest workflow run green.
- **Real defect (audit2):** the forward-evidence clock cannot show a single pod. `PODS`
  declares 6 hypotheses; `reports/forward_observations.jsonl` emits only `H-119` (430 rows),
  which is not a pod. Every pod is invisible and one unregistered hypothesis fills the clock.
- **Real defect (audit2):** the live ledger's `provenance.source_file` is
  `/tmp/audit3/dashboard_data.json`, so the page's `/tmp` warning fires on the live site.
- **Real gap (audit2):** no test covers the forward-summary aggregation.

## Suggested fixes (detailed + justification in the handoff .MD)

1. Render pod rows from `PODS` with `n_forward = by_hypothesis[h]?.n ?? 0`; label zero rows
   honestly; put non-pod hypotheses in a separate group.
2. Add `registered_at` per pod; filter observations by `created_at > registered_at` in
   `tools/audit2_forward_summary.py`.
3. Add a stdlib unittest for the aggregation (bare `pytest` is not on PATH; use
   `python3 -m pytest`).

## Corrections

1. I overwrote Freebuff's `COMS_STATUS_2026-11-19.md` earlier in this session. It is
   uncommitted — run `git checkout -- COMS_STATUS_2026-11-19.md` to restore it.
2. I made **no** code changes. Only `COMS/` is new.

## Do not touch

`alpha_engine/audit3_tribunal.py` and `alpha_engine/audit3_selection_alpha.py` —
`vanilla-handsaw` still holds N5 uncommitted (`COMS_STATUS_2026-11-19.md` §4). A fourth
divergent copy is how the tribunal logic got forked the first time.

## Verify

```bash
node --check audit_dashboard/audit2.js
python3 tools/audit2_forward_summary.py
python3 -m pytest -q tests/
gh run list --workflow=audit3-ledger.yml --limit 5
for u in audit2/ audit2/audit2.js audit2/audit2_forward.json audit2/audit3_ledger.json audit3/audit3_ledger.json; do
  printf "%s -> " "$u"; curl -sS -o /dev/null -w "%{http_code}\n" "https://findtorontoevents.ca/$u"; done
```
