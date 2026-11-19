# audit2 adoption checklist

Steps to make the audit2 page (prototype in `06_AUDIT2_PAGE/audit2.html`) live in the
source repo. These are source-repo changes **proposed** here, not yet applied.

## Prereqs
- [ ] `audit2.html` copied into the audit dashboard web root (`audit_dashboard/audit2.html`).
- [ ] Feed wiring: point its two `fetch()` calls at the real files
      - `reports/audit3_confirmatory.json`
      - `reports/forward_observations.jsonl`
- [ ] Confirm the forward ledger exists (even if 0 rows) so the page renders the honest
      "0 forward rows — nothing can promote" state.

## Route / deploy
- [ ] Register the `/audit2` route in the deploy manifest's per-site HTML page lists
      (`.github/workflows/audit-dashboard.yml`).
- [ ] Add `audit_dashboard/audit2.html` to `tools/deploy_audit_files.py`'s file glob.
- [ ] (Optional) add a `data/` sidecar dir for live feeds on the live site.

## Honesty / correctness
- [ ] Ensure no "PROVEN"/"T1"/"Renaissance" tier labels (the spec forbids them).
- [ ] Confirm candidate cards read status from the manifest (`pre_registered/post_hoc/declined`).
- [ ] Confirm every card shows its gate + (when forward rows exist) excess vs benchmark leg.
- [ ] Confirm the "Retired with reason" table is fed by a real elimination record.

## Source of truth
- [ ] Point the page at `reports/audit3_confirmatory.json` as the single source of
      registered pods (it is already).
- [ ] Wire `n_forward` + control CI from the shadow harness into the page so the
      trial counter and the "is anything accruing" question are visible.

## QA
- [ ] Load the page with live feeds; verify all four sections render.
- [ ] Verify "0 forward rows" state renders without JS errors.
- [ ] Run the existing audit dashboard Playwright specs (page load) against `/audit2`.
