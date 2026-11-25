# H-260 correct sizing harness

**Pre-registered before the run:** copier equity **$100,000**, equal **1/n** allocation to each
top-decile wallet, **one** stop at **−10%**, stop fill at **−12%** (2% slippage), gap/no-fill when raw
return ≤ **−100%** (loss −100%), cost **26 bp**, **trial count = 1**, one snapshot pair.
Script: `12_INSIDER/h260_correct_sizing.py`; JSON: `h260_correct_sizing.json`.

## Two denominators, side by side

Top decile by prior return: **n=882** of 8,820 eligible.

| denominator | raw mean | raw median | stopped mean | net after 26 bp | stop fills | no-fill gaps |
|---|---:|---:|---:|---:|---:|---:|
| A. wallet PnL / snapshot equity (invalid for a copier) | **−3.7422%** | +8.1135% | **+7.7159%** | **+7.4559%** | 840 | **42** |
| B. wallet PnL / max(equity, wk_vlm/2) — no-leverage proxy | **+4.8451%** | +1.3152% | **+5.0232%** | **+4.7632%** | 881 | **1** |

A is the old denominator: it divides PnL earned on notional running to hundreds of times equity by
snapshot equity. It is invalid for a copier. A −10% stop turns its −3.74% raw mean into +7.46% net;
that sign flip is the artifact warning, not a discovery.

B is a **proxy**, not the correct denominator: `wk_vlm/2` is a weekly-turnover estimate, not position
notional. It has only **1** no-fill gap and +4.76% net, but it cannot be quoted as an edge.

## Correct denominator

The snapshot has **no position notional** and no per-position records, so the committed-capital
denominator a copier can actually replicate is **not measurable**. Verdict: **UNDERDETERMINED /
DATA_INVALID** for the economic translation. The rank signal may be real; the economic number is not.

## Capacity — four names carrying 63% of P supply

ADV = 60-day median Close×Volume from 1-year daily bars (measured 2026-11-25).

| name | ADV USD | 5% ADV cap |
|---|---:|---:|
| PARA | 166,320 | 8,316 |
| UPST | 97,763,710 | 4,888,186 |
| RIVN | 317,422,219 | 15,871,111 |
| LCID | 39,167,434 | 1,958,372 |

Equal 63% allocation across four names = **$15,750** each at $100k. PARA's 5% ADV cap is **$8,316**, so
$100k **breaches capacity**; the max copier equity at 5% ADV across this concentration is about
**$52,800**. Capacity is a binding constraint before returns are.

## Verdict

- **Old denominator:** −3.74% raw, +7.46% with a stop — invalid and stop-dependent.
- **Proxy denominator:** +4.76% net — not admissible; no notional in the snapshot.
- **Correct committed-capital net expectancy:** **not computable / DATA_INVALID**.
- **No edge.** A clean null/underdetermined result is the outcome.

next_probe: obtain per-wallet position notional (or a second snapshot with positions) and rerun the
same fixed-fraction/one-stop harness; until then do not quote an H-260 economic return.
