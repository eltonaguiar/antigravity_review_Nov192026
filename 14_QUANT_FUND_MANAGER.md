# Quant / Fund-Manager view — per-asset-class, risk-tiered candidate menu

**Date:** 2026-11-19 · **Author:** Kilo (as quant/fund manager), `universal-pisces`
**Grounding:** every candidate is drawn from the verified corpus (in-repo
walk-forward / live-realized numbers cited per row). Nothing here is claimed
money-ready — it is a **candidate menu** for the now-implemented forward clock,
tiered by risk budget. It answers: *"what quick viable strategies, at what risk"*
per asset class, plus the **method** to surface them.

**Rule 0 (unchanged):** no strategy is tradeable until it clears the forward gate
(n≥100, net PF CI-LB>1.0 or IR≥0.5, intrabar first-touch 100%, benchmark coverage
≥90%) — see `13_PEER_MERGE_STATUS.md` §2.

---

## Part 1 — The method: how to get "quick viable strategies"

A 5-step repeatable pipeline (all pieces exist in-repo):

1. **Harvest the verified top-3 per class** (Part 2) — these already passed
   walk-forward / live-realized; they are the fastest path because the
   statistical hurdle is partly cleared.
2. **Pre-register each as a pod** in `reports/audit3_confirmatory.json`
   (single source of registered pods). Nothing is tested without registration.
3. **Emit as shadow/paper legs** into `forward_observations` (the contract is
   implemented — `alpha_engine/forward_observations.py`), with a benchmark leg
   per card.
4. **Let the forward clock accrue** — promotion only on forward rows
   (closed on/after `registered_at`), read by `_promote()`.
5. **Tier by risk budget** (Part 3): conservative pods = high-conviction,
   low-vol, benchmark-relative; aggressive pods = higher-expected-value,
   higher-variance, smaller sleeve.

This is deliberately the **opposite** of adding new strategies — it converts the
already-built evidence into sizes.

---

## Part 2 — Per-asset-class fund-manager view (verified candidates)

### CRYPTO
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | VWAP mean-reversion (4h) | OOS 516/953, Sharpe 3.10, DSR 21.4, PBO 0.18, edge improving OOS | strongest crypto candidate |
| Conservative | Bollinger mean-reversion | OOS 38, Sharpe 1.38, WR 52.6% | safest/consistent |
| Balanced | Donchian breakout (BTC/ETH/SOL) | WF PASS all 3, DSR 7.24, costed Sharpe 5.0; PBO 0.676 | real but higher overfit risk |
| Balanced | Funding-rate arb (delta-neutral) | 70%+ forward pass (crisis); 1.5× capital gate | market-neutral diversifier |
| Aggressive | Turn-of-candle microstructure (minute) | Sharpe ~4.96 claimed, t>9, 7 venues | needs minute data/latency; pre-register on intraday first |
| Aggressive | Liquidation-cascade post-entry | descriptive; post-cascade rally +119% (historical) | unverified; observe only |
| Avoid | CRYPTO LONG directional (daily) | alpha −0.44%/pick vs hold | the class problem, not the product |

### EQUITY
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | Faber 200d TAA (SPY/QQQ) | Sharpe 1.74/1.65, PF 5.69/7.88 | broad bull capture, monthly |
| Conservative | Equity momentum 12-1 (QQQ) | Sharpe 1.63, WR 64.3%, PF 7.88 | classic J-T |
| Balanced | Equity Breakout Momentum | LIVE realized n=37, cum +37.6 | the one live-positive equity edge |
| Aggressive | PEAD (liquid large-cap, 60d) | most-replicated anomaly (Bernard–Thomas) | needs 500+ name screen |
| Aggressive | Overnight/intraday decomposition | proposed (trigger 30–50%/day) | fixes pick-starvation; pure OHLC |

### ETF
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | Monthly rotation / buy-and-hold beta | low-cost core; ETF intraday = cost artefact (234% slippage) | only monthly rotation survives |
| Balanced | Cross-sectional momentum (liquid sector ETFs) | 12-1 methodology | monthly rebalance |
| Aggressive | Intermarket flow / ETF creation-redemption | proposed; shares-outstanding free data | needs flow feed; verify |
| Avoid | Intraday ETF churn | slippage 234% of PnL | prohibited |

### FOREX
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | FX momentum USDJPY | Sharpe 2.02, PF 2.03, MC p=0.48 | B-tier |
| Balanced | G10 carry + 200d trend filter | gross 1.102 → net 1.035 (net-of-cost) | net ≈ coin-flip; needs trend overlay |
| Aggressive | Central-bank divergence / correlation arbitrage | practitioner claim | table targets, unbacktested |
| Prereq | FX data backfill + symbol mapping | `fx_prices` ends 2026-02-09; `XXXYYY=X` mapping broken | **blocker** — fix first |

### COMMODITY / FUTURES
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | Roll-yield harvesting | class WR 55.6%, PF 1.06; textbook | #1 quick-win idea |
| Balanced | Futures momentum | LIVE realized n=443, PF ~1.1, cum +17.4 | healthy trend signature |
| Aggressive | TSMOM (ETF proxy) | strongest documented premium; crisis alpha | needs proxy plumbing |
| Aggressive | Opening Range Breakout (NQ) | WR 74.6%, PF 2.51 (external) | verify in-repo |

### BOND / MUTUAL_FUND
| Tier | Candidate | Evidence | Verdict |
|---|---|---|---|
| Conservative | Yield-curve steepener (2s10s) | proposed; most-cited bond idea | 10–15 trades/yr |
| Balanced | Bond core (low-cost index) | SPIVA: ~93% active trails over 20y | the boring base |
| Aggressive | Credit/long-duration tilt | no corpus evidence | low data; defer |

---

## Part 3 — Risk-tier framework (sizing & controls)

| Bucket | Target | Max DD | Sleeve | Controls |
|---|---|---|---|---|
| **Conservative** | Sharpe ≥0.5, low turnover | ≤8% | 50–70% of risk budget | vol-targeted, benchmark-relative (IR≥0.5), half-Kelly cap 20% |
| **Balanced** | Sharpe 0.5–1.0 | ≤15% | 20–30% | −15% drawdown breaker halts; 3% daily loss limit |
| **Aggressive** | higher expected value, higher variance | ≤25% | 5–15% | −25% pause; ≤5% per pod; only after forward gate clears |

Cross-cutting risk rules (from the corpus):
- **Volatility scaling is free alpha** — inverse realized-vol sizing on all sleeves.
- **No single-source >60%, no single symbol >60%** per pod.
- **Benchmark leg mandatory on every card** (excess vs SPY/BTC/T-bills/AGG/GSG).
- **No new strategy while a P0 item is open** — every candidate above is already
  evidence-backed, not new.

---

## Part 4 — "Quick start" recommendation (fastest viable path)

Emit **at most 6 pods** immediately as paper/shadow on the forward clock:
1. CRYPTO VWAP MR (4h) — conservative
2. CRYPTO Bollinger MR — conservative
3. EQUITY Faber TAA — conservative
4. EQUITY Breakout Momentum — balanced
5. FOREX USDJPY momentum — conservative (after FX backfill)
6. COMMODITY roll-yield — balanced

These six are the highest-evidence, lowest-new-infrastructure items. Let the
forward clock accrue; promote only those clearing the gate. This is the fastest,
most honest route to "quick viable strategies" — it reuses what already passed
OOS rather than inventing more.

---

## Evidence index

All rows cite the verified corpus: `verified_strategies/HEDGE_FUND_EDGE_REPORT.md`
(VWAP/Bollinger/Donchian/Faber/EqMom/FXMom), `per_asset_class_pick_analysis_2026-04-21.md`
(live-realized equity/forex/futures), `quant-audit` (stop-fill, per-class PF),
`reports/selection_alpha_2026-11-19.json` (no class shows skill after costs).

*Not investment advice; nothing here is money-ready until the forward gate clears.*
