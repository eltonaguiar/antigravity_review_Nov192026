# A7 — Does the live Pages site serve every result file the README claims?

**Question asked:** does `https://eltonaguiar.github.io/antigravity_review_Nov192026/`
actually serve every result file the PROVEIT README claims? Report the missing ones.

**Answer: no. It serves one of them. Every result file under `PROVEIT/` returns 404.**

**Date:** 2026-11-24 · **Branch:** `proveit-extended-scenarios-2026-11-24` @ `7940e8a`
**Method:** `PLAN/verify_pages.sh` (committed, re-runnable) plus a per-claim extraction pass. HTTP statuses read live with `curl -L`, cache-busted with `?_=$(date +%s)`.

## Root cause

`.github/workflows/pages.yml` uploads `actions/upload-pages-artifact@v3` with:

```yaml
path: docs
```

Only `docs/` is published. Everything at repository root — the whole `PROVEIT/`
tree, including all four agents' directories — is outside the published root and
is unreachable by construction. This is not a broken link, a build failure, or a
race with deployment; the files are not in the published artifact at all.

## Live status

| path | status | class |
|---|---|---|
| `/` (index.html) | **200** | already live from `main` |
| `/PROVEIT_KILOCODE.html` | **200** | already live from `main` |
| `/PROVEIT/README.md` | 404 | outside `docs/` — will never serve |
| `/PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/README.md` | 404 | outside `docs/` — will never serve |
| `/PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_2026-11-24T0350Z.json` | 404 | outside `docs/` — will never serve |
| `/PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/paramscan_2026-11-24T0350Z.json` | 404 | outside `docs/` — will never serve |
| `/PROVEIT/data/market_prices.csv` | 404 | outside `docs/` — will never serve |
| `/docs/PROVEIT/index.html` (mirror, in this PR) | 404 **now**, 200 after merge | pending |

## The one nuance that matters

`PROVEIT/README.md` claims `data/market_prices.csv`. That file exists in the repo
in agent `PROVEIT_24-11-2026_KILOCODE_AGENT/data/` and 404s on the site for the
same reason as everything else. Nine claimed files, one served.

## What the mirror fixes, and what it does not

PR #5 now adds `docs/PROVEIT/index.html` plus byte-identical copies of the three
result files. After merge those four paths move from `pending` to `served`,
verified by:

```
./PLAN/verify_pages.sh          # post-merge: NEW_IN_PR must be 200
./PLAN/verify_pages.sh --pre    # pre-merge:  NEW_IN_PR must still be 404
```

The links inside `docs/PROVEIT/index.html` are **relative**
(`PROVEIT_24-11-2026KILOCODE_AGENT/sim_...json`), so once merged they resolve to
`/PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_...json` — correct, and confirmed
`pending` in the pre-merge run.

**Not fixed:** the other three agents' `PROVEIT/` directories remain unreachable.
They are not this PR's files and are not mine to relocate. Options, in order of
preference:

1. Change the workflow to publish the repo root with `docs/` as the landing
   directory — one-line change, but republishes everything including large data
   files and any future secret left at root. **Not recommended without review.**
2. Add a second `upload-pages-artifact` step assembling `docs/` plus a
   whitelist of `PROVEIT/` paths. More moving parts, but bounded.
3. Leave as-is and treat GitHub Pages as serving only authored HTML, with result
   files fetched from the repo (raw.githubusercontent) instead. Cheapest, and
   honest about what Pages is for.

## Verification note

Two files were previously reported 200 in an earlier pass and one earlier
`--expect-404` run flagged them as mismatches. They are 200 because they are
already on `main` — not because this PR published them. The verifier now models
three classes (`ALREADY_LIVE`, `NEW_IN_PR`, `NEVER_SERVED`) precisely so that
"already live" cannot be mistaken for "this PR works", and so a pre-merge run
does not fail on files that were never expected to be absent.
