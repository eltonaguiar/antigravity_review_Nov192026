# Implementation handoff — audit2 + audit3 correctness fixes (worktree witty-fight, 2026-11-19T17:00Z)

**Scope:** a full review of **both** `/audit2` (candidate & methodology page, its JS
and forward sidecar) and `/audit3` (kill-tribunal ledger, gates, coverage block
and summary), plus the fixes made in this worktree.
**Audience:** the engineer/agent landing these changes on `origin/main`.
**Worktree:** `witty-fight`, branch `review-investment-strategy-audits`
(base `f9e6c8202a1`, **1,063 commits behind `origin/main`** at `e48387f0fd9`).
**Status:** changes are implemented and tested here but **uncommitted**.

Read this together with:
- `updates/2026-11-19-audit3-coverage-honesty-fix.md`
- `updates/2026-11-19-forward-benchmark-window-right-edge-fix.md`
- `updates/2026-11-19-audit2-reproducibility-and-local-routes.md`
- `updates/2026-11-19-audit-vs-audit3-contradiction-reconciliation.md`
- `updates/2026-11-19-audit-surface-verification-and-stale-branch-delta.md`
- `COMS/AUDIT2_REVIEW_FOR_PEERS.md`

---

## A. audit3 review — verified live state and defects

Live `https://findtorontoevents.ca/audit3/audit3_ledger.json`
(`generated_at 2026-11-19T13:02:16Z`, source data `10:03:39Z`) parsed directly:

### A1. Verdicts (as measured)
- 8,605 of 14,632 closed picks scored (58.8%); 67 strategy cells tested of 359.
- **0 PROVEN, 0 CANDIDATE, 59 WEAK, 8 KILL, 292 INSUFFICIENT.**
- 3 asset classes KILL (CRYPTO, COMMODITY, BOND); 10 symbol cells killed.
- Forward gate enforced; `reports/forward_observations.jsonl` has 430 rows, all H-119.

### A2. Defects found
1. **Impossible ratio.** `scored_rows 8605` vs `valid_closed_picks 8175` published
   `scored_share_of_valid_pct 105.26`, with 430 rows unaccounted between
   `total − valid` (6,457) and `unscored_rows` (6,027). **Fixed** here.
2. **False exclusion claim.** Auto-expired rows were described as "dropped before
   scoring and never counted", while the canonical book retains timeout/flat exits
   (`zero_pnl_count 134`; `status: FLAT` present). **Fixed** here (mode-aware wording).
3. **Candidate KPI contradicts the symbol table.** `summary.n_candidate = 0` while
   `symbols` carries `FOREX AUDJPY LONG, n=31, WR 0.8065, PF 8.6353,
   CI [0.5044, 1.0009], q=0.034, verdict CANDIDATE`. The summary counted strategy
   cells only. **Fixed** here (`n_candidate_symbols`, `n_candidate_segments`).
4. **Forward coverage 79.8%.** 87 of 430 rows have a null `benchmark_leg_ret`,
   below the 0.90 gate. Root cause is the right-edge query window, not missing
   data: 63 of 87 nulls sit at each symbol's latest exit (55.8% vs 7.6%).
   **Fixed** here in `forward_observations_ingest.collect()`.
5. **Not promotable even after the fix.** H-119 also fails `pf_ci_lb 0.9213 <= 1.0`
   and `IR 0.043 < 0.5`. Coverage is one of three independent failures.
6. **Cross-surface denominators differ.** `/audit` 16,341 total / 7,909 valid /
   8,735 resolved with 826 unlabelled rows; audit3 14,632 / 8,175 / 8,605. Two
   canonical hashes (`aa7f7f89…` vs `4f635550…`). audit3's 430 is now labelled;
   `/audit`'s 826 is **still unlabelled on main** (out of scope here).
7. **`/audit` confidence claim has four values on one page** (14.4 / 47 / 22.2 /
   40% WR for `conf>=0.90`). audit3 does not score confidence at all, so nothing
   arbitrates it. **Not fixed** (main-branch scoring work).

### A3. Evidence commands
```
curl -sL https://findtorontoevents.ca/audit3/audit3_ledger.json -o /tmp/kilo/live/audit3_ledger.json
python3 - <<'PY'
import json; d=json.load(open('/tmp/kilo/live/audit3_ledger.json'))
print(d['summary']); print(d['coverage']['denominator']); print(d['forward_gate']['enforced'])
print([s for s in d['symbols'] if s['verdict']=='CANDIDATE'])
PY
```

---

## B. audit2 review — verified live state and defects

Live `https://findtorontoevents.ca/audit2/` returns 200 with `audit2.js`
(11,404 B) and `audit2_forward.json` (185 B, `generated_at 13:02:15Z`, `n_rows 430`).
`audit_dashboard/audit2.html` and `.js` did not exist in this branch; they were
vendored byte-identically (JS SHA-256
`95765e65…7be940` matches live). Defects:

1. **P0 deploy target dead.** CI uploads to `/audit/` (404); live page is `/audit2/`
   (200). Refs: `.github/workflows/audit-dashboard.yml:1286-1304,1418-1435,1479-1496`;
   `tools/deploy_audit_files.py:147-149`.
2. **P0 false-green test.** `tests/test_audit2_page_deploy.py:29-44` asserts
   filenames appear in the workflow, not that the URL resolves.
3. **P0 false data-source claim.** `audit2.html:112` says every number comes from
   `audit3_ledger.json`; the forward clock reads `audit2_forward.json`
   (`audit2.js:155`), and 7 of 9 sections are static arrays (`audit2.js:6-70`).
4. **P1 pods not connected.** Six pods hardcoded at `audit2.js:6-25`, including
   `H-2026-11-19-01..05` that exist nowhere else; `reports/audit3_confirmatory.json`
   has three. `ledger.forward_gate.pods` is never read.
5. **P1 zero-row pod invisible.** `POD-EQUITY-BREAKOUT` (`n_forward: 0`) cannot
   appear because the clock is built from the sidecar, not the ledger.
6. **P1 sidecar drift.** Repo 08:41, live 13:02, tdotevent 09:04 (`n_rows` 8,735
   vs 8,605). No scheduled producer on the branch.
7. **P2** first ledger path always 404s (`audit2.js:138`); cost figures
   (`audit2.html:88`) are prose; `POD-LUXALGO-SHORT` mislabelled "Retired" though
   the manifest says `post_hoc`; no nav links.

What is correct: the verdict table and forward-gate numbers match the live ledger
exactly.

---

## C. Non-negotiable context

The working tree is stale. Several files required for testing were **vendored from
`origin/main`** and must **not** be committed here as new files:

`alpha_engine/forward_observations.py`,
`alpha_engine/forward_observations_ingest.py`,
`tests/test_forward_observations.py`,
`tests/test_forward_observations_ingest.py`,
`audit_dashboard/audit2.html`,
`audit_dashboard/audit2.js`,
`tools/audit2_forward_summary.py`.

They already exist on `main`. The correct landing procedure is to re-apply the
deltas below to `main`, not to merge this branch as a whole.

---

## 1. audit3 coverage honesty
**File:** `alpha_engine/audit3_tribunal.py`
**Functions:** `_coverage_statement()` (~line 441), `payload_coverage()` (~line 466),
`build_report()` summary (~line 1202).

### Change 1a — withhold impossible percentages
`scored_share_of_valid_pct` was published as **105.26** because the live ledger
scores 8,605 canonical rows against a dashboard `valid_closed_picks` of 8,175.
A percentage above 100 is not a measurement; it is proof the two denominators
disagree.

What we do now:
- `scored_share_of_valid_pct = None` when `scored > valid`;
- `scored_share_of_valid_pct_raw` keeps the raw 105.26 for auditors;
- `valid_denominator_inconsistent = True`;
- `denominator_reconciliation` reports `canonical_rows`,
  `dashboard_valid_closed_picks`, `delta`, `scored_but_not_dashboard_valid`,
  `consistent`, `note`.

**Why this shape:** nulling the headline stops a reader (or a downstream script)
from treating 105% as a quantity, while the raw value and the 430-row bucket
preserve the information instead of hiding it. Deleting the field would break
consumers; redefining `valid_closed_picks` inside the tribunal would fork the
dashboard's definition.

**Justification (evidence):** live `audit3_ledger.json`
`coverage.scored_rows=8605`, `valid_closed_picks=8175`, published
`scored_share_of_valid_pct=105.26`; `14632 − 8175 = 6457` while
`unscored_rows = 6027`, a 430-row hole exactly equal to `8605 − 8175`.

### Change 1b — stop claiming auto-expired rows are never scored
The cohort reason said timeouts are "dropped before scoring and never counted",
but the canonical book retains timeout/flat exits (`zero_pnl_count = 134` in the
live payload; `status: FLAT` in the canonical rows). The wording is now
mode-aware:
- canonical mode: timeouts that survive integrity checks are **retained at their
  resolved exit**, and the zero-P&L count is cited;
- payload-slice mode: the strict original wording is kept.

**Why mode-aware:** the two paths genuinely differ. Rewriting both to the softer
claim would make the payload-slice path understate its exclusions.

### Change 1c — candidate counters must match their own tables
Live contradiction (verified by parsing the ledger):
`summary.n_candidate = 0` while `symbols` contains
`FOREX AUDJPY LONG, n=31, WR 0.8065, PF 8.6353, net CI [0.5044, 1.0009], q=0.034,
verdict CANDIDATE`.
Cause: the summary counted strategy cells only and published no symbol/segment
counters.

Added `n_candidate_symbols` and `n_candidate_segments`, each computed from its
own table. **Why not rename `n_candidate`:** existing readers and the `/audit3`
KPI bind to it; changing its meaning silently would be worse than adding explicit
siblings.

The page half is also done: `audit_dashboard/audit3.html` now labels the KPI
**"Candidate cells"** and adds **"Candidate symbols"** from
`summary.n_candidate_symbols` (shows `—` on older ledgers). Without this the
number existed in JSON but the visible contradiction remained.

**Verify:**
```
python3 -m pytest tests/test_audit3_tribunal.py tests/test_audit3_coverage_alpha.py \
  tests/test_audit3_enforcement.py tests/test_audit3_selection_alpha.py \
  tests/test_audit3_expectancy_gates.py -q      # 57 passed
```
Regression tests (in `tests/test_audit3_coverage_alpha.py`):
- `test_scored_rows_above_valid_never_publish_over_100_pct`
- `test_auto_expired_wording_matches_canonical_reality`
- `test_payload_slice_mode_keeps_strict_auto_expired_wording`
- `test_summary_candidate_counts_match_each_table`

---

## 2. Forward benchmark coverage: right-edge window bug
**File:** `alpha_engine/forward_observations_ingest.py`
**Sites:** constant block (~line 59), `close_at()` default (~line 140),
`collect()` window build (~line 384).

### The bug
`benchmark_leg()` is the same symbol's direction-adjusted buy-and-hold, resolved
by `close_at(series, ts)`, which takes the **first bar at or after** `ts` and
tolerates 6h. `collect()` built the bar query window as `(entry, exit)` with
`exit = intrabar_resolved_at`; `fetch_bars` queries `BETWEEN lo AND hi` on 1h
bars. Exits carry seconds, so the settling bar is after `hi` and is never
fetched. The tolerance can never be consumed.

Measured signature in the live ledger: 63/113 nulls at each symbol's **latest**
exit (55.8%) vs 24/317 elsewhere (7.6%); 55 of 87 nulls on two batch-resolution
instants. Total coverage 343/430 = 79.8%, below the 90% promotion gate.

### The fix
- `BENCHMARK_LOOKAHEAD_MS = 6 * 3600_000`, used as `close_at()`'s default so the
  query pad and the tolerance cannot drift.
- `collect()` now requests `max(hi, exit_ms + BENCHMARK_LOOKAHEAD_MS)`.

**Why pad rather than backfill:** the bars already exist and every row passed
`features()` on the same series; this is a query-window defect, not missing data
or a symbol-mapping gap. Extending the window fixes future rows at the source.
**Why not change `fetch_bars` semantics:** it is shared; an exclusive/inclusive
change could affect other callers.

**Verify:**
```
python3 -m pytest tests/test_forward_observations.py \
                   tests/test_forward_observations_ingest.py -q   # 44 passed
```
New tests `test_fetch_window_is_padded_past_the_exit` and
`test_consecutive_exits_merge_the_padded_window` were confirmed to **fail** when
the single `max(...)` change is reverted.

### Residual (do these on main, in order)
1. **Backfill the 87 null legs.** `FO.append()` dedupes deterministic ids, so
   `--apply` cannot repair them. Either re-run `collect()` with the padded window
   and replace `reports/forward_observations.jsonl`, or add a
   `--repair-benchmark` mode that rewrites only `benchmark_leg_ret` on rows where
   it is null. Keep the pre-repair file for audit.
2. **Schedule the ingest.** No workflow runs
   `alpha_engine.forward_observations_ingest`; `.github/workflows/audit3-ledger.yml`
   (~93-101) only runs the tribunal. That is why `POD-EQUITY-BREAKOUT` still shows
   `n_forward: 0` after its condition was registered.
3. **Do not expect promotion.** H-119 also fails `pf_ci_lb 0.9213 <= 1.0` and
   `IR 0.043 < 0.5`. Coverage is one of three failures; fixing it does not make
   the strategy promotable.

---

## 3. audit2 reproducibility + local routes
### 3a. Vendor the live page (done here, already on main)
`audit_dashboard/audit2.html` (6,781 B) and `audit_dashboard/audit2.js`
(11,404 B) were fetched from `https://findtorontoevents.ca/audit2/`; the JS
SHA-256 matches the live response
(`95765e6545b50911b9e5d1c0b4dc62d6886a241b14b93634198acee38c7be940`).

### 3b. Make the sidecar producer testable
`tools/audit2_forward_summary.py` gained `summarize(src, generated_at)` and
`--src/--out`. Missing file → empty payload (not an error); malformed and
non-dict lines are skipped; pods are deduped and sorted.

**Why:** the checked-in `audit2_forward.json` was stale (08:41) versus live
(13:02) and tdotevent (09:04, 8,735 vs 8,605 rows), and there was no way to test
the aggregation without touching the real ledger.

**Verify:** `python3 -m pytest tests/test_audit2_forward_summary.py -q` → 5 passed.

### 3c. Local routes mirror production
`tools/serve_local.py` now serves `/audit2/` and `/audit3/` with the sidecars in
the same directory, matching the FTP layout. The mapping is a module-level
`AUDIT_LIVE_ALIASES` / `AUDIT_DIRECTORY_INDEX` pair so it is unit-tested rather
than living inline in the request handler
(`tests/test_serve_local_audit_routes.py`, 4 tests: directory URLs resolve,
every sidecar the pages fetch is mapped, targets exist or are the known-absent
forward sidecar, and no target escapes audit_dashboard/). Verified:
```
/audit2/                    200  6781    text/html
/audit2/audit2.js           200  11404   application/javascript
/audit2/audit3_ledger.json  200  276377  application/json
/audit3/                    200  38278   text/html
/audit3/audit3_ledger.json  200  276377  application/json
/audit3/audit3_evidence.json 200 2523018 application/json
```
**Why route-level, not a rewrite in the page alone:** the live behaviour is
directory-based, so local dev should reproduce it rather than special-case it.

### 3d. Resilient sidecar loading
`audit_dashboard/audit3.html` now uses `fetchJsonWithFallback([...])` and tries
`audit3_*.json`, `data/audit3_*.json`, then `../audit/data/audit3_*.json`. A
non-404 error no longer aborts the chain.

**Why:** local static serving and the historical `/audit/` layout both put the
sidecars elsewhere; the page previously showed "Ledger unavailable" for a path
problem. The first path is unchanged, so live behaviour is identical.

---

## 4. audit2 defects that are **not** fixed here (main-branch work)
These are documented, with refs, in `COMS/AUDIT2_REVIEW_FOR_PEERS.md`. Summary:

1. **P0 deploy target is dead.** CI uploads `audit2` to `/audit/` (404); the live
   page is `/audit2/` (200). Refs:
   `.github/workflows/audit-dashboard.yml:1286-1304,1418-1435,1479-1496`;
   `tools/deploy_audit_files.py:147-149`.
2. **P0 false-green test.** `tests/test_audit2_page_deploy.py:29-44` asserts
   filenames appear in the workflow, not that the URL resolves.
3. **P1 pods are static.** `audit2.js:6-25` lists six pods, including
   `H-2026-11-19-01..05` that exist nowhere else; `audit3_confirmatory.json` has
   three. Pods are not joined to `ledger.forward_gate`.
4. **P1 zero-row pods are invisible.** The clock reads `audit2_forward.json`, so
   `POD-EQUITY-BREAKOUT` (`n_forward: 0`) can never appear.
5. **P1 sidecar drift.** Three versions (repo 08:41, live 13:02, tdotevent 09:04).
6. **P2** first ledger path always 404s (`audit2.js:138`); footer claim at
   `audit2.html:112` is false; cost figures at `audit2.html:88` are prose;
   `POD-LUXALGO-SHORT` is mislabelled "Retired" though the manifest says
   `post_hoc`; no nav links.

**Recommended order:** fix deploy + test (1,2), then render pods from a
web-served confirmatory sidecar and show zero-row pods from
`ledger.forward_gate.pods` (3,4), then generate the sidecar in CI (5), then the
footer/cost literals (6).

---

## 5. Landing procedure

1. Branch from current `origin/main`.
2. Re-apply **only** these deltas:
   - `alpha_engine/audit3_tribunal.py` — hunks in `_coverage_statement`,
     `payload_coverage`, summary.
   - `tests/test_audit3_coverage_alpha.py` — four appended tests.
   - `alpha_engine/forward_observations_ingest.py` — constant + default + window
     pad (three hunks).
   - `tests/test_forward_observations_ingest.py` — two appended tests.
   - `audit_dashboard/audit3.html` — fetch fallback (one hunk).
   - `tools/serve_local.py` — `/audit2` + `/audit3` route block.
   - `tools/audit2_forward_summary.py` — `summarize()`/CLI version.
   - `tests/test_audit2_forward_summary.py` — new file.
   - `tests/test_serve_local_audit_routes.py` — new file.
   - `tools/serve_local.py` — alias constants + route test support.
   - `updates/2026-11-19-*.md` — documentation.
3. Do **not** add the vendored files listed in §0.
4. Run the nine test files (§6). Expect 111 passed.
5. Smoke-test the routes with `PORT=5199 python3 tools/serve_local.py` (§3c).
6. Only then touch CI: deploy target, forward ingest step, sidecar generation.

## 6. Full verification command
```
python3 -m pytest \
  tests/test_audit3_tribunal.py \
  tests/test_audit3_coverage_alpha.py \
  tests/test_audit3_enforcement.py \
  tests/test_audit3_selection_alpha.py \
  tests/test_audit3_expectancy_gates.py \
  tests/test_forward_observations.py \
  tests/test_forward_observations_ingest.py \
  tests/test_audit2_forward_summary.py \
  tests/test_serve_local_audit_routes.py -q
# 111 passed in ~7s
```

## 7. Risk and rollback
- **Coverage fields** are additive except `scored_share_of_valid_pct` becoming
  `None` in the inconsistent case. Any consumer that formats it as a number must
  handle null. Search before landing: `scored_share_of_valid_pct`.
- **Summary additions** are additive and safe.
- **Window pad** widens queries by 6h per symbol chunk. Worst case adds a handful
  of bars per symbol; `CHUNK=400` and `LIMIT 8000` bound it.
- **Fetch fallback** keeps the original first path; live behaviour unchanged.
- **Routes** are local-dev only; production deploy is untouched.
- Rollback for each is a single-file revert; no data migration is introduced by
  these changes (the backfill in §2 is separate and should keep a copy).
