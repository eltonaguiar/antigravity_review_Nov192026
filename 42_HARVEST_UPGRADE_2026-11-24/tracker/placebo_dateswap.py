#!/usr/bin/env python3
"""placebo_dateswap.py -- the falsifier a preregistered analyst claim depends on.

Claim under test: "a broker's UPGRADE predicts positive net benchmark-adjusted
return." The placebo destroys the only thing the claim relies on -- the timing
-- while keeping everything else identical:

  * for each real upgrade event, draw 1000 pseudo entry dates from the SAME
    ticker, in the SAME calendar month but a DIFFERENT year,
  * exclude any pseudo date within +/- 63 days of ANY real action by that broker
    on that ticker (otherwise the placebo lands on top of the real signal),
  * apply the IDENTICAL benchmark (same ticker's benchmark series over the same
    dates) and the IDENTICAL cost charge,
  * report the placebo distribution of net benchmark-adjusted return, its 95th
    percentile, and whether the real mean exceeds it.

Self-test (required): generate synthetic data where the real events are drawn
from the SAME distribution as the placebo. The verdict MUST come back FAIL --
if a harness can certify a signal that is not there, it certifies nothing.

Usage:
  python3 placebo_dateswap.py --selftest
  python3 placebo_dateswap.py --events events.json --prices prices.csv
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20261124
N_PLACEBO = 1000
EXCLUSION_DAYS = 63
COST_BPS = 26.0          # round turn, same as everywhere else in this programme
HORIZON = 63            # trading days approximated by calendar days below


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
def _trade_return(prices: dict[date, float], entry: date, horizon_days: int) -> float | None:
    """Return from the first price on/after entry to horizon_days later."""
    days = sorted(d for d in prices if d >= entry)
    if not days:
        return None
    start = days[0]
    target = start + timedelta(days=horizon_days)
    after = [d for d in prices if d >= target]
    if not after:
        return None
    end = after[0]
    if prices[start] <= 0:
        return None
    return prices[end] / prices[start] - 1.0


def _same_month_other_years(d: date, years: list[int]) -> list[date]:
    out = []
    for y in years:
        if y == d.year:
            continue
        try:
            out.append(d.replace(year=y))
        except ValueError:      # Feb 29 in a non-leap year
            out.append(d.replace(year=y, day=28))
    return out


def placebo_returns(events: list[dict], prices_by_ticker: dict[str, dict[date, float]],
                    bench_by_ticker: dict[str, dict[date, float]],
                    real_dates_by_broker: dict[tuple[str, str], list[date]],
                    n_placebo: int = N_PLACEBO, seed: int = SEED,
                    cost_bps: float = COST_BPS, horizon: int = HORIZON) -> dict:
    """Placebo distribution of net benchmark-adjusted return, one per draw."""
    rng = random.Random(seed)
    all_years = sorted({d.year for prices in prices_by_ticker.values() for d in prices})
    draws: list[float] = []
    real: list[float] = []
    for ev in events:
        tk, broker = ev["ticker"], ev["broker"]
        d0 = datetime.strptime(ev["date"], "%Y-%m-%d").date()
        px, bx = prices_by_ticker.get(tk), bench_by_ticker.get(tk)
        if not px or not bx:
            continue
        r = _trade_return(px, d0, horizon)
        b = _trade_return(bx, d0, horizon)
        if r is None or b is None:
            continue
        real.append((r - b) * 10000 - cost_bps)
        blocked = real_dates_by_broker.get((tk, broker), [])
        cands = [c for c in _same_month_other_years(d0, all_years)
                 if all(abs((c - bd).days) > EXCLUSION_DAYS for bd in blocked)]
        if not cands:
            continue
        for _ in range(n_placebo):
            cd = rng.choice(cands)
            pr = _trade_return(px, cd, horizon)
            pb = _trade_return(bx, cd, horizon)
            if pr is None or pb is None:
                continue
            draws.append((pr - pb) * 10000 - cost_bps)
    draws.sort()
    real_mean = statistics.mean(real) if real else None
    p95 = draws[int(round(0.95 * (len(draws) - 1)))] if draws else None
    return {"n_real": len(real), "n_placebo": len(draws),
            "real_mean_bps": round(real_mean, 3) if real_mean is not None else None,
            "placebo_mean_bps": round(statistics.mean(draws), 3) if draws else None,
            "placebo_p95_bps": round(p95, 3) if p95 is not None else None,
            "real_exceeds_p95": (real_mean is not None and p95 is not None
                                 and real_mean > p95),
            "verdict": ("PASS" if (real_mean is not None and p95 is not None
                                   and real_mean > p95) else "FAIL")}


# ---------------------------------------------------------------------------
# Self-test: real drawn from the SAME distribution as the placebo -> must FAIL
# ---------------------------------------------------------------------------
def _synthetic(rng: random.Random):
    tickers = ["AAA", "BBB"]
    days = [date(2018, 1, 1) + timedelta(days=k) for k in range(365 * 8)]
    prices, bench = {}, {}
    for tk in tickers:
        p, b, px, bx = 100.0, 100.0, {}, {}
        for d in days:
            p *= 1 + rng.gauss(0.0, 0.012)
            b *= 1 + rng.gauss(0.0, 0.012)
            px[d], bx[d] = p, b
        prices[tk], bench[tk] = px, bx
    events = []
    for tk in tickers:
        for _ in range(25):
            d = rng.choice(days[200:-100])
            events.append({"ticker": tk, "broker": "BRK", "date": d.isoformat()})
    real_dates = {}
    for ev in events:
        key = (ev["ticker"], ev["broker"])
        real_dates.setdefault(key, []).append(
            datetime.strptime(ev["date"], "%Y-%m-%d").date())
    return events, prices, bench, real_dates


def selftest() -> int:
    rng = random.Random(SEED)
    events, prices, bench, real_dates = _synthetic(rng)
    res = placebo_returns(events, prices, bench, real_dates, n_placebo=200)
    print("SELF-TEST (real drawn from the SAME distribution as the placebo)")
    for k, v in res.items():
        print(f"  {k}: {v}")
    print(f"\n95th percentile of the placebo distribution: {res['placebo_p95_bps']} bps")
    print(f"VERDICT: {res['verdict']}  (must be FAIL)")
    return 0 if res["verdict"] == "FAIL" else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--events")
    ap.add_argument("--prices")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.events and a.prices):
        ap.error("give --selftest, or --events and --prices")
    events = json.loads(Path(a.events).read_text(encoding="utf-8"))
    rows = Path(a.prices).read_text(encoding="utf-8").splitlines()
    hdr = rows[0].split(",")
    prices, bench = {}, {}
    for line in rows[1:]:
        parts = dict(zip(hdr, line.split(",")))
        d = datetime.strptime(parts["date"], "%Y-%m-%d").date()
        tk = parts["ticker"]
        prices.setdefault(tk, {})[d] = float(parts["close"])
        bench.setdefault(tk, {})[d] = float(parts["benchmark"])
    real_dates = {}
    for ev in events:
        real_dates.setdefault((ev["ticker"], ev["broker"]), []).append(
            datetime.strptime(ev["date"], "%Y-%m-%d").date())
    res = placebo_returns(events, prices, bench, real_dates)
    print(json.dumps(res, indent=1))
    print(f"\n95th percentile of the placebo distribution: {res['placebo_p95_bps']} bps")
    print(f"VERDICT: {res['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
