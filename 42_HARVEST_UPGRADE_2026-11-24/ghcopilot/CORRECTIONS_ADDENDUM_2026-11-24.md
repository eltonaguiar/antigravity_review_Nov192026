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

## E3. The "gross needed" column was linear — and linear understates it

Qwen3.6 Flash raised compounding. The instinct is right, the formula they offered answers a
different question, and settling it **changes my headline number**.

Two questions had been conflated under one column:

- **Q1 — what fraction of capital does cost consume?** $1-(1-c)^N$. This is *smaller* than
  $N \times c$, so **linear overstates** it. Crypto at 1-day: linear 90.7%, compounded 59.7%.
- **Q2 — what gross return do I need to net a fixed hurdle?** Solve
  $((1+g_d)(1-c))^N = 1+h$, giving $g_{ann} = [(1+h)^{1/N}/(1-c)]^N - 1$. This is
  *larger* than $h + N c$, because cost compounds against a growing base.

My published column was `hurdle + N × c` labelled as "gross needed" — i.e. a Q1-shaped
formula used to answer a Q2 question. Recomputed (hurdle 4.32%, 1-day turnover,
`compounded_drag.py` → `out/compounded_drag.json`):

| class | rt bp | published (linear) | correct (compounded) | understated by |
|---|---:|---:|---:|---:|
| fund | 0.00 | 4.3% | 4.3% | — |
| bond ETF | 0.61 | 5.9% | 5.9% | 0.1 pp |
| equity | 4.01 | 14.4% | 15.4% | 1.0 pp |
| ETF | 6.71 | 21.2% | 23.6% | 2.3 pp |
| FOREX | 7.53 | 23.3% | 26.1% | 2.8 pp |
| commodity | 20.00 | 54.7% | **72.8%** | 18.1 pp |
| crypto | 36.00 | 95.0% | **158.9%** | 63.8 pp |

**The headline was 95.0% for crypto; it is 158.9%.** The conclusion strengthens rather than
weakens: at daily turnover, crypto does not merely need an implausible edge, it needs a
gross return above anything this estate has ever measured. Commodity moves the same way.

So Qwen's direction was right for Q2 and wrong for Q1, where they wrote that compounded drag
"exceeds 95%" — $N c$ is an upper bound on $1-(1-c)^N$, so it cannot. Both statements are
true once the questions are separated, which is why the column needed splitting rather than
patching.

## E4. Hurdle provenance — resolved, and not an inconsistency

The cross-check asked whether 4.32% contradicts the measured SGOV CAGR of 3.89%. It does not;
they are different quantities:

- **4.32%** = `tools/capacity_model.py` → `HURDLE_TBILL_APR`, labelled **MEASURED**, consumed
  at `PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT_SIGNALS/sim/proveit.py:44`. A T-bill APR.
- **3.89%** = realised **SGOV CAGR** over 2021-11-15 → 2026-11-13. A 5-year average.

Sensitivity checked, because every "gross needed" figure scales off it: moving the hurdle
4.32% → 3.89% shifts the 1-day crypto requirement by only **1.1 pp** (158.9% → 157.8%) and
equity/ETF by 0.5 pp. The compounding cost dominates, so **no verdict changes**. The hurdle
choice only matters in the low-cost rows.

## What these corrections change

- **The gross-at-1d figures do NOT stand.** They were linear. Corrected: crypto **158.9%**
  (not 95.0%), commodity **72.8%** (not 54.7%), ETF 23.6%, FOREX 26.1%, equity 15.4%.
  The "scalping is foreclosed" conclusion is stronger, not weaker.
- The **inversion** is withdrawn.
- The **gap-through-stop** claim is withdrawn and replaced with a measured intrabar wick-out
  rate that is larger and better evidenced than what I originally asserted.
- The **analyst-coverage** claim is narrowed to the endpoint that was actually tested.
- The **"10.1×"** was 9.98× — reported to one significant figure as **~10×**.

## Cost stack still not measured — state it, don't estimate it

Beyond impact/slippage/MEV (above), the following are absent from every bp figure here and
belong on the "cannot measure yet" list:

- **Taxes.** Short-term gains at daily turnover can exceed the transaction cost outright.
  Jurisdiction-dependent, so unmodellable in this table — but it means every drag figure is an
  understatement for a taxable account.
- **Stop-level fill risk.** A stop on an illiquid name fills far from the stop price; this is a
  cost not in the bp table.
- **Survivorship.** Every series used here is of instruments that still exist.

