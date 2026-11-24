# audit3 forward-gate coverage (live ledger, 2026-11-24T12:35Z)

Source: `findtorontoevents.ca/audit/data/audit3_ledger.json` (`forward_gate`, `cells`).

## Gate
`enforced: true`. Rule: a pod’s cell reaches PROVEN_T2 only when its own forward
rows (closed on/after `registered_at`) clear n>=100, net PF CI-LB>1.0 or IR>=0.5,
honest intrabar first-touch.

## Coverage
- Pods: **9**.
- `n_forward`: **5 pods have 0**, 3 have 2, 1 has 3.
- Eligible: **0 of 9**.
- Status: 1 `pre_registered`, 8 `observe` — **no pod has enough forward rows to promote**.
- Gate ledger claims `n_rows = 451`, but only 4 pods hold 2–3 post-registration rows;
  the remainder is the backfilled ledger (the 451 rows are not forward).
- Cells: **365** (was 366); **0 cell-level forward fields** — forward evidence exists
  only at pod level, so no cell can be described as forward-tested.
- Cell outcomes: 68 tested, **0 proven**, 0 candidates, 6 kill, 297 insufficient.

## Implication
Cells/picks have **no forward evidence**; any PROVEN claim would be unsupported.
Current gate blocks promotion correctly. Next requirement is genuinely new post-registration
rows per pod (n>=100), not backfill.
