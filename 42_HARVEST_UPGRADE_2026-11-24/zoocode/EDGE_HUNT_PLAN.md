# Edge-hunt plan: from analysis to a defensible edge

zoo-savant · 2026-11-24 · every step below is ordered by cost, so a cheap step can kill or advance the next.

## What I already know (measured, not assumed)

| Finding | Number | What it rules in / out |
|---|---|---|
Analyst DIRECTION does not predict | 63d UP−DOWN net **−0.194%**, sign p 0.73 | Ranking analysts or traders by buy/sell direction is dead |
Analyst ACTIVITY is the only positive hint | UP +2.188% vs random +0.574%; but DOWN +1.739% too | Something about *events* pays, not the endorsement |
Consensus LEVEL is inverted | STRONG_BUY −0.174% vs HOLD +1.967% | The label is not a return forecast; a higher label is not better |
Revisions are noise | 0 of 71 survive BH; noise floor median 2.94 pp | Month-over-month "momentum" in ratings is not a signal |
Costs decide most cases | round turns 0.61-52 bp by class | Any edge must be measured NET, per class |

## The plan, in order

### E1. Analyst ACTIVITY with the confound removed (highest value, cheapest)
**Question:** does *any rating change* predict, once you control for pre-event drift?
**Why:** it is the one place a positive excess appeared, but a change often follows a move, so the "edge" may be momentum already in the price.
**Method:** for each event, regress forward 21/63d excess on (a) an activity dummy, (b) the t−20..t−1 cumulative abnormal return. If the activity coefficient survives, activity carries information beyond drift; if it vanishes, we were measuring momentum.
**Kill condition:** activity coefficient CI includes 0 after the CAR control.

### E2. Are events just earnings dates?
**Question:** what fraction of rating changes fall within ±5 trading days of an earnings release?
**Why:** if most do, "activity predicts" collapses into "earnings predict", which is well known and already arbitraged.
**Method:** yfinance earnings dates; report the share, and re-run E1 excluding earnings windows.
**Kill condition:** the effect disappears outside earnings windows.

### E3. Firm-level skill, ranked properly
**Question:** do some *firms* consistently beat? 
**Why:** this is the "top traders" idea at firm level, which is the only level the data supports.
**Method:** on 308 tickers of dated actions, rank firms on a trailing window and evaluate on the NEXT window (never the same one), with a random-firm null and n ≥ 30 per firm.
**Kill condition:** no firm's out-of-window excess CI excludes 0 after BH.

### E4. Level vs change
**Question:** is the consensus LEVEL a contrarian signal? STRONG_BUY was the worst bucket.
**Method:** regress forward excess on level and on change jointly. Report each coefficient.
**Kill condition:** neither coefficient significant.

### E5. Crowd/analyst agreement delta
**Question:** when crowd markets and analysts agree, is the forward return better than when they disagree?
**Method:** the difference test (agree − disagree) with a CI. Never the level.
**Kill condition:** the delta CI includes 0.

### E6. Copytrade data
**Question:** do mirrored traders beat their own benchmark after their fees?
**Method:** the repo already ingests copy-trader profiles; measure per-trader excess at cluster-robust n, with a survivorship note (only traders still on the platform are visible).
**Kill condition:** no trader clears a deflated bar with n ≥ 30.

### E7. Cost-structure edge (the non-predictive option)
**Question:** can we earn from the mechanics rather than a forecast? Maker rebates, funding carry, borrow, roll yield.
**Why:** these do not require prediction, which is why they are the most likely "extremely profitable" outcome. It is also where crypto 20-52 bp round turns make taker strategies unviable and maker ones viable.
**Kill condition:** net carry after fees is within noise of zero.

### E8. A predictive framework, only if E1-E7 justify it
**Question:** can a cross-sectional model rank assets better than a constant?
**Method:** few, economically motivated features; purged/embargoed CV; DSR over the trial count; report a permutation null. **Not** a deep net over 400 noisy features, which would be the classic overfit.
**Gate:** OOS net Sharpe CI excluding 0 after DSR, or no framework is published.

## Guardrail on every step

Pre-register the rule before running it, cluster by symbol, report the MDE next to every null, and treat a null as the result rather than a reason to widen the definition. My own record today shows how easy the opposite is: three times I found a "significant" number that clustering or a control then removed.

## The honest expectation

The prior is that most of this comes back null, and that is a legitimate finding. If E1-E7 all fail, the defensible statement is that this data cannot support a predictive framework, and the profitable path is E7 (cost structure) or beta, not a prediction engine.
