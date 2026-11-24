# Plan — make PROVEIT actually reachable on Pages

**Date:** 2026-11-24 · **Author:** ghcopilot · **Branch:** `pages-serve-proveit-2026-11-24`

## The defect, measured

| observation | evidence |
|---|---|
| Pages serves **0 of 35** PROVEIT result files | every path under `/PROVEIT/` returned 404 |
| All 404s are **identical 9,379 B** | GitHub Pages 404 page — uniform, not per-file |
| Deploy pipeline is **healthy** | `/index.html` 200 (112,802 B), `/PROVEIT_KILOCODE.html` 200 (8,531 B), `/EVALUATION_HARNESS.md` 200 (7,833 B); last 5 Pages runs `completed/success` |
| Root `PROVEIT/` exists on `main` | 35 files, ~440 KB |
| `docs/PROVEIT/` does **not** exist on `main` | 0 files |

**Root cause:** `.github/workflows/pages.yml` publishes `path: docs` only. The deliverable lives at
root `PROVEIT/`, which is browsable on github.com and **invisible to Pages**. The three files that
do serve are all under `docs/`. This is a publish-path contract failure, not lost work.

## Why PR #5 is not the fix

PR #5 (`proveit-extended-scenarios-2026-11-24`) mirrors the deliverable a *second* time into
`docs/PROVEIT/`. That creates two copies of the same 8 result files with no sync mechanism — the
silent-divergence pattern that already cost this repo a revert (`8277657`).

It also **cannot be merged by me**: its diff carries 6 `CONTEST/` paths that are absent from
`main` (API returns 404 for `CONTEST/tools/check_round_integrity.py` and
`CONTEST/CONTEST_STATUS_2026-11-24.md`). Those are another agent's work. The standing rule —
never land files I did not author — forbids merging it.

Note: `gh pr view 5 --json files` reported 31 files with **zero** `CONTEST/` paths, while
`git diff --name-only origin/main...HEAD` reported **6**. The CLI's file list was incomplete;
the diff is authoritative. Anyone reviewing PR #5 from the `gh` summary alone would miss the
foreign files entirely.

## The plan

1. **Single canonical home:** root `PROVEIT/`. It already holds 35 files and is what `README.md`
   and the live `/PROVEIT_KILOCODE.html` link to on github.com. Moving it would break those links.
2. **Bring the 4 branch-only result files into root `PROVEIT/`** so the folder is complete:
   `PROVEIT_EXTENDED_SCENARIOS_20261124T0350Z.md`, `paramscan_2026-11-24T0350Z.json`,
   `provenance_2026-11-24T0350Z.json`, `sim_2026-11-24T0350Z.json`.
3. **Publish by build-time copy, not by duplication.** Add a `pages.yml` step that copies
   `PROVEIT/` → `docs/PROVEIT/` into the *build workspace* before
   `actions/upload-pages-artifact`. Nothing committed under `docs/PROVEIT/` except the landing
   page, so there is exactly one source of truth and no divergence window.
4. **Add `PROVEIT/**` to the `paths:` trigger**, or a PROVEIT change will not redeploy the site.
5. **Fix the orphan:** `docs/PROVEIT/index.html` links 7 of the 8 result files.
   `provenance_2026-11-24T0350Z.json` ships but is linked from nowhere — the provenance record is
   the one nobody can find. Add the link.

## Acceptance criteria

- `pages.yml` build step copies PROVEIT without failing the existing asset checks
  (`docs/index.html` present, `id="toc"` anchor present) — both are preserved untouched.
- After merge, all 8 result files return **200** from
  `https://eltonaguiar.github.io/antigravity_review_Nov192026/PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT/<file>`.
- `git ls-tree origin/main -- docs/PROVEIT` shows **only** `index.html` — proving no duplicate
  result files were committed.
- No `CONTEST/` path appears in this branch's diff.

## Out of scope

PR #5 itself. It should be closed or rebased by whoever owns the CONTEST commits; this branch
supersedes the PROVEIT half of it.
