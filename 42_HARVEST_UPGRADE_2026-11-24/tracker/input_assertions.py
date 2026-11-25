#!/usr/bin/env python3
"""Pre-statistic denominator guards.

A statistic is not allowed to print a verdict unless its denominator is declared,
non-zero, and measurably populated.  Use these before computing the statistic, not
after; the point is to fail with the offending bucket named.

API:
    require_denominator(metric, declared, value)
    denominator_coverage(metric, rows, field, max_missing=0.10)
    require_leverage(metric, value, max_plausible)
    require_unit_scale(metric, observed, expected, rel_tol=0.25)
    bucket_status(metric, n, floor)
    guarded(metric, fn) -> {"status": "OK"|"DATA_INVALID"|"UNMEASURED", ...}
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any, Callable, Iterable


class DataInvalid(Exception):
    def __init__(self, metric: str, reason: str):
        self.metric = metric
        self.reason = reason
        super().__init__(f"{metric}: {reason}")


@dataclass
class MetricResult:
    metric: str
    status: str          # OK | DATA_INVALID | UNMEASURED
    reason: str = ""
    value: Any = None


def require_denominator(metric: str, declared: str, value: float) -> None:
    """The metric must name its denominator and the denominator must be > 0."""
    if not declared or not str(declared).strip():
        raise DataInvalid(metric, "denominator is not declared")
    if value is None or value <= 0:
        raise DataInvalid(metric, f"declared denominator {declared!r} is non-positive ({value!r})")


def denominator_coverage(metric: str, rows: Iterable[dict], field: str,
                         max_missing: float = 0.10) -> float:
    """Print and enforce the share of rows with missing/zero denominator values."""
    rows = list(rows)
    if not rows:
        raise DataInvalid(metric, "no rows for denominator coverage")
    missing = sum(1 for r in rows if r.get(field) in (None, "", 0, 0.0, "0", "0.0"))
    share = missing / len(rows)
    print(f"[{metric}] denominator field={field!r} rows={len(rows)} "
          f"missing_or_zero={missing} share={share:.2%} limit={max_missing:.0%}")
    if share > max_missing:
        raise DataInvalid(metric, f"denominator {field!r} missing/zero on {share:.2%} of rows "
                                  f"(limit {max_missing:.0%}; {missing}/{len(rows)})")
    return share


def require_leverage(metric: str, value: float, max_plausible: float) -> None:
    """Per-unit-of-equity figures cannot exceed a declared physical/accounting maximum."""
    if max_plausible <= 0:
        raise DataInvalid(metric, "max_plausible leverage is not declared")
    if value is None or value > max_plausible:
        raise DataInvalid(metric, f"leverage {value!r}x exceeds declared maximum {max_plausible}x")


def require_placebo_p95(metric: str, p95_bps: float, n: int,
                        expected_sd: float = 0.1329, rel_tol: float = 1.0) -> None:
    """A mean-null p95 must be 1.645*sd/sqrt(n), not a per-event percentile.

    This catches the 26x error: 2733 bp at BofA implies an impossible 390% per-event
    sd; the expected p95 at sd=13.29% is ~99.6 bp for n=482.
    """
    if n is None or n <= 0:
        raise DataInvalid(metric, "placebo n is non-positive")
    expected = 1.645 * expected_sd * 10000.0 / math.sqrt(n)
    require_unit_scale(f"{metric} placebo_p95", p95_bps, expected, rel_tol=rel_tol)


def require_unit_scale(metric: str, observed: float, expected: float,
                       rel_tol: float = 0.25) -> None:
    """Catch a denominator/numerator unit mismatch before it becomes a 10x verdict."""
    if expected == 0:
        raise DataInvalid(metric, "expected scale is zero")
    ratio = observed / expected
    print(f"[{metric}] observed/expected scale={ratio:.4f}")
    if abs(ratio - 1.0) > rel_tol:
        raise DataInvalid(metric, f"unit scale {ratio:.4f}x differs from 1.0 by more than "
                                  f"{rel_tol:.0%}")


def bucket_status(metric: str, n: int, floor: int) -> MetricResult:
    """A bucket at zero or below its floor is UNMEASURED and cannot carry a verdict."""
    if n is None or n <= 0:
        return MetricResult(metric, "UNMEASURED", f"bucket population is zero ({n})")
    if n < floor:
        return MetricResult(metric, "UNMEASURED", f"bucket n={n} is below floor {floor}")
    return MetricResult(metric, "OK", f"bucket n={n} >= floor {floor}", n)


def guarded(metric: str, fn: Callable[[], Any]) -> MetricResult:
    """Run a statistic and convert assertion failures into DATA_INVALID with reason."""
    try:
        return MetricResult(metric, "OK", value=fn())
    except DataInvalid as e:
        return MetricResult(metric, "DATA_INVALID", e.reason)


def _selftest() -> int:
    print("input_assertions selftest")
    cases = []

    cases.append(guarded("zero_denom", lambda: require_denominator("zero_denom", "equity", 0)))
    cases.append(guarded("unit_10x", lambda: require_unit_scale("unit_10x", 10, 1)))
    rows = [{"exposure": 0}] * 115 + [{"exposure": 1}] * 373
    cases.append(guarded("coverage", lambda: denominator_coverage("coverage", rows, "exposure")))
    cases.append(guarded("leverage", lambda: require_leverage("leverage", 1133.6, 50)))
    cases.append(guarded("old_p95", lambda: require_placebo_p95("old_p95", 2733.86, 482)))
    cases.append(guarded("new_p95", lambda: require_placebo_p95("new_p95", 99.6, 482)))
    cases.append(bucket_status("empty_bucket", 0, 30))
    cases.append(bucket_status("floor_bucket", 12, 30))
    cases.append(bucket_status("ok_bucket", 100, 30))
    for c in cases:
        print(f"  {c.metric:18s} {c.status:12s} {c.reason}")
    expected = ["DATA_INVALID", "DATA_INVALID", "DATA_INVALID", "DATA_INVALID", "DATA_INVALID", "OK", "UNMEASURED", "UNMEASURED", "OK"]
    got = [c.status for c in cases]
    ok = got == expected
    print("selftest", "PASS" if ok else f"FAIL got={got}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
