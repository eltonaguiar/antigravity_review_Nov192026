#!/usr/bin/env python3
"""PROVEIT behaviour — the cost of common investor mistakes, on real adjusted prices.
Baseline buy&hold vs: panic-sell at -10/-15/-20% DD then re-enter after 1/3/6 months;
missing the best 10/20/30 days; entering at the worst (peak) date. Common window; total return."""
import csv,math,json,statistics as st
from datetime import datetime,timezone
from pathlib import Path
F=Path(__file__).parent/"data/market_prices.csv"
def load():
    rows=list(csv.DictReader(open(F))); return [float(r["FXAIX_adj"]) for r in rows if r["FXAIX_adj"] not in ("","NA")]
def cagr_from_values(v): # v = equity curve ending value per $1
    yrs=len(v)/252.0; return (v[-1])**(1/yrs)-1 if v[-1]>0 else -1
def dd_curve(px):
    peak=px[0]; out=[]
    for p in px: peak=max(peak,p); out.append(p/peak-1)
    return out
def buyhold(px): return px[-1]/px[0]-1
def panic(px,thr,reentry_days):
    # exit when dd<=thr; stay in cash reentry_days; then buy back
    pos=1.0; val=1.0; peak=px[0]; cash=None; cooldown=0; in_cash=False
    for i in range(1,len(px)):
        r=px[i]/px[i-1]-1
        if not in_cash:
            val*=(1+r); peak=max(peak,px[i])
            dd=px[i]/peak-1
            if dd<=thr: in_cash=True; cooldown=reentry_days  # sell at close
        else:
            cooldown-=1
            if cooldown<=0: in_cash=False; peak=px[i]  # rebuy
    yrs=len(px)/252.0
    return val**(1/yrs)-1  # val is total growth factor
def miss_best(px,k):
    r=[px[i]/px[i-1]-1 for i in range(1,len(px))]
    idx=sorted(range(len(r)),key=lambda i:-r[i])[:k]
    tot=1.0
    for i,ri in enumerate(r):
        if i in idx: continue
        tot*=(1+ri)
    return tot**(252/len(r))-1
def main():
    px=load(); years=len(px)/252
    base_factor=px[-1]/px[0]            # growth FACTOR (not fraction)
    base_cagr=base_factor**(1/years)-1
    out={"generated_at":datetime.now(timezone.utc).isoformat(),"years":round(years,2),
         "baseline_buyhold_cagr_pct":round(base_cagr*100,2),
         "panic_sell_cagr_pct":{},"miss_best_days_cagr_pct":{},"notes":{}}
    for thr in (-0.10,-0.15,-0.20):
        for rd in (21,63,126):
            c=panic(px,thr,rd)
            out["panic_sell_cagr_pct"][f"dd{int(thr*100)}_reenter{rd}d"]=round(c*100,2)
    for k in (10,20,30):
        out["miss_best_days_cagr_pct"][f"miss_top{k}"]=round(miss_best(px,k)*100,2)
    # worst entry: enter at the date with the deepest subsequent 20-day drawdown, hold to end
    worst_i=0; worst=-9
    for i in range(len(px)-20):
        dd=px[i+20]/px[i]-1
        if dd<worst: worst=dd; worst_i=i
    out["worst_entry_hold_cagr_pct"]=round(((px[-1]/px[worst_i])**(252/(len(px)-worst_i))-1)*100,2)
    out["notes"]={"panic":"dd<=thr exit to cash, rebuy after N days","miss_best":"drop top-K daily returns",
                  "worst_entry":"enter at deepest 20-day-drop date, hold"}
    Path(__file__).parent.joinpath(f"BEHAVIOUR_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%MZ')}.json").write_text(json.dumps(out,indent=2)+"\n")
    print("baseline buy&hold CAGR:",out["baseline_buyhold_cagr_pct"],"%  (years",round(years,2),")")
    print("panic-sell (CAGR%):"); [print("  ",k,v) for k,v in out["panic_sell_cagr_pct"].items()]
    print("miss best days (CAGR%):",out["miss_best_days_cagr_pct"])
    print("worst entry then hold CAGR%:",out["worst_entry_hold_cagr_pct"])
if __name__=="__main__": main()
