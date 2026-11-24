
---

# Extended scenarios — $10K / $20K / $50K (2026-11-24T0350Z)

Source: `sim_2026-11-24T0350Z.json` and `paramscan_2026-11-24T0350Z.json`

## Provenance and conventions (read before quoting any number)

- **Window:** `2021-11-15 -> 2026-11-13`, 1255 trading bars. The JSON field `n_days: 1255` is **trading days**, not calendar days — `1255 / 252 = 4.98` years. Reading it as calendar days yields 3.44 years and a 13.58% CAGR instead of 9.18%, a 4.40pp error. Divides by 252, never by 365.
- **Entry bar:** the simulation skips the first 200 bars as a 200-day-SMA warm-up, so all strategies enter at **bar 200 = 2022-09-01**. On that bar the closes were SPY **$374.84**, TLT **$92.83**, GLD $157.87, BIL $76.38. SPY is verifiable against this folder's own data: row 200 of `data/market_prices.csv` reads `2022-09-01, SPY_adj=374.8433837890625`, and the file has exactly 1255 rows, which is the `n_days` value in the sim artifact. The window's first-bar SPY close ($437.19, SPY_adj) is *not* the entry price.
- **`idle_cash_pct` is cash as a share of ENDING nav,** not of starting capital. At $300 the account ends holding $207.12 cash against a $286.50 nav = 72.3%; measured against the $300 it started with, that is 69.0%. Both are true; the field reports the former.
- **Fee model:** $0 commission, 5bp round-turn spread on traded notional, daily MER drag (SPY 0.0945%, TLT 0.15%, GLD 0.40%, BIL 0.136%), **no fractional shares**.

## Buy-and-hold converges: above ~$10K, size stops mattering

| start | final | CAGR | maxDD | fees+spread | size effect |
|---:|---:|---:|---:|---:|---|
| $300 | $286.50 | -0.92% | -6.98% | $0.05 | granularity binds |
| $500 | $473.01 | -1.11% | -8.37% | $0.09 | granularity binds |
| $2,000 | $3,030.04 | +8.70% | -13.51% | $0.93 | granularity binds |
| $10,000 | $15,489.06 | +9.18% | -14.20% | $4.99 | granularity stops binding |
| $20,000 | $30,978.12 | +9.18% | -14.20% | $9.99 | granularity stops binding |
| $50,000 | $77,445.30 | +9.18% | -14.20% | $24.97 | granularity stops binding |

**The $10K, $20K and $50K rows return the identical 9.18%.** That is the cleanest result in this study: once whole-share granularity stops binding, account size becomes irrelevant to the return — the same portfolio is simply scaled. Every size-dependent effect lives below $10K.

## Does a bigger account make a strategy work?

| start | hold CAGR | best variant | best CAGR | edge | variants |
|---:|---:|---|---:|---:|---:|
| $300 | -0.92% | trend_200 | +0.00% | +0.92pp | 4 |
| $500 | -1.11% | tp_sl | +11.88% | +12.99pp | 4 |
| $2,000 | +8.70% | trend_200 | +9.29% | +0.59pp | 4 |
| $10,000 | +9.18% | trend_200 | +10.49% | +1.31pp | 4 |
| $20,000 | +9.18% | trend_200 | +10.60% | +1.42pp | 4 |
| $50,000 | +9.18% | trend_200 | +10.68% | +1.50pp | 4 |

The 200-day trend edge creeps up with size (+1.31 / +1.42 / +1.50pp) but stays inside the noise band, and it is the same rule family the 1000-cell sweep killed across five asset classes — **0 PASS in 47 cells, every candidate failed walk-forward**. A larger account does not fix a rule that has no out-of-sample edge; it only makes the same artefact cost more.

**The most flattering row in this table is not in the trend family, and it is disclosed here rather than omitted:** at **$500 the TP/SL variant returns +11.88% against a −1.11% hold, an edge of +12.99pp** — an order of magnitude larger than any trend edge quoted above. It is not evidence. It rests on 18 trades inside a $500 account where one TLT share is 19% of the portfolio, so share granularity, not rule quality, drives the result; the same variant at $2K, $10K, $20K and $50K underperforms holding (see below). A rule that only works when the position size is small enough to be noisy is measuring noise.

## Costs scale linearly, which is the one size-dependent effect that persists

TP/SL costs $44.61 at $10K, $90.23 at $20K and $226.80 at $50K having paid 16 trades at each size, and returns **8.56% / 9.02% / 9.05%** against a 9.18% hold.

| start | TP/SL cost | TP/SL CAGR | hold CAGR | difference |
|---:|---:|---:|---:|---:|
| $10,000 | $44.61 | **8.56%** | 9.18% | **−0.62pp** |
| $20,000 | $90.23 | 9.02% | 9.18% | −0.16pp |
| $50,000 | $226.80 | 9.05% | 9.18% | −0.13pp |

**All three are below holding.** The $10,000 row is the one that matters, because it is the size most accounts actually have, and there the active overlay gives up 0.62pp a year for the privilege of trading 16 times. No confidence interval was computed and none is claimed: this is a single path over one window, so the honest reading is "no demonstrated benefit at any size", not "statistically indistinguishable from holding". **Trading activity scales with capital while its edge does not.**

## Verdict across all six sizes

No account size produces an investable edge. The recommendations are unchanged from the main README: at $300–$500 the constraint is instrument choice, not strategy; from ~$2K the 60/40 becomes expressible; above ~$10K size is irrelevant and only cost and holding discipline matter.
