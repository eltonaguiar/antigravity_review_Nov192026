# Corrected book expectancy — priced rows only

**Read-only** query of `ejaguiar1_stocks.at_pick_outcomes`, 2026-11-25. Credentials read at runtime;
never printed or committed. No table writes.

## Filter counts

```sql
SELECT status, pnl_pct FROM at_pick_outcomes WHERE status IN ('WON','LOST');
```

| stage | n |
|---|---:|
| WON + LOST resolved | **33,096** |
| of those, pnl_pct = 0 | **0** |
| **priced rows used** | **33,096** |

The resolved WON/LOST set already equals the priced set: no zero placeholders remain inside it.
(The earlier headline used 33,092; a 4-row drift from the live table does not change anything.)

## Result

| measure | headline (33,092) | priced-only (33,096) |
|---|---:|---:|
| mean | **+6.34 bp** | **+6.3474 bp** |
| median | **−38.98 bp** | **−38.9950 bp** |
| profitable | — | 13,645 |
| losing | — | 19,451 |
| round-turn cost | 26 bp | 26 bp |

## Does the conclusion change?

**No.** The priced-only mean is **+6.35 bp**, still **below the 26 bp round turn**; the median is
**−39.00 bp**, still negative. The book remains **negative net of cost**. Removing zero rows did not
rescue it because the 33k resolved set contained no zeros.

This also means the +6.34 outcome is **not** being inflated by expired/zero rows; it is a real
resolved-trade mean, and it is still below its own trading cost. The two-table disagreement and the
sign-flip quarantine remain separate unresolved issues; this table does not fix those.

next_probe: recompute the same two statistics after the trading_picks price-derived PnL reconciliation,
not from either stored pnl_pct.
