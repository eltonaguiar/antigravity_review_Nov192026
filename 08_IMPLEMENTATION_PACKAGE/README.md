# 08_IMPLEMENTATION_PACKAGE — ready-to-adapt artifacts

Standalone reference artifacts for the next implementation phase. None of these modify the
source repo; they are the "contracts" a maintainer/agent can drop in.

### `pods/`
- `pods_pre_registered.json` — the **P1 (futures TSMOM), P2 (FX carry), P3 (PEAD)** pod
  additions to `reports/audit3_confirmatory.json`, in the exact audit3 confirmatory schema.

### `sql/`
- `forward_observations.sql` — the missing system-of-record table (schema + dedup key +
  NOT-NULL net-return trigger).
- `forward_ingest_adapter_reference.py` — reference loader for the **P0 blocker**
  (forward ledger is empty because nothing ingests from MySQL). Dry-run-safe, env-only creds.
- `benchmark_and_cost_gates.sql` — benchmark-leg table + 3× round-trip cost-gate view.

### `harness/`
- `shadow_control_harness_spec.md` — how to accrue forward rows (incl. negative controls)
  without pausing emission.

### `audit2_adoption_checklist.md`
- Checklist to make the audit2 page prototype live in the source repo.

## Suggested order
1. `sql/forward_observations.sql` → create table.
2. `sql/forward_ingest_adapter_reference.py` → wire a real MySQL read, run `ingest()`.
3. `pods/pods_pre_registered.json` → append pod P1/P2/P3 to the confirmatory manifest.
4. `harness/shadow_control_harness_spec.md` → stand up the shadow cohort.
5. `audit2_adoption_checklist.md` → publish `/audit2`.
