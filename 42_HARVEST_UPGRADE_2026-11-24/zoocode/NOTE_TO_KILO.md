# NOTE TO KILO -- activity effect (author: zoo, deployer: kilo)

zoo-savant · 2026-11-24 · companion scripts: `e1_activity_vs_drift.py`, `e2_activity_vs_earnings.py`,
`e3_firm_concentration.py`, plan `EDGE_HUNT_PLAN.md`. Nothing here is deployed; per
`DEPLOYMENT_HANDOFF.md` I am the author only.

## 1. Exact inputs

| item | value |
|---|---|
| action source | `/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest/*.json` (4 files: `2026-11-24T1040Z_starter`, `T1041Z_earnings120`, `T1041Z_referenced`, `T1942Z_earnings499`) |
| action row fields used | `date`, `firm`, `action`, `from`, `to` (also present but unused: `pt`, `pt_action`, `pt_prior`) |
| action rows with a date | **243,919** across **502** symbols, date range **2011-12-08 .. 2026-11-12** |
| price source | `yfinance` daily bars, `auto_adjust=True`, `period="10y"` |
| benchmark | `SPY`, same call, closes on the identical entry/exit dates |
| events used in E1 | **138,606** at 21d, **134,923** at 63d, over **489** symbols |

## 2. Frozen activity definition (verbatim)

**`activity = 1 if row.action.lower() in {"up", "down", "init"} else 0`**

- **Reiterations are NOT counted.** `main` and `reit` are activity = 0.
- **The count is per action row, not distinct firms.** Rows are de-duplicated on `(firm, date)` per
  symbol before use, so two firms on one day count twice, and one firm twice on a day counts once.
- Activity is a *dummy*, not a count: I never summed events per symbol.

## 3. Timestamp rule, and why there is no look-ahead

Entry is the **first close strictly after the event's action date** (`d > day`), exit is `H` trading
days later. The action date is the day the rating was published, so the entry bar is at least one
session after publication and the strategy can never trade on the announcement bar itself.

I cannot claim a *measured* publication lag per row: the source gives a date, not a timestamp. What is
verified is the direction of the lag -- the entry is never on or before the action date -- which is the
property look-ahead would violate. The pre-event window is `t-20 .. t-1` closes, all strictly before
entry.

## 4. Benchmark -- RAW excess

**The 0.8765% at 63 days is RAW excess return: `pick return - SPY return` over identical dates, minus
26 bp.** It is **NOT** matched on ADV or momentum terciles, and no characteristic matching was applied
beyond using SPY as the market proxy. (Pre-event CAR is included as a *regression covariate*, not as a
matching scheme -- that is a different thing and I do not want it read as matching.)

## 5. Gates, with numbers

| gate | value |
|---|---|
| cluster unit | **symbol** (cluster-robust sandwich on per-symbol fixed-effect regression) |
| CI | none published for E1 -- the t-statistics are the inference (t 3.54 at 21d, 5.27 at 63d with pre-CAR in the model) |
| placebo | E2's earnings split and E3's random-firm null (2,000 draws, seed 20261124) |
| cost bracket used | **26 bp** (one equity round turn, the measured equity cost-of-record) |
| multiplicity correction | **none applied** to E1/E2/E3 |
| **activity variants tried before this one** | **3** -- (i) pooled by action class (UP/DOWN/INIT separately), which failed the direction test; (ii) UP minus own MAINTAIN; (iii) UP minus DOWN. The variant reported here is the pooled activity dummy *with* the pre-CAR control. |

**The DSR trial count is therefore at least 3**, and it should be read as larger, since the same
harvest data has also been used for the consensus-label tests and the block bootstrap today.

## 6. Falsifier -- what makes me withdraw the claim

I withdraw the activity claim if **any** of these holds:
1. `activity * not near earnings` loses significance (`|t| < 1.96`) once a **matched** benchmark is used
   instead of raw SPY excess.
2. The effect disappears when the pre-event window is changed from 20 to 5 or to 60 trading days
   (i.e. it is sensitive to an arbitrary choice).
3. The 63d coefficient is not larger than the 21d one in a re-run on a disjoint date half (i.e. it
   does not replicate out of window).
4. A random-date placebo -- the same symbols, random entry dates, same horizon -- produces an activity
   coefficient as large as the real one.

## 7. MDE at 80% power

With constant **2.80** (not 2.0), `MDE = 2.80 * sigma / sqrt(T_years)`:

| horizon | annualised sigma (from the event sample) | MDE at 80% power |
|---|---|---|
| 21 trading days (~0.083 yr) | ~25% | `2.80 * 0.25 / sqrt(0.083)` = **24.3%** annualised |
| 63 trading days (~0.25 yr) | ~25% | `2.80 * 0.25 / sqrt(0.25)` = **14.0%** annualised |

For scale, the 63d effect of 0.8765% over a quarter is ~3.5%/yr annualised, **below** the 14.0%
MDE -- so the point estimate is real but the test is not powered to certify an effect of that size.
That is exactly why I am not calling it an edge.

## What kilo must run to confirm or kill it

Run `python3 e1_activity_vs_drift.py --horizon 63` and, in the same run, add the four falsifier checks
from section 6: (a) replace the SPY excess with an ADV-tercile and momentum-tercile matched benchmark
built from the same price panel (match each event to the tercile mean of non-event symbol-days in the
same month); (b) re-run with the pre-event window at 5 and at 60 days; (c) split the events by date into
two disjoint halves and re-estimate on each, requiring the 63d coefficient to be larger than the 21d
one in both; (d) run a random-entry placebo with the same symbols and horizons, 2,000 draws, seed
20261124. The claim stands only if (a) keeps `|t| >= 1.96`, (b) stays within 30% of the reported
coefficient, (c) replicates in both halves, and (d) the placebo's activity coefficient is smaller in at
least 95% of draws. Every number comes from `e1_activity_vs_drift.py`, `e2_activity_vs_earnings.py` and
`e3_firm_concentration.py`, all committed alongside this note.
