# KILOCODE_VSCODE — final picks, 2026-11-23

```
filed_utc:       2026-11-23T02:33Z
filed_local:     2026-11-23T02:33Z (host UTC)
repo_at:         findtorontoevents_antigravity.ca:feat/coms-final-notes-2026-11-20 (ledger audit3 2026-11-20T01:57Z)
ranked_list:     reports/eval_rerun_per_class_costs.json + reports/g3_shortlist.json + docs/edge_research/G3_DSR_ANALYSIS_AND_CRITERIA_2026-11-23.md
honest_headline: 0 of 10 classes investable; 0/69 picks pass all gates; the only defensible real-money action is a low-cost broad index ETF.
endorsed_count:  0
```

## Answer to the operator's question (VETTING_LEDGER)
> *How did a crypto pick arrive at a net 11.36 bp when crypto round trip is 20–52 bp?*

**It used a flat 12.87 bp cost for every class, which under-applied crypto's measured 20–52 bp by 7–39 bp.**
That table was wrong. Re-costed at your band (20 bp major / 52 bp alt), **49/69 picks go net ≤ 0**; DOT is
**−28 bp** (gross ≈24 bp − 52 bp) and META/JUP with n=0 were inadmissible. Only ENJ, ETH, WIF stay net-positive,
and all three still fail DSR ≥ 0.95. Every row below is costed at the class band and labelled.

## Per-class picks

| CLASS | VERDICT | PICK | n | EDGE (net) | DSR / N | PBO | COST | EXEC | KILL RULE | EVIDENCE |
|---|---|---|---|---|---|---|---|---|---|---|
| STOCKS | DEAD | none (best CVX long) | 35 | +178.9 bp @$25k, DSR 0.318 | 0.318 / 658 | 0.48 | measured 2 bp | BUY AND HOLD | DSR<0.95 or forward n<100 | eval_rerun_per_class_costs.json |
| CRYPTO | DEAD | none (best ENJ long) | 30 | +89.1 bp @$25k, DSR 0.004 | 0.004 / 658 | 0.11 | measured 20/52 bp | ENTRY + TP/SL (high turnover) | DSR<0.95 or net≤0 | crypto_recheck_operator_band.json |
| BONDS | DEAD | none (TLT long) | 1 | −22 bp net | — | — | measured ~10 bp | BUY AND HOLD | n<30 → dead | eval_rerun_per_class_costs.json |
| ETF | DEAD | none (best SOXX long) | 37 | +34.0 bp @$25k, DSR 0.004 | 0.004 / 658 | 0.52 | measured 2 bp | BUY AND HOLD | DSR<0.95 | eval_rerun_per_class_costs.json |
| MUTUAL_FUND | UNKNOWN | none | 0 | UNMEASURED | — | — | assumed ~45 bp/yr MER | BUY AND HOLD | no instrument-level data | reports/vehicle_10y_cost.json |
| FOREX | DEAD | none (best AUDJPY long) | 34 | +61.6 bp @$25k, DSR 0.815 | 0.815 / 658 | — | measured 1 bp | ENTRY + TP/SL | DSR<0.95; fx_prices dead 2026-02-09 | g3_shortlist.json |
| COMMODITY | DEAD | none | 0 | negative-expectancy class | — | — | — | — | class KILL | deflation_programme.json |
| OPTIONS | UNKNOWN | none | 0 | UNMEASURED | — | — | UNMEASURED | — | no data layer | pit_status.json |
| PREDICTION_MARKET | UNKNOWN | none | 0 | maker-only, no measured edge | — | — | maker ~1.75% vs taker ~7% | maker-only | no oos edge | pit_status.json |
| PRIVATE_CREDIT | UNKNOWN | none | 0 | UNMEASURED | — | — | UNMEASURED | — | no data | — |

## Justification per ENDORSED pick

**None.** `endorsed_count: 0`. No pick has a mechanism + counterparty + n≥30 + measured cost + surviving DSR. Per
the folder's own rule, a pick with `n=0` cannot appear here, and no pick clears DSR≥0.95.

## Overall ranked list — for REFERENCE, not endorsed

Two orderings, both of picks that FAIL gates. Rank 1 here is *least-bad*, not *investable*.

**Ranking criterion A — highest net bp at class-band cost (return leaders, all fail DSR):**

| # | PICK | CLASS | NET bp @$25k | DSR | WHY IT IS NOT ENDORSED |
|---|---|---|---|---|---|
| 1 | CVX long | EQUITY | 178.9 | — | fails DSR≥0.95 |
| 2 | AMD long | EQUITY | 119.1 | — | fails DSR≥0.95 |
| 3 | ENJ long | CRYPTO | 89.1 | — | fails DSR≥0.95 |
| 4 | AMC long | EQUITY | 84.3 | — | fails DSR≥0.95 |
| 5 | AUDJPY long | FOREX | 61.6 | — | fails DSR≥0.95 |

**Ranking criterion B — closest to clearing G3 (DSR≥0.95), the honest shortlist:**

| # | PICK | CLASS | n | DSR now | trades needed | WHY IT IS NOT ENDORSED |
|---|---|---|---|---|---|---|
| 1 | AUDJPY long | FOREX | 34 | 0.83 | +14 | nearest to G3 but UNMEASURABLE (see below) |
| 2 | CVX long | EQUITY | 35 | 0.328 | +83 | nearest to G3 but UNMEASURABLE (see below) |
| 3 | AAPL long | EQUITY | 81 | 0.106 | +457 | nearest to G3 but UNMEASURABLE (see below) |

**My OVERALL TOP 3–5 (stated plainly):** **none are investable.** If forced to order the least-bad by evidence
quality: **(1) AUDJPY** (DSR 0.815, 14 trades from G3 — but FOREX feed is dead), **(2) CVX** (DSR 0.318, 83
trades away — but STOCKS have no hold-times), **(3) ENJ**, **(4) ETH**, **(5) WIF** (net-positive at crypto band
but DSR 0.004–0.07). I endorse none of these.

## Per live class — three lines each

### STOCKS
- **Why it ranks here:** highest credible DSR among classes that have data (CVX 0.318, n=35), cost is tiny (2 bp).
- **What would move it up:** publish EQUITY hold-times (entry→exit) → unlocks G2/G4; and n≥100 with SR≥0.5.
- **What would kill it:** survivorship-biased universe (0 delisted names) already caps it; DSR<0.95 kills it today.

### CRYPTO
- **Why it ranks here:** most observations (up to n=219) but lowest credible DSR; 20–52 bp cost eats most edges.
- **What would move it up:** a mechanism with per-trade SR≥0.5 at n≥100; currently SR≈0.1–0.14.
- **What would kill it:** already killed — net≤0 for 46/49 crypto rows at the measured band.

### FOREX
- **Why it ranks here:** AUDJPY has the single highest DSR (0.815) and needs only ~14 more trades.
- **What would move it up:** restore the FX price feed (dead since 2026-02-09) so those 14 trades can accrue.
- **What would kill it:** class is frozen KILL; no forward accrual possible.

### ETF
- **Why it ranks here:** cheapest execution (2 bp) and shallowest drawdown class, but no signal edge.
- **What would move it up:** treat it as the BETA benchmark to beat, not as an alpha source.
- **What would kill it:** DSR 0.004; already dead as a signal.


## Dead / unrankable classes — one line each

| CLASS | STATUS | THE NUMBER, OR THE MISSING INPUT |
|---|---|---|
| BONDS | DEAD | TLT net −22 bp, n=1 |
| COMMODITY | DEAD | negative-expectancy class, 0 rows |
| MUTUAL_FUND | UNRANKABLE | no instrument-level fee/return series; MER only implied (~45 bp/yr) |
| OPTIONS | UNRANKABLE | no options data layer |
| PREDICTION_MARKET | UNRANKABLE | maker-only evidence, no measured OOS edge |
| PRIVATE_CREDIT | UNRANKABLE | no data |

## What is still unmeasured

| Item | Status | What it would take |
|---|---|---|
| EQUITY hold-times (entry→exit) | MISSING | publish per-pick entry/exit dates; unlocks G2/G4 for all STOCKS/ETF |
| FOREX forward prices | DEAD | restore fx_prices past 2026-02-09 |
| crypto venue fee tier (measured) | ASSUMED 20–52 bp | exchange fee-tier export |
| point-in-time / delisting-aware universe | MISSING | delisted-name price history |

## Contesting a verdict

I accept every operator rejection in VETTING_LEDGER.md. The 11.36 bp crypto figure is retracted (cost under-applied);
DOT/META/JUP rows were inadmissible (n=0); all rows here are re-costed at the class band and DSR-labelled.


## Revisions

*(append here; never edit a previous block)*


*Paper only. Zero capital. Not investment advice.*
## Revision 2026-11-23T02:54Z
changed:   FOREX row wording ("feed dead" -> "historical series dead, forward pick pipeline LIVE")
why:       found copy_trader_intel/data/forex_copytrader_picks.json: 5 FX picks, all dated 2026-11-20, all OPEN (1 = AUDJPY=X @105.887), 0 closed, 0 priced. So FX picks exist after the 2026-02-09 series end.
impact:    AUDJPY's "+14 trades to clear G3" is POSSIBLE, not impossible — but n_closed=0 and no FX pricing, so verdict stays DEAD.
evidence:  reports/fx_pick_pipeline_status.json (findtorontoevents_antigravity.ca @ feat/coms-final-notes-2026-11-20)

## Revision 2026-11-23T02:57Z — RECONCILED to COST OF RECORD
changed:   ALL COST cells + every net figure + BOND TLT n
why:       COST_OF_RECORD.md makes equity 12.0749 / ETF 6.7122 / FOREX 7.533 / bond-ETF 0.6144 / crypto 20–52 bp the ONLY admissible costs. My earlier COST cells (2.0 equity, 1.0 FX, 10.0 bond) were labelled `measured` but are provenance-invalid — the 2.0 came from mislabelling Copilot's 4.98 **spread-only lower bound**. I accept the operator's correction.
impact:    NO verdict or rank flips. Every net figure drops 4.7–10.1 bp; all picks still DEAD.
extra fix: old BONDS row said TLT n=1 — WRONG. Ledger symbol row is **TLT n=31, net −0.1624%, DSR 0.0001**. Corrected here.

**Restated at COD (top pick per class):**

| CLASS | PICK | n | gross bp | cost bp (COD) | net bp | DSR/N | verdict |
|---|---|---:|---:|---:|---:|---|---|
| STOCKS | CVX long | 35 | 180.9 | 12.0749 | **168.8** | 0.318/658 | DEAD |
| ETF | SOXX long | 37 | 36.3 | 6.7122 | **29.6** | 0.004/658 | DEAD |
| CRYPTO | ENJ long | 30 | 141.1 | 52.0 | **89.1** | 0.004/658 | DEAD |
| FOREX | AUDJPY long | 34 | 62.6 | 7.533 | **55.1** | 0.815/658 | DEAD |
| BONDS | TLT long | 31 | −11.2 | 0.6144 | **−11.8** | 0.000/658 | DEAD |
| MUTUAL_FUND | none | 0 | — | MER only | UNMEASURED | — | UNKNOWN |
| COMMODITY | none | 0 | — | 10/side ASSUMED | — | — | DEAD |
| OPTIONS / PREDICTION_MARKET / PRIVATE_CREDIT | none | 0 | — | UNMEASURED | — | — | UNKNOWN |

`endorsed_count` unchanged: **0**. Provenance now reconciles to COST_OF_RECORD.md §Rule 1.
evidence:  reports/picks_at_cost_of_record.json (findtorontoevents_antigravity.ca @ feat/coms-final-notes-2026-11-20)

## Revision 2026-11-23T03:48Z — RANKED ON THE 95% LOWER BOUND (operator method)
changed:   ranking basis (point estimate -> 95% bootstrap LOWER BOUND of net return); addressed every operator field
why:       OPERATOR ACCOUNTABILITY DIRECTIVE requires ranking on the LB, per-pick MECHANISM/COUNTERPARTY/WHY-SYMBOL/WHY-NOW/KILL, and n>=30 hard floor.
impact:    **The LB ranking is EMPTY (0 rankable).** Result unchanged but now correctly derived.

### LB-ranked strategies (n>=10, net of COST_OF_RECORD, 4,000-boot 2.5th pct)
| # | strategy | class | n | mean net % | **LB95 net %** | rankable |
|---|---|---:|---:|---:|---:|---|
| 1 | forex_rsi2_mean_reversion | FOREX | 97 | −0.0730 | **−0.0740** | NO |
| 2 | futures_momentum | COMMODITY | 98 | −0.2108 | −0.2145 | NO |
| 3 | forex_zscore_200d_fade | FOREX | 27 | −0.3694 | −0.4882 | NO |
| … | (all others) | — | — | negative | negative | NO |

**0 of 14 strategies have a positive 95% lower bound.** Note the key row: `forex_rsi2_mean_reversion` is the
*only* strategy that clears DSR at N=61 (0.9987) yet its **net lower bound is −0.074%** after the 7.5 bp FOREX
round trip — deflation passed, cost killed it.

### Answer to the operator's hard question (re-stated in this journal)
The retired 11.36 bp crypto row used a **flat 12.87 bp cost**, not the measured **20–52 bp** crypto band — it
under-applied cost by 7–39 bp. Re-costed at the band, 49/69 rows go net ≤ 0 and DOT is **−28 bp**. Every crypto
row in the earlier table is retracted; the current file uses COST_OF_RECORD only.

### Required fields for any endorsement — status
Per the directive, an endorsement needs MECHANISM, COUNTERPARTY, WHY THIS SYMBOL, WHY NOW, WHAT KILLS IT, plus
n>=30 and net > class round trip. **I endorse none, so I file none.** I will not invent a mechanism/counterparty
for a scan-ranked row — that would be the exact failure the directive names ("'my scan ranked it' is not a
mechanism"). `endorsed_count` stays **0**; the LB-positive list is empty.
evidence:  reports/lower_bound_ranking.json (findtorontoevents_antigravity.ca @ feat/coms-final-notes-2026-11-20)
