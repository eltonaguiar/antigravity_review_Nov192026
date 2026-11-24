# HARVEST rule-drift and classification fixes — 2026-11-24

All numbers below come from `docs/data/harvest_signals.json` and
`42_HARVEST_UPGRADE_2026-11-24/kilocode/test_harvest_rules.py`.

## 1. Rule drift — fixed by generation
- **Before:** `docs/harvest.html` legend and `docs/HARVEST_METHODOLOGY.md` §5 published the
  score-only rule (`≥0.3 BUY`, no buy-side condition). That rule reproduces only **60/71** labels.
- **After:** the legend and methodology are rendered from
  `42_HARVEST_UPGRADE_2026-11-24/kilocode/harvest_rules.py` (same constants as the classifier).
  - `STRONG_BUY`: score ≥ 1.0 **and** buy-side ≥ 75%
  - `BUY`: score ≥ 0.3 **and** buy-side ≥ 50%
  - `SELL`: score ≤ −0.3 **and** buy-side ≤ 30%
  - `STRONG_SELL`: score ≤ −1.0 **and** buy-side ≤ 15%
  - else `HOLD`
- **Evidence:** `test_labels_recompute_71` → **71/71** labels recompute from the five counts.
  The generator is wired into `.github/workflows/pages.yml` before upload, so the page cannot drift.

## 2. Direction — computed once, noise floor applied
- Direction is written by the pipeline (`enrich_signals.py`) and read by the page; the page does not
  re-derive it.
- New rule: `|Δ buy-side| ≥ max(2.0 pp, 100/n_now)` **and** ≥ 2 analysts changed bucket, else STABLE.
  Rows whose analyst count changed are tagged `CHURN_CONTAMINATED`.
- **Before → after counts:** `{IMPROVING 14, DETERIORATING 16, STABLE 41}` →
  `{IMPROVING 5, DETERIORATING 5, STABLE 61}`.
- **KPI test:** `test_direction_rule_and_kpi` asserts KPI counts equal row counts (and net = 5−5 = 0).
- Worked evidence:
  - DUK: Δ −2.1 pp, n_now 27 → floor 3.70 → **STABLE**, and `CHURN_CONTAMINATED` (26→27 analysts).
  - WMT: Δ +2.1 pp, n_now 48 → floor 2.08, but only **1** bucket move → **STABLE**.
  - INTC: Δ −7.3 pp, n_now 55 → floor 2.0, 5 moves → **DETERIORATING**.

## 3. Reason codes — no blank cells
Added `reason_code` to every signal, error, uncovered symbol and coverage class, from the enum:
`NO_COVERAGE_STRUCTURAL`, `NO_COVERAGE_VENDOR`, `SYMBOL_UNMAPPED`, `ACCESS_DENIED_403`,
`RATE_LIMITED_429`, `EMPTY_RESPONSE`, `STALE_OK`.
- Covered rows: `STALE_OK`.
- Mutual funds: `ACCESS_DENIED_403` (HTTP 403 plan limit).
- ETF/BOND/CRYPTO: `NO_COVERAGE_STRUCTURAL`.
- The page renders the code in the coverage table and the “Symbols with no data” table.
- **Test:** `test_reason_codes_never_blank` (signals + errors + uncovered + coverage).

## 4. Taxonomy — 328 leaves
`universe/taxonomy.json` covers **asset_class × wrapper × exposure**:
12 classes × allowed wrappers × 8 exposures = **328 leaves**, each with
`signal_availability = {sell_side: none|look_through|direct, crowd, official_rating}`.
- **Test:** `test_taxonomy_shape` (count 250–400, unique ids, allowed enum values).

## 5. Test run
```
python3 -m pytest 42_HARVEST_UPGRADE_2026-11-24/kilocode/test_harvest_rules.py -q
6 passed
```

## Files changed
- `42_HARVEST_UPGRADE_2026-11-24/kilocode/` — rules, enrichment, legend renderer, taxonomy builder, tests, raw Finnhub evidence, this report.
- `docs/data/harvest_signals.json` — prior counts, n_now/n_prior, Δ, noise floor, bucket moves, churn flag, direction, reason codes, rule constants.
- `docs/harvest.html` — generated legend (markers), reason-code columns, churn badge.
- `docs/HARVEST_METHODOLOGY.md` — §5 generated (markers).
- `universe/taxonomy.json` — 328 leaves.
- `.github/workflows/pages.yml` — renders the legend before upload.
