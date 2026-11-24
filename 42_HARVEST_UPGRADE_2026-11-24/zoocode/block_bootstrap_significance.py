#!/usr/bin/env python3
"""Is the 63d 'rating change beats the market' effect real, once you stop
treating overlapping windows as independent observations?

Method -- block bootstrap over TIME, resampling contiguous calendar blocks so
   * a symbol's overlapping windows stay together (they share most of their
     return path), and
   * market regimes stay intact (a block from 2020 does not get stitched to one
     from 2023 at the daily level),

  statistic(h=63) = mean excess over SPY of UP rows  -  mean excess of MAINTAIN rows

  p = share of resampled books whose statistic is <= 0   (one-sided: "is UP better?")

This is deliberately NOT a sign test: the counter controls showed the effect is
not directional (DOWN earns as much as UP), so a per-symbol sign test answers the
wrong question. This asks only whether the UP-vs-MAINTAIN gap is bigger than the
gap you would get from resampling the same market history.

Inputs are the raw dated actions on disk; prices come from yfinance.
Seed is fixed, so the p-value reproduces.
"""
from __future__ import annotations

import glob
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SEED = 20261124
N_BOOT = 1000
BLOCK_DAYS = 63          # one quarter: long enough to keep a 63d window intact
HORIZON = 63
LEDGER = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest")
OUT = Path(__file__).resolve().parent / "block_bootstrap_results.json"

BULL = {"strong buy", "buy", "outperform", "overweight", "accumulate", "positive",
        "market outperform", "sector outperform", "top pick", "add"}
BEAR = {"underperform", "underweight", "sell", "strong sell", "negative",
        "market underperform", "sector underperform", "reduce"}


def rank(g):
    g = (g or "").strip().lower()
    return 2 if g in BULL else (0 if g in BEAR else 1)


def classify(r):
    a = (r.get("action") or "").lower()
    if a == "up":
        return "UP"
    if a == "down":
        return "DOWN"
    if a == "init":
        return "INIT"
    f, t = r.get("from") or "", r.get("to") or ""
    if f and t and f != t:
        return "UP" if rank(t) > rank(f) else "DOWN"
    return "MAINTAIN"


def main() -> int:
    import yfinance as yf

    by_symbol: dict[str, list[dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok" or not rec.get("rows"):
                continue
            by_symbol.setdefault(sym, []).extend(
                r for r in rec["rows"] if r.get("date"))

    spy = yf.Ticker("SPY").history(period="10y", interval="1d", auto_adjust=True)
    if not len(spy):
        print("BLOCKED: no SPY prices")
        return 2
    spy_close = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    obs = []   # (date, cls, excess)
    for sym, rows in by_symbol.items():
        try:
            df = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=True)
        except Exception:
            continue
        if not len(df):
            continue
        idx = list(df.index)
        closes = [float(c) for c in df["Close"]]
        seen = set()
        for r in rows:
            key = (r.get("firm"), r["date"])
            if key in seen:
                continue
            seen.add(key)
            day = datetime.strptime(r["date"], "%Y-%m-%d").date()
            i = next((j for j, d in enumerate(idx) if d.date() > day), None)
            if i is None or i + HORIZON >= len(idx):
                continue
            e, x = idx[i].date(), idx[i + HORIZON].date()
            if e not in spy_close or x not in spy_close:
                continue
            stock = closes[i + HORIZON] / closes[i] - 1
            bench = spy_close[x] / spy_close[e] - 1
            obs.append((e, classify(r), stock - bench))

    print(f"observations at {HORIZON}d: {len(obs)}")
    up = np.array([o[2] for o in obs if o[1] == "UP"])
    mn = np.array([o[2] for o in obs if o[1] == "MAINTAIN"])
    print(f"UP n={len(up)} mean={100*up.mean():.3f}%  MAINTAIN n={len(mn)} mean={100*mn.mean():.3f}%")
    point = up.mean() - mn.mean()
    print(f"observed difference = {100*point:.3f}%")

    # ---- block bootstrap over calendar time -------------------------------
    dates = sorted({o[0] for o in obs})
    day_index = {d: k for k, d in enumerate(dates)}
    by_day: dict[int, list[tuple[str, float]]] = {}
    for e, c, x in obs:
        by_day.setdefault(day_index[e], []).append((c, x))
    n_days = len(dates)
    blocks = [list(range(s, min(s + BLOCK_DAYS, n_days)))
              for s in range(0, n_days, BLOCK_DAYS)]
    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(N_BOOT):
        chosen = []
        for _b in blocks:
            chosen.extend(blocks[rng.integers(len(blocks))])
        u, m = [], []
        for di in chosen:
            for c, x in by_day.get(di, ()):
                (u if c == "UP" else m if c == "MAINTAIN" else []).append(x)
        if u and m:
            diffs.append(statistics.mean(u) - statistics.mean(m))
    diffs = np.array(diffs)
    p = float((diffs <= 0).sum() + 1) / (len(diffs) + 1)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"block bootstrap ({len(diffs)} draws, block={BLOCK_DAYS}d, seed={SEED}):")
    print(f"  95% CI = [{100*lo:+.3f}%, {100*hi:+.3f}%]   one-sided p(UP<=MAINTAIN) = {p:.4f}")

    OUT.write_text(json.dumps({
        "generated": datetime.now(timezone.utc).isoformat(), "seed": SEED,
        "n_boot": len(diffs), "block_days": BLOCK_DAYS, "horizon": HORIZON,
        "n_up": int(len(up)), "n_maintain": int(len(mn)),
        "mean_up_pct": round(100 * float(up.mean()), 4),
        "mean_maintain_pct": round(100 * float(mn.mean()), 4),
        "observed_diff_pct": round(100 * float(point), 4),
        "ci95_pct": [round(100 * float(lo), 4), round(100 * float(hi), 4)],
        "p_one_sided": round(p, 5),
    }, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
