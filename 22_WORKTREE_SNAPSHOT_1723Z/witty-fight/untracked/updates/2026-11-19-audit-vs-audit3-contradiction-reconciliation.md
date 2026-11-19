# /audit vs /audit3 contradictions: measured reconciliation (2026-11-19)

Sources: live `/audit` (1,435,761 B), live `/audit3/audit3_ledger.json`
(276,377 B, `generated_at 2026-11-19T13:02:16Z`), and a Python parse of that
ledger for the symbol table.

## 1. Two real arithmetic conflicts — one fixed, one now labelled
### 1a. Share above 100% (fixed)
`scored_rows 8605` vs `valid_closed_picks 8175` produced
`scored_share_of_valid_pct 105.26`.

Fixed in `updates/2026-11-19-audit3-coverage-honesty-fix.md`: the ratio is
withheld, `scored_share_of_valid_pct_raw` keeps 105.26, and
`denominator_reconciliation` now names the 430-row set as
`scored_but_not_dashboard_valid`.

### 1b. Candidate KPI contradicts its own symbol table (fixed)
Verified by parsing the live ledger:

```
summary.n_candidate = 0
symbols with verdict CANDIDATE = 1
  FOREX AUDJPY LONG  n=31  WR=0.8065  PF=8.6353
  net_ci_pct=[0.5044, 1.0009]  q=0.034
```

The page reads "Candidate 0" while the symbol table shows one. Root cause: the
summary counted strategy cells only and published no symbol/segment counters.

Fixed in `alpha_engine/audit3_tribunal.py` summary: added
`n_candidate_symbols` and `n_candidate_segments`, each computed from its own
table, with a regression test asserting each headline count equals its table.

Follow-up risk (not fixed): a FOREX symbol cell at PF 8.64 / WR 80.65% with n=31
deserves a stop-fill and outlier check before any sizing. This is the same
failure mode as the crypto stop-fill issue, just on a different class.

## 2. "Candidate" means two different things (wording, not data)
`/audit` labels `crypto_rsi5070_us` **"FORWARD-TRACKING CANDIDATE"**, and the card
itself says "Forward-shadow only, never sized." audit3's `CANDIDATE` is a ledger
verdict (n>=30, net CI>0, q<=0.20). Verdict: **different definitions.** The same
word is used for a tracking state and a verdict.

## 3. Confidence inversion: four values on one page
`/audit` states all of these for the same `conf>=0.90` band:
- 14.4% WR (two places, labelled "static measurement 2026-05-15")
- 47% WR (crypto filter note)
- 22.2% WR ("worst bucket" comment)
- 40% WR ("analysis of 4,578 closed trades")

audit3 does not score confidence at all. Verdict: **real internal disagreement on
`/audit`**, with no independent surface to arbitrate. One generated calibration
artifact keyed by class/band/date is the fix.

## 4. ETF: 1.9% vs 43.x is cohort, not conflict
- 1.9% = 1 win / 52 rows, labelled `sizing_source: intrabar_truth`
  (`display_wr_pct 1.9`, `display_n 52`), i.e. a 52-row intrabar slice.
- 43.84% = 256 / (586−2) on the closed ledger (flat excluded).
- 43.7% = 255 / 584 (flat included).
- 43.17% = audit3 net-of-cost wins (253 / 586).
- The literal "43.1" in `dashboard_data.json` belongs to
  `systems[kimi_riseoftheclaw].display_win_rate_pct`, a five-class system
  aggregate — not ETF.

Verdict: **different cohorts and denominators.** The defect is labelling: the
52-row slice is shown without "n=52, intrabar first-touch" next to it.

## 5. Ghost rows — confirmed
`/audit` reads live `db_health.json` (22,947 ghost rows, 10 cohorts) and warns not
to cite the 2026-05-31 "cleared" claim. Consistent with the review's data-debt
finding.

## 6. Denominators across surfaces still disagree
- `/audit` summary: 16,341 total / 7,909 valid / 7,510 integrity / 96 mirrors →
  8,735 resolved; 826 rows are resolved but not "valid" and have no label.
- audit3: 14,632 total / 8,175 valid / 8,605 scored.
- Canonical hashes differ: `aa7f7f89…` (8,735 rows) vs `4f635550…` (8,605 rows).

Verdict: **two different canonical cuts plus an undefined `valid_closed_picks`.**
The 430-row and 826-row gaps need explicit buckets. audit3's side is now labelled;
`/audit`'s 826 is not (main-branch work).

## 7. Staleness
audit3 ledger is freshest (built 13:02Z from a 10:03Z payload). `/audit` health
artifacts are 2026-11-16T03:52-04:07Z; its confidence prose is dated 2026-05-15.
Both dates are shown on the page.
