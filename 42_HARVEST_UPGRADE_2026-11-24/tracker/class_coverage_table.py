#!/usr/bin/env python3
"""Per-class coverage and priced-only returns, live resolvers only (read-only).

Filter: COALESCE(resolver_version,'') NOT LIKE 'backfill%'.
Priced row: pnl_pct is not NULL and != 0.
Credentials: line index 82 of /home/eaguiar2015/dbpasses.txt at runtime.
"""
import json, statistics, collections
import pymysql

def pw():
    return open('/home/eaguiar2015/dbpasses.txt',errors='ignore').read().splitlines()[82].strip()

def main():
    c=pymysql.connect(host='mysql.50webs.com',user='ejaguiar1_stocks',password=pw(),database='ejaguiar1_stocks',connect_timeout=20,charset='utf8mb4')
    cur=c.cursor()
    cur.execute("SELECT asset_class,symbol,pnl_pct,resolver_version,status,resolution_method FROM at_pick_outcomes")
    rows=cur.fetchall(); c.close()
    counts={'raw':len(rows),'backfill_excluded':0,'live':0,'null_resolver':0,'priced':0}
    by=collections.defaultdict(lambda:{'n':0,'priced':0,'vals':[]})
    for ac,sym,pnl,rv,st,rm in rows:
        if (rv or '').lower().startswith('backfill'):
            counts['backfill_excluded']+=1; continue
        if rv is None: counts['null_resolver']+=1
        counts['live']+=1
        cls=(ac or 'BLANK').strip().upper()
        rec=by[cls]; rec['n']+=1
        if pnl is not None and float(pnl)!=0:
            rec['priced']+=1; rec['vals'].append(float(pnl)); counts['priced']+=1
    out={'source':'ejaguiar1_stocks.at_pick_outcomes','filter':"resolver_version NOT LIKE 'backfill%' (NULL included as non-backfill)",'counts':counts,'classes':{}}
    for cls,rec in sorted(by.items(),key=lambda x:(-x[1]['n'],x[0])):
        vals=rec['vals']; n=rec['n']; p=rec['priced']
        out['classes'][cls]={'n':n,'priced':p,'priced_coverage_pct':round(100*p/n,2) if n else None,
            'mean_pct':round(statistics.mean(vals),4) if vals else None,
            'median_pct':round(statistics.median(vals),4) if vals else None,
            'pct_of_all_rows':round(100*n/counts['raw'],2)}
    json.dump(out,open('42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_COVERAGE_TABLE.json','w'),indent=1)
    print(json.dumps(out,indent=1))

if __name__=='__main__': main()
