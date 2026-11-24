# Addendum — two errors of my own, retracted

**Date:** 2026-11-24 · Corrections to `ZOOCODE_ASKANYMODEL_REVIEW.md` and
`cost_of_hurdle.py`, raised by an independent arena.ai cross-check
(deepseek-v4.1-flash-high, gpt-6.1-terra-low, Claude Opus 5.5, Kimi K2.7, Qwen3.8 Max).

Script: `meme_gap_and_inversion.py` → `out/meme_gap_and_inversion.json`

Two of the criticisms are correct and both are mine. I committed, in a review accusing
someone else of inconsistent number-picking, the same error.

---

## E1. The "ETF-vs-equity inversion" is retracted — it was inconsistent point selection

I published: *"at 1-day turnover equity needs 14.4% gross but ETF needs 21.2%, because ETF
point cost (6.71) exceeds equity central (4.01) — so 'ETF is cheaper than stock' is false."*

That grades **equity at central** and **ETF at its point**. `03_equity_cost_settlement.md`
requires grading at the **upper end**. Recomputed with every class at its ceiling:

| class | bp (ceiling) | gross needed @ 1d | gross needed @ 1w |
|---|---:|---:|---:|
| fund | 0.0000 | 4.3% | 4.3% |
| bond ETF | 0.6144 | 5.9% | 4.6% |
| ETF | 6.7122 | 21.2% | 7.7% |
| FOREX | 7.5330 | 23.3% | 8.1% |
| **equity** | **12.0749** | **34.7%** | 10.4% |
| commodity | 20.0000 | 54.7% | 14.4% |
| crypto | 52.0000 | 135.4% | 30.5% |

equity @central **14.4% < 21.2%** ETF ← what I published
equity @ceiling **34.7% > 21.2%** ETF ← what our own rule mandates

**The inversion does not hold under the rule the settlement doc sets.** It is an artifact of
mixing a central estimate with a point estimate. The honest statement is the weaker one:
ETF is dearer than equity on central estimates and cheaper on ceiling estimates —
**unresolved until an ETF bracket exists**. It is not a finding in either direction.

## E2. Close-to-close is not a gap measure, and the naive gap test is structurally zero

I published: *"SPY moved >5% on 3/1254 days, so even a 5% stop gets jumped."* Two defects:

1. **A gap is open-vs-previous-close.** A close-to-close move spans the whole session and
   says nothing about whether a stop was jumped. My "floor on gap risk" framing was wrong.
2. When I did implement the correct test on Binance daily bars, it returned **0.00% for every
   symbol including meme coins** — because crypto trades 24/7 with no session break, so
   `open_t ≈ close_{t-1}` and a session gap cannot exist by construction. Measured:
   exact equality in 41.5–57.0% of bars, and no deviation anywhere near 5%.

The binding risk in a continuous market is **intrabar**, so that is what I measured —
999 daily bars per symbol, low-vs-open:

| symbol | low breaks −5% from open | low breaks −20% | broke −5% then closed back above | worst intrabar |
|---|---:|---:|---:|---:|
| WIFUSDT | **42.11%** | 1.01% | **22.91%** | −91.2% |
| BONKUSDT | 39.20% | 1.10% | 20.90% | −78.8% |
| PEPEUSDT | 35.80% | 0.90% | 20.20% | −69.9% |
| FLOKIUSDT | 32.40% | 0.90% | 17.60% | −83.4% |
| DOGEUSDT | 23.90% | 0.50% | 14.50% | −61.8% |
| SHIBUSDT | 21.10% | 0.70% | 13.00% | −43.5% |
| ETHUSDT *(control)* | 15.30% | 0.30% | 9.30% | −25.9% |
| BTCUSDT *(control)* | 6.30% | 0.00% | 4.00% | −16.2% |

The fourth column is the one that matters: **on WIF, 22.9% of days broke a −5% stop and then
closed back above it.** The stop fired and the trade was still right — the wick, not the
direction, cost the position. That is a measured answer to the "stops fail on meme coins"
claim, and it is a different failure mode from the one I originally asserted: not gaps, but
intrabar wick-out, roughly 5.7× BTC's 4.0% rate.

## Claim #4 was overclaimed, and I am narrowing it

I wrote *"meme coins have no analyst coverage — **VERIFIED**."* That was too strong, and
two reviewers caught it independently.

`/stock/recommendation` is Finnhub's **sell-side equity ratings** endpoint. Zero records for
DOGE proves DOGE is not in *that* database — it does not prove no research exists anywhere.
Crypto has coverage (Messari, Kaiko, CoinMetrics, Glassnode, Arkham), just not sell-side
buy/hold consensus. The defensible claim, which is now the only one I make:

> **Zero records in Finnhub's equity-recommendation endpoint for DOGE, SHIB, PEPE, BONK,
> WIF, FLOKI (controls AAPL/COIN/MSTR returned 4 each), and zero meme coins in our own
> `harvest_signals.json` feed (71 US large caps). No conclusion about analyst coverage
> outside that endpoint.**

Also correct: ticker strings collide across asset classes, so a 0 on "WIF" could mean "not an
equity" rather than "no coverage" — the endpoint cannot distinguish those.

## Number reconciliation: 36 vs 40 bp

My table computed crypto at **36.0 bp** (the midpoint of the 20–52 band); my prose said
"40 bp is the crypto band". Both cannot be the measurement. Correct labelling:

- **20 bp** band low · **36 bp** band midpoint (what the table uses) · **52 bp** band high
- **40 bp is zoocode's figure — an external assumption, not a repo measurement**

## Footnotes the cross-check correctly asked for

- **Hurdle = 4.32%** (used but never defined in my review). It is the estate's standing
  opportunity-cost hurdle, not a risk-free rate. Measured cash proxy SGOV CAGR was
  **3.89%/yr** over the same window, so the hurdle is ~0.43pp above cash. **Every
  gross-required figure scales linearly off this constant** — change the hurdle and the
  whole column moves, which is why it must be stated.
- **Turnover convention:** 252/5 = **50.4 round-turns per year** at weekly holding
  (one buy + one sell per turn). If a reader interprets 50.4 as *one-way* trades, all drag
  figures halve. Stated so the table is reproducible.
- **20.16%/yr is of traded notional, not portfolio NAV.** Position size and leverage
  determine the NAV impact. The figure is a cost per unit of turnover, not a portfolio return.

## The criticism I should have made myself

**The measured cost excludes market impact, slippage and MEV.** 36 bp is a spread-type
estimate, consistent with large-cap CEX trading. A meme-coin round turn on a thin DEX is
swap fee ×2 + priority fee ×2 + slippage ×2 + MEV — realistically **100–500 bp**. So the
95% gross-at-1d figure is a floor that applies to large-cap crypto and is **badly optimistic
for meme coins**; the true requirement there is far higher. Any cost table for this estate
needs a `includes_impact: Y/N` column, and today it would read **N** for every row.

## What these corrections change

- The **95% crypto / 54.7% commodity** gross-at-1d figures stand — those were computed at the
  band midpoint and are, if anything, understated for the meme venues.
- The **inversion** is withdrawn.
- The **gap-through-stop** claim is withdrawn and replaced with a measured intrabar wick-out
  rate that is larger and better evidenced than what I originally asserted.
- The **analyst-coverage** claim is narrowed to the endpoint that was actually tested.
