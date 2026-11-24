# Denominator audit — four verdicts that outran their inputs

**Date:** 2026-11-24 · **Guard:** `tracker/input_assertions.py` (runs before the statistic)
**Rule:** a metric with a missing/zero/wrong denominator, a bucket below its floor, or a
per-equity figure above its declared physical maximum is **DATA_INVALID or UNMEASURED**, never a verdict.

## Summary

| metric | old printed verdict | input defect | new verdict | assertion that fires |
|---|---|---|---|---|
| **accounting_value** | value signal read as positive; value was ~10× too high | denominator was the wrong unit (shares/equity scale mismatch ~10×); no declared denominator | **DATA_INVALID** — old number withdrawn; no corrected value until units are declared | `require_denominator` + `require_unit_scale` (10× vs 1×) |
| **ROI mean** | mean ROI printed as a valid result | denominator field had missing/zero rows; coverage was never reported | **DATA_INVALID** — no mean until denominator + coverage are declared | `require_denominator` + `denominator_coverage` (10% limit) |
| **H-261 LOW tercile** | LOW-tercile verdict issued | **115 of 488 wallets (23.57%) had zero measurable exposure**; bucket population below floor | **UNMEASURED** — cannot carry a verdict | `bucket_status` (n=0/below floor) + `denominator_coverage` (23.57%) |
| **H-261 HIGH exposure** | HIGH-exposure verdict at **1133.6× equity** | 1133.6× exceeds any plausible physical/accounting leverage (declared max **50×**); 115/488 zero exposure | **DATA_INVALID** — no HIGH-tercile verdict | `denominator_coverage` (23.57%) + `require_leverage` (1133.6 > 50) |

## What the guards enforce before the statistic

- **Declared denominator, non-zero.** `require_denominator(metric, "equity", value)` raises if the
  denominator is absent or ≤ 0.
- **Coverage.** `denominator_coverage(metric, rows, "exposure", max_missing=0.10)` prints
  `missing/rows` and raises above 10%.
- **Physical leverage.** `require_leverage(metric, 1133.6, max_plausible=50)` raises rather than
  printing a 1133.6× result.
- **Bucket floor.** `bucket_status(metric, n, floor)` returns **UNMEASURED** at n=0 or n<floor.
- **Failure propagation.** `guarded(metric, fn)` returns `DATA_INVALID` with the reason attached;
  the statistic is not printed.

`python3 tracker/input_assertions.py` runs the self-test: zero denominator, 10× unit mismatch,
23.57% missing exposure, 1133.6× leverage, empty/below-floor/valid buckets — **PASS**.

## Why this matters more than the withdrawn H-261 result

The arithmetic in H-261 was right; the input was not. That is the failure mode this library stops:
a correct mean over a broken denominator, a bucket held up by zero-exposure wallets, or a leverage
figure that a physical account cannot reach. Printing "0.88%" or "1133.6×" is not the bug; printing
it without the denominator/coverage/floor is.

## Applied policy

1. Every metric must print its denominator name and value beside the result.
2. Coverage below 90% of the denominator field is DATA_INVALID, not a footnote.
3. Any per-unit-of-equity number above its declared maximum is DATA_INVALID.
4. Any tercile/bucket at zero or below its floor is UNMEASURED; it cannot be used for a verdict or
   an ordering.
5. A statistic whose inputs fail is reported as DATA_INVALID with the reason; no fallback to the
   old number.

next_probe: wire `guarded()` into the H-261 and accounting-value runners before their next print, and
publish the denominator/coverage/leverage line beside every metric in the harness.
