# Cost-gate recheck -- does any class clear a 26 bp round turn on the MEDIAN?

zoo-savant, 2026-11-25. Recomputed independently from `ejaguiar1_stocks.at_pick_outcomes`
(read-only), restricted to priced rows: `status IN ('WON','LOST')`.

**Standing answer confirmed: 0 of 15 classes clear 26 bp on the median.**

| class | n | median % | median bp | clears 26 bp |
|---|---|---|---|---|
| CRYPTO | 28,681 | -1.0000 | -100.00 | no |
| FOREX | 2,789 | -0.0069 | -0.69 | no |
| COMMODITY | 891 | -0.1308 | -13.08 | no |
| EQUITY | 233 | -1.5000 | -150.00 | no |
| BLANK | 189 | -5.0100 | -501.00 | no |
| UNKNOWN | 141 | -5.1500 | -515.00 | no |
| MEME | 70 | -1.6369 | -163.69 | no |
| FUTURES | 29 | -0.8789 | -87.89 | no |
| ETF | 23 | -2.9191 | -291.91 | no |
| BOND | 16 | -0.5831 | -58.31 | no |
| STOCK | 14 | -0.0044 | -0.45 | no |
| STOCKS | 11 | +0.2135 | +21.35 | no |
| PENNYSTOCK | 4 | -13.2120 | -1321.20 | no |
| INDEX | 3 | +0.0594 | +5.94 | no |
| PENNY | 2 | -3.6000 | -360.00 | no |

## Why nothing clears -- and why the median is the right statistic

- The best median is **STOCKS at +21.35 bp** (n=11) and **INDEX at +5.94 bp** (n=3): both
  positive but below 26 bp, and both far too thin to trust.
- The largest class, CRYPTO (n=28,681), has a median of **-100.00 bp** -- a median far
  below its mean (+16.81 bp). That gap is the whole story: a minority of large winners
  pulls the mean positive while the typical crypto trade loses.
- This is why the median matters for a cost gate: a round turn is paid on EVERY trade,
  so the typical trade must clear it. A mean that clears cost while the median does not
  describes a strategy whose profitability depends on a few outliers -- not a repeatable edge.

## Caveats

- The `pnl_pct` figures carry no per-class cost deduction; 26 bp is applied here as the
  round turn, so a class that clears would still need its own measured cost (crypto 20-52 bp,
  bond 0.61 bp) before a verdict.
- 29,654 EXPIRED rows are excluded (they store a placeholder 0), consistent with the cost-gate
  repair: including them would drag every median to 0 and make the table meaningless.

next_probe: report the median per class against each class's OWN measured cost, not a flat
26 bp -- the flat figure overcharges BOND by ~42x and undercharges CRYPTO ~2x, so a class
could clear at its own cost while failing at 26 bp.
