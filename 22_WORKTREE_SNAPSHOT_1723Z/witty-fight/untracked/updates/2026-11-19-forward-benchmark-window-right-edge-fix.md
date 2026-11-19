# Forward-ledger benchmark coverage: right-edge window bug (2026-11-19)

## Symptom
Live `audit3_ledger.json.forward_gate` shows the only populated hypothesis,
`H-119`, at:

```
n_forward = 430
net_pf    = 1.1147
pf_ci_lb  = 0.9213
ir        = 0.0429
benchmark_coverage = 0.798      # gate requires >= 0.90
```

343 of 430 rows carry a `benchmark_leg_ret`; 87 are null. This alone blocks
promotion of an otherwise-positive forward track.

## Root cause (measured)
The benchmark leg is the same symbol's direction-adjusted buy-and-hold
(`forward_observations_ingest.py:149-164`). It is resolved with `close_at()`,
which takes the **first bar at or after** the timestamp and tolerates 6h
(`:137-146`).

`collect()` builds the bar query window as `(entry, exit)` where
`exit = intrabar_resolved_at` (`:360-382`). `fetch_bars` queries with an inclusive
`BETWEEN lo AND hi` on 1h bars (`tools/stamp_entry_conditions.py:65-80`). Exits
carry seconds (e.g. `18:15:53`), so the bar that contains the exit is stamped
before it and the next bar — the one `close_at` would accept — is outside `hi`.
The 6h tolerance therefore can never be consumed at the right edge.

Evidence in the live ledger:

| Cut | Rows | Nulls | Null rate |
|---|---|---|---|
| `closed_at` == symbol max exit | 113 | 63 | 55.8% |
| any other exit | 317 | 24 | 7.6% |
| batch resolver instants 2026-06-09/10 | — | 55 of 87 | 63% |

A row only got a leg when a *later* row for the same symbol extended the cached
series past its exit, which is why the failure concentrates on each symbol's last
trade. This is not missing price data: every row passed `features()` on the same
series.

## Fix
`alpha_engine/forward_observations_ingest.py`

- New constant `BENCHMARK_LOOKAHEAD_MS = 6 * 3600_000`, also used as
  `close_at()`'s default `tol_ms`, so the query pad and the tolerance cannot
  drift.
- `collect()` pads the window upper bound:
  `max(hi, exit_ms + BENCHMARK_LOOKAHEAD_MS)`.

## Verification
```
$ python3 -m pytest tests/test_forward_observations.py \
                   tests/test_forward_observations_ingest.py -q
44 passed in 0.39s
```

Two new regression tests in `tests/test_forward_observations_ingest.py`:

- `test_fetch_window_is_padded_past_the_exit` — captures the window passed to
  `fetch_bars` and asserts `hi == exit + 6h`.
- `test_consecutive_exits_merge_the_padded_window` — two rows for one symbol keep
  the widest padded bound.

Both were confirmed to **fail before the fix** (temporary revert of the single
`max(...)` line → 2 failed) and pass after.

## Residual work (not in this change)
1. **Backfill.** `FO.append()` dedupes on deterministic ids, so `--apply` cannot
   repair the 87 existing null legs. Re-run `collect()` with the padded window and
   replace the ledger, or add a targeted `--repair-benchmark` mode that rewrites
   only `benchmark_leg_ret` on null rows.
2. **Schedule the ingest.** No workflow runs `forward_observations_ingest`
   (`.github/workflows/audit3-ledger.yml:93-101` runs only the tribunal), which is
   why `POD-EQUITY-BREAKOUT` still shows `n_forward = 0` even after its condition
   was registered.
3. Re-check the gate after backfill: H-119's CI-LB 0.9213 and IR 0.0429 are
   independent of coverage and would still fail `PF CI-LB > 1.0` / `IR >= 0.5`.
   Fixing coverage does **not** promote it.
