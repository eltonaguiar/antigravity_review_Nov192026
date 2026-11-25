#!/usr/bin/env python3
"""Recompute RESOLVE_FAILED_MAX_RETRIES from entry/exit prices (read-only).

The resolver left pnl_pct=0 on 1,664 rows that already carry entry_price and
exit_price. This computes direction-aware return; no table writes.
Credentials: line index 82 of /home/eaguiar2015/dbpasses.txt, read at runtime.
"""
import json, statistics
import pymysql

def pw():
    return open('/home/eaguiar2015/dbpasses.txt', errors='ignore').read().splitlines()[82].strip()

def main():
    c = pymysql.connect(host='mysql.50webs.com', user='ejaguiar1_stocks',
                        password=pw(), database='ejaguiar1_stocks',
                        connect_timeout=20, charset='utf8mb4')
    cur = c.cursor()
    cur.execute("""SELECT id,symbol,direction,entry_price,exit_price,pnl_pct,status
                   FROM trading_picks WHERE exit_reason='RESOLVE_FAILED_MAX_RETRIES'""")
    rows = cur.fetchall()
    c.close()
    out = []
    skipped = []
    for rid, sym, direction, entry, exitp, oldpnl, status in rows:
        try:
            e = float(entry) if entry is not None else None
            x = float(exitp) if exitp is not None else None
        except Exception:
            e = x = None
        if not e or e <= 0 or x is None:
            skipped.append((rid, sym, direction, entry, exitp))
            continue
        d = (direction or '').strip().lower()
        if d in ('short', 'sell', 's'):
            pnl = (e - x) / e * 100.0
        else:
            pnl = (x / e - 1.0) * 100.0
        out.append({'id': rid, 'symbol': sym, 'direction': direction,
                    'entry': e, 'exit': x, 'old_pnl': float(oldpnl) if oldpnl is not None else None,
                    'recomputed_pnl_pct': pnl, 'status': status})
    vals = [r['recomputed_pnl_pct'] for r in out]
    summary = {
        'rows_found': len(rows),
        'recomputed': len(out),
        'skipped_missing_price': len(skipped),
        'mean_pct': round(statistics.mean(vals), 4) if vals else None,
        'median_pct': round(statistics.median(vals), 4) if vals else None,
        'profitable': sum(1 for v in vals if v > 0),
        'zero': sum(1 for v in vals if v == 0),
        'losing': sum(1 for v in vals if v < 0),
        'min_pct': round(min(vals), 4) if vals else None,
        'max_pct': round(max(vals), 4) if vals else None,
        'exit_equals_entry': sum(1 for r in out if r['exit'] == r['entry']),
        'exit_zero': sum(1 for r in out if r['exit'] == 0),
        'directions': {d: sum(1 for r in out if (r['direction'] or '').strip().lower() == d)
                       for d in sorted({(r['direction'] or '').strip().lower() for r in out})},
    }
    json.dump({'summary': summary, 'rows': out, 'skipped': skipped},
              open('42_HARVEST_UPGRADE_2026-11-24/tracker/RESOLVE_FAILED_RECOMPUTE.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
