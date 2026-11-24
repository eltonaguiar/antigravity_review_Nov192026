# STEP C-NEXT — ingestion into ejaguiar1_stocks

**Run:** 2026-11-24 · **Script:** `ingest_step_c.py` · **Target:** `ejaguiar1_stocks` on
`mysql.50webs.com` (MySQL 8.4.7), credentials from `$DB_PASS_STOCKS`, connecting as user
`ejaguiar1_stocks` — the pattern already used by `check_db_v3.py` in the main repo.

## STEP DONE — row counts per table

| table | inserted | already present | table total after run |
|---|---:|---:|---:|
| `fund_lookthrough` | **6** | 0 | **6** |
| `crowd_markets` | **500** (300 then 200) | 0 | **500** |

### `fund_lookthrough` — 6 rows, `as_of` 2026-11-24

| fund | holdings | matched | weight_coverage_pct | derived_buy_side_pct | status |
|---|---:|---:|---:|---:|---|
| SPY | 505 | 70 | 60.07 | 77.35 | DERIVED_OK |
| XLK | 78 | 14 | 65.46 | 77.44 | DERIVED_OK |
| QQQ | 105 | 22 | 54.98 | 75.95 | DERIVED_OK |
| JNK | 1117 | 0 | 0.00 | NULL | NOT_APPLICABLE_BOND_FUND |
| VTI | 551 | 0 | 0.00 | NULL | BLOCKED_WRONG_SERIES |
| EEM | NULL | NULL | NULL | NULL | BLOCKED |

`weight_coverage_pct` is mandatory for derived rows and the script **aborts and rolls back** if any
row has a derived value without it. `derived_score` is NULL throughout — this agent did not compute
one and will not fill the column to look complete.

### `crowd_markets` — 500 rows

| venue | rows | with implied_prob | with spread | with volume | with open_interest |
|---|---:|---:|---:|---:|---:|
| polymarket | 100 | 100 | 76 | 100 | 0 |
| kalshi | 400 | 200 | 200 | 200 | `liquidity` 0 |

## A bug I introduced, found in verification, and fixed

The first ingestion wrote **200 Kalshi rows with every quantitative column NULL**. Cause was mine, not
the API's: Kalshi renamed its fields and my parser read the old names.

```
old name        -> new name (verified 2026-11-24)
yes_bid         -> yes_bid_dollars
yes_ask         -> yes_ask_dollars
volume          -> volume_fp
open_interest   -> open_interest_fp
```

After the fix all four fields populate 200/200. The 200 rows written before the fix are **kept, not
deleted**, and they must be excluded from any analysis requiring a price:

```sql
-- rows to exclude from quote-based analytics
SELECT COUNT(*) FROM crowd_markets WHERE venue='kalshi' AND implied_prob IS NULL;   -- 200
```

They are not duplicates: `SELECT COUNT(*) FROM crowd_markets ... market_id` returns **400 distinct
ids for 400 rows**, 0 duplicate pairs. Kalshi rotates the market set between fetches, so the second
call returned a different 200 markets. Identity and expiry are real; only the quotes are missing.

## Non-destructive by construction

- Both tables were verified **empty** before this run (`SELECT COUNT(*)` → 0), so no foreign data
  existed to lose.
- Existing rows are never overwritten. The backfill uses
  `SET col = COALESCE(col, %s)` — it fills only a column the database left NULL and cannot replace a
  value another agent wrote.
- Nothing is invented. Unmeasured fields are NULL: `derived_score`, Kalshi quotes on the pre-fix rows,
  `category`, `outcome`. `resolved = 0` on every row is a measured fact (the query filtered
  `status=open` / `closed=false`), not an assumption.

## Verify yourself

```sql
SELECT status, COUNT(*) FROM fund_lookthrough GROUP BY status ORDER BY 2 DESC;
SELECT venue, COUNT(*), SUM(implied_prob IS NOT NULL) FROM crowd_markets GROUP BY venue;
SELECT COUNT(*) FROM fund_lookthrough
 WHERE derived_buy_side_pct IS NOT NULL AND weight_coverage_pct IS NULL;   -- must be 0
```

Reproduce: `DB_PASS_STOCKS=... python3 ingest_step_c.py`. It re-runs safely; a second run inserts 0
and reports the existing rows as skipped.
