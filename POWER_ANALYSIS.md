# Power Analysis — Per-Class MDE Table

**Gate:** SE(mean annual return) = vol / sqrt(years); t = mean / SE; significant iff |t| >= 2 (95% CI excludes 0).
**MDE at t=2:** 2 * vol / sqrt(years) — the smallest effect/yr the sample can detect.

## Per-Class MDE Table (t=2)

| Class | Sample length (yrs) | Annualised vol | MDE at t=2 (%/yr) | Smallest edge detectable |
|-------|--------------------|----------------|-------------------|--------------------------|
| equity | 10 | 0.10 | 6.32 | ~6.3%/yr |
| bond | 10 | 0.06 | 3.79 | ~3.8%/yr |
| etf | 10 | 0.10 | 6.32 | ~6.3%/yr |
| fund | 10 | 0.08 | 5.06 | ~5.1%/yr |
| crypto | 10 | 0.20 | 12.65 | ~12.6%/yr |
| fx | 10 | 0.08 | 5.06 | ~5.1%/yr |
| commodity | 10 | 0.15 | 9.49 | ~9.5%/yr |
| option | 10 | 0.20 | 12.65 | ~12.6%/yr |
| futures | 10 | 0.15 | 9.49 | ~9.5%/yr |
| prediction | 1 | 0.30 | 60.00 | ~60.0%/yr |

## How to read this

- **MDE** = Minimum Detectable Effect: any true edge smaller than the MDE will fail to clear t=2 in this sample, regardless of whether it is real.
- **equity at 10% vol, 10 years:** needs a ~6.3%/yr edge to be detectable. Academic HML is ~3-5%/yr — **invisible** in this sample.
- **crypto at 20% vol, 10 years:** needs ~12.6%/yr. Most crypto edges are below this threshold.
- **prediction at 30% vol, 1 year:** needs ~60%/yr. Effectively nothing is detectable.
- A 5-year sample at 10% vol can only see effects bigger than ~9%/yr. Everything smaller is invisible, valid or not.

## Reference: SPY power control (positive_control.py)

- Source: Yahoo monthly adjusted SPY, 406 monthly returns (~33.8 years)
- SPY annualised vol: 14.77%
- MDE at t=2: 5.08%/yr
- A 3%/yr injected alpha is NOT recovered as significant (t=1.18, CI spans 0)
- A 10%/yr injected alpha IS recovered as significant (t=3.94, CI excludes 0)

**The harness is testing the least powerful statistic available.** A cross-sectional IC test uses every name on every period (t ~ IC * sqrt(n)), delivering ~40x the power of a single equity curve.

*Paper only. Zero capital. Not investment advice.*
