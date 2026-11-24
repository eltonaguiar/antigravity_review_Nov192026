# Contest — top 15 cells by net bp/trade (post 26bp cost)

This is a **ranking of a noisy quantity**, published because it was asked for. Read the DSR column before the net column: a cell can top this table and still be indistinguishable from noise.

| # | cell | class | n | net bp | 95% CI | perm p | DSR | walk-forward | verdict |
|---:|---|---|---:|---:|---|---:|---:|---|---|
| 1 | `SOLUSDT/breakout/1d` | CRYPTO | 62 | +71.90 | [-29.01, 184.28] | 0.013 | 0.0045 | CONSISTENT_SIGN | INCONCLUSIVE |
| 2 | `BTCUSDT/bb_meanrev/1d` | CRYPTO | 58 | +50.51 | [-23.98, 135.62] | 0.001 | 0.0031 | NOT_ROBUST | INCONCLUSIVE |
| 3 | `SOLUSDT/donchian/1d` | CRYPTO | 33 | +36.41 | [-108.93, 177.46] | 0.145 | 0.0009 | NOT_ROBUST | INCONCLUSIVE |
| 4 | `BTCUSDT/momentum_12_1/1w` | CRYPTO | 34 | +15.49 | [-191.83, 237.1] | 0.442 | 0.0002 | not run | INCONCLUSIVE |
| 5 | `BTCUSDT/donchian/1d` | CRYPTO | 48 | +1.66 | [-65.08, 76.07] | 0.214 | 0.0001 | not run | INCONCLUSIVE |
| 6 | `SOLUSDT/bb_meanrev/1d` | CRYPTO | 54 | -7.58 | [-140.11, 129.3] | 0.365 | 0.0001 | not run | INCONCLUSIVE |
| 7 | `BTCUSDT/breakout/1d` | CRYPTO | 82 | -12.18 | [-63.86, 40.05] | 0.314 | 0.0 | not run | INCONCLUSIVE |
| 8 | `BTCUSDT/donchian/1h` | CRYPTO | 63 | -19.34 | [-31.7, -7.07] | 0.078 | 0.0 | not run | KILL |
| 9 | `ETHUSDT/bb_meanrev/1d` | CRYPTO | 59 | -19.39 | [-128.54, 100.54] | 0.428 | 0.0 | not run | INCONCLUSIVE |
| 10 | `SOLUSDT/vwap_reversion/1d` | CRYPTO | 154 | -23.68 | [-91.04, 42.46] | 0.52 | 0.0 | not run | INCONCLUSIVE |
| 11 | `ETHUSDT/donchian/1d` | CRYPTO | 37 | -23.87 | [-115.89, 69.96] | 0.473 | 0.0 | not run | INCONCLUSIVE |
| 12 | `BTCUSDT/vwap_reversion/1h` | CRYPTO | 321 | -27.08 | [-33.88, -20.05] | 0.444 | 0.0 | not run | KILL |
| 13 | `BTCUSDT/momentum_12_1/1h` | CRYPTO | 557 | -29.62 | [-33.61, -25.36] | 0.922 | 0.0 | not run | KILL |
| 14 | `ETHUSDT/momentum_12_1/1d` | CRYPTO | 242 | -30.95 | [-78.8, 19.54] | 0.619 | 0.0 | not run | INCONCLUSIVE |
| 15 | `BTCUSDT/bb_meanrev/1h` | CRYPTO | 128 | -31.24 | [-43.85, -19.25] | 0.872 | 0.0 | not run | KILL |

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
