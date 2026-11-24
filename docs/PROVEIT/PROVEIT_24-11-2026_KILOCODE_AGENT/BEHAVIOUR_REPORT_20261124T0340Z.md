# PROVEIT behaviour — what investor mistakes actually cost (real adjusted prices)

**KILO CODE · dated run · sim `simulate_behaviour.py` · total-return (FXAIX adj), full ~5y window · paper only, not advice.**
Baseline **buy & hold = 11.66%/yr**.

## Missing the best days (the case for staying invested)
| scenario | CAGR |
|---|---:|
| hold all days (baseline) | **11.66%** |
| miss the best 10 days | **3.47%** |
| miss the best 20 days | −1.62% |
| miss the best 30 days | −6.05% |

**Missing ~10 up-days destroys most of the return.** Timing "out and back in" must catch those days — which is why the
timing overlays in TWEAKS underperform. **Stay invested.**

## Panic-selling on a drawdown (sell at −X%, rebuy after N days)
| trigger / re-enter | CAGR |
|---|---:|
| −10% / 21d | 12.10% |
| −15% / 21d | 7.63% |
| −20% / 21d | 11.39% |
| −10% / 63d | 10.11% |
| −15% / 63d | 5.19% |
| −20% / 63d | 10.50% |
| −10% / 126d | 7.00% |
| −15% / 126d | 6.17% |
| −20% / 126d | 10.09% |

**Most panic rules LOWER CAGR vs 11.66%** (e.g., −15%/63d → 5.19%, −10%/126d → 7.00%). The lone higher case
(−10%/21d → 12.10%) is **dip-buy luck in this one window**, not a repeatable rule — do not generalize it. Behavioural
selling is a bet that you can re-enter better than you left; the data says you usually cannot.

## Caveat
"Worst-entry-then-hold" returned ≈ baseline because the deepest 20-day drop occurred at the **start** of this sample;
so that subtotal is uninformative here — the strong, robust results are the **miss-best-days** and **panic-sell** columns.

## What this adds to the proof
It operationalizes the **hold rule**: the biggest controllable cost after fees is **behaviour** — bailing or timing out.
For every account size ($300 → $10,000): **buy the cheap index, automate contributions, set a rebalance/drift alert, and
do not sell into a drawdown.** Manage cost and drift; do not manage the market.

*Paper only. Not investment advice.*
