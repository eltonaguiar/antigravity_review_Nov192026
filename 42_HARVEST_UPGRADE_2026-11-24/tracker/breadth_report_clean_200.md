# Breadth report (200+) -- CLEAN change events only

zoo-savant, 2026-11-24. Source: `analyst_actions.csv`
(105,258 rows, 246 tickers resolved, 286 firms).
Universe: sp120.txt expanded from 155 to 253 tickers.

**Filter line:** `action IN ('up','down','init')` -- `main` (reiterated) and `reit` are EXCLUDED.

| floor | ALL rows | CLEAN changes |
|---|---|---|
| 300 | 47 | 25 |
| 500 | 46 | 15 |
| 750 | 34 | 9 |

**Firms reaching 300 / 500 / 750 clean changes: 25 / 15 / 9.**
**Best firm: Morgan Stanley with 1012 clean changes.**

## Comparison with the 155-ticker run

| floor | 155 tickers | 253 tickers |
|---|---|---|
| 300 | 14 | 25 |
| 500 | 5 | 15 |
| 750 | 0 | 9 |

## Top firms by clean changes

```
  Morgan Stanley             1012  (of 8597 rows total)
  Goldman Sachs              1004  (of 2656 rows total)
  BofA Securities             977  (of 3467 rows total)
  J.P. Morgan                 868  (of 4781 rows total)
  UBS                         837  (of 4675 rows total)
  Citi                        818  (of 5587 rows total)
  Barclays                    773  (of 6557 rows total)
  Deutsche Bank               765  (of 4012 rows total)
  Wells Fargo                 764  (of 4937 rows total)
  Jefferies                   711  (of 3020 rows total)
  Credit Suisse               639  (of 3048 rows total)
  BMO Capital Markets         554  (of 2611 rows total)
```

## Reading

Clean changes grow roughly in proportion to ticker breadth, as PREREG section 0 predicted.
At least one firm now clears 750 clean events, so the 750-event test is runnable.
Counts are per firm_norm over one Yahoo snapshot; they are not adjusted for merger eras
(see firm_aliases.csv), so a firm that absorbed another may be split across two names --
which makes these counts an UNDER-estimate for the merged entity, never an over-estimate.
