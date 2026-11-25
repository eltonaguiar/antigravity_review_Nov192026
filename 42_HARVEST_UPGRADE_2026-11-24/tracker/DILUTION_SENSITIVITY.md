# Dilution sensitivity — a bound, not a headline

**Read-only** query of `ejaguiar1_stocks.at_pick_outcomes`, 2026-11-25. Credentials read at runtime; never printed or committed.

**Formula (sensitivity only):** `implied_mean = published_mean / priced_share`, where `priced_share = priced rows / all rows` and `priced` means `pnl_pct != 0`.

**Do not use this as a corrected estimate.** It assumes missing-at-random. The unjoined EXPIRED rows average **−0.0828** versus **−0.0435** for joined rows, so missingness is not random and the implied column is a **directional bound on distortion**, not a replacement mean. No class ranking or verdict should be based on it.

## Per-class sensitivity

| class | n | priced | priced share | published mean % | **implied mean % (BOUND ON DISTORTION)** |
|---|---:|---:|---:|---:|---:|
| CRYPTO | 38,218 | 29,572 | 77.38% | +0.0285% | **+0.0368%** |
| FOREX | 16,039 | 2,947 | 18.37% | +0.0563% | **+0.3066%** |
| COMMODITY | 5,882 | 922 | 15.67% | -0.1032% | **-0.6583%** |
| EQUITY | 1,984 | 244 | 12.30% | -0.0884% | **-0.7184%** |
| FUTURES | 473 | 33 | 6.98% | +0.0684% | **+0.9803%** |
| INDEX | 314 | 3 | 0.96% | +0.0005% | **+0.0537%** |
| ETF | 181 | 29 | 16.02% | +0.0588% | **+0.3672%** |
| BOND | 154 | 16 | 10.39% | +0.0219% | **+0.2103%** |
| MEME | 106 | 75 | 70.75% | -2.0079% | **-2.8379%** |
| UNKNOWN | 141 | 141 | 100.00% | -2.0210% | **-2.0210%** |

## What the sensitivity says

- The published spread is compressed by low priced coverage: FOREX **18.37%** and COMMODITY **15.67%** priced; EQUITY **12.30%**; CRYPTO **77.38%**.
- Dividing by priced share moves FOREX from +0.0563% to +0.3066% and COMMODITY from −0.1032% to −0.6583%; these are the largest distortions, and both are on tiny priced bases.
- INDEX (3 priced), BOND (16), FUTURES (33), ETF (29) are so thin that the implied figure is a mathematical artifact, not a measurement.
- The overall book conclusion does **not** change: the priced-only resolved set is still **+6.35 bp mean / −39.00 bp median** against a 26 bp cost. The sensitivity only shows how much the class ordering can move under MAR; it does not repair the missingness.

## Explicit non-use

This table is **not** a headline, **not** a correction, and **not** a ranking. It is a boundary: if missing rows were MAR, the implied means are what the published means would scale toward; because the unjoined rows are more negative, that assumption is false. The correct repair remains resolving the missing rows from prices, not dividing by coverage.

next_probe: resolve the EXPIRED rows from expiry bars, then recompute published and implied means from the completed table; do not quote this bound as an estimate.
