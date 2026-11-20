# Consolidation plan — `/audit`, `/audit2`, `/audit3` → one source

**Agent:** opencode-deepseek-flash (Windows, desktop-081g9oh)
**Seat:** `inbox/desktop-081g9oh/findtorontoevents-ca/opencode-deepseek-flash`
**Date:** 2026-11-20T07:46Z
**Scope:** `eltonaguiar/findtorontoevents_antigravity.ca`, the three audit surfaces, the DB/GHA producers, and a test plan.
**Status:** proposal for review. No source changes in this document.

## 0. Bottom line

- **Nothing is money-ready.** Live `audit3` 07:35:29Z: **0 PROVEN / 0 CANDIDATE / 8 KILL**, 8,795/16,406 scored (53.6%), forward 444, eligible 0.
- Selection alpha is **significantly negative**: **−0.2674%/trade**, 95% CI **[−0.5114, −0.0249]**, n=3,152. The picks underperform holding the same instruments.
- CRYPTO and COMMODITY are class-level KILL. EQUITY is the only positive point estimate (n≈943, +0.16%, CI straddles zero, PF≈1.08, required_n≈9,972) but is WEAK and not significant.
- **B1:** the four pre-registered EQUITY pod strategy names were never emitted. The forward clock cannot start until the pod is amended to real emitters (or those four are implemented).
- The three pages are **three views of overlapping but not identical ledgers**, and they drift. The goal is one canonical ledger and one deploy path, with each page owning a distinct question.

## 1. Current state (verified 2026-11-20T07:35–07:46Z)

| Item | Value |
|---|---|
| `audit3` ledger | generated 07:35:29Z, provenance `9bf6fb7f214c3283` |
| Scored / total | 8,795 / 16,406 (53.6%) |
| Verdicts | 0 PROVEN, 0 CANDIDATE, 59 WEAK, 8 KILL |
| Selection alpha | −0.2674%/trade, CI [−0.5114, −0.0249], n=3,152 |
| Gate | `applied=true`, tested 444, scopes strategy 36 / class_proxy 401 / class 7 |
| Forward | 444 rows; `POD-EQUITY-BREAKOUT` 0; eligible 0 |
| `/audit` money-ready | money=[], watch=[COMMODITY] |
| `/audit2` live pods | 11 (manifest-driven); committed `audit2_pods.json` is stale at 6 |
| DB health | 22,947 ghost rows; 94,606 open vs 21 active; 130/24,158 PnL sign mismatches |
| Recent fixes | #996 gate report, #995 audit2 ledger pin, #998 dashboard YAML restore |
| Open blocker | #965 (stale, 15 conflicts); `hotfix/required-n-power` must be closed, not merged |

## 2. Root causes of the current state

1. **Multiple ledgers / denominators.** `/audit` and `/audit3` can publish at different cadences; `/audit2` historically resolved more than one path. That is a reconciliation bug, not three independent opinions.
2. **Data quality.** 22.9k ghosts, 94k open vs 21 active, stale/contaminated class labels, excluded cohorts, and only ~54% coverage. Verdicts are computed on a moving subset.
3. **Measurement was regressed and is now fixed.** The alpha gate report and `by_strategy` were dropped; #996 restored them and live verification passed. The gate must be published, not just executed.
4. **Forward clock never started for the only pre-registered pod.** B1 is a naming/registration error: the four pod strategies exist only in the backtest namespace, not in `trading_picks` / `at_pick_outcomes` / `at_signal_outcomes`.
5. **Model scope:** nothing has passed the gates because selection alpha is negative and the sample is thin. This is a finding, not a bug to paper over.
6. **Process debt:** stale branches, a credential leak, generated files tracked as source, and CI/deploy cadence races.

## 3. Target architecture — one source, three views

```
DB canonical picks/outcomes
  -> canonical loader (one denominator, class labels, costs)
  -> selection alpha sidecar (by_class / by_slice / by_strategy)
  -> audit3 tribunal (BH, DSR, 2x cost, split-half, concentration, forward)
  -> audit.canonical.v2.json  (single source; provenance id)
       -> /audit3  : verdicts, gates, kill tribunal, forward evidence
       -> /audit2  : candidate pods, forward clock, measures/traps, same ledger
       -> /audit   : live ops, data health, IC, leaderboard, evidence; no duplicate verdicts
  -> forward_observations.jsonl -> forward gate -> tribunal
  -> evidence registry / denylist / backtests -> sidecars, never verdicts
```

**Canonical schema (`audit.canonical.v2`):**
- `provenance`: id, module, git_sha, input_sha256, generated_at, source_generated_at.
- `population`: canonical vs payload_slice; `population_rows`, `population_total`.
- `cost_model`: per-class round-trip bps; `win_definition`.
- `coverage`: scored/total, excluded cohorts, row drops, statement.
- `cells`, `classes`, `symbols`, `families`, `segments`: n, WR/CI, PF, net expectancy/CI/2x, q, DSR, `dsr_n_trials`, verdict, reasons, alpha_gate.
- `selection_alpha`: available, overall, by_class, by_slice, **by_strategy**, bar_coverage, **gate**.
- `forward_gate`: rows, fingerprint, pods, hypotheses, eligible, reasons.
- `hypotheses`, `kill_tribunal`, `db_health`, `doctrine`, `limits`.

**Invariants (fail the build):**
1. One `provenance.id` across all rendered surfaces.
2. `population_rows == coverage.scored_rows`.
3. Every cell with a DSR has `dsr_n_trials`.
4. Every PROVEN/CANDIDATE has a forward-gate block and alpha gate status.
5. `/audit2` and `/audit3` read the same ledger path; `/audit` shows the same provenance.
6. No surface shows a verdict/alpha number without its `provenance_id`.

## 4. What to keep, what to cut

| Source | Keep | Cut |
|---|---|---|
| `/audit3` | Tribunal, gates, selection alpha, forward evidence, kill list, coverage | Duplicated class tables that disagree with `/audit`; stale hardcoded banners |
| `/audit2` | Pre-registered pods, forward clock, measures library, traps, retired-with-reason | Static pod prose that duplicates the manifest; ledger fallbacks after the canonical pin |
| `/audit` | Live ops, active/closed picks, data health, IC, leaderboard, evidence | Hardcoded PASS banners; zero-observation green tiles; legacy verdict panels |
| Everywhere | Provenance, coverage, gate status, 2x-cost, forward | Unbounded grids, 96-config TP/SL, unfalsifiable claims, stale committed generated files |

## 5. Suggested fixes (priority, owner, test)

### P0 — measurement integrity

1. **One canonical ledger + schema + provenance triple** — owner: kilo/data. Files: `alpha_engine/audit3_tribunal.py`, `audit_dashboard/audit2.js`, `audit3.html`, deploy workflow. Test: schema contract + parity CI (same id/population/cost/win across pages).
2. **B1 pod amendment + `emitted` flag** — owner: pod/manifest owner. Amend to real emitters (`donchian_breakout_scalp`, `proven_donchian_adx_trend`, `adx_momentum`) as a dated pre-registration; restart the clock; add `emitted:true/false` from `strategy EXISTS in trading_picks` for every pod cell. Test: dry-run/synthetic row makes `emitted=true`; unknown name fails.
3. **Data quality** — owner: resolver/data. Ghost rows 22,947; open 94,606 vs 21; class-label contamination; coverage <60%. Test: ghosts excluded from every aggregate; FX symbols cannot be CRYPTO; coverage floor gate.
4. **Secrets** — owner: repo owner. The credential source (`dbpasses.txt`) must never be committed; rotate the exposed credential from `feat/audit-review-organization`; add secret scanning. Test: `gitleaks`/history scan clean.
5. **Branch hygiene** — owner: kilo/owners. Close #965 (stale ledger, 15 conflicts); close `hotfix/required-n-power`; keep archive tags; no force `main`. Test: mergeable-clean + focused suite.
6. **audit2 committed drift** — owner: deploy. Either commit generated `audit2_pods.json`/`audit2_forward.json` after deploy or untrack them; never hand-edit. Test: live pods == committed pods.

### P1 — one clock and one cost model

7. **Forward clock strict mode** — per-pod rows after registration, intrabar first-touch, benchmark leg >=90%, PF CI-LB>1, IR>=0.5; watchdog red on 7 days of no accrual.
8. **Canonical cost model** — one per-class all-in cost (fees+spread+funding+borrow; ER+tracking difference+tax for funds/ETFs); 2x stress; publish the model in provenance.
9. **Canonical PBO/DSR** — one CSCV implementation, threshold 0.5; 0.0 must render as “not computed”; DSR `n_trials` >=658 for PROVEN.
10. **TAA/rotation control** — beta-matched same-universe buy-and-hold arm; paper until n>=200 forward; do not call drawdown control alpha.
11. **Asset-class data repairs** — FX price/symbol fix, crypto on-chain/funding, bond/futures proxies, mutual-fund NAV, prediction-market contract payoff, copytrading freshness.

### P2 — research and UI

12. **Point-in-time registry** — delisted-inclusive equities/funds, as-of fundamentals, as-of funding/on-chain; makes every per-class claim survivorship/look-ahead safe.
13. **Value/quality study** — annual rebalance, 3–5y horizon, PIT; not in the trade tribunal.
14. **UI consolidation** — delete hardcoded/stale tiles; every number links to `provenance_id`; one ledger deploy.

## 6. Test plan

### 6.1 Unit / golden
- Schema contract: required keys, types, provenance triple.
- `selection_alpha` includes `by_strategy` and `gate`; gate `applied`, `tested`, `demoted`, `scopes` present.
- Every DSR has `dsr_n_trials`; PROVEN/CANDIDATE has forward + alpha gate.
- Cost model matches per-class config; 2x stress computed.
- Class labels: FX not CRYPTO; EURUSDT not FOREX; BOND not CRYPTO.
- Pod manifest names all exist in `trading_picks` (or `emitted=false`).

### 6.2 Integration
- Rebuild from a committed sample payload → ledger → render all three pages; same `provenance.id` and population.
- Forward ingest: eligible row increments pod; zero admissible fails red; benchmark coverage reported.
- audit2 pods: live count == committed count; forward clock includes per-hypothesis reasons.
- One-ledger deploy: `/audit`, `/audit2`, `/audit3` timestamps within one run.

### 6.3 Data quality
- Ghost/open/PnL/class/coverage checks; `db_health.any_red=false` or documented.
- Excluded cohorts reported; no hidden denominator.
- Stale bar tables fail with a named reason.

### 6.4 Validation (per candidate)
- Walk-forward + purged CV/embargo; IS vs OOS; WF efficiency.
- BH q<=0.10, DSR>=0.95 with true trial count, PBO<0.5.
- Net CI-LB>0 at 2x cost; concentration caps; random-entry **and** beta-matched controls.
- Forward: n>=100 (class floor), intrabar, benchmark leg, persistence 2 runs.

### 6.5 CI
- Ubuntu + Windows: `python -m pytest tests/... -q`; COMS UTF-8 check.
- Secret scan; no hardcoded credentials.
- Golden ledger diff; parity invariant; deploy dry-run.
- Acceptance: no PROVEN without gate; no CANDIDATE without forward; no surface disagreement; no secret.

## 7. Asset-class plan (current stance)

| Class | Current | Next test | Money stance |
|---|---|---|---|
| EQUITY | Only positive point estimate; WEAK; B1 names not emitted | Real emitter + forward clock; breakout/PEAD + RVOL; beta-matched control | Paper only; no real money until forward gate |
| ETF | Flat (PF≈1.005); TAA drawdown control | Core VOO/VTI; TAA/rotation paper; all-in cost | Cheap beta; rotation paper |
| CRYPTO | KILL (n≈6.7k; policy-clean PF≈0.23) | Event study ATH/skyrocket; on-chain/funding; paper | No real money; class KILL |
| FOREX | WEAK; FX data gap | Backfill/symbol fix; AUDJPY paper | No real money |
| COMMODITY | KILL; COT falsified | Dedup/lag COT; carry/seasonality | No real money |
| BOND | Thin; low return | Duration/credit study; ballast only | Ballast, not return |
| FUTURES | Thin; DBMF/KMLM proxies | TSMOM/CTA with roll costs | Paper/diversifier |
| MUTUAL FUNDS | No pick emitter | Fee/PIT NAV screen; index only | Low-cost index beta |
| PREDICTION / COPY | Shadow | Contract payoff; feed freshness | Shadow only |

## 8. Permutations (pre-registered, not 96-grid)

- TP/SL: 5 configs max (ATR stop, RR, time stop), intrabar stop-first.
- Volume: prior-bar RVOL 1.0/1.5/2.0; volume z-score; dollar-volume floor.
- Entry lag: 0/1/2 bars; next-open vs next-close.
- Vol targeting: 10/15/20%; inverse-vol weights.
- Cost: 1x/2x/3x/5x; report break-even bps.
- Controls: random-entry and beta-matched same-universe buy-and-hold.
- Acceptance: OOS net CI-LB>0 at 2x cost, PBO<0.5, DSR with true trials, n floors, forward persistence.

## 9. Rollout

- **Phase 0 (now):** P0-1/2/3/4/5/6; no new strategy work; verify gate live; close stale branches.
- **Phase 1 (next):** one forward clock, canonical costs/PBO/DSR, asset-class data repairs; paper sleeves.
- **Phase 2:** PIT registry, value/quality, PM payoff, UI cleanup.
- **Exit criteria:** one ledger, parity green, forward clock accruing, no secrets, no surface disagreement.

## 10. Decisions needed

1. B1: A (dated amendment to real emitters) or B (implement the four) — recommend A.
2. One denominator: canonical full book (recommended) vs payload slice; publish the triple.
3. Cost model: per-class all-in; one source.
4. TAA: suitability sleeve, not alpha; 90/0/10 or 100% core until forward n>=200.
5. Real money: zero until a pod passes the forward gate on 2 consecutive runs.

*Review/engineering plan, not investment advice.*
