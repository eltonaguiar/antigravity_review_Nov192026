# Windows / opencode — review snapshot 2026-11-19T2308Z

**Agent:** opencode (Windows)
**Host:** desktop-081g9oh
**Seat:** `inbox/desktop-081g9oh/findtorontoevents_antigravity-ca/opencode`
**Snapshot:** 2026-11-19T23:08Z
**Canonical source branch:** `review/windows-2026-11-19` in `eltonaguiar/AGENT_FOLDERFRAMEWORK`
**Backup tag:** `archive/2026-11-19/review-windows` (`ed63ddc`; branch later rebased to `51d6de4`)

This folder is self-contained and intentionally isolated from every other agent's subfolder.
No files outside `windows/opencode/2026-11-19T2308Z/` were edited.

## Contents

| File | What it is |
|---|---|
| `00_SUMMARY.md` | Executive findings, per-surface verdict table, live ledger state |
| `01_proof.md` | Commands + outputs, DSR/coverage/forward evidence, code line references |
| `02_open_items.md` | Prioritized gaps and recommended fixes (owners + files) |
| `03_followup_verification.md` | Verification of `c4ec1ecb6b7`; correction of the zero-CANDIDATE attribution |
| `04_audit_surfaces_asset_class_deep_review.md` | Every `/audit`, `/audit2`, `/audit3` section/metric; per-asset-class research; TP/SL/volume test plan; ATH/skyrocket event study |
| `05_COLLABORATION_PROTOCOL.md` | Multi-agent branch/worktree/backup/COMS protocol v1 + roll call |
| `MANIFEST.json` | Machine-readable snapshot metadata |

## Live state at snapshot (checked from the pages)

- `/audit`, `/audit2`, `/audit3`: HTTP 200.
- `audit3_ledger.json`: generated `2026-11-19T21:02:25Z`, source `20:05:51Z`, provenance id `c4efa215e26a91ba`.
- 8,621 rows scored of 14,658 (58.81% canonical coverage).
- **0 PROVEN / 0 strategy CANDIDATE / 59 WEAK / 8 KILL.**
- Selection alpha: **−0.2689%/trade**, CI [−0.5043, −0.0364], n=3,185.
- Forward: 430 rows, only H-119; `POD-EQUITY-BREAKOUT` = 0.
- `/audit` money-ready: money=[], watch=[COMMODITY].
- CRYPTO and COMMODITY are class-level KILL; EQUITY is the only positive point estimate
  (n=941, +0.167%, CI [−0.419, +0.748], PF 1.08, required_n 9,064, WEAK).

## Bottom line

No surface has a money-ready pick today. The only credible future route is EQUITY via the
pre-registered breakout pod after the forward clock starts and passes. Cheap beta is the only
justifiable real-money allocation; the trading system is paper-only until the forward gate passes.

## Safety / merge notes

- Do not merge `feat/audit-review-organization-2026-11-19`: it contains a credential commit.
- Do not merge PR #965 wholesale: stale ledger + 15 conflicts; main already has most of it.
- Archive tags exist for the active work; see `MANIFEST.json`.
- One folder per agent, timestamped; never edit another agent's folder.

*Review artifact, not investment advice.*
