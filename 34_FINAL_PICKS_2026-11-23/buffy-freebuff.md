# Buffy (freebuff) — final picks, 2026-11-23

```
filed_utc:       2026-11-23T02:28Z
filed_local:     2026-11-22T21:28
repo_at:         findtorontoevents_antigravity.ca:push/phase2-round-2026-11-22@abe852ca4cb
ranked_list:     2026-11-23/buffy-freebuff/PICKS.md on antigravity_review_Nov192026 main @ a3f6a6b
honest_headline: 0 of 10 classes investable — one CANDIDATE (STOCKS) fails only the deflated-Sharpe gate, one forward-only CANDIDATE (ETF) has no records until 2026-11-30, and the other eight are dead or unmeasurable on our own bars.
```

## Per-class picks

| CLASS | VERDICT | PICK | n | EDGE (net) | DSR / N | PBO | COST | EXEC | KILL RULE | EVIDENCE |
|---|---|---|---|---|---|---|---|---|---|---|
| STOCKS | CANDIDATE | XLV long, KO long, MSFT long (H-201 xsmom top-3 of 44, 6m formation, monthly) | 179 trades | +10.95 bp/day at $25k backtest (gross 11.521 less 0.575 amortised cost); vol-matched excess -0.533 | 0.9469 / N=29 (0.9490 at N=28; clears only at N<=27) | UNMEASURED | measured, 12.0749 bp round trip (peer measures 1-5 bp; unresolved, stated) | ENTRY + TP/SL on rank-drop, monthly rebalance, ~12 partial round trips/yr | REFUTED if forward CI-LB <= 0 at day 40; NOT_PROVEN while DSR < 0.95 at N >= 28 | reports/asset_class_risk_reward_ladder_2026-11-23.md; reports/dsr_recompute_2026-11-23.json (C-029) |
| CRYPTO | CANDIDATE | BTCUSDT perp, delta-neutral funding carry — allocation 0% | 111 | +1.9252 bp/day gross measured; net UNMEASURED (fee tier assumed) | n/a (N=1, no series) | UNMEASURED | assumed VIP0 — explicitly not a measurement | ENTRY + TP/SL, daily rehedge (0.0 bp/day when quantity-matched) | 0% allocation until the venue fee tier is measured; overlay dead if it costs more than the 1,738 bp it avoids (measured: costs 15,440 bp) | alpha_engine/funding_rate_arb.py; notes/asset-class-ladder-risk-profit-proof-2026-11-23 |
| BONDS | DEAD | none | — | CI-LB -0.453; bond momentum 0 bp/side | UNMEASURED | UNMEASURED | SHY 0.6144 bp measured; rest unmeasured | buy and hold only | already dead: signal cell negative before cost | docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md |
| ETF | CANDIDATE | XLE long, XLV long, XLK long, IWM long, EFA long (R4b 12m absolute momentum, top 5 of 20, monthly) — all five clear the 4.32% hurdle | 0 records | UNMEASURED — forward ledger empty until 2026-11-30 | n/a (single pre-registered trial, N=1) | UNMEASURED | measured, 6.7122 bp round trip — lowest of any class measured | ENTRY + TP/SL on rank-drop, monthly rebalance, no short leg, no borrow | frozen: annualised net <= 4.32%, or one-sided 95% upper bound <= 4.32%, on forward rows only | docs/preregistration/ETF_TREND_FORWARD_2026-11-23.md; tools/etf_trend_forward_clock.py |
| MUTUAL_FUND | UNKNOWN | none | — | CI-LB +0.997 bp/day but MDE 4.27; needs 73.7 years of daily data to detect 1.92 bp/day | UNMEASURED | UNMEASURED | unmeasured | buy and hold only | untestable at available sample length | reports/asset_class_risk_reward_ladder_2026-11-23.md |
| FOREX | DEAD | none | — | CI [-4.32, +11.09] bp spans 0; break-even 4.3038 bp sits below the 7.533 bp cost upper bound | UNMEASURED | UNMEASURED | upper bound only, 7.533 bp, from the Sunday reopen | n/a | dead: break-even below cost | docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md |
| COMMODITY | UNKNOWN | none | — | UNMEASURED — roll-corrupted continuous series | UNMEASURED | UNMEASURED | unmeasured | n/a | no re-test is meaningful until roll-adjusted series is procured | docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md |
| OPTIONS | UNKNOWN | none | 0 | UNMEASURED — no options cost model exists in the estate | UNMEASURED | UNMEASURED | unmeasured (no model) | n/a | none measured; cannot be killed or confirmed | none |
| PREDICTION_MARKET | UNKNOWN | none | 0 | UNMEASURED — signal modules exist, no validated net-of-cost edge | UNMEASURED | UNMEASURED | unmeasured | n/a | none measured | alpha_engine/polymarket_signals.py, alpha_engine/kalshi_signals.py (not validated) |
| PRIVATE_CREDIT | UNKNOWN | none | 0 | UNMEASURED — no data, no vehicle, no marks | UNMEASURED | UNMEASURED | unmeasured | n/a | none measured | none |

## Overall ranked list

| # | PICK | CLASS | WHY IT RANKS HERE | EXEC | NET OF COST |
|---|---|---|---|---|---|
| 1 | XLV long | STOCKS | 4/5 gates; only G3 fails; k*=50.9 so cost is irrelevant to this cell | ENTRY + TP/SL, monthly | +10.95 bp/day backtest |
| 2 | KO long | STOCKS | same series, same gates — ranked by 6m signal strength, not by separate stats | ENTRY + TP/SL, monthly | +10.95 bp/day backtest |
| 3 | MSFT long | STOCKS | same series, same gates | ENTRY + TP/SL, monthly | +10.95 bp/day backtest |
| 4 | R4b basket: XLE, XLV, XLK, IWM, EFA longs | ETF | pre-registered, trial count 1, cheapest measured cost — but zero records, so it cannot rank above a measured backtest | ENTRY + TP/SL, monthly | UNMEASURED |
| 5 | T-bills at 4.32% | — | the bar, not a pick. Listed so every net number above has its reference on the same page | buy and hold | +4.32%/yr |

Ranking criterion used: **CI lower bound on net return at a $25,000 ticket**, not the point estimate. Tie-breaks: (1) break-even cost multiple k*, (2) fewer trials consumed, (3) shallowest drawdown. Kilo ranks by gates-passed then net bp; Zoo refuses to rank without a CI on net return. This uses the Zoo ordering on the evidence and the Kilo ordering on the gates.

## Per live class — three lines each

### STOCKS
- **Why it ranks here:** the only cell in the programme with a positive CI lower bound on net return (+7.246 bp/day raw) that also survives a 50.9x cost multiple.
- **What would move it up:** 137 more forward trading days at the same effect size at N=29, or an independent replication on a non-overlapping universe (adds observations without adding trials). Both are specified; neither can be hurried.
- **What would kill it:** forward CI-LB <= 0 at day 40; or DSR < 0.95 held at N >= 28 permanently; or the vol-matched negative (-0.533) turning out to be the whole story, i.e. it is SPY beta wearing a momentum costume.

### ETF
- **Why it ranks here:** cheapest measured vehicle (6.7122 bp), no short leg, no borrow, trial count 1 so its deflation bar stays near nominal — and it is the only rule in the estate that was pre-registered without being backtested first.
- **What would move it up:** its first legitimate record at 2026-11-30, then ~60 monthly records. Any single month is noise; only the clock changes the verdict.
- **What would kill it:** frozen rule, no post-hoc rescue — annualised net <= 4.32%, or a one-sided 95% upper bound <= 4.32%, on forward rows only.

### CRYPTO
- **Why it ranks here:** the funding carry is the best risk-adjusted object we have measured (1.9252 bp/day, rehedge 0.0 bp/day when quantity-matched) and it still earns 0% allocation, because its cost is assumed rather than measured.
- **What would move it up:** a measured venue fee tier. That single procurement converts a 0% allocation into a sized one.
- **What would kill it:** measured fees making the overlay's 15,440 bp cost exceed the 1,738 bp it avoids — which the current estimate already says it does.

## Dead classes — one line each

| CLASS | THE NUMBER THAT KILLED IT |
|---|---|
| BONDS | CI-LB -0.453 on the signal cell; bond momentum at 0 bp/side fails before cost is even applied |
| FOREX | break-even 4.3038 bp below a 7.533 bp cost upper bound, and the CI [-4.32, +11.09] spans zero |

## What is still unmeasured

| Item | Status | What it would take |
|---|---|---|
| commission from actual fills | UNMEASURED | fill prices; entry_price is stored, fill_price is not |
| point-in-time universe (delisting-aware) | PARTIAL_NON_DELISTING_AWARE | a delisting-aware vendor; 12 genuinely delisted tickers probed, all 12 return 0 bars |
| capacity / market impact at size | UNMEASURED | participation tests above 0.008% of ADV |
| venue fee tier (carry) | ASSUMED VIP0 | a measured tier from the exchange |
| equity round-trip cost | DISPUTED 12.0749 vs 1-5 bp | reconcile the two measurements; does not change STOCKS (k*=50.9) but changes the mid-table families |
| options cost model | ABSENT | a spread/assignment model; no options measurement exists in the estate |
| prediction-market cost | ABSENT | venue fee + settlement model |
| PBO for STOCKS | UNMEASURED | CSCV run against the 0.51 noise baseline at N=29 |

## Revisions

*(none yet — revisions append here, newest at the bottom; earlier blocks are never edited)*

## Revision 2026-11-23T02:31Z

changed:   the ETF row and the ETF entry in the ranked list
why:       reports/r4b_power_2026-11-23.md shows the frozen CONFIRM gate needs a point estimate of
           110 bp/month (13.2%/yr) at n=60, because SE = 45.0 bp/month for a 3.49%/month book. Power
           to confirm a hurdle-sized 36 bp/month edge is 5.0%; 36 bp/month would need 736 months.
impact:    ETF stays **CANDIDATE**. The expectation that ~60 monthly records produce a verdict is
           WITHDRAWN. The clock is a refutation instrument (point <= -38 bp/month refutes; 91.6%
           power at -100 bp/month) plus a point estimate whose interval tightens monthly.
evidence:  reports/r4b_power_2026-11-23.md;
           docs/preregistration/ETF_TREND_FORWARD_2026-11-23_AMENDMENT-1_PROPOSED.md (PROPOSED, not in force)
