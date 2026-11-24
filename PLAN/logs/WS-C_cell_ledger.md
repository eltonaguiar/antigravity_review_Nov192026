# WS-C — cell ledger state as measured

**Date:** 2026-11-24 · **Source:** `/tmp/cells/results/cells/*.json` (149 files, read directly)
**Not** taken from any summary document — every count below is a `collections.Counter` over the
cell artifacts themselves.

## Counts

| verdict | cells |
|---|---:|
| `INSUFFICIENT_TRADES` | 61 |
| `BLOCKED_NO_DATA` | 38 |
| `KILL` | 23 |
| `INCONCLUSIVE` | 21 |
| `NOT_ROBUST` | 3 |
| `CONSISTENTLY_NEGATIVE` | 2 |
| **`CONSISTENT_SIGN`** | **1** |
| **total** | **149** |

**40.9% of the grid is not measurable at all**: 61 cells cannot reach a trade count and 38 have no bar
data (`bars=0`). Only 50 cells produced a verdict that speaks to sign at all, and of those **one is
positive**.

## Correction to a number I was carrying

Earlier in this programme I quoted the sweep as "**47 measured cells, 0 PASS**". The ledger now holds
**149** cells. The 47 figure was a snapshot taken mid-sweep and repeated afterwards as if it were the
final state — an instance of the exact defect class this programme is auditing: a stale quantity
quoted with present-tense confidence. The correct current statement is **149 cells, 0 PASS,
1 sign-consistent**.

## The one cell that is not dead

```
cell     SOLUSDT/breakout/1d
verdict  CONSISTENT_SIGN
```

This is **the pre-registered forward candidate**. That matters in both directions:

- **In its favour:** the single cell that survives every gate in a 149-cell grid is the one that was
  registered *before* measurement, not the one that looked best afterwards. Selection bias cannot
  explain its position, because its position was fixed in advance.
- **Against drawing any conclusion:** it has **0 of 30 forward trades**. A backtest sign that survives
  149 multiple-comparison corrections is a candidate, not evidence. With 149 cells tested and a 5%
  threshold, ~7 false positives are expected by chance alone; one survivor is *below* the noise floor,
  not above it.

The honest statement: **the sweep found nothing, and the one cell that was pre-registered to be worth
watching is still awaiting its first observation.**

## What is genuinely outstanding

| item | count | note |
|---|---:|---|
| `INSUFFICIENT_TRADES` | 61 | needs longer history or a different horizon; not a code defect |
| `BLOCKED_NO_DATA` | 38 | bar source absent — must be quoted as blocked, never as a null result |

These 99 cells cannot be closed by more compute. 61 need time; 38 need a data source that does not
exist in the repo. Presenting either as "measured and failed" would inflate the denominator and make a
thin result look thorough — the mirror image of the 47-cell error.

## Reproduce

```bash
python3 - <<'PY'
import json, pathlib, collections
c = collections.Counter()
for f in pathlib.Path('results/cells').glob('*.json'):
    c[str(json.load(open(f)).get('verdict'))] += 1
print(dict(c), sum(c.values()))
PY
```
