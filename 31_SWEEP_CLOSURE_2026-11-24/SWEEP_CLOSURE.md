# Sweep closure — 2026-11-24

**Result: no surviving candidate in any asset class.**

## What was done

47 measured cells across 5 asset classes, from a 1000-cell ledger.
Every cell reported n, net bp/trade after a 26bp round-turn, 95% bootstrap CI,
signal-label permutation p, and DSR deflated for 1000 trials.

## Per-class outcome

| class | measured | KILL | PASS | median net bp | median gross bp | diagnosis |
|---|---:|---:|---:|---:|---:|---|
| EQUITY | 6 | 4 | 0 | -20.69 | +5.31 | COST problem |
| FOREX | 2 | 2 | 0 | -22.25 | +3.75 | COST problem |
| COMMODITY_ETF | 5 | 2 | 0 | -22.76 | +3.24 | COST problem |
| CRYPTO | 28 | 12 | 0 | -31.09 | -5.10 | SIGNAL problem |
| BOND_ETF | 3 | 3 | 0 | -43.29 | -17.29 | SIGNAL problem |

## Walk-forward results — every candidate tested

| `BTCUSDT/bb_meanrev/1d` | 2/3 | -17.82 | NOT_ROBUST |
| `EURUSD/trend_pullback/1d` | 0/3 | -28.95 | CONSISTENTLY_NEGATIVE |
| `GLD/breakout/1w` | 1/2 | -28.26 | NOT_ROBUST |
| `SOLUSDT/breakout/1d` | 3/3 | 122.74 | CONSISTENT_SIGN |
| `SOLUSDT/donchian/1d` | 1/2 | -77.16 | NOT_ROBUST |
| `SPY/donchian/1d` | 0/3 | -16.43 | CONSISTENTLY_NEGATIVE |

The class-level positive gross medians did not survive at the individual-cell
level: the best cell in each COST-problem class is negative net in every fold
where it has enough trades.

## What this closes and what it does not

**Closed:** generic daily technical rules (the 10 strategies in the ledger) do not
produce a reproducible positive net return after a 26bp round-turn, in any of the
five classes tested.

**Not closed:** `SOLUSDT/breakout/1d`, pre-registered 2026-11-24, is the only
candidate that was positive in all three sequential folds (+50.71 / +137.23 /
+122.74 net bp). It is awaiting out-of-sample data at 0/30 forward trades and
remains unproven. It is the single open thread.

**Never tested:** the 15m and 4h horizons (370 ledger cells) have no bar source,
and `ma_cross` / `rsi2_pullback` / `gap_fade` are structurally too rare to reach
n>=30 on daily bars. Those cells cannot yield a verdict and should not be counted
as tested.
