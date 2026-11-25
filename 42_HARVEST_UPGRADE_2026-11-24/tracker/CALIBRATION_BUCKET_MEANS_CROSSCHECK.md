# Track B bucket means — reproducibility cross-check

Copilot (ghcopilot), 2026-11-25. **Reproducibility check only — not an edge claim.**
Nothing here tests, defends or rescues the rho, the inversion, or any bucket's
profitability. It answers one question: do the bucket means published in
`class_calibration.md` recompute from `CLASS_CALIBRATION_PRICE_PANEL.csv`?

Inputs used, both verbatim from `origin/main`, neither edited:

| file | bytes | note |
|---|---|---|
| `CLASS_CALIBRATION_PRICE_PANEL.csv` | 135,832 | sha256 `8c5ae1842ed6df8915e577731e4b78f6c8ca45fe0fa5a8f4866480ea8d4f85fc` — matches the hash documented in `CLASS_CALIBRATION_PRICE_PANEL.md` |
| `class_calibration.md` | 6,138 | published figures, quoted not modified |

---

## 1. The headline finding: the CSV has no rating column

The task assumes the panel carries a rating bucket per row. It does not. The header is:

```
symbol, period_bucket, entry_date, entry_close, exit_date, exit_close,
bench_entry_close, bench_exit_close, included, exclusion_reason
```

`period_bucket` is **not** a rating. Its distinct values are `-1m`, `-2m`, `-3m` — the
forward-window offset. Sweeping every column of all 1,467 rows for the strings
`STRONG_BUY` / `BUY` / `HOLD` / `SELL` returns nothing.

I checked the obvious sibling, `CLASS_CALIBRATION_ROW_MANIFEST.csv`
(`symbol,date,bucket,included,exclusion_reason`), in case the label lived there. Its
`bucket` column holds the **same period values** `-3m 484 / -2m 491 / -1m 492`, and
contains no rating label either.

**Consequence: a per-bucket recomputation is not executable from this file set.** The
count of rows I could assign to `STRONG_BUY`, `BUY`, `HOLD`, `SELL` is **0, 0, 0, 0**. That
is a missing-column result, not a mismatch result, and no arithmetical difference is
defined on it.

Note this is consistent with what the panel's own author claims for the file. They wrote
that a reader can "recompute every included event's forward excess return … and check
that the calibration's 963/504 split follows from the windows actually available". That
is a row-level and row-count claim. It is **not** a per-bucket claim, and reading the CSV
as one over-reads the artifact.

---

## 2. Row universe — this part does reconcile exactly

| quantity | published | recomputed from CSV | agree |
|---|---|---|---|
| candidate data rows | 1,467 | 1,467 | yes |
| `included = 1` | 963 | 963 | yes |
| `included = 0` | 504 | 504 | yes |
| distinct symbols among included | 485 | 485 | yes |
| rows per symbol (included) | 963/485 = 1.99 | 1.99 | yes |
| exclusion reasons | 1 reason | 1 reason, all 504 rows: `no complete forward window (entry/exit bar missing)` | yes |

Integrity checks over the 963 included rows, all clean:

- rows with a missing or zero value in any of the four close fields: **0**
- rows with a blank `entry_date` or `exit_date`: **0**
- duplicate `(symbol, entry_date, period_bucket)` keys: **0**

Where the 504 exclusions fall, and why the included set is only two windows:

| period_bucket | candidates | included | excluded |
|---|---|---|---|
| `-1m` | 492 | **0** | 492 |
| `-2m` | 491 | 485 | 6 |
| `-3m` | 484 | 478 | 6 |
| total | 1,467 | **963** | 504 |

`-1m` contributes nothing: the most recent event has no complete forward window yet.
So the 963 included rows are exactly 485 rows of the `-2m` window plus 478 of the `-3m`
window. This also rules out a date-mapping difference later — the pairs are uniform:

| period_bucket | entry_date | exit_date | n |
|---|---|---|---|
| `-2m` | 2026-10-02 | 2026-11-02 | 485 |
| `-3m` | 2026-09-02 | 2026-10-02 | 478 |

The benchmark columns are constant per date pair (2 distinct
`(entry_date, exit_date, bench_entry_close, bench_exit_close)` tuples across 963 rows), and
`exit_date − entry_date` is 30–31 days for every row. There is one benchmark series, applied
on the same dates as the stock legs.

---

## 3. What is reproducible: row-level excess, and the aggregate

Applying the task's formula literally to all 963 included rows —

$$\text{excess}_i = \left(\frac{\text{exit\_close}_i}{\text{entry\_close}_i} - \frac{\text{bench\_exit\_close}_i}{\text{bench\_entry\_close}_i}\right)\times 100$$

— gives (equal-weighted across rows):

| statistic | value |
|---|---|
| n | **963** |
| mean gross excess | **+1.886896 pp** |
| median | +0.572091 pp |
| sd | 13.286180 pp |
| min | −47.4654 pp |
| max | +39.7861 pp |

Per `period_bucket`, since that is the only grouping the file supports:

| period_bucket | n | mean gross excess |
|---|---|---|
| `-1m` | 0 | — |
| `-2m` | 485 | **+8.4001 pp** |
| `-3m` | 478 | **−4.7217 pp** |

The two windows differ by 13.1 pp. See the caveat in §6 — this is the reason bucket means
are fragile even once labels are recovered.

---

## 4. The one testable cell: aggregate reconciliation

Although I cannot recompute the four bucket means, their **n-weighted average** is
over-determined by the published table, so it can be compared against the panel.

| | value |
|---|---|
| recomputed **gross** mean, 963 rows | **+1.886896 pp** |
| published means, n-weighted: (207×1.2818 + 579×1.6708 + 164×2.8798 + 13×−0.5222) / 963 | **+1.763473 pp** |
| **gap (recomputed − published)** | **+0.123423 pp = 12.3423 bp** |

Published n sum to 963 exactly, which is the first sign the table and the panel describe
the same row set.

### The gap is the documented cost charge, to within rounding

`class_calibration.md` charges a liquidity-bucketed round turn, and its own cost table
gives the band row counts. The row-count-weighted average charge is:

$$\frac{152\times 6.71 + 784\times 12.07 + 27\times 52.0}{963} = 12.3435\ \text{bp}$$

| candidate explanation | value | distance from the observed 12.3423 bp |
|---|---|---|
| published figures are **gross** (no cost) | 0 bp | 12.34 bp — rejected |
| all rows at deep band (6.71 bp) | 6.71 bp | 5.63 bp |
| all rows at normal band (12.07 bp) | 12.07 bp | 0.27 bp |
| all rows at thin band (52.0 bp) | 52.0 bp | 39.66 bp |
| **documented cost mix 152/784/27** | **12.3435 bp** | **0.0012 bp** |

**Residual: −0.0012 bp (−0.0000118 pp).** All four published means are quoted to 4 decimal
places, so their n-weighted average carries a rounding envelope of
$\pm 0.5\times10^{-4}$ pp $=\pm 0.005$ bp. The residual is **inside that envelope** — the
reconciliation is exact to the precision at which the figures were published.

Corroborating, independent of the arithmetic: the published field in
`class_calibration.json` is named **`mean_net_pct`**. The producer labelled these figures
"net". The task's formula is gross. The 12.34 bp gap is that word.

---

## 5. Published beside recomputed

| bucket | published n | published mean | recomputed n | recomputed mean | gap |
|---|---|---|---|---|---|
| STRONG_BUY | 207 | +1.2818 | **not assignable** | **not computable** | undefined |
| BUY | 579 | +1.6708 | **not assignable** | **not computable** | undefined |
| HOLD | 164 | +2.8798 | **not assignable** | **not computable** | undefined |
| SELL | 13 | −0.5222 | **not assignable** | **not computable** | undefined |
| **all included (aggregate)** | **963** | **+1.763473** (n-weighted) | **963** | **+1.886896** | **+0.1234 pp** |

The count per bucket I actually got is `0` for every rating bucket, because no column
assigns rows to them. The only count I can report is per period: `-1m` 0, `-2m` 485,
`-3m` 478.

---

## 6. Verdict

**REPRODUCED in the aggregate; per-bucket NOT VERIFIABLE from this CSV.** The four
published bucket means cannot be recomputed — the file carries no rating column, so 0 of
963 rows are assignable to STRONG_BUY/BUY/HOLD/SELL. At the one cell the file does
determine, all 963 rows, the published table's n-weighted mean sits **0.1234 pp (12.3423 bp)**
below the panel's gross mean, which is the documented liquidity-bucketed cost of
**12.3435 bp** to a residual of **0.0012 bp**, i.e. inside the 0.005 bp rounding envelope of
4-dp published figures.

**Classification of the gap: a cost / units-of-measurement difference — net-of-cost versus
gross.** Not a price-source difference (a different price vendor would not land on the
documented cost mix to 0.0012 bp, and the panel's sha256 pins the closes used). Not a
date-mapping difference (the entry/exit pairs are uniform — two windows, 30–31 day gaps,
one benchmark on the same dates — and the row counts 963/504 and 485 symbols match
exactly). Row count used throughout: **963 included of 1,467 candidates.**

What this does and does not establish:

- **Does establish:** the published bucket table is arithmetically consistent with this
  price panel under the artifact's own stated cost model. The panel is a genuine row-level
  provenance record for the 963-event sample, and its row universe is exactly the one the
  calibration reports.
- **Does not establish:** that the four bucket *levels* are correct. A single aggregate
  identity cannot detect a compensating error — e.g. two buckets each off by ±X pp in
  proportion to their n — and the labels needed to rule that out are absent.

---

## 7. Caveats worth carrying forward

1. **The two included windows have opposite signs** (`-2m` +8.40 pp on 485 rows, `-3m`
   −4.72 pp on 478). Any bucket mean is therefore heavily a function of how that bucket's
   rows split across the two windows. With 2 rows per symbol, a symbol's rating can be
   constant while its two rows straddle the windows, so bucket levels are not stable
   under window composition. This is a properties-of-the-artifact observation, not a claim
   about edge in either direction.
2. **`-1m` is 100% excluded**, so the sample is two monthly cohorts, not three, and no
   result here says anything about the most recent month.
3. **The closes are a live-price snapshot** (as the panel's own caveat says); the sha256
   pins this run and re-collection on another day can move rows across the 963/504 line.
4. n per row group is small where it matters most: SELL is 13 rows, 7.7× below the
   artifact's own floor of 100 — unchanged from the published correction, and unaffected
   by anything in this check.

---

## 8. What would close the remaining gap

To reproduce the per-bucket cells, the row-level rating must be joined in on a key that
exists in both files — `(symbol, entry_date)` or `(symbol, period_bucket, entry_date)`.
`CLASS_CALIBRATION_PRICE_PANEL.csv` and `CLASS_CALIBRATION_ROW_MANIFEST.csv` contain no
such field; per `class_calibration.md`'s method line the ratings originate in
`ZOOCODE/harvest/*.json`, which is the 44 MB input the panel was built to avoid needing.

Recommended follow-up, in the spirit of the existing row manifest: publish a
`rating` column on the panel (or a `symbol,date,rating` label file). Until then, the
honest statement is that Track B's bucket **levels** are not independently reproducible
from the repo, while its bucket **counts**, its row universe, and its cost model all
reconcile exactly.

---

### Provenance

Every number above resolves to a stated source and row count:

| figure | source | rows |
|---|---|---|
| 1,467 / 963 / 504 / 485 | `CLASS_CALIBRATION_PRICE_PANEL.csv`, `included` column | 1,467 |
| +1.886896, +0.572091, 13.286180, −47.4654, +39.7861 | same, formula in §3 | 963 |
| −1m 0 / −2m 485 / −3m 478 | same, `period_bucket` | 963 |
| +8.4001 / −4.7217 | same, `period_bucket` groups | 485 / 478 |
| +1.2818 / +1.6708 / +2.8798 / −0.5222, n 207/579/164/13 | `class_calibration.md` bucket table; identical in `class_calibration.json` under `mean_net_pct` | 963 |
| 6.71 / 12.07 / 52.0 bp, rows 152/784/27 | `class_calibration.md` cost model table; `cost_band_rows` in `class_calibration.json` | 963 |
| 12.3435 bp | arithmetic in §4 over those three bands | 963 |
| 0.123423 pp / 12.3423 bp | §4 subtraction | 963 |

Reproducer: load the CSV, keep `included == '1'` (963 rows), compute
`(exit_close/entry_close − bench_exit_close/bench_entry_close)*100` per row, take the
mean; compare to the n-weighted published means as in §4. No file was modified by this
check — `class_calibration.md`, `class_calibration.json` and every CSV are unchanged.
