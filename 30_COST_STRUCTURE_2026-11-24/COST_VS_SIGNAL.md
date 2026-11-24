# Cost structure vs signal quality — break-even analysis

Source: 44 measured cell artifacts. Round-turn cost charged in the sweep was **26bp**.

## The question

Every class loses after cost. Either the signals have no gross edge (a signal problem), or they have one that 26bp of cost eats (a cost problem). The break-even cost of a cell *is* its gross mean bp/trade, so this is answerable from data already collected.

## Result: **SIGNAL PROBLEM**

the median cell has NO gross edge at all; lowering cost cannot rescue a negative expectancy

- Median GROSS bp/trade across all cells: **-1.51**
- Cells with positive gross edge: **21/44** (48%)
- Median NET bp/trade after 26bp: **-27.51**

## Per class

| class | cells | median gross bp | % with gross > 0 | best gross bp |
|---|---:|---:|---:|---:|
| EQUITY | 6 | +5.31 | 67% | +11.14 |
| FOREX | 2 | +3.75 | 100% | +4.34 |
| COMMODITY_ETF | 5 | +3.24 | 80% | +19.15 |
| CRYPTO | 28 | -5.10 | 39% | +97.90 |
| BOND_ETF | 3 | -17.29 | 0% | -8.83 |

## The best cells and the cost they would need

| cell | n | gross bp | break-even cost | net bp at 26bp |
|---|---:|---:|---:|---:|
| `SOLUSDT/breakout/1d` | 62 | +97.90 | 97.90bp | +71.90 |
| `BTCUSDT/bb_meanrev/1d` | 58 | +76.51 | 76.51bp | +50.51 |
| `SOLUSDT/donchian/1d` | 33 | +62.41 | 62.41bp | +36.41 |
| `BTCUSDT/momentum_12_1/1w` | 34 | +41.49 | 41.49bp | +15.49 |
| `BTCUSDT/donchian/1d` | 48 | +27.66 | 27.66bp | +1.66 |

## Honest reading

A positive gross number is not an edge. It is an edge *candidate* that must still survive the paired/permutation test and DSR deflation — and every candidate in this sweep that got that far failed them. The break-even column answers a narrower and more useful question: **at what cost would this specific rule set stop losing money?**

For the cells below-zero on gross, no execution improvement helps. Those are signal problems and should be closed rather than optimised.

## Consequence

If the verdict above is SIGNAL PROBLEM, the correct action on this rule set is to stop, not to hunt for a cheaper venue. If it is COST PROBLEM, the next experiment is a fill-quality study, not another strategy.
