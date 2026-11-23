# Investment Hub assessment — what is worth translating into audit/audit2/audit3

**Date:** 2026-11-23T03:25Z · **Author:** Kilo · Paper only, zero capital.

## 1. What the "Other Stuff → Investment Hub" menu points at
Real pages live under `findstocks/`, `findmutualfunds/`, `findcryptopairs/`, `findforex2/`,
`investments/`, `live-monitor/`, `STOCKS/`. The most audit-relevant are in **`findcryptopairs/`**:

| Page | What it is | Data it reads |
|---|---|---|
| `audit-trail.html` | per-pick audit trail view | `audit_trail/data/dashboard_payload.json`, Binance ticker, `api/algo_competition.php` |
| `incubator.html` | strategy incubation funnel | `alpha_engine/data/incubator_report.json`, `incubator_paper_ready.json` |
| `pump-watch.html` | **cross-system live picks aggregator** | alpha_engine, mercury2, ml_battleground, KIMI active/closed picks |
| `algo-competition-enhanced.html` | algo competition leaderboard | `api/algo_competition.php` |
| `now.html`, `genome.html` | live / genome views | (thin) |

## 2. The three things worth building on
### (a) `pump-watch.html` → feed audit3 a cross-system view  ✅ HIGH VALUE
It already aggregates active + closed picks from **multiple independent systems** (alpha_engine, mercury2,
ml_battleground, KIMI). audit3 currently ranks **one** ledger. Wiring pump-watch's per-system feeds into an audit3
"cross-system consensus" panel is the cheapest real improvement — it is the same idea as my review-repo aggregator,
already built, just pointed at live systems.

### (b) `incubator.html` → the strategy-generation funnel  ⚠️ USEFUL, NOT ADMISSIBLE AS-IS
`incubator_report.json` summary: **4,987 permutations, 24,935 backtests, 4,649 candidates, 20 "paper-ready"**.
Problems that make its output inadmissible into audit3 today:
- **`best_sharpe: 9248.977`** — a Sharpe of 9,249 is a computation bug (near-zero variance), so the Sharpe column
  cannot be trusted.
- **No `n`** on the 20 paper-ready rows → DSR is undefined (DSR needs a sample size).
- **Duplicate rows** (three identical `cross_sectional_momentum` at sharpe 4.08, PF 2.056) → dedup defect.
- **24,935 backtests** is a trial debt so large that almost nothing can survive deflation at that N.
**Translation:** keep the funnel (it is good strategy generation), but gate its output with a validator that requires
`n`, dedups, and reports DSR at the honest permutation count **before** anything becomes an audit3 pod.

### (c) `alpha_engine/data/closed_picks.json` (2,204 resolved) → immediate, usable  ✅ HIGH VALUE
This is real closed data with `strategy`, `entry_date`, `pnl_pct` across **61 strategies**. I recomputed per-strategy
per-trade Sharpe and the production DSR:

| strategy | n | mean %/trade | Sharpe | DSR@N=61 | DSR@N=4987 |
|---|---:|---:|---:|---:|---:|
| **forex_rsi2_mean_reversion** | 97 | +0.002 | 0.458 | **0.9987 ✅** | 0.8756 ❌ |
| clone_hl_copy_lb_None | 12 | +0.003 | 0.217 | 0.072 | 0.004 |
| prediction_market_consensus | 54 | +0.035 | 0.199 | 0.072 | 0.000 |
| everything else | — | mostly negative | — | <0.10 | 0.000 |

**This is the complete illustration of the whole programme in one row:** `forex_rsi2_mean_reversion` is the *only*
strategy that clears DSR at N=61 — and it dies twice: (i) at the honest programme N=4,987 it drops to 0.876, and
(ii) its +0.2 bp/trade gross is **below the 7.5 bp FOREX round trip**, so it is net-negative before deflation even
matters. Deflation alone is not enough; cost and N both have to be right.

## 3. Recommendation
1. **Translate now (cheap):** pump-watch's multi-system feed → an audit3 "cross-system consensus" panel.
2. **Translate with a gate:** incubator → audit3 pod pipeline, behind a validator requiring `n`, dedup, and
   DSR at the 4,987 permutation count; fix the `best_sharpe 9248` bug before anything reads it.
3. **Do not import:** the 20 "paper-ready" strategies as validated picks — they carry no `n`, duplicate rows, and a
   broken Sharpe column.
4. Keep `alpha_engine/closed_picks.json` as the independent recompute set; it is the cleanest closed-pick corpus in the
   estate and already reproduces the audit3 verdict (with one instructive N-sensitive exception).

*Paper only. Zero capital. Not investment advice.*
