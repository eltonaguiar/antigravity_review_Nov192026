# Decision — disposition of the 5 KILL verdicts with unsound evidence

**Date:** 2026-11-24 · **Trigger:** `PLAN/logs/H_intraday_and_stale_cache.md`
**Affects:** the ledger's kill list, which any downstream reader treats as settled

## The decision

**All 5 are downgraded from `KILL` to `UNPROVEN`.** They are not re-measured, not re-instated, and
not left as kills. The kill list moves from **23 established to 18 established + 5 unproven**.

| cell | recorded | evidence problem | disposition |
|---|---|---|---|
| `BTCUSDT_vol_compression_15m` | KILL (n=57) | served `binance:1d`, horizon declared 15m | **UNPROVEN** |
| `BTCUSDT_momentum_12_1_1h` | KILL (n=557) | 90-day cache ending 261 days ago; a 12-month lookback cannot exist inside 90 days | **UNPROVEN** — `BLOCKED_NO_DATA` is fairest |
| `BTCUSDT_vwap_reversion_1h` | KILL (n=321) | same stale 90-day cache | **UNPROVEN** |
| `BTCUSDT_bb_meanrev_1h` | KILL (n=128) | same stale 90-day cache | **UNPROVEN** |
| `BTCUSDT_donchian_1h` | KILL (n=63) | same stale 90-day cache | **UNPROVEN** |

## Why not "re-measure and see"

Re-measuring is the obvious move and it is the wrong one to do *now*, for two reasons.

**For `momentum_12_1_1h` the data does not exist.** A 12-month-minus-1-month rule needs 13+ months of
1-hour bars. The repo holds 90 days. No amount of compute closes that gap. The only honest verdict is
`BLOCKED_NO_DATA`, and calling it a kill is a claim about a rule that was never evaluated.

**For the other four, re-measuring would compound the error.** The stale cache is the *only* 1-hour
source in the repo. Re-running against it produces the same 90 days, so the "new" measurement would
be the old one wearing a fresh timestamp — and it would then look independently confirmed. Verifying a
number by recomputing it from the same bad input is the most convincing possible way to be wrong.

## Why not "leave them as kills"

A kill is a demotion with consequences; it removes a strategy from consideration. Leaving five
demotions standing on wrong-resolution or 8.6-month-stale data means the kill list overstates what
has been ruled out. `UNPROVEN` is the accurate description: not acquitted, not convicted, no trial.

The direction of the bias matters. Short windows and stale regimes both *reduce* measured edge, so the
error runs systematically toward false kills. Five of twenty-three is 21.7% of the kill list resting on
evidence that could only have made the strategies look worse than they are.

## What would change this

1. **1-hour bars back to 2025-11-01 or earlier** — unblocks all four cache cells and `momentum_12_1_1h`,
   which needs 13 months.
2. **A genuine 15-minute series** — unblocks `vol_compression_15m` and `rsi2_pullback_15m`.
3. **A declared comparison window in every cell artifact** — so "shorter window" stops being invisible.
   `bar_source` records provenance well for the `_1w` cells (`binance:1d resampled->1w (142 bars from
   1000 daily)`); the cache cells record the file but not its span.

## Enforcement

`R8-BARSOURCE` and `R9-CACHE` in `PLAN/tools/artifact_lint.py` fail on any recurrence. Verified
precision on the current ledger: 8 HIGH findings, all 8 genuine, zero false positives — and a planted
`_15m` file fires through the acknowledged baseline, so the gate cannot be silently waived.
