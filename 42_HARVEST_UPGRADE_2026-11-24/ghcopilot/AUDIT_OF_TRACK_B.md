# Audit of Track B — `zoocode/class_calibration.md`

**Auditor:** ghcopilot (Track C) · **Date:** 2026-11-24
**Artifact audited:** `42_HARVEST_UPGRADE_2026-11-24/zoocode/class_calibration.md` (57 lines, origin)
**Checked against:** `zoocode/class_calibration.json` (its own output; `generated 2026-11-24T21:05:58Z`)

Per the cross-check protocol I answer the five counts, and I name what I checked so that "clean"
where I say clean is a finding rather than silence. I did not edit Track B's artifact.

---

## The five counts

| # | question | count |
|---|---|---:|
| 1 | rows present vs rows claimed | **1 discrepancy** (504 excluded rows never disclosed) |
| 2 | rows failing schema / blank required fields | **unverifiable** (cited input absent from the repo) |
| 3 | figures in the markdown not matching the JSON it cites | **1 mismatch** of 21 checked |
| 4 | bucket below its own stated floor yet given a verdict | **1** (SELL, n=13, floor 100) |
| 5 | significance claim without a CI or placebo reference | **1** (bucket ordering; the rho claim is properly backed) |

> **Status update, 2026-11-25:** counts **1** and **2** are **superseded**. The provenance gap that
> count 2 named has been closed in the repo — see **§8 PROVENANCE GAP CLOSED 2026-11-25** at the foot
> of this file. The original counts remain below, unedited, as the record of what was true on
> 2026-11-24. Counts **3**, **4** and **5** are unaffected.

---

## 1. Rows present vs rows claimed — 1 discrepancy

Every internal total reconciles:

| quantity | markdown | JSON | agrees |
|---|---:|---:|---|
| EQUITY n | 963 | 963 | yes |
| bucket n sum (207+579+164+13) | 963 | 963 | yes |
| cost-band rows (152+784+27) | 963 | 963 | yes |
| symbols | 485 | 485 | yes |
| per-class rows | 6 classes | 6 classes | yes |

**The discrepancy is an omission.** `class_calibration.json` carries `excluded_rows = 504`. Total
rows attempted = 963 + 504 = **1,467**, so **34.4% of rows were dropped** and the markdown never
mentions it, nor says what the exclusion rule was. A reader sees n=963 and has no way to know a
third of the sample is missing. That is a rows-present-vs-claimed defect even though the arithmetic
is right.

## 2. Schema / blank required fields — UNVERIFIABLE, and this is the serious one

The markdown's stated input is `ZOOCODE/harvest/*.json` (499 tickers). **That path does not exist in
the repo.** Measured: `git ls-tree -r origin/main -- ZOOCODE` returns exactly **one** file,
`ZOOCODE/COPILOT20261124T1043Z.MD`; there is no `ZOOCODE/harvest/` directory on origin, and the path
is not gitignored either.

`class_calibration.json` holds **aggregates only** — no row-level records — so even the JSON cannot
support a per-row schema check. Therefore count 2 is **unverifiable**, not zero-failures. The
upstream chain cannot be reproduced from the repo at all; only the final aggregate can be inspected.
This is the same provenance gap as a page citing a hash that nothing reproduces, and I would treat
it as the highest-priority fix in this artifact.

## 3. Markdown figures vs the JSON it cites — 1 mismatch in 21

Verified individually, all matching: n=963 · n_symbols=485 · rho −0.04673 · permutation_p 0.9995 ·
sign inverted · monotone False · design_effect 0.38 · mde_pct 18.868 · STRONG_BUY 207/+1.2818
[0.0619, 2.6378] · BUY 579/+1.6708 [1.0377, 2.3423] · HOLD 164/+2.8798 [1.5612, 4.3512] · SELL
13/−0.5222 [−6.7069, 3.9964] · cost bands 6.71/12.07/52.0 bp · band rows 152/784/27 · the five
`insufficient` reasons.

Internal consistency also holds: `design_effect 0.38` = `(t_raw/t_cluster)²` = (4.117/6.709)² =
**0.3766** ✓.

**The mismatch:** the markdown's header says **"499 tickers"**; the JSON's only symbol count is
**485**. The gap of 14 is unexplained, and plausible reconstructions do not close it (485 covered +
28 probed non-equity = 513 ≠ 499). Either the header figure comes from a different run or it is
stale — either way it is a number in the markdown that its own JSON does not support.

## 4. Bucket below its own floor but still given a verdict — 1

The artifact states its floor explicitly: `class_floor = 100`, and "`insufficient` is used where
n < 100". **SELL has n = 13** — 7.7× below that floor — yet it is reported with a mean and a CI in
the same table as the qualifying buckets, and it participates in the headline verdict
("monotone across buckets: **False**"). The most bearish bucket scoring negative is precisely what
creates the non-monotonicity. So a below-floor bucket is load-bearing for a verdict. Either SELL
should be marked `insufficient` inside the bucket table, or the monotonicity verdict should state
that it depends on a 13-row bucket.

## 5. Significance without CI or placebo — 1

- **Supported:** the rho claim. `permutation_p = 0.9995` is a placebo (2,000 within-symbol shuffles)
  and the direction of the deviation is the finding, not the p-value's smallness. That is done right.
- **Not supported:** the *ordering*. The verdict "inverted" rests on HOLD (+2.8798) > BUY (+1.6708) >
  STRONG_BUY (+1.2818), but the reported CIs **overlap pairwise** — STRONG_BUY [0.062, 2.638] and BUY
  [1.038, 2.342] overlap across almost their whole width. No CI is given for any *difference*
  between adjacent buckets, so the bucket ordering is asserted from separate per-bucket intervals,
  which cannot establish an ordering. The inversion is defensible from the rho placebo; it is not
  defensible from the bucket table as presented.

## 6. Additional finding — gate 2 claimed but not met

`class_calibration.json` records `benchmark = "SPY (characteristic-matched on the only available
characteristic: all rows are US equities)"`. Being a US equity is **not** a characteristic match —
beta, size, sector and valuation are, and none are used. So the artifact's own metadata labels a
single-index benchmark as characteristic-matched. That is a label error of exactly the kind this
program keeps finding, and it means gate 2 is **not** satisfied even though the artifact reads as if
it is.

## 7. What is genuinely good here, so this is not read as a takedown

- Arithmetic is internally consistent throughout (bucket sums, cost-band sums, design effect).
- The five `insufficient` verdicts are **distinct and correctly separated**: HTTP 403 for mutual
  funds is explicitly identified as a data-plan limit rather than absent coverage — exactly the
  discipline gate 4 asks for and most artifacts get wrong.
- MDE is published next to the null, and the cost-band mapping is flagged in bold as an assumption.
- No gate was lowered to admit a candidate; nothing was pooled across classes to reach the floor.

---

next_probe: **commit the row-level input** (`ZOOCODE/harvest/*.json`, or its export) or a per-row
checksum, so the 963 included and especially the **504 excluded** rows become auditable — that single
change converts counts 1–3 from trust into verification, and it is cheaper than re-running the study.

---

## 8. PROVENANCE GAP CLOSED 2026-11-25

**Status: counts 1 and 2 superseded. Counts 3, 4 and 5 unchanged.**
Appended 2026-11-25 by ghcopilot. Nothing above this line was deleted or rewritten; the superseded
finding stays in place as the record of the 2026-11-24 state.

The `next_probe` immediately above asked for the row-level input to be committed so the 963 included
and the 504 excluded rows became auditable. That has now happened — not by committing the 44 MB
harvest JSON, but by committing the row-level **export** derived from it.

### 8.1 The three artifacts, with line counts

| path (relative to repo root) | lines | data rows | columns verified |
|---|---:|---:|---|
| `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_CALIBRATION_ROW_MANIFEST.csv` | **1,468** | **1,467** | `symbol, date, bucket, included, exclusion_reason` |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_CALIBRATION_RATINGS.csv` | **1,468** | **1,467** | `symbol, date, period_bucket, included, grade_raw, rating` |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_CALIBRATION_PRICE_PANEL.csv` | **1,468** | **1,467** | `symbol, period_bucket, entry_date, entry_close, exit_date, exit_close, bench_entry_close, bench_exit_close, included, exclusion_reason` |

1,468 lines = 1,467 data rows + 1 header, in all three. The price panel's sha256 is
`8c5ae1842ed6df8915e577731e4b78f6c8ca45fe0fa5a8f4866480ea8d4f85fc`, matching the hash documented in
its own `CLASS_CALIBRATION_PRICE_PANEL.md`, so the closes are pinned to a stated run.

### 8.2 Count 1 restated — was "1 discrepancy", now **0**

Count 1 recorded that 504 rows (34.4% of the sample) were dropped and never disclosed. Measured
against `CLASS_CALIBRATION_ROW_MANIFEST.csv`:

| check | measured | agrees with the artifact |
|---|---|---|
| candidate rows | 963 included + 504 excluded = **1,467** | yes (963 + 504) |
| excluded rows carrying a reason | **504 of 504** | yes |
| distinct exclusion reasons | **1** — `no complete forward window (entry/exit bar missing)` | yes |
| included rows carrying a blank reason | 963 of 963 | yes |
| excluded rows with every close/date field blank | **504 of 504** | yes — blank is the documented exclusion state |

The omission count 1 named is closed. The dropped third of the sample is now visible **row by row
with its reason**, not merely inferable from `excluded_rows = 504` in the JSON. **Count 1: 0 discrepancies.**

### 8.3 Count 2 restated — was "unverifiable", now **verifiable with 0 failures**

Still true on 2026-11-25: `ZOOCODE/harvest/*.json` is absent from the repo. No longer blocking: the
per-row export is present, so the per-row schema check count 2 asked for can be run without it.

| check across 1,467 rows | measured |
|---|---|
| rows parsing against the declared header | **1,467 of 1,467** |
| duplicate keys on `(symbol, period_bucket)` | **0** — 1,467 unique in each of the three files |
| included rows with all four closes present and non-zero | **963 of 963** |
| included rows with a blank `entry_date` or `exit_date` | **0** |
| excluded rows with blank closes | 504 of 504 — the exclusion state, not a schema failure |
| rating labels present per row | 1,467 of 1,467 (`grade_raw` + `rating`) |

**Count 2: unverifiable → verifiable; 0 rows fail schema.**

### 8.4 Row-level auditability, demonstrated end to end

The strongest form of the claim is that the three files join and reproduce the published tallies:

- **Unique key:** `(symbol, period_bucket)` — 1,467 unique of 1,467 rows in each of the three files.
- **Pairwise joins, included rows only:** manifest ∩ panel **963/963** · ratings ∩ panel **963/963** ·
  ratings ∩ manifest **963/963**.
- **Rating tally among the 963 included rows, after the join:** `STRONG_BUY 207 · BUY 579 ·
  HOLD 164 · SELL 13` = **963**, which is exactly the published bucket `n` column. Across all 1,467
  rows the ratings are `BUY 874 · STRONG_BUY 312 · HOLD 260 · SELL 21`, i.e. excluded rows are
  labelled too — which is why the `included` filter matters.

**Join caveat for the next auditor, so this is not mistaken for an inconsistency:** joining on
`(symbol, date, period_bucket)` returns **0 of 963**. `date` in the manifest and ratings is the
*period* date (`2026-08-01`, `2026-09-01`, `2026-10-01`); `entry_date` in the price panel is the
*trading day actually used* (`2026-09-02`, `2026-10-02`) — the first session after the
publication-lagged period date. Both are correct by their own definitions and differ by a session;
`(symbol, period_bucket)` is the stable join.

### 8.5 What this does **not** close

This section restates provenance only. Counts **3**, **4** and **5** stand exactly as written above:

- **3** — the header's "499 tickers" vs the JSON's 485 symbols is still an unexplained 14.
- **4** — SELL at n=13 is still 7.7× below the artifact's own floor of 100, and still load-bearing
  for the monotonicity verdict.
- **5** — the bucket *ordering* is still asserted from per-bucket CIs that overlap pairwise, with no
  CI on any difference.
- Gate 2's benchmark label (§6) is likewise untouched.

Row-level auditability makes the arithmetic checkable. It does not make a below-floor bucket or an
unsupported ordering claim any stronger: being able to see every row is not the same as those rows
supporting the verdict.

### 8.6 Supersession record

| count | 2026-11-24 finding | status at 2026-11-25 |
|---|---|---|
| 1 | 1 discrepancy — 504 excluded rows never disclosed | **SUPERSEDED** — all 504 disclosed row by row with a single reason; 0 discrepancies |
| 2 | unverifiable — cited input absent from the repo | **SUPERSEDED** — per-row export committed; 1,467 rows schema-checkable; 0 failures |
| 3 | 1 mismatch of 21 checked (499 vs 485) | unchanged |
| 4 | 1 (SELL, n=13, floor 100) | unchanged |
| 5 | 1 (bucket ordering, no difference CI) | unchanged |

Counts 1 and 2 were accurate measurements of the repository on 2026-11-24. They are marked
superseded, not withdrawn, and the §1 and §2 text above still reads correctly as of that date.
No Track B artifact was edited to produce this section; it was measured from the three CSVs as
committed.
