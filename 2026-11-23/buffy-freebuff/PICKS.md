# Buffy (freebuff) — final picks per asset class

**Generated:** 2026-11-23T02:27Z · **Ticket:** $25,000 (every bp figure below is per $25,000 unless stated) · **Paper only. Zero capital. Not investment advice.**

**VERDICT: 0 of 10 pick objects pass all five gates.** Best is EQUITY at 4/5, failing only the deflated-Sharpe gate. Five gate passes across ten picks is the whole summary of the programme: the strategies are mostly fine and the *statistics* are not yet there.

Gates: **G1** gross > 2× measured round-trip cost · **G2** hold ≥ 1 day · **G3** DSR ≥ 0.95 at the declared trial count · **G4** net annualised > 4.32% T-bill on committed capital · **G5** recorded before the outcome.

Two things differ from the other entries in this folder, and both matter for how you read the numbers: my EQUITY stats are **strategy-level** (one 179-trade series), not per-name, and my ETF picks are **forward-only with zero records**, so their gross/net are `UNMEASURED` rather than backtested.

---

## EQUITY — H-201 cross-sectional 6-month momentum, top 3 of 44, monthly

Live names recomputed from the pod's own frozen 44-name universe at the 2026-11-19 close (6-month formation, base 2026-05-21). **The pod's recorded book is the authority, not this recompute** — read `reports/pods/forward/POD-EQUITY-H201-XSMOM-6M_anchor.json` in the research tree for its set-at state.

| # | symbol | 6m return | n | gross bp/day | cost bp (RT) | net bp/day | DSR | hold | gates | FAILS |
|---|--------|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | XLV | +20.77% | 179 | 11.521 | 12.0749 | 10.946 | 0.9469 | 126d | 4/5 | **G3** |
| 2 | KO | +19.86% | 179 | 11.521 | 12.0749 | 10.946 | 0.9469 | 126d | 4/5 | **G3** |
| 3 | MSFT | +19.35% | 179 | 11.521 | 12.0749 | 10.946 | 0.9469 | 126d | 4/5 | **G3** |

- **G1 pass, by 50.9×.** Round-trip breakeven is **614 bp** (C-017); measured cost is **12.0749 bp**, so cost is not the question for this cell. `k* = 50.9`.
- **G3 FAIL, and it is the only failure.** DSR **0.9469 at N=29**, and **0.9490 even at N=28** once the series' own skew (−0.050) and kurtosis (12.254) enter the denominator. The cell clears only at **N ≤ 27**; 29–31 trials are declared. `net_bp/day` amortises cost over a 21-session rebalance (`12.0749/21 = 0.575`), which is the only assumption in the row.
- **The number I will not bury:** vol-matched to SPY the excess is **−0.533**. Raw +7.246 bp/day CI-LB, matched negative. That is what a high-beta proxy looks like, and G4 passing at 27.6% annualised does not address it.
- **Forward clock:** day 15 of a 20-day sanity gate, and losing. Last recorded mark in the copy I have: **−539.5 bp** excess at day 15 (an older copy of the same file read −836.4, so verify against the live tree before quoting either). The gate needs **137** forward days at N=29, not 77 — 77 was withdrawn (C-029).
- **Cost is disputed, and I am flagging rather than resolving it:** I measure **12.0749 bp**; a peer's note on the bus measures **1–5 bp** on 191 names at 0.008% of ADV. At $25,000 both are small, and k*=50.9 survives either. It is not small for the families that die near their cost floor.

## ETF — R4b 12-month absolute momentum, top 5 of 20, monthly

Ranking recomputed at the 2026-11-19 close (base 2025-11-18). **No ledger records exist — the clock's first legitimate record is 2026-11-30.** These are the names the frozen rule nominates today, not results.

| # | symbol | 12m return | n | gross bp | cost bp (RT) | net bp | DSR | hold | gates | FAILS |
|---|--------|---:|---:|---|---:|---|---:|---:|---|---|
| 1 | XLE | +37.55% | 0 | UNMEASURED | 6.7122 | UNMEASURED | n/a | 21d | 2/5 | G1G3G4 |
| 2 | XLV | +18.24% | 0 | UNMEASURED | 6.7122 | UNMEASURED | n/a | 21d | 2/5 | G1G3G4 |
| 3 | XLK | +15.77% | 0 | UNMEASURED | 6.7122 | UNMEASURED | n/a | 21d | 2/5 | G1G3G4 |
| 4 | IWM | +14.32% | 0 | UNMEASURED | 6.7122 | UNMEASURED | n/a | 21d | 2/5 | G1G3G4 |
| 5 | EFA | +10.09% | 0 | UNMEASURED | 6.7122 | UNMEASURED | n/a | 21d | 2/5 | G1G3G4 |

- **G1 and G4 are `UNMEASURED`, not failed** — there is nothing to measure yet. G3 is `n/a` deliberately: this family has been tested **once, forward**, so its trial count is 1 and its deflation bar stays near nominal. That is the entire reason it exists.
- All five clear the **4.32%** absolute hurdle, so the rule is fully invested rather than in cash this month.
- G5 **passes**: pre-registered 2026-11-23 (`docs/preregistration/ETF_TREND_FORWARD_2026-11-23.md`), before the first record. No backtest of this rule will be run again.
- **XLE at +37.55% is an energy concentration, not a diversified pick** — 2.4× the next name. If the forward record ever looks good, check it against an XLE buy-and-hold before believing it.
- **XLV appears in both EQUITY and ETF.** That is correlated exposure across two "independent" picks, not diversification.

## CRYPTO — funding carry is real; allocation stays 0

| # | symbol | n | gross bp/day | cost bp | net bp | DSR | hold | gates | FAILS |
|---|---|---||---:|---|---:|---|---:|---:|---|---|
| 1 | BTCUSDT perp, delta-neutral carry | 111 | 1.9252 | **UNMEASURED** (VIP0 assumed) | UNMEASURED | n/a | 1d | 1/5 | G1G3G4G5 |
| 2 | BTC-USD (beta only) | — | — | — | — | — | — | 0/5 | **KILL** |

Carry is the best risk-adjusted object we have and it stays at **0% allocation** because the fee tier is an assumption, and because funding decay kills the overlay (avoids 1,738 bp, costs 15,440 bp). A pick whose cost is assumed cannot pass G1. **BTC beta is not a pick** — 49.1% CAGR with −83.0% drawdown and Sharpe 0.911 is compensated risk, not selection.

## No pick — and why

| class | reason |
|---|---|
| BOND | signal cell is already **negative** (CI-LB −0.453). Bond momentum dead at 0 bp/side. Not risky — just no edge. |
| MUTUAL_FUND | CI-LB +0.997 bp/day but MDE 4.27; needs **73.7 years** of daily data to detect 1.92 bp/day. Untestable here. |
| INDEX | alias of ETF; SPY-200d null (53.4, excess −6.8 pp). Inherits the R4b pick or nothing. |
| FOREX | cost is an upper bound only (7.533 bp, Sunday reopen); breakeven 4.3038 bp **below** cost; CI [−4.32, +11.09] spans 0. |
| COMMODITY | roll-corrupted continuous series. No re-test is meaningful until that is procured. |
| PENNY / MEME | MDE 19.73 bp/day ≈ **1,572 years**; MEME cost unmeasurable (SHIB: 84.3% zero-range bars). |
| FUNDING-CARRY (allocated) | see CRYPTO row 1 — await a measured venue fee tier. |

## The one real-money action on this page

Buy a low-cost broad index ETF as a **buy decision, not an edge**. Nothing above clears G3, so nothing above earns a position on evidence. The vol-targeted 60/40 overlay (Sharpe 0.750→0.895, maxDD −31.4%→−22.4%) is the only tested improvement available, and it is risk control, not alpha — on a single asset it *lowers* return.

---

*Sources: `reports/asset_class_risk_reward_ladder_2026-11-23.md`, `reports/dsr_recompute_2026-11-23.json` (C-029), `docs/preregistration/ETF_TREND_FORWARD_2026-11-23.md`, `reports/claim_register.json` (29 claims), `docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md`. Independently reviewed against `notes/asset-class-risk-edge-copilot-20261123`; the two cost figures and the 20-vs-24 ETF universe differ and are flagged above rather than silently reconciled.*

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
