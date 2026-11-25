#!/usr/bin/env python3
"""H-260 fixed-fraction copier sizing harness.

Pre-registered before looking at the result:
  copier equity        = $100,000
  allocation           = equal fraction 1/n of equity to each top-decile wallet
  stop                 = -10% position return, filled at -12% (2% slippage)
  gap/no-fill          = raw wallet return <= -100% cannot be stopped; loss = -100%
  trial count          = 1 stop level only
  horizons             = one snapshot pair (no replication)

Two denominators are printed:
  A. wallet PnL / wallet snapshot equity  (the old number; invalid for a copier)
  B. wallet PnL / max(wallet equity, wk_vlm/2) (no-leverage notional proxy)

Neither is the true committed-capital denominator: the snapshot has no position
notional. If B is the only available proxy, the economic verdict is
UNDERDETERMINED/DATA_INVALID, not an edge.
"""
import glob, json, math, statistics as st, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '42_HARVEST_UPGRADE_2026-11-24/tracker'))
from input_assertions import (DataInvalid, denominator_coverage, guarded,
                              require_denominator, bucket_status)

SNAP = sorted(glob.glob('/home/eaguiar2015/findtorontoevents_antigravity.ca/reports/hl_leaderboard_snapshot_*.json'))[-1]
E = 100_000.0
STOP = -0.10
SLIP = 0.02
COST = 0.0026
TRIAL_COUNT = 1

def stop_fill(x):
    """Return (filled_return, filled?)."""
    if x <= -1.0:
        return -1.0, False          # gap through equity: no stop fill
    if x < STOP:
        return STOP - SLIP, True    # stop fills with slippage
    return x, True

def stats(vals):
    filled = [stop_fill(x) for x in vals]
    stopped = [v for v, _ in filled]
    return {
        'n': len(vals),
        'raw_mean_pct': round(100 * st.mean(vals), 4),
        'raw_median_pct': round(100 * st.median(vals), 4),
        'stopped_mean_pct': round(100 * st.mean(stopped), 4),
        'stopped_net26bp_pct': round(100 * (st.mean(stopped) - COST), 4),
        'stop_fills': sum(1 for _, ok in filled if ok),
        'no_fill_gaps': sum(1 for _, ok in filled if not ok),
        'loss_below_stop': sum(1 for x in vals if x < STOP),
        'loss_below_100pct': sum(1 for x in vals if x <= -1.0),
    }

def main():
    snap = json.load(open(SNAP))
    rows = [r for r in snap['rows']
            if (r.get('acct') or 0) >= 10000 and (r.get('wk_vlm') or 0) > 0 and (r.get('mo_vlm') or 0) > 0]
    require_denominator('H260 copier equity', 'copier equity E', E)
    denominator_coverage('H260 acct', rows, 'acct', max_missing=0.10)
    denominator_coverage('H260 wk_vlm', rows, 'wk_vlm', max_missing=0.10)
    b = bucket_status('H260 top-decile', len(rows) // 10, floor=100)
    if b.status != 'OK':
        raise DataInvalid('H260 top-decile', b.reason)
    rows.sort(key=lambda r: r['prior'] / r['acct'], reverse=True)
    top = rows[:len(rows) // 10]
    denom_a = [r['future'] / r['acct'] for r in top]
    denom_b = [r['future'] / max(r['acct'], r['wk_vlm'] / 2.0) for r in top]

    # Capacity inputs measured 2026-11-25 from 1y daily bars, 60d median
    # Close*Volume (USD); source command is in the accompanying report.
    adv = {'PARA': 166320, 'UPST': 97763710, 'RIVN': 317422219, 'LCID': 39167434}
    cap = {s: {'adv_usd': a, 'max_5pct_adv_usd': round(0.05 * a)} for s, a in adv.items()}
    # equal allocation of 63% of E across the four names
    alloc_each = 0.63 * E / 4.0
    cap['equal_alloc_each_usd'] = round(alloc_each)
    cap['max_copier_equity_5pct_adv_usd'] = round(min(0.05 * a / (0.63 / 4.0) for a in adv.values()))

    out = {
        'snapshot': SNAP,
        'eligible': len(rows),
        'top_decile_n': len(top),
        'copier_equity': E,
        'allocation': 'equal 1/n of copier equity per top-decile wallet',
        'stop': STOP,
        'slippage': SLIP,
        'trial_count': TRIAL_COUNT,
        'cost': COST,
        'denominator_A_snapshot_equity': stats(denom_a),
        'denominator_B_notional_proxy': stats(denom_b),
        'capacity_top4': cap,
        'event_supply_share_top4': '63% (33/52 owner-rows; 46 distinct P transactions)',
        'verdict': 'UNDERDETERMINED',
        'reason': 'The snapshot has no position notional. A is invalid for a leveraged wallet; B uses wk_vlm/2 as a no-leverage proxy. Neither is the committed-capital denominator a copier can replicate. Do not quote a net edge from B.',
    }
    Path('12_INSIDER/h260_correct_sizing.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    raise SystemExit(main())
