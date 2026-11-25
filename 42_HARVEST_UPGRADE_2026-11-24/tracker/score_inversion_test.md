# Score inversion test — HOLD vs BUY vs STRONG_BUY

**Owner:** Kilo (Track A cross-check of Track B) · **Date:** 2026-11-24
**Source:** `ZOOCODE/harvest/2026-11-24T1942Z_earnings499.json` (499 tickers) + Yahoo prices
**Reproducer:** this file's numbers are in `score_inversion_test.json`; the event test is described below.

Track B reported HOLD **+2.88%** [1.56, 4.35], BUY **+1.67%** [1.04, 2.34], STRONG_BUY
**+1.28%** [0.06, 2.64] with n=164/579/207. That is decreasing in our own score. I reran the
question independently rather than accepting the bucket table.

## Method (frozen before the run)

- Events: `action` in `{up, down}`, `to` grade mapped through the frozen 1..5 file; dates
  2023-06-01..2026-10-01; deduplicated on symbol-date.
- Entry: **next session open** after the publication date (lag-1, never same close).
- Exit: close **21 trading days** later.
- Benchmark: same-date mean forward net return of other symbols in the **same ADV tercile and
  126-day momentum tercile**. Size proxy is 60-day dollar volume, **not market cap** — see limits.
- Cost: **10 / 30 / 100 bp** round turn by ADV tercile, applied to the event and the control mean.
- CI: **2,000 symbol-cluster bootstrap**; design effect = (cluster SE / iid SE)^2.

## 1. Confound check

| bucket | n | distinct symbols | largest symbol | largest share | median date |
|---|---:|---:|---|---:|---|
| HOLD | 2,617 | 456 | ENPH | **0.9%** | 2025-01-07 |
| BUY | 2,541 | 456 | AMD | **0.8%** | 2025-01-30 |
| STRONG_BUY | 23 | 23 | AMD | **4.3%** | 2025-01-28 |

The HOLD bucket is not 3 symbols and not one date: 456 symbols, 0.9% maximum share, median
2025-01-07. The confound hypothesis does not explain the Track B ordering.

## 2. Benchmark + cost + lag (matched controls, net)

| bucket | n | mean net excess | 95% clustered CI | design effect |
|---|---:|---:|---|---:|
| HOLD | 2,617 | **+0.111%** | [-0.276%, +0.520%] | **1.31** |
| BUY | 2,541 | **+0.242%** | [-0.137%, +0.632%] | **1.36** |
| STRONG_BUY | 23 | **−0.479%** | [-3.758%, +3.685%] | **0.99** |

All three CIs include zero. The ordering is not the same as Track B's (BUY > HOLD >
STRONG_BUY here), and no bucket survives the matched benchmark at 95%.

## 3. Design effect / Track B's 0.38

I **do not reproduce 0.38**. My symbol-cluster design effects are **1.31 (HOLD), 1.36 (BUY),
0.99 (STRONG_BUY)**. A value below 1 is possible with negative intra-cluster correlation but is
not what this event set shows; Track B's t inflation is not reproduced here, so its t statistic
should not be treated as settled.

## 4. Verdict

**UNDERDETERMINED.** The inversion is not confirmed: with lag, cost and a size/momentum-matched
control, no bucket has a CI excluding zero, and the ordering changes. It is also not refuted —
the size proxy is ADV, not market cap, and STRONG_BUY has only n=23.

The one measurement that would settle it: replace the ADV size proxy with a point-in-time market
cap and collect ≥100 STRONG_BUY events, then rerun the same matched benchmark and symbol-cluster
bootstrap.

next_probe: PIT market-cap size matching + ≥100 STRONG_BUY events; same 21d lag, 10/30/100 bp
cost, symbol-cluster CI.

## PAIRWISE DIFFERENCE TESTS 2026-11-25

**Method:** symbol-cluster bootstrap, 5,000 replicates, resampling symbols with replacement from the
union of the two buckets; values are the same per-event net-excess bps used above. CI = 2.5/97.5
percentiles; two-sided p = 2 × min(share of replicates ≤0, share ≥0), capped at 1. This is a difference
test, not an overlap-of-per-bucket-CIs argument.

| comparison | mean difference | 95% cluster CI | p |
|---|---:|---|---:|
| HOLD − BUY | **−13.037 bp** | **[−66.725, +38.706]** | **0.6416** |
| HOLD − STRONG_BUY | **+58.985 bp** | **[−353.643, +407.619]** | **0.7284** |
| BUY − STRONG_BUY | **+72.021 bp** | **[−327.013, +411.686]** | **0.6588** |

Means used: HOLD +11.114 bp (n=2,617), BUY +24.151 bp (n=2,541), STRONG_BUY −47.870 bp (n=23).
These p-values are **my recomputation**; they are not the Track B values 0.099/0.124/0.597, which come
from a different row set and were not copied.

**No pairwise difference CI excludes zero.**

## Counting-basis reconciliation

- **My run:** a bucket row is one **analyst-action event** — an `up`/`down` record reduced to one
  symbol-date event, with the `to` grade mapped to the 1..5 ordinal and a price/control filter. The
  counts **2,617 / 2,541 / 23** are **event counts** (not monthly snapshots). The STRONG_BUY n=23 is
  small because strict `to`-grade Strong Buy events with usable prices are rare.
- **Track B's 963-row set:** a row is a **symbol-period consensus snapshot** (three monthly periods
  per symbol across ~485 symbols, scored from the consensus bucket counts). The buckets
  **164 / 579 / 207** are **snapshot observations**, not individual analyst actions. The 963 is a
  snapshot count, not the same event count as my 2,617/2,541/23, and no multiplier reconciles them.
- Which is the event count: **2,617 / 2,541 / 23 are the event counts in this file.** The 963 is a
  monthly-snapshot observation count; the two cannot be pooled or compared as if they were the same
  unit.

## Verdict

**UNDERDETERMINED — no pairwise difference CI excludes zero.** The bucket ordering BUY > HOLD >
STRONG_BUY is a point ordering only; overlapping per-bucket CIs do not establish it, and the
difference tests above do not either. No upgrade to REAL.
