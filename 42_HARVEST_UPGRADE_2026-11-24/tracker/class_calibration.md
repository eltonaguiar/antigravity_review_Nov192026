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
| EQUITY | 963 | 485 | -0.0467 | 0.9995 | inverted | 0.38 | 18.868% | inverted |
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

> **Correction (2026-11-25):** this verdict is driven by the SELL bucket at
> **n=13**, which is 7.7x below this artifact's own floor of 100. With SELL
> marked `insufficient` and excluded from the ordering, the remaining buckets
> are still NOT monotone (STRONG_BUY +1.2818 < BUY +1.6708 < HOLD +2.8798), so
> the inversion stands -- but it should be read from the buckets that clear the
> floor, not from the 13-row one.

## Defect ledger (2026-11-25) -- three defects, each reproduced or refuted

**1. `design_effect = 0.38` is below 1 and "inflates" t from 4.117 to 6.709 -- REPRODUCED, but the reading is wrong.**
The arithmetic is exact: `(t_raw / t_cluster)^2 = (4.117 / 6.709)^2 = 0.3766`. A design effect
below 1 means clustering *reduced* the variance, and with `n / n_symbols = 963 / 485 = 1.99`
observations per symbol that is plausible rather than impossible: overlapping windows inflate
variance only when the within-symbol correlation is positive *and* there are many observations per
symbol. **What is a defect is the interpretation:** a design effect of 0.38 is an estimate from
485 clusters, not a licence to prefer the larger t. The conservative choice is to quote
`t_cluster` with an interval, and to treat a sub-1 design effect as "no measurable inflation"
rather than as "the clustered test is more powerful". It does **not** change the inverted verdict,
which rests on rho and its permutation p.

**2. `mde_pct = 18.868` as a units error -- REFUTED: the units are consistent.**
`MDE = 2.80 * sigma_symbol_mean / sqrt(n_symbols)` at 80% power gives 18.868% with
`sigma_symbol_mean` ~ 148.5% annualised. That is a *per-symbol mean* dispersion over 485 symbols,
not a per-trade one, so the figure is an annualised percentage and the `%` label is correct. The
real concern is its size: an 18.9%/yr MDE means the test cannot resolve any plausible equity
premium, so the null is uninformative rather than negative -- which the artifact already says by
publishing the MDE beside the null. A units test cannot change the inverted verdict either.

**3. Benchmark SPY fails the characteristic-matched gate -- REPRODUCED; the gate failure is the verdict.**
`class_calibration.json` records `benchmark = "SPY (characteristic-matched on the only available
characteristic: all rows are US equities)"`. Being a US equity is not a match on beta, size, sector
or valuation, none of which were used. **Corrected label: SPY is a single-index market benchmark,
and gate 2 is UNMET.** I have not swapped in a matched benchmark here because a real ADV/momentum
match needs the price panel rebuilt per event, which is the queued follow-up (see `next_probe`);
claiming a swap without running it would be exactly the kind of unmeasured assertion this
correction is about. The benchmark choice affects the magnitude of the bucket means, not the sign
of rho, so the inverted verdict survives the gate failure but the bucket *levels* should not be
quoted until it is fixed.

**Summary:** defect 1 reproduced (interpretation corrected), defect 2 refuted (units consistent,
but the MDE is too large to be informative), defect 3 reproduced (gate 2 unmet, label corrected).
None of the three restores monotonicity or a positive rho.

## Rules applied

- `insufficient` is used where n < 100; nothing was pooled across classes to reach the floor.
- An inverted sign is reported as **inverted**, not relabelled.
- Every null carries its MDE so it is quantified, not asserted.

next_probe: extend the class census beyond the documented probes by resolving each symbol's instrument type from an authoritative listing file, so ETF/BOND/FUND rows are identified rather than inferred from a probe -- the current limit is that neither source carries an asset-class field.
