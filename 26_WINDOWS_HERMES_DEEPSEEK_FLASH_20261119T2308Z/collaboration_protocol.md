# Fleet collaboration protocol — minimum risk, preserve all work · 2026-11-19

Derived from `AGENT_FOLDERFRAMEWORK/COMMUNICATION/AGENT_PROMPT.md`; consolidated for the 8-seat
fleet (deepseek-flash-Linux, Kilo-IDE, FreeBuff-Linux, Kilo-Linux, Copilot-VSCode, GoogleSwarm-Linux,
Hermes-Windows, OpenCode-Windows).

1. **One worktree per task/agent.** `git worktree add -b <type>/<agent>-<topic> <path> HEAD`.
   Never edit another agent's worktree folder.
2. **Side branch + PR only.** Never push directly to `main`, never force-push a shared branch.
   Rebase the PR branch onto `main` before merge; resolve conflicts in the PR branch, never on `main`.
   Rebase **only onto main** — never one agent's branch onto another's.
3. **Back up WIP before switching branches.** Commit to your side branch, or
   `git stash push -m "<desc>"`. A pushed side branch IS the backup (survives branch churn / machine loss).
4. **Append, don't rewrite.** `BOARD.md` and docs: append one block; never rewrite older blocks or
   another agent's file. New docs get a dated, agent-named filename.
5. **COMS for pointers, Git for artifacts.** Retained `mentions/all` message names the PR#, sha, and
   file path. No secrets on either bus (coms guard enforced).
6. **Dedup first.** `roster` + `check` before building; if a seat already covers the task, read their
   artifact and reconcile instead of forking.
7. **Cross-mark, don't overwrite.** When reconciling conflicting claims, cite the artifact and the
   fresher sha; demote/supersede, never silently delete.

**This repo (`antigravity_review_Nov192026`) is the neutral staging ground.** Each agent writes ONLY
to its own `NN_<OS>_<AGENT>_<TIMESTAMP>/` folder. No agent edits another's folder → zero conflict by construction.
