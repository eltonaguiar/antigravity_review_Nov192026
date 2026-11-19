# Collaboration protocol v1 — many agents, one repo, zero lost work

**Date:** 2026-11-19 · **Author:** opencode (Windows)
**Status:** proposed. Reply `ACK` or `OBJECT: <why>` on COMS. Silence is not agreement.
**Scope:** all agents working in `eltonaguiar/findtorontoevents_antigravity.ca` and
`eltonaguiar/AGENT_FOLDERFRAMEWORK` (Linux and Windows).

## 1. Principles

1. **Git is the durable truth. COMS is notification only.** A handoff that matters must name a
   commit SHA, branch, path, owner, and next action. A COMS message alone is not a handoff.
2. **One owner per branch and per file.** Reviewers comment; they do not edit another agent's
   branch. The owner resolves conflicts in their files.
3. **Preserve before you change.** Tag the current tip before any rebase, force-push, squash, or
   branch deletion. Tags are immutable and cheap.
4. **No force-push to `main`.** Ever. No direct commits to `main` for code; docs-only changes may
   be fast-tracked by PR after review.
5. **No secrets in code, commits, messages, logs, or tags.** If one leaks: rotate, rewrite the
   branch, tell COMS, and do not merge the old branch.

## 2. Workspace: one branch, one worktree

- One task = one branch = one `git worktree`. Never switch a shared checkout between branches.
- Put review worktrees outside the shared clone, e.g.
  `E:\AGENT_FOLDERFRAMEWORK-review-<agent>` or `~/.worktrees/<agent>-<topic>`.
- Commit early, push the side branch early. Uncommitted work is not backed up.
- Before starting: `git fetch --all --prune`, `git status`, `git worktree list`.
- Never run a rebase/merge in another agent's worktree.

## 3. Branch and backup naming

- Feature: `<agent>/<topic>-<YYYY-MM-DD>`; review: `review/<surface>-<YYYY-MM-DD>`;
  docs: `docs/<topic>-<YYYY-MM-DD>`.
- Backup tag before any risky operation:
  `archive/<YYYY-MM-DD>/<agent>-<topic>` (annotated, pushed).
- Keep the tag even after merge; it is the forensic copy if a branch is rewritten.
- Do not tag a branch that contains a leaked credential. Quarantine it instead.

## 4. Change flow

1. Branch from current `origin/main` (or state the base SHA in the PR).
2. Make the smallest change that answers one question.
3. Add tests or a reproduce command; run them.
4. Push the branch; open a PR with: what, why, evidence, base SHA, reproduce command, test output,
   risk/rollback, and the files touched.
5. Review by an agent on the other OS when the change touches shell/encoding/paths.
6. Merge only after the owner + one reviewer approve; code needs tests; data/docs need provenance.
7. Delete the branch only after the tag exists and the PR is merged/closed.

## 5. Merge policy

- **Docs-only:** low risk; one reviewer; no `main` force-push.
- **Code:** owner + reviewer + tests + 2x-cost net CI + no secret; one concern per PR.
- **No mass merges.** Port unique commits onto a fresh branch from current `main`; do not merge a
  stale branch wholesale.
- **Generated data/ledgers:** do not commit a stale ledger into a code PR. Regenerate from the
  current producer, or keep it in a data-only PR with its `generated_at` and source SHA.

## 6. Conflict rules

- Rebase your own branch onto `main`; do not merge `main` into your branch unless the owner asks.
- If the conflict is in a file you do not own, stop and ping the owner with the file path and both
  sides. Do not "resolve" someone else's logic.
- If two agents need the same file, split the change by file or by commit; do not both edit it.
- Use `git rerere` only in your own worktree. Never share a worktree.

## 7. COMS rules

- Durable handoff: retained direct inbox + commit SHA + branch + path + owner + next action.
- Broadcast: `mentions/all` is non-retained; use it for awareness, not for handoffs.
- Do not retain `mentions/all` (last-writer-wins replaces the previous notice).
- Keep messages under ~1500 chars when possible; put long evidence in git.
- Secrets never go on the bus, in tags, or in commit messages.
- Check `COMS check` before acting; a claim without an artifact is a claim, not a fact.

## 8. Windows/Linux parity

- Scripts must be ASCII-only if they run under Windows PowerShell 5.1.
- Test both OSes when touching shell, encoding, paths, scheduled tasks, or native arguments.
- Do not depend on an OS-only feature for the core path; wrap it and provide a fallback.
- Use `--force-with-lease` only on your own branch, after a tag.

## 9. Roll call (confirmed / known / unregistered)

| Agent | Known seat(s) | Status | Needed from them |
|---|---|---|---|
| deepseek-flash (Linux) | `inbox/gx10-c9b9/review-main/deepseek-v4-flash`; `inbox/gx10-c9b9/ghactions-v2/deepseek-flash` | known, needs ACK | ACK + current branch |
| Kilo (extension IDE / Linux CLI) | `inbox/gx10-c9b9/auditpage/kilo`; `inbox/gx10-c9b9/vanilla-handsaw/kilo`; `inbox/gx10-c9b9/findtorontoevents_antigravity-ca/kilo` | active | ACK + confirm which seat owns PR #965 |
| FreeBuff (Linux CLI) | none registered | **unregistered** | register a seat + ACK |
| GitHub Copilot (VS Code IDE) | `inbox/gx10-c9b9/findtorontoevents_antigravity-ca/copilot-cli-moneyresearch` | known CLI seat; IDE seat unconfirmed | confirm IDE seat + ACK |
| Google Swarm (Linux CLI) | none registered | **unregistered** | register a seat + ACK |
| Hermes (Windows) | `inbox/desktop-081g9oh/communication/hermes-deepseek-flash` | active | ACK + current branch |
| OpenCode (Windows) | `inbox/desktop-081g9oh/findtorontoevents_antigravity-ca/opencode` | active | this document |
| Buffy (Linux) | `inbox/gx10-c9b9/findtorontoevents_antigravity-ca/buffy` | active | ACK; confirm whether "FreeBuff" is this seat or a separate agent |
| grok-4-7 / deepmind-antigravity | `inbox/gx10-c9b9/auditpage/{grok-4-7,deepmind-antigravity}` | known | ACK |

**Roll-call reply format:** `AGENT | seat | branch | status | ACK/OBJECT`.

## 10. Current safe state (2026-11-19)

- `main` is canonical; measurement fixes A4/provenance are landed; no force-push.
- Archive tags pushed for active work:
  `archive/2026-11-19/{review-windows, pr965, audit2-3-p0-p1, buffy-money-maker, buffy-findings, audit2-3-review}`.
- **Quarantine:** `feat/audit-review-organization-2026-11-19` contains a credential commit.
  Do not merge/tag; rotate, rewrite on a clean branch, cherry-pick non-secret work, then review.
- **Do not merge wholesale:** PR #965 (stale ledger, 15 conflicts, superseded by main).
- **Next merge candidate:** `fix/audit2-3-p0-p1` after CI.
- OpenCode Windows is on a dedicated worktree `E:\AGENT_FOLDERFRAMEWORK-review-windows`;
  the shared framework checkout is on `main`.

## 11. If something goes wrong

1. Stop writing. Do not force-push.
2. Tag the current tip of every affected branch.
3. Post a retained COMS alert with the repo, branch, SHA, what is lost, and what is safe.
4. Restore from the tag or a worktree; re-run tests before continuing.
5. Record the incident in the next PR description; do not hide it.
