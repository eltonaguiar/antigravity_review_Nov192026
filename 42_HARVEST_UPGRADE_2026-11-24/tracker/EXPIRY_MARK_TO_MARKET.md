# EXPIRY_MARK_TO_MARKET — the TIME_EXPIRED branch must store a return

**Source:** `DEFECT_RESOLVER_CLASS_CONFOUND.md` (2026-11-25). **Scope:** the `TIME_EXPIRED` branch of
`at_pick_outcomes`/`trading_picks`. **Status:** specification, not an applied backfill.

## The measured defect

| resolution_method | rows | `pnl_pct = 0` | zero share |
|---|---:|---:|---:|
| **TIME_EXPIRED** | **29,505** | **28,430** | **96.4%** |
| SL_HIT | 18,534 | 0 | 0.0% |
| TP_HIT | 12,448 | 2 | 0.02% |

A pick that hit neither TP nor SL still has a return at the moment its window closed. The resolver
discarded it and wrote `0`, which is not a flat outcome; it is **missing data coded as a number**.
The defect is specific to `TIME_EXPIRED`; SL/TP rows are clean.

Live recheck at 2026-11-25T06:48Z: TIME_EXPIRED 29,506 / 28,430 zero; SL_HIT 18,537 / 0; TP_HIT
12,449 / 2 (1–3 rows of normal drift from the brief; same conclusion).

## Correct semantics

For every TIME_EXPIRED row with a valid entry:

1. **Expiry timestamp** — use `closed_at` (trading_picks) or `resolved_at` (at_pick_outcomes), whichever
   is the actual window end. Do not substitute “now” or a batch timestamp.
2. **Expiry bar** — the last bar with timestamp **<= expiry** from the point-in-time bar source for that
   symbol. No bar after expiry, no look-ahead.
3. **Exit price** — if the parent row already has a non-zero `exit_price`, use it; otherwise the expiry
   bar close. If neither exists, mark the row `UNRESOLVED_NO_BAR`; do not write 0.
4. **Direction-aware return**:
   - long: `pnl_pct = (exit / entry - 1) * 100`
   - short: `pnl_pct = (entry - exit) / entry * 100`
5. **Costs are separate.** Store the gross mark-to-market return; the cost gate subtracts its stated
   round-turn cost. Do not bake an arbitrary cost into the row.
6. **Status.** Keep `status = EXPIRED` (the window ended) but set `resolution_method = TIME_EXPIRED`,
   `exit_price`, and a non-zero/gross `pnl_pct` when the bar exists. A true flat (exit == entry) is
   allowed only when the bar exists and the price is equal; a missing bar is `UNRESOLVED_NO_BAR`.
7. **Timestamp.** Set `resolved_at` to the expiry timestamp used; never leave it NULL for a resolved
   row.

## Schema/invariant

Add a resolver-time assertion:

```
if resolution_method == 'TIME_EXPIRED':
    require exit_price is not None
    require pnl_pct is not None
    require abs(pnl_pct - computed_from(entry, exit, direction)) < tolerance
    require resolved_at is not None
else:
    require pnl_pct == 0 only if exit_price == entry_price
```

A `TIME_EXPIRED` row with `pnl_pct=0` and a non-zero `exit_price` is a **hard error**, not a neutral
outcome. This is the same denominator guard used elsewhere: fail the write instead of storing a
fabricated zero.

## Repair sequence (one writer, after approval)

1. Snapshot the affected rows; count before/after by class.
2. For TIME_EXPIRED rows with parent `exit_price`, recompute from entry/exit/direction.
3. For rows without exit, join the PIT bar at expiry; if missing, mark `UNRESOLVED_NO_BAR`.
4. Never overwrite SL_HIT/TP_HIT; never change entry, direction, or strategy.
5. Publish reconciliation counts: resolved / still no bar / true flat.
6. Re-run the cost gate and per-class stats only after the counts reconcile.

## Tests

- Synthetic long entry 100, expiry exit 104 → +4.00%, not 0.
- Synthetic short entry 100, expiry exit 96 → +4.00%, not 0.
- Entry == exit with a valid bar → 0.00% and `resolved_at` set.
- Missing expiry bar → `UNRESOLVED_NO_BAR`, not 0.
- No bar after expiry is used (no look-ahead).
- TIME_EXPIRED with exit_price 104 and pnl 0 → assertion failure.

## Expected effect

Fixing this branch recovers the **28,430** zero rows (and the 1,076 non-zero TIME_EXPIRED rows stay
untouched). Combined with the 1,664 `RESOLVE_FAILED_MAX_RETRIES` rows that have entry+exit, this is
the difference between a resolver/status bug and a data problem: the prices mostly exist, the return
was simply not written.

next_probe: implement the expiry bar lookup for the 28,430 zeros and report resolved / no-bar / true-flat
counts before any table write.
