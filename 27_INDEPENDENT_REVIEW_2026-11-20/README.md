# Independent audit3 review + COMS messages (preserved 2026-11-20T02:40Z)

From worktree `vanilla-handsaw` (untracked at HEAD `d07390e`, "final notes for
independent review") before deletion.

| File | What |
|---|---|
| `AUDIT3_INDEPENDENT_REVIEW_KILO_2026-11-20.md` | independent verification of every gate and claim |
| `COMS_MESSAGE_2026-11-20.md`, `COMS_MESSAGE_KILO_2026-11-20.md` | fleet messages |
| `COMS_AUDIT3_HANDOFF_2026-11-19.md` | earlier handoff |
| `2026-11-20-COMS_INDEPENDENT_REVIEW.md` | review summary update |

## Its verified findings (measured, not asserted)
- F1 block bootstrap, F2 split-half, N1 persistence, N2 churn, N3 recency,
  N4 materiality, N5 hold-time alpha, N7 freeze — all present and wired
  (`audit3-ledger.yml:201`).
- Freeze gate exits **1** (frozen). Local tests: 50 passed.
- Corrections to circulating notes: audit2 deploy is **not** broken; candidate
  counters exist; N5 alpha is published.

## Its remaining defects
1. **P0** coverage denominator: 8,769 scored vs 7,942 valid = **110.41%**
   (`scored_share_of_valid_pct` correctly returns `null`, but the underlying
   mismatch needs reconciliation).
2. **P1** H-119 forward benchmark coverage **0.798 < 0.90** (PF CI-LB 0.9213, IR 0.0429).
3. **P1** both registered pods had `n_forward: 0`.
