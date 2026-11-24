# Backtest — does any of this actually work?

**Run:** 2026-11-24 · **Data:** `docs/data/harvest_signals.json` (71 symbols, up to 4 monthly periods each)
+ Tiingo adjusted daily prices · **Method:** forward return from one monthly consensus snapshot to the next.

## What was tested

For every symbol with ≥2 monthly consensus periods, take the label at period `t`, measure the
adjusted-price return from period `t` to period `t+1`, and bucket the results by that label. This is
the cheapest honest test of whether the consensus labels carry forward information.

- Symbols with price data: 46 of 71 (25 returned no prices from Tiingo in the window).
- Observations: **138** (one symbol-contribution per consecutive period pair).
- Window: 2026-08 → 2026-11. Periods are month-start, so ~1-month forward returns.
- No transaction costs applied. No benchmark adjustment. Both would make the result *worse*.

## Result — no edge, and the ordering is inverted

| label at start of period | n | mean | median | hit rate (>0) | vs base (mean) |
|---|---:|---:|---:|---:|---:|
| STRONG_BUY | 58 | +1.16% | **−0.62%** | 47% | **−0.18 pp** |
| BUY | 51 | +1.56% | **−0.85%** | 45% | +0.22 pp |
| HOLD | 29 | +1.32% | **+0.23%** | 52% | −0.03 pp |
| **BASE RATE (all)** | **138** | **+1.34%** | — | — | — |

Three findings, in order of how much they matter:

1. **STRONG_BUY underperformed its own base rate** (−0.18 pp) and had a **negative median** (−0.62%).
   The mean is dragged up by a few winners while the typical name fell.
2. **Monotonicity fails.** On median return the ordering is HOLD (+0.23%) > STRONG_BUY (−0.62%) >
   BUY (−0.85%). If the label meant anything, Strong Buy should beat Hold. It does not.
3. **Hit rates are below 50% for both buy buckets** (47% and 45%), while HOLD is the only bucket
   above coin-flip (52%). A consensus that is more "buy" does not produce more up-months.

**Verdict: not viable on this sample.** The harvest consensus, as currently scored, has no
demonstrated forward value, and the strongest bucket is the weakest performer.

## Why this result should not be over-read either

A null result on 138 overlapping observations is weak evidence *against* the signal, not proof it is
worthless. Limits, stated so nobody cites this table out of context:

- **n is small.** 46 symbols × ~3 non-overlapping periods. Per-bucket n is 29–58.
- **Overlapping windows.** Consecutive period pairs on one symbol share a month, so the effective
  sample is smaller than 138.
- **One regime.** Aug–Nov 2026 only. A single three-month window cannot distinguish "no edge" from
  "no edge *in this window*".
- **Survivorship.** Only the 71 currently-covered names; no delisted or dropped-coverage symbols.
- **No costs.** Adding ~26 bp round-turn would push every bucket negative.
- **Not benchmark-relative.** Some of the +1.34% base is just the market. Against SPY over the same
  window the excess may be negative for all buckets.

## What would change the answer

The test that matters is the one this table cannot do yet: **a forward-scored scorecard**, where
snapshots are archived going forward and scored after the horizon elapses, benchmark-relative, with
costs, and with the `breakeven_wr = 1/(1+payoff_ratio)` gate applied per bucket. That requires
snapshots that were committed *before* the outcome was known — which is why archiving starts now
rather than being reconstructed later.

Until that exists, the honest statement on the page is: **consensus labels are descriptive, not
predictive, and no forward edge has been demonstrated.**

## Also not backtestable from what we hold

- **Fund look-through** (`fund_lookthrough`): the derived value is a current-snapshot aggregate with
  no history. Without past holdings snapshots there is no series to score. Coverage is 60.07% / 65.46%
  / 54.98% of fund weight anyway, so even a series would describe a minority of each fund.
- **Crowd markets** (`crowd_markets`): one snapshot, no resolutions. Scoring implied probability needs
  realised outcomes; Brier score and calibration are impossible from a single capture.
- **Analyst track record**: blocked at the source — no dated firm-attributed event feed
  (finnhub upgrade-downgrade 403, price-target 403, fmp 429).

Reproduce the consensus test with the script embedded in this session's run: Finnhub
`/stock/recommendation` for 4 periods × Tiingo `/tiingo/daily/<t>/prices`, joined on the first trading
day on or after each period date.
