> SUPERSEDED 2026-11-25 -- canonical copy is tracker/class_calibration.md (mde_pct 8.78 pp/yr, benchmark gate 2 UNMET); this file is retained as the 2026-11-24 original.

# Track B -- per-asset-class calibration

zoo-savant, 2026-11-24. Source: `ZOOCODE/harvest/*.json` (499 tickers) + yfinance, seed 20261124.

**Method:** `score = (2*SB + B - S - 2*SS)/n` against forward **net** return
(stock - SPY - cost), entry after the publication lag, 26 bp replaced by a
liquidity-bucketed charge (see cost model). Permutation null shuffles scores
within symbol; CIs bootstrap by symbol.

## Cost model (liquidity-bucketed, not flat)

| coverage band | cost | basis | rows |
|---|---|---|---|
| deep (n_analysts >= 30) | 6.71 bp | ETF/index measured round turn | 152 |
| normal (n_analysts >= 10) | 12.07 bp | equity measured round turn | 784 |
| thin (n_analysts >= 0) | 52.0 bp | crypto measured round turn (widest on record) | 27 |

The bp figures are measured cost-of-record values. **The mapping from analyst
coverage to a cost band is an assumption**, since coverage is only a proxy for liquidity.

## Per-class results

| class | n | symbols | rho | perm p | sign | design effect | MDE | verdict |
|---|---|---|---|---|---|---|---|---|
| EQUITY | 963 | 485 | -0.0467 | 0.9995 | inverted | 0.38 | 8.78% | inverted |
| ETF | 0 | 0 | -- | -- | -- | -- | -- | insufficient |
| BOND | 0 | 0 | -- | -- | -- | -- | -- | insufficient |
| MUTUAL_FUND | 0 | 0 | -- | -- | -- | -- | -- | insufficient |
| CRYPTO | 0 | 0 | -- | -- | -- | -- | -- | insufficient |
| COMMODITY_FUTURES_FOREX | 0 | 0 | -- | -- | -- | -- | -- | insufficient |

Reasons for each `insufficient`:

- **ETF**: probed 14 ETFs: the consensus source returned an empty array -- no analyst coverage for the instrument type
- **BOND**: probed 6 bond funds: empty array -- no analyst coverage
- **MUTUAL_FUND**: probed 6 mutual funds: HTTP 403 -- a data-plan limit, so NOT an absence of coverage
- **CRYPTO**: probed 2 crypto pairs: empty array -- no analyst coverage
- **COMMODITY_FUTURES_FOREX**: no analyst consensus source exists; the appropriate signals are CFTC COT / funding rates, not ratings

## Bucket table -- EQUITY (n=963)

| bucket | n | mean net % | 95% CI (by symbol) | CI excludes zero |
|---|---|---|---|---|
| STRONG_BUY | 207 | +1.2818 | [+0.062, +2.638] | True |
| BUY | 579 | +1.6708 | [+1.038, +2.342] | True |
| HOLD | 164 | +2.8798 | [+1.561, +4.351] | True |
| SELL | 13 | -0.5222 | [-6.707, +3.996] | False |

**Sign is inverted**, monotone across buckets: **False**.

## Rules applied

- `insufficient` is used where n < 100; nothing was pooled across classes to reach the floor.
- An inverted sign is reported as **inverted**, not relabelled.
- Every null carries its MDE so it is quantified, not asserted.

next_probe: extend the class census beyond the documented probes by resolving each symbol's instrument type from an authoritative listing file, so ETF/BOND/FUND rows are identified rather than inferred from a probe -- the current limit is that neither source carries an asset-class field.

**Matched-benchmark re-baseline (2026-11-25): the INVERTED sign SURVIVES** -- SPY rho -0.04673 (p 0.9995) vs beta/size/momentum-matched rho -0.04400 (p 0.9945, n=945). The matched benchmark does not rescue monotonicity: STRONG_BUY 1.2818 < BUY 1.6708 < HOLD 2.8798 still holds, so gate 2 is met on the benchmark question but the ordering remains inverted.
