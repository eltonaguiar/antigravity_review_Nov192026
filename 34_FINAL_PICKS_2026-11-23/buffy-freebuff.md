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

## Revision 2026-11-23T02:35Z — justification block per endorsed candidate

Required by the accountability layer added 2026-11-23 (`34_FINAL_PICKS_2026-11-23/JUSTIFICATION_RULES.md (commit d5588ae)`): mechanism / counterparty /
why-this-symbol / why-now / what-kills-it, plus an explicit cost-vs-edge check. **Verdicts
unchanged: still 0 of 10 classes investable.** These are CANDIDATE rows, not endorsements for capital.

### STOCKS — XLV long, KO long, MSFT long (H-201)
- **Mechanism:** cross-sectional 6-month momentum. Under-reaction to news and premature
  profit-taking leave a persistent premium; the return is compensation for holding what has run.
- **Counterparty:** the seller who takes profit on a name up ~20% in six months. If that behaviour
  disappears, the premium goes with it.
- **Why these symbols:** top 3 of the pod's frozen 44-name universe by 6-month return at the
  2026-11-19 close — XLV +20.77%, KO +19.86%, MSFT +19.35%. Rule-selected, nothing hand-picked.
- **Why now:** the arithmetic permits it and only the statistics do not — 179 trades (above the
  n>=30 floor), CI-LB +7.246 bp/day, k*=50.9, DSR 0.9469 at N=29. Clock is day 15 of 20.
- **What kills it:** forward CI-LB <= 0 at day 40; DSR < 0.95 held at N >= 28; or the vol-matched
  -0.533 proving it is SPY beta rather than a premium.
- **Cost-vs-edge:** measured 12.0749 bp round trip against 11.521 bp/day gross — passes ~20x on the
  amortised basis. PIT is PARTIAL_NON_DELISTING_AWARE (flagged). **Duplicate exposure:** XLV is also
  in the ETF basket below; that is one view of healthcare, not two.

### ETF — R4b basket (XLE, XLV, XLK, IWM, EFA longs)
- **Mechanism:** 12-month absolute momentum with a cash alternative. Trend persistence plus vol-drag
  rotation out of losers; no short leg, so no borrow and no squeeze.
- **Counterparty:** the allocator who holds last year's loser to avoid realising a loss.
- **Why these symbols:** strictly the frozen rule's top five — no discretion, reproducible from
  `tools/etf_trend_forward_clock.py` and the cached closes.
- **Why now:** it is *not* now. First legitimate record is 2026-11-30, and the power analysis says a
  hurdle-sized edge confirms only 5% of the time at n=60 — the clock is a refutation instrument.
- **What kills it:** the frozen rule itself — annualised net <= 4.32%, or a one-sided 95% upper bound
  <= 4.32%, on forward rows only. No post-hoc rescue, no re-test.
- **Cost-vs-edge:** 6.7122 bp round trip is the cheapest measured vehicle we have; edge UNMEASURED,
  so this row cannot pass a cost-vs-edge check yet and does not claim to.

### CRYPTO — BTCUSDT perp delta-neutral carry (0% allocation)
- **Mechanism:** funding paid by leveraged longs to shorts, delta-hedged so direction is removed and
  only the funding stream remains.
- **Counterparty:** the leveraged perp long paying funding to stay in the trade.
- **Why this instrument:** deepest perp book with a measured funding series (1.9252 bp/day, n=111
  crossings) and 0.0 bp rehedge when quantity-matched.
- **Why now:** no — deliberate. 0% allocation until the venue fee tier is measured, because the
  overlay costs 15,440 bp to avoid 1,738 bp of decay.
- **What kills it:** measured fees making it net negative, which the current estimate already implies.
- **Cost-vs-edge:** the crypto cost band is 20-52 bp while the gross edge is 1.9 bp/day by
  construction — the check fails on an assumed cost, so it stays at zero.

## Revision  — per-class ranking, overall order, and the fee question

Full document: `reports/top_picks_per_class_and_overall_2026-11-23.md` in the research repo.
Nothing below changes a verdict; **0 of 10 classes investable, 4 untested.**

| rank | class | best cell | CI-LB bp/day | fails on |
|---|---|---|---|---|
| 1 | EQUITY | H-201 xsmom_top3_6m | +7.246 | DSR 0.9469 vs 0.95 |
| 2 | CRYPTO | H-206 tsmom_6m | +8.452 | benchmark (31.75% vs 35.94%), MDD −64.9% |
| 3 | ETF | H-205 xsmom_top3_6m | +2.007 | benchmark |
| 4 | INDEX | H-221 xsmom_top2_6m | +1.613 | benchmark |
| 5 | MUTUAL_FUND | H-216 VFIAX | +1.286 | n=28, benchmark 13.97% vs 9.02% |
| 6 | FUTURES | H-218 xsmom_top2_6m | +0.186 | 2× cost → −0.054 |
| 7 | BOND | H-213 xsmom_top2_6m | −0.453 | no signal |
| 8 | COMMODITY | H-210 GC=F | −0.724 | data integrity |
| 9 | FOREX | H-208 USDJPY | −0.520 | no signal |
| 10 | PENNY_STOCK | H-219 xsmom_top2_6m | −8.636 | no signal |

MEMECOIN / OPTIONS / PREDICTION_MARKET / PRIVATE_CREDIT have no pre-registered cell: UNKNOWN, not dead.

**Overall, worth spending money on: nothing.** Order is cash 4.32% → H-201 equity → vol-targeted
60/40 (risk control only; return half refuted OOS) → R4b clock (refutation only) → BTC carry at 0%.

**On mutual funds specifically:** dominated rather than merely worse. Best cell 9.02% CAGR against
**13.97%** for buy-and-hold of its own universe, so a fee cut does not close the gap; daily NAV means
no intraday exit; the same index in ETF form costs **6.7122 bp** with no minimum. The `$3,000`
Admiral-share minimum and the 9 bp expense gate are real but never decide anything, because the class
is already out on benchmark excess and executability.

**Gainer predictability:** daily null (AUC 0.537), weekly null (105 weeks; holdout top-5 precision
1.0× base rate crypto, 1.08× equity, with the top feature's IC flipping sign on holdout), monthly
not runnable — 24 months of data against ~48 needed for a 2× lift.
