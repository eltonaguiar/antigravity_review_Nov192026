# Windows re-review — audit3 G8/G9 landing (2026-11-19)

**Reviewer:** `opencode`, Windows seat `desktop-081g9oh/findtorontoevents_antigravity-ca`
**Requested by:** kilo, `COMMUNICATION/handoffs/2026-11-19-kilo-to-coms-audit3-peer-review.md` @ `eef9e9d`
**Code tested:** `eltonaguiar/findtorontoevents_antigravity.ca` `main` @ `e2d552093172`
(contains the landed `6abfa22364e` code + `77718be66922` docs; `main` moves several times an hour)
**Artifacts:** this folder on branch `review/windows-2026-11-19` (not `main`)

Environment: Windows 11, PowerShell 5.1 client, Python 3.14.2, pytest 9.0.2, pandas 2.3.3.

## Verdict

The landed commit is real and the focused suite passes on Windows: **109 passed in 7.13s**
(six files listed in `01_proof.md`). Three of the four decisions are implemented as
described; **decision 4 has two documentation/implementation mismatches that make the
forward job able to stay green while accruing nothing.**

| # | Decision | Windows verdict |
|---|---|---|
| 1 | Strategy-scope alpha; class numbers are `class_proxy` and demote | Implemented, keys match, fail-closed works. Aggressive in practice: only 37 of 434 gate lookups resolve to `strategy`; 390 are `class_proxy`. Class aggregates use scope `class`. No code bug found. |
| 2 | 658 DSR floor for PROVEN, bucket width for CANDIDATE | Implemented as described. On the live ledger the split is currently inert and the floor is harsh: 66 DSR-scored cells, 2 clear 0.95, 0 cells pass `dsr_local >= 0.50` while failing global, and all 4 cells with n>=200 still have global DSR < 0.95. Live ledger: `n_proven=0`, `n_candidate=0`. |
| 3 | `require_alpha` demotes PROVEN when the sidecar is missing | Verified by code + test. Live gate `applied=true`, `demoted=0`. Risk is secret naming: `audit3-ledger.yml` only exports `DB_PASS_STOCKS`, while `tools/db_env.py` prefers `DB_PASSWORDS_JSON` and calls `DB_PASS_STOCKS` potentially stale. If only the canonical JSON secret exists, alpha silently skips and every PROVEN demotes. |
| 4 | Forward ingest cron `41 */6`, `ref: main`, fails on `n_admissible == 0` | **Two mismatches.** (a) The workflow does not pin `ref: main`; checkout at line 39 uses the triggering ref. (b) `n_admissible == 0` does not fail: `forward_observations_ingest.py` returns 0 (line 466) and the workflow only asserts the *ledger* is non-empty (line 76), which passes on the existing 430 historical rows. A writer that stops accruing stays green — the exact failure this job exists to surface. |

## Live-ledger evidence (from the tested commit)

`audit_dashboard/data/audit3_ledger.json`, generated `2026-11-19T18:14:32Z`:

- cells 359 (67 tested, 66 DSR-scored), rows 8,613
- verdicts: 292 `INSUFFICIENT_N`, 59 `WEAK`, 8 `KILL`, **0 `CANDIDATE`, 0 `PROVEN_T2`**
- alpha gate: `applied=true`, `tested=434`, `demoted=0`,
  `scopes={strategy:37, class_proxy:390, class:7}`
- alpha status: `beta_dominant=357`, `proven=1`, `unmeasured=1`
- the only `proven` alpha cell (`EQUITY / vol-contraction-scout / LONG`, n=62, alpha_n=61,
  CI-LB +0.1745) has verdict `WEAK` from earlier gates, not from alpha

A 357/359 `beta_dominant` rate is either genuine (all strategies are beta) or a
measurement/coverage artifact. Confirm which before treating zero PROVEN as the truth.

## COMS corrections (the handoff asked to confirm or correct these)

1. **`send` is not QoS 0.** The current client publishes **QoS 1**, still non-retained.
   Retained still requires `--retain` (Linux) / `--retain` or `-Retain` (Windows). Both
   platforms gained this before this review (`44a0b75`, `1c8b562`).
2. **Suggestion accepted with one caveat.** Adding `--retain` for direct inboxes is right.
   Do **not** retain `mentions/all`: retained is last-writer-wins per topic, so each new
   broadcast replaces the previous one and every future subscriber replays it.
3. **`check` semantics:** reads retained + in-flight on the seat inbox,
   `inbox/<host>/<wt>/all`, and `mentions/all`. It does not read other worktrees.
   This is now one line in `COMMUNICATION/coms-messaging/SKILL.md`; keep it there.
4. Registering a seat is required for replies. The B6 warning also fires when refreshing
   your own seat; that is noisy but not harmful.

## What was not changed

No source-repo edits. This branch only adds review artifacts. Recommended fixes and owners
are in `02_open_items.md`.
