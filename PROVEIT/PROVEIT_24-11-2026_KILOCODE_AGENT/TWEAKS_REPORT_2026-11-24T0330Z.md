# PROVEIT tweaks — do any parameter tweaks or blends beat plain buy-and-hold?

**Run:** 2026-11-24T0330Z UTC · engine `simulate_tweaks.py` · common window (start bar 250) · data `data/market_prices.csv`
**Paper only. Not investment advice.**

| variant | net CAGR | max DD | excess Sharpe |
|---|---:|---:|---:|
| **Baseline: buy & hold equity** | **19.01%** | −18.76% | **0.937** |
| 200d-MA timing (MA=100) | 11.47% | −10.41% | 0.647 |
| 200d-MA timing (MA=150) | 13.38% | −8.41% | 0.763 |
| timing (MA=200) | 13.76% | −9.39% | 0.779 |
| timing (MA=250) | 13.35% | −15.92% | 0.703 |
| 60/40 rebalance 21d | 6.91% | −20.73% | 0.313 |
| 60/40 rebalance 63d | 6.78% | −20.87% | 0.303 |
| 60/40 rebalance 252d | 6.91% | −20.92% | 0.312 |
| **Blend 50/50 (equity + timing200)** | 16.13% | −13.99% | 0.877 |

**Pareto test — does anything beat baseline on BOTH return and drawdown? → NONE.**

## What the tweaks prove
1. **No parameter setting or blend beats plain buy-and-hold on risk-adjusted terms.** Every timing variant and the blend
   *lower* CAGR and Sharpe to buy a shallower drawdown — that is **risk control, not alpha**. MA=150 gives the best
   drawdown (−8.4%) at ~5.6%/yr return cost; MA=250 is worst on both.
2. **The 60/40 sleeve was poor over this window** (~6.9%/yr, DD ~−20.7%) because bonds drew down in the rate-hike regime —
   a reminder that 60/40 helps in *some* regimes, not all; its value is regime-dependent drawdown, not a free lunch.
3. **Blending two near-identical equity exposures does not create edge** — the 50/50 blend sits between its parts on every
   metric (Sharpe 0.877 < baseline 0.937). Diversification across *uncorrelated* assets helps; blending correlated
   variants does not.
4. **Honest conclusion unchanged:** the provable edge is **cheap, diversified, patient beta**. Tweaking parameters of an
   active overlay only trades return for drawdown.

*(Re-run `simulate_tweaks.py` for a fresh dated dump; window start 250 vs the main report's 200 explains the small
baseline difference — 19.01% vs 18.30% — both measured, neither cherry-picked.)*
