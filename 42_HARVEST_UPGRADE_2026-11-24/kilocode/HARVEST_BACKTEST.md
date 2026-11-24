# Backtest + Monte Carlo verdict (2026-11-24)

## HARVEST consensus/labels → forward excess vs SPY
Entry next trading close after the period date; 6.7122bp cost; 71 US large caps, 4 monthly periods.

| Label | n(21d) | mean 21d | CI 21d | n(63d) | mean 63d | CI 63d |
|---|---|---|---|---|---|---|
| BUY | 117 | +0.580 [-0.740,+1.877] | | 56 | -2.369 [-4.892,+0.100] | |
| HOLD | 53 | +1.061 [-1.571,+3.736] | | 29 | +0.098 [-4.949,+5.068] | |
| SELL | 4 | +2.969 [-2.081,+8.020] | | 2 | — | |
| STRONG_BUY | 110 | +1.325 [-0.329,+3.109] | | 55 | +0.003 [-3.249,+3.320] | |

**No label has a 21d or 63d CI-low above zero.** The STRONG_BUY basket was +2.36%, −0.41%, +3.07%, +0.28% across four periods (2/4 positive on n=4).

## Direction (month-over-month)
| Direction | n(21d) | mean | CI |
|---|---|---|---|
| DETERIORATING | 11 | +0.235 | [-3.024,+3.422] |
| IMPROVING | 12 | -0.598 | [-4.265,+3.449] |
| STABLE | 190 | +0.694 | [-0.523,+1.916] |

Direction adds nothing (IMPROVING n=12 −0.60%; DETERIORATING n=11 +0.24%; STABLE +0.69%, CI includes 0).

## Published pick classes — Monte Carlo (3,000 resamples, 1% risk/trade)

| Class | n | mean % | P(mean>0) | mean CI | equity P5/P50/P95 | MDD P50 | sign-perm p |
|---|---|---|---|---|---|---|---|
| CRYPTO | 1803 | -0.501 | 0.000 | [-0.686,-0.309] | -11.65/-8.64/-5.42% | -8.92% | 1.000 |
| EQUITY | 783 | +0.061 | 0.624 | [-0.362,+0.493] | -2.81/+0.48/+3.92% | -1.64% | 0.377 |
| ETF | 589 | +0.052 | 0.673 | [-0.190,+0.289] | -1.11/+0.34/+1.71% | -0.66% | 0.338 |
| FOREX | 229 | -0.054 | 0.114 | [-0.142,+0.034] | -0.32/-0.12/+0.08% | -0.18% | 0.885 |
| COMMODITY | 54 | -2.518 | 0.000 | [-3.960,-1.272] | -2.12/-1.33/-0.69% | -1.36% | 1.000 |
| BOND | 36 | -0.013 | 0.470 | [-0.322,+0.307] | -0.12/-0.00/+0.11% | -0.06% | 0.529 |

**Verdict:** nothing is viable. CRYPTO (−0.501%, P=0.000, perm=1.000) and COMMODITY (−2.518%, P=0.000) are significantly negative; EQUITY/ETF positive means are noise (P=0.62/0.67, perm=0.38/0.34) with negative medians; FOREX/BOND flat. Consensus/direction has no predictive CI.

## What this means
- Do not publish any of this as an edge; paper/negative controls only.
- Negative classes are reliably negative (avoid signal), not investable longs.
- Real person-level testing needs a paid dated ledger.
- Next gate: forward n≥100, expectancy_worst>0, DSR≥0.95, BH, PBO<0.5.

## Coverage-change experiment (the one remaining distinct test)
Signal: change in the number of covering analysts between months, not the level or
month-over-month direction. `INITIATION` = +2 or more analysts; `DROP` = −2 or more;
`STABLE` otherwise. Entry next close after the period; excess vs SPY; 6.7122bp cost.

| Bucket | horizon | n | mean excess | 95% CI | hit | CI-low>0 |
|---|---|---|---|---|---|---|
| DROP | 21d | 19 | +4.257% | [+1.059, +7.455] | 68% | **yes, but n<30** |
| INITIATION | 21d | 12 | +2.085% | [−2.007, +6.335] | 50% | no |
| STABLE | 21d | 182 | +0.118% | [−1.136, +1.391] | 48% | no |
| STABLE | 63d | 69 | +0.536% | [−2.308, +3.213] | 55% | no |

**Verdict: not defensible.** The only positive CI is DROP at n=19, below the
n≥30 ranking floor; the 63d buckets are under n=3. It is a hypothesis to
pre-register, not a result.
**Falsifier:** pre-register the coverage-change rule now; if after forward
accumulation no bucket reaches n≥30 with CI-low>0 and effect > 2× cost, the
mechanism is dead. Do not retest consensus levels or direction again.
