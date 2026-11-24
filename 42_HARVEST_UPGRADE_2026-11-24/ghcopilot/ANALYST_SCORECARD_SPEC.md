# Analyst scorecard — specification

**Scope:** what can be computed, from which fields, at what cost. Does not duplicate
`../DESIGN_ANALYST_SIMULATION.md` (commit `ae831a8`), which already fixes the scorecard filter
(its §2) and the seven disclosure biases (its §6). This document adds the two things that design
does not contain: **the free-vs-paid field matrix**, and **the estimator set with the β/CI method**.

> **The blocking fact, stated first.** A per-analyst track record cannot be built from the
> credentials we hold. `finnhub /stock/upgrade-downgrade` returns `HTTP 403`,
> `finnhub /stock/price-target` returns `HTTP 403`, `fmp /api/v4/upgrades-downgrades` returns
> `HTTP 429 "Limit Reach"` (all measured 2026-11-24, recorded in
> `../../docs/data/harvest_signals.json → sources[]`). Without a dated, firm-attributed rating-change
> event feed, there is no `(analyst, date, action)` row to score. Any "analyst P/L" published today
> would be fabricated. This spec therefore separates what is computable **now** from what needs a
> purchase.

---

## 1. Event-study estimators

For an event `(symbol i, date t0, direction d_i)` with `d_i = +1` upgrade/initiation-to-buy,
`−1` downgrade/initiation-to-sell, `0` reiteration:

**Raw and abnormal return over horizon `h`:**

```
r_i(h)   = P(t0+h) / P(t0) − 1                     total return, split/dividend adjusted
AR_i(h)  = r_i(h) − r_b(h)                          b = benchmark (sector ETF, SPY fallback)
CAR(h)   = (1/n) Σ_i AR_i(h)                        equal-weighted cohort CAR
```

**Standardised (BMP-style) test**, which is the one to report because it handles event-induced
variance:

```
SAR_i(h) = AR_i(h) / s_i(h)                         s_i = estimation-window σ of AR_i
Z        = Σ_i SAR_i / sqrt(Σ_i s_i²/σ²)            ~ N(0,1) under H0
```

**Calendar-time portfolio** (the cross-check that survives cross-correlation):

```
For each month m: form portfolio of all symbols with an active endorsement in m
Regress   Rp(m) − Rf(m) = α + β·(Rm − Rf) + ε      → report α with HAC (Newey-West) errors
```

Report **both** the event-time CAR and the calendar-time α. When they disagree, the event-time
result is the one that is usually wrong (overlapping windows inflate it).

**Price-target skill:**

```
PT_MAE%      = mean | PT − P(t0+h) | / P(t0)
PT_optimism% = mean ( PT − P(t0+h) ) / P(t0)        > 0 means systematically too high
```

**Shrunk alpha and reliability badge** — use exactly the rules in `../DESIGN_ANALYST_SIMULATION.md`
§2 (`k ≈ 30` shrinkage; badges A/B/C/`INSUFFICIENT_DATA`, n≥15 floor, BH at q=0.05). Do not
re-derive them here, or the two documents will drift.

---

## 2. β and confidence interval for the Layer B mappings

Layer B maps an *event market* to an *asset*. Its β answers: how much does the asset move per unit
of implied-probability change?

```
Δp_t  = p_t − p_{t−1}            daily change in market-implied probability
y_t   = r_asset,t − r_benchmark,t   daily excess return of the mapped proxy
β     = Σ(Δp_t − mean Δp)(y_t − mean y) / Σ(Δp_t − mean Δp)²
SE    = sqrt( σ²_ε / Σ(Δp_t − mean Δp)² )        σ²_ε from the residuals
CI    = β ± 1.96·SE                               with HAC (Newey-West, lag ≈ 10) errors
```

**Minimum requirements before this is publishable:** ≥ 250 overlapping daily observations, the
probability series taken as-of each day (never the settled value), and the CI excluding 0.

**Current status: not estimable.** We hold no matched time series of market-implied probabilities
and asset returns at daily frequency. `out/crowd_layer.json → layer_b_event_mappings[].beta` is
`null` on every row and `beta_status` states the reason per row. Do not fill this with a
cross-sectional correlation between unrelated series.

---

## 3. Free versus paid, measured

| Field needed for a scorecard | Free now? | Where / evidence |
|---|---|---|
| Monthly consensus distribution | **yes** | `finnhub /stock/recommendation`, `HTTP 200`, 71 rows, recorded in `docs/data/harvest_signals.json` |
| Rating-change events with **firm** attribution | **no** | `finnhub /stock/upgrade-downgrade` → `HTTP 403`; `fmp /api/v4/upgrades-downgrades` → `HTTP 429` |
| Rating-change events with **individual analyst** name | **no** | Not exposed by either vendor at any tier we hold; Benzinga / LSEG / Capital IQ territory |
| Price targets (mean / high / low) | **no** | `finnhub /stock/price-target` → `HTTP 403`; `fmp /api/v3/price-target-consensus` → `HTTP 429` |
| Daily prices for forward returns | **yes** | Tiingo `/tiingo/daily/<ticker>/prices` → `HTTP 200` (AAPL 3,966 B, verified 2026-11-24); key already in env |
| Benchmark / sector ETF prices | **yes** | same Tiingo endpoint (SPY metadata `HTTP 200`) |
| Fund holdings for look-through | **yes, per issuer** | SSGA xlsx `HTTP 200`; SEC N-PORT `HTTP 200`; iShares CSV blocked (HTML body) — see `LOOKTHROUGH.md` |
| Institutional holdings (13F) | **yes** | SEC EDGAR, public, no key |
| Insider transactions (Form 4) | **yes** | SEC EDGAR, public, no key |
| Short interest | **yes** | FINRA `HTTP 200`, CSV, needs explicit settlement dates |
| Futures/commodity positioning | **yes** | CFTC COT, `HTTP 200`, `commodities.json`-style dataset `6dca-aqww`; BITCOIN history from 2017-12-19 |
| Per-analyst historical accuracy | **no** | TipRanks / StarMine class product. Public scraping is brittle and likely breaches terms. |

**Consequence:** the only scorecard computable today is a **consensus-level, not analyst-level**
scorecard:

```
For each monthly snapshot and each consensus bucket (STRONG_BUY … STRONG_SELL):
    forward return over h ∈ {1m, 3m, 6m} from Tiingo, net of a stated cost
    → realised return per bucket per horizon
```

That answers *"did following this consensus have paid?"* It cannot answer *"is analyst X good?"*,
and the page must say exactly that. Per-analyst scoring is blocked on a licensed event feed, not on
effort.

---

## 4. The seven biases that must be printed

Use `../DESIGN_ANALYST_SIMULATION.md` §6 verbatim — market beta, analyst survivorship, look-ahead,
clustering, multiple testing, reiteration spam, costs — with one addition specific to a
consensus-level scorecard:

8. **Consensus drift is not an event.** The monthly distribution changing from 60% to 62% buy does
   not mean anybody acted. A consensus-level backtest silently assumes a position was taken at every
   rebalance, which no analyst recommended.

---

## 5. What must never be displayed

- A "P/L%" without horizon, benchmark, cost assumption, and n.
- A hit rate without a confidence interval (`83%` on n=6 is not a hit rate).
- An analyst ranked on fewer than 15 actions — render `INSUFFICIENT_DATA`.
- A beta without its CI, or a correlation without a mechanism.
- A number produced by an estimator that cannot be reproduced from `out/*.json`.
