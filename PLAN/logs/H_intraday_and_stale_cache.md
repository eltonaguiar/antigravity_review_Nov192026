# H — Intraday cells rest on the wrong bars, and 5 KILL verdicts depend on them

**Date:** 2026-11-24 · **Source:** `/tmp/cells/results/cells/*.json` + `/tmp/cells/data/cache/*.csv`, read directly
**Status:** 6 of 149 cells have unsound evidence; **5 of 23 KILL verdicts (21.7%)** depend on it.

## Part 1 — two intraday cells were measured on daily bars

| cell | declared horizon | `bar_source` | bars | n | verdict |
|---|---|---|---:|---:|---|
| `BTCUSDT_rsi2_pullback_15m` | 15m | **`binance:1d`** | 1000 | 3 | `INSUFFICIENT_TRADES` |
| `BTCUSDT_vol_compression_15m` | 15m | **`binance:1d`** | 1000 | 57 | **`KILL`** |

`BTCUSDT_rsi2_pullback_15m` reports **n=3**, identical to its `1d` sibling. That identity is the
signature of the original defect: the "15-minute" cell is the daily cell wearing a different name.

`BTCUSDT_vol_compression_15m` is worse than mislabelled. It returned **KILL** on n=57 bars that were
daily. **A strategy was demoted using a measurement of a horizon it was never tested on.**

## Part 2 — my own claim about this was false

I had recorded, in repository memory and in `PLAN/DEFECT_CLASSES.md`:

> Guard: intraday requests return `bars=0` rather than falling back to daily.

**That is not true.** It was true of the code path I patched and false as a statement about the
ledger. The distinction matters: I verified the fix in one place and then wrote a claim about all
cells. That is the same error pattern as the artefacts I have been auditing — a correct observation
generalised one step too far, then quoted as a guarantee.

Corrected in both places. The replacement guard is a **test**, not a convention.

## Part 3 — the 1h cells rest on a 261-day-stale single-window cache

All six `_1h` cells use one file: `data/cache/BTCUSDT_3mo_1h.csv`.

```
Price,Close,High,Low,Open,Volume          <-- header row 1
Ticker,BTC-USD,BTC-USD,BTC-USD,...        <-- header row 2  (ticker says BTC-USD, file named BTCUSDT)
Datetime,,,,,                             <-- header row 3
2025-12-08 01:00:00+00:00,90906.87,...    <-- first data row
...
2026-03-08 01:00:00+00:00,67250.53,...    <-- last data row
```

| property | value |
|---|---|
| window | 2025-12-08 → 2026-03-08 (**90 days**) |
| ledger date | 2026-11-24 |
| **staleness** | **261 days (8.6 months) of 1h history missing** |
| comparability | daily cells use 1000×1d = **2.7 years**; these use 2161×1h = **90 days** |

Four cells return KILL from it:

| cell | n | verdict |
|---|---:|---|
| `BTCUSDT_momentum_12_1_1h` | 557 | **KILL** |
| `BTCUSDT_vwap_reversion_1h` | 321 | **KILL** |
| `BTCUSDT_bb_meanrev_1h` | 128 | **KILL** |
| `BTCUSDT_donchian_1h` | 63 | **KILL** |

The two-header-row defect *was* handled — `bar_source` records `(2161 bars, 2 header rows skipped)`,
which is good provenance practice. What was never asked is **what period the file covers**. A
strategy killed on 90 days of data ending 8.6 months ago is being compared against strategies
measured over 2.7 years ending now.

`momentum_12_1` is especially exposed: a 12-month-minus-1-month momentum rule evaluated on a 90-day
window cannot contain a 12-month lookback at all. Its KILL is not evidence about that rule.

## Blast radius

| | count |
|---|---:|
| cells with unsound bar provenance | 6 |
| of which carry KILL | 5 |
| total KILLs in ledger | 23 |
| **share of KILLs resting on unsound evidence** | **21.7%** |

Of the 23 strategies killed across this sweep, **five were killed by data that was the wrong
resolution or 8.6 months out of date.** The direction of that error is systematically toward
false kills: shorter windows and stale regimes both raise variance and depress measured edge.

## What this does *not* say

It does not say the five strategies are alive. It says their kills are **not established** and must
be re-measured or downgraded to `BLOCKED_NO_DATA` before anyone cites them. Re-measuring
`momentum_12_1_1h` needs 13+ months of 1h bars, which this repo does not have — so the honest
verdict there is `BLOCKED_NO_DATA`, not `KILL`.

## Reproduce

```bash
cd /tmp/cells
python3 - <<'P'
import json, pathlib, re
for f in sorted(pathlib.Path('results/cells').glob('*.json')):
    o = json.load(open(f)); src = str(o.get('bar_source',''))
    m = re.search(r'_(15m|1h|4h|1d|1w)$', f.stem)
    if m and m.group(1) in ('15m','1h','4h') and not re.search(r'(15m|1h|4h|min|hour)', src):
        print('MISLABELLED', f.stem, src, o.get('n'), o.get('verdict'))
    if 'cache:' in src:
        print('CACHE', f.stem, src, o.get('n'), o.get('verdict'))
P
```
