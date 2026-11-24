# Backtest — does any of this actually work?

**Run:** 2026-11-24 · **Data:** `docs/data/harvest_signals.json` (71 symbols, up to 4 monthly periods each)
+ Tiingo adjusted daily prices · **Method:** forward return from one monthly consensus snapshot to the next.

> ## ⚠️ TWO CORRECTIONS TO THE READING OF THIS DOCUMENT, added later the same day
>
> **1. These numbers are RAW return, not excess return — they are not comparable to kilocode's
> backtest and theirs is the better design.** They measure excess vs SPY with a 6.7122 bp cost,
> next-trading-close entry, and explicit 21d/63d horizons. Raw return over a rising market makes
> every label look positive, which is exactly what the table below shows. Defer to
> `kilocode/HARVEST_BACKTEST.md`; this file stands only as the raw-return counterpart.
>
> **2. The permutation test I planned could never run.** Tiingo is still returning HTTP 429
> ("hourly request allocation") and this run never persisted its 138 observations, so the vector
> is unrecoverable. `monte_carlo.py` now caches prices and persists observations so this cannot
> recur, but the loss here is real. The substitute test lives in
> `mc_on_published_aggregates.py` → `out/mc_published_aggregates.json` and is summarised at the
> bottom of this file. It is weaker (normal approximation on aggregates, not a permutation test)
> and is labelled as such.

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

---

## Substitute significance test — on kilocode's published aggregates

**Script:** `mc_on_published_aggregates.py` · **Output:** `out/mc_published_aggregates.json`
**Why substitute:** the permutation test needs the raw `(label, return)` vector. Tiingo is still
HTTP 429; this run lost its own vector; `docs/data/harvest_backtest.json` stores aggregates only
(n, mean, ci95, median, hit_rate) — no per-observation values. So the raw vector does not exist
anywhere and a true permutation test is not possible today. This is the best available check, and
it is weaker: it assumes normality and reconstructs SD from the published 95% CI.

**Step 0 — do their numbers reconcile with their own per-period rows?**
Yes, exactly. Recomputing STRONG_BUY/21d from the four `strong_buy_basket` periods gives
mean `+1.325029` and hit `0.545455`, matching the published values to `|Δ| = 0.00e+00`. The
aggregates are internally consistent, so they are safe to test.

**Step 1 — is STRONG_BUY distinguishable from everything else?**

| horizon | STRONG_BUY | rest | delta | SE | z | p (two-sided) | n/arm for 80% power |
|---|---|---|---:|---:|---:|---:|---:|
| 21d | n=110, +1.325% | n=174, +0.781% | +0.544 pp | 1.070 | +0.508 | **0.611** | **4,493** |
| 63d | n=55, +0.003% | n=85, −1.527% | +1.530 pp | 2.066 | +0.741 | **0.459** | **1,035** |

Neither horizon is close to significance. Note the 63d delta looks large only because BUY is
catastrophically negative there (−2.369%, n=56) — that is the rest dragging the mean down, not
STRONG_BUY adding value.

**Step 2 — monotonicity fails at both horizons.**
21d inversions: STRONG_BUY < SELL, BUY < HOLD, BUY < SELL, HOLD < SELL.
63d inversions: STRONG_BUY < HOLD, BUY < HOLD.
SELL n=4 (21d) and n=2 (63d) is unusable for inference, but BUY < HOLD at both horizons is
measured on n=117/53 and 56/29 — that one is real and destroys any ordinal reading of the labels.

**Step 3 — the verdict, stated at the precision the data supports.**
- Detecting the 21d effect needs ~4,493 observations per arm. The study has 110 vs 174 across
  4 monthly periods on 71 symbols. **The design cannot resolve the effect it is looking for.**
- "No edge found" is the correct reading. "No edge exists" is **not** supported, and
  "small edge" is not supported either. A null result from an underpowered design is
  uninformative, not reassuring.
- Consumption rule: never publish a STRONG_BUY premium from this design in either direction.
