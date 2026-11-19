# Fund-manager playbook — quick viable strategies per asset class, by risk tier

**Role:** quant / fund manager. **Goal:** a *fast-to-stand-up*, evidence-grounded set of
strategies per asset class, offered at three risk levels (Conservative / Moderate /
Aggressive), with the sizing and verification rules that keep them honest.

**Ground rule from every review in this repo:** no *prediction* edge has been proven; the
only classes with positive out-of-sample statistics are EQUITY/ETF breakout (OOS Sharpe
+0.61/33 folds) and the pre-registered pods. So "quick viable" here means **harvest
documented risk premia expressed correctly** (vol-targeted, time/vol exits, no fixed TP),
plus **beta + cost discipline**. This is the honest ceiling at retail scale.

---

## 0. The universal "quick viable" method (applies to every row below)

1. **Emulate the literature, not the old pick pipeline.** Each strategy below maps to a
   documented premium (trend, carry, PEAD, value/quality/low-vol). Implement it *as
   documented* — vol-scaled size, symmetric time/vol exit, monthly/weekly cadence — never
   as fixed-TP/SL picks.
2. **Pre-register a pod**, then run it as a **shadow control alongside a beta benchmark**
   (SPY/BTC/AGG/GSG) so forward data accrues. Promotion requires the audit3/forward-ledger
   gates: n≥100 forward, net CI-LB>0 at 2× measured slippage, IR≥0.5, 90-day clock.
3. **Cost gate first:** reject any class whose average per-trade PnL is < 3× its measured
   round-trip slippage (ETF intraday and commodity intraday fail this — do not emit).
4. **Sizing:** inverse realized vol to a portfolio vol target; a fixed drawdown
   circuit-breaker per sleeve.
5. **Tier = allocation share + sleeve aggressiveness**, not "find the winner."

---

## 1. Equities (Stocks)

| Tier | Strategy | Method (quick) | Evidence / gate |
|---|---|---|---|
| **Conservative** | Core beta core (index) | Hold XEQT/VEQT + SPY/VTI; monthly rebalance; no tactical overlay | SPIVA: ~93% of large-cap active trails over 20y; `MF_CAN_WIN.md` |
| **Moderate** | Multi-factor tilt | Value/quality/low-vol factor ETFs, or a simple composite screen (momentum+quality+low-vol) rebalanced quarterly | Frazzini–Pedersen BAB; Baker–Bradley–Wurgler |
| **Moderate** | PEAD drift | SUE-ranked earnings surprise; long +1σ decile, 60-day hold, week rebalance, ≥500-name screen | Bernard–Thomas 1989; `EDGE_REVIEW` P3 |
| **Aggressive** | Breakout family (pre-registered pod) | `donchian-stock-breakout`/`rs-breakout-scout`/`vol-contraction-scout`/`adx-trend-scout`, monthly cadence, vol-scaled, time/ATR exit | **POD-EQUITY-BREAKOUT**; OOS Sharpe +0.61 |
| **Aggressive** | Momentum factor (Jegadeesh–Titman) | 6-month momentum, skip-month, top/bottom deciles, monthly | classic; 252-day backtest + forward |

## 2. Crypto

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | BTC/ETH hold, capped sleeve | ≤5–10% of NAV, no leverage, no TP/SL | risk-premia-free; pure beta exposure |
| **Moderate** | Trend-following (TSMOM) on majors | vol-targeted trend, ensemble of 3–12m lookbacks, symmetric time exit | Moskowitz–Ooi–Pedersen; Hurst 100y evidence |
| **Aggressive** | POSITION-horizon signal | The only positive crypto bucket (n=33, WR 69.7%, PF 3.18); small size; **only after the stop-fill fix** | `PER_CLASS_PATHS_TO_PROFIT.md` |
| **Do NOT** | Crypto SWING, fixed-TP score bands, daily RSI2, longs in a drawdown regime | — | KILL / negative alpha (−0.442%/pick) |

## 3. Forex

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | none — do not trade | data ends 2026-02-09; cost/liquidity poor | `AUDIT_SURFACE_REVIEW` |
| **Moderate** | G10 carry + trend filter (P2) | rank G10 by forward discount; long top-3/short bottom-3; vol-targeted; 200d trend overlay | `EDGE_REVIEW` P2; H21–23 carry work |
| **Aggressive** | not recommended | FX breakeven WR 16pp above actual | `PER_CLASS_PATHS_TO_PROFIT.md` |

## 4. Bonds / Fixed Income

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | Short-duration ballast | SGOV / SHY / BND; core allocation | low vol, positive carry |
| **Moderate** | Duration rotation / TAA | long duration when trend up, short/flat when down (Faber TAA style), monthly | classic TAA |
| **Aggressive** | Credit-spread overlay (small) | high-yield ETF tilt only over a broad investment-grade core | limited evidence; keep small |

## 5. ETFs

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | Balanced / dividend core | broad multi-asset ETF | beta core |
| **Moderate** | Dual momentum | `etf_dual_momentum` (WALKFORWARD PASS, PF 2.75, n=11 — small n, forward-test) | walkforward report |
| **Aggressive** | Managed-futures proxy / TSMOM | Horizons HMF / DBMF / KMLM-style vehicles, or self-built futures trend | `EDGE_REVIEW` P1 |
| **Warning** | ETF intraday | measured slippage = 234% of per-trade PnL → **monthly cadence only** | `slippage_validation` |

## 6. Commodities / Futures

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | Gold/commodity ETF hedge | small allocation, defensive | hedge, not alpha |
| **Moderate** | TSMOM trend across futures (P1) | vol-scaled trend on 20–60 liquid futures; 3–12m lookback ensemble; monthly | strongest documented premium; crisis alpha |
| **Aggressive** | Managed futures | same as above with higher vol target | watch commodity intraday cost (422% of PnL) |

## 7. Mutual Funds

| Tier | Strategy | Method | Evidence / gate |
|---|---|---|---|
| **Conservative** | Index funds | FXAIX / VTSAX / FZROX (ER ≤0.20%) | `MF_CAN_WIN.md`; FXAIX +73% net 5y |
| **Moderate** | Low-cost target-date | simple glide path | cost discipline |
| **Aggressive** | Sector funds with momentum overlay | rotate within broad sectors using 3-month momentum | speculative; small sleeve |

---

## 8. Suggested "first 30 days" quick-viable stand-up

| Week | Action |
|---|---|
| 1 | Stand up the **shadow-control harness**: emit the 3 pre-registered pods + 2 known-fuller controls at paper size, benchmarked vs SPY/BTC/AGG. Fix the forward-ledger ingestion adapter. |
| 1–2 | Deploy the **cost gate** (3× round-trip) and the `at_issue_*` stamping fix (leaky walk-forward). |
| 2 | **Pre-register** one pod per chosen sleeve: EQUITY breakout (aggressive), FX carry (moderate), futures TSMOM (moderate). |
| 3 | Start **forward paper** on all three; log daily; begin the 90-day clock. |
| 4 | Monthly: rebalance beta core to 70–85% NAV; size sleeves by inverse vol to a fixed portfolio vol target. |

## 9. Realistic expectation (write this on every card)

- **Sharpe target:** ~0.5–1.0 *on the sleeve* at small capacity — that is the realistic
  prize. The beta core captures most of the long-run return by itself.
- **Risk tiers = allocation, not "winners":** Conservative ≈ 85% beta / 15% sleeves;
  Moderate ≈ 75% beta / 25% sleeves; Aggressive ≈ 65% beta / 35% sleeves (sleeves still
  each ≤5% of NAV, vol-targeted).
- **Kill discipline:** any pod with forward CI-LB ≤ 0 at day 30/60 is retired and recorded
  in the "Retired with reason" table. No ego.

*Not personalized investment advice — sizing depends on each investor's situation.*
