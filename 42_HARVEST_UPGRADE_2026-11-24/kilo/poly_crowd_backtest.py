#!/usr/bin/env python3
"""Pre-registered backtest: buy the Polymarket crowd favorite 7 days before resolution.

Rule (frozen before the first fetch):
- Universe: closed binary markets, volume >= $100k, endDate 2024-01-01..now,
  outcomePrices exactly one 1 and one 0 (resolved binary).
- Signal time: last daily price at or before end - 7 days, and no older than end - 30 days.
- Entry: if p_fav >= 0.5 buy that outcome at p_fav, else buy the other at 1-p_fav.
  Skip 0.02 < p < 0.98 only (exclude near-certain/never-traded).
- Payoff 1 if the bought outcome won, else 0. Return = (payoff-entry)/entry.
- No fee (Polymarket has no resolution fee; gas ignored). Report gross.
- Falsifier: mean net return <= 0 with 95% CI excluding 0 => no crowd-favorite edge.
"""
import json, math, random, statistics, time, urllib.request, urllib.error
from datetime import datetime, timezone

GAMMA="https://gamma-api.polymarket.com/markets"
CLOB="https://clob.polymarket.com/prices-history"
UA={"User-Agent":"kilo-research/1.0"}
MIN_VOL=1_000_000.0
HORIZON_D=7
MAX_AGE_D=30
N_MARKETS=120
random.seed(20261124)

def get(u):
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(1.0)
    return None

def ts(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()

def boot(vals,B=4000):
    if len(vals)<3: return (None,None)
    means=[]
    n=len(vals)
    for _ in range(B):
        means.append(sum(vals[random.randrange(n)] for _ in range(n))/n)
    means.sort(); return means[int(.025*B)], means[int(.975*B)-1]

markets=[]; off=0
while len(markets)<N_MARKETS and off<800:
    d=get(f"{GAMMA}?closed=true&limit=100&offset={off}&order=volumeNum&ascending=false")
    if not d: break
    for m in d:
        try:
            vol=float(m.get("volumeNum") or m.get("volume") or 0)
            if vol<MIN_VOL or not m.get("closed"): continue
            prices=json.loads(m.get("outcomePrices") or "[]")
            if len(prices)!=2 or sorted(float(x) for x in prices)!=[0.0,1.0]: continue
            end=m.get("endDate")
            if not end: continue
            e=ts(end)
            if e < ts("2024-01-01T00:00:00Z") or e > time.time(): continue
            toks=json.loads(m.get("clobTokenIds") or "[]")
            if len(toks)!=2: continue
            markets.append((m,toks,[float(x) for x in prices],e))
        except Exception:
            continue
    off+=100

rows=[]; skipped=0
for m,toks,prices,end in markets:
    cutoff=end-HORIZON_D*86400
    h=get(f"{CLOB}?market={toks[0]}&interval=max&fidelity=1440")
    hist=(h or {}).get("history") or []
    pts=[(x["t"],float(x["p"])) for x in hist if isinstance(x.get("p"),(int,float)) and x["t"]<=cutoff]
    pts=[x for x in pts if x[0]>=end-MAX_AGE_D*86400]
    if not pts:
        skipped+=1; continue
    p0=pts[-1][1]
    if not (0.02<p0<0.98):
        skipped+=1; continue
    win0 = prices[0]==1.0
    if p0>=0.5:
        entry=p0; won=win0
    else:
        entry=1-p0; won=not win0
    if entry<=0 or entry>=1:
        skipped+=1; continue
    rows.append({"question":m.get("question","")[:80],"volume":float(m.get("volumeNum") or m.get("volume") or 0),
                 "end":datetime.fromtimestamp(end,timezone.utc).date().isoformat(),
                 "p_fav":round(max(p0,1-p0),4),"entry":round(entry,4),
                 "won":bool(won),"ret":(1.0 if won else 0.0)/entry-1.0})
    time.sleep(0.15)

rets=[r["ret"] for r in rows]
mean=sum(rets)/len(rets) if rets else None
lo,hi=boot(rets)
wr=sum(r["won"] for r in rows)/len(rows) if rows else None
# calibration by favorite-price bucket
buckets={}
for r in rows:
    b=round(math.floor(r["p_fav"]*10)/10,1); b=max(b,0.5); b=min(b,0.9)
    buckets.setdefault(b,[]).append(r)
cal=[{"p_bucket":f"{b:.1f}-{b+0.1:.1f}","n":len(v),
      "predicted":round(sum(x["p_fav"] for x in v)/len(v),4),
      "realized":round(sum(x["won"] for x in v)/len(v),4)} for b,v in sorted(buckets.items())]
out={"prereg":{"rule":"buy crowd favorite at T-7d, hold to resolution","min_volume":MIN_VOL,
     "horizon_days":HORIZON_D,"max_entry_age_days":MAX_AGE_D,"fee_bps":0,
     "falsifier":"mean net <= 0 with 95% CI excluding 0"},
     "fetched_markets":len(markets),"used":len(rows),"skipped":skipped,
     "mean_ret":mean,"median_ret":statistics.median(rets) if rets else None,
     "ci95": [lo,hi],"win_rate":wr,"p_one_sided_gt0": None,
     "calibration":cal,"rows":rows}
# permutation/sign test p that mean>0
if rets:
    pos=sum(1 for x in rets if x>0)
    # exact-ish normal approx sign test
    n=len(rets); z=(pos-n/2)/math.sqrt(n/4) if n else 0
    out["sign_test_z"]=z; out["sign_test_p_gt0"]=0.5*(1+math.erf(z/math.sqrt(2)))
json.dump(out,open("42_HARVEST_UPGRADE_2026-11-24/kilo/poly_crowd_backtest.json","w"),indent=1)
print(json.dumps({k:out.get(k) for k in ("fetched_markets","used","skipped","mean_ret","ci95","win_rate","sign_test_p_gt0")},indent=1))
for c in cal: print(c)
