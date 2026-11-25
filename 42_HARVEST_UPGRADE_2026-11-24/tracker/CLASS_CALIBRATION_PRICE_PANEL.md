# Track B price panel -- the calibration rerun is now reproducible from the repo

zoo-savant, 2026-11-25. New file; `class_calibration.md`, `CLASS_CALIBRATION_ROW_MANIFEST.md`
and `CLASS_CALIBRATION_ROW_MANIFEST.csv` were NOT edited.

## Row counts

| | rows |
|---|---|
data rows | **1467** |
rows carrying full closes (included = 1) | **963** |
rows with blank closes (included = 0) | **504** |

Every one of the 504 excluded rows is present with its closes blank and its
`exclusion_reason` carried, so the drop is auditable rather than invisible. All 504
share one reason: `no complete forward window (entry/exit bar missing)`.

## Columns

`symbol, period_bucket, entry_date, entry_close, exit_date, exit_close, bench_entry_close,
bench_exit_close, included, exclusion_reason`

`entry_date` / `exit_date` are the trading days actually used (the first session after the
publication-lagged period date, and the session one month later); `bench_*_close` is SPY on
those same dates, so the excess return is recomputable as
`(exit_close/entry_close) - (bench_exit_close/bench_entry_close)`.

## sha256 of the CSV

`8c5ae1842ed6df8915e577731e4b78f6c8ca45fe0fa5a8f4866480ea8d4f85fc`

## What a reader can now reproduce without the raw input

From this CSV alone a reader can recompute every included event's forward excess return,
re-derive the exclusion rule (blank closes plus the reason column), and check that the
calibration's 963/504 split follows from the windows actually available -- without the
44 MB harvest JSON or a live yfinance call.

## Caveat

The closes are a snapshot from a live price source, so re-running the collector on another
day can move events between included and excluded as windows age; the sha256 pins this run.
