# RESOLVE_FAILED_MAX_RETRIES — recompute from stored prices

**Read-only** query of `ejaguiar1_stocks`, 2026-11-25. Credentials read at runtime; never printed or committed.
No table writes. Script: `tracker/recompute_resolve_failed.py`.

```bash
python3 42_HARVEST_UPGRADE_2026-11-24/tracker/recompute_resolve_failed.py
```

## Result

| measure | value |
|---|---:|
| rows with `exit_reason='RESOLVE_FAILED_MAX_RETRIES'` | **1,664** |
| recomputed from entry/exit | **1,664** |
| skipped for missing/invalid price | **0** |
| mean return | **0.0000%** |
| median return | **0.0000%** |
| profitable (>0) | **0** |
| zero | **1,664** |
| losing (<0) | **0** |
| min / max | 0.0000% / 0.0000% |
| **exit_price == entry_price** | **1,664 / 1,664** |
| exit_price = 0 | 0 |
| directions | long 647, short 1,017 |

## Finding

Every one of the 1,664 rows has **`exit_price` exactly equal to `entry_price`**. The stored “exit” is a
copy/placeholder, not a market exit. Direction-aware return therefore computes to **0.00% for all
1,664**, and **none is profitable**. This is not a recomputable price set; copying `t.pnl_pct` would
also copy zero (as expected).

The failure is one layer deeper than “dead pnl”: **the exit price is not a resolution**. To recover these
rows, the resolver must either (a) look up the actual bar at the exit/expiry timestamp, or (b) mark them
`UNRESOLVED_NO_EXIT` rather than writing entry as the exit.

Do not quote 1,664 zeros as flat outcomes. They are missing exits coded as a number, the same defect
class as the 28,430 TIME_EXPIRED zeros.

## Recommendation

1. Stop writing `exit_price = entry_price` on resolver failure; leave exit NULL and status UNRESOLVED.
2. Resolve these 1,664 from the price bar at their expiry/exit timestamp (the same expiry-bar rule as
   `EXPIRY_MARK_TO_MARKET.md`).
3. Until then, exclude them from expectancy and win-rate denominators; they cannot contribute 0.

next_probe: join these 1,664 to a PIT bar at their expiry/closed timestamp and report resolved / no-bar,
not re-use entry as exit.
