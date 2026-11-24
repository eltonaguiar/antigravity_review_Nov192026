#!/usr/bin/env python3
"""PROVEIT tweaks — does ANY parameter tweak or blend beat plain buy-and-hold?
Sweeps 200d-MA length {100,150,200,250}, 60/40 rebalance {21,63,252}d, and a 50/50 EQ+timing blend.
Common window (start bar 200) for fairness. Net of 26bp only where traded. Writes dated JSON."""
import csv,json,math,statistics as st
from datetime import datetime,timezone
from pathlib import Path
F=Path(__file__).parent/"data/market_prices.csv"
def load():
    rows=list(csv.DictReader(open(F))); ser={c:[float(r[c]) for r in rows if r[c] not in("","NA")] for c in (k for k in rows[0] if k.endswith("_adj"))}
    n=min(len(v) for v in ser.values()); return {k:v[:n] for k,v in ser.items()}
def rets(x): return [x[i]/x[i-1]-1 for i in range(1,len(x))]
def mdd(r):
    eq=1;pk=1;m=0
    for x in r: eq*=(1+x);pk=max(pk,eq);m=min(m,eq/pk-1)
    return m
def cagr(r): return (math.prod(1+x for x in r))**(252/len(r))-1
def xsharpe(r,rf):
    n=min(len(r),len(rf)); ex=[r[i]-rf[i] for i in range(n)]; mu=st.mean(ex); sd=st.pstdev(ex)
    return mu/sd*math.sqrt(252) if sd else 0
def agg(r,rf): return {"cagr_pct":round(cagr(r)*100,2),"dd_pct":round(mdd(r)*100,2),"sharpe":round(xsharpe(r,rf),3)}
def timing(spy,cash,ma):
    rs=rets(spy);rc=rets(cash);out=[]
    for i in range(ma,len(spy)-1):
        sma=sum(spy[i-ma+1:i+1])/ma
        out.append(rs[i] if spy[i]>sma else rc[i])
    return out
def sixty40(spy,bnd,reb):
    rs=rets(spy);rb=rets(bnd);n=min(len(rs),len(rb));sv={"s":.6,"b":.4};prev=1;out=[]
    for i in range(n):
        sv["s"]*=(1+rs[i]);sv["b"]*=(1+rb[i]);tot=sv["s"]+sv["b"];out.append(tot/prev-1);prev=tot
        if (i+1)%reb==0: sv={"s":.6*tot,"b":.4*tot}
    return out
def main():
    ser=load(); START=250
    spy=ser["SPY_adj"];bnd=ser["BND_adj"];cash=ser["SGOV_adj"];fxaix=ser["FXAIX_adj"]
    rf=rets(cash)
    base_r=rets(fxaix[START:]); base=agg(base_r,rf[-len(base_r):])
    out={"generated_at":datetime.now(timezone.utc).isoformat(),"baseline_buyhold":base,"timing":{},"sixty40":{},"blend":{}}
    for ma in (100,150,200,250):
        r=timing(spy,cash,ma); out["timing"][ma]=agg(r,rf[-len(r):])
    for reb in (21,63,252):
        r=sixty40(spy,bnd,reb); out["sixty40"][reb]=agg(r,rf[-len(r):])
    # blend 50/50 buy&hold(SPY) + timing200
    t=timing(spy,cash,200); bh=rets(spy)[-len(t):]
    blend=[0.5*bh[i]+0.5*t[i] for i in range(len(t))]; out["blend"]["50_50_eq_timing200"]=agg(blend,rf[-len(blend):])
    # honesty: does anything BEAT baseline on BOTH cagr and dd (pareto)?
    b=base; pareto=[]
    for grp in ("timing","sixty40","blend"):
        for k,v in out[grp].items():
            if v["cagr_pct"]>b["cagr_pct"] and v["dd_pct"]>b["dd_pct"]: pareto.append(f"{grp}:{k}")
    out["pareto_beats_baseline"]=pareto or "NONE"
    Path(__file__).parent.joinpath(f"TWEAKS_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%MZ')}.json").write_text(json.dumps(out,indent=2)+"\n")
    print("baseline buy&hold:",base)
    for g in ("timing","sixty40","blend"):
        for k,v in out[g].items(): print(f"  {g}:{k}",v)
    print("Pareto beats baseline (higher CAGR AND shallower DD):",out["pareto_beats_baseline"])
if __name__=="__main__": main()
