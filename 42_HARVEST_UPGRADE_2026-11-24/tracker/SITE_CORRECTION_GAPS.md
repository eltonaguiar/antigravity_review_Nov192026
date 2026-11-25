# Site correction gaps — `Corrections from 25 November`

**Auditor:** ghcopilot · **Date:** 2026-11-25 · **Type:** audit, new file only
**Deployed page:** `https://eltonaguiar.github.io/antigravity_review_Nov192026/changelog-2026-11-24.html`
**Repo source:** `docs/changelog-2026-11-24.html` at `origin/main` = **`036fe98`**, section at `<h3>` lines 600–612
**Artifacts compared:** `CLASS_COVERAGE_TABLE.md`, `EXPECTANCY_CORRECTED.md`, `ZOO_COVERAGE_CRITIQUE.md`,
`DILUTION_SENSITIVITY.md`, `TWO_TABLE_RECONCILIATION.md` (all under `42_HARVEST_UPGRADE_2026-11-24/tracker/`)

**Deployed vs repo:** the five subsections on the deployed page match the repo source; every figure below
was confirmed present on both. No file other than this one was created or edited.

---

## 1. Verdict summary

| subsection | artifact | numbers match exactly? | material omission? |
|---|---|---|---|
| Class coverage — live resolvers only | `CLASS_COVERAGE_TABLE.md` | **yes** (all 9) | **yes** — priced-coverage spread, negative medians |
| Corrected book expectancy | `EXPECTANCY_CORRECTED.md` | **yes** (all 7) | **yes** — hit rate 41.2% |
| Coverage critique | `ZOO_COVERAGE_CRITIQUE.md` | **yes** (all 8 stated) | **yes** — the four failure mechanisms |
| Dilution sensitivity | `DILUTION_SENSITIVITY.md` | **yes** (all 6) | partial — 2 of 10 classes, by design |
| Two-table reconciliation | `TWO_TABLE_RECONCILIATION.md` | **yes** (all 11) | **yes** — `signflip_purge_20260` lineage |

**Headline: zero numerical mismatches.** Every figure the section states that also appears in its artifact
matches exactly. The gaps are **omissions** and **provenance**, not wrong arithmetic.

Two numbers in the section — **33.3%** and **21,858** — are **not stated in any of the five artifacts**.
They trace to the later reconciliation commit `13e63ec` ("reconcile CRYPTO backfill denominators"). They are
not wrong, but they are unsourced *to the five artifacts this section claims to be correcting against*.

---

## 2. Per-subsection cross-check

### 2.1 Class coverage — live resolvers only → `CLASS_COVERAGE_TABLE.md`

| site figure | artifact | exact |
|---|---|---|
| 63,797 raw rows | `raw rows 63,797` | ✅ |
| 37,115 backfill excluded | `backfill rows excluded 37,115` | ✅ |
| 26,682 live-resolver rows | `live-resolver rows 26,682` | ✅ |
| 26,161 priced rows | `live priced rows 26,161` | ✅ |
| CRYPTO 25,488 of 26,682 (95.5%) | `25,488 of 26,682 live rows (95.5%)` | ✅ |
| 12,730 backfilled CRYPTO rows | `38,218 − 25,488` (arithmetic over artifact values) | ✅ |
| 33.3% of all 38,218 CRYPTO rows | computed 12,730/38,218 = 33.31% | ✅ (not stated in artifact — see §4 G4) |

**Material omission — the priced-coverage spread.** This subsection is titled "live resolvers only" and
reports a single aggregate of 26,161 priced rows, but the artifact's third finding is that **priced coverage
is wildly uneven within the live filter**:

| class | priced coverage (artifact) |
|---|---:|
| BOND | **25.00%** |
| FUTURES | 39.13% |
| COMMODITY | 40.99% |
| ETF | 50.00% |
| EQUITY | 60.94% |
| FOREX | 72.22% |
| CRYPTO | 99.47% |
| UNKNOWN | 100.00% |

Without this, the site's own argument is weaker than its artifact: the point is not merely that CRYPTO
dominates *row count*, but that the small classes are **also mostly unpriced**, so BOND's 4 rows are
effectively 1. The site's conclusion "no cross-class comparison is powered" is correct but under-argued.

**Material omission — negative medians.** The artifact records CRYPTO mean `+0.1084%` with median
`−1.0000%`, EQUITY mean `−0.0791%` with median `−1.5000%`, and states: *"Positive means with negative
medians remain payoff-shape, not edge."* The site never gives any class mean or median, so a reader cannot
see the payoff-shape finding that qualifies the means.

**Material omission — the artifact's standing warning:** *"Do not compare these means to the cost gate
directly: this table is gross, priced-only, and class n is not powered."*

### 2.2 Corrected book expectancy → `EXPECTANCY_CORRECTED.md`

| site figure | artifact | exact |
|---|---|---|
| 33,092-row headline (was) | `headline (33,092)` | ✅ |
| 33,096 WON/LOST rows | `priced rows used 33,096` | ✅ |
| mean +6.3474 bp (was +6.34) | `+6.3474 bp` / `+6.34 bp` | ✅ |
| median −38.9950 bp (was −38.98) | `−38.9950 bp` / `−38.98 bp` | ✅ |
| 26 bp round turn | `round-turn cost 26 bp` | ✅ |
| "book remains below the 26 bp round turn" | identical conclusion | ✅ |

**Material omission — the hit rate.** The artifact reports **profitable 13,645 / losing 19,451**, i.e. a
41.2% win share. The site states the mean and median but no hit rate, so a reader cannot tell that the
mean is being carried by a 41% minority of trades.

**Framing gap.** The site attributes non-rescue to "the four-row drift changes no conclusion". The
artifact's actual reason is stronger: *"Removing zero rows did not rescue it because the 33k resolved set
contained no zeros."* The 4-row drift is incidental; the substantive point is that the zero-removal step
was a **no-op by construction**, which is a different and more informative claim.

### 2.3 Coverage critique → `ZOO_COVERAGE_CRITIQUE.md`

| site figure | artifact | exact |
|---|---|---|
| coverage spans 0.010 to 0.750 | `The spread is 0.010 to 0.750` | ✅ |
| "a 75× ratio" | `a 75x ratio` | ✅ |
| 12,730 of 16,360 uppercase CRYPTO rows backfilled | `12,730 of its 16,360 rows … i.e. 77.8%` | ✅ |
| 77.8% | `77.8%` | ✅ |
| 33.3% of all 38,218 | see §2.1 (not the artifact's figure) | ✅ arithmetic |
| 37,115 of 63,792 rows (58.2%) | `37,115 of 63,792 (58.2%)` | ✅ |

**Material omission — the four numbered mechanisms.** The artifact's core section, *"Why disclosure alone
fails — four ways it still misleads"*, is absent from the site. The most material is #2:

> the most-covered class (CRYPTO 0.750) has a **POSITIVE mean (+0.1681%) but a negative median
> (−1.3100%)**, and the least-covered (INDEX 0.010) has 3 resolved rows. **High coverage does not make a
> class's estimate reliable.**

That is the sharpest anti-inference in the artifact — "more coverage ≠ more trustworthy" — and the site
drops it, leaving the coverage number readable as a quality score.

**Verdict word softened.** The artifact's verdict is **"Disclosed, not fixed."** The site's closing line is
"Disclosure is necessary, not sufficient." Close in spirit, but "not sufficient" is weaker than "not fixed",
and the artifact's own next_probe (standardise per-day, matched-benchmark before ranking) is omitted.

**Where the site is ahead of its artifact (not a gap).** The artifact explicitly declines to reconcile
77.8% vs 33.3%: *"The figures may be computed on a different denominator, so I report mine with the query
attached rather than claiming the brief is wrong."* The site **does** reconcile them ("Those percentages use
different denominators, not different facts"). That is an improvement, landed by `13e63ec`.

### 2.4 Dilution sensitivity → `DILUTION_SENSITIVITY.md`

| site figure | artifact | exact |
|---|---|---|
| FOREX +0.0563% → +0.3066% | identical | ✅ |
| COMMODITY −0.1032% → −0.6583% | identical | ✅ |
| unjoined −0.0828 vs joined −0.0435 | identical | ✅ |
| "bound must not be ranked or quoted as a mean" | `not a headline, not a correction, not a ranking` | ✅ (weaker) |

**Omission — 8 of 10 classes.** The artifact covers 10 classes; the site quotes 2. Defensible as "the two
largest distortions" (the artifact says so itself), but it means CRYPTO's own implied mean
(`+0.0285% → +0.0368%`) and EQUITY's (`−0.0884% → −0.7184%`) are absent — and CRYPTO is the class the
whole section is about.

**Omission — the operational definition.** The artifact defines `priced` as **`pnl_pct != 0`**. The site
never states it, so "priced" is undefined for a reader who wants to reproduce the number.

### 2.5 Two-table reconciliation → `TWO_TABLE_RECONCILIATION.md`

| site figure | artifact | exact |
|---|---|---|
| 1,263 of 7,945 disagree (15.9%) | identical | ✅ |
| largest gap 187.18 pp | `largest absolute gap 187.18 pp` | ✅ |
| −0.0929% at_pick | `mean from at_pick_outcomes −0.0929%` | ✅ |
| +0.0172% trading | `mean from trading_picks +0.0172%` | ✅ |
| at_pick 5,833/6,049 (96.4%) | identical | ✅ |
| trading 4,626/6,049 (76.5%) | identical | ✅ |
| "prices come from trading_picks, but reported PnL must be recomputed" | `authoritative for prices and resolution … recompute` | ✅ |

**Material omission — the mechanism.** The artifact identifies *why* the tables disagree: the
**`signflip_purge_20260`** resolver lineage, **360 rows** in the overlapping set, where the sign was flipped
in `trading_picks.pnl_pct` while `at_pick_outcomes` kept the price-consistent sign. The site gives the
187.18 pp largest gap but never says it is a **sign flip**, which is the difference between "two sources
disagree somewhat" and "one field is corrupted in a known, identifiable way".

**Omission — the quarantine instruction.** The artifact's recommendation 2 is *"Quarantine
`signflip_purge_20260` rows from any published mean until re-derived."* The site omits it.

---

## 3. The CRYPTO denominator check (requested explicitly)

Every CRYPTO percentage in the section, with its denominator as printed:

| where | site percentage | denominator on the page? |
|---|---|---|
| §2.1 | **95.5%** | **YES** — "25,488 of those 26,682" |
| §2.1 | **33.3%** | **YES** — "of all 38,218 CRYPTO rows (25,488 live + 12,730 backfill)", and the composition is spelled out |
| §2.3 | **77.8%** | **YES** — "12,730 of the 16,360 rows stored with the exact uppercase label CRYPTO … of that case-sensitive subset" |
| §2.3 | **33.3%** (repeat) | **YES** — "of all 38,218 CRYPTO rows" |

**Result: every CRYPTO percentage on the section carries its denominator. No flag on this test.** This is
worth stating plainly because it is the failure mode the section was written to avoid, and it does not
commit it.

**One adjacent gap does exist.** The coverage endpoints in §2.3 — "coverage spans **0.010 to 0.750** — a
75× ratio" — are **not attributed to classes**. Per `ZOO_COVERAGE_CRITIQUE.md` the 0.750 is **CRYPTO** and
the 0.010 is **INDEX (3 resolved rows)**. A reader cannot tell which class anchors each end, and since
INDEX is a 3-row class, the "75×" headline is driven by the thinnest class in the table — exactly the kind
of unlabelled denominator the rest of the section avoids.

---

## 4. Gaps that span subsections

**G1 — Two different raw-row totals in the same section (63,797 vs 63,792).**
§2.1 says "of **63,797** raw rows"; §2.3 says "37,115 of **63,792** rows". The 5-row difference is inherited
from the artifacts themselves (`CLASS_COVERAGE_TABLE.md` = 63,797; `ZOO_COVERAGE_CRITIQUE.md` = 63,792), so
the site is faithfully reproducing an **artifact-level** discrepancy — but it never says so. Worse, the
sentence "Those percentages use different denominators, not different facts" sits immediately before the
63,792, and reads as if it covers this difference; it actually refers to the 77.8%/33.3% CRYPTO
denominators. **A reader is likely to conclude the two totals are reconciled when they are not.**

**G2 — The build stamp predates the section itself.**
The footer reads `commit be9d3ce`. `be9d3ce` is an ancestor of main dated **2026-11-24**, and at that
commit **the "Corrections from 25 November" section does not exist at all** (`grep` count 0). The section
was introduced at **`7690426`**, and its §2.3 reconciliation text at **`13e63ec`** — both later. The stamp
therefore cannot vouch for any figure on the page it sits under.

**G3 — The Sources line names none of the five artifacts.**
The section opens "Five tracker artifacts published today" and its Sources line reads: `13_EXEC_SUMMARY_DB_2026-11-24.md`, `12_INSIDER/RESULTS_form4_feasibility_2026-11-24.md`, `up_only_breadth.md`, `score_inversion_test.md`, `DEPLOYMENT_LOG.md`. **Zero of the five artifacts the section is built from are named**
(verified: 0 occurrences each of CLASS_COVERAGE_TABLE, EXPECTANCY_CORRECTED, ZOO_COVERAGE_CRITIQUE,
DILUTION_SENSITIVITY, TWO_TABLE_RECONCILIATION). A reader cannot locate the primary source for any
subsection.

**G4 — `21,858` and `33.3%` are unsourced to the five artifacts.**
Neither appears in any of the five. Both are consistent (21,858 = 38,218 − 16,360; 33.3% = 12,730/38,218)
and both trace to the later `13e63ec` reconciliation, but the section presents them as part of the artifact
set it is summarising.

**G5 — Coverage endpoints unattributed** (see §3).

---

## 5. Priority

| priority | gap | why |
|---|---|---|
| **P1** | **G2** stale build stamp | the page's own provenance claim is false; cheap to fix |
| **P1** | **G3** sources name none of the five artifacts | the section is unreproducible as published |
| **P2** | **G1** 63,797 vs 63,792 | a reader-facing inconsistency *inside one section*, currently disguised |
| **P2** | §2.3 the four mechanisms, esp. CRYPTO positive mean / negative median | removes the strongest qualifier |
| **P3** | §2.1 priced-coverage spread + negative medians + cost-gate warning | the conclusion is under-argued without it |
| **P3** | §2.5 `signflip_purge_20260` lineage and quarantine | turns "disagree" into "a known corrupted field" |
| **P4** | G4, G5, §2.2 hit rate, §2.4 definition of "priced" | completeness |

---

## 6. What the section gets right

Not a takedown — the following are true and were verified:

- **Every figure the section and its artifact share matches exactly.** The five cross-check tables in §2
  list **30 figure-to-artifact comparisons**, and all 30 agree.
- **All four explicit CRYPTO percentages carry denominators** (§3) — the specific failure the section was
  written to prevent.
- **No verdict is upgraded and no edge is claimed.** Checked against the categories in
  `BENEFIT_OVERCLAIM_AUDIT.md`: the section uses "withdrawn", "no cross-class comparison is powered",
  "must not be ranked or quoted as a mean", and "no single per-class figure may be published".
- **It resolves rather than conceals** the 77.8%/33.3% denominator tension that `ZOO_COVERAGE_CRITIQUE.md`
  explicitly left open.
- The omissions above are mostly **figures that weaken the programme's own position**, so their absence
  flatters the section slightly rather than inflating a claim.

---

### Provenance

| figure | source |
|---|---|
| site text of all five subsections | deployed page, fetched 2026-11-25; identical to `docs/changelog-2026-11-24.html` @ `036fe98` lines 600–612 |
| 63,797 / 37,115 / 26,682 / 26,161 / 25,488 / 95.5% | `CLASS_COVERAGE_TABLE.md` |
| priced coverage 25.00%–100%, medians, cost-gate warning | `CLASS_COVERAGE_TABLE.md` §Findings |
| 33,092 / 33,096 / +6.3474 / −38.9950 / 26 bp / 13,645–19,451 | `EXPECTANCY_CORRECTED.md` |
| 0.010–0.750 / 75× / 16,360 / 77.8% / 63,792 / 58.2% / four mechanisms / "Disclosed, not fixed" | `ZOO_COVERAGE_CRITIQUE.md` |
| +0.0563→+0.3066 / −0.1032→−0.6583 / −0.0828 vs −0.0435 / `priced = pnl_pct != 0` | `DILUTION_SENSITIVITY.md` |
| 1,263 / 7,945 / 15.9% / 187.18 / −0.0929 / +0.0172 / 5,833 / 4,626 / 6,049 / `signflip_purge_20260` 360 rows | `TWO_TABLE_RECONCILIATION.md` |
| section introduced at `7690426`; §2.3 text at `13e63ec`; absent at `be9d3ce` | `git log -S` / `git show be9d3ce:docs/changelog-2026-11-24.html` |
