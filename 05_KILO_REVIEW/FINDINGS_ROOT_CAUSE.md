# Antigravity Financial-Prediction Review — Root Cause Findings

**Date:** 2026-11-19
**Reviewer:** Kilo (worktree `lapis-chronometer`)
**Source repo:** `eltonaguiar/findtorontoevents_antigravity.ca` @ `1cd4f6527ee` (main tip)
**Scope:** stocks/crypto/forex/bonds/ETFs/commodities/futures/mutual-funds prediction
systems, `/audit`, `/audit2`, `/audit3`, `/audit/hyrotrader`, Polymarket/Kalshi,
reverse-engineered gainer strategies, hypothesis/idea trackers.

---

## TL;DR

The programme is not failing because of a missing strategy. It is failing for
four **provable** reasons, and the repo's own November 2026 work already
documents three of them:

1. **There is no positive selection alpha.** Proven with confidence intervals,
   not suspected. (commit `a191e67e484`)
2. **The value destroyed is exit-geometry + costs, not signal.** TP/SL cuts
   winners short; ETF slippage eats 234% of per-trade PnL.
3. **The walk-forward "quality gate" is a rear-view mirror** — it peeks at the
   future and collapses under point-in-time replay.
4. **Tracking is fragmented** — 409 tables, 5+ competing pick ledgers, a stale
   portfolio-snapshot table, and two audit surfaces that disagree about the same
   asset classes.

The user's three complaints map one-to-one:

| Complaint | Finding | Status |
|---|---|---|
| "failed to find reliable picks" | No positive selection alpha in any slice | **Proven** (F1) |
| "no proper tracking of current strategies" | Fragmented ledgers + contradictory surfaces + leaky gate | **Proven** (F4, F3) |
| "no way to switch variables and see if profit" | A/B infrastructure exists but orphaned; E14 still a backlog idea | **Proven** (F5) |

---

## F1. No positive selection alpha — the ledger is net-negative

**Evidence:** `alpha_engine/audit3_edge_hunt.py`, `alpha_engine/audit3_selection_alpha.py`
(commit `a191e67e484`, "feat(audit3): prove the ledger has no positive selection alpha"),
`updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md`.

Measured against **3,500 closed picks**, 2026-02-21 → 2026-11-19 (246 days), net of
per-class slippage:

| Slice | n | net/trade |
|---|---|---|
| Whole book | 3,500 | **−0.188%** |
| CRYPTO LONG | 1,281 | **−1.136%** |
| CRYPTO SHORT | 570 | +0.886% |

The "crypto shorts win, longs lose" headline is **market beta counted once**, not
skill: `mean(long) + mean(short) ≈ −2 × cost` (observed −0.250% vs −0.300%
predicted). Crypto drifted ~−1% per holding window; the long/short split is one
fact about the market, not two facts about skill.

The actual skill test — **selection alpha vs direction-adjusted buy-and-hold**
over the same entry→exit window — is negative or null everywhere:

| Slice | alpha | 95% CI |
|---|---|---|
| Whole book | −0.296% | [−0.621, +0.053] |
| **CRYPTO LONG** | **−0.442%** | **[−0.892, −0.085]** |
| **ETF LONG** | **−0.272%** | **[−0.504, −0.037]** |
| EQUITY LONG | +0.115% | [−0.379, +0.589] |

Two intervals exclude zero and **both are negative**. The quote from the source:
> "No slice anywhere produces a positive alpha interval. That is the answer to the question."

## F2. The loss is exit-geometry + cost, not signal

- Median crypto TP/SL is **+2.50% / −1.50%**: the exit machinery takes profit and
  stops out *before* the move that holding would have captured.
- Measured slippage as % of per-trade PnL (`docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` §3.1):
  | Class | slippage % of PnL | flag |
  |---|---|---|
  | ETF | **234%** | CRITICAL |
  | CRYPTO | 37% | CRITICAL |
  | FUTURES | 75% | CRITICAL |
  | COMMODITY | 13% | WARNING |
  | EQUITY | 13% | WARNING |
- One-sentence diagnosis from `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md`:
  > "we do not have a prediction edge, we have a cost and exit-design problem."

## F3. The walk-forward gate is a rear-view mirror (leakage)

**Evidence:** `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` §2.

- `wf_verdict ∈ {VIABLE, STRONG}` looks superb: n=480, **+0.964%/trade**, positive
  in 10/10 months.
- Point-in-time (leakage-free) replay — letting a strategy vote only with its
  **already-closed** picks — collapses the edge:
  - `prior WR ≥ 65%` → **−0.187%/trade** (n=129)
  - hi-vs-lo difference +0.167%, CI [−0.686, +1.036] → **not proven**.
- Root cause: `at_issue_strat_fwd_wr` is stamped on only **215 / 3,500** rows
  (6%); `strat_fwd_wr` fills in *later*, so the gate's input partly knows the answer.

## F4. Tracking is fragmented — no single source of truth

**Evidence:** `docs/FINANCE_DB_SCHEMA_SPEC.md`, `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md`,
`docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md`.

**Database sprawl:** 10 MySQL databases; `ejaguiar1_stocks` alone has **409 tables**.
There are at least **five** pick ledgers in the primary DB:

| Table | ~Rows | Role |
|---|---|---|
| `trading_picks` | 147k | canonical pick ledger |
| `at_raw_picks` | 113k | pre-aggregation raw |
| `at_pick_outcomes` | 63k | resolved outcomes |
| `at_signal_outcomes` | 51k | "honest lane" intrabar outcomes |
| `now_history` | 86k | "now" scan history |
| `at_local_picks` | **76M** | archived local dumps (through 2026-03) |

`portfolio_snapshots` last snapshot **2026-03-10** (8 months stale) — portfolio
Sharpe claims are therefore suspect.

**Contradictory surfaces** (`docs/AUDIT_SURFACE_REVIEW_2026-11-19.md`):
- `/audit` vs `/audit3` disagree on the same classes. ETF is the tell: **1.9% WR /
  PF 0.02** (n=52) on `/audit` vs **43.1% WR / PF 0.98** (n=584) on audit3 — both
  cannot be right.
- audit3 scores **3,500 of 16,330** closed picks (**21.4%**); 7,502 excluded for
  integrity (46%), 9,100 auto-expired. The page did not state this until a recent fix.
- **Two kill lists that do not reconcile**: kill_switch reports 42 kills of 56;
  audit3 reports 11. They share **1** strategy name.
- Smart picks show two realities on one page: `total_scored = 0` vs
  `95 picks, 68.4% WR`.
- `tier2_proven_strategies` contains no proven strategy — cards are `dead` /
  `monitoring` / `empty`.

## F5. The "switch variables and see" gap — A/B infra exists but is orphaned

The user asked for "variables we could switch and see if we'd have made a profit
with minor adjustments." That capability is **half-built and disconnected**:

**What exists (schema `schema-baseline.sql`, 322 tables):**
- `whatif_scenarios`, `strategy_whatif_results`, `simulation_grid`, `simulation_meta`,
  `ml_ab_tests`, plus per-domain variants `cr_/fx_/fxp_/mf2_/mf_whatif_scenarios`.
- `strategy_variation_generator.py` — a genetic-algorithm that recombines
  "winning DNA" (strategy type, indicators, parameters).

**What is missing:**
- No **forward, point-in-time** A/B harness that emits the *same* signal under two
  exit geometries side-by-side and scores selection alpha on realized rows.
- The one concrete A/B test the reviewers agreed on — **E14: current TP/SL vs
  symmetric vol-scaled time exit on the same signals** — is still a backlog entry,
  not code (`docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §4).
- Branch `add-strategy-variable-tracking` exists in the source repo but its diff
  is data churn + audit3 work; it contains **no variable-tracking implementation**.

## F6. Backtest-n vs realized-n is the most expensive confusion in the repo

`docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §14:
> "EAGLE Grok-4.3's Tier-1 picks were backtest-size, not realized.
> `stocks_rsi2` PF 4.76 and `crypto_liquidity_wick_reversal_v1` n=4,904 are
> backtest rows; the realized cohort is n=43 at +0.15%/trade, which is below
> round-trip cost."

This is why "so many strategies" feel like wins but nothing survives: the headline
counts were backtest rows, not realized trades. The audit3 coverage panel now
states the denominator on every render to counter this.

## F7. Contradictory audit conclusions *within the repo*

Two fresh audits disagree on whether an edge exists:

- `docs/ML_SYSTEMS_HEALTH_AUDIT_2026-11-19.md` — **optimistic**: "the ML layer is
  not broken — it is under-deployed"; gatekeeper 12-fold walk-forward lift 10.44%
  (p=0.008), holdout PF 2.826; consensus WR 50.6% vs 41.9%.
- `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` — **rigorous**: no
  positive selection alpha anywhere.

These do not actually contradict: the ML audit's "lift" is **walk-forward backtest
lift**, not **beta-separated, realized, 2×-cost selection alpha**. It is the same
trap F3/F6 describe — a gate that looks good until you remove the peeking and count
only realized trades. The ML-health audit's own ground-truth query agrees: 32,352
resolved picks, WR 41.7%, avg PnL **+0.085%** (break-even, edge concentrated).

---

## What a winning path looks like (from the repo's own data)

- **EQUITY is the only class with positive out-of-sample Sharpe**: +0.61 across 33
  walk-forward folds. CRYPTO (60% of volume) is **−2.08** across 32 folds.
- **CRYPTO directional picks are the problem, not the product.**
- **ETF intraday is a cost artefact** (234% slippage); only monthly rotation survives.
- **FOREX cannot be judged**: `fx_prices` ends 2026-02-09 (3,855 rows, 15 pairs),
  symbol mapping broken (`AUDJPY=X` never matches `AUDJPY`), so 211 forex picks
  have **zero computable alpha**. EURUSDT is even mis-filed as FOREX.
- **Risk premia > prediction.** Trend/carry/value/PEAD are the only edges with
  century-scale public evidence; directional prediction on public daily bars is the
  low-probability path.
- **The barbell**: low-cost beta core + small premia sleeve in the one positive-OOS
  class (EQUITY) + no speculative sleeve until selection alpha is positive in two regimes.

## Bottom line

Nothing on `/audit` or `/audit3` is worth sizing today — and that is a **measured,
citable** result, not a hunch. The path to a real edge is not another strategy; it
is: stop the two value-destroying expressions, fix the leaky gate, agree one
denominator, and run the hold-benchmark A/B pilot. The repo already has the plan
(`docs/EDGE_IDEAS_BACKLOG_2026-11-19.md`); it needs a forward A/B harness to
execute the "switch variables and see" test the user describes.
