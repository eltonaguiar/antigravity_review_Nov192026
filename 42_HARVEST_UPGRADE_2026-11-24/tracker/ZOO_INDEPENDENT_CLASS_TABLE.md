# ZOO independent per-class table -- live-resolver rows only

zoo-savant, 2026-11-25. Computed directly from `ejaguiar1_stocks.at_pick_outcomes` (read-only),
**before** reading Kilo's table, as instructed.

## What 'live-resolver' means here

The table has a `resolver_version` column with 7 distinct values:

```
backfill_2026-06-01, backfill_updated_202, backfill_widened_202,
signflip_purge_20260, universal_v2, v2.1, v2.2_sync_2026-06-05
```

The `backfill_*` values are re-labelling passes, so the restriction used here is
**`resolver_version = 'universal_v2'`** -- the largest genuine resolver
(13,012 LOST + 8,256 WON + 1,017 EXPIRED = 22,285 rows, of which 21,268 are resolved).
If the intended definition is different, only the WHERE clause changes; every figure
below is reproducible from the SQL stated at the end.

## Table (universal_v2 rows)

| class | rows | resolved | win rate | mean pnl % | median pnl % |
|---|---|---|---|---|---|
| BOND | 3 | 0 | -- | -- | -- |
| CRYPTO | 21,858 | 21,141 | 0.388 | +0.1681 | -1.3100 |
| EQUITY | 180 | 103 | 0.340 | -0.1006 | -2.0000 |
| FOREX | 175 | 1 | 1.000 | +3.0000 | +3.0000 |
| FUTURES | 69 | 23 | 0.435 | +0.3913 | -2.0000 |

## What it shows

- **CRYPTO dominates**: 21,858 of 22,285 rows (98.1%),
  win rate 0.388, mean +0.1681% but median -1.3100% --
  a positive mean with a negative median means a few large winners carry it, so the mean alone is misleading.
- **EQUITY** is negative on both (-0.1006% mean, -2.0000% median) over 103 resolved.
- **FOREX** has 175 rows but only 1 resolved, so its 100% win rate is one observation, not a result.
- **BOND** has 3 rows and none resolved; FUTURES has 23 resolved.

## Comparison with Kilo's table

**Not possible in this round**: `CLASS_COVERAGE_TABLE.md` is not on `origin/main` (checked with
`git ls-tree -r origin/main`), so there was nothing to compare against. When it lands, the
comparison to make is per class: rows, resolved count, and win rate -- a difference in any of
them means one of us used a different resolver restriction or a different denominator.

## Reproduce

```sql
SELECT asset_class, status, pnl_pct FROM at_pick_outcomes WHERE resolver_version = 'universal_v2';
```

next_probe: when CLASS_COVERAGE_TABLE.md lands, diff the three per-class counts (rows, resolved,
win rate) and name the resolver restriction each table used -- the only way two per-class tables
can disagree while both being right.
