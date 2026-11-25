#!/usr/bin/env python3
"""settle_inversion_v3.py - falsification. Can I break the 63d Strong Buy effect?

v2 found STRONG_BUY excess over a NEUTRAL control in 3 of 3 size terciles at 63
days (+2.07 / +3.11 / +2.66 pp), and nothing at 21 days. Before that is reported
it has to survive the two ways it is most likely to be fake:

  A SUB-PERIOD. 2012-2018 vs 2019-2026. A pooled 15-year effect can be one
    regime (e.g. 2020-21 liquidity) repeated. If only one half carries it, the
    finding is a regime, not an anomaly.
  B ACTION TYPE. 'up' = a genuine upgrade TO Strong Buy. 'main' = an analyst
    REITERATING Strong Buy. These are different information events. If the
    effect lives only in 'main', it is momentum-chasing dressed as a rating, and
    it means analysts flag winners after the fact rather than before.
  C ANNUAL BREAKDOWN, so a single year cannot carry the result unnoticed.

Prices come from /tmp/px_cache.pkl - no re-download.
"""
import csv
import datetime as dt
import pickle
import random
import statistics as st
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")

CSV = "/home/eaguiar2015/antigravity_review/42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv"
px = pickle.load(open("/tmp/px_cache.pkl", "rb"))
spy = px["SPY"]
spy_idx = {d: k for k, d in enumerate(spy["dates"])}

NEUTRAL = {"hold", "neutral", "equal-weight", "equalweight", "market perform",
           "sector perform", "peer perform", "inline", "in-line", "market weight"}
H = 63


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
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return int(dt.datetime.strptime(s[:10], fmt).replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            continue
    return None


rows = list(csv.DictReader(open(CSV, encoding="utf-8", errors="replace")))
ev = {}
for r in rows:
    sym = (r.get("symbol") or "").strip().upper()
    ts = parse_date(r.get("date"))
    if not sym or ts is None:
        continue
    ev.setdefault((sym, ts), ((r.get("to_grade") or "").strip().lower(),
                              (r.get("action") or "").strip().lower()))


def fwd(sym, ts):
    p = px.get(sym)
    if not p:
        return None
    k = next((j for j, x in enumerate(p["dates"]) if x > ts), None)
    if k is None or k + H >= len(p["dates"]):
        return None
    ent = p["open"][k]
    if not ent or ent <= 0:
        return None
    ret = p["close"][k + H] / ent - 1.0
    ks, ke = spy_idx.get(p["dates"][k]), spy_idx.get(p["dates"][k + H])
    if ks is None or ke is None or ke >= len(spy["dates"]):
        return None
    return ret - (spy["close"][ke] / spy["open"][ks] - 1.0)


def size_proxy(sym, ts):
    p = px.get(sym)
    if not p:
        return None
    v = []
    for j, x in enumerate(p["dates"]):
        if x >= ts:
            break
        v.append(p["close"][j] * p["vol"][j])
    v = [x for x in v[-60:] if x and x > 0]
    return st.median(v) if len(v) >= 20 else None


recs = []
for (sym, ts), (g, act) in ev.items():
    x = fwd(sym, ts)
    if x is None:
        continue
    s = size_proxy(sym, ts)
    if s is None:
        continue
    recs.append({"symbol": sym, "ts": ts, "year": dt.datetime.utcfromtimestamp(ts).year,
                 "grade": g, "action": act, "excess": x, "size": s})

sb = [r for r in recs if "strong buy" in r["grade"]]
neu = [r for r in recs if r["grade"] in NEUTRAL]
print(f"priced events: {len(recs):,}  strong_buy {len(sb):,}  neutral {len(neu):,}")
print(f"{H}-day excess vs SPY, next-open entry\n")

pool = sorted(sb + neu, key=lambda x: x["size"])
c1, c2 = pool[len(pool) // 3]["size"], pool[2 * len(pool) // 3]["size"]


def terc(s):
    return 0 if s <= c1 else (1 if s <= c2 else 2)


def block(label, S, C):
    if len(S) < 25 or len(C) < 200:
        print(f"  {label:<26} insufficient (sb {len(S)}, ctl {len(C)})")
        return
    diffs, sigs = [], 0
    for t in range(3):
        g = [x["excess"] for x in S if terc(x["size"]) == t]
        c = [x["excess"] for x in C if terc(x["size"]) == t]
        if len(g) < 8 or len(c) < 40:
            continue
        by = defaultdict(list)
        for x in S:
            if terc(x["size"]) == t:
                by[x["symbol"]].append(x["excess"])
        keys = sorted(by)
        boots = []
        for _ in range(1500):
            pick = [random.choice(keys) for _ in keys]
            boots.append(st.mean([y for k in pick for y in by[k]]))
        boots.sort()
        lo, hi = boots[int(.025 * len(boots))], boots[int(.975 * len(boots))]
        d = st.mean(g) - st.mean(c)
        diffs.append(d)
        if lo > 0 or hi < 0:
            sigs += 1
    if diffs:
        print(f"  {label:<26} n_sb={len(S):<5} mean diff {st.mean(diffs)*100:>+6.2f}%  "
              f"{sigs}/3 terciles SIG")


print("=" * 78)
print("A. SUB-PERIOD STABILITY")
print("=" * 78)
for lo, hi in ((2012, 2018), (2019, 2026), (2012, 2026)):
    block(f"{lo}-{hi}", [r for r in sb if lo <= r["year"] <= hi],
          [r for r in neu if lo <= r["year"] <= hi])

print("\n" + "=" * 78)
print("B. UPGRADE vs REITERATION  (this is the one that matters)")
print("=" * 78)
for act in ("up", "main", "init", "reit"):
    S = [r for r in sb if r["action"] == act]
    if S:
        block(f"action={act}", S, neu)

print("\n" + "=" * 78)
print("C. ANNUAL - can one year carry it?")
print("=" * 78)
print(f"  {'year':>6} {'n_sb':>6} {'sb mean':>9} {'neu mean':>9} {'diff':>9}")
for y in range(2012, 2027):
    S = [r["excess"] for r in sb if r["year"] == y]
    C = [r["excess"] for r in neu if r["year"] == y]
    if len(S) < 10 or len(C) < 50:
        continue
    print(f"  {y:>6} {len(S):>6} {st.mean(S)*100:>+8.2f}% {st.mean(C)*100:>+8.2f}% "
          f"{(st.mean(S)-st.mean(C))*100:>+8.2f}%")
