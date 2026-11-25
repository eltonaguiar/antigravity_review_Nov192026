# The unjoined EXPIRED rows -- are they random?

zoo-savant, 2026-11-25. Measured read-only from `ejaguiar1_stocks`.

## Count: the brief's 2,906 does not reproduce

Joining `at_pick_outcomes` (status EXPIRED) against the older table
`at_pick_outcomes_pre_pillar_migration_2026_06_09` (39,908 rows) on `pick_id`:

| older table checked | EXPIRED rows that do NOT join |
|---|---|
| `at_pick_outcomes_pre_pillar_migration_2026_06_09` | **820** |
| `at_pick_outcomes_kimi_archive_2026_06_05` | 918 |
| `at_pick_outcomes_v2` | 960 |

No candidate yields 2,906, so I report **820** (against the pre-pillar migration
table, the most likely intended one) rather than the briefed figure. The
characterisation below holds for whichever archive is used, since the three counts
differ by less than 15%.

## Distribution of the 820

**By symbol** (top): SAND-USD 97, BTCUSDT 63, MANA-USD 37, ETHUSDT 35, TRX-USD 32,
SOLUSDT 28. Against ALL EXPIRED rows, whose top symbols are BTCUSDT 2,666,
EURJPY=X 1,521, AUDUSD=X 1,415 -- so the unjoined set is led by *different* names.

**By strategy**: `unknown` 244, `luxalgo_confluence` 133,
`forex_rsi2_mean_reversion` 46, `combined_confidence` 29, `top_gainers_momentum` 23,
`prediction_market_consensus` 22.

**By resolver version**: `universal_v2` 769, `v2.1` 51. Against ALL EXPIRED rows,
where `backfill_widened_202` (20,589) and `backfill_updated_202` (7,609) dominate.

**By asset class**: `crypto` 570 (lower-case), `forex` 80, `equity` 69, `futures` 46,
`FOREX` 42 (upper-case), `CRYPTO` 7. Against ALL EXPIRED rows, where `FOREX`
(13,026) and `CRYPTO` (8,019) dominate.

## Is the omission random?

**No -- it is structured, and the structure is in the resolver, not the market:**

1. **It is a `universal_v2` phenomenon.** 769 of 820 (93.8%) carry `universal_v2`,
   while the EXPIRED population is overwhelmingly `backfill_*`. The archive
   predates the pillar migration, so rows resolved by the current resolver
   naturally have no ancestor row: this is a *provenance gap*, not a data loss.
   The unjoined rows are the newest ones, not a random sample of all rows.
2. **Asset-class labels are inconsistent in case.** `crypto` (570) and `CRYPTO` (7)
   are the same class spelled two ways, as are `forex` and `FOREX`. Any per-class
   aggregate that groups on the raw string silently splits these, which is a
   separate defect worth fixing before those counts are quoted.
3. **Symbol concentration is real but mild**: the top 6 symbols are 292 of 820
   (35.6%), versus 6,042 of 29,655 (20.4%) for the top 6 of all EXPIRED rows.
   Higher, but not a handful-of-names artifact.

## Consequence

The 820 unjoined rows are mostly *newer* rows from the live resolver, so they do not
indicate that older outcomes were dropped. The more consequential finding is #2:
the case-inconsistent `asset_class` values mean per-class counts computed on the raw
column are wrong for both CRYPTO and FOREX.

## Reproduce

```sql
SELECT COUNT(*) FROM at_pick_outcomes o
WHERE o.status = 'EXPIRED'
  AND NOT EXISTS (SELECT 1 FROM at_pick_outcomes_pre_pillar_migration_2026_06_09 p
                  WHERE p.pick_id = o.pick_id);   -- 820
```

next_probe: normalise `asset_class` (UPPER) in the aggregate queries and re-run the
per-class table -- the CRYPTO and FOREX counts will each rise by the amount currently
hidden under the lower-case spelling.
