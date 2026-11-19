# /audit2 reproducibility, sidecar producer, and local routes (2026-11-19)

## What was wrong
1. **The live page had no source in this branch.** `/audit2/` served 200 with
   `audit2.js` and `audit2_forward.json`, but `audit_dashboard/audit2.html` and
   `audit_dashboard/audit2.js` did not exist in the worktree.
2. **No in-repo producer for the forward sidecar.** `audit2_forward.json` was an
   externally regenerated artifact; `tools/audit2_forward_summary.py` existed only
   on `origin/main`. Three copies disagreed: repo 08:41, live 13:02,
   tdotevent.ca 09:04 (`n_rows` 8,735 vs 8,605).
3. **Local dev could not load either audit page at the live URL shape.**
   `tools/serve_local.py` only routed `/audit/`, so opening `/audit2/` or
   `/audit3/` 404'd the page and its sidecars.

## What changed
### Vendored the live page (byte-identical)
`audit_dashboard/audit2.html` (6,781 B) and `audit_dashboard/audit2.js`
(11,404 B) were fetched from `https://findtorontoevents.ca/audit2/` and verified
with SHA-256:

```
95765e6545b50911b9e5d1c0b4dc62d6886a241b14b93634198acee38c7be940  audit2.js
95765e6545b50911b9e5d1c0b4dc62d6886a241b14b93634198acee38c7be940  live response
```

### Testable sidecar producer
`tools/audit2_forward_summary.py` now exposes `summarize(src, generated_at)` and
`--src/--out` flags while keeping the repo defaults. Missing file → empty payload
(not an error), malformed lines are skipped, non-dict lines are skipped, pods are
deduped and sorted.

Tests: `tests/test_audit2_forward_summary.py` (5 passing), covering missing file,
coverage counts, hypothesis separation, malformed input, and the CLI write path.

### Local routes mirror production
`tools/serve_local.py` now serves, from the repo layout (mapping kept as
`AUDIT_LIVE_ALIASES` / `AUDIT_DIRECTORY_INDEX`, unit-tested in
`tests/test_serve_local_audit_routes.py`):

| URL | File |
|---|---|
| `/audit2/` | `audit_dashboard/audit2.html` |
| `/audit2/audit2.js` | `audit_dashboard/audit2.js` |
| `/audit2/audit2_forward.json` | `audit_dashboard/data/audit2_forward.json` |
| `/audit2/audit3_ledger.json` | `audit_dashboard/data/audit3_ledger.json` |
| `/audit3/` | `audit_dashboard/audit3.html` |
| `/audit3/audit3_ledger.json` | `audit_dashboard/data/audit3_ledger.json` |
| `/audit3/audit3_evidence.json` | `audit_dashboard/data/audit3_evidence.json` |

### Resilient ledger/evidence loading in `audit3.html`
Replaced two single-path `fetch()` calls with `fetchJsonWithFallback([...])`, which
tries `audit3_*.json`, `data/audit3_*.json`, then
`../audit/data/audit3_*.json`. A non-404 error no longer aborts the chain.

## Verification
```
$ PORT=5199 python3 tools/serve_local.py   # then:
$ for p in /audit2/ /audit2/audit2.js /audit2/audit3_ledger.json \
           /audit3/ /audit3/audit3_ledger.json /audit3/audit3_evidence.json; do
    curl -s -o /dev/null -w "%{http_code} %{size_download} %{content_type}  $p\n" \
      "http://127.0.0.1:5199$p"; done
200 6781     text/html; charset=utf-8                 /audit2/
200 11404    application/javascript; charset=utf-8    /audit2/audit2.js
200 276377   application/json; charset=utf-8          /audit2/audit3_ledger.json
200 38278    text/html; charset=utf-8                 /audit3/
200 276377   application/json; charset=utf-8          /audit3/audit3_ledger.json
200 2523018  application/json; charset=utf-8          /audit3/audit3_evidence.json
```

## Still broken on `origin/main` (this worktree cannot fix it)
The **deploy target**, not the page, is the P0 defect:
- CI uploads `audit2.html` / `audit2.js` / `audit2_forward.json` to `/audit/`
  (`.github/workflows/audit-dashboard.yml:1286-1304, 1418-1435, 1479-1496`;
  `tools/deploy_audit_files.py:147-149`).
- Those URLs return 404; the live `/audit2/` directory is not produced by the repo.
- `tests/test_audit2_page_deploy.py:29-44` only asserts the filenames occur in the
  workflow, so the dead target stays green.

Required fix on `main`: point those uploads at `/audit2/…` (or add a rewrite to
`/audit2/index.html`), add `tools/audit2_forward_summary.py` to the
audit3-ledger workflow right after the forward ingest, and change the deploy test
to fetch the deployed URLs.

## Content gaps also confirmed (not fixed here)
Pods are a static array (`audit2.js:6-25`) with five hypothesis IDs that exist only
in that file; `reports/audit3_confirmatory.json` registers three. The forward clock
fetches `audit2_forward.json` and therefore can never show a registered pod with
zero rows — `POD-EQUITY-BREAKOUT` (`n_forward: 0`) is invisible even though
`audit3_ledger.json.forward_gate.pods` already reports it.
