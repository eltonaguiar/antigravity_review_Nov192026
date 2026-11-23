# Open PR backlog on the main repo (2026-11-23)

Repo: `eltonaguiar/findtorontoevents_antigravity.ca` - the one that publishes to findtorontoevents.ca.
This folder is the ideas/brainstorm tracker; **code** belongs in the main repo.

| PR | Branch | Mergeable | Opened |
|---|---|---|---|
| **#1018** | `zoo/p0-recovery-2026-11-20` - audit2 per-class verdict panel + honest remediation | **MERGEABLE** | 2026-11-20 |
| #1046 | `fix/dsr-baselines-h146-key-scrub-2026-11-21` - bracket trial count, renumber H-149, EQUITY backtest, scrub consult_multi keys | UNKNOWN | 2026-11-21 |
| #1003 | `fix/audit-ledger-population-survivorship` - stop publishing two populations as one cohort | UNKNOWN | 2026-11-20 |
| #1001 | `docs/audit-consolidation-plan-ef6c` - consolidation + fix + test plan | UNKNOWN | 2026-11-20 |
| #965 | `feat/audit3-p0-p1-correctness` - G8 alpha gate, global-n DSR, G9 stress gate, blocklist wiring, forward shadow emission, denylist watchdog | UNKNOWN | 2026-11-19 |

Merged today and therefore absent from the list: **#1064** (`be2f2d60185`, provenance ledger + resolver
+ emit hook) and **#1065** (HML pre-registration).

## Notes

- **`mergeable: UNKNOWN` on four PRs** means GitHub has not recomputed mergeability since the base
  moved. They need a push or a base refresh before anyone can judge them; they have been open 1-3 days.
- **#965 is the one to look at first**: it carries P0/P1 correctness work (alpha gate, global-n DSR,
  stress gate, blocklist wiring) that several other results may implicitly depend on.
- **One branch has no PR**: `block-d-session-record-2026-11-22` - one of the 12 pushed today. Pushed but
  unopened means it is invisible to review.
