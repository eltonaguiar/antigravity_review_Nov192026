# Deployed site vs origin -- per-class number audit

zoo-savant, 2026-11-25. Pages fetched live (all HTTP 200): `asset-class-ranking.html`,
`harvest.html`, `harvest-zoo.html`, `best-picks.html`, and the index. Compared against the
tracker artifacts on `origin/main`. **The site was not edited.**

## 1. asset-class-ranking.html -- per-class verdicts and numbers

| class | site verdict | site number | origin value | verdict |
|---|---|---|---|---|
| CRYPTO | KILL | WR 35.8%, PF 0.917, n=3,726 | cost gate (resolved rows): CRYPTO mean +8.85 bp, median **-100.00 bp**, n=28,677 | **CONTRADICTION in level** (see below) |
| COMMODITY | KILL | -2.9619 net expectancy/trade, n=50, CI [-5.004, -1.338] | cost gate: COMMODITY mean **-70.11 bp**, median -13.08, n=891 | MATCH in sign and magnitude class |
| EQUITY | WEAK | selection alpha **+0.1058**, n=956, CI [-0.480, +0.693] | class_calibration: **rho -0.04673**, p 0.9995, n=963, 485 symbols, buckets SB 1.2818 / BUY 1.6708 / HOLD 2.8798 / SELL -0.5222 | **DIFFERENT QUANTITY** -- not comparable |
| ETF | WEAK | -0.0062, n=590, CI [-0.437, +0.433] | cost gate: ETF mean +27.07 bp, median **-291.91 bp**, n=23 | **CONTRADICTION in n** (590 vs 23) |
| FOREX | WEAK | -0.0447, n=264, CI [-0.169, +0.078]; "0 of 35 cells" | cost gate: FOREX mean +32.45 bp, median -0.69, n=2,789 | **CONTRADICTION in n and sign** |
| BOND | WEAK | -0.0978, n=37, CI [-0.339, +0.169]; constant-duration test +84 bp/yr at Sharpe 0.13, -91.58 bp at real cost | cost gate: BOND mean +21.03 bp, median -58.31, n=16 | **CONTRADICTION in n** (37 vs 16) |
| FUTURES | INSUFFICIENT_N | n=4 | cost gate: FUTURES n=29, mean +275.48 bp | **CONTRADICTION in n** (4 vs 29) |

### What the contradictions actually mean

Most are **not** the site being wrong about the same quantity -- they are the site and the tracker
measuring **different populations**, and the page never says so:

- The site's n values (3,726 / 590 / 264 / 37 / 4) are its own per-class samples from a different
  pipeline; the tracker's cost gate uses resolved `at_pick_outcomes` rows (28,677 / 23 / 2,789 /
  16 / 29). Different denominators, same class names.
- The **CRYPTO level** is the sharpest case: the site reports a negative aggregate (WR 35.8%,
  PF 0.917) while the origin table has a **positive mean (+8.85 bp) and a median of -100 bp**.
  Both can be true -- the mean is carried by a few large winners -- but a reader comparing them
  sees a flat contradiction. **The site's negative reading is the honest one for a typical trade;
  the origin mean is the misleading summary.**
- **EQUITY** is the clearest "not comparable": selection alpha (+0.1058, n=956) and rank
  correlation (rho -0.04673, n=963) are different statistics on overlapping but not identical
  samples. Neither contradicts the other, and the site's WEAK verdict is consistent with origin's
  inverted, non-monotone buckets.

## 2. harvest.html / harvest-zoo.html -- the Track B corrections

The deployed pages carry **none** of the corrected calibration figures: `18.868`, `8.78`, `148.5`,
`characteristic-matched`, `single-index`, `design effect` and `0.38` are all ABSENT. So they
neither match nor contradict origin -- they simply do not publish these numbers, which is why
the corrections I landed are not reflected on the site.

Origin (tracker/class_calibration.json, repaired): `mde_pct` **8.78** (was 18.868),
benchmark **"SPY (single-index market benchmark; characteristic-match gate 2 UNMET)"**,
design_effect 0.38, rho -0.04673, permutation_p 0.9995.

## 3. Index page

Class-level figures there are about costs and peer counts (e.g. ETF 6.7122 bp, FOREX 56.93), not
the calibration statistics: `18.868`, `8.78`, `0.0467`, `0.9995`, `1.2818`, `2.8798`, `-0.5222`
are all absent. No contradiction with origin; also no reflection of the corrections.

## 4. Summary

- **MATCH**: COMMODITY sign/magnitude.
- **CONTRADICTION (different denominators, undisclosed)**: CRYPTO level, ETF/FOREX/BOND/FUTURES n.
- **DIFFERENT QUANTITY (not comparable)**: EQUITY.
- **ABSENT from the site**: every corrected Track B figure (mde 8.78, benchmark gate 2 UNMET).

The site's headline -- "no asset class is proven, no ranking is statistically distinguishable,
zero picks endorsed" -- is **consistent** with origin, where every class-level test either spans
zero or is inverted.

next_probe: publish the site's per-class n alongside each number (as the tracker does), so a
reader can tell a different-denominator figure from a contradiction.
