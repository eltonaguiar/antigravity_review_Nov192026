#!/usr/bin/env python3
"""Experiment: does a change in analyst COVERAGE (not level, not direction)
predict forward excess returns? Buckets: INITIATION (n_now-n_prior>=2),
DROP (<=-2), STABLE. Entry next close; exits 21/63d; excess vs SPY; 6.7122bp.
Falsifier: no bucket with CI-low>0 at n>=30, or effect < 2x cost.
"""
import json, statistics, sys, time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_harvest as B
import harvest_rules as R

RAW = Path(__file__).resolve().parent / "evidence" / "finnhub_recommendation_raw.jsonl"
OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "harvest_coverage_change.json"

def main():
    recs=[json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    px={}
    for s in [r["symbol"] for r in recs]+["SPY"]:
        try: px[s]=B.chart(s)
        except Exception as e: print("chart fail",s,e)
        time.sleep(0.7)
    spy=px["SPY"]; buckets=defaultdict(lambda: defaultdict(list))
    for rec in recs:
        sym=rec["symbol"]
        if sym not in px: continue
        hist=sorted(rec["rows"], key=lambda x:x["period"])
        for i in range(1,len(hist)):
            now,prev=hist[i],hist[i-1]
            n_now=now["strongBuy"]+now["buy"]+now["hold"]+now["sell"]+now["strongSell"]
            n_prev=prev["strongBuy"]+prev["buy"]+prev["hold"]+prev["sell"]+prev["strongSell"]
            d=n_now-n_prev
            bucket="INITIATION" if d>=2 else ("DROP" if d<=-2 else "STABLE")
            start=date.fromisoformat(now["period"])
            e21=B.excess(px[sym],spy,start,21); e63=B.excess(px[sym],spy,start,63)
            if e21 is not None: buckets[bucket]["21d"].append(e21)
            if e63 is not None: buckets[bucket]["63d"].append(e63)
    out={"experiment":"coverage_change","cost_bps":B.COST_BPS,
         "buckets":{k:{h:B.stats(v) for h,v in d.items()} for k,d in buckets.items()}}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    for h in ("21d","63d"):
        print(h)
        for k in ("INITIATION","STABLE","DROP"):
            s=buckets[k].get(h,[])
            st=B.stats(s)
            if st.get("n") and st.get("mean_pct") is not None:
                print(f"  {k:<10} n={st['n']:<3} mean={st['mean_pct']:+.3f}% CI=[{st['ci95_pct'][0]:+.3f},{st['ci95_pct'][1]:+.3f}] hit={st['hit_rate']:.0%} low>0={st['ci_low_gt_0']}")
    print("wrote",OUT)

if __name__=="__main__": main()
