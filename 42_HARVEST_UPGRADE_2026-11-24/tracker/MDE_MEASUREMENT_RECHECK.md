# MDE measurement recheck — independent recomputation

**Author:** ghcopilot · **Date:** 2026-11-25 · **Type:** independent recheck, new artifacts only
**Script:** `42_HARVEST_UPGRADE_2026-11-24/tracker/mde_recheck.py`
**Input (read-only):** `42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_CALIBRATION_PRICE_PANEL.csv`
**Not touched:** `class_calibration.json`, `class_calibration.py` (owned by another panel this tick),
and the input CSV — this run only reads.

---

## 1. Method

Rows with `included == 1` are kept. Per-row gross excess is

$$\text{excess}_i=\left(\frac{\text{exit\_close}_i}{\text{entry\_close}_i}-1\right)-\left(\frac{\text{bench\_exit\_close}_i}{\text{bench\_entry\_close}_i}-1\right)$$

reported in percentage points (fraction × 100). Per-symbol means are the arithmetic means of a
symbol's rows; `sd_symbol_means` is the standard deviation across the 485 symbol means. Annualisation
is **× 12** (monthly → yearly). MDE at 80% power (two-sided α = 0.05):

$$\text{MDE}=2.802\cdot\frac{\text{sd\_symbol\_means}}{\sqrt{n_{\text{symbols}}}}$$

Run as a single bare command, no pipes and no redirects:

```
python3 42_HARVEST_UPGRADE_2026-11-24/tracker/mde_recheck.py
```

---

## 2. My measured values, against the stated ground truth

Each ground-truth figure was **recomputed here, not copied in**.

| # | quantity | my measured value | ground truth | difference | agrees |
|---|---|---:|---:|---:|---|
| 1 | included row count | **963** | 963 | 0 | ✅ |
| 2 | distinct symbols | **485** | 485 | 0 | ✅ |
| 3 | row-level SD (sample, ddof=1) | **13.2931 pp** | — (not stated) | — | — |
| 4 | per-symbol mean: mean / **SD (ddof=1)** | **+1.8762 pp / 5.7505 pp** | 5.751 pp/month | **−0.0005** | ✅ |
| 5 | annualised sigma (×12) | **69.0061 pp/yr** | 69.01 pp/yr | **−0.0039** | ✅ |
| 6 | MDE at 80% power | **0.7317 pp/month = 8.7798 pp/yr** | 0.732 pp/month = 8.78 pp/yr | **−0.0003 / −0.0002** | ✅ |

**Verdict: REPRODUCED.** All four ground-truth figures I was given — 963, 485, 5.751, 69.01, 0.732,
8.78 — reproduce to within the precision at which they were quoted. Every residual is ≤ 0.004 and is
pure 3-significant-figure rounding: 5.7505 → 5.751, 69.0061 → 69.01, 0.7317 → 0.732, 8.7798 → 8.78.
The ground truth is **not** changed.

---

## 3. Full output of the run

```
candidate data rows ................ 1467
included == 1 rows ................. 963
rows usable (all 4 closes present) . 963
rows skipped (missing/zero close) .. 0
distinct symbols ................... 485
rows per symbol .................... 1.9856

row-level gross excess, pp:
   mean ........................... +1.8869
   median ......................... +0.5721
   SD (sample, ddof=1) ............ 13.2931
   SD (population, ddof=0) ........ 13.2862

per-symbol mean returns, pp per monthly hold:
   n symbols ...................... 485
   mean of symbol means ........... +1.8762
   SD of symbol means (ddof=1) .... 5.7505   <-- sd_symbol_means
   SD of symbol means (ddof=0) .... 5.7446
   min / max symbol mean .......... -26.2405 / +21.8284

annualised sigma (x12):
   from ddof=1 .................... 69.0061 pp/yr
   from ddof=0 .................... 68.9350 pp/yr

MDE at 80% power = 2.802 * sd_symbol_means / sqrt(n_symbols):
   ddof=1 ......................... 0.7317 pp/month = 8.7798 pp/yr
   ddof=0 ......................... 0.7309 pp/month = 8.7708 pp/yr
```

---

## 4. Sensitivity to the three conventions that usually cause a mismatch

Because a recheck is only useful if it can distinguish "wrong" from "measured differently", each of the
three classic causes was computed rather than assumed away. **None of them amounts to a discrepancy
here**, but each changes a digit:

### 4a. Sample vs population SD (ddof)

| quantity | ddof=1 | ddof=0 | ratio |
|---|---:|---:|---:|
| row-level SD | 13.2931 | 13.2862 | 1.00052 |
| **sd of symbol means** | **5.7505** | 5.7446 | 1.00103 |
| annualised sigma | 69.0061 | 68.9350 | 1.00103 |
| MDE pp/month | 0.7317 | 0.7309 | 1.00103 |

The ground truth's 5.751 matches **ddof=1** (5.7505) and not ddof=0 (5.7446), so the original figure
used the sample SD over 485 symbol means. The two differ by $\sqrt{485/484}=1.00103$ — small, but a
recheck using the wrong one would mis-report 5.745 instead of 5.751.

### 4b. Annualisation: ×12, not ×√12

I used ×12, as specified. Had I compounded by √12, the annualised sigma would be
$5.7505\sqrt{12}=19.920$ pp/yr and the MDE 2.535 pp/yr — a factor of 3.46 off. The stated 69.01 is
unambiguously the **×12** convention, so the two figures are not comparable to each other.

### 4c. pp vs fraction

All figures are in percentage points (fraction × 100). In fractions the same quantities read
0.057505 and 0.690061, i.e. 100× smaller. The ground truth's 5.751 is pp, so a fraction-space recheck
would look like a catastrophic 100× miss while being arithmetically correct.

### 4d. Not a cause: the row-level SD is *not* the input to the MDE

Worth stating explicitly, since it is the most likely confusion: the MDE uses
`sd_symbol_means` (5.7505 pp), **not** the row-level SD (13.2931 pp). Using the row-level SD would give
a much larger, wrong MDE. The MDE is a per-symbol-mean dispersion over 485 symbols, which is why it is
smaller than the row dispersion despite 1.9856 rows per symbol.

---

## 5. What this does and does not establish

**Establishes:** the 963 / 485 / 5.751 / 69.01 / 0.732 / 8.78 chain is arithmetically correct and
reproducible from the committed panel by an independent script, under the stated conventions.

**Does it make the null informative? No — and the number itself is the reason.** An MDE of
**8.78 pp/yr** at 80% power means the test cannot resolve an effect smaller than ~8.8 percentage points
annualised. That is far above any plausible analyst-rating premium, so the *inverted* rho is an
uninformative null rather than a demonstrated absence of edge. This recheck confirms the size of the
MDE; it says nothing about the sign of the effect, and nothing here should be read as an edge claim.

**Does not establish:** anything about rho, the bucket ordering, the benchmark choice, or the
`design_effect = 0.38` question. Those are separate defects owned elsewhere and are unaffected by this
run.

---

## 6. Provenance

| figure | where it comes from |
|---|---|
| 1,467 / 963 / 485 | `CLASS_CALIBRATION_PRICE_PANEL.csv`, `included` column |
| +1.8869 / +0.5721 / 13.2931 / 13.2862 | script §3, row-level block |
| +1.8762 / 5.7505 / 5.7446 / −26.2405 / +21.8284 | script §3, per-symbol block |
| 69.0061 / 68.9350 | script §3, ×12 block |
| 0.7317 / 8.7798 / 0.7309 / 8.7708 | script §3, MDE block |
| 963 / 485 / 5.751 / 69.01 / 0.732 / 8.78 | ground truth supplied with the task, **recomputed** above |

Reproducer: `python3 42_HARVEST_UPGRADE_2026-11-24/tracker/mde_recheck.py` (stdlib only, no network,
writes nothing). Script reads its input by path relative to its own location, so it works from a
worktree as well as from the repo root.
