#!/usr/bin/env python3
"""Backtest the analyst-action signal against what the market did afterwards.

Question: when a firm upgrades a stock, does the stock beat the benchmark over
the next N days? If yes, the HARVEST data is worth tracking and trading. If not,
it is a descriptive page and should be labelled as one.

Inputs (all already on disk -- no refetch):
  /home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest/*.json
      full Yahoo upgradeDowngradeHistory per symbol (date, firm, from, to, action, pt)
Outputs:
  backtest_results.json   per-horizon stats overall and by action class
  (stdout)                the table printed in my reply

Method -- stated so it can be attacked:
  * entry  = close on the FIRST trading day AFTER the action date (never the
             action day itself; the note is published before the move is known)
  * exit   = close N trading days after entry, N in HORIZONS
  * return = exit/entry - 1, and EXCESS = stock return - benchmark return over
             the SAME entry/exit dates (window is identical by construction)
  * benchmark = SPY (the class benchmark for US equity)
  * an action whose window has no complete price data is dropped and COUNTED,
    never filled with a zero
  * dedupe: one action per (symbol, firm, date) -- Yahoo repeats revisions
  * significance: one-sample t-test on excess returns within each action class,
    plus a bootstrap 95% CI (fixed seed) because upgrade returns are fat-tailed

The honest null: analysts are structurally bullish, so 'upgrades beat the
market' is only interesting if the UPGRADE group beats the DOWNGRADE group and
both beat a random-entry control of the same symbols and dates.

Usage:
  python3 backtest_analyst_actions.py [--max-symbols 30] [--horizons 5,21,63]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

MAIN_REPO = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca")
LEDGER_DIR = MAIN_REPO / "ZOOCODE" / "harvest"
OUT = Path(__file__).resolve().parent / "backtest_results.json"
SEED = 20261124
N_BOOT = 2000


def load_actions(max_symbols: int | None) -> dict[str, list[dict]]:
    by_symbol: dict[str, list[dict]] = {}
    for path in sorted(LEDGER_DIR.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok" or not rec.get("rows"):
                continue
            rows = by_symbol.setdefault(sym, [])
            for r in rec["rows"]:
                if r.get("date") and (r.get("action") or r.get("from") or r.get("to")):
                    rows.append(r)
    if max_symbols:
        by_symbol = dict(sorted(by_symbol.items())[:max_symbols])
    return by_symbol


def dedupe(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in sorted(rows, key=lambda x: x["date"], reverse=True):
        key = (r.get("firm"), r["date"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def classify(r: dict) -> str:
    a = (r.get("action") or "").lower()
    frm, to = (r.get("from") or ""), (r.get("to") or "")
    if a == "up":
        return "UP"
    if a == "down":
        return "DOWN"
    if a == "init":
        return "INIT"
    if frm and to and frm != to:
        return "UP" if _better(to, frm) else "DOWN"
    return "MAINTAIN"


_BULL = {"strong buy", "buy", "outperform", "overweight", "accumulate", "positive",
         "market outperform", "sector outperform", "top pick", "add"}
_BEAR = {"underperform", "underweight", "sell", "strong sell", "negative",
         "market underperform", "sector underperform", "reduce"}


def _rank(grade: str) -> int:
    g = (grade or "").strip().lower()
    if g in _BULL:
        return 2
    if g in _BEAR:
        return 0
    return 1


def _better(a: str, b: str) -> bool:
    return _rank(a) > _rank(b)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-symbols", type=int)
    ap.add_argument("--horizons", default="5,21,63")
    a = ap.parse_args(argv)
    horizons = [int(h) for h in a.horizons.split(",")]

    import pandas as pd
    import yfinance as yf

    by_symbol = load_actions(a.max_symbols)
    symbols = list(by_symbol)
    print(f"symbols with actions on disk: {len(symbols)}", file=sys.stderr)

    # one download for the benchmark, one per symbol
    def prices(sym: str):
        try:
            df = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=True)
            return df if len(df) else None
        except Exception:
            return None

    spy = prices("SPY")
    if spy is None:
        print("BLOCKED: no SPY prices", file=sys.stderr)
        return 2
    spy_idx = list(spy.index)

    def forward(sym_df, day, n: int):
        idx = list(sym_df.index)
        try:
            i = next(j for j, d in enumerate(idx) if d.date() > day)
        except StopIteration:
            return None
        j = i + n
        if j >= len(idx):
            return None
        entry_date, exit_date = idx[i], idx[j]
        try:
            si = next(k for k, d in enumerate(spy_idx) if d.date() == entry_date.date())
            sj = next(k for k, d in enumerate(spy_idx) if d.date() == exit_date.date())
        except StopIteration:
            return None
        stock = float(sym_df["Close"].iloc[j]) / float(sym_df["Close"].iloc[i]) - 1
        bench = float(spy["Close"].iloc[sj]) / float(spy["Close"].iloc[si]) - 1
        return stock, bench

    obs: dict[int, dict[str, list[float]]] = {h: defaultdict(list) for h in horizons}
    # per-symbol means, so UP can be compared against the SAME symbol's MAINTAIN
    # baseline -- the pooled comparison is confounded because MAINTAIN has ~10x
    # the rows and differs in composition (quiet days vs event days)
    per_sym: dict[int, dict[str, dict[str, list[float]]]] = {h: defaultdict(lambda: defaultdict(list)) for h in horizons}
    # random-entry control: same symbol, same horizon, random date -> what does
    # an arbitrary entry earn? If UP does not beat this, the signal is the symbol.
    rand_ctrl: dict[int, list[float]] = {h: [] for h in horizons}
    rng = random.Random(SEED)
    dropped = defaultdict(int)
    per_symbol_used = 0
    # TWO-LEG COST. A round trip is a single 26 bp charge per leg. Comparing a
    # long (UP) with a long (MAINTAIN or random) cancels the cost, but comparing
    # UP with DOWN, or a long with cash, does not: the second leg is another
    # position and pays its own round turn. Every difference below is therefore
    # reported NET, subtracting 26 bp per extra leg it involves.
    LEG_BPS = 26.0
    for sym in symbols:
        df = prices(sym)
        if df is None:
            dropped[f"{sym}:no_price"] += len(by_symbol[sym])
            continue
        per_symbol_used += 1
        days_all = [d.date() for d in df.index]
        for r in dedupe(by_symbol[sym]):
            day = datetime.strptime(r["date"], "%Y-%m-%d").date()
            cls = classify(r)
            for h in horizons:
                fwd = forward(df, day, h)
                if fwd is None:
                    dropped[f"h{h}"] += 1
                    continue
                stock, bench = fwd
                ex = stock - bench
                obs[h][cls].append(ex)
                per_sym[h][sym][cls].append(ex)
                if cls in ("UP", "DOWN"):
                    rday = days_all[rng.randrange(len(days_all))]
                    rf = forward(df, rday, h)
                    if rf is not None:
                        rand_ctrl[h].append(rf[0] - rf[1])

    random.seed(SEED)

    def boot_ci(xs: list[float], n: int = N_BOOT):
        if len(xs) < 3:
            return (None, None)
        means = []
        for _ in range(n):
            means.append(statistics.mean(random.choices(xs, k=len(xs))))
        means.sort()
        return (means[int(0.025 * n)], means[int(0.975 * n)])

    def t_stat(xs):
        if len(xs) < 3:
            return None, None
        m, sd = statistics.mean(xs), statistics.stdev(xs)
        if sd == 0:
            return None, None
        return m / (sd / math.sqrt(len(xs))), m

    out = {"generated": datetime.now(timezone.utc).isoformat(), "seed": SEED,
           "benchmark": "SPY", "symbols_used": per_symbol_used,
           "dropped": dict(dropped), "horizons": {}}

    # POOLED LEVELS ARE SURVIVORSHIP-CONTAMINATED, so they are computed but not
    # published as findings. The universe is today's ticker list applied to
    # 2012-2026, so delisted/acquired/bankrupt names are absent and every class
    # inherits positive drift -- which is why UP and DOWN can both "beat SPY".
    print(f"\n{'h':>4} {'class':<9}{'n_raw':>7}{'n_sym':>6}{'mean excess %':>15}"
          f"{'t_raw':>8}{'t_cluster':>11}{'design':>8}")
    for h in horizons:
        out["horizons"][h] = {}
        for cls in ("UP", "DOWN", "INIT", "MAINTAIN"):
            xs = obs[h][cls]
            if not xs:
                continue
            t, m = t_stat(xs)
            # one mean per symbol, then a t-test over SYMBOLS: this is the
            # cluster-robust version. Windows inside a symbol overlap, so the
            # raw n massively overstates the information.
            per_symbol = []
            for byc in per_sym[h].values():
                vals = byc.get(cls)
                if vals:
                    per_symbol.append(statistics.mean(vals))
            t_c, m_c = t_stat(per_symbol) if len(per_symbol) >= 3 else (None, None)
            design = (t / t_c) ** 2 if (t and t_c) else None
            verdict = "n_sym<30 -- no verdict" if len(per_symbol) < 30 else (
                "SIGNIFICANT" if t_c is not None and abs(t_c) > 1.96 else "not significant")
            out["horizons"][h][cls] = {
                "n_raw": len(xs), "n_symbols": len(per_symbol),
                "mean_excess_pct": round(100 * m, 4) if m is not None else None,
                "t_raw": round(t, 3) if t is not None else None,
                "t_cluster": round(t_c, 3) if t_c is not None else None,
                "design_effect": round(design, 2) if design else None,
                "verdict_cluster": verdict,
                "PUBLISHABLE": False,
                "why_not": "survivorship-contaminated levels; use within-symbol controls",
            }
            print(f"{h:>4} {cls:<9}{len(xs):>7}{len(per_symbol):>6}{100*m:>15.3f}"
                  f"{(t or 0):>8.2f}{(t_c or 0):>11.2f}{(design or 0):>8.1f}x")
    # ---- control 2: within-symbol comparisons, the survivorship-immune claim ---
    # Two contrasts, both paired inside a symbol so the universe's survivorship
    # bias cancels:  UP - DOWN (both positions, 2 legs of cost) and
    #                UP - MAINTAIN (both longs, cost cancels; kept for continuity).
    from math import comb

    def sign_test(diffs):
        pos = sum(1 for x in diffs if x > 0)
        n = len(diffs)
        k = min(pos, n - pos)
        return pos, n, min(1.0, 2 * sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n))

    def cluster_ci(diffs):
        """Bootstrap CI resampling SYMBOLS (already one value per symbol)."""
        if len(diffs) < 3:
            return (None, None)
        means = []
        for _ in range(N_BOOT):
            means.append(statistics.mean(rng.choices(diffs, k=len(diffs))))
        means.sort()
        return (means[int(0.025 * N_BOOT)], means[int(0.975 * N_BOOT)])

    print(f"\n{'h':>4} {'contrast':<12}{'sym':>5}{'mean %':>9}{'net %':>9}{'95% CI (by symbol)':>26}{'pos':>6}{'sign p':>9}")
    for h in horizons:
        for name, want_extra_legs in (("UP-DOWN", True), ("UP-MAINTAIN", False)):
            diffs = []
            for sym, byc in per_sym[h].items():
                a = byc.get("UP")
                b = byc.get("DOWN" if want_extra_legs else "MAINTAIN")
                if a and b and len(a) >= 5 and len(b) >= 5:
                    diffs.append(statistics.mean(a) - statistics.mean(b))
            if not diffs:
                continue
            raw = statistics.mean(diffs)
            net = raw - (LEG_BPS / 10000.0 if want_extra_legs else 0.0)
            pos, n, p = sign_test(diffs)
            lo, hi = cluster_ci(diffs)
            ci = f"[{100*lo:+.3f}, {100*hi:+.3f}]" if lo is not None else "--"
            out.setdefault("within_symbol_control", {}).setdefault(h, {})[name] = {
                "n_symbols": n, "mean_raw_pct": round(100 * raw, 4),
                "mean_net_pct": round(100 * net, 4),
                "ci95_by_symbol_pct": [round(100 * lo, 4) if lo is not None else None,
                                       round(100 * hi, 4) if hi is not None else None],
                "positive": pos, "sign_test_p": round(p, 5), "extra_cost_bps": LEG_BPS if want_extra_legs else 0,
            }
            print(f"{h:>4} {name:<12}{n:>5}{100*raw:>9.3f}{100*net:>9.3f}{ci:>26}{pos:>6}{p:>9.5f}")

    # ---- control 3: random entry on the same symbols -------------------------
    print(f"\n{'h':>4} {'UP %':>9}{'random %':>10}{'edge over random':>18}")
    for h in horizons:
        up = obs[h]["UP"]
        rc = rand_ctrl[h]
        if not up or not rc:
            continue
        mu, mr = statistics.mean(up), statistics.mean(rc)
        out.setdefault("random_entry_control", {})[h] = {
            "mean_up_pct": round(100 * mu, 4), "mean_random_pct": round(100 * mr, 4),
            "edge_pct": round(100 * (mu - mr), 4), "n_random": len(rc),
        }
        print(f"{h:>4} {100*mu:>9.3f}{100*mr:>10.3f}{100*(mu-mr):>18.3f}")

    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
