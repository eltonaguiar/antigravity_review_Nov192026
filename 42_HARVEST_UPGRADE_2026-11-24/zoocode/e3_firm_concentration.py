#!/usr/bin/env python3
"""E3: does the ACTIVITY effect concentrate in particular firms?

E1/E2 established that a rating change predicts ~+0.88-0.96% at 63d, clustered,
drift-controlled, and not the earnings effect. The question now is whether that
is carried by a few firms (an exploitable pattern: follow those firms) or is
diffuse across all of them (a market-wide drift: not exploitable).

DESIGN -- out-of-window by construction:
  1. Split events by date into an EARLY half and a LATE half.
  2. Rank firms on the EARLY half only, requiring n >= MIN_N in that half.
  3. Evaluate the top-decile firms on the LATE half, where they were NOT chosen.
  4. Null: draw random firm sets of the same size from the LATE half, 2000 times,
     and ask how often a random set does as well.
  A real concentration means the early winners beat both the late average and
  the random-set null. A null means the early ranking does not carry forward,
  which is what a diffuse effect looks like.

The excess return is vs SPY over the same dates, net of 26 bp (equity round turn).

Usage: python3 e3_firm_concentration.py [--horizon 63]
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from datetime import datetime
from pathlib import Path

import numpy as np

import e1_activity_vs_drift as e1
from e1_activity_vs_drift import LEDGER, PRE

OUT = Path(__file__).resolve().parent / "e3_firm_concentration.json"
MIN_N = 30
SEED = 20261124
N_NULL = 2000
COST = 0.0026


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=63)
    a = ap.parse_args()
    import yfinance as yf

    by_symbol: dict[str, list[dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok":
                continue
            by_symbol.setdefault(sym, []).extend(r for r in rec.get("rows") or [] if r.get("date"))

    spy = yf.Ticker("SPY").history(period="10y", interval="1d", auto_adjust=True)
    spy_c = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    # one record per ACTIVITY event: (date, symbol, firm, excess)
    recs = []
    H = a.horizon
    for sym, rows in by_symbol.items():
        try:
            df = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=True)
        except Exception:
            continue
        if not len(df):
            continue
        idx = [d.date() for d in df.index]
        close = [float(c) for c in df["Close"]]
        seen = set()
        for r in sorted(rows, key=lambda x: x["date"]):
            if (r.get("action") or "").lower() not in ("up", "down", "init"):
                continue
            key = (r.get("firm"), r["date"])
            if key in seen:
                continue
            seen.add(key)
            day = datetime.strptime(r["date"], "%Y-%m-%d").date()
            i = next((j for j, d in enumerate(idx) if d > day), None)
            if i is None or i + H >= len(idx):
                continue
            e, x = idx[i], idx[i + H]
            if e not in spy_c or x not in spy_c or close[i] <= 0:
                continue
            ex = (close[i + H] / close[i] - 1) - (spy_c[x] / spy_c[e] - 1) - COST
            if math.isfinite(ex):
                recs.append((e, r.get("firm") or "?", ex))

    print(f"activity events with a full {H}d window: {len(recs)}  firms: {len({r[1] for r in recs})}")
    if len(recs) < 200:
        print("insufficient")
        return 1

    cut = sorted(r[0] for r in recs)[len(recs) // 2]
    early = [r for r in recs if r[0] < cut]
    late = [r for r in recs if r[0] >= cut]

    def by_firm(rs):
        d = {}
        for _, f, ex in rs:
            d.setdefault(f, []).append(ex)
        return {f: (len(v), statistics.mean(v)) for f, v in d.items()}

    fe, fl = by_firm(early), by_firm(late)
    eligible = [f for f in fe if fe[f][0] >= MIN_N and f in fl and fl[f][0] >= MIN_N]
    print(f"firms eligible (n>={MIN_N} in BOTH halves): {len(eligible)}")
    if len(eligible) < 10:
        print("insufficient firms for a ranking")
        return 1

    ranked = sorted(eligible, key=lambda f: -fe[f][1])
    k = max(1, len(ranked) // 10)
    top = ranked[:k]
    top_late = [fl[f][1] for f in top]
    all_late = [fl[f][1] for f in eligible]
    rng = random.Random(SEED)
    null_means = []
    for _ in range(N_NULL):
        pick = rng.sample(eligible, k)
        null_means.append(statistics.mean(fl[f][1] for f in pick))
    obs = statistics.mean(top_late)
    p = (sum(1 for x in null_means if x >= obs) + 1) / (N_NULL + 1)
    print(f"\ntop-decile firms by EARLY mean (k={k}): {top}")
    print(f"{'':<34}{'mean excess late':>18}")
    print(f"{'top decile (chosen on early)':<34}{100*obs:>17.3f}%")
    print(f"{'all eligible firms':<34}{100*statistics.mean(all_late):>17.3f}%")
    print(f"{'random-set null mean':<34}{100*statistics.mean(null_means):>17.3f}%")
    print(f"\npermutation p (random set >= top decile) = {p:.4f}")
    verdict = ("CONCENTRATED -- early ranking carries forward" if p < 0.05
               else "DIFFUSE -- the early ranking does not carry forward")
    print(f"VERDICT: {verdict}")

    OUT.write_text(json.dumps({
        "horizon_days": H, "n_events": len(recs), "split_date": str(cut),
        "n_early": len(early), "n_late": len(late),
        "firms_eligible": len(eligible), "k_top": k, "top_firms": top,
        "mean_excess_late_top_pct": round(100 * obs, 4),
        "mean_excess_late_all_pct": round(100 * statistics.mean(all_late), 4),
        "null_mean_pct": round(100 * statistics.mean(null_means), 4),
        "permutation_p": round(p, 5), "verdict": verdict,
        "cost_bps": COST * 10000,
    }, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
