# Round 29 — Ledger mine + four new hypothesis tests (2026-11-22)

Author: `copilot-cli-deepseek-flash` (VS Code / DeepSeek V4.1 Flash).
Source repo: `eltonaguiar/findtorontoevents_antigravity.ca`, branch
`push/phase2-round-2026-11-22`. All work is **unpushed to the source repo** — that
branch carries other agents' commits.

Zero capital deployed. Not investment advice. `UNMEASURED` means unmeasured, not
zero.

---

## The one-paragraph version

The live ledger **loses 15.24 bp per resolved pick at t = −3.91** across 10,968
picks in 7 asset classes, and 0 of 7 clear a cluster-robust profit factor of 1.0.
The strongest statistical fact the programme has produced — the volatility risk
premium at **t = +46.50** — is the **worst trade in the set** once implemented
(equity goes to zero in March 2020). H-119's "forward" ledger is **100% backfilled**
(430/430 rows written after the outcome). Crypto funding carry means **+3.555%/yr**
against a 3.50% T-bill but decays **+5.96% → +1.24%** across the sample. And
Polymarket prices beat a base-rate forecast by **50% Brier skill** — the market,
again, is right.

---

## Documents in this folder

| file | what it establishes |
|---|---|
| `2026-11-22-ledger-mine-leakage-robustness-attribution.md` | Leakage audit (35.7% of the ledger is redundant re-emissions), per-class cluster-robust PF, source attribution with BH correction, and the 78.9% CRYPTO claim **not reproduced** |
| `2026-11-22-pick-survival-regime-conditioning.md` | Duration distribution; **430/430 H-119 rows backfilled**; two self-caught look-ahead defects in my own regime analysis |
| `2026-11-22-funding-venue-dispersion-fee-tiers.md` | 5-venue synchronised funding; carry stability; **fee tier is not the binding constraint** (worth ~7 bp/yr vs ~470 bp of time-variation) |
| `2026-11-22-vol-premium-pairs.md` | VRP t=+46.50 and **RUINED** when harvested; GDX/SLV fails cointegration OOS (ADF +0.15) |
| `2026-11-22-prediction-market-calibration.md` | Brier skill +0.4956 on 362 resolved markets; mid-range deviation flagged but **not called an edge** (binomial p≈0.086) |
| `2026-11-22-weekly-scorecard.md` | The one-page weekly gate and its CI wiring |
| `2026-11-22-carry-snapshot-series-status.md` | 2 of 20 carry snapshots; explicitly **not** inflated to close the todo |
| `2026-11-22-consult-multi-presets-refresh-and-sports-clv-blocked.md` | All 3 fan-out presets were dead; `--probe` added. Sports CLV recorded **BLOCKED** on a credential |

## Machine-readable artifacts

`ledger_mine.json`, `survival_regime.json`, `funding_venues.json`,
`vol_premium_pairs.json`, `calibration.json`, `scorecard.json`.

## Reproducers (in the source repo)

```
python3 tools/ledger_mine.py --boot 2000
python3 tools/pick_survival_regime.py --boot 1500
python3 tools/funding_venue_dispersion.py --days 120
python3 tools/vol_premium_pairs.py
python3 tools/prediction_market_calibration.py --max 400 --lead-days 7
python3 tools/weekly_scorecard.py --strict
python3 tools/consult_multi.py --probe
```

---

## Verdict table

| item | label | basis |
|---|---|---|
| Live ledger, all classes | **REFUTED** | −15.24 bp, PF 0.90, CI-LB 0.85, t=−3.91, n=10,968 |
| CRYPTO | **REFUTED** | −18.17 bp, PF 0.885, n=9,099 |
| EQUITY | **NOT ESTABLISHED** | +18.60 bp but PF CI-LB 0.885 |
| ETF / FOREX / BOND | **REFUTED** | −0.32 / −15.13 / −18.22 bp |
| COMMODITY | **REFUTED** | −346.51 bp, PF 0.120, n=44 |
| FUTURES | **UNMEASURED** | n=12 |
| H-119 (directional) | **REFUTED** | net −2.52 bp/trade; 430/430 backfilled |
| Funding carry | **REFUTED** as a stable cash-beater | +3.555% mean, halves 5.96 → 1.24%/yr |
| Cross-venue funding arb | **REFUTED** | best harvest +1.56%/yr, below cash |
| Vol risk premium (existence) | **ESTABLISHED** | +357.9 bp, t=+46.50, n=5,192 |
| Short-vol harvest | **RUINED** | equity ≤ 0 at 2020-03 |
| GDX/SLV pairs | **REFUTED** | ADF OOS +0.15 |
| Polymarket calibration | **ESTABLISHED** | Brier skill +0.4956, n=362 |
| `mega_mutation` source | **CANDIDATE** | +135 bp, n=105, 67 days, survives falsification |
| Sports CLV | **UNMEASURED (blocked)** | no reachable `ejaguiar1_sportsbet` credential |

## Eight defects I found in my own work this round

Listed because the pattern matters: nearly all of them **over-stated** evidence.

1. Timestamp parser silently dropped **67%** of the ledger (6,513 rows).
2. Benjamini-Hochberg q-values attached to the **wrong sources** — printed a
   p=0.29 source as significant at q=0.004.
3. Regime conditioned on the **close** date — look-ahead. Produced the round's
   best-looking number, and it was an artefact.
4. `+395 bp/trade "beats BTC" t=9.33` — compared a market-neutral book to a
   long-only index in a −20% market.
5. Funding venue comparison across **non-overlapping** windows.
6. Two sections of **one tool** running on two different samples.
7. A **ruined** equity curve (`nan` CAGR) still labelled **CANDIDATE**.
8. `verify`/scorecard code reading **guessed** field names and reporting `n/a` as
   if it were a result.

## Ask for reviewers

The claim I most want falsified: **`mega_mutation` is the only surviving source**
(+135 bp, n=105, 67 days, 55L/50S, split-half +83.6 → +196.0 bp, best-day removal
costs 8%). If that does not replicate on your data, the programme currently has
**no** positive-expectancy emitter at all, and the honest recommendation is
T-bills.
