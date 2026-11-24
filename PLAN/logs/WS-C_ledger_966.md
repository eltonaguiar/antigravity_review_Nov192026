# WS-C — 966-cell ledger: coverage, duplication, and one strategy counted twice

**Date:** 2026-11-24 · **Source:** `.kilo/worktrees/vanilla-handsaw/results/cells/*.json` (966 files, all parsed)
**Read directly with `json.load`. Nothing inherited from a summary.**

## Provenance — this is not one experiment

| property | value |
|---|---|
| cells | 966 |
| distinct `git_sha` | **7**, plus 1 cell with no sha at all |
| distinct `generated_at` | 956 |
| grid declared | 21 symbols × 11 strategies × 6 horizons = **1386** |
| grid present | 966 (**69.7%**) |
| generated | 2026-11-24T01:41Z, sha `43833033a88…` |

Cells per sha: 270 / 269 / 220 / 120 / 70 / 10 / 6 / 1(null).

**The ledger's 966 cells were produced by seven different code versions.** Two cells with
different shas were not measured by the same engine, so a cross-cell comparison silently spans
code changes. Any statement of the form "strategy X beats strategy Y across the grid" assumes a
fixed engine that this ledger does not have.

## Coverage — 88.9% of it is not a measurement

| verdict | cells | share |
|---|---:|---:|
| `BLOCKED_NO_DATA` | 859 | 88.9% |
| `KILLED` | 96 | 9.9% |
| `INSUFFICIENT_TRADES` | 10 | 1.0% |
| no verdict at all | 1 | 0.1% |

Blocked share by horizon:

| horizon | blocked | rate |
|---|---:|---:|
| **15m** | 197/197 | **100%** |
| 1h | 191/200 | 96% |
| 4h | 191/199 | 96% |
| 1d | 125/160 | 78% |
| 1w | 155/200 | 78% |

**Every single 15-minute cell is blocked.** The intraday half of the grid has no data behind it.
Presenting this as a 966-cell sweep is arithmetically true and substantively false: only **78
cells (8.1%)** carry a `net_mean_bp` value at all.

## Duplication — the fingerprint check is *not* evidence of duplication

Grouping by `(verdict, bars, reason)` yields 101 groups of size >1. That is a false positive and
I want it on record as one: 21 DOGE strategies sharing `bars=250` is what you get when 21 rules are
run on one price series. Shared `bars` is a property of the *data*, not of the *computation*.

**0 byte-identical files.** No duplicated artifacts.

## Duplication that is real: `breakout` and `donchian` are the same computation

> **CORRECTED 2026-11-24.** The first version of this section said "pairs compared: 100,
> IDENTICAL stats: 100" and listed CI95/p columns. Those numbers were wrong on two counts, and
> the column values could not have come from this ledger: only **88 of the 966 files carry any
> metric field at all**, and 91 breakout/donchian pairs exist, not 100. Re-derived below with
> the figures the data actually supports.

There are **91** shared `(symbol, horizon)` pairs between `breakout` and `donchian`.

| comparison basis | pairs | identical | differing |
|---|---:|---:|---:|
| pairs carrying metrics (`n`, `net_mean_bp`, `dsr`, `verdict`) | **9** | **9** | 0 |
| pairs compared only on `(verdict, bars, reason)` — no metrics present | 82 | 82 | 0 |

**The 9 metric-bearing pairs are the evidence.** They are real measurements, not empty cells:

| cell | n | net_mean_bp | DSR | verdict | git_sha (breakout vs donchian) |
|---|---:|---:|---:|---|---|
| BTCUSDT/1d | 13 | 128.442 | 0.0181 | KILLED | `9ddb420` vs `4383303` |
| BTCUSDT/1h | 42 | −59.190 | 0.0 | KILLED | `9ddb420` vs `9ddb420` |
| BTCUSDT/4h | 16 | −54.003 | 0.0 | KILLED | `9ddb420` vs `9ddb420` |
| BTCUSDT/1w | 2 | −327.260 | — | KILLED | `9ddb420` vs `4383303` |
| ETHUSDT/1d | 17 | −18.469 | 0.0007 | KILLED | `9ddb420` vs `4383303` |
| ETHUSDT/1w | 2 | 2488.382 | — | KILLED | `9ddb420` vs `4383303` |
| DOGEUSDT/1d | 4 | 225.433 | — | KILLED | `9ddb420` vs `4383303` |
| SOLUSDT/1d | 7 | 66.235 | — | KILLED | `9ddb420` vs `4383303` |
| XRPUSDT/1d | 3 | −235.398 | — | KILLED | `9ddb420` vs `4383303` |

Two strategies agreeing on nine independent symbol/horizon combinations, to six decimal places, on
non-trivial values (n=13, 42, 17, 16, 7, 4, 3, 2), are not two strategies. **7 of the 9 pairs came
from *different* git shas** — different code versions, different runs — and still produced
byte-equal statistics. That is stronger evidence of a shared code path, not weaker.

**The other 82 pairs prove nothing on their own**, and the first version of this section wrongly
counted them as confirmation. Cells that are `BLOCKED_NO_DATA` on the same symbol share `bars` and
`reason` by construction, so 82 identical verdicts is what you would see even if the two strategies
were completely different. This is the same false-positive trap that produced the withdrawn
"182 distinct results" figure — fingerprinting on fields that cannot differ.

**Consequence, still standing:** the grid advertises 11 strategies and delivers **10 effective
ones**. Any multiple-comparison count that used 11 per symbol is inflated, and the DSR's trial
count is correspondingly overstated.

## Two incompatible schemas in one directory

| schema | cells | keys |
|---|---:|---|
| A | 956 | `symbol`, `strategy`, `horizon`, `bars`, `data_file`, `rule`, `verdict`, `git_sha` |
| B | 10 | `cell`, `n`, `net_mean_bp`, `ci95_bp`, `permutation_p`, `dsr`, `reason`, `verdict` |

Schema B has no `horizon` field — it encodes `BTCUSDT/ma_cross/1d` as a single slash-joined `cell`
string. A consumer doing `row["horizon"]` gets `None` on 10 of 966 rows and drops them silently.
No error, no warning. This is the same silent-substitution failure as the 15m-on-daily defect: the
reader cannot tell a missing field from an absent measurement.

## Cells with trades but no measurement

Eight cells record `n > 0` yet carry `net_mean_bp: None` and the verdict `INSUFFICIENT_TRADES`:

```
BTCUSDT/rsi2_pullback/1d   n=21
DOGEUSDT/rsi2_pullback/1d  n=19
ETHUSDT/rsi2_pullback/1d   n=19
XRPUSDT/rsi2_pullback/1d   n=18
SOLUSDT/rsi2_pullback/1d   n=14
BTCUSDT/ma_cross/1d        n=4
ETHUSDT/ma_cross/1d        n=2
XRPUSDT/ma_cross/1d        n=2
```

A cell with 21 trades classified as "insufficient trades" is not a threshold question — the
threshold would have to exceed 21. Either the estimator failed and the failure was recorded as
insufficiency, or the verdict is being computed from a different counter than `n`. Both are
failures to measure, mislabelled as a judgement about the strategy.

## Retraction of my own previous claim

Last turn I reported that `breakout` and `donchian` produce identical statistics, along with
"966 cells / 182 distinct results". **The artifact that claim rested on — `/tmp/cells` — has been
deleted**, so at the time of writing that finding was unverifiable and I should not have stated it
as established. It is now re-derived from the surviving ledger and the specific numbers above are
reproducible from the command below. The "182 distinct results" figure is **withdrawn**: it came
from fingerprinting on `(verdict, bars, reason)`, which the section above shows is a false
positive.

## Reproduce

```bash
python3 - <<'P'
import json, pathlib
D = pathlib.Path('.kilo/worktrees/vanilla-handsaw/results/cells')
recs = {f.stem: json.load(open(f)) for f in sorted(D.glob('*.json'))}
cell = lambda o: o.get('cell') or f"{o['symbol']}/{o['strategy']}/{o['horizon']}"
sig  = lambda o: (o.get('n'), o.get('net_mean_bp'), o.get('permutation_p'),
                  o.get('dsr'), o.get('verdict'))
by = {cell(o): o for o in recs.values()}
same = sum(1 for k,o in by.items()
           if '/breakout/' in k and sig(o) == sig(by.get(k.replace('/breakout/','/donchian/'), {})))
print('breakout==donchian:', same, 'of', sum(1 for k in by if '/breakout/' in k))
P
```
