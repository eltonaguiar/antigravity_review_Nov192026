#!/usr/bin/env python3
"""Cost-adjusted expectancy by asset class and symbol (read-only).

DB: ejaguiar1_stocks.at_pick_outcomes. Credentials read from line index 82 of
/home/eaguiar2015/dbpasses.txt at runtime; never printed or committed.
Costs are explicit per-class round-turn assumptions, stated in the artifact.
"""
import json, statistics, collections, math
import pymysql

COST_BP = {
    'CRYPTO': 36.0,       # midpoint of measured 20-52 bp band; perps higher than equity
    'FOREX': 7.53,        # upper-bound measured
    'COMMODITY': 20.0,    # assumed, not measured
    'EQUITY': 4.01,       # central measured bracket (ceiling 12.07 is stress)
    'FUTURES': 12.07,     # equity ceiling proxy; no roll-adjusted series
    'INDEX': 6.71,        # ETF/index measured
    'ETF': 6.71,          # measured
    'BOND': 0.61,         # measured
    'MEME': 52.0,         # widest measured crypto band
    'UNKNOWN': 12.07,
    'BLANK': 12.07,
    'STOCKS': 4.01, 'STOCK': 4.01,
    'PENNY': 52.0, 'PENNYSTOCK': 52.0,
}
COST_BASIS = {
    'CRYPTO': 'midpoint of measured 20-52 bp; perp fees/spreads above equity',
    'FOREX': 'upper-bound measured',
    'COMMODITY': 'assumed 20 bp (not measured)',
    'EQUITY': 'central measured bracket; ceiling 12.07 bp is stress',
    'FUTURES': 'equity ceiling proxy; no roll-adjusted series',
    'INDEX': 'ETF/index measured', 'ETF': 'measured', 'BOND': 'measured',
    'MEME': 'widest measured crypto band', 'UNKNOWN': 'equity central proxy',
    'BLANK': 'equity central proxy', 'STOCKS': 'equity central', 'STOCK': 'equity central',
    'PENNY': 'crypto widest proxy', 'PENNYSTOCK': 'crypto widest proxy',
}

def read_pw():
    lines = open('/home/eaguiar2015/dbpasses.txt', errors='ignore').read().splitlines()
    return lines[82].strip()

def stats(vals):
    n=len(vals); mean=statistics.mean(vals)*100; med=statistics.median(vals)*100
    sd=statistics.stdev(vals)*100 if n>1 else None
    wins=[v for v in vals if v>0]; losses=[v for v in vals if v<0]
    return {'n':n,'mean_bp':round(mean,4),'median_bp':round(med,4),'sd_bp':round(sd,4) if sd else None,
            'win_rate':round(len(wins)/n,4) if n else None,
            'avg_win_bp':round(statistics.mean(wins)*100,4) if wins else None,
            'avg_loss_bp':round(statistics.mean(losses)*100,4) if losses else None,
            'wins':len(wins),'losses':len(losses),'min_bp':round(min(vals)*100,4),'max_bp':round(max(vals)*100,4)}

def verdict(mean_bp, cost):
    if mean_bp > cost: return 'CLEARS-COST'
    if mean_bp <= 0: return 'FAILS-COST'
    return f'BREAKEVEN-COST-NEEDED {mean_bp:.2f} bp'

def main():
    c=pymysql.connect(host='mysql.50webs.com',user='ejaguiar1_stocks',password=read_pw(),database='ejaguiar1_stocks',connect_timeout=20,charset='utf8mb4')
    cur=c.cursor(); cur.execute("SELECT asset_class, symbol, status, pnl_pct FROM at_pick_outcomes")
    rows=cur.fetchall(); c.close()
    counts={'raw':len(rows),'pnl_nonnull':0,'resolved':0,'class_known':0}
    by=collections.defaultdict(list); bysym=collections.defaultdict(list)
    for ac,sym,st,pnl in rows:
        if pnl is None: continue
        counts['pnl_nonnull']+=1
        if st not in ('WON','LOST','EXPIRED','FLAT'): continue
        counts['resolved']+=1
        cls=(ac or 'BLANK').strip().upper()
        if cls not in COST_BP: cls='UNKNOWN'
        v=float(pnl); by[cls].append(v); bysym[(cls,sym)].append(v)
    counts['class_known']=sum(len(v) for v in by.values())
    out={'source':'ejaguiar1_stocks.at_pick_outcomes','counts':counts,
         'cost_bp':COST_BP,'cost_basis':COST_BASIS,
         'classes':{},'symbols':[]}
    for cls,vals in sorted(by.items(), key=lambda x:(-len(x[1]),x[0])):
        s=stats(vals); cost=COST_BP.get(cls,12.07)
        s.update({'asset_class':cls,'cost_bp':cost,'verdict':verdict(s['mean_bp'],cost),
                  'mean_exceeds_cost':s['mean_bp']>cost,'median_exceeds_cost':s['median_bp']>cost,
                  'breakeven_cost_bp':round(s['mean_bp'],4) if s['mean_bp']>0 else None,
                  'payoff_shape_flag': bool(s['mean_bp']>0 and (s['median_bp']<=0 or s['win_rate']<0.30))})
        out['classes'][cls]=s
    syms=[]
    for (cls,sym),vals in bysym.items():
        if len(vals)<30: continue
        s=stats(vals); cost=COST_BP.get(cls,12.07)
        s.update({'asset_class':cls,'symbol':sym,'cost_bp':cost,
                  'verdict':verdict(s['mean_bp'],cost),
                  'mean_exceeds_cost':s['mean_bp']>cost,'median_exceeds_cost':s['median_bp']>cost})
        syms.append(s)
    out['symbols']=sorted(syms,key=lambda x:(-x['n'],x['asset_class'],x['symbol']))
    json.dump(out,open('42_HARVEST_UPGRADE_2026-11-24/tracker/COST_GATE_BY_CLASS.json','w'),indent=1)
    print(json.dumps({'counts':counts,'classes':{k:{x:v[x] for x in ('n','mean_bp','median_bp','cost_bp','verdict','mean_exceeds_cost','median_exceeds_cost','breakeven_cost_bp','win_rate','payoff_shape_flag')} for k,v in out['classes'].items()},'symbols_ge30':len(syms)},indent=1))

if __name__=='__main__': main()
