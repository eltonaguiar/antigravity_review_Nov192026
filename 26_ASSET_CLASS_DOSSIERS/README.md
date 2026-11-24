# 26 ASSET_CLASS_DOSSIERS - audit-surface review, 2026-11-22

Author: Zoo (subq-savant-1.4), seat `zoo-savant`. Branch
`review/2026-11-22-zoo-asset-class-dossiers` from `origin/main`.

Scope: the three audit surfaces (`/audit`, `/audit2`, `/audit3`) reviewed against frozen
evidence, with one dossier per asset class and a GitHub Actions quality framework.

## Contents

| File | What |
|---|---|
| `00_SURFACE_BASELINE.md` | page-to-fetch map, contradiction register C1-C7, metric glossary, do-not-trust list |
| `01_CRYPTO.md` ... `12_SPORTS.md` | twelve class dossiers, one fixed 8-section template each |
| `GHA_QA_FRAMEWORK.md` | design of `tools/gha_quality_framework.py` (Layers A-E) |
| `GHA_QA_RULE_CATALOG.md` | Q1-Q10 definitions, severity, and what they do not catch |
| `BLOCKERS.md` | steps that could not run (AI fan-out unavailable) and why |
| `REJECTED.md` | drafts that failed the lint or adversarial pass, and why |
| `_MANIFEST.json` | frozen artifact hashes and measured consistency checks |

The in-repo source of truth is `docs/audit_review_2026-11-22/` in
`eltonaguiar/findtorontoevents_antigravity.ca`. This folder is the published mirror.

## Cross-class verdict table

| # | Class | /audit3 ledger | /audit readiness | /audit money_ready | Blunt answer |
|---|---|---|---|---|---|
| 01 | CRYPTO | KILL | MONITORING | NOT_READY | NO edge |
| 02 | EQUITY | WEAK | MONITORING | NOT_READY | NOT PROVEN |
| 03 | ETF | WEAK | MONITORING | INSUFFICIENT_DATA | NOT PROVEN |
| 04 | FOREX | WEAK | BLOCKED | NOT_READY | UNMEASURED (coverage) |
| 05 | COMMODITY | KILL | BLOCKED | NOT_READY | NO edge |
| 06 | BOND | WEAK | BLOCKED | INSUFFICIENT_DATA | UNMEASURED |
| 07 | FUTURES | INSUFFICIENT_N | BLOCKED | INSUFFICIENT_DATA | UNMEASURED |
| 08 | MUTUAL_FUND | absent | MONITORING | INSUFFICIENT_DATA | placeholder |
| 09 | PENNY_STOCK | absent | MONITORING | INSUFFICIENT_DATA | UNMEASURED |
| 10 | MEMECOIN | absent | MONITORING | INSUFFICIENT_DATA | NO, leaning |
| 11 | INDEX | absent | absent | absent | alias, not a class |
| 12 | SPORTS | absent | absent | absent | out of scope |

## The three P0s

1. **Selection alpha is negative and significant**: 0.3696 pct per trade lost versus
   buy-and-hold, CI [-0.5673, -0.1674] (ledger `selection_alpha.overall`).
2. **Stale and broken data paths**: `/audit/data/audit2_forward.json` is 22 h stale; several
   payloads referenced by `/audit2` and `/audit3` return 404.
3. **Verdict labels without measurement**: `PROMOTED` sidecars at n 0, BOND WR 100 pct at n 2,
   FUTURES PF 1.87 at n 4.

## How numbers were checked

Every number in a dossier carries a `[SRC: ...]` marker or is the literal `UNMEASURED`.
`tools/doc_source_lint.py` enforces that; all twelve dossiers pass it.

*Not investment advice.*
