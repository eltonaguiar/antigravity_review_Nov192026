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

*Not personalized investment advice.*
