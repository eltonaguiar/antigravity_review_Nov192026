# CRYPTO backfill reconciliation — 33.3% vs 77.8%

**Kilo · 2026-11-25 · read-only measurement.** Resolves the apparent contradiction on
`docs/changelog-2026-11-24.html`: CRYPTO is reported as 33.3% backfilled in one place and
77.8% in another. Both figures are correct. They divide the same **12,730** backfilled rows by
different denominators. The 77.8% is **not** a share of all CRYPTO rows; it is a share of the
rows stored with the exact uppercase label `CRYPTO`.

## The two denominators

| reported | numerator | denominator | share | what the denominator is |
|---|---:|---:|---:|---|
| **33.3%** | 12,730 | **38,218** | 33.3% | every row whose `asset_class` is CRYPTO under the column's `utf8mb4_unicode_ci` (case-insensitive) collation |
| **77.8%** | 12,730 | **16,360** | 77.8% | only rows stored with the exact uppercase string `CRYPTO`, under a case-sensitive (`BINARY`) grouping |
| **58.2%** | 37,115 | **63,792** | 58.2% | every row in `at_pick_outcomes`, all classes, at the audit snapshot |

The 16,360 is a **storage-case subset**, not a class total. Because `asset_class` is
case-insensitive, `GROUP BY asset_class` already merges `crypto` and `CRYPTO`; the 38,218
figure is the class total, and 16,360 is only the uppercase-spelled part of it.

## Decomposition that makes both figures true

| stored label (case-sensitive) | rows | backfilled | live |
|---|---:|---:|---:|
| `CRYPTO` (uppercase) | 16,360 | 12,730 | 3,630 |
| `crypto` (lowercase) | 21,858 | 0 | 21,858 |
| **all CRYPTO (case-insensitive)** | **38,218** | **12,730** | **25,488** |

All 12,730 backfilled CRYPTO rows are in the uppercase subset; every lowercase row is live.
That is why the same numerator is **77.8% of 16,360** and **33.3% of 38,218**. The two
percentages answer different questions, and neither replaces the other.

The audit file `DEFECT_RESOLVER_CLASS_CONFOUND.md` uses a 5-row-earlier snapshot:
38,213 CRYPTO rows, 25,483 live, and the same 12,730 backfilled rows. That also gives
**33.3%** (12,730 / 38,213); the 5-row drift changes no one-decimal figure and is not a
second correction.

## The 58.2% overall figure — same check

- **37,115 / 63,792 = 58.2%** of **all rows in `at_pick_outcomes`**, all classes.
- The coverage table reports 63,797 raw rows: **37,115 / 63,797 = 58.18%**, also **58.2%**
  to one decimal. The 5-row total drift does not change the published figure.
- It is **not** a share of CRYPTO (that is 12,730 / 38,218 = 33.3%) and **not** a share of
  live rows (live rows are the complement, 26,682 / 63,797 = 41.8%).
- A read-only recheck on 2026-11-25 found 63,818 total rows; **37,115 / 63,818 = 58.16%**,
  still **58.2%** to one decimal. The denominator is the whole table, and it is named here.

## Reproduce (read-only)

```sql
-- Case-sensitive split: the 77.8% denominator is the uppercase subset only.
SELECT BINARY asset_class AS stored_label,
       COUNT(*) AS n,
       SUM(resolver_version LIKE 'backfill%') AS backfilled
FROM at_pick_outcomes
WHERE asset_class = 'CRYPTO'
GROUP BY BINARY asset_class;

-- All-table denominator for the 58.2% figure.
SELECT COUNT(*) AS all_rows,
       SUM(resolver_version LIKE 'backfill%') AS all_backfilled
FROM at_pick_outcomes;
```

## Verdict

- **33.3%** = 12,730 backfilled / **38,218 all CRYPTO rows** (case-insensitive class).
- **77.8%** = 12,730 backfilled / **16,360 rows stored exactly as uppercase `CRYPTO`**
  (case-sensitive storage subset). This is the figure that was right on its own denominator
  and is retained.
- **58.2%** = 37,115 backfilled / **63,792 all rows** (whole table).
- No figure is deleted; the page now names the denominator next to each one.
