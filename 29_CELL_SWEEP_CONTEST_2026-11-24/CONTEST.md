# Contest — top 15 cells by net bp/trade (post 26bp cost)

This is a **ranking of a noisy quantity**, published because it was asked for. Read the DSR column before the net column: a cell can top this table and still be indistinguishable from noise.

| # | cell | class | n | net bp | 95% CI | perm p | DSR | walk-forward | verdict |
|---:|---|---|---:|---:|---|---:|---:|---|---|
| 1 | `SOLUSDT/breakout/1d` | CRYPTO | 62 | +71.90 | [-29.01, 184.28] | 0.013 | 0.0045 | CONSISTENT_SIGN | INCONCLUSIVE |
| 2 | `BTCUSDT/bb_meanrev/1d` | CRYPTO | 58 | +50.51 | [-23.98, 135.62] | 0.001 | 0.0031 | NOT_ROBUST | INCONCLUSIVE |
| 3 | `SOLUSDT/donchian/1d` | CRYPTO | 33 | +36.41 | [-108.93, 177.46] | 0.145 | 0.0009 | NOT_ROBUST | INCONCLUSIVE |
| 4 | `BTCUSDT/momentum_12_1/1w` | CRYPTO | 34 | +15.49 | [-191.83, 237.1] | 0.442 | 0.0002 | not run | INCONCLUSIVE |
| 5 | `BTCUSDT/donchian/1d` | CRYPTO | 48 | +1.66 | [-65.08, 76.07] | 0.214 | 0.0001 | not run | INCONCLUSIVE |
| 6 | `GLD/breakout/1w` | COMMODITY_ETF | 34 | -6.85 | [-109.73, 87.9] | 0.697 | 0.0001 | not run | INCONCLUSIVE |
| 7 | `SOLUSDT/bb_meanrev/1d` | CRYPTO | 54 | -7.58 | [-140.11, 129.3] | 0.365 | 0.0001 | not run | INCONCLUSIVE |
| 8 | `BTCUSDT/breakout/1d` | CRYPTO | 82 | -12.18 | [-63.86, 40.05] | 0.314 | 0.0 | not run | INCONCLUSIVE |
| 9 | `SPY/donchian/1d` | EQUITY | 121 | -14.86 | [-25.85, -3.34] | 0.209 | 0.0 | not run | KILL |
| 10 | `GLD/breakout/1d` | COMMODITY_ETF | 131 | -15.16 | [-40.45, 7.89] | 0.311 | 0.0 | not run | INCONCLUSIVE |
| 11 | `SPY/donchian/1w` | EQUITY | 40 | -15.72 | [-53.62, 22.31] | 0.685 | 0.0 | not run | INCONCLUSIVE |
| 12 | `SPY/breakout/1d` | EQUITY | 163 | -18.67 | [-28.79, -8.15] | 0.354 | 0.0 | not run | KILL |
| 13 | `BTCUSDT/donchian/1h` | CRYPTO | 63 | -19.34 | [-31.7, -7.07] | 0.078 | 0.0 | not run | KILL |
| 14 | `ETHUSDT/bb_meanrev/1d` | CRYPTO | 59 | -19.39 | [-128.54, 100.54] | 0.428 | 0.0 | not run | INCONCLUSIVE |
| 15 | `EURUSD/trend_pullback/1d` | FOREX | 117 | -21.66 | [-30.71, -12.93] | 0.105 | 0.0 | not run | KILL |

## Contest winner: nobody

The top cell is positive and the rest of the table decays into negatives. Of the three candidates that looked genuinely promising at the pooled stage, walk-forward killed two and left one:

| candidate | folds positive | most recent fold | walk-forward |
|---|---:|---:|---|
| `SOLUSDT/breakout/1d` | 3/3 | **+122.74 bp** | CONSISTENT_SIGN |
| `SOLUSDT/donchian/1d` | 1/2 | −77.16 bp | NOT_ROBUST |
| `BTCUSDT/bb_meanrev/1d` | 2/3 | −17.82 bp | NOT_ROBUST (decayed 152→54→−18) |

`SOLUSDT/breakout/1d` was pre-registered on 2026-11-24 and is awaiting out-of-sample data (0/30 forward trades at time of writing). It is **not a finding**.

## Why a contest is the wrong instrument here

Ranking 1000 cells by realised return selects the luckiest slice. The DSR column exists precisely to deflate that selection, and after deflation the leaderboard is flat: every DSR is ≈0. The honest reading of a table like this is *no winner*, not *the top row is the winner*.
