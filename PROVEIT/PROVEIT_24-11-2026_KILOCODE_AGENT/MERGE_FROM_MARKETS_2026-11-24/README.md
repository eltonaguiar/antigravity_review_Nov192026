# PROVEIT — scenario portfolios, endorsements, and whether the philosophy survives

**Generated:** 2026-11-24T0322Z · **Window:** 2021-11-15 .. 2026-11-13 (1255 trading days)

> Paper research. **Not investment advice.** One bull-heavy window, one rate cycle.

## Fees actually charged (stated, not hidden)

| cost | value |
|---|---|
| commission per order | $0.00 (discount broker) |
| spread / slippage | 5.0bp round-turn on every traded notional |
| fund MER | SPY 0.0945%, TLT 0.15%, GLD 0.40%, BIL 0.136% — charged daily |
| fractional shares | **not available** (whole shares only) |

## THE finding: at small sizes the philosophy is irrelevant

A single SPY share cost **$374.84** at simulation start. That fact dominates:

| start | SPY shares buyable at 60% | idle cash at end | best CAGR |
|---|---:|---:|---:|
| $300 | 0 | 72.3% | +0.00% |
| $500 | 0 | 66.4% | +11.88% |
| $2,000 | 3 | 4.4% | +9.29% |
| $10,000 | 16 | 0.0% | +10.49% |

At $300 the account cannot buy one share of the S&P 500. 72% of the money sits in cash and the 5-year result is **-0.92%/yr** — not because the market did badly (SPY went 437 → 754) but because **the position was never expressible**. No strategy choice fixes this; instrument choice does.

## Endorsement by scenario

| portfolio | endorse | why |
|---:|---|---|
| **$300** | A broad low-cost ETF with a low share price, **or** a fractional-share broker. Not a 60/40 of SPY/TLT. | whole-share math leaves 72% idle; the 60/40 cannot be built |
| **$500** | Same — one SPY share at most, 66% idle | still cannot build the intended mix |
| **$2,000** | 60/40 SPY/TLT becomes buildable | buy-and-hold 8.70%/yr, maxDD -13.5% |
| **$10,000** | 60/40 or a simple 3-fund; cost no longer binding | buy-and-hold 9.18%/yr, fees 0.05% of capital |

## Does any trading philosophy beat holding?

| start | strategy | final | CAGR | maxDD | trades | fees+spread |
|---:|---|---:|---:|---:|---:|---:|
| $300 | buy_hold | $286.50 | -0.92% | -6.98% | 1 | $0.05 |
| $300 | annual_rebalance | $286.17 | -0.94% | -6.98% | 5 | $0.21 |
| $300 | tp_sl | $270.72 | -2.04% | -20.71% | 9 | $0.96 |
| $300 | trend_200 | $300.00 | +0.00% | 0.00% | 0 | $0.00 |
| $500 | buy_hold | $473.01 | -1.11% | -8.37% | 1 | $0.09 |
| $500 | annual_rebalance | $472.35 | -1.14% | -8.38% | 5 | $0.42 |
| $500 | tp_sl | $874.65 | +11.88% | -15.43% | 18 | $2.92 |
| $500 | trend_200 | $785.15 | +9.48% | -8.94% | 19 | $4.26 |
| $2,000 | buy_hold | $3,030.04 | +8.70% | -13.51% | 2 | $0.93 |
| $2,000 | annual_rebalance | $2,694.31 | +6.17% | -12.18% | 10 | $4.85 |
| $2,000 | tp_sl | $3,009.49 | +8.55% | -13.75% | 16 | $8.83 |
| $2,000 | trend_200 | $3,112.91 | +9.29% | -9.03% | 19 | $18.93 |
| $10,000 | buy_hold | $15,489.06 | +9.18% | -14.20% | 2 | $4.99 |
| $10,000 | annual_rebalance | $14,346.23 | +7.52% | -12.21% | 10 | $27.26 |
| $10,000 | tp_sl | $15,053.19 | +8.56% | -13.80% | 16 | $44.61 |
| $10,000 | trend_200 | $16,435.17 | +10.49% | -10.09% | 19 | $101.36 |

### Reading it honestly

1. **At $10,000 — the only size where the comparison is clean** — buy-and-hold returns **9.18%/yr**; annual rebalancing 7.52%; TP/SL 8.56%; 200-day trend timing 10.49%. The timing variant wins by ~1.3pp.
2. **That trend win is almost certainly an artefact.** The 1000-cell sweep tested this same family across five asset classes and 47 measured cells: **0 PASS**, and every candidate that looked good failed walk-forward. A single-window win here is the same artefact.
3. **TP/SL costs more than it earns**: 16 trades and $44.61 of cost at $10,000 for a result 0.6pp *below* doing nothing.
4. **Rebalancing lost to buy-and-hold** — consistent with the fund deep-dive, where rebalancing kept buying a falling bond sleeve.

## So is the philosophy powerful?

**No — and the question was malformed.** No trading rule here beat simply holding a broad index, and the ones that appeared to were single-window artefacts that fail out-of-sample. What actually moved the outcome was not a philosophy:

- **account size** (72% idle at $300 vs 0% at $10,000)
- **instrument choice** (a $374 share price vs a $50 one)
- **cost** (26bp round-turn against a gross edge of +3 to +5bp)

The leverage is in those three, not in entry rules.

## What would change this answer

- Execution ~**5x** cheaper than assumed: the COST-problem classes' +3 to +5bp gross edge would then survive
- A signal with a materially larger gross edge per trade
- Out-of-sample confirmation of SOL breakout (pre-registered, 3/3 in-sample folds, 0/30 forward trades)

## Reproduction

```
python3 proveit_sim.py --out-dir .
python3 proveit_sim.py --commission 9.99   # legacy broker
```

Every number above is generated from the timestamped `sim_*.json` in this folder.

## Error log (kept deliberately)

1. The first engine passed a slice of cash into `buy()` and assigned the remainder back to the whole balance, deleting the rest. It produced a $300 buy-and-hold ending at $72 with 100% idle cash — nonsense that looked like a finding. Caught before publishing; that dump was deleted.
2. The first README generator called `json.loads(<filename>)` instead of reading the file. Failed loudly rather than emitting an empty document.
