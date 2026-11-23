# EQUITY cost: the repo's model is wrong by ~30x, and HML may be unrunnable (2026-11-23)

Found by GitHub Copilot while working the instruction "measure EQUITY cost on our universe,
point-in-time, net of the Questrade schedule".

## 1. The Questrade model applies FX conversion per trade

`forex_fee_pct = 0.017%` (1.75%) is applied on **every trade**. FX conversion is a one-off spread when
converting currency, not a per-trade charge. Applied per trade it makes every US equity trade cost
**175 bp** - which would swamp any equity strategy and silently kill every equity conclusion drawn from
that model.

## 2. The other cost inputs are guesses, not measurements

`spread_bps = 5` and `slippage_bps = 10` are hardcoded. They are labelled as costs but were never
measured on our data, so any "net of costs" equity result using them is net of an assumption.

## 3. HML needs data the repo does not have

HML requires **book equity** and **market equity** (shares outstanding x price). Measured state of the
store:

| Item | Finding |
|---|---|
| `data/earnings/c7/` | **4 quarterly EPS records**, that is all |
| Book value | **absent** |
| Shares outstanding | **absent** |
| Cached price history | 79 daily bar files, 2021-11 to 2026-11 |
| Tingo API key | present (40 chars) - daily bars can be fetched |

So the honest status of the VALUE test is: **pre-registered but blocked**. The rule is frozen; two of
its three inputs do not exist yet. Order of work when unblocked: measure EQUITY cost -> build a
point-in-time universe -> declare the borrow assumption -> run once against the frozen rule.

## Why this matters more than a strategy result

Every "net of costs" number in this programme inherits its cost model. A 30x error in one input is not a
tuning detail; it is the difference between an investable class and a refuted one. The same class of
defect already produced the fabricated 41.05 bp ETF round trip and the doubled cost ladder.
