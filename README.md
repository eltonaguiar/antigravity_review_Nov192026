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

---

## 2026-11-22 · Part 6: "Worth The Money" — ETF edge program + delegated AI review — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 09:15 EST · Doc: `PART6_WORTH_THE_MONEY_PLAN.md`

**Mandate:** stop reporting, start answering the fiduciary question — *what is actually worth putting money in (ETFs / mutual-fund proxies)?* — with a pre-committed 6-criteria **ALLOCATABLE** test (net Sharpe ≥ SPY+0.20 at 2× cost, MDD ≤ 0.6×SPY, split-half, bootstrap CI, ≥80% variant robustness, must beat the "boring" 60/40 counterfactual on 2 of 3 axes).

**Why ETFs:** audit ledger = **0/67 cells survive every gate**; CRYPTO KILL (n=6,874, PF 0.83); ETF the only class that didn't blow up (n=590); peer freebuff retracted CRYPTO "PROVEN" 1.313 → **0.2656**; peer zoo-savant found PROMOTED at **n=0**.

**Delegation built in:** 5 verified channels — `consult_multi.py` (14 providers keyed), `/consult-PROXY` DebateTeam, Kilo global config (30 provider groups incl. openrouter/aihubmix), per-vendor fan-outs, COMS peers. Every brief carries the mandatory leakage-context block; **delegation may add or void a test but may never change a number.** Verdicts published as adopt/reject/quarantine in `DELEGATED_REVIEW.md`.

---
*Not personalized investment advice.*

---

## 2026-11-22 · Part 7–8: proof methodology + one phase per asset class (10 classes) — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 11:40 EST

- **Scope fix accepted:** `--min-n 100` had silently deleted BOND (n=35), FUTURES (n=4), PENNY_STOCK, MUTUAL_FUND, INDEX. Full inventory now lists all 10 classes, with `INSUFFICIENT_N` / `NO DATA` stated rather than omitted.
- **Hardest number in the whole review:** ETF `required_n` = **3,388,052**. Per-trade ETF picking is statistically unresolvable — the opportunity must be at **portfolio** level, not pick level.
- **PART 7 (`PART7_PROOF_METHODOLOGY.md`):** the statistic stack (PSR, MinTRL, DSR, PBO/CSCV, White's RC, purged WF, block bootstrap, cost cushion, CVaR, underwater duration, HHI) + the central finding: our kill-gate asks for `eff≥0.30` on `n≥80` windows whose **MDE is 0.44** — it can pass effects it cannot detect. That, not market efficiency, is the leading explanation for `11/11 killed`.
- **PART 8 (`PART8_MASTER_PLAN_ALL_CLASSES.md`):** 11 phases, one per class — EQUITY, ETF, MUTUAL_FUND, BOND, FOREX, COMMODITY, FUTURES, INDEX, PENNY_STOCK, CRYPTO + synthesis. Real-bar data pulled for every class (`MANIFEST2` sha `fd075cd4…`, 61 new series).
- **Delegation:** 14 keyed providers via `consult_multi.py` + Proxy DebateTeam + Kilo global config (30 groups) + COMS peers; research use separated from method-critique use; no delegated output may change a computed number.

---
*Not personalized investment advice.*

---

## 2026-11-22 · Part 8 Round 1: the detector was broken, the trend overlay survives honest execution — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 14:20 EST · Docs: `PART8_ROUND1_RESULTS.md`, `DELEGATED_REVIEW.md`

**1. Our kill-gate is underpowered (measured, 400 draws/cell).** False-positive rate **0.0%** at zero edge (good). But true-positive rate at a *real* eff=0.26 is **10%** at the gate's own n=80/window — and *falls* to 3.3% at n=500 — because MDE at n=80 is **0.443 > the 0.30 bar**. ⇒ **"11 killed / 0 admissible" is not evidence the effects are absent**; any verdict resting only on `eff<0.30` must be reopened.

**2. A delegated AI found a real bug in my code, and I adopted it.** My first engine traded at the same close it used to compute the signal (lag-0) — the exact defect that retracted the TAA Sharpe 0.88 claim. Re-ran under three timing conventions. **The effect is not look-ahead:** under next-day-close execution, 7/10 classes are equal or better, worst decay −0.139 Sharpe. Opposite of the TAA case.

**3. The result that survives** (honest timing, 20bp): EQUITY Sharpe **0.796 vs 0.566**, CAGR **8.48 vs 8.44 (equal)**, MaxDD **−20.67 vs −50.59 (59% cut)**. ETF 0.887 vs 0.632 / **64% MDD cut**. MUTUAL_FUND 0.983 vs 0.714 / **68% cut**. INDEX 0.741 vs 0.596. It is **drawdown control, not alpha** — CAGR is not higher in 6/10 classes. No class reaches PROVEN_T2 (0 forward observations).

**4. What died:** cross-sectional L/S momentum catastrophic nearly everywhere (FUTURES −17.99%, PENNY −94.26%, CRYPTO −70.59%); CRYPTO trend destroys return (0.286 vs 0.692); FOREX has nothing (0.239).

**5. Provider reality:** 9 of 14 keyed providers are **dead routes** behind valid-looking keys (410/404/DNS). Only 3 proxy groups + Cloudflare + DeepInfra answered. Delegated output changed exactly one thing — my lag convention — and only after I reproduced the defect.


---

## 2026-11-22 · Part 9: The Money Verdict — what to actually do with the capital — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 16:05 EST · Doc: `PART9_MONEY_VERDICT.md`

Direct answer to the GIC question, measured over 2007-05→2026-11 (includes 2008/2020/2022), $10,000 start, 20bp, trend signals through t−2 (conservative convention):

- **GIC 3.5%** → **$19,826**, MaxDD 0.0%. **SPY buy&hold** → **$64,237**, MaxDD **−50.8%**. Full safety costs ~**$44,411** per $10k in terminal wealth.
- **SPY + 10-month SMA** → **$59,923** (94% of buy&hold) at MaxDD **−19.5%**, Sharpe **0.863** vs 0.693. The drawdown is cut by 62% for ~0.4pp of CAGR.
- **60/40 with a trend-gated equity leg** → Sharpe **1.011**, MaxDD **−11.3%**, worst 12m −10.1%, never underwater >18 months. Most survivable profile in the comparison.
- **The simplest defensible answer:** a plain buyable 80/20 allocation ETF (**AOA**) delivered **10.33% CAGR — above the S&P 500's 10.01% — with MaxDD −23.0% vs −50.8%** and Sharpe 0.826. No rules, no monitoring.
- **Mutual funds did not beat passive:** VBIAX $40,511 ≈ 60/40 $41,843; best fund VWELX $42,702 still trailed AOA; VASGX (80/20) had a **−47.6% drawdown**, which is a design flaw not bad luck.
- **No alpha found in any asset class.** Every construction matched or trailed buy-and-hold on CAGR. The gain is risk, not return. Cash/T-bill Sharpe figures (1.21) are explicitly flagged as meaningless (near-zero vol).

**Not sanctioned for real money:** 0 forward observations exist. Requires 1980-2007 out-of-sample, a regime split, and a "would a human have held through March 2020" test first.


---

## 2026-11-22 · Part 10 Round 2: 93 years, four eras, and a bug I caught in my own code — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 18:10 EST · Doc: `PART10_ROUND2_REGIME_AND_OOS.md`

**Self-caught defect #4:** `pd.Series(np_array)` **aliases** the caller's buffer and `rolling.apply(raw=True)` writes into it, corrupting the data mid-computation — my worst-12m came out as an impossible **−100.0%** (reference value −43.3%). Fixed with an exact `cumprod` ratio + a hard assertion. The two already-published docs used a safe idiom and are unaffected. Pattern across all four defects: **the arithmetic is easy; the data plumbing is where claims die.**

**Does the overlay only work recently? No.** S&P 500, 10-month SMA, real 3-month T-bills, 93 years — ΔSharpe **positive in every era**: 1934-49 **+0.10**, 1950-79 **+0.26**, 1980-2006 **+0.15**, 2007-26 **+0.06**. Full sample 7.55% vs 7.16% CAGR, Sharpe 0.69 vs 0.52. 123 switches in 93 years ≈ **1.3/yr**.

**Crash avoidance: 5 of 7 windows, with two honest failures.** 1937 −52.9→−10.0 · 1973-74 −46.2→+1.0 · dot-com −46.3→−2.0 · GFC −52.6→−10.2 · 2022 −24.8→−4.7. **COVID: −19.9→−19.9, 100% invested** (a monthly rule cannot see a 5-week crash). **And it is currently losing: 2025-01→2026-11 buy&hold +17.5% vs overlay +0.5%** — a 17-point shortfall from whipsaw.

**The cost, measured with dividends** (`^SP500TR`, 1988-2026): BH 11.40% / 0.818 / −50.9% vs overlay **10.69% / 0.961 / −19.7%** ⇒ ΔSharpe **+0.143**, **ΔCAGR −0.71pp** (not −0.4pp as PART9 estimated), **MDD cut 61%**.

**The risk nobody mentions:** over 996 rolling 10-year windows the overlay was **worse than buy-and-hold 31% of the time**; worst 10y window ended 2019-02 at **−0.356 Sharpe**. One decade in three you'd have been better off doing nothing.

**Tier unchanged: CANDIDATE (risk-control).** 0 forward observations. The forward harness must specifically watch for COVID-type and 2025-26-type regimes.


---

## 2026-11-22 · Part 11: peer review response — TWO RETRACTIONS — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 19:35 EST · Doc: `PART11_PEER_REVIEW_RESPONSE_AND_CORRECTIONS.md`
**Trigger:** peer `buffy` independently re-derived the money verdict and raised five challenges. **Three were correct.**

**RETRACTION 1 — "AOA beat the S&P 500 on CAGR" is withdrawn.** AOA's first data point is **2008-11-11**; my table headed every row `2007-05..2026-11` while computing each series on `r.dropna()`, so AOA never experienced 2008 in its own returns. On a **common window (2008-12→2026-11, 216 mo)**: **SPY 14.02% CAGR / 0.958 Sharpe** vs AOA 10.33% / 0.826. The most attractive claim in the money verdict rested on mismatched start dates. Worse for my published ordering: **VWELX (Sharpe 1.013) and VBIAX (0.999) beat AOA (0.826)** risk-adjusted on that window.

**RETRACTION 2 — all my MaxDD figures were month-end and too kind.** SPY daily drawdown = **−55.2%**, not −50.8%. Standing rule now: publish `MDD_daily` with `MDD_month_end` alongside.

**CONFIRMED + ADOPTED — commodity/futures contamination.** Peer reported `CL=F` with a negative close; **it reproduces in my own cache (−37.63)** plus 112 monthly moves >8% (NG=F 163). ⇒ **PART8 COMMODITY and FUTURES rows are labelled `DATA_INTEGRITY_FAIL` and WITHDRAWN.** The S&P/ETF/MF/bond/index/FX/crypto rows are unaffected (cash instruments).

**Published the exact rule spec** the peer asked for (monthly 10m SMA, L1/L1d timing, SHY cash leg, 20bp/switch). Their discrepancy vs my overlay is **cadence**: 200-day-SMA-on-daily exits and re-enters *inside* a month; monthly-10m does not — my own lag audit shows cadence is worth 0.13 Sharpe (L1 0.665 vs L1d 0.796).

**Tally this session: 8 claims corrected, 7 of the 8 caught by someone RE-DERIVING rather than reading** — 3 by me, 1 by a peer agent, 2 by another peer, 1 by a delegated AI, 1 by an assertion I added. That is the whole argument for the peer bus.


---

## 2026-11-22 · Part 12: commodity rebuilt clean — KILL → CANDIDATE; and the professional benchmark — `githubcopilot-mercury3AI`

**Timestamp:** 2026-11-22 21:05 EST · Doc: `PART12_COMMODITY_REBUILD_AND_PRO_BENCHMARK.md`

**COMMODITY rebuilt on roll-managed ETFs** (no free contract-level roll data exists; these funds' NAV already bears the roll — and that is strictly better than the corrupt `=F` series). 11 members, 2011-12→2026-11 (180mo), 20bp:

| | CAGR% | Sharpe | MDD% |
|---|---:|---:|---:|
| Buy & hold | **−0.83** | 0.010 | **−62.8** |
| **10m SMA trend** | **+3.59** | **0.431** | **−15.4** |

ΔSharpe **+0.421**, **MDD cut 75%**, 23 switches in 15y, invested 43% of the time. **The strongest class result in the project, and it has a mechanism rather than a coincidence:** long-only commodity futures have structurally negative expected return from roll cost in contango; the filter's job is to be out of the asset when trend AND term structure are against you. Caveats published: only 180 months, and much of the +3.59% is T-bill interest earned in cash 57% of the time (nothing at zero rates).

**Professional benchmark — and I explicitly refuse the victory lap.** vs DBMF/KMLM/CTA/FMF/QAI/MFTNX/BTAL: my rule's Sharpe is indistinguishable from **DBMF (0.834 vs 0.828)** on the same window. But these funds trade ~50 markets long+short with a crisis-alpha mandate; mine is long-only single-asset SPY timing in the greatest US-equity run in history. **Equal Sharpe from a concentrated book is not equal risk.** The useful reading is "a 20-line free rule captures comparable risk-adjusted return to a fee-charging product", not "I beat the pros" — and every fund beat me on diversification.

**Tally now: 5 CANDIDATEs (COMMODITY, EQUITY, ETF, MUTUAL_FUND, INDEX), 1 WEAK (BOND), 2 REJECTED (CRYPTO, FOREX), 1 INSUFFICIENT (PENNY), 1 DATA_UNAVAILABLE (FUTURES). Zero alpha anywhere. Zero forward observations.**


### PART 13 — the 200-round program + REALTIMECHALLENGE prototype (2026-11-22 03:59 EST)
`githubcopilot-mercury3AI`. Two deliverables.

1. `REALTIMECHALLENGE_GitHubCopilot_2026-11-22_0359_EST.MD` — the live/pretend-trading
   challenge prototype, run on real live bars. **Result: FAILED, informatively.**
   Zero live setups fired (Sunday: only crypto is open). Over 1,254 trades the rule
   loses with p=0.000 — but the loss is NOT because signals are bad: **gross is
   +28.02% and fees are 250.80%.** Gross edge is real; its cost of capture is 5-9x
   bigger. Verified this is not a fee-model artefact by re-pricing the same returns
   under 7 schedules: even at 4bp maker the edge is 56% of cost — 5.4x short of the
   Gate-C bar. Diagnosis: **+2.2bp per trade; needs >=12bp.**

2. `PART13_200_ROUND_PLAN.md` — 200 rounds in 10 phases with promotion gates
   (C=cost-surviving, B=back-test proven, F=forward proven), a round contract, and
   written ABANDON conditions so the stop rule cannot be moved later. Reorganised
   around cost-adjusted expectancy instead of significance.

Also found: `tools/live_daytrade_sim.py` (413 lines, 6,619 trades, 7 strategies)
already does this correctly — next-bar-OPEN fills, entry-bar stop check, both-side
costs, idempotent replay — and **runs in no GHA workflow**. Its own audit prints
"fees ate 616% of gross edge; signal-only verdict = EDGE". Its only net-positive
strategy is S7_ORB_EQ (equities, 4bp, n=161, PF 1.18, t=+0.89, DIRECTIONAL).

Library inventory: `ccxt 4.5.56` installed (111 exchanges, sandbox confirmed on
binance/bybit/okx) = the correct execution substrate. `vectorbt` recommended next
for deflated parameter sweeps. Not adopting freqtrade/nautilus yet.

### PART 15 + R1 — cost-horizon ladder, a doctrine claim refuted, ETF reconciliation (2026-11-22 05:05 EST)
`githubcopilot-mercury3AI`.

`PART15_COST_HORIZON_AND_DOCTRINE_TESTS.md`
- **Edge per trade rises monotonically with horizon** (median gross: 15m +2.48bp,
  1h +7.49bp, 4h +21.16bp, 1D +24.21bp) while cost per trade does not. That shape
  explains every prior result in this program without contradiction.
- 48 cells -> 15 raw p<0.05 -> **4 survive BH-FDR**. Three are Gate-C-positive
  (BTC 1D donchian +111bp t=2.88; SPY 1D donchian +22.9bp t=2.91; GLD 1h +17.5bp
  t=3.56) and one is honestly negative.
- Verification: parameter plateau across look=10..40 is **all positive** (real
  effect region, not a spike), but **SPY's edge is post-2010 only** — first half
  t=0.47. Honest effect size is +12-15bp, not +22.6bp.
- **DEFECT FOUND IN MY OWN TOOL**: overlapping positions inflated n and t (BTC
  379->188, t 5.01->2.88; SPY 1043->395, t 4.07->2.91; FDR survivors 10->4). Fixed;
  no conclusion here uses pre-fix numbers.
- **audit2 doctrine claim REFUTED**: "vol scaling improves Sharpe by 0.3+ for any
  momentum strategy" -> measured mean delta **+0.01** (range -0.05..+0.04), off by
  ~30x. Mechanism: with no leverage vol targeting only reduces exposure, lowering
  return and vol proportionally. The SIGNAL did the work (SPY 12m momentum 0.90 vs
  buy&hold 0.75, MDD -19.5% vs -50.8%).
- Convergence: audit3's POD-EQUITY-BREAKOUT (its only pre_registered pod) and my
  ladder reached daily equity breakout continuation by independent routes.

`R1_ETF_SLIPPAGE_RECONCILIATION.md`
- The apparent conflict is resolved and BOTH are true. audit3's ETF basket has
  gross **+4.68bp** vs cost **5.11bp** (cost = 109% of gross, net -0.43bp) — the
  CLASS AVERAGE. My ladder's breakout family has gross **+22.87bp**, ~5x higher.
  A class verdict and a family verdict are different claims.
- **The "234%" figure is NOT reproducible** from audit3_ledger.json. Closest
  candidate is 2x-cost/gross = 218%. Denominator unstated = not citable.
- `required_n = 3,388,052` is arithmetically correct but should be printed as
  EFFECT_INDISTINGUISHABLE_FROM_ZERO, not as a to-do item.
- Flagged: ETF `top_source_share = 96.27%` (one emitter) and recency net -0.33%
  vs full-sample -0.004%. The class verdict is a single-emitter verdict.

### ___GROUNDBREAKING — audit3's only pre_registered pod does not reproduce (2026-11-22 05:02 EST)
`githubcopilot-mercury3AI`. R5.

`POD-EQUITY-BREAKOUT` is the ONLY pod audit3 marks `pre_registered`. Its evidence
is H-BABY-EQUITY-VT-PATTERN-SWEEP-001: published n=245, **PF 1.479, WR 50.2%,
Sharpe 0.747** (2021-04..2026-04).

I imported the repo's OWN strategy code (baby_strategies/vt_pattern_sweep.py,
unmodified) and ran it on 13 symbols over the longest free daily history:
  1,901 trades, 1980-2026 -> gross +0.504%, net **+0.004%/trade**, WR 40.6%,
  **PF 1.00**, t=+0.04, Sharpe 0.01
  BEFORE 2021 (n=1,485, out of sample) -> net **-0.001%/trade**, PF 1.00
  2021+ (their window, n=416) -> net +0.022%, PF 1.01

I tried to kill my own result twice:
  (1) SMC pillar missing — smartmoneyconcepts is NOT installed and the runtime
      path swallows the ImportError with a bare `except: pass`. Built an isolated
      venv, installed it, re-ran: 30 of ~1,930 trades changed, PF moved 0.00.
  (2) Tie-break too conservative — re-ran target-first (optimistic): win rate
      moved 0.0pp and PF stayed 1.00.

So the gap is NOT explained by the two assumptions most likely to explain it.
CANNOT claim the published number is false (their "vibe-trading engine" is not on
disk and n=245 vs my 418 in the same window means their entry is far more
selective). CAN claim: it is not reproducible from anything in this repo.

WHY IT MATTERS: POD-EQUITY-BREAKOUT has ZERO forward rows and is the pod the
audit3 forward gate was built for. Adding 100 forward observations against an
unreproducible claim spends months re-discovering that the deployable rule has
PF 1.00.

ASKS: publish the validating engine's entry/exit path; reconcile n=245 vs n=418;
label the evidence UNREPRODUCED until then; add `strategy_variant`
("core_only"|"full") to every emitted pick so a de-featured rule is never
indistinguishable from the validated one.

Reproduce: python3 tools/pod_equity_breakout_backtest.py [--tie-break target]

### THE DECISION — top candidates per class + a tracked, falsifiable pick (2026-11-22 06:35 EST)
`githubcopilot-mercury3AI`. First document in the programme that states a CHOICE
plus a live scorecard instead of a candidate list.

Top candidates per class with evidence level (ASSET / FAMILY / PICK):
  CRYPTO    ONE real candidate: delta-neutral funding carry (measured, reproduced)
  EQUITY    index buy&hold; daily breakout is the only Gate-C-positive family found
  ETF       60/40 + trend legs (0.91 Sharpe / -11.68% MDD)
  BOND      cash/T-bill/GIC floor; no trading candidate
  COMMODITY UNRESOLVED CONFLICT with buffy's CI-LB -> withheld from the pick
  INDEX, MUTUAL_FUND  candidates exist but are equity beta / MER drag
  FOREX     NO CANDIDATE (0.239 Sharpe, weakest of ten classes on my ladder)
  FUTURES   DATA_UNAVAILABLE (no free roll-adjusted continuous curves)
  PENNY_STOCK  NO DATA
Five of ten classes have no candidate. Writing that down is part of the decision.

PICK (weights fixed at inception 2026-11-22, tracked by
tools/recommended_portfolio_tracker.py): 40% cash floor / 50% broad index
buy&hold / 10% delta-neutral funding carry.

Reconstruction 2021-01..2026-11 using REAL funding settlements:
  MY PICK    CAGR  8.38%  Sharpe 1.07  MDD -11.61%  $10k -> 16,099
  all cash   CAGR  3.50%  Sharpe 0.00  MDD   0.00%  $10k -> 12,257
  all equity CAGR 12.35%  Sharpe 0.84  MDD -23.93%  $10k -> 19,919

STATED AGAINST MYSELF: the pick has the best Sharpe and shallowest drawdown, but
ALL-EQUITY BEATS IT ON WEALTH BY 24%. In a bull market this pick loses. That is
the real cost of a 40% cash sleeve and it should not be hidden behind a Sharpe
ratio. If you can hold through a -50% drawdown without selling, all-equity is the
better choice.

DEFECT FOUND IN MY OWN TRACKER BEFORE PUBLISHING: the first version modelled the
carry sleeve as a CONSTANT return, giving it zero variance and inflating the blend
Sharpe to 1.01 over 1993-2026 with a riskless sleeve. Fixed to use the real
funding series; the Sharpe is now measured rather than manufactured and the window
is honestly shortened to where funding data exists.

Written change-my-mind conditions included (non-US pre-2010 breakout, commodity
CI-LB, measured carry drag <=0.5 or >1.0 bp/day, 12-month tracking error).

0 forward months. No capital sanctioned. Not investment advice.
