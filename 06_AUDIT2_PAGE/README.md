# audit2 — page prototype

Standalone, self-contained implementation of the audit2 content spec
(`05_AUDIT2_SPEC.md`). It is a **reference implementation you can adopt**, not a change to
the source repo.

## Files

| File | What it is |
|---|---|
| `audit2.html` | Single-file page. Reads `reports/audit3_confirmatory.json` and `reports/forward_observations.jsonl` if present; otherwise renders embedded sample data. Sections: Forward Candidate Pods · Statistical Measures · Methodology · Retired-with-Reason · Benchmarks. |
| `data/confirmatory.sample.json` | Sample pod manifest (mirrors `reports/audit3_confirmatory.json` shape). |
| `data/forward.sample.jsonl` | Sample forward-ledger rows (empty by default — matches the real 0-row ledger). |

## How to adopt (in the source repo, when ready)

1. Copy `audit2.html` to the audit dashboard web root (e.g. `audit_dashboard/audit2.html`).
2. Point its two `fetch()` calls at the real feeds:
   - `reports/audit3_confirmatory.json`
   - `reports/forward_observations.jsonl`
3. Register the route `/audit2` in the deploy manifest (the `audit-dashboard.yml` per-site
   HTML lists) and `tools/deploy_audit_files.py`.
4. If no feed is present (pre-deploy), the page stays honest: it shows the static
   "0 forward rows — nothing can promote" state, which is the correct message.

## Honesty rules baked in

- No "PROVEN"/"T1"/"Renaissance" tier labels. Each pod card shows status
  (`pre_registered` / `post_hoc` / `declined`) taken straight from the manifest.
- Every candidate shows its **gate** and, when forward rows exist, excess vs the benchmark
  leg + IR. Raw PF is hidden in the headline.
- A "Retired with reason" table mirrors the copilot-style elimination record so nothing is
  silently dropped.
- The page renders a global trial counter placeholder (feeds off the forward ledger) and
  the cumulative-N DSR note.

*Not personalized investment advice.*
