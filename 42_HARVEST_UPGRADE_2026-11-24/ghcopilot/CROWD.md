# Crowd layer — method and limits

**Code:** `crowd_layer.py` · **Output:** `out/crowd_layer.json` · **Run:** 2026-11-24

## What returned

| venue | endpoint | status | rows |
|---|---|---|---|
| Polymarket Gamma | `gamma-api.polymarket.com/markets?limit=200&closed=false&active=true` | `HTTP 200` | 100 |
| Kalshi public | `api.elections.kalshi.com/trade-api/v2/markets?limit=200&status=open` | `HTTP 200` | 200 |

Captured per market: `market_id`, `question`, `implied_prob`, `bid`, `ask`, `spread`, `volume`,
`liquidity`, `open_interest`, `end_date`, `url`.
Note per venue: Polymarket Gamma does not expose open interest on this endpoint (`null`, not 0).
Kalshi quotes in cents, so `implied_prob` is the bid/ask mid divided by 100; when a market has no
two-sided quote `implied_prob` is `null` rather than guessed.

## The two-layer model

### Layer A — direct per-symbol matches

A market that names a specific ticker or company. Every row carries the venue `market_id` and a
`match_confidence` of `exact | ticker_mention | semantic`.

**Result: 0 matches out of 300 markets.**

That zero is the finding, and it took a correction to reach honestly. The first implementation
matched on lowercased substrings and produced four matches — **all four false positives**: the
ticker `DE` (Deere) inside the Spanish preposition of tennis market titles
(`"yes Luis Carlos Alvarez Valdes, yes Luciano ..."`). Matching is now a case-sensitive uppercase
token boundary test, plus exact company-name match for names of 8+ characters.

A representative Kalshi market returned this run: `"Xi Jinping out before 2027?"`. Prediction
markets price **events**, not equity endorsements. Anyone building a per-symbol "crowd consensus"
column from these two venues will be inventing a mapping.

### Layer B — explicit event-to-asset mapping

Five mappings, each carrying `mechanism`, `expected_sign`, `confidence`, and `beta`:

| event family | mapped class | transmission |
|---|---|---|
| Fed policy rate path | BOND (TLT/IEF/SHY) | expected front-end path → discount rate → duration-scaled price |
| CPI / inflation surprise | BOND (TLT/TIP/GLD) | expected policy path + inflation risk premium → nominal yields; TIPS via breakeven; gold via real rates |
| Recession probability | EQUITY_FACTOR (SPY vs XLP) | equity risk premium + earnings path; defensives have lower earnings beta |
| Bitcoin price threshold | CRYPTO (BTC-USD) | same underlying — a repricing, not a leading indicator |
| Equity index level | EQUITY (SPY) | definitional identity; scenario distribution only |

**Mechanism is enforced in code.** `layer_b_rejected_missing_mechanism` lists any row lacking one;
it is empty this run. A bare correlation is never emitted.

**Beta is `null` on all five**, each with a `beta_status` reason. The estimator is specified in
`ANALYST_SCORECARD_SPEC.md` §2; it needs ≥250 overlapping daily observations of implied probability
vs excess return, and we hold no such series. Filling these cells with a cross-sectional correlation
between unrelated series would be the exact failure this design exists to prevent.

## Limits

1. **One snapshot, no history.** A single implied probability is not a signal; the *change* is. This
   run captures a snapshot only. A second run tomorrow begins a usable series.
2. **Liquidity is not normalised.** A 95% implied probability on $200 of volume means nothing. The
   `liquidity`/`volume` fields are captured so a caller can gate on them, and no gate is applied by
   default.
3. **Thin markets mislead.** Spread is captured for this reason; a wide spread on an "implied
   probability" is a wide uncertainty band, not a precise forecast.
4. **No jurisdiction, no resolution-criteria parsing.** Where a contract resolves on an ambiguous
   source, the implied probability inherits that ambiguity.
5. **Layer B confidences are judgements, not measurements.** `high`/`medium` reflect how direct the
   transmission is, and are stated so a reader can discount them.

## Reproduce

```bash
python3 crowd_layer.py --feed ../../docs/data/harvest_signals.json
```

Two serial requests, 1.1 s apart, no pagination. Writes only to `./out/`.
