# AGENT PLAN 2026-11-24 — three lanes, one step per turn

Binding protocol for every agent executing this plan:

1. **Execute exactly ONE step per turn.** Never re-summarise the plan. Never propose an alternative plan.
2. **Every step must end with an artifact** that someone else can check without trusting you:
   a file path, a commit sha, or a PR number.
3. **Reply with exactly one line**, either:
   `STEP <id> DONE: <artifact>`
   `STEP <id> BLOCKED: <command> :: <error>`
   `STEP <id> BLOCKED: approval`
4. **Never ask the operator to choose.** If two fixes exist, take the one that touches fewer files
   and state in one clause which you took.
5. **If a command raises an approval prompt, stop and report `BLOCKED: approval`.** Do not retry it,
   do not click anything, do not work around it by editing files by hand.
6. **Commit the step's artifact and tick its checkbox below in the same commit.**

Anti-patterns that count as a failed step: a prose answer with no artifact, a plan restated back,
a question, or "I will now…" with nothing changed.

---

## Lane A — Kilo: get CI green on the audit PRs

- [ ] **A1** Reproduce the failure locally. Run the failing test (`tests/test_r40_power.py`,
      `tests/test_audit_metric_invariants.py`) and capture the exact error.
      Artifact: `PLAN/logs/A1_<testname>.log`
- [ ] **A2** Decide the CSV question. The test needs
      `data/cache/asset_class_review/<SYM>_5y.csv` for a 20-ETF universe and CI has no cache.
      Two candidate fixes: (a) commit the CSVs, (b) skip cleanly when the cache is absent.
      Take whichever touches fewer files. Artifact: one line in `PLAN/logs/A2_DECISION.md` naming the choice and why.
- [ ] **A3** Implement the chosen fix on branch `fix/r40-cache-ci-2026-11-24`, push it.
      Artifact: branch + sha.
- [ ] **A4** Verify with `gh pr checks <n>`. Report each check name and conclusion.
      Artifact: table in `PLAN/logs/A4_CHECKS.md`.

## Lane B — Zoo: resolve BESTIEB PR #39 (merging issues lane)

Facts already established by two independent merge-trees — treat as given, do not re-derive:
`SUCCESS_PACK_MUSE.MD` is **NOT** in conflict. The conflict set is 8 paths and every one is
bot-generated output: `jobs.json`, `public/jobs.json`, `public/gotjob/jobs.json`,
`public/findjobs/jobs.json`, `public/jobs-data.json`, `FRESH_JOBS.md`, `public/index.html`,
`README.md`. The writer is `.github/workflows/hourly-scan.yml:87`.

- [ ] **B1** Fetch and rebase `arlo/success-pack-2026-11-05` onto `origin/main`. Do not edit
      `SUCCESS_PACK_MUSE.MD` at all. Artifact: `git log --oneline -3` output in `PLAN/logs/B1_REBASE.md`.
- [ ] **B2** For the seven data files take `origin/main`'s version verbatim. For `README.md` take
      `origin/main` then re-apply only the authored prose the PR added.
      Artifact: `git diff --stat` vs main in `PLAN/logs/B2_RESOLVE.md`.
- [ ] **B3** Push the branch. Artifact: pushed sha.
- [ ] **B4** Verify: `gh pr view 39 --json mergeable,mergeStateStatus` must read `MERGEABLE`.
      Artifact: the two field values.

## Lane C — Copilot: land the review-repo work

- [ ] **C1** Audit PR #5 (`antigravity_review_Nov192026`) against its committed files: verify
      9.18% hold and +1.31/+1.42/+1.50pp and $44.61/$90.23/$226.80.
      Artifact: claim-vs-committed table in `PLAN/logs/C1_PR5.md`.
- [ ] **C2** If C1 shows no mismatch, merge PR #5. Otherwise report the mismatch and stop.
      Artifact: merge commit sha, or `BLOCKED` + the table.
- [ ] **C3** Merge the two clean PRs #4 and #2 (both `MERGEABLE/CLEAN`).
      Artifact: two merge commit shas.
- [ ] **C4** Report the remaining open-PR count for the repo. Artifact: number + list.

## Lane D — first agent to finish its lane: clear the BESTIEB backlog

PRs #43, #41, #40 are all `MERGEABLE/CLEAN`. Merge them in that order (lowest risk first:
privacy scrub, then the two doc packages). Artifact: three merge commit shas.

---

## Why one step per turn

A turn that answers in ten seconds is a turn whose whole deliverable was prose. Bounding the step to
one verifiable artifact, and forbidding the question, is what converts a ten-second answer into work
that shows up in git. The plan file is the memory: any successor agent reads the checkboxes instead
of needing the chat history.
