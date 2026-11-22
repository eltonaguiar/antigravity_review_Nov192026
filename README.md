# antigravity_review_Nov192026

Independent review of the financial-prediction system on
[`findtorontoevents_antigravity.ca`](https://github.com/eltonaguiar/findtorontoevents_antigravity.ca)
— covering `/audit`, `/audit2`, `/audit3`, the database schemas, and the strategy /
hypothesis / idea tracking apparatus.

**Date:** 2026-11-19 · **Method:** measured, not recalled — the numbers below came from
live page probes, the `audit3_ledger.json` / `audit3_evidence.json` payloads, the
hypothesis registry, and the schema spec, not from memory.

---

## TL;DR

The project has abundant *machinery* (a strict pre-registered kill tribunal, 99 tracked
hypotheses, 47+ strategy scripts, per-class ledgers) but **no promotion path and no
forward-observation table**, so as of today the strict ledger measures:

| Metric | Value |
|---|---|
| Cells tested | 45 / 171 |
| **PROVEN** | **0** |
| CANDIDATE | 1 (`luxalgo_confluence SHORT` — single-source 98%, in `discovery` → cannot promote) |
| KILL | 10 (11 kill symbols, 2 kill classes) |
| WEAK | 34 |
| INSUFFICIENT_N | 126 |
| Picks scored | 3,500 of 16,330 closed (21.4%) |

**Why there are no solid wins** — five root causes, in rough order of leverage:

1. **The audit is a one-way ratchet to zero.** Every gate is tuned to *deny*, there is
   no promotion/certification path, and the tribunal is **not wired to block emission**
   (its output is a web page, not a denylist the scanner reads). Statistically safe and
   strategically sterile — so it "proves" nothing is good and also prevents anything from
   being proven.
2. **The edge test is mis-specified for the strategies that actually work.** `WR > 50%`
   (G1) is only a break-even test for symmetric payoffs. Your best evidence class
   (premia/trend) has `WR ~35%, RR ~2.5` and can *never* pass G1 even with enormous
   expectancy. A genuine trend cell is structurally unprovable under the current gate.
3. **Fixed TP/SL expression destroys edge.** The "high WR but PF < 1" pathology
   (EQUITY class: WR 59–60%, PF 0.94) is the signature of TP-first labeling. The resolver
   mislabels `EXPIRED → WON`, inflating the surfacing numbers (raw WR 33% vs. the 78–88%
   shown on banner surfaces). Expectancy, not win rate, is the only honest definition of
   edge.
4. **Data & infra debt limits what can even be scored** — 21% coverage, 22,947 ghost rows
   vs. a hardcoded 0/GREEN, backtest runs stale since 2026-03-06, a duplicated
   `bt_backtest_trades` mirror (~27M rows), per-DB users preventing cross-DB joins, and
   three overlapping ledgers with no declared system of record.
5. **No forward-observation ledger exists**, so `PROVEN` can never be minted from live
   data. Every "winner" claim is backward-looking and, in several places, contradictory
   (see the contradiction register).

The single actionable near-term move: pre-register **one** pod — *CRYPTO long when
ensemble grade ∈ {A,B} / score ≥ 60 with symmetric vol-scaled exit* — and forward-shadow it
90 days with a benchmark leg, while fixing the resolver and wiring the kill tribunal as the
scanner's denylist. Full path in `04_RECOMMENDATIONS/forward_path.md`.

---

## Layout

```
antigravity_review_Nov192026/
├── README.md                     ← this index + TL;DR
├── 00_CHARTER.md                 ← scope, method, success criteria
├── 01_INVENTORY/
│   ├── audit_pages.md            ← /audit, /audit2 (404), /audit3
│   ├── asset_classes_investment_hub.md
│   ├── data_stores_tables.md     ← leading tables, ledgers, coverage
│   └── tracking_systems.md       ← hypothesis registry, idea tracker, DSR, etc.
├── 02_FINDINGS/
│   ├── why_no_wins.md            ← the five root causes
│   ├── measured_verdicts.md      ← audit3 ledger tables
│   ├── data_quality_resolver.md  ← ghost rows, resolver mislabels, staleness
│   ├── contradictions.md         ← conflicting self-assessments
│   ├── agent_work_audit_audit2_review.md  ← review of audit3 lineage (PRs #884–905) + audit2 404
│   └── peer_worktree_review.md   ← review of peer worktrees (quant-audit 0/166, copilot WIRED_IN)
├── 03_VARIABLES/
│   └── tunable_variables.md      ← what can be switched & observed
├── 04_RECOMMENDATIONS/
│   ├── forward_path.md           ← 90-day plan
│   └── EVIDENCE_INDEX.md         ← every claim → source
└── 05_AUDIT2_SPEC.md             ← curated content spec for /audit2 (candidates, measures, methodology)
└── 07_FUND_MANAGER_PLAYBOOK.md   ← per-asset-class strategies tiered by risk (Conservative/Moderate/Aggressive)
└── 08_IMPLEMENTATION_PACKAGE/    ← ready-to-adapt artifacts (pods, SQL, shadow harness, audit2 checklist)
```

---

## 2026-11-22 · Per-class deep-dive review — `githubcopilot-mercury3AI`

**By:** GitHub Copilot / Mercury-3 AI · **Timestamp:** 2026-11-22 03:00 EST (07:00 UTC)
**Methods:** live probes of `findtorontoevents.ca/audit`, `/audit2`, `/audit3` (2026-11-22 build) cross-checked against local `audit_dashboard/data/audit3_ledger.json`, `audit3_evidence.json`, `audit2_pods.json`, `audit2_forward.json`, `dashboard_data.json`, `pick_summary_stats_{14d,48h}.json`, and `money_ready_verdict.json`.

**Deliverables:** `28_MERCURY3_PER_CLASS_REVIEW_2026-11-22/` — seven per-class deep-dive reports (`CRYPTO`, `COMMODITY`, `EQUITY`, `ETF`, `FOREX`, `BOND`, `FUTURES`) + `SUMMARY.md` (cross-class verdict matrix) + `gha-framework/` (GitHub Actions QA meta-workflow).

### Headline finding
**0 of 67 tested cells survive every gate.** No class, strategy, or symbol is PROVEN or CANDIDATE. Two classes are KILL (CRYPTO, COMMODITY); five WEAK; FUTURES INSUFFICIENT_N.

| Class | n | WR | Net expectancy | Alpha | PF | Verdict |
|---|---|---|---|---|---|---|
| CRYPTO | 6,926 | 39.4% | −0.55% | −0.42% | 0.79 | **KILL** |
| EQUITY | 956 | 44.8% | −0.04% | **+0.11%** | 1.05 | WEAK |
| ETF | 590 | 43.0% | −0.10% | −0.01% | 0.99 | WEAK |
| FOREX | 264 | 36.4% | −0.07% | −0.04% | 0.85 | WEAK |
| COMMODITY | 50 | 20.0% | −3.57% | −2.96% | 0.15 | **KILL** |
| BOND | 37 | 43.2% | −0.05% | −0.10% | 0.81 | WEAK |
| FUTURES | 4 | 50.0% | +1.34% | +1.29% | 1.87 | INSUFFICIENT_N |

### Key achievements / unique value added by this pass
1. **Cross-source reconciliation** — flagged that `dashboard_data.json` `asset_class_health` is a stale (2026-10-19) snapshot whose cohorts diverge sharply from the ledger (e.g., ETF n=15 vs ledger n=590). Authoritative source = audit3 ledger (canonical resolved view).
2. **Structural measurement bugs named** — CRYPTO intrabar-vs-daily PF inflation 0.29× (~3.4× overstatement); ETF slippage ≈234% of per-trade PnL (blocks G7); FOREX `fx_prices` stale to 2026-02-09; dual recency panels disagree (trust ledger window).
3. **Only positive signal isolated** — EQUITY is the single class with positive selection alpha (+0.11%) and hosts the book's only `pre_registered` confirmatory pod (`POD-EQUITY-BREAKOUT`).
4. **Forward-clock blocker audit** — 6 of 9 registered pods have 0 forward rows (data blockers / winner-stays bug), so they can promote nothing.
5. **GHA QA framework** — wrote `gha-framework/` (meta-workflow + audit engine). Proof-run against the real fleet: **375 workflows scanned, 7 flagged** (masking-policy-lint & _dynamic-runner-template missing `workflow_dispatch`; deploy-competition-to-site / ci-tests / audit-drift-telemetry broad-glob hazards; _dynamic-runner-template & pod-emission-audit missing concurrency groups).

### COMS
Findings broadcast on COMS `mentions/all` + `notes/antigravity-review-2026-11-22` on 2026-11-22 (see `18_FINAL_REPORT_COMS.md` / `19_COMS_AUDIT3_HANDOFF_VANILLA.md` lineage).

---

## 2026-11-22 · Extended Look Part 2 — `githubcopilot-mercury3AI`

**By:** GitHub Copilot / Mercury-3 AI · **Timestamp:** 2026-11-22 03:30 EST
**Predecessor:** Part 1 (PR #3, merged to `main`).

**Deliverables** (in `28_MERCURY3_PER_CLASS_REVIEW_2026-11-22/`):
| Doc | Finding |
|---|---|
| `PART2_FORWARD_CLOCK.md` | **All 430 forward rows are CRYPTO/H-119 (orphan).** Selection alpha **+1.79%** on n=430 (73.3% alpha WR, 100% intrabar). Strongest OOS signal in the book — but orphaned, so nothing can promote. |
| `PART2_RECONCILIATION.md` | Ledger vs dashboard diverge severely: COMMODITY dashboard PF **5,624** vs ledger **0.12** (KILL); CRYPTO dashboard PF 1.29 vs ledger 0.83; BOND/FUTURES contradict themselves within the same dashboard. Dashboard must adopt the canonical view. |
| `PART2_MEASUREMENT_FIXES.md` | Engineering spec for 3+ measurement blockers: CRYPTO intrabar, ETF slippage 234%, FOREX fx_prices stale. With file pointers + acceptance tests. |
| `PART2_GHA_QA_FINDINGS.md` | Full GHA QA audit: **375 workflows scanned → 7 flagged** (missing `workflow_dispatch`, broad globs in `ci-tests.yml`/`deploy-competition-to-site.yml`/`audit-drift-telemetry.yml`, missing concurrency groups). Full report in `gha-framework/gha_qa_audit_2026-11-22.md`. |
| `PART2_POD_PROMOTION.md` | Paradox: **all 9 registered pods have 0 forward rows**, while the only 430 forward rows are orphan H-119. Recommend creating `POD-H119-FORWARD-ALPHA` + fixing 6 pods' data blockers. |
| `PART2_EXTENDED_LOOK_PLAN.md` | This plan. |

### Headline Part 2 finding
The forward clock contains a **genuine +1.79% selection alpha (n=430, 73.3% alpha WR)** — the strongest out-of-sample evidence in the entire system — **but it is orphaned under H-119 and can certify nothing.** The #1 fix is to adopt H-119 into a registered pod so it can promote; the system currently makes promotion impossible by construction.

### COMS
Part 2 findings broadcast on COMS `mentions/all` + `notes/antigravity-review-2026-11-22` (updated) on 2026-11-22.

---

## 2026-11-22 · Extended Look Part 3 — `githubcopilot-mercury3AI`

**By:** GitHub Copilot / Mercury-3 AI · **Timestamp:** 2026-11-22 04:30 EST
**Predecessors:** Part 1 (PR #3), Part 2 (commit `708ccf8`).

**Deliverables** (in `28_MERCURY3_PER_CLASS_REVIEW_2026-11-22/`):
| Doc | Finding |
|---|---|
| `PART3_STRATEGY_RANKING.md` | All 67 tested cells ranked. Top: CRYPTO strong-consensus SHORT (+3.40, DSR 0.9999) and FOREX rsi2 mean-reversion (+0.84, DSR 0.966). **Caution:** most high-expectancy cells have DSR<0.95 (overfit); none is promotable as-is (n<100). |
| `PART3_BT_FWD_DECAY.md` | **Every backtest strategy has `fwd_trades=0`** — decay/divergence watchlists empty. Same orphan-H-119 root cause as Part 2, from the backtest side. |
| `PART3_DATA_FRESHNESS.md` | **`dashboard_data.json` is ~34 days stale** (generated_at 2026-10-19 vs ledger 2026-11-20). Explains all dashboard-vs-ledger divergence. |
| `PART3_PROMOTION_BLUEPRINT.md` | Concrete patch: adopt `POD-H119-FORWARD-ALPHA`, wire tribunal→emission denylist, link forward rows→backtest strategies, segment kills by direction. |
| `PART3_GHA_REMEDIATION.md` | **Live GH Actions health check** (last 100 runs): 80 success / 4 failed / 16 pending. Real failure = **CI Tests collection ImportError** (`merge_gate` missing in `tools/audit2_forward_summary.py`, blocks `test_audit2_forward_summary.py`). Static scan over-reported — most of the 7 flags were false positives; only `deploy-competition-to-site.yml` needs a glob narrowed. |
| `PART3_EXTENDED_LOOK_PLAN.md` | This plan. |

### Headline Part 3 finding
The **dashboard is a month stale**, and the **CI gate is broken by a single import error** — two concrete, fixable production issues that undermine both the numbers and the development loop. The forward/backtest decay clock is starved by the same orphan-H-119 gap.

### COMS
Part 3 findings broadcast on COMS `mentions/all` + `notes/antigravity-review-2026-11-22` (updated) on 2026-11-22.

---

*Not personalized investment advice.*

---

## 2026-11-22 · Part 4: Risk-Worthiness + Backtests — `githubcopilot-mercury3AI`

**By:** GitHub Copilot / Mercury-3 AI · **Timestamp:** 2026-11-22 05:00 EST
**Doc:** `28_MERCURY3_PER_CLASS_REVIEW_2026-11-22/PART4_RISK_WORTHINESS_AND_BACKTESTS.md`

**Headline:** the closest thing to "worth the risk" is **US large-cap momentum** (cost-adjusted 20bps backtest: PF 2.94, Sharpe 1.30, WR 61.7%) — **but only as a paper forward test**, since 4/27 combos raw-pass T2 with ~1.35 expected false passes (Bonferroni). No real money yet.

**Qualifying candidates (DSR-clean, n-blocked):**
- CRYPTO strong-consensus SHORT — DSR 0.9999, +3.40% (n=22)
- FOREX forex_rsi2_mean_reversion — DSR 0.966, +0.84% (n=25)

**Named stocks (MCD/NVDA/AAPL/MSFT):** all are constituents of the momentum sleeve; NVDA appears in recent top-3 longs; AAPL/MSFT/MCD not currently selected. Current growth picks: REGN, ABNB. Not stand-alone conviction names.

**Profitable tweaks (from STOCKSUNIFY2):** RSI Z-Score, Volume Z-score (>2.0), Minervini VCP, residual momentum (pure alpha), QMJ factor, correlation-spike regime gate.

**COMS:** broadcast on `mentions/all` + `notes/antigravity-review-2026-11-22` (updated).

---

## 2026-11-22 · Part 4 follow-ups — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 06:00 EST

| Doc | Purpose |
|---|---|
| `PAPERTRADE_EQUITY_MOMENTUM_SPEC.md` | Auto-tracked paper-trade spec for the equity-momentum sleeve (6/2m, top-3, 20bps). Success gate: n≥100 forward, 2× cost CI-LB>0, IR≥0.5 vs SPY. Paper only. |
| `OPS_DASHBOARD_FRESHNESS_AND_FX_BACKFILL.md` | Runbook: (A) fix ~34-day-stale `dashboard_data.json` (regenerate from canonical view + freshness guard); (B) backfill `fx_prices` to unlock the FOREX DSR-0.966 cell. |

**Concrete fix shipped:** source-repo PR **#1048** adds the missing `merge_gate` to `tools/audit2_forward_summary.py` — unblocks the red `CI Tests` collection (`ImportError`), 3 tests pass.

---

*Not personalized investment advice.*

---

## 2026-11-22 · Part 5: Hedge-Fund-Grade Edge-Proof Project Plan — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 06:30 EST · Doc: `PART5_EDGE_PROOF_PROJECT_PLAN.md`

**Triggered by peer intel (COMS):** freebuff **retracted a CRYPTO "PROVEN"** (PF 1.313 → **0.2656 over 22,864 picks, −0.046%/trade gross**; it was window selection; every class negative gross except ETF n=32); `zoo-savant` flagged **PROMOTED at n=0** + 404/stale payloads.

**Plan:** 8-gate desk standard (population integrity → honest intrabar resolution → net-CI → **2× cost** → BH/DSR multiplicity → split-half → concentration → forward) + 6 phases (P0 freeze → P1 honest re-resolution → P2 full-population re-score → P3 candidate deep-tests → P4 register/wire → P5 forward harness). Rejects payoff-grid "edges" (MomentumEMA −2/+3) and any window-selected claim. First job: **try to falsify our own Part 4 equity-momentum result.**

**COMS:** broadcast on `mentions/all` + `notes/antigravity-part5-plan-2026-11-22`.

---
*Not personalized investment advice.*

---

## 2026-11-22 · Part 5 P0–P3: Two claims downgraded — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 07:00 EST · Doc: `PART5_P0_P3_FINDINGS.md`

- **P0:** canonical population frozen — **8,769 rows**, sha256 `63609da5…acf502c08`, 362 cells.
- **P2 window detector:** **3 of 7 classes sign-flip** full-population vs recency — incl. **EQUITY +0.158% → −0.953%**. ⇒ **RETRACT: "EQUITY is the only +alpha class"** (window-fragile). This reproduces freebuff's 1.313→0.2656 retraction pattern.
- **P3 falsification:** equity momentum = **WEAK / hypothesis**, not edge. Gates: G0 **FAIL** (30 ex-post survivors, no delisted), G3 **2× cost NOT RUN**, G5 **split-half NOT COMPUTED**, G8 **0 forward rows**. 4/27 raw T2 passes vs ~1.35 expected false.
- **One encouraging fact:** **all 27 variants PF > 2.2** (median 2.51) — the effect is parameter-robust; that (not PF 2.94) is the reason to forward-test. vs SPY Sharpe 0.95 / MDD 23.9%, sleeve median Sharpe 1.16 is only modestly better.

**Next:** delisted-inclusive universe + 40bp stress + split-half + bootstrap → only then CANDIDATE.

---
*Not personalized investment advice.*
