# Breadth report -- CLEAN change events only

zoo-savant, 2026-11-24. Source: `analyst_actions.csv` (70,233 rows, 153 tickers, 237 firms).

**Filter line:** `action IN ('up','down','init')` -- `main` (reiterated) and `reit` are EXCLUDED,
because a reiteration is not a change of opinion.

| floor | ALL rows (incl. reiterations) | CLEAN changes only |
|---|---|---|
| 300 | 47 | 14 |
| 500 | 33 | 5 |
| 750 | 27 | 0 |

**Firms reaching 300 / 500 / 750 clean changes: 14 / 5 / 0.**
**Any firm clearing 750 clean events: NO** (best is 616 by BofA Securities).

## Top firms by clean changes

```
  BofA Securities             616  (of 2334 rows total)
  Goldman Sachs               603  (of 1724 rows total)
  Morgan Stanley              585  (of 5531 rows total)
  UBS                         531  (of 3167 rows total)
  Citi                        516  (of 3861 rows total)
  Wells Fargo                 485  (of 3205 rows total)
  Deutsche Bank               484  (of 2677 rows total)
  Barclays                    481  (of 4287 rows total)
  J.P. Morgan                 470  (of 3039 rows total)
  Jefferies                   424  (of 2016 rows total)
```

## Reading

The earlier ALL-row table overstated breadth: 47 firms reach 300 rows, but only 14 reach 300
actual changes, and NO firm reaches 750 changes. So the 30-ticker baseline's ZERO at 300 was
partly a breadth problem and partly a counting problem -- on clean events the best firm has
~616, below the 750 floor the prereg needs. Reaching 750 clean events needs a wider ticker
universe (or a different firm), not just a recount.
