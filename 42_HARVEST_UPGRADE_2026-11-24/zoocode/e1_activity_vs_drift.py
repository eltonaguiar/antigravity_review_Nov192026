#!/usr/bin/env python3
"""E1: does analyst ACTIVITY predict, once pre-event drift is controlled for?

The one positive hint in this programme is that UP and DOWN both beat a random
entry into the same symbol -- i.e. *something happened* pays, not *which way*.
But a rating change usually follows a move, so the apparent edge may just be
momentum already in the price. This script separates the two.

MODEL (within symbol, so each symbol is its own control):
    fwd_excess = a_s + b1 * activity + b2 * pre_event_CAR + e
      activity      1 for up/down/init, 0 for main/reit   (the contrast Kilo used)
      pre_event_CAR cumulative excess over SPY from t-20 to t-1
    a_s is a symbol fixed effect, absorbed by demeaning (Frisch-Waugh-Lovell).
    Standard errors are CLUSTERED BY SYMBOL.

READING:
    b1 survives -> activity carries information beyond drift
    b1 vanishes -> we were only measuring momentum, and there is no edge

Usage: python3 e1_activity_vs_drift.py [--horizon 21] [--max-symbols N]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from datetime import datetime
from pathlib import Path

import numpy as np

LEDGER = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest")
OUT = Path(__file__).resolve().parent / "e1_activity_vs_drift.json"
PRE = 20          # pre-event window, trading days
ACTIVITY = {"up", "down", "init"}


def cluster_ols(y: np.ndarray, X: np.ndarray, groups: np.ndarray):
    """OLS with symbol fixed effects (demeaned) and cluster-robust SE by group."""
    def demean(v):
        out = np.empty_like(v, dtype=float)
        for g in np.unique(groups):
            m = groups == g
            out[m] = v[m] - v[m].mean(axis=0)
        return out
    yd = demean(y.reshape(-1, 1)).ravel()
    Xd = demean(X)
    beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    resid = yd - Xd @ beta
    # cluster-robust sandwich
    k = Xd.shape[1]
    bread = np.linalg.inv(Xd.T @ Xd)
    meat = np.zeros((k, k))
    for g in np.unique(groups):
        m = groups == g
        u = Xd[m].T @ resid[m]
        meat += np.outer(u, u)
    V = bread @ meat @ bread
    se = np.sqrt(np.diag(V))
    t = beta / se
    return beta, se, t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=21)
    ap.add_argument("--max-symbols", type=int)
    a = ap.parse_args()

    import yfinance as yf

    by_symbol: dict[str, list[dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok":
                continue
            by_symbol.setdefault(sym, []).extend(r for r in rec.get("rows") or [] if r.get("date"))
    syms = sorted(by_symbol)
    if a.max_symbols:
        syms = syms[: a.max_symbols]

    spy = yf.Ticker("SPY").history(period="10y", interval="1d", auto_adjust=True)
    spy_c = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    y, rows, groups = [], [], []
    H = a.horizon
    for sym in syms:
        try:
            df = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=True)
        except Exception:
            continue
        if not len(df):
            continue
        idx = [d.date() for d in df.index]
        close = [float(c) for c in df["Close"]]
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
            e, x = idx[i], idx[i + H]
            p0, p1 = idx[i - PRE], idx[i - 1]        # pre-event window
            if any(d not in spy_c for d in (e, x, p0, p1)):
                continue
            if min(close[i - PRE], close[i], close[i + H]) <= 0:
                continue
            fwd = (close[i + H] / close[i] - 1) - (spy_c[x] / spy_c[e] - 1)
            pre = (close[i - 1] / close[i - PRE] - 1) - (spy_c[p1] / spy_c[p0] - 1)
            act = 1.0 if (r.get("action") or "").lower() in ACTIVITY else 0.0
            if not (math.isfinite(fwd) and math.isfinite(pre)):
                continue
            y.append(fwd)
            rows.append((act, pre))
            groups.append(sym)

    y = np.array(y)
    X = np.array(rows)
    groups = np.array(groups)
    print(f"events with a full window: {len(y)}   symbols: {len(set(groups))}   horizon: {H}d")
    if len(y) < 100:
        print("insufficient")
        return 1

    # model 1: activity alone
    b1, s1, t1 = cluster_ols(y, X[:, [0]], groups)
    # model 2: activity + pre-event CAR
    b2, s2, t2 = cluster_ols(y, X, groups)

    print(f"\n{'model':<28}{'b_activity':>12}{'se':>9}{'t':>7}")
    print(f"{'activity only':<28}{100*b1[0]:>11.4f}%{100*s1[0]:>8.4f}{t1[0]:>7.2f}")
    print(f"{'activity + pre-CAR':<28}{100*b2[0]:>11.4f}%{100*s2[0]:>8.4f}{t2[0]:>7.2f}")
    print(f"{'  b_preCAR':<28}{100*b2[1]:>11.4f}%{100*s2[1]:>8.4f}{t2[1]:>7.2f}")

    verdict = ("activity SURVIVES the drift control" if abs(t2[0]) > 1.96
               else "activity does NOT survive -- it was momentum")
    print(f"\nVERDICT: {verdict}")
    OUT.write_text(json.dumps({
        "horizon_days": H, "n_events": int(len(y)), "n_symbols": int(len(set(groups))),
        "pre_window_days": PRE,
        "activity_only": {"beta_pct": round(100 * float(b1[0]), 4),
                          "se_pct": round(100 * float(s1[0]), 4), "t": round(float(t1[0]), 3)},
        "activity_plus_precar": {
            "beta_activity_pct": round(100 * float(b2[0]), 4),
            "se_activity_pct": round(100 * float(s2[0]), 4),
            "t_activity": round(float(t2[0]), 3),
            "beta_precar_pct": round(100 * float(b2[1]), 4),
            "t_precar": round(float(t2[1]), 3)},
        "verdict": verdict,
    }, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
