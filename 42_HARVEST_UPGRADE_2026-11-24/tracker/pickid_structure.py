#!/usr/bin/env python3
"""pickid_structure.py - pick_id carries the date, so EXPIRED rows ARE recoverable.

pick_id samples: '::DYDX-USD::2026-06-05'  '::NEAR-USD::2026-06-01'
So every row knows its own symbol and pick date. The 'no dates' conclusion was
wrong and the 'unrecoverable' conclusion was wrong with it.

This measures: format consistency, where the prices live, and how much of the
29,654 EXPIRED pile is actually resolvable.
"""
import os
from collections import Counter

import pymysql

PW = [l.strip() for l in open(os.path.expanduser("~/dbpasses.txt"), encoding="utf-8",
                              errors="replace").read().splitlines()][82]
c = pymysql.connect(host="mysql.50webs.com", user="ejaguiar1_stocks", password=PW,
                    database="ejaguiar1_stocks", connect_timeout=30)
cur = c.cursor()

print("=" * 78)
print("1. pick_id FORMAT CONSISTENCY")
print("=" * 78)
cur.execute("SELECT pick_id, status FROM at_pick_outcomes")
rows = cur.fetchall()
ok = bad = 0
syms = set()
dates = []
for pid, st in rows:
    parts = (pid or "").split("::")
    if len(parts) == 3 and parts[2][:4].isdigit():
        ok += 1
        syms.add(parts[1])
        dates.append(parts[2])
    else:
        bad += 1
print(f"  parseable ::SYM::DATE  {ok:,} of {len(rows):,} ({100*ok/len(rows):.1f}%)")
print(f"  unparseable            {bad:,}")
print(f"  distinct symbols       {len(syms):,}")
if dates:
    print(f"  date range             {min(dates)} .. {max(dates)}")

print("\n" + "=" * 78)
print("2. WHERE COULD PRICES COME FROM?")
print("=" * 78)
cur.execute("""SELECT table_name, table_rows FROM information_schema.tables
               WHERE table_schema=%s AND (table_name LIKE '%%ohlcv%%'
                 OR table_name LIKE '%%price%%' OR table_name LIKE '%%candle%%')
               ORDER BY table_rows DESC LIMIT 12""", ("ejaguiar1_stocks",))
tabs = cur.fetchall()
for t, n in tabs:
    print(f"  {t:<34} est_rows={n}")
    try:
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s",
                    ("ejaguiar1_stocks", t))
        cols = [x[0] for x in cur.fetchall()]
        print(f"      cols: {cols[:9]}")
    except Exception:
        pass

print("\n" + "=" * 78)
print("3. HOW MUCH OF THE EXPIRED PILE IS PRICE-COVERED?")
print("=" * 78)
# sample crypto symbols from the expired pile and test coverage in daily_prices
cur.execute("""SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(pick_id,'::',2),'::',-1) sym, COUNT(*) n
               FROM at_pick_outcomes WHERE status='EXPIRED'
               GROUP BY sym ORDER BY n DESC LIMIT 12""")
top = cur.fetchall()
print("  top expired symbols:", [(s, n) for s, n in top[:12]])

for cand in ("daily_prices", "stock_ohlcv", "equity_daily_ohlcv", "crypto_prices", "crypto_ohlcv"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{cand}`")
        n = cur.fetchone()[0]
        print(f"  {cand:<20} rows={n:,}")
    except Exception:
        continue

# test one join-able coverage: does daily_prices hold any of these symbols?
for sym, _ in top[:6]:
    for cand in ("daily_prices", "stock_ohlcv"):
        try:
            cur.execute(f"SELECT COUNT(*) FROM `{cand}` WHERE ticker=%s" if cand == "daily_prices"
                        else f"SELECT COUNT(*) FROM `{cand}` WHERE symbol=%s", (sym,))
            n = cur.fetchone()[0]
            if n:
                print(f"    {sym:<14} {cand}: {n:,} bars")
        except Exception:
            pass

c.close()
