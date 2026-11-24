#!/usr/bin/env python3
"""Per-symbol HARVEST consensus history + forward excess for the track-record tab."""
import json, sys, time
from collections import defaultdict
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_harvest as B
import harvest_rules as R

RAW = Path(__file__).resolve().parent / "evidence" / "finnhub_recommendation_raw.jsonl"
OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "harvest_symbol_history.json"

def main():
    recs=[json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    px={}
    for s in [r["symbol"] for r in recs]+["SPY"]:
        try: px[s]=B.chart(s)
        except Exception as e: print("chart fail",s,e)
        time.sleep(0.6)
    spy=px["SPY"]; out=[]; agg=defaultdict(list)
    for rec in recs:
        sym=rec["symbol"]
        if sym not in px: continue
        hist=sorted(rec["rows"], key=lambda x:x["period"])
        periods=[]
        for i,per in enumerate(hist):
            c={"strong_buy":per["strongBuy"],"buy":per["buy"],"hold":per["hold"],"sell":per["sell"],"strong_sell":per["strongSell"]}
            start=date.fromisoformat(per["period"])
            label=R.label_for_counts(**c)
            d=None
            if i>0:
                p={"strong_buy":hist[i-1]["strongBuy"],"buy":hist[i-1]["buy"],"hold":hist[i-1]["hold"],"sell":hist[i-1]["sell"],"strong_sell":hist[i-1]["strongSell"]}
                delta=100*(R.buy_side_of(**c)-R.buy_side_of(**p))
                d=R.direction_for(delta,R.counts_total(**c),R.bucket_moves(p,c))
            e21=B.excess(px[sym],spy,start,21); e63=B.excess(px[sym],spy,start,63)
            periods.append({"period":per["period"],"label":label,"analysts":R.counts_total(**c),
                            "buy_side_pct":round(100*R.buy_side_of(**c),1),"direction":d or "STABLE",
                            "fwd21_pct":round(e21,3) if e21 is not None else None,
                            "fwd63_pct":round(e63,3) if e63 is not None else None})
            if e21 is not None: agg[sym].append(e21)
        v=[x for x in periods if x["fwd21_pct"] is not None]
        out.append({"symbol":sym,"periods":periods,"n_periods":len(periods),
                    "mean_fwd21_pct":round(sum(agg[sym])/len(agg[sym]),3) if agg[sym] else None,
                    "latest":periods[-1]["label"] if periods else None,"latest_direction":periods[-1]["direction"] if periods else None})
    out.sort(key=lambda x:(x["mean_fwd21_pct"] is None, -(x["mean_fwd21_pct"] or -999)))
    res={"schema":"harvest_history/1","generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
         "entry":"next close strictly after period date","cost_bps":B.COST_BPS,"benchmark":"SPY",
         "caveats":["monthly consensus only (4 periods)","overlapping windows","survivorship",
                    "sell-side bullish bias","no firm/person attribution in the free feed"],
         "symbols":out}
    OUT.write_text(json.dumps(res,indent=2)+"\n")
    print("wrote",OUT,"symbols",len(out))
if __name__=="__main__": main()
