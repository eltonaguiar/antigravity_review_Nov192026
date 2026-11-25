#!/usr/bin/env python3
"""settle_inversion_v2.py - the honest control.

v1 compared STRONG_BUY against ALL other rating events (80,653), which includes
9,720 downgrades. Downgrades underperform by construction, so any Strong Buy vs
"everything else" gap is contaminated by the direction mix of the control pool.

v2 uses THREE controls and reports all of them:
  NEUTRAL  to_grade in Hold/Neutral/Equal-Weight/Market Perform/Sector Perform
           -> the only fair control: same information content, no directional tilt
  UPGRADE  to_grade in Buy/Overweight/Outperform/Positive
  ALL      v1's pool, kept so the contamination is visible rather than hidden

Prices cached to /tmp/px_cache.pkl so this is rerunnable without re-downloading.
"""
import csv
import json
import os
import pickle
import random
import statistics as st
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")

CSV = "/home/eaguiar2015/antigravity_review/42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv"
CACHE = "/tmp/px_cache.pkl"

NEUTRAL = {"hold", "neutral", "equal-weight", "equalweight", "market perform",
           "sector perform", "peer perform", "inline", "in-line", "market weight"}
BULLISH = {"buy", "overweight", "outperform", "positive", "accumulate", "add",
           "strong buy", "conviction buy", "top pick"}


def parse_date(d):
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
    import datetime as dt
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return int(dt.datetime.strptime(s[:10], fmt).replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            continue
    return None


rows = list(csv.DictReader(open(CSV, encoding="utf-8", errors="replace")))
events = {}
for r in rows:
    sym = (r.get("symbol") or "").strip().upper()
    ts = parse_date(r.get("date"))
    if not sym or ts is None:
        continue
    events.setdefault((sym, ts), (r.get("to_grade") or "").strip().lower())

sb, ctl_neutral, ctl_up, ctl_all = [], [], [], []
for (sym, ts), g in events.items():
    e = {"symbol": sym, "ts": ts, "grade": g}
    if "strong buy" in g:
        sb.append(e)
    else:
        ctl_all.append(e)
        if g in NEUTRAL:
            ctl_neutral.append(e)
        elif g in BULLISH:
            ctl_up.append(e)

print(f"distinct events {len(events):,}")
print(f"  STRONG_BUY      {len(sb):,} ({len(set(e['symbol'] for e in sb))} symbols)")
print(f"  NEUTRAL control {len(ctl_neutral):,}")
print(f"  UPGRADE control {len(ctl_up):,}")
print(f"  ALL control     {len(ctl_all):,}")

syms = sorted(set(e["symbol"] for e in sb) | set(e["symbol"] for e in ctl_neutral))

if os.path.exists(CACHE):
    px = pickle.load(open(CACHE, "rb"))
    print(f"prices from cache: {len(px)} symbols")
else:
    import yfinance as yf
    import datetime as dt
    lo = min(e["ts"] for e in sb) - 400 * 86400
    hi = max(e["ts"] for e in sb) + 400 * 86400
    start = dt.datetime.utcfromtimestamp(max(lo, 946684800)).strftime("%Y-%m-%d")
    end = dt.datetime.utcfromtimestamp(min(hi, 1990000000)).strftime("%Y-%m-%d")
    px = {}
    need = syms + ["SPY"]
    for i in range(0, len(need), 40):
        chunk = need[i:i + 40]
        try:
            df = yf.download(chunk, start=start, end=end, progress=False,
                             auto_adjust=True, group_by="ticker", threads=True)
        except Exception:
            continue
        for s in chunk:
            try:
                sub = df[s] if len(chunk) > 1 else df
                sub = sub.dropna(subset=["Close"])
                if len(sub) < 30:
                    continue
                px[s] = {"dates": [int(d.timestamp()) for d in sub.index],
                         "open": [float(x) for x in sub["Open"].values],
                         "close": [float(x) for x in sub["Close"].values],
                         "vol": [float(x) for x in sub["Volume"].values]}
            except Exception:
                continue
        print(f"  {min(i+40,len(need))}/{len(need)} <- {len(px)} usable")
    pickle.dump(px, open(CACHE, "wb"))
    print(f"cached {len(px)} symbols to {CACHE}")

spy = px.get("SPY")
if not spy:
    raise SystemExit("SPY missing")
spy_idx = {d: k for k, d in enumerate(spy["dates"])}


def fwd(sym, ts, h):
    p = px.get(sym)
    if not p:
        return None
    k = next((j for j, x in enumerate(p["dates"]) if x > ts), None)
    if k is None or k + h >= len(p["dates"]):
        return None
    ent = p["open"][k]
    if not ent or ent <= 0:
        return None
    ret = p["close"][k + h] / ent - 1.0
    ks, ke = spy_idx.get(p["dates"][k]), spy_idx.get(p["dates"][k + h])
    if ks is None or ke is None or ke >= len(spy["dates"]):
        return None
    sret = spy["close"][ke] / spy["open"][ks] - 1.0
    return ret - sret


def size_proxy(sym, ts):
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


def build(evs):
    out = []
    for e in evs:
        x = fwd(e["symbol"], e["ts"], H)
        if x is None:
            continue
        s = size_proxy(e["symbol"], e["ts"])
        if s is None:
            continue
        out.append({"symbol": e["symbol"], "excess": x, "size": s})
    return out


for H in (21, 63):
    print("\n" + "=" * 78)
    print(f"HORIZON {H} TRADING DAYS")
    print("=" * 78)
    S = build(sb)
    for name, pool in (("NEUTRAL", ctl_neutral), ("UPGRADE", ctl_up), ("ALL", ctl_all)):
        C = build(pool)
        if len(S) < 50 or len(C) < 200:
            print(f"  {name}: insufficient (sb {len(S)}, ctl {len(C)})")
            continue
        pooled = sorted(S + C, key=lambda x: x["size"])
        c1, c2 = pooled[len(pooled) // 3]["size"], pooled[2 * len(pooled) // 3]["size"]

        def t_of(sz):
            return 0 if sz <= c1 else (1 if sz <= c2 else 2)

        print(f"\n  control = {name}  (n={len(C):,})")
        print(f"    {'terc':>5} {'sb n':>5} {'sb mean':>9} {'ctl n':>7} {'ctl mean':>9} {'diff':>9} {'sb CI':>18}")
        sig_count = 0
        for t in range(3):
            g = [x["excess"] for x in S if t_of(x["size"]) == t]
            c = [x["excess"] for x in C if t_of(x["size"]) == t]
            if len(g) < 10 or len(c) < 30:
                continue
            by_sym = defaultdict(list)
            for x in S:
                if t_of(x["size"]) == t:
                    by_sym[x["symbol"]].append(x["excess"])
            keys = sorted(by_sym)
            boots = []
            for _ in range(2000):
                pick = [random.choice(keys) for _ in keys]
                boots.append(st.mean([y for k in pick for y in by_sym[k]]))
            boots.sort()
            lo, hi = boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]
            d = st.mean(g) - st.mean(c)
            excl = lo > 0 or hi < 0
            if excl:
                sig_count += 1
            print(f"    {t:>5} {len(g):>5} {st.mean(g)*100:>+8.2f}% {len(c):>7} {st.mean(c)*100:>+8.2f}% "
                  f"{d*100:>+8.2f}%  [{lo*100:+6.2f},{hi*100:+6.2f}] {'SIG' if excl else ''}")
        print(f"    -> {sig_count} of 3 terciles exclude zero")
