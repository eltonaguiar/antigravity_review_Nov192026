#!/usr/bin/env python3
"""Backtest HARVEST monthly consensus + direction against forward excess returns.

Signal is known at the period date (month start); entry is the next trading close.
Exits at +21 and +63 calendar days. Excess vs SPY, minus 6.7122bp round trip.
Data: Finnhub recommendation history (4 monthly periods, 71 US large caps) +
Yahoo daily charts. Overlapping, survivorship-biased, small n — labelled.
"""
import json, math, random, statistics, sys, time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R
from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "evidence" / "finnhub_recommendation_raw.jsonl"
OUT = ROOT / "docs" / "data" / "harvest_backtest.json"
MD = Path(__file__).resolve().parent / "HARVEST_BACKTEST.md"
COST_BPS = 6.7122

def chart(sym):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2y&interval=1d"
    r = requests.get(u, impersonate="chrome", timeout=30)
    d = r.json()["chart"]["result"][0]
    return [(datetime.fromtimestamp(a, timezone.utc).date(), b)
            for a, b in zip(d["timestamp"], d["indicators"]["adjclose"][0]["adjclose"]) if b]

def price_strictly_after(px, d):
    for day, p in px:
        if day > d: return day, p
    return None, None


def price_on_or_after(px, d):
    for day, p in px:
        if day >= d: return day, p
    return None, None

def price_on_or_before(px, d):
    last = None
    for day, p in px:
        if day <= d: last = (day, p)
        else: break
    return last if last else (None, None)

def excess(px, spy, start, days):
    """Entry at the first close STRICTLY after the signal date (no same-bar)."""
    e_day, e_px = price_strictly_after(px, start)
    if not e_day: return None
    x_day, x_px = price_on_or_after(px, e_day + timedelta(days=days))
    se_day, se_px = price_on_or_after(spy, e_day)
    sx_day, sx_px = price_on_or_after(spy, x_day) if x_day else (None, None)
    if not all([e_px, x_px, se_px, sx_px]): return None
    ret = (x_px/e_px - 1) * 100
    bret = (sx_px/se_px - 1) * 100
    return ret - bret - COST_BPS/100

def boot(vals, iters=3000, seed=5):
    if len(vals) < 3: return (None, None, None)
    rnd = random.Random(seed); n = len(vals); m = []
    for _ in range(iters):
        m.append(sum(vals[rnd.randrange(n)] for _ in range(n))/n)
    m.sort(); return statistics.mean(vals), m[int(0.025*iters)], m[int(0.975*iters)]

def stats(pairs):
    """pairs = [(value, cluster)]. Cluster bootstrap by symbol to respect
    repeated/overlapping observations."""
    if not pairs: return {"n": 0}
    vals = [v for v, _ in pairs]
    groups = defaultdict(list)
    for v, c in pairs: groups[c].append(v)
    keys = list(groups)
    rnd = random.Random(5); means = []
    if len(keys) < 2:
        n = len(vals)
        for _ in range(3000):
            means.append(sum(vals[rnd.randrange(n)] for _ in range(n))/n)
    else:
        for _ in range(3000):
            flat = []
            for _ in range(len(keys)):
                flat.extend(groups[keys[rnd.randrange(len(keys))]])
            means.append(sum(flat)/len(flat))
    means.sort(); m = statistics.mean(vals)
    lo = means[int(0.025*len(means))]; hi = means[int(0.975*len(means))]
    p_one = sum(1 for x in means if x <= 0)/len(means)
    return {"n": len(vals), "clusters": len(keys), "mean_pct": m, "ci95_pct": [lo, hi],
            "median_pct": statistics.median(vals),
            "hit_rate": sum(1 for v in vals if v > 0)/len(vals),
            "p_one_sided": p_one,
            "ci_low_gt_0": bool(lo > 0)}

def bh(pvals):
    m = len(pvals); order = sorted(range(m), key=lambda i: pvals[i]); q = [0.0]*m; prev = 1.0
    for rank in range(m-1, -1, -1):
        i = order[rank]; val = min(prev, pvals[i]*m/(rank+1)); q[i] = val; prev = val
    return q


def main():
    rows = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    symbols = [r["symbol"] for r in rows]
    px = {}
    for i, s in enumerate(symbols + ["SPY"]):
        try:
            px[s] = chart(s)
        except Exception as e:
            print("chart fail", s, e)
        time.sleep(0.7)
    spy = px.get("SPY", [])
    by_label = defaultdict(lambda: defaultdict(list))
    by_dir = defaultdict(lambda: defaultdict(list))
    basket = defaultdict(list)
    for rec in rows:
        sym = rec["symbol"]
        if sym not in px: continue
        hist = sorted(rec["rows"], key=lambda x: x["period"])
        for i, per in enumerate(hist):
            counts = {"strong_buy": per["strongBuy"], "buy": per["buy"], "hold": per["hold"],
                      "sell": per["sell"], "strong_sell": per["strongSell"]}
            label = R.label_for_counts(**counts)
            start = date.fromisoformat(per["period"])
            e21 = excess(px[sym], spy, start, 21)
            e63 = excess(px[sym], spy, start, 63)
            if e21 is not None: by_label[label]["21d"].append((e21, sym))
            if e63 is not None: by_label[label]["63d"].append((e63, sym))
            if i > 0:
                prev = hist[i-1]
                pc = {"strong_buy": prev["strongBuy"], "buy": prev["buy"], "hold": prev["hold"],
                      "sell": prev["sell"], "strong_sell": prev["strongSell"]}
                delta = 100*(R.buy_side_of(**counts)-R.buy_side_of(**pc))
                direction = R.direction_for(delta, R.counts_total(**counts), R.bucket_moves(pc, counts))
                if e21 is not None: by_dir[direction]["21d"].append((e21, sym))
                if e63 is not None: by_dir[direction]["63d"].append((e63, sym))
            if label == "STRONG_BUY" and e21 is not None:
                basket[per["period"]].append(e21)
    for h in ("21d","63d"):
        keys = [k for k in by_label if (by_label[k].get(h) or [])]
        ps = [stats(by_label[k][h])["p_one_sided"] for k in keys]
        qs = bh(ps)
        for k, q in zip(keys, qs):
            by_label[k].setdefault("q", {})[h] = q
    out = {"schema": "harvest_backtest/1", "synthetic": False,
           "cost_bps": COST_BPS, "benchmark": "SPY", "entry": "next trading close",
           "periods": sorted({r["rows"][0]["period"] for r in rows if r["rows"]}),
           "by_label": {k: {h: stats(d[h]) for h in ("21d","63d") if h in d} for k, d in by_label.items()},
           "by_direction": {k: {h: stats(d[h]) for h in ("21d","63d") if h in d} for k, d in by_dir.items()},
           "strong_buy_basket": {p: {"n": len(v), "mean_excess_pct": statistics.mean(v),
                                     "hit_rate": sum(1 for x in v if x>0)/len(v)}
                                 for p, v in sorted(basket.items())},
           "caveats": ["71 US large caps; 4 monthly periods; overlapping windows",
                       "survivorship (no delisted names); sell-side structurally bullish",
                       "small n; no multiple-testing correction"]}
    OUT.write_text(json.dumps(out, indent=2)+"\n")
    L = ["# HARVEST backtest (consensus + direction -> forward excess vs SPY)", "",
         "Entry next trading close after the period date; cost 6.7122bp; exits 21/63d.", ""]
    for h in ("21d","63d"):
        L.append(f"## Label -> forward excess ({h})")
        L.append("| Label | n | mean % | 95% CI | median % | hit | p(≤0) | BH q | CI-low>0 |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for lab, d in sorted(by_label.items()):
            s = stats(d.get(h) or [])
            if not s.get("n") or s.get("mean_pct") is None: continue
            L.append(f"| {lab} | {s['n']} | {s['mean_pct']:+.3f} | [{s['ci95_pct'][0]:+.3f},{s['ci95_pct'][1]:+.3f}] | {s['median_pct']:+.3f} | {s['hit_rate']:.0%} | {s.get('p_one_sided',0):.3f} | {d.get('q',{}).get(h,1):.3f} | {s['ci_low_gt_0']} |")
        L.append("")
    L.append("## Strong-buy basket by period (21d excess)")
    for p, s in sorted(basket.items()):
        L.append(f"- {p}: n={len(s)}, mean {statistics.mean(s):+.3f}%, hit {sum(1 for x in s if x>0)/len(s):.0%}")
    L.append("")
    L.append("Caveats: overlapping windows, survivorship, sell-side bullish bias, small n.")
    MD.write_text("\n".join(L)+"\n")
    print("wrote", OUT, "and", MD)

if __name__ == "__main__":
    main()
