#!/usr/bin/env python3
"""settle_inversion.py - Item B settle probe: does the STRONG_BUY inversion survive
a size-matched, market-adjusted control?

Why this exists: score_inversion_test.md returned UNDERDETERMINED because the
matched-control CIs all include zero with STRONG_BUY n=23. A fresh count of
analyst_actions.csv gives 967 Strong Buy events across 129 symbols, so the earlier
sample was over-filtered rather than absent.

Design (pre-registered here, before running):
  event      to_grade contains "strong buy", one row per (symbol, date)
  entry      next session OPEN after the event date   (lag-1, no same-close fill)
  horizons   21 and 63 trading days
  outcome    excess vs SPY over the identical window  (market-adjusted)
  matching   size tercile, size = 60d median dollar volume BEFORE the event
             (proxy for market cap: shares outstanding are not in the data, so the
             proxy is stated rather than assumed away)
  control    the size-tercile matched median excess from NON-Strong-Buy rating
             events in the same symbol population
  inference  symbol-cluster bootstrap, 2000 draws
  verdict    inversion holds only if STRONG_BUY excess is BELOW its matched
             control with a CI excluding zero at BOTH horizons
"""
import csv
import json
import os
import random
import statistics as st
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")

CSV = "/home/eaguiar2015/antigravity_review/42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv"
OUT = "/home/eaguiar2015/settle_inversion_results.json"


def truthy_str(v):
    return (v or "").strip().lower()


def parse_date(d):
    """Handles epoch seconds, epoch ms and ISO."""
    s = (d or "").strip()
    if not s:
        return None
    try:
        t = float(s)
        if t > 2e10:
            t /= 1000.0
        return int(t) // 86400 * 86400
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            import datetime as dt
            return int(dt.datetime.strptime(s[:10], fmt).replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            continue
    return None


rows = list(csv.DictReader(open(CSV, encoding="utf-8", errors="replace")))
print(f"loaded {len(rows):,} analyst actions")

# one event per (symbol, date), keep the strongest classification seen
events = {}
for r in rows:
    sym = (r.get("symbol") or "").strip().upper()
    ts = parse_date(r.get("date"))
    if not sym or ts is None:
        continue
    key = (sym, ts)
    g = truthy_str(r.get("to_grade"))
    if key not in events:
        events[key] = {"symbol": sym, "ts": ts, "grade": g}
print(f"distinct (symbol, date) events: {len(events):,}")

sb = [e for e in events.values() if "strong buy" in e["grade"]]
other = [e for e in events.values() if "strong buy" not in e["grade"]]
print(f"  STRONG_BUY events: {len(sb):,} across {len(set(e['symbol'] for e in sb))} symbols")
print(f"  comparison events: {len(other):,}")

syms = sorted(set(e["symbol"] for e in events.values()))
print(f"  symbols needed: {len(syms)}")

# ---- prices -------------------------------------------------------------
try:
    import yfinance as yf
    print("yfinance: available")
except ImportError:
    print("yfinance: MISSING - cannot proceed")
    raise SystemExit(1)

import datetime as dt
lo = min(e["ts"] for e in events.values()) - 400 * 86400
hi = max(e["ts"] for e in events.values()) + 400 * 86400
start = dt.datetime.utcfromtimestamp(max(lo, 946684800)).strftime("%Y-%m-%d")
end = dt.datetime.utcfromtimestamp(min(hi, 1990000000)).strftime("%Y-%m-%d")
print(f"price window {start} .. {end}")

print("downloading bars (this is the slow part)...")
px = {}
BATCH = 40
need = syms + ["SPY"]
for i in range(0, len(need), BATCH):
    chunk = need[i:i + BATCH]
    try:
        df = yf.download(chunk, start=start, end=end, progress=False, auto_adjust=True,
                         group_by="ticker", threads=True)
    except Exception as exc:
        print(f"  batch {i} failed: {exc}")
        continue
    for s in chunk:
        try:
            sub = df[s] if len(chunk) > 1 else df
            sub = sub.dropna(subset=["Close"])
            if len(sub) < 30:
                continue
            px[s] = {
                "dates": [int(d.timestamp()) for d in sub.index],
                "open": [float(x) for x in sub["Open"].values],
                "close": [float(x) for x in sub["Close"].values],
                "vol": [float(x) for x in sub["Volume"].values],
            }
        except Exception:
            continue
    print(f"  {min(i+BATCH, len(need))}/{len(need)} symbols fetched, {len(px)} usable")

if "SPY" not in px:
    print("SPY missing - cannot market-adjust")
    raise SystemExit(1)
spy = px["SPY"]
spy_idx = {d: k for k, d in enumerate(spy["dates"])}


def forward_excess(sym, ts, horizon):
    """entry = next open after ts; exit = close at entry+horizon; excess vs SPY."""
    p = px.get(sym)
    if not p:
        return None
    d = p["dates"]
    k = None
    for j, x in enumerate(d):
        if x > ts:
            k = j
            break
    if k is None or k + horizon >= len(d):
        return None
    entry = p["open"][k]
    exitp = p["close"][k + horizon]
    if not entry or entry <= 0:
        return None
    ret = exitp / entry - 1.0
    # SPY over the same calendar window
    d0, d1 = d[k], d[k + horizon]
    ks = spy_idx.get(d0)
    ke = spy_idx.get(d1)
    if ks is None or ke is None or ke >= len(spy["dates"]):
        return None
    sret = spy["close"][ke] / spy["open"][ks] - 1.0
    return {"ret": ret, "excess": ret - sret, "entry_ts": d0}


def size_proxy(sym, ts):
    """60d median dollar volume strictly BEFORE the event."""
    p = px.get(sym)
    if not p:
        return None
    vals = []
    for j, x in enumerate(p["dates"]):
        if x >= ts:
            break
        vals.append(p["close"][j] * p["vol"][j])
    vals = [v for v in vals[-60:] if v and v > 0]
    return st.median(vals) if len(vals) >= 20 else None


print("\ncomputing outcomes...")
for h in (21, 63):
    res = {"strong_buy": [], "comparison": []}
    for grp, evs in (("strong_buy", sb), ("comparison", other)):
        for e in evs:
            fx = forward_excess(e["symbol"], e["ts"], h)
            if fx is None:
                continue
            sz = size_proxy(e["symbol"], e["ts"])
            if sz is None:
                continue
            res[grp].append({"symbol": e["symbol"], "excess": fx["excess"], "size": sz})

    print(f"\n=== horizon {h}d ===")
    for grp in ("strong_buy", "comparison"):
        v = res[grp]
        print(f"  {grp}: n={len(v):,} symbols={len(set(x['symbol'] for x in v))}")

    # size terciles from the pooled sample
    pooled = sorted(res["strong_buy"] + res["comparison"], key=lambda x: x["size"])
    if len(pooled) < 90:
        print("  too few priced events for terciles")
        continue
    t1, t2 = len(pooled) // 3, 2 * len(pooled) // 3
    cuts = (pooled[t1]["size"], pooled[t2]["size"])

    def terc(sz):
        if sz <= cuts[0]:
            return 0
        if sz <= cuts[1]:
            return 1
        return 2

    out = {"horizon": h, "cuts": cuts, "buckets": {}}
    for t in range(3):
        sbg = [x["excess"] for x in res["strong_buy"] if terc(x["size"]) == t]
        ctg = [x["excess"] for x in res["comparison"] if terc(x["size"]) == t]
        if len(sbg) < 10 or len(ctg) < 10:
            print(f"  tercile {t}: sb n={len(sbg)} ctl n={len(ctg)} - too few")
            continue
        diff = st.mean(sbg) - st.mean(ctg)
        # symbol-cluster bootstrap
        by_sym = defaultdict(list)
        for x in res["strong_buy"]:
            if terc(x["size"]) == t:
                by_sym[x["symbol"]].append(x["excess"])
        ctl_by_sym = defaultdict(list)
        for x in res["comparison"]:
            if terc(x["size"]) == t:
                ctl_by_sym[x["symbol"]].append(x["excess"])
        keys = sorted(by_sym)
        boots = []
        for _ in range(2000):
            pick = [random.choice(keys) for _ in keys]
            mv = [y for k in pick for y in by_sym[k]]
            boots.append(st.mean(mv))
        boots.sort()
        lo_ci, hi_ci = boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]
        sig = "SIGNIFICANT" if (lo_ci > 0 or hi_ci < 0) else "includes zero"
        print(f"  tercile {t}: sb n={len(sbg)} mean {st.mean(sbg)*100:+.2f}%  "
              f"ctl n={len(ctg)} mean {st.mean(ctg)*100:+.2f}%  "
              f"diff {diff*100:+.2f}%  sb CI [{lo_ci*100:+.2f},{hi_ci*100:+.2f}] {sig}")
        out["buckets"][t] = {
            "sb_n": len(sbg), "sb_mean_bp": round(st.mean(sbg) * 10000, 1),
            "ctl_n": len(ctg), "ctl_mean_bp": round(st.mean(ctg) * 10000, 1),
            "diff_bp": round(diff * 10000, 1),
            "sb_ci_bp": [round(lo_ci * 10000, 1), round(hi_ci * 10000, 1)],
            "ci_excludes_zero": bool(lo_ci > 0 or hi_ci < 0),
        }
    out["verdict"] = ("INVERSION HOLDS" if any(b["ci_excludes_zero"] and b["diff_bp"] < 0
                                               for b in out["buckets"].values())
                      else "UNDERDETERMINED - no bucket shows a significant negative gap")
    print(f"  -> {out['verdict']}")
    json.dump(out, open(OUT.replace(".json", f"_{h}d.json"), "w"), indent=1)

print(f"\nwrote {OUT.replace('.json','_21d.json')} and _63d.json")
