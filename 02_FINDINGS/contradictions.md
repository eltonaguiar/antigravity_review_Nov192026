# Findings — Contradiction register

The repo contains multiple self-assessments that disagree. A reviewer (and any future
automation) must treat these as **not reconciled**, and the strict ledger as the default
source of truth until they are.

| Claim | Where | Date | Versus |
|---|---|---|---|
| "mega_mutation is the only statistically valid, profitable edge" (PF 8.32, WR 84% forward, paired bootstrap pass) | `TRUE_PROFITABILITY_VALIDATED.md` | 2026-11-14 | audit3 ledger (2026-11-19): mega_mutation n=19 → **INSUFFICIENT_N**, observe don't trade |
| CRYPTO PF 9–18 / WR 78–88% | Dashboard banners | ongoing | raw WR 33% after EXPIRED→WON mislabels |
| Kill-switch "WR lift +6.10pp" | `/audit` kill card | ongoing | **PF lift −0.0224** — removing 42 "losers" worsened profit factor; the lift line overclaims |
| Ghost rows 0 / GREEN | `template.html` / `index.html` | 2026-05-31 baseline | live 22,947 |
| Backtest run metadata current | `bt_backtest_runs` | — | frozen since 2026-03-06 |
| "re-run at n≥150 gate (~2026-06-25)" for `crypto_rsi5070_us` | `/audit` | — | it already has n=431; text is stale |
| Multiple "we have edge" reports (quantum_fusion, rare_strategy, etc.) | `reports/`, root `.md` | 2026 | none of these pass the strict tribunal; all have n far below the 100-trade floor |

**Why this matters:** these contradictions are not cosmetic. They mean the project cannot
answer the owner's exact question — *"would we have made a profit with minor adjustments?"*
— because each subsystem counts trials and reports success differently. The fix is to
declare a single system of record and a single forward-observation ledger, then reconcile
every historical claim against it.
