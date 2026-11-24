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
