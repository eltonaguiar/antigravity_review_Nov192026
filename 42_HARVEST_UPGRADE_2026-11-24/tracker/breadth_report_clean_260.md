# Breadth report (260+) -- CLEAN change events only

zoo-savant, 2026-11-24. Universe: `sp260.txt` (317 tickers requested).
Tickers actually fetched: **308**. Total rows: 122,746. **Total clean rows: 28,405**
(action in up/down/init only; 291 firms).

**Filter line:** `action IN ('up','down','init')` -- `main` (reiterated) and `reit` are EXCLUDED.

| floor | ALL rows | CLEAN changes |
|---|---|---|
| 300 | 51 | 28 |
| 500 | 46 | 18 |
| 750 | 37 | 11 |

**Firms reaching 300 / 500 / 750 clean changes: 28 / 18 / 11.**
**Best firm: Goldman Sachs with 1236 clean changes.**

## Progression

| tickers | 300 | 500 | 750 | best firm (clean) |
|---|---|---|---|---|
| 153 | 14 | 5 | 0 | BofA Securities 616 |
| 246 | 25 | 15 | 9 | Morgan Stanley 1012 |
| 308 | 28 | 18 | 11 | Goldman Sachs 1236 |

The 155-ticker report (`breadth_report_clean.md`) is left untouched. The raw CSV is not committed.

## Top firms by clean changes

```
  Goldman Sachs              1236  (of 3148 rows total)
  BofA Securities            1221  (of 4047 rows total)
  Morgan Stanley             1213  (of 10095 rows total)
  J.P. Morgan                1057  (of 5585 rows total)
  UBS                        1002  (of 5435 rows total)
  Citi                        984  (of 6593 rows total)
  Barclays                    951  (of 7779 rows total)
  Wells Fargo                 944  (of 5908 rows total)
  Deutsche Bank               909  (of 4609 rows total)
  Jefferies                   844  (of 3460 rows total)
  Credit Suisse               777  (of 3463 rows total)
  Evercore ISI Group          679  (of 2515 rows total)
```
