# audit2 — consolidated spec (merge of `05` peer spec + `09` Kilo recommendation + this wave)

**Status:** reconciliation of the two competing audit2 specs. Not a third
independent spec — the single authoritative version to build from.

**Sources merged:**
- `05_AUDIT2_SPEC.md` (peer) — division-of-labour, pods P1–P8, measures library,
  quotes, boring portfolio, requirements E1–E5.
- `09_AUDIT2_CONTENT_RECOMMENDATION.md` (Kilo) — 3-tier strategy shortlist, trap
  panel, conflation-bug list, 7-panel architecture, file:line evidence.
- `10_PEER_REVIEW_NEXT_WAVE.md` (this reviewer) — stop-fill overshoot (mean+median),
  effective-N/power rule, single-denominator rule, retire v2 action.

---

## 1. Role

| Surface | Role |
|---|---|
| `/audit3` | KILL tribunal — strict denial, 0 PROVEN / 1 CANDIDATE |
| `/audit` | wide dashboard (still has contradictions) |
| **`/audit2`** | CANDIDATE + METHODOLOGY library — the positive side: what is worth forward-testing and the measurement kit to judge it |

**First action:** retire/re-point the orphaned `audit_dashboard/v2/index.html`
(301 → `/audit3/`) — it is frozen 2026-05-16 and contradicts audit3 on the sign of
CRYPTO/COMMODITY/ETF (`PAGES_AUDIT2_AUDIT3.md`).

## 2. Candidate pods (forward-testing shortlist)

Tier A — **already pass in-repo walk-forward / live-realized:**

| Pod | Class | Evidence | Source |
|---|---|---|---|
| VWAP mean-reversion (4h) | CRYPTO | OOS 516/953, Sharpe 3.10, DSR 21.4, PBO 0.18 | `HEDGE_FUND_EDGE_REPORT.md:29,40,46` |
| Bollinger mean-reversion | CRYPTO | OOS 38, Sharpe 1.38 | `…:30,42,82` |
| Equity Breakout Momentum | EQUITY | LIVE n=37, cum +37.6 | `per_asset_class…2026-04-21.md:95` |
| Faber 200d TAA | EQUITY/ETF | Sharpe 1.74, PF 5.69 | `HEDGE_FUND_EDGE_REPORT.md:19,160` |
| Equity momentum 12-1 | EQUITY | Sharpe 1.63, PF 7.88 | `…:22` |
| FX momentum USDJPY | FOREX | Sharpe 2.02 | `…:17` |
| forex_rsi2_mean_reversion | FOREX | LIVE n=523, cum +34.6 | `per_asset_class…:124` |
| futures_momentum | COMMODITY | LIVE n=443, PF ~1.1 | `per_asset_class…:157` |

Tier B — academically strong / candidate (pre-register, wait for forward n):

- TSMOM, funding-rate arb, EG-cointegration pairs, Asness value+momentum, ORB
  (verify in-repo), commodity roll-yield, equity overnight/intraday decomposition.
- From peer `05`: P1 (TSMOM), P2 (FX carry+trend), P3 (PEAD), P4 (EQUITY/ETF
  breakout — **already pre-registered `POD-EQUITY-BREAKOUT`, make it the default
  first pod**), P6 (`luxalgo_confluence SHORT`, require 2nd source), P7 (EQUITY
  time-exit).

Tier C — **traps, do NOT surface as candidates:** daily crypto RSI2, SMC order
blocks alone, meme/gainer ML, copy-trading wallets, COT shorts, fixed-TP labels,
CRYPTO SWING, KSS cointegration.

**Effective-N rule (new):** any pod with n < 100 forward sits in an **observe**
tier (not candidate) and must show `required_n` from a power calculation
(`audit3_edge_hunt.py:161`). This moves peer P5 (n=33) and P8 (n=19) to observe.

## 3. Measures panel (the "how we judge" kit)

DSR, PBO, SPA, FDR/BH, Wilson CI, bootstrap net-expectancy CI, selection/alpha-
vs-hold, Bonferroni, walk-forward + purged K-fold + embargo, intrabar-true
resolution, effective-N, 2×-cost stress + measured slippage, benchmark-relative
gates (IR, down-capture), Brier/calibration, meta-labeling. Include the
**stop-fill overshoot** as a tracked measurement (mean 1.071pp; median +41.9% —
report both, sourced from `quant-audit` `console_r_multiples.txt`).

## 4. Conflation bugs to forbid on audit2

From `QUANT_DEBUG_PICKS.md` / `QUANT_DEP_DEBUG.md` / `risk_adjusted_analysis.py`:
zero-Sharpe/high-Sortino inconsistency; stress-multiplier-as-result; 100× PnL
unit bug; 24h-resolution WR bias; score-inversion; gross-vs-net; backtest-n vs
realized-n.

## 5. Page requirements (final)

1. Every candidate card: pre-registration date, hypothesis ID, gate, benchmark leg,
   `required_n`, forward-clock evidence. Hide raw PF as a headline.
2. Global trial counter + cumulative-N DSR (anti-p-hacking display).
3. No PROVEN/T1/Renaissance labels — single axis: forward-clock evidence.
4. Retired-with-reason table (like H-143).
5. **Single denominator:** all numbers come from the audit3 ledger or the canonical
   `resolved_closed_picks_net` view — no per-pod slices.
6. Wire to `reports/audit3_confirmatory.json` as the single source of registered pods.

## 6. Relationship to next-gen audit3

audit2 is the **forward side** of audit3's denial side: its pods feed
`forward_observations`, and audit3's gates consume those resolutions. Build the
forward clock first (audit3 E4) so audit2's pods have a place to accrue.

*Not investment advice.*
