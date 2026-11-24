# HARVEST backtest (consensus + direction -> forward excess vs SPY)

Entry next trading close after the period date; cost 6.7122bp; exits 21/63d.

## Label -> forward excess (21d)
| Label | n | mean % | 95% CI | median % | hit | p(≤0) | BH q | CI-low>0 |
|---|---|---|---|---|---|---|---|---|
| BUY | 117 | +0.589 | [-0.508,+1.616] | +0.231 | 50% | 0.135 | 0.135 | False |
| HOLD | 53 | +1.451 | [+0.172,+2.681] | +0.928 | 53% | 0.016 | 0.063 | True |
| SELL | 4 | +3.261 | [-1.416,+7.937] | +3.269 | 50% | 0.076 | 0.102 | False |
| STRONG_BUY | 110 | +1.437 | [-0.090,+2.949] | +0.192 | 52% | 0.033 | 0.065 | False |

## Label -> forward excess (63d)
| Label | n | mean % | 95% CI | median % | hit | p(≤0) | BH q | CI-low>0 |
|---|---|---|---|---|---|---|---|---|
| BUY | 56 | -1.814 | [-3.840,+0.215] | -1.886 | 38% | 0.955 | 0.955 | False |
| HOLD | 29 | -0.197 | [-4.187,+3.843] | +2.587 | 62% | 0.554 | 0.739 | False |
| SELL | 2 | +4.884 | [-4.316,+14.085] | +4.884 | 50% | 0.251 | 0.739 | False |
| STRONG_BUY | 55 | +0.290 | [-3.371,+3.882] | -0.395 | 47% | 0.437 | 0.739 | False |

## Strong-buy basket by period (21d excess)
- 2026-08-01: n=28, mean +2.362%, hit 57%
- 2026-09-01: n=27, mean -0.370%, hit 26%
- 2026-10-01: n=27, mean +3.486%, hit 56%
- 2026-11-01: n=28, mean +0.279%, hit 68%

Caveats: symbol-clustered bootstrap, BH-corrected; overlapping windows, survivorship, sell-side bullish bias, small n; 63d only Aug+Sep.
