#!/usr/bin/env python3
"""Cost-adjusted expectancy on RESOLVED trades only (WON/LOST), read-only.

Excludes EXPIRED and FLAT: they carry no resolved P&L (EXPIRED 28,531/29,654 zeros;
FLAT 1,046/1,046 zeros). Credentials read at runtime from line index 82; never printed.
"""
import json, statistics, collections
import pymysql

COST_BP = {'CRYPTO':36.0,'FOREX':7.53,'COMMODITY':20.0,'EQUITY':4.01,'FUTURES':12.07,
           'INDEX':6.71,'ETF':6.71,'BOND':0.61,'MEME':52.0,'UNKNOWN':12.07,
           'BLANK':12.07,'STOCKS':4.01,'STOCK':4.01,'PENNY':52.0,'PENNYSTOCK':52.0}
COST_BASIS = {
 'CRYPTO':'midpoint of measured 20-52 bp; perp fees/spreads above equity',
 'FOREX':'upper-bound measured','COMMODITY':'assumed 20 bp (not measured)',
 'EQUITY':'central measured bracket; ceiling 12.07 bp is stress',
 'FUTURES':'equity ceiling proxy; no roll-adjusted series',
 'INDEX':'ETF/index measured','ETF':'measured','BOND':'measured',
 'MEME':'widest measured crypto band','UNKNOWN':'equity central proxy',
 'BLANK':'equity central proxy','STOCKS':'equity central','STOCK':'equity central',
 'PENNY':'crypto widest proxy','PENNYSTOCK':'crypto widest proxy'}

def read_pw():
    return open('/home/eaguiar2015/dbpasses.txt',errors='ignore').read().splitlines()[82].strip()

def stats(vals):
    n=len(vals); mean=statistics.mean(vals)*100; med=statistics.median(vals)*100
    wins=[v for v in vals if v>0]; losses=[v for v in vals if v<0]
    return {'n':n,'mean_bp':round(mean,4),'median_bp':round(med,4),
            'win_rate':round(len(wins)/n,4) if n else None,
            'wins':len(wins),'losses':len(losses),
            'avg_win_bp':round(statistics.mean(wins)*100,4) if wins else None,
            'avg_loss_bp':round(statistics.mean(losses)*100,4) if losses else None,
            'min_bp':round(min(vals)*100,4),'max_bp':round(max(vals)*100,4)}

def verdict(mean_bp,cost):
    if mean_bp>cost: return 'CLEARS-COST'
    if mean_bp<=0: return 'FAILS-COST'
    return f'BREAKEVEN-COST-NEEDED {mean_bp:.2f} bp'

def main():
    c=pymysql.connect(host='mysql.50webs.com',user='ejaguiar1_stocks',password=read_pw(),database='ejaguiar1_stocks',connect_timeout=20,charset='utf8mb4')
    cur=c.cursor(); cur.execute("SELECT asset_class, symbol, status, pnl_pct FROM at_pick_outcomes")
    rows=cur.fetchall(); c.close()
    counts={'raw':len(rows),'zeros':sum(1 for r in rows if r[3] is not None and float(r[3])==0),
            'expired':sum(1 for r in rows if r[2]=='EXPIRED'),
            'flat':sum(1 for r in rows if r[2]=='FLAT'),
            'won':sum(1 for r in rows if r[2]=='WON'),
            'lost':sum(1 for r in rows if r[2]=='LOST'),
            'resolved_after_exclusion':0}
    by=collections.defaultdict(list); bysym=collections.defaultdict(list); all_vals=[]
    for ac,sym,st,pnl in rows:
        if st not in ('WON','LOST') or pnl is None: continue
        cls=(ac or 'BLANK').strip().upper()
        if cls not in COST_BP: cls='UNKNOWN'
        v=float(pnl); by[cls].append(v); bysym[(cls,sym)].append(v); all_vals.append(v)
    counts['resolved_after_exclusion']=sum(len(v) for v in by.values())
    out={'source':'ejaguiar1_stocks.at_pick_outcomes','overall':stats(all_vals),
         'filter':'status IN (WON, LOST); EXPIRED and FLAT excluded (no resolved P&L)',
         'counts_before_after':counts,'excluded':counts['expired']+counts['flat'],'cost_bp':COST_BP,'cost_basis':COST_BASIS,
         'cost_note':'per-class cost assumptions unchanged from 71d1733',
         'classes':{},'symbols':[]}
    for cls,vals in sorted(by.items(), key=lambda x:(-len(x[1]),x[0])):
        s=stats(vals); cost=COST_BP.get(cls,12.07)
        s.update({'asset_class':cls,'cost_bp':cost,'powered':s['n']>=100,'verdict':verdict(s['mean_bp'],cost),
                  'mean_exceeds_cost':s['mean_bp']>cost,'median_exceeds_cost':s['median_bp']>cost,
                  'breakeven_cost_bp':round(s['mean_bp'],4) if s['mean_bp']>0 else None,
                  'payoff_shape_flag': bool(s['mean_bp']>0 and (s['median_bp']<=0 or s['win_rate']<0.30))})
        out['classes'][cls]=s
    syms=[]
    for (cls,sym),vals in bysym.items():
        if len(vals)<30: continue
        s=stats(vals); cost=COST_BP.get(cls,12.07)
        s.update({'asset_class':cls,'symbol':sym,'cost_bp':cost,'verdict':verdict(s['mean_bp'],cost),
                  'mean_exceeds_cost':s['mean_bp']>cost,'median_exceeds_cost':s['median_bp']>cost})
        syms.append(s)
    known=['CRYPTO','FOREX','COMMODITY','EQUITY','FUTURES','INDEX','ETF','BOND','MEME','UNKNOWN']
    out['class_level']={'known':len(known),'mean_clear_all':sum(1 for c in known if out['classes'].get(c,{}).get('mean_exceeds_cost')),'median_clear_all':sum(1 for c in known if out['classes'].get(c,{}).get('median_exceeds_cost')),'mean_clear_powered':sum(1 for c in known if out['classes'].get(c,{}).get('mean_exceeds_cost') and out['classes'].get(c,{}).get('powered'))}
    out['symbols']=sorted(syms,key=lambda x:(-x['n'],x['asset_class'],x['symbol']))
    json.dump(out,open('42_HARVEST_UPGRADE_2026-11-24/tracker/COST_GATE_BY_CLASS.json','w'),indent=1)
    print(json.dumps({'counts':counts,'classes':{k:{x:v[x] for x in ('n','mean_bp','median_bp','cost_bp','verdict','mean_exceeds_cost','median_exceeds_cost','breakeven_cost_bp','win_rate','payoff_shape_flag')} for k,v in out['classes'].items()},'symbols_ge30':len(syms)},indent=1))

if __name__=='__main__': main()
