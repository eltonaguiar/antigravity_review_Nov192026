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
│   └── contradictions.md         ← conflicting self-assessments
├── 03_VARIABLES/
│   └── tunable_variables.md      ← what can be switched & observed
└── 04_RECOMMENDATIONS/
    ├── forward_path.md           ← 90-day plan
    └── EVIDENCE_INDEX.md         ← every claim → source
```

*Not personalized investment advice.*
