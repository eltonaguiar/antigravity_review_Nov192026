# Speculative instruments — profitability and risk, measured

**Status:** working record, 2026-11-24. Educational, not advice. Every number below is from a
named artifact in this repo or from the live `/audit` snapshot; classes with no trade history
are marked **NOT TESTABLE**, not given a plausible-looking estimate.

## Why this document exists

Analyst coverage is not the question. The question is whether a class has positive expectancy
after costs, and what its risk of ruin looks like. Those are separate measurements. This page
records both, and records the gaps explicitly.

## 1. Summary

| class | measured sample | profitability | risk | evidence status |
|---|---|---|---|---|
| **Penny stocks** | ledger n=4 | WR 50.0%, **PF 0.1779** | gap/wick and dilution unmeasured (no bar series) | **negative, tiny n** |
| **Options** | no chain/IV history | not computed | max loss structure-dependent; theta/vega; no fills | **NOT TESTABLE** |
| **Meme coins** | ledger n=10; DOGE 250 bars | WR 10.0%, **PF 0.0234**; DOGE 20d mom −1.257%/trade (n=70, WR 31.4%), 5d rev −0.724% (n=142, WR 42.3%) | DOGE ann. vol **89.2%**, max DD **−69.4%**, 250-day return **−43.3%** | **negative** |
| **Commodities** | Monte Carlo n=54 | mean **−2.518%/trade**, permutation **p=0.000** | contract vol 16.9–81.4%; NG max DD **−66.2%**, CL **−39.3%** | **negative** |
| **Futures** | ledger n=68 | WR **31.58%**, **PF 0.6834** | leverage/notional; roll and gap risk; no roll-adjusted test | **negative** |
| **Broad funds/ETFs** | policy comparator | cost **0 bp** (fund), ETF 6.7122 bp; hurdle **4.32%** | market drawdown, no idiosyncratic blow-up | **only positive-expectancy vehicle without an edge** |

No speculative class in this table has a measured positive net expectancy. The passive vehicle
is the only one that does not require an edge; it also has the lowest cost.

## 2. By class

### Penny stocks
- Ledger: n=4, win rate 50.0%, profit factor **0.1779**. PF < 1 with a coin-flip hit rate means
  the average loss is roughly 5.6× the average win — the losses are not small.
- No daily bar cache for these names, so volatility, max drawdown, gap-through-stop and
  dilution events are **unmeasured**. Do not infer them from the PF.
- Verdict: sample too small to rank, direction negative. Any strategy claim here is untested.

### Options
- Snapshot only: SPY ATM IV 16.44% (expected move 0.64%), AAPL ATM IV 21.73% (1.48%).
- No historical chains, no fills, no greeks history → no expectancy, PF, or drawdown can be
  computed. A defined-risk spread caps loss by construction; that is a risk property, not a
  profitability result.
- Verdict: **NOT TESTABLE** with current data. Do not publish an options edge.

### Meme coins
- Ledger: n=10, win rate 10.0%, PF **0.0234** (near-total loss profile).
- DOGE, 250 daily bars (2025-06-29..2026-03-05): annualised vol **89.2%**, total return
  **−43.3%**, max drawdown **−69.4%**.
- Rule probes: 20-day momentum n=70, mean net **−1.257%/trade**, WR 31.4%; 5-day reversal
  n=142, mean net **−0.724%**, WR 42.3%. Both negative after cost.
- Risk: a 69% drawdown needs +226% to recover; position sizing must assume −100% is possible.
- Verdict: negative on every measured rule. Treat as a lottery bucket, not an allocation.

### Commodities
- Monte Carlo (3k resamples, 1% risk): n=54, mean **−2.518%/trade**, permutation p=0.000.
- Contract risk from the rough front-month rank: vol 16.9% (ZS) to 81.4% (NG); max drawdown
  NG **−66.2%**, CL **−39.3%**, ES −18.5%.
- No roll-adjusted strategy backtest; contango/roll cost is not in the trade ledger.
- Verdict: negative as traded here; the volatility is measurable, the edge is not present.

### Futures
- Ledger: n=68, win rate **31.58%**, PF **0.6834**.
- Leverage is the defining risk: margin is a deposit, not the risk. Size from
  `risk$ / (stop distance × tick value)`, and treat notional as the position.
- No roll-adjusted, slippage-inclusive test yet, so the PF is a floor on realised drag rather
  than a complete estimate.
- Verdict: negative; do not scale a losing rule with leverage.

## 3. Risk controls that are measurable

These bound loss; they do not create expectancy. A negative-expectancy rule with good controls
loses more slowly.

1. **Risk per trade:** 0.25–1.0% of capital at the stop, not the position notional.
2. **Size from the stop:** `shares = risk$ / (entry − stop)`; futures:
   `contracts = risk$ / (stop ticks × tick value)`.
3. **Volatility scaling:** halve size when ATR/realised vol doubles; DOGE's 89% vol is not the
   same instrument as SPY's ~12%.
4. **Hard portfolio heat cap:** total open risk ≤ 2–3%; correlated meme coins are one bet.
5. **Drawdown circuit breaker:** stop after a set loss (e.g. 10% of the speculative sleeve),
   not after a feeling.
6. **Liquidity and exit check:** if the exit needs more than a small fraction of daily volume,
   the position is too large regardless of the stop.
7. **Costs before entry:** apply the class round trip (fund 0, bond 0.61, equity bracket
   0.98/4.01/12.07, ETF 6.71, FOREX 7.53, commodity 20, crypto 20–52 bp) and require the
   post-cost edge to clear the 4.32% policy hurdle.

## 4. What would change a verdict

- Penny: a PIT bar series with corporate actions, n≥100 closed trades, dilution events flagged.
- Options: historical chains + fills, IV rank, defined-risk structures, n≥100.
- Meme: PIT on-chain liquidity and holder concentration, fees/MEV included, n≥100 per rule.
- Commodities/futures: roll-adjusted continuous contracts, slippage, n≥100 per rule.
- All: report mean net, CI, PF, max DD, and the 4.32% hurdle comparison together.

Until then the record is: **none proven, several measured negative, passive funds are the only
zero-edge positive-expectancy comparator.**

## Provenance

- Ledger verdicts: `docs/data/speculative_snapshot.json` (`ledger_verdicts`).
- Meme bars: same file, `meme.DOGE` (250 bars, 2025-06-29..2026-03-05).
- Options snapshot: same file, `options`.
- Futures vol/DD: same file, `futures_rough_rank`.
- Commodity MC: live `/audit` dashboard audit, 2026-11-24 (n=54, −2.518%, p=0.000).
- Costs: `README.md` "Cost of record"; equity bracket per
  `37_BUFFY_DRAFT_PATCHES_2026-11-23/03_equity_cost_settlement.md`.
