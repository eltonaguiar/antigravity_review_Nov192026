#!/usr/bin/env python3
"""E2: is the ACTIVITY effect just earnings clustering?

E1 showed that any rating change (up/down/init) predicts +0.28% at 21d and
+0.88% at 63d, clustered and drift-controlled. But analysts publish around
earnings, and earnings drive returns -- so the whole effect could be the
well-known earnings drift, which is not an edge we can act on.

DESIGN
  Same windows as E1. Each event is tagged:
      near_earnings = 1 if an earnings date of that symbol falls within
                      +/- 5 trading days of the event's entry day
  Then activity is split into two dummies:
      act_near   (activity AND near earnings)
      act_far    (activity AND NOT near earnings)
  Both are regressed on forward excess with the pre-event CAR control and
  symbol fixed effects, SEs clustered by symbol.

READING
  act_far survives        -> activity carries something beyond earnings
  act_far collapses       -> the effect WAS earnings, and E1 is closed as a
                             known effect rather than an edge

Also reported: the share of rating changes that fall near earnings, which is
the descriptive version of the same question.

Usage: python3 e2_activity_vs_earnings.py [--horizon 21] [--max-symbols N]
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import e1_activity_vs_drift as e1   # reuse the loader and the clustered OLS

OUT = Path(__file__).resolve().parent / "e2_activity_vs_earnings.json"
ACTIVITY = {"up", "down", "init"}
NEAR_DAYS = 5


def earnings_dates(ticker) -> list:
    try:
        ed = ticker.get_earnings_dates(limit=60)
    except Exception:
        return []
    if ed is None or not len(ed):
        return []
    out = []
    for ts in ed.index:
        try:
            out.append(ts.date())
        except Exception:
            pass
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--max-symbols", type=int)
    a = ap.parse_args()

    import yfinance as yf
    from e1_activity_vs_drift import LEDGER, PRE

    by_symbol: dict[str, list[dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok":
                continue
            by_symbol.setdefault(sym, []).extend(
                r for r in rec.get("rows") or [] if r.get("date"))
    syms = sorted(by_symbol)
    if a.max_symbols:
        syms = syms[: a.max_symbols]

    spy = yf.Ticker("SPY").history(period="10y", interval="1d", auto_adjust=True)
    spy_c = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    y, X, groups = [], [], []
    n_act = n_near = 0
    H = a.horizon
    for sym in syms:
        try:
            tk = yf.Ticker(sym)
            df = tk.history(period="10y", interval="1d", auto_adjust=True)
        except Exception:
            continue
        if not len(df):
            continue
        idx = [d.date() for d in df.index]
        close = [float(c) for c in df["Close"]]
        edates = earnings_dates(tk)
        seen = set()
        for r in sorted(by_symbol[sym], key=lambda x: x["date"]):
            key = (r.get("firm"), r["date"])
            if key in seen:
                continue
            seen.add(key)
            day = datetime.strptime(r["date"], "%Y-%m-%d").date()
            i = next((j for j, d in enumerate(idx) if d > day), None)
            if i is None or i - PRE < 0 or i + H >= len(idx):
                continue
            e, x, p0, p1 = idx[i], idx[i + H], idx[i - PRE], idx[i - 1]
            if any(d not in spy_c for d in (e, x, p0, p1)):
                continue
            if min(close[i - PRE], close[i], close[i + H]) <= 0:
                continue
            fwd = (close[i + H] / close[i] - 1) - (spy_c[x] / spy_c[e] - 1)
            pre = (close[i - 1] / close[i - PRE] - 1) - (spy_c[p1] / spy_c[p0] - 1)
            if not (math.isfinite(fwd) and math.isfinite(pre)):
                continue
            act = 1.0 if (r.get("action") or "").lower() in ACTIVITY else 0.0
            near = 0.0
            if act and edates:
                # calendar-day distance, ~5 trading days = 7 calendar days
                if min(abs((ed - e).days) for ed in edates) <= NEAR_DAYS * 1.4:
                    near = 1.0
            if act:
                n_act += 1
                n_near += int(near)
            y.append(fwd)
            X.append((act * near, act * (1 - near), pre))
            groups.append(sym)

    y = np.array(y); X = np.array(X); groups = np.array(groups)
    print(f"events: {len(y)}   symbols: {len(set(groups))}   horizon: {H}d")
    print(f"activity events: {n_act}   near earnings (+/-~5 td): {n_near} "
          f"({100*n_near/n_act if n_act else 0:.1f}%)")
    if len(y) < 100:
        print("insufficient")
        return 1
    beta, se, t = e1.cluster_ols(y, X, groups)
    print(f"\n{'term':<24}{'beta':>12}{'se':>10}{'t':>7}")
    for name, b, s, tt in (("activity * near earnings", beta[0], se[0], t[0]),
                          ("activity * NOT near earnings", beta[1], se[1], t[1]),
                          ("pre-event CAR", beta[2], se[2], t[2])):
        print(f"{name:<24}{100*b:>11.4f}%{100*s:>9.4f}{tt:>7.2f}")
    survived = abs(t[1]) > 1.96
    verdict = ("activity SURVIVES outside earnings" if survived
               else "activity collapses outside earnings -- it WAS the earnings effect")
    print(f"\nVERDICT: {verdict}")
    OUT.write_text(json.dumps({
        "horizon_days": H, "n_events": int(len(y)), "n_symbols": int(len(set(groups))),
        "n_activity": n_act, "n_near_earnings": n_near,
        "share_near_pct": round(100 * n_near / n_act, 2) if n_act else None,
        "act_near": {"beta_pct": round(100 * float(beta[0]), 4), "t": round(float(t[0]), 3)},
        "act_far": {"beta_pct": round(100 * float(beta[1]), 4), "t": round(float(t[1]), 3)},
        "precar": {"beta_pct": round(100 * float(beta[2]), 4), "t": round(float(t[2]), 3)},
        "verdict": verdict,
    }, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
