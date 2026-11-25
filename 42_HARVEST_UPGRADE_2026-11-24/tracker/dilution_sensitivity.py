import pymysql,statistics,collections,json
lines=open('/home/eaguiar2015/dbpasses.txt',errors='ignore').read().splitlines()
c=pymysql.connect(host='mysql.50webs.com',user='ejaguiar1_stocks',password=lines[82].strip(),database='ejaguiar1_stocks',connect_timeout=20,charset='utf8mb4')
cur=c.cursor(); cur.execute("SELECT asset_class,pnl_pct,status,resolver_version FROM at_pick_outcomes")
rows=cur.fetchall(); c.close()
by=collections.defaultdict(list)
for ac,pnl,st,rv in rows:
    cls=(ac or 'BLANK').strip().upper(); by[cls].append(float(pnl) if pnl is not None else None)
out={}
for cls,vals in by.items():
    nonnull=[v for v in vals if v is not None]
    priced=[v for v in nonnull if v!=0]
    pub=statistics.mean(nonnull) if nonnull else None
    share=len(priced)/len(nonnull) if nonnull else None
    implied=(pub/share) if (pub is not None and share) else None
    out[cls]={'n':len(nonnull),'priced':len(priced),'priced_share':round(share,4) if share is not None else None,
              'published_mean_pct':round(pub,4) if pub is not None else None,
              'implied_mean_pct':round(implied,4) if implied is not None else None,
              'label':'BOUND ON DISTORTION, not corrected estimate'}
json.dump(out,open('/tmp/dilution.json','w'),indent=1)
print(json.dumps(out,indent=1))
