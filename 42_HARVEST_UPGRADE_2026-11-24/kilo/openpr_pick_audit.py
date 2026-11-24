#!/usr/bin/env python3
"""Post-publication audit: openPR '7 Best Meme Coins to Buy' (published 2026-11-23 11:52 CET).

Picks named: DOGE, SHIB, PEPE, BONK, WIF, FLOKI, APEING (presale).
Rule: entry = close of the first full 1h Binance bar after publication; latest = last close;
20 bp round trip; BTC same window. APEING has no market price -> unmeasurable.
Also checks the article's quoted Nov-19 prices against the actual Nov-19 daily close.
"""
import json,time,urllib.request
from datetime import datetime,timezone

PUB="2026-11-23T10:52:35Z"  # 11:52:35 +01:00
PUB_TS=int(datetime.fromisoformat(PUB.replace("Z","+00:00")).timestamp())
QUOTED={"DOGE":0.05895,"SHIB":0.000003796,"PEPE":0.000003744,"BONK":0.000002360,"WIF":0.133682,"FLOKI":0.00001773}
SYMS={"DOGE":"DOGEUSDT","SHIB":"SHIBUSDT","PEPE":"PEPEUSDT","BONK":"BONKUSDT","WIF":"WIFUSDT","FLOKI":"FLOKIUSDT","BTC":"BTCUSDT"}

def kl(sym,interval,start,limit=200):
    u=f"https://api.binance.com/api/v3/klines?symbol={sym}&interval={interval}&startTime={start}&limit={limit}"
    with urllib.request.urlopen(u,timeout=30) as r: return json.loads(r.read().decode())

out={"source":"https://www.openpr.com/news/4697189/from-market-favourites-to-new-contenders-7-best-meme-coins-to-buy",
     "publication":"2026-11-23T11:52:35+01:00","entry":"first full 1h close after publication",
     "cost_bps":20,"assets":{}}
# actual Nov 19 daily close for quoted-price check
d19=int(datetime(2026,11,19,tzinfo=timezone.utc).timestamp()*1000)
h_start=PUB_TS//3600*3600*1000
data={}
for n,s in SYMS.items():
    try:
        h=kl(s,"1h",h_start,60); d=kl(s,"1d",d19,3)
        bars=[(int(x[0]),float(x[4])) for x in h]
        entry=next((c for t,c in bars if t+3600*1000>PUB_TS*1000),None)
        last=bars[-1][1] if bars else None
        data[n]={"entry":entry,"last":last,"nov19_close":float(d[0][4]) if d else None,"bars":len(bars)}
    except Exception as e: data[n]={"error":str(e)}
    time.sleep(0.2)

btc=data.get("BTC",{})
for n,v in data.items():
    if "entry" not in v or v.get("entry") is None: out["assets"][n]={"error":v.get("error","no bars")}; continue
    r=v["last"]/v["entry"]-1
    q=QUOTED.get(n)
    out["assets"][n]={"entry":v["entry"],"last":v["last"],"ret_since_pub_pct":round(100*r,3),
        "ret_since_pub_net20bp_pct":round(100*r-0.20,3),"bars":v["bars"],
        "quoted_nov19":q,"actual_nov19_close":v["nov19_close"],
        "quoted_vs_actual_pct":round(100*(q/v["nov19_close"]-1),2) if q and v["nov19_close"] else None}
    if n!="BTC" and btc.get("entry"):
        out["assets"][n]["excess_vs_btc_pp"]=round(100*(r-(btc["last"]/btc["entry"]-1)),3)
out["btc_ret_since_pub_pct"]=round(100*(btc["last"]/btc["entry"]-1),3) if btc.get("entry") else None
out["apeing"]="presale at $0.00095; no public market price -> unmeasurable"
out["source_quality"]={
 "transparency":{"score":1,"note":"paid press release on openPR; distributor 'Crypto Presale PR'; no author"},
 "specificity":{"score":2,"note":"7 named assets, quoted Nov-19 prices, several Dec-2026 targets"},
 "independence":{"score":0,"note":"promotes Apeing presale; the release is by a crypto presale PR service"},
 "verifiability":{"score":2,"note":"dated publication timestamp and quoted prices can be checked"},
 "measurable_track_record":{"score":0,"note":"no prior calls or outcomes"},
 "total_5":5}
json.dump(out,open("42_HARVEST_UPGRADE_2026-11-24/kilo/openpr_pick_audit.json","w"),indent=1)
print(json.dumps(out["assets"],indent=1)); print("BTC",out["btc_ret_since_pub_pct"])
