# UP-only MDE — the alternative to the unreachable 750 floor

**Date:** 2026-11-25. **No gate changed; no existing artifact edited.**
**Inputs:** best clean UP-only firm **BofA Securities**, 439 events after the 182-day no-prior-up/down
filter (`UP_ONLY_BREADTH.md`); horizon **21 trading days**; costs **10 / 30 / 100 bp** by ADV tercile;
design effects **1.31 (HOLD)** and **1.36 (BUY)** from `score_inversion_test.md`.

## Event set and measured SD

- Brief count: **439** clean UP-only events.
- Reconstruction: **436** events / 223 symbols; **425 usable** after price and 21-day forward coverage.
- Event return: next-session open to close at +21 trading days; benchmark SPY over the same window;
  cost by ADV tercile (tercile cutoffs measured at **$153.8M / $335.2M**).
- **Realised cross-sectional SD of 21-day net excess: 1,036.94 bp** (10.37% per event).
- Mean net excess on the same set: **−9.98 bp** (context only; not part of the MDE).

## Formula

For a two-sided 5% test (`t=2`) and event count `n`:

```
MDE_t2_iid     = 2 * SD / sqrt(n)
MDE_t2_cluster = 2 * SD * sqrt(design_effect / n)
MDE_80_iid     = 2.802 * SD / sqrt(n)
MDE_80_cluster = 2.802 * SD * sqrt(design_effect / n)
```

At 80% power the normal quantile sum is `1.96 + 0.842 = 2.802`.

## Results (n = 425)

| measure | iid | cluster DE 1.31 | cluster DE 1.36 |
|---|---:|---:|---:|
| MDE at t=2 | **100.60 bp** | **115.14 bp** | **117.32 bp** |
| MDE at 80% power | **140.94 bp** | **161.31 bp** | **164.36 bp** |

Sensitivity to the brief's full count: using n=439 with the same SD gives **98.99 bp** iid and
**115.49 bp** cluster at DE 1.36; the usable set is the defensible figure.

## Annualised figure — overlap assumption stated

21-day events **overlap**, so a naive ×17 annualisation is wrong. The only annualisation reported here
uses **non-overlapping 21-trading-day blocks** (`252/21 = 12` per year, factor `sqrt(12) = 3.464`):

| measure | iid | cluster DE 1.36 |
|---|---:|---:|
| annualised MDE from t=2 | **348.48 bp** (3.48%/yr) | **406.35 bp** (4.06%/yr) |

That annualised figure is **conditional on non-overlap** and is not valid for the overlapping event
set. With overlap, the effective independent count is lower and the honest annual MDE is larger. Do not
use the ×sqrt(12) number as the overlapping-set annual MDE.

## Reading

The 750-event floor cannot be met with the current universe (best clean firm 439). Restated as an MDE,
the UP-only test can detect roughly **101 bp/event iid** or **117 bp/event cluster-adjusted** at t=2;
at 80% power it needs **141–164 bp/event**. Any claimed UP-only edge below ~1.2% per 21-day event is
inside the noise floor of this sample. No gate was lowered.

next_probe: obtain the full 439-event price panel (not the 425 usable subset) and recompute the same SD
and MDE; until then quote the 425-event figures with the coverage note.
