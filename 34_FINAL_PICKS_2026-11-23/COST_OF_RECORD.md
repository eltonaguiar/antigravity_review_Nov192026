# COST OF RECORD — the only admissible cost input for a pick row

**Status:** canonical as of 2026-11-23. Owner: operator. Any pick row whose `COST` cell disagrees with this table is
**inadmissible until reconciled** — not "conservative", not "a different view". A cost labelled `measured` must be one of
these numbers or carry its own artifact path and a named reconciliation against this table.

Why this file exists: in three consecutive filings the same word — *measured* — has carried cost values that differ by
**3× to 20×** across agents. That is a provenance failure, not a modelling disagreement, and it is the defect that has
most often decided a verdict.

## The table

| Class | Round trip (bp) | Basis | Provenance |
|---|---|---|---|
| **Bond ETF** | **0.6144** | measured | SHY, cheapest instrument measured anywhere; bond-ETF composite 1.2125 bp |
| **ETF** | **6.7122** | measured | 1-min upper bound; house band |
| **Index** | **8.0325** | measured | broad-market index |
| **Direct equity** | **12.0749** | measured | spread + impact at 0.008% ADV participation |
| **Equity (spread only)** | 4.98 | measured, **LOWER BOUND** | spread-only, excludes impact — always label as lower bound |
| **FOREX** | **7.533** | measured, **UPPER BOUND** | Tiingo top-of-book, thin Sunday reopen; weekday London/NY not yet run |
| **FOREX (weekday)** | 4.98 | measured, other desk | do not mix with 7.533 in one ranking; name which |
| **Crypto — major** | **20.0** | measured band | |
| **Crypto — alt** | **52.0** | measured band | |
| **Commodity** | 10.0 /side | **ASSUMED** | never label measured |
| **Futures** | **UNMEASURED** | — | any row is `CANDIDATE` at best |
| **Options** | **UNMEASURED** | — | |
| **Mutual fund** | expense ratio only | measured (published MER) | not a spread; do not add to a round-trip column |

## The two labels that are not interchangeable

- **`measured`** — reproduced from our own bars or a named artifact in this estate, with a path.
- **`assumed`** — a number someone chose. Permitted in a row, but it may not be used to pass a gate, and it must be
  stress-tested at 2× before the row is called `CANDIDATE`.

## Cross-agent effects on record (2026-11-23)

| Filing | Cost used | Verdict effect |
|---|---|---|
| **Zoo Code** | house record exactly (12.0749 equity, 7.533 FX, 0.6144 bond) | none — internally consistent |
| **GitHub Copilot** | house record, plus its own 4.98 lower bound, **both shown** and the disagreement named | none |
| **Kilo Code** | 2.0 equity, 2.0 ETF, 1.0 FX, 10.0 bond — **labelled measured** | no verdict flips; every net figure overstated by 4.7–10.1 bp |

**Sensitivity, computed:** at the cost of record, CVX 178.9→168.8, AMD 119.1→109.0, AMC 84.3→74.2, AAPL 58.7→48.6,
BAC 51.9→41.8, SOXX 34.0→29.3, XLE 28.0→23.3, XLF 21.9→17.2, AUDJPY 61.6→55.1, ENJ 89.1 (unchanged, already at the
crypto band), TLT −22.0→−12.6. **Zero sign flips, zero rank changes.** The ranking survives; the provenance claim does
not.

## Rule going forward

1. Quote the number from this table, or cite an artifact that reconciles to it.
2. If a measurement disagrees, **show both and name the disagreement in the filing** (Copilot's pattern, §2 and §4 of
   its file, is the standard).
3. A row costed below this table without a lower-bound justification is rejected on provenance, even if its conclusion
   is right.
