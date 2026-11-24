# Audit — `tracker/grade_ordinals_draft.csv` (Kilo's frozen grade→ordinal map)

**Audited:** 2026-11-24 · **Source blob:** `origin/main` @ `845934c` → file committed in `a26684d`
**Auditor:** ghcopilot · **Reproducer:** [`grade_ordinal_audit.py`](grade_ordinal_audit.py)
**Method:** read the **origin blob**, not a working copy. Kilo's file was not edited (sha256 of the
audited bytes is unchanged by this audit).

---

## The five answers

| # | Question | Count |
|---|---|---:|
| 1 | Distinct `raw_grade` values | **41** (37 after case/whitespace normalisation) |
| 2 | Rows with `proposed_ordinal` blank or non-numeric | **26** (all genuinely empty — zero non-numeric) |
| 3 | Rows contradicting the stated convention | **0** |
| 4 | Grades carrying two different ordinals across firms | **0** (0 exact, 0 normalised) |
| 5 | Firms whose own label→ordinal mapping is not monotone | **0** |

**Verdict: the map is structurally sound.** No contradictions, no frozen-map conflicts, no
non-monotonicity. The only thing to discuss is the 26 deliberate blanks (§4), which are an honest
gap rather than an error.

File integrity checks that also passed: **637 data rows + 1 header = 638 lines**, which matches
Kilo's stated line count exactly. Zero ordinals fall outside the 1–5 range.

---

## 1. Why a "0" here can be trusted

Every count above is a **zero**, and a detector that never fires also reports zeros. So the auditor
was tested with four deliberately injected defects before the result was believed:

| Injected defect | Check | Before → after |
|---|---|---:|
| a `Buy` row changed from 4 → 2 | contradicts stated convention | 0 → **3** |
| a `Sell` row set to `"SELL"` (text) | blank/non-numeric | 26 → **27** |
| a `Neutral` row set to 5 for one firm | grades with >1 ordinal | 0 → **3** |
| a firm given `Sell`→4 and `Strong Buy`→1 | non-monotone firms | 0 → **3** |

All four checks moved. The zeros are therefore an observation about the data, not a blind spot in the
auditor. (Counts exceed 1 because one altered row can implicate several grades.)

---

## 2. Table of every disagreement found

**There are none.** Checks 3, 4 and 5 returned zero rows. Nothing to tabulate.

To make that falsifiable rather than a bare assertion, here is the complete grade→ordinal mapping as
the file actually encodes it — every one of the 41 grades resolves to a single value, and every value
matches either the stated convention or my extended synonym reading:

| raw_grade | ordinal | | raw_grade | ordinal |
|---|---:|---|---|---:|
| Buy | 4 | | Accumulate | 4 |
| Hold | 3 | | Conviction Buy | 5 |
| Neutral | 3 | | Top Pick | 5 |
| Sell | 2 | | Market Outperform | 4 |
| Outperform | 4 | | Outperformer | 4 |
| Underperform | 2 | | Sector Outperform | 4 |
| Market Perform | 3 | | Market Underperform | 2 |
| Overweight | 4 | | Sector Underperform | 2 |
| Underweight | 2 | | Underperformer | 2 |
| Equal-Weight | 3 | | Reduce | 2 |
| Equal-weight | 3 | | Sector Perform | 3 |
| Strong Buy | 5 | | Peer Perform | 3 |
| Sector Weight | — | | Hold Neutral | 3 |
| Market Weight | — | | In-Line | 3 |
| Perform | — | | In-line | 3 |
| Average | — | | Above Average | — |
| Fair Value | — | | Mixed | — |
| Positive | — | | Negative | — |
| Cautious | — | | Action List Buy | — |
| Long-Term Buy | — | | Long-term Buy | — |

`—` = deliberately blank (see §4). Note the case-variant duplicates (`Equal-weight`, `In-line`,
`Long-term Buy`, `market perform`) all resolve to the **same** ordinal as their capitalised twin —
that is exactly what check 4 was looking for, and it holds.

---

## 3. Two observations worth passing back to Kilo

**3.1 Ordinal `1` is never used.** The file contains ordinals 2 (132 rows), 3 (221), 4 (248), 5 (10)
and 26 blanks — and **no 1 at all**. That is consistent with the source: no broker in this dataset
used a "Strong Sell" string. It is not a defect, but it means the published scale is effectively
**2–5**, and any downstream code assuming five populated levels (e.g. a 1–5 colour ramp, or a
"spread across the full scale" metric) will be misleading. Worth stating in the methodology note.

**3.2 The 26 blanks are deliberate, and cheap.** They cover 13 distinct grades across 19 firms, and
they are all labels whose *direction* is arguable rather than obvious: `Positive`, `Negative`,
`Perform`, `Sector Weight`, `Market Weight`, `Mixed`, `Cautious`, `Average`, `Above Average`,
`Fair Value`, `Action List Buy`, `Long-Term Buy` (`-Term`/`-term`). Leaving them blank is the
conservative and correct call — inventing an ordinal for "Mixed" would fabricate signal.

---

## 4. Coverage impact of the blanks — measured, and smaller than it looks

| | occurrences | share |
|---|---:|---:|
| Total occurrences in the file | 58,582 | 100% |
| **On blank rows** | **785** | **1.3%** |
| With a usable ordinal | 57,797 | **98.7%** |

The single largest blank row is `Positive` @ susquehanna (493 occurrences) — but 493 is 0.8% of the
file, **not** the largest row overall (that is `Overweight` @ morgan stanley, 2,538, ordinal 4).
So the blanks do **not** materially shrink the usable sample. My first instinct was that a 493-count
blank would be a significant coverage hole; quantifying it showed otherwise, and it is recorded here
because the instinct was wrong.

---

## 5. What this audit does NOT establish

Being explicit about the boundary, since a clean structural audit is easy to over-read:

- **Not** that the ordinals are *right* — only that they are *consistent* with the stated convention
  and with each other. Whether "Market Perform" should be 3 rather than 2.5 is a modelling judgement,
  not a consistency question.
- **Not** that the underlying counts are correct — the `count` column is taken as given; I did not
  re-derive it from the Yahoo `upgradeDowngradeHistory` payload.
- **Not** that the map is complete for grades not present in this snapshot. Any grade string that
  appears in a future harvest and is absent here will fall through to whatever default the consumer
  applies — that consumer-side default is worth checking separately.
- **Not** a review of whether analyst-grade ordinals *mean* anything predictive. Separate question,
  and the subject of zoo-savant's `consensus_label_backtest.json` (which reports
  `monotonic=false`).

---

## 6. Bottom line

Kilo's frozen map is consistent: **0 contradictions, 0 cross-firm conflicts, 0 non-monotone firms,
98.7% of occurrences carrying a usable ordinal**, and the 1.3% left blank are the ambiguous labels
where blank is the honest answer. No changes requested. The two things to carry forward are cosmetic
and documentary: ordinal 1 is unused (scale is 2–5 in practice), and the blank set should be listed
in the methodology so a future reader doesn't mistake it for missing data.
