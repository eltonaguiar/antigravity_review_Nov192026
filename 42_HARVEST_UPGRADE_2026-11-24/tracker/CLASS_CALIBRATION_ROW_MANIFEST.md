# Track B row manifest -- auditable exclusion list

zoo-savant, 2026-11-25. Source input: the files declared in
`tracker/DATA_MANIFEST_2026-11-24.json` (`harvest_499.json` for the consensus trend,
`analyst_actions.csv` for the universe), all verified present with matching sha256 on this host.
`class_calibration.md` and its statistics were **not** changed or edited.

## Row counts

| | rows |
|---|---|
candidates | **1467** |
included | **963** |
excluded | **504** |

## The exclusion rule, in one sentence

A candidate event is excluded when its forward window cannot be priced -- i.e. the
entry bar (first trading day after the 1st of the month following the period) or the
exit bar (one month later) is missing for the symbol, or the benchmark lacks a close on
either date, or the price is non-finite or non-positive.

Measured reason breakdown of the 504: **all 504** are "no complete forward window
(entry/exit bar missing)". No row was excluded for a missing benchmark date, a
non-positive price, or a non-finite net return.

## Provenance

- CSV: `CLASS_CALIBRATION_ROW_MANIFEST.csv`, one row per candidate:
  `symbol,date,bucket,included,exclusion_reason` (`bucket` is the period: -1m / -2m / -3m).
- sha256 of the CSV: `7b6cf10c46f73b2b9fbe02a2601a622dbebb80ec25e4d56c971dde7fde5ce575`
- Reproduced by the same rule order as `zoocode/class_calibration.py` (publication lag on,
  symbols taken in sorted order up to 499, yfinance daily closes).

## What this does not fix

The row list makes the exclusion rule *checkable*, but the input is not on origin, so a
reader still cannot rerun it from the repo alone -- they need the manifest's local paths.
And because prices come from a live yfinance call, a re-run on another day can move
events between "included" and "excluded" as windows age; the sha256 pins *this* run.
