#!/usr/bin/env python3
"""PROVEIT simulation — fee-aware, account-size scenarios for KILOCODE's philosophy.

Data: data/market_prices.csv (adjusted + close, 2021-11..2026-11). Philosophies:
  EQ       = buy & hold 100% equity (FXAIX adj, S&P500 total return)
  60_40    = 60% SPY / 40% BND, monthly rebalance
  TIMING   = 200-day MA on SPY (in cash/SGOV when below), risk-control comparator
Sizes: $300, $500, $2000, $10000. Fee scenarios:
  base     = zero-commission broker, CAD-listed (no FX)
  fx       = +1.5% one-time FX (USD ETF for a Canadian)
  fxtrade  = +1.5% FX AND $5/trade (two sides)  -> small-account killer
Reports terminal value, net CAGR, max drawdown, excess-of-cash Sharpe. Writes date-stamped JSON.
"""
import csv, json, math, random, statistics as st, sys
from datetime import datetime, timezone
from pathlib import Path

F = Path(__file__).parent / "data/market_prices.csv"
COST={"EQ":0.0,"60_40":0.0,"TIMING":0.0}

def load():
    rows=list(csv.DictReader(open(F)))
    ser={}
    for c in [k for k in rows[0] if k.endswith("_adj")]:
        ser[c]=[float(r[c]) for r in rows if r[c] not in ("","NA")]
    n=min(len(v) for v in ser.values())
    return {k:v[:n] for k,v in ser.items()}

def rets(x): return [x[i]/x[i-1]-1 for i in range(1,len(x))]

def mdd(r):
    eq=1;pk=1;m=0
    for x in r: eq*=(1+x);pk=max(pk,eq);m=min(m,eq/pk-1)
    return m

def excess_sharpe(r, rf, ann=252):
    n=min(len(r),len(rf)); ex=[r[i]-rf[i] for i in range(n)]
    mu=st.mean(ex); sd=st.pstdev(ex)
    return mu/sd*math.sqrt(ann) if sd else None

def buyhold(px):
    return px[-1]/px[0]-1

def sixty40(spy,bnd):
    # monthly rebalance sleeves
    n=min(len(spy),len(bnd)); w={"s":0.6,"b":0.4}; sv={"s":0.6,"b":0.4}; prev=1; out=[]
    rs=rets(spy); rb=rets(bnd)
    for i in range(n-1):
        sv["s"]*=(1+rs[i]); sv["b"]*=(1+rb[i]); tot=sv["s"]+sv["b"]; out.append(tot/prev-1); prev=tot
        if (i+1)%21==0: sv={"s":0.6*tot,"b":0.4*tot}
    return out

def timing(spy,cash):
    # long SPY when close>SMA200 else cash(SGOV)
    rs=rets(spy); rc=rets(cash); n=len(spy); out=[]; pos=0
    for i in range(200,n-1):
        sma=sum(spy[i-199:i+1])/200
        newpos=1 if spy[i]>sma else 0
        r=rs[i] if newpos else rc[i]
        out.append(r); pos=newpos
    return out

def grow(r, start, fee_pct_once):
    v=start*(1-fee_pct_once)
    for x in r: v*=(1+x)
    return v

def strategies(ser):
    # COMMON WINDOW: start all philosophies at bar 200 so the comparison is fair
    # (otherwise the 200d-MA rule silently excludes the 2021-22 drawdown).
    START=200
    sq=ser["SPY_adj"][START:]; bnd=ser["BND_adj"][START:]; cash=ser["SGOV_adj"][START:]
    fxaix=ser["FXAIX_adj"][START:]
    r6040=sixty40(sq,bnd); rtim=timing(ser["SPY_adj"],ser["SGOV_adj"])  # timing recovers its own START
    rtim=rtim  # timing already starts at 200
    rf=rets(cash)
    def agg(r):
        return {"cagr_pct":round((( math.prod(1+x for x in r))**(252/len(r))-1)*100,2),
                "max_dd_pct":round(mdd(r)*100,2),
                "sharpe_excess":round(excess_sharpe(r,rf[-len(r):]),3) if len(r)>2 else None}
    return {
      "EQ": (r:=rets(fxaix), agg(r)),  # fxaix sliced at START
      "60_40": (r6040, agg(r6040)),
      "TIMING": (rtim, agg(rtim)),
    }

def fee_scenario(name, size, gross_cagr_pct, years):
    # convert gross CAGR to terminal given fees
    if name=="base": fx=0.0; trades=0
    elif name=="fx": fx=0.015; trades=0
    else: fx=0.015; trades=2*5.0  # $5/side
    gross_terminal=size*(1+gross_cagr_pct/100)**years
    net_terminal=(gross_terminal - (0 if name=="base" else (size*fx if name=="fx" else size*fx+trades)))
    net_cagr=((net_terminal/size)**(1/years)-1)*100 if net_terminal>0 else -100
    return {"terminal":round(net_terminal,2),"net_cagr_pct":round(net_cagr,2),
            "fee_drag_pct_of_start":round((1-net_terminal/size/(1+gross_cagr_pct/100)**years)*100,2)}

def main():
    ser=load(); n=len(ser["SPY_adj"]); years=round(n/252,2)
    S=strategies(ser)
    out={"generated_at":datetime.now(timezone.utc).isoformat(),"bars":n,"years":years,
         "data":"data/market_prices.csv (adjusted)","costs":"26bp round-turn where traded; equity/MF total-return adj",
         "philosophies":{},"by_size":{}}
    for k,(r,m) in S.items(): out["philosophies"][k]=m
    sizes=[300,500,2000,10000]
    for size in sizes:
        out["by_size"][size]={}
        for k,(r,m) in S.items():
            out["by_size"][size][k]={sc:fee_scenario(sc,size,m["cagr_pct"],years) for sc in ("base","fx","fxtrade")}
    Path(__file__).parent.joinpath(f"SIM_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%MZ')}.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=1)[:1500])
    print("years",years)
    for k,m in out["philosophies"].items(): print(k,m)

if __name__=="__main__": main()
