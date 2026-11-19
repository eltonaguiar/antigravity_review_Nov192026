# 00 — Charter: financial-prediction review

**Reviewer:** antigravity_review_Nov192026 workstream
**Repo of record:** `eltonaguiar/findtorontoevents_antigravity.ca`
**Artifact store:** `eltonaguiar/antigravity_review_Nov192026`
**Date:** 2026-11-19

---

## 1. Why this review exists

The owner's question, in one line: *"We have built dozens of strategies, a hypothesis
tracker, an idea tracker, polymarket/kalshi/hydrotrader pipelines, reverse-engineered
daily/weekly top gainers, and a full audit dashboard — yet we still have no solid wins.
Why?"*

This deliverable answers that question with measured evidence, then catalogues the
variables that can be toggled and observed (counterfactual / "would we have made a profit
with minor adjustments"), and ends with a concrete forward path.

## 2. Scope

| In scope | Out of scope |
|---|---|
| `/audit`, `/audit2`, `/audit3` pages and what data they actually serve | Making changes to the source repo |
| The database schemas (`FINANCE_DB_SCHEMA_SPEC.md`, `schema-baseline.sql`) | Live trading / capital placement |
| Pick/outcome ledgers and their coverage | Fixing code (this is a report) |
| Hypothesis/idea/strategy tracking systems | Anything not in the source repo |
| Why 0 PROVEN today; the tunable variables; the forward path | |

## 3. Method

1. Probed the live pages (`findtorontoevents.ca/audit`, `/audit2`, `/audit3`) for
   HTTP status and size.
2. Parsed `audit_dashboard/data/audit3_ledger.json` + `audit3_evidence.json` (measured
   verdicts, classes, kill tribunal, candidate cell).
3. Read the hypothesis registry (`reports/hypothesis_registry.json`, 99 entries) and the
   schema spec.
4. Reviewed the recent `.MD` decision/validation docs for internal contradictions
   (e.g. `TRUE_PROFITABILITY_VALIDATED.md` vs. the audit3 ledger).
5. Confirmed `/audit2` is dead (404) and mapped the investment-hub asset classes.

Every quantitative claim is linked to a source in `04_RECOMMENDATIONS/EVIDENCE_INDEX.md`.
