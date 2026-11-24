#!/usr/bin/env python3
"""Post-publication audit of a meme-coin 'analyst picks' listicle.

Source: bmic.ai/listicles/analyst-pick-meme-coin-2026/ (page says Updated 2026-08-29)
Named assets: DOGE, SHIB, PEPE, BONK, FLOKI, BMIC (BMIC is the publisher's presale token).
Rule frozen before fetching: enter at the first daily close on/after 2026-08-30, hold to the
latest close; report 7d, 30d, and to-date return; benchmark BTC; 20 bp round-trip cost.
BMIC has no public market price -> unmeasurable, not assumed.
"""
import json,time,urllib.request
from datetime import datetime,timezone

URL="https://bmic.ai/listicles/analyst-pick-meme-coin-2026/"
PUB="2026-08-29"
START=int(datetime(2026,8,30,tzinfo=timezone.utc).timestamp()*1000)
SYMS={"DOGE":"DOGEUSDT","SHIB":"SHIBUSDT","PEPE":"PEPEUSDT","BONK":"BONKUSDT","FLOKI":"FLOKIUSDT","BTC":"BTCUSDT"}

def klines(sym):
    u=f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1d&startTime={START}&limit=200"
    with urllib.request.urlopen(u,timeout=30) as r: return json.loads(r.read().decode())

def ret(closes,a,b): return closes[b]/closes[a]-1

out={"source":URL,"publication_label":PUB,"entry":"first daily close on/after 2026-08-30",
     "cost_bps":20,"assets":{}}
data={}
for name,sym in SYMS.items():
    try:
        k=klines(sym); data[name]=[float(x[4]) for x in k]
        print(name, len(k), k[0][0], k[-1][0])
    except Exception as e:
        print("ERR",name,e); data[name]=[]
    time.sleep(0.3)

for name,cl in data.items():
    if len(cl)<2: out["assets"][name]={"error":"no klines"}; continue
    r7=ret(cl,0,min(7,len(cl)-1)); r30=ret(cl,0,min(30,len(cl)-1)); rtd=ret(cl,0,len(cl)-1)
    peak=cl[0]; mdd=0.0
    for p in cl:
        peak=max(peak,p); mdd=min(mdd,p/peak-1)
    out["assets"][name]={"n_bars":len(cl),"entry":cl[0],"last":cl[-1],
        "ret_7d_pct":round(100*r7,2),"ret_30d_pct":round(100*r30,2),
        "ret_to_date_pct":round(100*rtd,2),"max_dd_from_entry_pct":round(100*mdd,2)}
    out["assets"][name]["ret_to_date_net20bp_pct"]=round(100*rtd-0.20,2)

btc=out["assets"].get("BTC",{}).get("ret_to_date_pct")
for name in ("DOGE","SHIB","PEPE","BONK","FLOKI"):
    a=out["assets"].get(name)
    if a and btc is not None and "ret_to_date_pct" in a:
        a["excess_vs_btc_pp"]=round(a["ret_to_date_pct"]-btc,2)
out["btc_ret_to_date_pct"]=btc
out["bmic"]="no public market price; presale token promoted by the publisher -> unmeasurable"
out["source_quality"]={
 "transparency":{"score":2,"note":"named 'BMIC Research Desk', date 2026-08-29, no author"},
 "specificity":{"score":1,"note":"tickers only; no entry price, horizon, target or sizing"},
 "independence":{"score":0,"note":"article ends by promoting the publisher's own BMIC presale; a paid-advertorial conflict"},
 "verifiability":{"score":1,"note":"no dated call, no archived claim; only the page's 'Updated' date"},
 "measurable_track_record":{"score":0,"note":"no prior calls or outcomes published"},
 "total_5":4}
json.dump(out,open("42_HARVEST_UPGRADE_2026-11-24/kilo/news_source_pick_audit.json","w"),indent=1)
print(json.dumps({k:out["assets"].get(k) for k in ("DOGE","SHIB","PEPE","BONK","FLOKI","BTC")},indent=1))
