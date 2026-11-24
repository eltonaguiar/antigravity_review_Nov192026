# Form 4 collection — feasibility results (2026-11-24)

Not a return result. This is the event-supply measurement that decides whether the insider probe can be
run at all, plus one trap found in the data before any price was touched.

## What was collected

`collect_form4.py`, 24 tickers × the 60 most recent Form 4 filings each, mixed caps.

| | |
|---|---:|
| Transaction rows | **2,616** |
| distinct issuers | 24 |
| filing lag, median | **2 business days** |
| filing lag, p95 | **3 business days** |

The lag matters: Form 4 is legally due within 2 business days, and the measured distribution matches.
If p95 had come back at 30 days, the pipeline would be reading a later date than the filing and the
whole probe would be contaminated by look-ahead.

## Rows by transaction code

| Code | Meaning | Rows |
|---|---|---:|
| S | open-market sale (the CONTROL) | **920** |
| A | grant / award | 602 |
| M | option exercise | 506 |
| F | tax withholding | 468 |
| **P** | **open-market purchase (the EVENT)** | **46** |
| G | gift | 32 |
| C | conversion | 20 |
| J | other | 18 |
| X, H, D | misc | 4 |

**Purchases are rare: 1.76% of rows, a P:S ratio of 1:20.** That asymmetry is the hypothesis, not a
problem — but it sets the sample requirement.

## The decisive comparison

| Universe | Rows | P events |
|---|---:|---:|
| 8 mega caps (AAPL, MSFT, NVDA, AMD, CRM, COST, JPM, XOM) | 290 | **0** |
| 24 mixed / small-mid caps | 2,616 | **46** |

Mega-cap insiders **do not buy in the open market** in the recent window — they sell and are granted
stock. The event lives in small and mid caps. Any probe restricted to large caps would have reported
"no events" and wrongly concluded the signal does not exist.

Event depth is adequate: P transactions span **2022-01-11 → 2026-11-19** across 4+ years, at **1.92 P
events per ticker**. Extrapolated to a 500-ticker universe that is **~958 P events** — comfortably above
the 100–200 per bucket needed for a powered test, and roughly an order of magnitude more than the
analyst-upgrade stream ever produced at the same ticker count.

## The trap: the P stream is dominated by 10%-owners, not insiders

Purchase sizes across the 46 events:

| Statistic | Value |
|---|---:|
| median | $250,386 |
| 25th / 75th pct | $9,996 / $1,272,461 |
| mean | $34,786,657 |
| max | **$999,943,400** |

A mean 139× the median is not a fat tail, it is **two different populations mixed together**:

- **Real insider purchases** — roughly $10k to $1.3M, consistent with a person buying stock.
- **Entity block purchases** — RIVN ~$1.0bn over 6 filings, LCID ~$550m over 3. These are strategic and
  sovereign holders filing as 10% owners (a sovereign fund scaling into a position is not an insider
  signalling private information about the next quarter).

Evidence from the ownership flags: only **7 of the 46 P rows carry `isOfficer` or `isDirector` true**
(1 officer, 5 directors, 1 both). The other 39 are entities and 10% owners.

**Consequence for the probe:** filter to `isOfficer == true OR isDirector == true` **before** any return
test. Unfiltered, the event set is ~85% corporate block trades, and a result computed on it would
measure "does a sovereign wealth fund's accumulation predict returns" while being reported as "do
insiders know something". The spec's exclusion of 10% owners is load-bearing, not tidiness.

**Engineering gap now visible:** the collector records the flags but does not yet filter on them, and the
per-owner flags are taken from the first reporting-owner block in a filing that may contain several. A
filing with both an entity owner and an individual officer needs **per-owner** attribution before the
filter is trustworthy. That is the next engineering step, and it is a correctness issue, not a nicety.

## next_probe

1. Fix per-owner attribution: parse each `reportingOwner` block with its own `reportingOwnerId` and
   relationship flags, so an officer's purchase inside a multi-owner filing is not lost and an entity's
   is not counted.
2. Apply the officer/director filter and re-report the P count — expect it to drop materially from 46.
3. Then collect the full 308-ticker universe over the available history and run the frozen gates:
   matched benchmark (ADV × 126-day momentum tercile), 21/63/126-day horizons, cost bracket 0.98/4.01/
   12.07 bp, symbol-cluster CI, date-shift placebo, and the P-vs-S asymmetry test.
4. Report the MDE at 80% power (constant 2.80) beside every cell, and the ADV distribution of the event
   set, since small-cap concentration is the first listed way this could look like an edge without
   being one.
