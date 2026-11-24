# Canonical trial ledger (append-only JSONL)

- `trials_union.jsonl` — 19 disjoint trials, unioned on `trial_id` from the three forked
  `trial_ledger.db` copies (11 + 6 + 2 rows).
- sha256: `225c72d1d3328b996548ebcd420a44ac8fcb1e0fce97d1de7c7bf2bbf71adc14`
- Fields: `family, kept, run_id, sharpe_is, sharpe_oos, source_file, trial_id, ts_logged, variant`.

This is the canonical path for readers. The sqlite copies remain until the owner deletes them;
do not append to any sqlite file. Append-only: never edit or remove a row.

The earlier hash `66c09887` referred to the pre-provenance-emit version and is stale.
