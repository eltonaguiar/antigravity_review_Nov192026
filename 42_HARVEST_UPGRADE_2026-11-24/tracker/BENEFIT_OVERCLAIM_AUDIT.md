# Benefit overclaim audit — claims this programme cannot support

**Author:** ghcopilot · **Date:** 2026-11-25 · **Type:** pre-publication guard, new file only
**Target:** the benefits section about to be published on `docs/changelog-2026-11-24.html`
**Method:** for each claim that commonly appears in a programme's own benefits summary, ask whether an
artifact **on `origin/main`** supports it. Where one contradicts it, the artifact is named and quoted.
Where the claim survives only in weakened form, the accurate wording is given.

`origin/main` at sweep time: **`13e63ec`**. No file other than this one was created or edited.

**Verdict key**

| verdict | meaning |
|---|---|
| **UNSUPPORTED** | no artifact supports it, at least one contradicts it — do not publish |
| **OVERSTATED** | a real artifact exists but the usual phrasing claims more than it says |
| **MANUFACTURED** | the claim is true only under a denominator the programme itself has withdrawn |
| **SUPPORTABLE** | an artifact supports it, provided the stated qualifier travels with the number |

---

## Summary table

| # | common claim | verdict | artifact that governs it |
|---|---|---|---|
| A1 | "we found a profitable edge / positive expectancy" | **UNSUPPORTED** | `EXPECTANCY_CORRECTED.md` |
| A2 | "class X outperforms class Y" | **UNSUPPORTED** | `TWO_TABLE_RECONCILIATION.md` |
| A3 | "analyst ratings carry exploitable information" | **UNSUPPORTED** | `class_calibration.json` / `TRACK_B_DEFECT_AUDIT.md` |
| A4 | "we identified skilled analysts / top traders" | **UNSUPPORTED** | `firm_skill_weights.csv` |
| A5 | "dilution-corrected means are higher, so the book is better" | **OVERSTATED** | `DILUTION_SENSITIVITY.md` |
| B1 | "we fixed the asset-class bug" | **OVERSTATED** | `ZOO_UNJOINED_PATTERN_CORRECTION.md` |
| B2 | "we fixed the MDE error" | **OVERSTATED** | `MDE_PROVENANCE_SWEEP.md` §5 |
| B3 | "we resolved the missing / excluded rows" | **OVERSTATED** | `AUDIT_OF_TRACK_B.md` counts 1–2 |
| B4 | "the benchmark gate is satisfied" | **UNSUPPORTED** | `TRACK_B_DEFECT_AUDIT.md` |
| B5 | "coverage disclosure fixes comparability" | **UNSUPPORTED** | `ZOO_COVERAGE_CRITIQUE.md` |
| C1 | "STRONG_BUY outperforms its control (3 of 3 terciles)" | **OVERSTATED** | `class_calibration.md` bucket CIs |
| C2 | "the quartile spread is significant" | **UNSUPPORTED** | changelog's own "+4.97 pp, not significant" |
| C3 | "the effect has decayed to zero" | **OVERSTATED** | `ITEM_B_SETTLE_PROBE.md` per-year table |
| D1 | "CRYPTO is the best-performing class" | **MANUFACTURED** | `CLASS_COVERAGE_TABLE.md` |
| D2 | "six asset classes analysed and ranked" | **MANUFACTURED** | `CLASS_COVERAGE_TABLE.md` |
| E1 | "large sample: 63,797 rows" | **OVERSTATED** | `CLASS_COVERAGE_TABLE.md` |
| E2 | "forward-tested / out-of-sample" | **UNSUPPORTED** | no open forward gate on main |

---

## A. Claims of an edge or a return

### A1. "We found a profitable edge" / "the book has positive expectancy" — **UNSUPPORTED**

`EXPECTANCY_CORRECTED.md` measures the priced-only resolved set (33,096 WON+LOST rows, 0 zero
placeholders remaining):

| measure | value |
|---|---:|
| mean | **+6.3474 bp** |
| median | **−38.9950 bp** |
| profitable / losing | 13,645 / 19,451 (**41.2%** winners) |
| round-turn cost | **26 bp** |

The mean is **+6.35 bp against a 26 bp round turn = −19.65 bp net**, and the median is **−39.00 bp**.
The artifact's own conclusion: "The book remains **negative net of cost**."

`DILUTION_SENSITIVITY.md` goes further about its own derived column: "This table is **not** a headline,
**not** a correction, and **not** a ranking. It is a boundary."

**Accurate wording:** "On the priced-only resolved set the mean return is +6.35 bp against a 26 bp
round-turn cost (−19.65 bp net), with a median of −39.00 bp and a 41.2% hit rate. The programme has
**not** demonstrated a net edge."

### A2. "Class X outperforms class Y" — **UNSUPPORTED**

`TWO_TABLE_RECONCILIATION.md`: over 7,945 rows where both source tables hold a non-zero return,
**15.9% disagree**, and the two table means have **opposite signs** (`at_pick_outcomes` −0.0929%,
`trading_picks` +0.0172%). The artifact states: "choosing a table decides whether the book looks
profitable." The price-arithmetic test favours `at_pick_outcomes` (96.4% vs 76.5%) but this
**adjudicates the data, not the strategy** — and the larger number is the losing one.

**Accurate wording:** "Class rankings are not quotable: the two PnL sources disagree on 15.9% of
overlapping rows with opposite-sign means, so no ranking is stable across sources."

### A3. "Analyst ratings carry exploitable information" — **UNSUPPORTED**

Three independent artifacts: `class_calibration.json` (`rho = −0.04673`, `permutation_p = 0.9995`,
**sign inverted**); `mde_recheck.py` / `MDE_MEASUREMENT_RECHECK.md` (MDE **8.78 pp/yr** at 80% power,
too coarse to resolve any plausible premium); and `AUDIT_OF_ITEM_B_TOTALS.md` (the effect, whatever its
sign, is carried by **reiterations**, `main` 438 of 593, not fresh upgrades `up` 117).

**Accurate wording:** "The analyst question is closed as **unmeasurable at this sample size**, not as
'no edge': rho is inverted with p = 0.9995, and the MDE of 8.78 pp/yr is larger than any plausible
rating premium."

### A4. "We identified skilled analysts / consistently winning traders" — **UNSUPPORTED**

`firm_skill_weights.csv`: of the 9 firms clearing the 300 clean-event floor, **exactly one beats its
placebo threshold** (Morgan Stanley, +178.20 bp vs 109.6 bp); the other **8 are `indistinguishable`**,
and **210 firms sit below the floor as `underpowered`**. A 1-of-9 hit rate against an 80%-power placebo
is what noise looks like.

**Accurate wording:** "One firm of nine testable clears its placebo threshold; that is a lead requiring
forward confirmation, **not** an established skill set."

---

## B. Claims that a defect was FIXED when it was only DOCUMENTED

This is the most seductive category, because the programme is genuinely good at **finding** defects and
the documentation is real. Documentation is not repair.

### B1. "We fixed the asset-class case bug" — **OVERSTATED**

`ZOO_UNJOINED_PATTERN_CORRECTION.md` shows `asset_class` is `utf8mb4_unicode_ci`, so a plain `GROUP BY`
**already merged** `crypto`/`CRYPTO`; `UPPER()` changed **no count** (CRYPTO 573→573, FOREX 122→122).
Meanwhile the real label defect survives untouched: `STOCK` 19 / `STOCKS` 4 (neither counted as
`EQUITY`), `PENNY` 2 / `PENNYSTOCK` 3. **A label-alias map is what would fix it; none exists.**

### B2. "We fixed the MDE error" — **OVERSTATED**

The correction is real in `tracker/class_calibration.{json,md}` and in `zoocode/class_calibration.json`.
But `MDE_PROVENANCE_SWEEP.md` §5 records **one STALE hit that remains on main**:
`zoocode/class_calibration.md:25` still prints **`18.868%`** in the per-class results table while its own
sibling JSON says `mde_pct: 8.78`. The sweep calls it out as the single outstanding fix. Until that cell
is edited, the `zoocode` `.md` and `.json` **disagree with each other**.

### B3. "We resolved the missing / excluded rows" — **OVERSTATED**

`AUDIT_OF_TRACK_B.md` counts 1 and 2 were superseded on the *provenance* axis — the 504 exclusions are
now row-level auditable — but **auditable is not resolved**. The rows are still excluded from the
analysis. Likewise `ZOO_UNJOINED_PATTERN.md`'s 820 (now **816**) unjoined EXPIRED rows are **disclosed,
not joined**. `AUDIT_OF_TRACK_B.md` keeps findings 3–7 standing precisely to preserve this distinction.

### B4. "The benchmark gate is satisfied" — **UNSUPPORTED**

`TRACK_B_DEFECT_AUDIT.md` defect 3: SPY is a single-index benchmark, characteristic-match **gate 2 is
UNMET**; `class_calibration.json` now **says so** (`"benchmark": "...gate 2 UNMET"`). The label was
corrected; **the gate was not passed.** Gate 4 and the bucket *levels* remain unquotable until it is.

### B5. "Reporting coverage fixes cross-class comparability" — **UNSUPPORTED**

`ZOO_COVERAGE_CRITIQUE.md`, verbatim: "**it does not fix it — it *relabels* it.** … Disclosure is
necessary and not sufficient." The pooled number is still dominated by the class with the most priced
rows.

---

## C. Claims of significance where intervals include zero

### C1. "STRONG_BUY outperforms its control — 3 of 3 terciles exclude zero" — **OVERSTATED**

The tercile result is a **per-tercile** interval, not a CI on any *difference*. `AUDIT_OF_TRACK_B.md`
finding 5: the bucket ordering is asserted from separate per-bucket intervals which **overlap pairwise**
(STRONG_BUY [0.062, 2.638] and BUY [1.038, 2.342] overlap across almost their whole width), and **no CI
is given for any difference between adjacent buckets**. Additionally the **SELL bucket's CI
[−6.7069, +3.9964] includes zero** (`ci_excludes_zero: false`) at n = 13, 7.7× below the artifact's own
floor of 100.

**Accurate wording:** "Three of three terciles have per-tercile intervals excluding zero; **no interval
on any between-bucket difference was computed**, so no ordering is established."

### C2. "The quartile spread is significant" — **UNSUPPORTED**

The changelog's own line 119 already reads "bottom quartile −9.48% · spread **+4.97 pp, not
significant**". Publishing a benefits section that promotes this to significant would contradict the
page it sits on.

### C3. "The effect has decayed to zero" — **OVERSTATED**

`ITEM_B_SETTLE_PROBE.md` prints the per-year table (lines 68–74): the 2026 cell is **n = 22** against
2025's **n = 45**, and the two cells together are 67 events = **13.9% of the 481** per-year total and
**6.9% of the 967** headline. A decay-to-zero claim cannot rest on n = 22 alone.

*(My detailed audit of that file's denominators — 967 raw / 610 price-resolved / 593 action-type / 481
per-year — is `ghcopilot/AUDIT_OF_ITEM_B_TOTALS.md`, which currently exists only on branch
`track-c/item-b-totals-audit-2026-11-25` (PR #10), **not** on `origin/main`. The cells cited above are
quoted from the on-main source file, so this claim's evidence does not depend on that branch.)*

---

## D. Cross-class comparison when one class is 95.5% of the live-resolver rows

### D1. "CRYPTO is the best-performing class" — **MANUFACTURED**

`CLASS_COVERAGE_TABLE.md` (live resolvers only, `resolver_version NOT LIKE 'backfill%'`):

| quantity | value |
|---|---:|
| live-resolver rows | **26,682** |
| CRYPTO rows | **25,488** |
| **CRYPTO share of live-resolver rows** | **95.53%** |
| all non-CRYPTO rows | **1,194 (4.47%)** |

The non-CRYPTO classes are, in full: FOREX 612, EQUITY 192, COMMODITY 161, FUTURES 69, **BOND 4, ETF 2,
INDEX 0**. A "CRYPTO beats X" statement compares 25,488 rows against 0–612. That is not a cross-class
comparison; it is a **CRYPTO measurement with rounding-error comparators**.

### D2. "Six asset classes analysed and ranked" — **MANUFACTURED**

Of the six headline classes, after the live filter: CRYPTO 25,488, FOREX 612, EQUITY 192, COMMODITY 161,
and ETF/BOND at **2 and 4 rows**. `CLASS_COVERAGE_TABLE.md` also reports priced coverage as low as
**25.00% (BOND)** and **39.13% (FUTURES)**, so even the small classes are mostly unpriced.

**Accurate wording:** "Four classes have enough live rows to describe; **two (ETF, BOND) have 6 rows
between them and cannot be ranked.** Any cross-class statement is a CRYPTO statement."

### D3. "Coverage is now disclosed, so classes are comparable" — **UNSUPPORTED**

See B5. `ZOO_COVERAGE_CRITIQUE.md` measures coverage as "almost perfectly confounded with the class
label" — spread 0.010 (INDEX) to 0.750 (CRYPTO), which the artifact states as a **75×** ratio. (Excluding
the 3-row INDEX, the real-class spread is 0.061 FUTURES to 0.750 CRYPTO = **12.3×** — still enough to
make a pooled number a CRYPTO number.)

---

## E. Two further claims that recur in benefits summaries

### E1. "We analysed a large sample — 63,797 rows" — **OVERSTATED**

`CLASS_COVERAGE_TABLE.md`: of 63,797 raw rows, **37,115 (58.2%) are backfill** and excluded; the live
sample is **26,682 (41.8%)**. The changelog elsewhere notes `EXPIRED` rows are **96.2% zeros**. Quoting
63,797 as the analysis N overstates the evidence base by ~2.4× and inflates the effective n again
because most of the remainder are zero placeholders.

### E2. "Forward-tested" / "out-of-sample validated" — **UNSUPPORTED**

There is **no open forward gate** artifact on `origin/main` in this repository supporting any of these
claims — no forward-clock state file shows the gate OPEN. The horizon evidence that does exist points
the other way: `MDE_MEASUREMENT_RECHECK.md` shows the test cannot resolve an effect smaller than
**8.78 pp/yr**, and the out-of-sample work cited elsewhere in this programme is not in this repo at all.
Backfill rows are *older* rows, not out-of-sample rows — `CLASS_COVERAGE_TABLE.md` excludes all 37,115 of
them.

---

## F. What this programme CAN claim — so the section is not empty

These survive with their qualifiers attached:

- **It found and quantified specific defects.** E.g. the two-table disagreement (15.9%, 96.4% vs 76.5%
  price-arithmetic agreement), the dilution bound, and the 95.5% concentration figure above. Each has a
  committed artifact with a row count.
- **It withdrew its own claims in public.** The changelog already carries "Correction, again mine" and
  "WITHDRAWN" sections; `MDE_PROVENANCE_SWEEP.md` adds a further supersession pointer. This is a genuine,
  unusual benefit — and it is the one claim that gains from being stated precisely rather than inflated.
- **It established that several questions are unmeasurable at this sample size** (analyst ratings:
  MDE 8.78 pp/yr; most firms underpowered). "Unmeasurable" is a real result; "no edge" is not the same
  statement and must not be substituted for it.

---

## G. Rules the benefits section should follow

1. **Every bp or % carries its denominator.** "+6.35 bp" is meaningless without "priced-only, 33,096
   rows, against a 26 bp round turn".
2. **Documented ≠ fixed.** If a defect's artifact is an audit rather than an edit, the verb is "found and
   documented", not "fixed".
3. **Never quote a pooled or cross-class number while one class is 95.5% of the rows.** Quote CRYPTO
   alone, or state the concentration in the same sentence.
4. **No ordering claim without a difference CI.** Per-bucket intervals cannot establish an order.
5. **Zero-mass and backfill denominators must be stated** (`96.2%` zeros; `58.2%` backfill).

---

### Provenance

| figure | artifact on origin/main |
|---|---|
| +6.3474 bp / −38.9950 bp / 13,645–19,451 / 26 bp | `tracker/EXPECTANCY_CORRECTED.md` |
| 15.9% disagreement, opposite signs, 96.4% vs 76.5% | `tracker/TWO_TABLE_RECONCILIATION.md` |
| 26,682 live rows, 25,488 CRYPTO = 95.53%, BOND 4, ETF 2, INDEX 0 | `tracker/CLASS_COVERAGE_TABLE.md` |
| 0.010–0.750 coverage spread, "relabels it" | `tracker/ZOO_COVERAGE_CRITIQUE.md` |
| MAR false, −0.0828 vs −0.0435 | `tracker/DILUTION_SENSITIVITY.md` |
| rho −0.04673, p 0.9995, SELL CI [−6.7069, +3.9964] n=13 | `tracker/class_calibration.{md,json}` |
| MDE 8.78 pp/yr, sd_symbol_means 5.751 | `tracker/MDE_MEASUREMENT_RECHECK.md` |
| 1 of 9 beats placebo, 210 underpowered | `tracker/firm_skill_weights.csv` |
| zoocode/class_calibration.md:25 still `18.868%` | `tracker/MDE_PROVENANCE_SWEEP.md` §5 |
| 967 / 610 / 593 / 481; 2026 n=22 vs 2025 n=45 | `tracker/ITEM_B_SETTLE_PROBE.md` (branch-only audit: `ghcopilot/AUDIT_OF_ITEM_B_TOTALS.md`, PR #10) |
| 504 disclosed not resolved; findings 3–7 standing | `ghcopilot/AUDIT_OF_TRACK_B.md` |
| gate 2 UNMET | `tracker/TRACK_B_DEFECT_AUDIT.md`, `class_calibration.json` |
| CRYPTO 573→573, FOREX 122→122 under UPPER | `tracker/ZOO_UNJOINED_PATTERN_CORRECTION.md` |

No file other than this one was created or edited. No new measurement was taken for this audit; every
number is quoted or summed from a committed artifact, except the concentration ratio 25,488/26,682 =
95.53% and the net −19.65 bp, which are arithmetic over two committed figures.
