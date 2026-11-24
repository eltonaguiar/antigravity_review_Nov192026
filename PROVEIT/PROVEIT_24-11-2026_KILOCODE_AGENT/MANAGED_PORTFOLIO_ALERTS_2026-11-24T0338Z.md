# Managed portfolio — rebalancing, alerts, and hold rules

**KILO CODE · 2026-11-24T0338Z UTC · paper only, not investment advice.**
Companion to the PROVEIT and TWEAKS reports. This is the *operating manual*: what to set, when, and why.

## The hold rule (all sizes)
- **Core index fund: hold indefinitely.** Do **not** set TP/SL on the core (evidence: TP/SL turnover costs more than it protects; the 200d-MA "timing" overlay *lowers* return — see TWEAKS). Minimum hold **>= 1 year** (avoids short-term tax + churn).
- **Bonds (60/40 only):** hold as the drawdown damper; rebalance, don't trade around it.
- **Cash (SGOV):** hold only as the emergency buffer / the ~3.8% hurdle — not a position to "manage".

## Rebalancing schedule
| portfolio | rule | when |
|---|---|---|
| **100% single index** | none — buy & hold | annual *check* only |
| **60/40** | rebalance when a sleeve drifts **> 5 percentage points** from target, or annually if no band hit | check quarterly; act on the 5-pt band |
| **All-in-one (XEQT/VEQT)** | none — internally rebalanced | annual check |

**Why band (not calendar-only):** bands rebalance on real drift and cut unnecessary trades/cost; calendar-only misses large drifts. (Sweep showed calendar 21/63/252d all ~6.9%/yr — cadence is second-order; the *existence* of rebalancing matters more.)

## Alerts to set (calendar + threshold)
1. **Rebalance alert** — recurring quarterly reminder ("check 60/40 sleeve drift vs 5-pt band").
2. **Drift alert** — broker allocation alert if equity or bond sleeve leaves its 5-pt band.
3. **Contribution alert** — monthly: invest new cash (DCA only because you *lack* a lump sum — lump-sum wins ~80% historically).
4. **Cash-floor alert** — if cash < 3-6 months expenses, pause investing.
5. **(Optional) MA-cross alert** — monthly price vs 200-day MA; exit to cash on cross-down, re-enter on cross-up. This is optional risk control and costs ~4-6%/yr of return (TWEAKS); only justified if it keeps you invested through a drawdown.
6. **Fee alert (annual)** — confirm fund MER stays <= ~0.10%; switch if a cheaper same-index vehicle appears.

## Per-account operating plan
| size | portfolio | alerts | hold |
|---|---|---|---|
| **$300** | 100% one index fund (FXAIX/FZROX; or CAD VFV fractional) | monthly contribution; annual fee check | hold indefinitely |
| **$500** | 100% total-market index | same | hold indefinitely |
| **$2,000** | all-in-one (XEQT/VEQT) or 60/40 | quarterly drift check; annual fee check | hold indefinitely |
| **$10,000** | 60/40 (or XEQT + bond sleeve) | quarterly 5-pt band + rebalance alert; annual fee check | hold indefinitely |

## What you are NOT managing
- No per-stock picking, no active value basket, no crypto/FX strategies — **0 demonstrated alpha** (grid 0/362; census 96/96 killed).
- You are managing **two things only: cost and drift.** That is the whole job.

## Sanity numbers (this PROVEIT run, common window)
Buy & hold equity **19.0%/yr, -18.8% DD, Sharpe 0.94**; 60/40 ~6.9%/yr, ~-20.7% DD (weak — bonds drew down this regime); 200d-MA timing 13.8%/-9.4% (risk control). **Fee drag:** $300 = 2.09% vs $10,000 = 0.69%.

*Paper only. Not investment advice.*
