# KILOCODE_VSCODE — FINAL findings per asset class + overall ranking

**Agent:** Kilo (VS Code) · **As of:** 2026-11-24 · **Paper only, zero capital, not investment advice.**
This is the consolidated, current answer. It supersedes older per-topic notes in this folder; detail/evidence is linked at the bottom.

## THE VERDICT (one line)
**0 of 10 asset classes is investable.** No strategy in the programme has demonstrated alpha above the detection floor. The
only defensible real-money action is a **low-cost, CAD-traded broad index ETF** — a *buying* decision (beta), not an edge.

## PER-ASSET-CLASS FINDINGS
| class | best candidate | status | why (measured) |
|---|---|---|---|
| **STOCKS (EQUITY)** | CVX | **DEAD** | DSR 0.318 (bar 0.95); alpha-negative; no hold-times in repo → G2/G4 unmeasurable; survivorship-biased universe |
| **ETF** | SPY / SOXX | **DEAD as signal** | beta, DSR 0.004; **this is the vehicle for the real-money answer**, not an alpha source |
| **CRYPTO** | ETH / ENJ | **DEAD** | net ≤ 0 at 20–52 bp cost for most cells; DSR < 0.07 |
| **FOREX** | AUDJPY | **DEAD** | `beta_dominant=true`, `alpha_gate` FAILED, `recent_ok=false` (last 8 trades −0.54%); marked open FX positions lost ~5%; 0/24 closed |
| **BONDS** | SGOV (T-bill) | **CASH HURDLE (not a pick)** | ~3.8%/yr risk-free; TLT negative over window |
| **MUTUAL_FUND** | FXAIX / FZROX (index) | **BETA — fees decide** | 0.995–0.998 correlated to SPY; same beta; low MER is the only lever |
| **COMMODITY** | — | **DEAD** | no nameable mechanism; negative expectancy |
| **OPTIONS / FUTURES / PREDICTION_MARKET / PRIVATE_CREDIT** | — | **UNRANKABLE** | no data layer / no measured OOS edge |

## OVERALL RANKING — what to actually buy (for a real human)
1. **Broad low-cost index ETF, CAD-listed & CAD-traded** (VFV/XUS for S&P 500, or **XEQT/VEQT** all-in-one).
   *Why:* same beta as every "signal" here, but cheapest and simplest; no FX conversion cost; **not US-situs** (avoids US estate tax). 
2. **US-listed VOO — inside an RRSP only** (US–Canada treaty exempts dividend withholding), converting CAD→USD cheaply (Norbert's gambit); watch the ~$60k USD US-estate threshold.
3. **60/40 (or a conservative all-in-one like VCNS/VCIP)** if a ~25% drawdown is intolerable — 6.85%/yr, −20.7% DD measured.
4. **Cash (SGOV)** is the hurdle every active idea must beat (~3.8%/yr); it is not an edge.
**None of the programme's strategies ranks above #4** — they are beta-dominant with no proven alpha.

## CONTEST ENTRY (published)
`CONTEST/_incoming/KILOCODE_VSCODE/picks.json` — 4 picks, $1,000: **SPY** (R≈1.5), **VTSAX** (fund, no TP/SL), **SGOV**, **BTCUSD**
(flagged 8-mo stale). Official-scorer dry-run: 4 picks, **0 void**, 3 R-scored + 1 fund. Declined equity/FX/commodity/options/
futures/prediction (no dated price; will not fabricate brackets). Not gaming R (stops wider than one bar). **No fills yet**, so
no realized R; the **R-bootstrap falsifier is built and calibrated** (clear winner 97.8% → allowed; null 0%) and will run on
fills. Ranking rule §7 currently **confirmed: no ranking** (bracket-fit bootstrap → 0/2000 unique winners).

## INDEPENDENT CORROBORATION (peer, not mine)
The `29_CELL_SWEEP_CONTEST_2026-11-24` round independently filled EQUITY/FOREX coverage: `SPY/donchian/1d` n=121 net **−14.9 bp** (CI [−25.9,−3.3]) KILL; `SPY/breakout/1d` n=163 **−18.7** KILL; `EURUSD/trend_pullback/1d` n=117 **−21.7** KILL. Class averages: **EQUITY −20.7 bp**, **FOREX −22.3 bp**, **0 survivors**. → the null is **not crypto-specific**; it holds across equities and FX too. This matches my census (96/96 measured cells KILLED).

## EVIDENCE ANCHORS (verified)
- **Alpha gate:** 0/69 symbols, **0/362 cells** pass; best class FOREX α-CI-lo −0.144%; gate is sound but **underpowered** (MDE ≈ 5.08%/yr on 33.8y SPY).
- **1000-cell backlog (main repo):** **106 killed** (96 real measurements — all KILLED, **0 survivors** — plus 10 INSUFFICIENT_TRADES rsi2/ma_cross@1d) · **891 blocked_no_data** (no bars) · 3 claimed · open 0.
- **Fees:** 0.03% vs 1.80% MER = $755k vs $458k per $100k over 30y (~39% less).
- **Risk:** SPY −24.5% drawdown, ~14 months to recover; missing the best 10 days cut +72.6% → +16.8%.

## COST-INDEPENDENCE (peer cost-vs-signal, `30_COST_STRUCTURE_2026-11-24`)
Median **GROSS** bp/trade across 44 measured cells = **−1.51** (net −27.51 at 26 bp). So the typical cell has **no gross
edge at all** — the null is a **signal problem, not a cost artifact**; a cost breakthrough cannot rescue a negative-expectancy
signal. The few gross-positive cells (`SOL breakout +97.9`, `BTC bb_meanrev +76.5`) still have CIs spanning 0 → INCONCLUSIVE.

## LABELLING NOTE (cross-repo consistency)
The DONE_CONDITION classifies a cell whose 95% CI spans 0 as **KILLED**; the `29_CELL_SWEEP` labels the same cells
**INCONCLUSIVE**. They are equivalent — both mean **no proven edge** (the CI cannot reject zero). The programme does **not**
promote either to a survivor. Verified: across both sweeps, **0 cells have a positive CI lower bound**.

## CORRECTIONS LOG (integrity)
Withdrew "zero alpha" (→ "no alpha above MDE"); withdrew "value premium +0.11%→+2.89%" (the +0.11% is **equity-class alpha**, and
value/HML was **never measured**; yfinance default is already adjusted); retracted F4 "MF beats its ETF"; corrected Sortino (/N);
fixed cost model to per-class COST_OF_RECORD. All logged in the linked files.

## DETAIL / EVIDENCE FILES (in this folder)
`PROGRAMME_ALPHA_SWEEP_2026-11-23.md` · `ALPHA_GATE_POWER_CORRECTION_2026-11-23.md` · `FUNDS_WHAT_TO_BUY_2026-11-23.md` ·
`INVESTOR_FAQ_2026-11-23.md` · `MECHANISM_AUDIT_2026-11-23.md` · `CLASS_VERDICT_CORRECTED_2026-11-23.md` ·
`STATE_OF_PROGRAMME.md` · `PROCUREMENT_SPECS.md`.

*Paper only. Not investment advice.*
