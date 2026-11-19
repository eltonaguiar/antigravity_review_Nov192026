# Audit2 content recommendation — viable strategies, statistical measures, methodology quotes

**Date:** 2026-11-19 · **Author:** Kilo (`universal-pisces`)
**Method:** three parallel read-only sweeps of the source repo's `.MD/.MD`
documents (strategy catalogs/inventories; statistical/validation/rigor docs;
per-asset-class research), then cross-checked against the audit3 ledger. Every
row is cited to `file:line`. Anything flagged as a trap (small n, backtest-vs-
realized, gross-vs-net, survivorship) is marked.

This is a **content plan for `/audit2`** (currently a 404; being built by a
peer swarm). It is not investment advice and not a claim that any item is
money-ready — it is what the buried `.MD` files are worth surfacing on the page.

---

## 1. The single most useful buried methodology (quote to lead audit2 with)

From `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` and the repo's
own edge review — these are the project's best self-stated principles, worth
printing verbatim on audit2 as a "doctrine" banner:

> "Public daily OHLCV is arbitraged by thousands of participants. Remaining
> public edges are (i) risk premia (persistent, compensated, capacity-limited)
> and (ii) microstructure/flow (needs intraday/TAPE/options data or venue
> access). Everything else is noise dressed as signal." — `EDGE_REVIEW_2026-11-19.md:48`

> "Volatility scaling is free alpha. Simply scaling positions by inverse
> realized vol improves Sharpe by 0.3+ for any momentum strategy." — `RARE_HOURLY_CRYPTO_STRATEGIES_RESEARCH.md:613`

> "Edge, if any exists, should be expressed with symmetric, vol-scaled,
> time-based exits and sized by vol targeting — the expression of every trade
> changes the statistics more than the signal does." — `EDGE_REVIEW_2026-11-19.md:41`

> "With 700+, every backtest 'winner' is pre-purchased p-hacking… The binding
> constraint is hypothesis quality and trial budget, not techniques." — `EDGE_REVIEW_2026-11-19.md:33`

> "One great signal is worth less than five decent independent ones" (10
> streams @ Sharpe 0.5, ρ≈0.1 → stack Sharpe ≈ 1.5). — `EDGE_REVIEW_2026-11-19.md:66`

> "1bp of cost a day ≈ 20% annual leakage." — `EDGE_REVIEW_2026-11-19.md:67`

---

## 2. Viable strategy shortlist (tiered, with evidence)

### Tier A — already pass in-repo walk-forward / live-realized (strongest candidates)

| Strategy | Class | Evidence (n, metrics) | Source | Caveat |
|---|---|---|---|---|
| **VWAP mean-reversion (4h)** | CRYPTO | OOS 516/953 trades, WR 45.7%, PF 1.323, Sharpe 3.10, DSR 21.4, PBO 0.18 | `verified_strategies/HEDGE_FUND_EDGE_REPORT.md:29,40,46` | Best-supported crypto candidate; needs vol-scaled, time-based exits |
| **Bollinger mean-reversion** | CRYPTO | OOS 38 trades, WR 52.6%, PF 1.673, Sharpe 1.38 | `HEDGE_FUND_EDGE_REPORT.md:30,42,82` | Small n but passes walk-forward |
| **Equity Breakout Momentum** | EQUITY | LIVE realized n=37, WR 59.5%, cum +37.6 | `per_asset_class_pick_analysis_2026-04-21.md:95` | The clearest live positive in the one positive-OOS class |
| **Faber 200d Tactical Asset Allocation** | EQUITY/ETF | Sharpe 1.74 (SPY), PF 5.69 | `HEDGE_FUND_EDGE_REPORT.md:19,160` | B-tier; broad bull capture, monthly |
| **Equity momentum 12-1** | EQUITY | Sharpe 1.63, WR 64.3%, PF 7.88 | `HEDGE_FUND_EDGE_REPORT.md:22` | B-tier; Jegadeesh–Titman |
| **FX momentum (USDJPY)** | FOREX | Sharpe 2.02, WR 40.5%, PF 2.03, MC p=0.48 | `HEDGE_FUND_EDGE_REPORT.md:17` | B-tier |
| **forex_rsi2_mean_reversion** | FOREX | LIVE realized n=523, cum +34.6, WR 28.3% | `per_asset_class_pick_analysis_2026-04-21.md:124` | Low WR, large winners; best FX engine |
| **futures_momentum** | COMMODITY | LIVE realized n=443, PF ~1.1, cum +17.4 | `per_asset_class_pick_analysis_2026-04-21.md:157` | Healthy trend signature |

### Tier B — academically strong / conditionally viable (candidate pods)

| Strategy | Class | Claimed | Source | Caveat |
|---|---|---|---|---|
| Time-Series Momentum (TSMOM) | multi-asset | Sharpe 0.9–1.2, score 9.8, crisis alpha | `STRATEGY_SELECTION_COMMITTEE_REPORT.md:63,1230` | Strongest documented premium; implement regime-filtered |
| Funding-rate arbitrage | CRYPTO | viability 88, expectancy 1.02; 70%+ forward pass | `STRATEGY_INVENTORY_COMPLETE.md:25,226`; `STRATEGY_CRISIS_ANALYSIS.md:57` | Market-neutral; capital/fee-heavy; gate vs cash/1.5× cost |
| Pairs / statistical arbitrage (EG coint) | multi-asset | Sharpe 1.0–1.5; viability 79 | `STRATEGY_INVENTORY_COMPLETE.md:26,227`; committee `:151` | Use EG, not KSS (KSS = documented trap) |
| Value + Momentum (Asness) | multi-asset | Sharpe 1.0–1.3 | committee `:195` | Diversifier combo |
| Opening Range Breakout (NQ) | FUTURES | WR 74.6%, PF 2.51 | committee `:341–351` | External YouTube backtest — verify in-repo |
| Commodity roll-yield harvesting | COMMODITY | proposed, class WR 55.6% PF 1.06 | `strong_strategy_per_asset_class_2026-04-20.md:147–149` | #1 quick-win idea; not yet implemented |
| Equity overnight/intraday decomposition | EQUITY | proposed, trigger 30–50%/day | `strong_strategy_per_asset_class_2026-04-20.md:76` | Fixes equity pick-starvation; pure OHLC |

### Tier C — flagged traps (do NOT surface as wins)

| Trap | Why | Source |
|---|---|---|
| Connors RSI-2 | DEAD in-repo: WR 60–69% but negative expectancy (avg_loss ≫ avg_win); crypto Sharpe −2.6 | `HEDGE_FUND_EDGE_REPORT.md:64–74,179–182` |
| ICT/SMC order blocks alone | "negative results almost everywhere" without confluence | `SMC_TRADING_GUIDE...md:89`; `STRATEGY_GRAVEYARD.md:34,49,50` |
| Meme scanner / pump watch "forward 580%" | contradicts live 5% WR v2 | `strategy_catalog.md:304` |
| Cross-sectional momentum / residual momentum | inventory marks residual momentum viability 42, −75% degradation | `STRATEGY_INVENTORY_COMPLETE.md:249` |
| Tiny-n ML cohorts (n=5–35) | statistically fragile regardless of PF | `STRATEGY_EXPANALYSIS.md:20–29` |
| KSS cointegration | >160% max drawdown; use EG | `RARE_HOURLY...md:98` |

---

## 3. Statistical measures worth standardizing into audit2

From the validation/rigor `.MD` set (see `07_/08_` reviews for detail). These
are the measure names the docs use — audit2 should render a consistent, labeled
subset on every card:

- **Expectancy (net/trade) and net 95% bootstrap CI** — the headline edge test
  (`TESTING_PROTOCOL.MD`; audit3 `conventions`).
- **Profit factor (PF)** — only as a secondary descriptor, never the gate.
- **Win rate (WR)** — always labeled as descriptor, with `n`; never gross.
- **Sharpe / Sortino / IR vs benchmark** — quote the OOS walk-forward Sharpe per
  class (`QUANT_EDGE_ANALYSIS_PER_ASSET_CLASS.md`: DSR>0.95, PBO<0.05,
  WFE≥60%, live Sharpe>0.5, n≥100).
- **Deflated Sharpe Ratio (DSR)** and **PBO (probability of backtest
  overfitting)** — the anti-overfit pair.
- **Multiplicity**: Benjamini–Hochberg q, Bonferroni α/m, confirmatory vs
  discovery namespaces.
- **Cost realism**: measured slippage per class; 2× cost-stress column; win =
  net pnl>0.
- **Stability**: chronological split-half / rolling cohort means.
- **Concentration**: top-symbol share, top-source share.
- **Coverage**: scored rows / total closed rows (denominator always visible).
- **Regime & vol**: Hurst/HMM/regime label; realized-vol scaling.

Conflation bugs found in the docs to explicitly avoid on audit2 (from
`QUANT_DEBUG_PICKS.md`, `QUANT_DEP_DEBUG.md`, `risk_adjusted_analysis.py`):
zero-Sharpe/high-Sortino inconsistency, stress-multiplier-as-result, unit
bug 100× PnL, 24h-resolution WR bias, score-inversion, gross-vs-net.

---

## 4. Concrete audit2 page architecture

Based on the buried material, recommend `/audit2` surface:

1. **Doctrine banner** — the five quotes in §1 (collapsible).
2. **Verdict table** — class × verdict × n × net-expectancy CI × DSR × 2×cost
   (single canonical denominator; reuse audit3 ledger, not a second source).
3. **Candidate-pod registry** — Tier A (§2) as pre-registered pods with a
   forward-observation table and target-n from a power statement.
4. **Trap / graveyard panel** — Tier C items, each with the one-line reason
   (so nobody re-literates a killed idea).
5. **Statistical glossary/measures panel** — §3, with definition per measure and
   the exact unit/gate, so the numbers are self-explanatory.
6. **Methodology & provenance** — generator version, input SHA-256, git SHA,
   source path, coverage % (never a `/tmp` path).
7. **Freshness strip** — per-table staleness with green/yellow/red and CI-fail
   (backed by `db_freshness` + watchdog).

Everything must be data-live from tracked files (no hardcoded win rates) and
cross-linked to the audit3 ledger so `/audit`, `/audit2`, `/audit3` never
disagree on a class again.

---

## Evidence index

All rows cite source-repo paths + line numbers above. Cross refs: `07_…` /
`08_…` peer reviews, `06_…` corroboration.
