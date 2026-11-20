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

---

## Update 2026-11-20T05:40Z — three of these findings are now resolved

Verified live against `audit3_ledger.json` @ 05:21Z and `status.json`:

| Original claim | Current measured state |
|---|---|
| **P0** coverage 110.41% (8,769 scored vs 7,942 valid) | **Fixed** (PR #984): `valid` reconciles to the canonical kept rows — now `8,649 / 8,649`, basis `canonical_kept_rows`, share 100% |
| **P1** "no scheduled ingest, pods can never promote" | **Incorrect**: `forward-observations-ingest.yml` is scheduled (`41 */6`). The real gap was missing ingest *conditions* for emitting pods — fixed in #978 |
| **P1** zero-row pods | **Partly resolved**: the forward ledger grew **430 → 443** rows with the first-ever `H-2026-11-19-03` (12) and `H-2026-11-19-06` (1). Their only remaining blocker is the deliberate `observe` status |
| **P1** H-119 benchmark coverage 0.798 < 0.90 | **Still open** — needs price joins for ~87 rows (DB) |
| **Policy** N7 freeze red | **Still intended** until E11/E13/E14 close |

Two further defects were found and fixed while exercising the accrual:
`inf` profit factor broke JSON serialisation (#991), and the status contract was
built before the ledger it reports (#990).
