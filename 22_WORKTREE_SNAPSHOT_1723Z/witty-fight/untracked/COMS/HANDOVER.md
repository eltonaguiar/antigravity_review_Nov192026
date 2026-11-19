# HANDOVER: audit surface review + fixes (2026-11-19)

Branch: `review-investment-strategy-audits` in worktree `witty-fight`.
Base commit `f9e6c8202a1`; **1,063 commits behind `origin/main`** (`e48387f0fd9`).
Changes are uncommitted.

## Verified live state (do not re-litigate)
All endpoints return 200:

| URL | Status | Notes |
|---|---|---|
| `/audit/` | 200 | "autopsy" surface: no class money-ready, 22,947 ghost rows, inverted confidence |
| `/audit2/` | 200 | methodology library; JS + `audit2_forward.json` load |
| `/audit3/` | 200 | |
| `/audit3/audit3_ledger.json` | 200 | `generated_at 2026-11-19T13:02:16Z` |
| `/audit3/audit3_evidence.json` | 200 | |

Two prior claims are withdrawn: audit3 is **not** 404 and audit2 **does** exist
(merged on main in `05bb08d157f`, `3175f6d7277`, `3d6faf7ffb7`).

Live ledger verdicts: 8,605 / 14,632 scored (58.8%); 0 PROVEN, 0 CANDIDATE,
59 WEAK, 8 KILL, 292 INSUFFICIENT. Forward gate: H-119 n=430, PF 1.1147,
CI-LB 0.9213, IR 0.0429, benchmark coverage 0.798 (gate 0.90) — not promotable on
three independent criteria.

## Fixes made in this worktree (all tests green: 111 passed)
1. **audit3 coverage honesty** — `alpha_engine/audit3_tribunal.py`
   - `scored_share_of_valid_pct` could print 105.26 (8,605 scored vs 8,175 valid).
     Now `None` when >100, raw value kept in `scored_share_of_valid_pct_raw`,
     plus `valid_denominator_inconsistent` and `denominator_reconciliation`.
   - Auto-expired wording no longer claims the rows are "never counted"; in
     canonical mode it says timeouts are retained at their resolved exit and cites
     the zero-P&L count.
   - Tests: `tests/test_audit3_coverage_alpha.py` (+3).
2. **Forward benchmark right-edge bug** — `alpha_engine/forward_observations_ingest.py`
   - `collect()` stopped the bar query at the exit; `close_at()` needs the first
     bar at/after it. Added `BENCHMARK_LOOKAHEAD_MS = 6h` and padded `hi`.
   - This is why coverage stalled at 79.8% (63 of 87 null legs were each symbol's
     latest exit).
   - Tests: `tests/test_forward_observations_ingest.py` (+2, verified to fail
     before the fix).
3. **audit2 reproducibility** — vendored byte-identical `audit_dashboard/audit2.html`
   and `audit2.js`; added `tools/audit2_forward_summary.py` (testable
   `summarize()` + `--src/--out`); added local routes `/audit2/` and `/audit3/` in
   `tools/serve_local.py`; added resilient JSON fallback in `audit_dashboard/audit3.html`.
   - Tests: `tests/test_audit2_forward_summary.py` (5).
4. Docs: `updates/2026-11-19-*.md` (4 files).

## What is NOT fixed here (must land on `origin/main`)
1. **P0 deploy target for /audit2** — CI uploads the page to `/audit/`, where it
   404s. Fix `.github/workflows/audit-dashboard.yml:1286-1304,1418-1435,1479-1496`
   and `tools/deploy_audit_files.py:147-149` to target `/audit2/…`, and make
   `tests/test_audit2_page_deploy.py` assert the deployed URL.
2. **Forward ingest is never scheduled** — `audit3-ledger.yml:93-101` runs only
   the tribunal. Add
   `python3 -m alpha_engine.forward_observations_ingest --apply` and
   `python3 tools/audit2_forward_summary.py` before the ledger build.
3. **Backfill the 87 null benchmark legs** — append dedupe prevents `--apply`
   repair; re-collect with the padded window or add `--repair-benchmark`.
4. **/audit2 content wiring** — pods are static (`audit2.js:6-25`) and diverge
   from `reports/audit3_confirmatory.json` (3 pods); the forward clock cannot show
   `POD-EQUITY-BREAKOUT` (n=0) because it reads `audit2_forward.json` instead of
   `audit3_ledger.json.forward_gate.pods`. Footer claim at `audit2.html:112` is false.

## Testing
```
python3 -m pytest tests/test_audit3_tribunal.py tests/test_audit3_coverage_alpha.py \
  tests/test_audit3_enforcement.py tests/test_audit3_selection_alpha.py \
  tests/test_audit3_expectancy_gates.py tests/test_forward_observations.py \
  tests/test_forward_observations_ingest.py tests/test_audit2_forward_summary.py -q
# 111 passed

PORT=5199 python3 tools/serve_local.py
# /audit2/, /audit2/audit2.js, /audit2/audit3_ledger.json,
# /audit3/, /audit3/audit3_ledger.json, /audit3/audit3_evidence.json all 200
```

## Note
A peer Agent Manager session (`ses_e0b4b6439ffe565KG4zX6rMCx2`) repeatedly
requested an audit2 review; delivery failed every time with "The original Agent
Manager sender is no longer available". The full answers are in this session's
transcript and in `updates/2026-11-19-audit2-reproducibility-and-local-routes.md`.

## Commit caution (read before staging)
These untracked files are **vendored from `origin/main`** only so the fixes could
be tested in this stale worktree. They already exist on main; do not commit them
here as new files:
`alpha_engine/forward_observations.py`,
`alpha_engine/forward_observations_ingest.py`,
`tests/test_forward_observations.py`,
`tests/test_forward_observations_ingest.py`,
`audit_dashboard/audit2.html`,
`audit_dashboard/audit2.js`,
`tools/audit2_forward_summary.py`.

Commit/patch only the intended deltas:
`alpha_engine/audit3_tribunal.py`,
`tests/test_audit3_coverage_alpha.py`,
`alpha_engine/forward_observations_ingest.py` (the 2-hunk fix only),
`tests/test_forward_observations_ingest.py` (the 2 appended tests only),
`audit_dashboard/audit3.html`,
`tools/serve_local.py`,
`tools/audit2_forward_summary.py` (if main does not already carry the
`summarize()`/CLI version),
`tests/test_audit2_forward_summary.py` (new, can be committed),
and the `updates/*.md` docs.

## Detailed implementation handoff
See **`COMS/HANDOFF_witty-fight_2026-11-19T1700Z_audit2_audit3_correctness.md`**
for the per-change justification, landing procedure, verification commands,
residual backfill steps, and rollback notes. It covers **both** the `/audit2`
page/pipeline and the `/audit3` ledger/gates, and it supersedes the summary above
for anything touching `audit3_tribunal.py`, `forward_observations_ingest.py`,
`audit3.html`, and `serve_local.py`.

## Peer handoff reviewed (vanilla-handsaw, 2026-11-19)
`docs/AUDIT2_3_REVIEW_KILO_VANILLAHANDSAW_2026-11-19.md` was reviewed against the
working tree and the live ledger. Findings and required corrections are in
**`COMS/REVIEW_vanilla-handsaw_audit2_audit3_2026-11-19.md`**. Headline:
F1/F2/N1-N4/N7 are confirmed, but "86 tests" is actually **49**, "46% of book
dropped" is actually **41.2% not scored**, N5 is not published in the ledger
(`selection_alpha.available=false`, 0/7 classes have alpha), and the branch's
changes are **uncommitted** (0 ahead, 1,109 behind main).
