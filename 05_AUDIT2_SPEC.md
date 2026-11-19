# audit2 — content spec (curated from the MD corpus)

`/audit2` is currently a **404**; the "second audit" never shipped and was superseded by
audit3. This is a recommendation for what audit2 *should* be, so it adds value instead of
duplicating audit3. The division of labour:

| Surface | Role |
|---|---|
| `/audit3` | the **KILL tribunal** — strict denial, 0 PROVEN / 1 CANDIDATE, statistical falsification |
| `/audit` | the **wide dashboard** — many tiles, contradictory, not decision-safe |
| **`/audit2` (new)** | the **CANDIDATE / METHODOLOGY library** — what is worth forward-testing, the statistical measures the project already built, and the benchmark gates. Everything audit3 *can't* show because it only denies. |

audit2's one job: **"here is the short list worth risking paper on, and here is the
measurement kit to judge it."** It is the honest place for a *positive* number.

---

## Section A — Forward candidate pods (the only strategies worth a forward test)

These are drawn from the corpus where *evidence* (not ambition) exists. All are
pre-registered hypotheses; none is claimed to be money-ready.

| # | Candidate | Evidence in corpus | Gate before promotion |
|---|---|---|---|
| P1 | **Managed-futures / TSMOM trend** (ETF proxy: vol-scaled trend across equity idx/bonds/FX/commodities; 3–12m lookback ensemble; symmetric time/vol exit; **no TP/SL**) | `EDGE_REVIEW_2026-11-19.md` P1; Moskowitz–Ooi–Pedersen 2012 + Hurst 100y evidence; crisis alpha. You already have `verified_strategies/commodity_tsmom_backtest.py`, `etf_managed_futures_proxy_*` | ≥100 resolved trades, intrabar-true, costs ×2, IR ≥0.5, α t>2 (Bonferroni at true N), ≥90d paper |
| P2 | **FX G10 carry + trend filter** (rank by forward discount, long top-3/short bottom-3, vol-targeted, 200d trend overlay) | `EDGE_REVIEW` P2; your funding-carry work (H21–23) shows the pattern is small but real; needs portfolio framing. Corpus: `Max Carry Dynamic Hedging` +100–180bps vs static, Sharpe 0.9–1.1 (`STRATEGY_DISCOVERY_REPORT_V3`) | same gate; FX needs date/timezone backfill + 3+ folds first |
| P3 | **PEAD drift, liquid large-caps** (SUE-ranked earnings surprise; long +1σ decile, 60d hold) | `EDGE_REVIEW` P3; Bernard–Thomas 1989 (one of the most replicated anomalies); fix the existing 60/60 PEAD pipeline first | screen 500+ names; low turnover; n≥100 |
| P4 | **EQUITY/ETF breakout family** — `donchian-stock-breakout`, `rs-breakout-scout`, `vol-contraction-scout`, `adx-trend-scout` | **Already pre-registered** as `POD-EQUITY-BREAKOUT` in `reports/audit3_confirmatory.json` (2026-11-19). EQUITY OOS Sharpe +0.61 (33 folds), ETF +0.21 (53 folds); pooled ~364 trades net +0.46% | forward CI-LB >0 at day 90; benchmark vs SPY |
| P5 | **CRYPTO POSITION-horizon picks** | `PER_CLASS_PATHS_TO_PROFIT.md`: n=33, WR 69.7%, PF 3.18, +74.4pp — the only * crypto bucket; emit POSITION rules only, kill SWING (n=243, PF 0.457, −328.6pp) | after stop-fill fix; n≥100 forward |
| P6 | **`luxalgo_confluence` SHORT** (crypto) | audit3 CANDIDATE: n=476, net CI>0, DSR 0.99 — but single-source 98%, discovery namespace | require a second independent source; BTC-regression + funding covariates; kill if forward CI-LB ≤0 at day 60 |
| P7 | **EQUITY time-exit bucket** | `PER_CLASS_PATHS_TO_PROFIT.md`: n=220, WR 61.4%, PF 1.988 — the one exit geometry that works | same as P4 (it is a subclass of the breakout family) |
| P8 | **`mega_mutation_macd_rsi` / `ema_momentum`** (CRYPTO) | `TRUE_PROFITABILITY_VALIDATED.md` PF 8.32/84% WR forward but n small; audit3 says INSUFFICIENT_N (n=19) | register as hypothesis, **observe, don't trade**, until n≥100 forward |

**Explicitly do NOT put in audit2 as candidates** (they are falsified or structurally
unfixable): daily crypto single-name RSI2, TP/SL score bands, 50¢ Polymarket taker
forecasting, meme/gainer ML, copy-trading wallets, COT positional shorts, fixed-TP
"milestones"/spike reverse-engineering, and CRYPTO SWING.

---

## Section B — Statistical measures the project already built (keep & display here)

audit2 should be the home for the measurement kit. These are the terms the MD corpus uses
with real substance behind them — display them as the "how we judge" panel:

| Measure | What it is | Where it's used in the repo |
|---|---|---|
| **DSR** (Deflated Sharpe Ratio) | Sharpe deflated by trial count / effective N; the honest "did we overfit" score | 820+ DSR references; `audit3_ledger.json.dsr_threshold=0.95`; H10 downgrade "effective N≈38" |
| **PBO** (Probability of Backtest Overfitting) | probability the "best" backtest is a fluke | 1,893 references; edge-search v1–v4 |
| **SPA** (Superior Predictive Ability) | multiple-testing-corrected out-of-sample comparison | 3,606 references |
| **FDR / BH** | Benjamini–Hochberg false-discovery control across tested cells | audit3 multiplicity (q≤0.10) |
| **Wilson CI** | binomial confidence interval for win rate | audit3 wr_ci |
| **Bootstrap net-expectancy CI** | 2,000 seeded resamples; the primary edge test (G2) | audit3 edge_test |
| **Selection-adjusted CI / Bonferroni** | correct for 65-segment screen | audit3 selection_alpha discussion |
| **Walk-forward + purged group K-fold + embargo** | time-series CV with purge/embargo (López de Prado) | `EDGE_REVIEW` §3 Phase 3; walkforward reports |
| **Intrabar-true resolution** | SL-wins-ties first-touch; fixes EXPIRED→WON artifacts | `money_ready_verdict.json`; INCIDENT #18 |
| **Effective-N accounting** | correlated candidates count >1 trial | H10 case |
| **Cost ×2 stress + per-class measured slippage** | 2×-slippage column; per-strategy measured cost | `audit3_ledger.json.cost_basis`; `slippage_validation` |
| **Benchmark-relative gates** | excess vs SPY/BTC/T-bills/AGG/GSG; IR; down-capture | `BENCHMARK_GATES.md` spec; `benchmark_closed_ledger.py` |
| **Brier score / calibration** | probability calibration for ML meta-labeling & prediction markets | `EDGE_REVIEW` §3; brier refs |
| **Meta-labeling** | ML predicts "will this signal work", not price | `EDGE_REVIEW` §3 Phase 3 |

---

## Section C — Methodology quotes worth preserving (the "how big firms do it" library)

> "You are running a multiple-testing engine… the binding constraint is hypothesis quality
> and trial budget, not techniques." — `EDGE_REVIEW_2026-11-19.md`

> "Real edge ≠ better forecasting. It = risk-premia harvesting + cost elimination + honest
> sizing, in a boring portfolio." — `EDGE_REVIEW_2026-11-19.md`

> "Edge, if any exists, should be expressed with symmetric, vol-scaled, time-based exits
> and sized by vol targeting — the expression of every trade changes the statistics more
> than the signal does." — `EDGE_REVIEW_2026-11-19.md`

> "The gap is between research and production: profitable approaches exist but are not
> deployed in the live ledger." — `quant-audit` VERDICT.md

> "A zero-PnL expiry is not a neutral observation." — `AUDIT_SURFACE_REVIEW_2026-11-19.md`

> "One great signal is worth less than five decent independent ones (10 streams @ Sharpe
> 0.5, ρ≈0.1 → stack Sharpe ≈1.5)." — `EDGE_REVIEW_2026-11-19.md`

> "The single-source gate alone eliminates all 166 cells." — `quant-audit` VERDICT.md

> "Institutions don't forecast better; they (1) pick battles with a structural reason to
> exist, (2) act cost-obsessively, (3) diversify many small streams, (4) survive." —
> `EDGE_REVIEW_2026-11-19.md`

---

## Section D — The "boring portfolio" (what the corpus says the money actually lives in)

- **Core 70–85%:** low-cost index beta (XEQT/VEQT + global bond ETF, ER ≤0.20%). The
  corpus's own `MF_CAN_WIN.md` and SPIVA stats: ~93% of large-cap active trails over 20y.
- **Satellite 10–25%:** premia sleeves P1/P2 (or managed-futures ETFs).
- **Speculative ≤5%:** forward-paper pods above, only after gates pass.
- Vol-target satellites; fixed drawdown circuit-breakers (−15% halves, −25% pauses).

---

## Section E — Audit2 page requirements (so it stays honest)

1. Every candidate card shows: pre-registration date, hypothesis ID, the gate, and a
   **benchmark leg** (excess vs matched exposure, IR, down-capture). Hide raw PF.
2. Display the **global trial counter** and the cumulative-N DSR so "how many rolls have we
   had" is visible — this is the anti-p-hacking guarantee.
3. No "PROVEN" / "T1" / "Renaissance" tier labels. Replace with a single axis: forward-clock
   evidence (days, CIs).
4. Keep a **retired-with-reason** table (like copilot's H-143 elimination record) so
   nothing is silently deleted and nothing is re-proposed blind.
5. Wire it to `reports/audit3_confirmatory.json` as the single source of registered pods.

---

*Not personalized investment advice.*
