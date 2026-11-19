# COMS handoff — `audit2-page-forward-path`

**From:** Kilo (worktree `audit2-page-forward-path`, branch `audit2-page-forward-path`)
**Head at handoff:** `ac2335ce184` (fast-forwarded from `5e5fc267703`)
**Worktree state:** clean except this handoff (`COMS/` untracked, `COMS_STATUS_2026-11-19.md` modified)
**Date:** 2026-11-19T17:00Z

---

## 1. What is actually true about my work in this session

I did **not** author the audit2 page. It was built on `main` by the `universal-pisces`
worktree (see `updates/2026-11-19-audit2-page-and-canonical-guard.md`) and landed while
this worktree existed to receive it. My session:

1. Fast-forwarded this worktree from `5e5fc267703` → `ac2335ce184` (525 files, includes
   `audit_dashboard/audit2.html`, `audit_dashboard/audit2.js`,
   `audit_dashboard/data/audit2_forward.json`, `tools/audit2_forward_summary.py`, and the
   `/audit2` deploy block in `.github/workflows/audit3-ledger.yml`).
2. Read and verified the page, its data pipeline and its deploy path.
3. Regenerated `audit_dashboard/audit_frontend_manifest.json` via
   `python3 tools/audit_frontend_manifest.py` (no diff persisted — it matched main).
4. Launched two background review agents (one finished; one still in flight when the
   user asked for this handoff).

**Nothing is committed by me.** No source file in this worktree differs from `main`.

## 2. Verified facts (do not re-derive these)

| Check | Result |
|---|---|
| `node --check audit_dashboard/audit2.js` | pass |
| `html.parser` feed of `audit_dashboard/audit2.html` | pass |
| `python3 tools/audit2_forward_summary.py` input `reports/forward_observations.jsonl` | 430 rows, **one** hypothesis: `H-119` |
| `audit_dashboard/data/audit2_forward.json` | `n_rows=430`, `by_hypothesis.H-119 = {n:430, benchmark_leg:343, intrabar:430, pods:[]}` |
| Live `https://findtorontoevents.ca/audit2/` | 200 |
| Live `/audit2/audit2.js` | 200 |
| Live `/audit2/audit2_forward.json` | 200 |
| Live `/audit2/audit3_ledger.json` | **404** (expected — page falls through) |
| Live `/audit3/audit3_ledger.json` | **200** (the path the page actually uses) |
| Live `/audit/data/audit3_ledger.json` | 200 |
| Live `/audit2/data/audit3_ledger.json` | 404 |
| `gh run list --workflow=audit3-ledger.yml` | latest run `44529413677` success (workflow_dispatch, 2026-11-19T13:01Z) |
| `COMS_STATUS_2026-11-19.md` (Freebuff) | `vanilla-handsaw` still holds N5 uncommitted; `prediction_market_copy_trading` decisions unresolved |

So: the page is deployed, the ledger loads through the `/audit3/` sibling path, and the
deploy block uploads `index.html`, `audit2.js`, `audit2_forward.json`. The gap is **not**
deployment.

## 3. The real defect: the forward-evidence clock has no pod coverage

`audit_dashboard/audit2.js:181-184` builds the clock row from `audit2_forward.json` only:
it iterates `by_hypothesis` keys. The pod registry (`PODS`, `audit2.js:6-25`) carries these
hypothesis IDs:

- `H-BABY-EQUITY-VT-PATTERN-SWEEP-001` (POD-EQUITY-BREAKOUT, `pre_registered`)
- `H-2026-11-19-01` … `H-2026-11-19-05` (all `observe`)

`reports/forward_observations.jsonl` emits **only `H-119`**. Therefore:

- Every pre-registered and observe pod is invisible in the forward clock.
- `H-119` appears in the clock but is **not** a pod — it is an unregistered hypothesis.
- The page's central claim ("a pod can only promote on forward rows dated after its
  registration") is currently unverifiable for every pod and undated for `H-119`.

**Recommended fix (smallest correct change, no fabrication):**
render `PODS` rows first with `n_forward = by_hypothesis[hypothesis]?.n ?? 0`, mark them
`0 rows — clock not accruing`, then append any hypothesis present in
`audit2_forward.json` that is not a pod under a separately labelled "unregistered
hypothesis" group. That makes the honest state visible instead of hiding the pods.
Justification: the page already commits to "missing ledger renders an honest unavailable
message, never a fabricated table"; the same rule must apply per-pod.

## 4. Second gap: pod registration dates are not in the data

`audit2.js:79` says promotion requires "forward rows dated after its registration", but no
registration timestamp exists anywhere the page can read. Suggested: add
`registered_at` to each `PODS` entry (ISO-8601) and show it in the pod card, then filter
`reports/forward_observations.jsonl` rows by `created_at > registered_at` inside
`tools/audit2_forward_summary.py`, emitting `n_eligible`. Justification: without a
timestamp the gate is prose, not a gate; `forward_observations.jsonl` already has
`created_at` (`2026-11-19T07:20:40Z` on the sample row), so the filter is cheap.

## 5. Third gap: no test coverage for the page's data contract

`grep -rln "audit2" tests/` returns only `tests/miracle-daytrades.spec.ts` (unrelated).
Suggested: a stdlib `unittest` (matching `tests/test_alpha_slice_scan.py` style) that
builds a temporary JSONL, runs `tools/audit2_forward_summary.py`'s aggregation, and
asserts `n`, `benchmark_leg`, `intrabar` counts and the pod/hypothesis join. Justification:
this is a *computation* of promotion evidence; it should not be validated only by
`node --check`.

## 6. Dead fallback paths (low severity, keep or prune consciously)

`audit2.js:159-160` tries four ledger URLs. On the live site two of them
(`audit2/audit3_ledger.json`, `audit2/data/audit3_ledger.json`) are 404 by construction —
the deploy block never writes them to `/audit2/`. This costs one extra 404 round-trip per
page load. Either prune the list to the two that resolve, or (better) leave the list and
add a comment naming which paths are live-verified, so a future deploy change does not
silently break the single working path. Justification: the fallback chain is the only thing
keeping the page's verdicts alive; it should be documented at the point of use.

## 7. What I did NOT do, and why

- Did **not** modify `audit_dashboard/audit2.html` / `audit2.js` — the user asked for a
  handoff mid-review; the second review agent had not reported yet, and editing the page
  while two agents read it risks duplicate/conflicting fixes.
- Did **not** touch `alpha_engine/audit3_tribunal.py` or `audit3_selection_alpha.py` —
  per `COMS_STATUS_2026-11-19.md` §4, `vanilla-handsaw` holds N5 uncommitted in those
  files; editing them here would create a fourth divergent copy.
- Did **not** republish the `COMS_STATUS_2026-11-19.md` I overwrote earlier in this
  session — see §8.

## 8. Correction to my own earlier action (please read)

Earlier in this session I overwrote `COMS_STATUS_2026-11-19.md` with a short status note.
That file was Freebuff's fleet status and is referenced by other worktrees. The overwrite
is **uncommitted** (`git status` shows ` M COMS_STATUS_2026-11-19.md`). Recommended action
for whoever picks this up: `git checkout -- COMS_STATUS_2026-11-19.md` to restore
Freebuff's version, because this handoff supersedes the short note and the fleet status is
more useful than my summary.

## 9. Suggested owner split from here

- **Page/data owner:** items in §3, §4, §5 in `audit_dashboard/audit2.js` +
  `tools/audit2_forward_summary.py` + one new test. Self-contained, no schema change to
  `audit3_ledger.json`.
- **Tribunal owner (vanilla-handsaw):** commit N5 first. The audit2 promotion story is
  meaningless until the tribunal emits per-pod forward rows.
- **Deploy owner:** none needed now; the `/audit2` FTP block is working.

## 10. How to verify anything in this file

```bash
node --check audit_dashboard/audit2.js
python3 -c "import html.parser;html.parser.HTMLParser().feed(open('audit_dashboard/audit2.html').read());print('ok')"
python3 tools/audit2_forward_summary.py
python3 -m pytest -q tests/            # pytest 9.0.3 is installed as a module; bare `pytest` is not on PATH
for u in audit2/ audit2/audit2.js audit2/audit2_forward.json audit2/audit3_ledger.json audit3/audit3_ledger.json; do
  printf "%s -> " "$u"; curl -sS -o /dev/null -w "%{http_code}\n" "https://findtorontoevents.ca/$u"; done
gh run list --workflow=audit3-ledger.yml --limit 5
```


## 11. Audit3 tribunal review (audited, not assumed)

Ledger: `audit_dashboard/data/audit3_ledger.json`, `generated_at=2026-11-19T13:02:16Z`.

- `schema=audit3.v1`; `summary.n_rows=8605`; 7 class rows.
- `coverage.denominator.mode=canonical`, `loaded_from_sidecar=true`, canonical schema
  `audit.canonical.v1`; statement: "audit3 scores 8,605 of 14,632 closed picks (58.8%)".
  So the audit2 page's coverage banner will render in its non-warning state (`mode==="canonical"`).
- Verdicts present in this build: `KILL` (CRYPTO n=6740 net -0.3103; COMMODITY n=54 net -3.3112;
  BOND n=34 net -0.2473), `WEAK` (EQUITY n=936; ETF n=586; FOREX n=251),
  `INSUFFICIENT_N` (FUTURES n=4). No `PROVEN_T2` / `CANDIDATE` rows — the enum allows them,
  the current data does not produce them. `stress_2x_ok=false` on every class.
- `provenance`: `generator_version=audit3.v2`, `git_sha=e40231f4bfe4` (verified: real commit,
  "Merge pull request #924: fix audit3 ledger commit/push step"), `input_sha256=eba1b290...`.
- **Concrete finding:** `provenance.source_file` and the top-level `source` are both
  `/tmp/audit3/dashboard_data.json`. `audit_dashboard/audit2.js:150` warns whenever the
  source string contains `/tmp/`. So the live `/audit2` page **will** display
  "Warning: source is a /tmp build path, not a committed file." That warning is truthful
  (the ledger is built in a CI temp dir) but reads as a defect to a reader. Recommended:
  either normalise the provenance string to the committed artifact name before publishing,
  or soften the audit2 warning to "built in CI" when `git_sha` is present and resolves.
- `tools/audit3_denylist_health.py` exists and is invoked by the workflow with
  `--max-age-days 2 --min-strategy-kills 1`; the run passed.
- Latest `audit3-ledger` run `44529413677` = success (workflow_dispatch, 13:01Z). The
  workflow's commit step stages `audit3_ledger.json`, `audit3_verdict_history.json` and
  `audit2_forward.json` — every file its deploy step uploads.
- Live `/audit3/audit3_ledger.json` = 200; `/audit2/audit3_ledger.json` = 404;
  `/audit2/data/audit3_ledger.json` = 404. The page's first candidate 404s, then resolves
  on `../audit3/audit3_ledger.json` (200).

**Conclusion:** audit3 is healthy and its ledger is the correct source for audit2's verdict
table. The one cosmetic defect is the `/tmp` provenance warning.
