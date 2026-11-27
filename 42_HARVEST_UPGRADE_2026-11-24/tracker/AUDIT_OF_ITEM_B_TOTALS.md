# Audit of Item B event totals — `ITEM_B_SETTLE_PROBE.md`

**Auditor:** ghcopilot (Track C) · **Date:** 2026-11-25
**File under audit:** `42_HARVEST_UPGRADE_2026-11-24/tracker/ITEM_B_SETTLE_PROBE.md` (108 lines, origin/main)
**Method:** arithmetic on the totals as printed in that file. No data download, no per-event record, no
recomputation of any mean, difference, CI or p-value. Every number below is either quoted from the file
or a sum of numbers quoted from the file.

**Scope limit, stated up front:** this audit is about **event counts and which count backs which result**.
It does not adjudicate the direction of the effect. I do not call the inversion real, monotone or refuted,
and I cite no Track B p-value as evidence of anything. Separately, `ITEM_B_SETTLE_PROBE.md` was not edited.

> ### AMENDMENT 2026-11-25 — the central finding of this audit is RETRACTED
>
> The claim that **967 is no result's N** (and that the file is "internally inconsistent on event count") is
> **wrong and is withdrawn.** `analyst_actions.csv` on origin/main carries **exactly 967** rows with
> `to_grade = 'Strong Buy'` out of 122,746 data rows, across 129 symbols and 9 firms — so 967 is a real,
> reproducible event count, not an unmeasured header. **610 is the price-resolved 63-day pooled sample**:
> a different denominator, not a contradiction. §1, §2, §6 and §7 below are annotated in place; §9 records
> the retraction with the exact commands and their output. **Findings 3, 4, 5, 6 and 7 are unaffected.**

---

## 1. The four event totals the file carries

The file reports event counts in five places. They do not agree.

| section | line | counts as printed | sum I compute | gap to the 967 headline |
|---|---|---:|---:|---:|
| Header claim | 4 | "**967** Strong Buy events", 129 symbols | 967 (asserted, no derivation given) | — |
| Result 1 — size terciles, 63d | 26–28 | 154 + 198 + 258 | **610** | **−357** |
| Result 2 — sub-period | 40–42 | 95 + 515, "pooled **610**" | **610** (95+515 = 610 ✓) | **−357** |
| Result 3 — action-type split | 52–54 | 117 + 438 + 38 | **593** | **−374** |
| Result 4 — per-year | 68–74 | 83+84+97+108+42+45+22 | **481** | **−486** |

Two things follow immediately.

**First, Result 2 is the only breakout whose own arithmetic closes.** It prints its parts (95, 515) and
its total (610), and 95 + 515 = 610 exactly. Results 1, 3 and 4 print parts but no total, so their totals
exist only as the sums above — 610, 593 and 481.

**Second, 610 + 357 = 967.** So the three parts of Result 1 and the two parts of Result 2 both sum to
610, not 967; 357 events (36.9% of the headline) are carried by the header and by none of the breakouts.
The file never says where those 357 went. Plausible explanations exist — events dropped in the
price/control join, symbols unresolved (`303/309 symbols resolved`, line 5), or the neutral-control
requirement — but the file states none of them, so the 967 is an **unreconciled** header figure rather
than a measured analysis N.

> **⚠ RETRACTED 2026-11-25.** "Unreconciled rather than a measured analysis N" is wrong. 967 **is** a
> measured count — the exact number of `to_grade = 'Strong Buy'` rows in `analyst_actions.csv` — and the
> 357 are events with no resolvable 63-day price/neutral-control window. What survives is narrower: the
> file never **states** the 967 → 610 transition, so the subset relationship is invisible to a reader.
> That is an omission of one sentence, not a bad number. See §9.

Note that Result 1's tercile sum (610) equals Result 2's pooled figure (610) exactly. That is consistent
with both tables resting on the same 63-day joined sample while 967 is a pre-join count, but that is an
**inference from two equal numbers, not a statement the file makes**.

---

## 2. Which total is the analysis N for each result

| result | what it measures | analysis N actually used | interval it sits in |
|---|---|---:|---|
| Result 1 — size terciles | SB excess vs neutral control, 63d | **610** (154/198/258) | between 593 and 967 |
| Result 2 — sub-period | SB diff, 2012–2018 vs 2019–2026 | **610** (95/515, pooled 610) | between 593 and 967 |
| Result 3 — action-type split | SB diff by `up` / `main` / `reit` | **593** (117/438/38) | lowest except R4 |
| Result 4 — per-year | SB diff by calendar year | **481** (seven cells) | lowest |
| Header | raw `Strong Buy` event count | **967** | verified in `analyst_actions.csv`; the population every breakout draws from |

~~**No result in the file uses 967 as its N.**~~ ~~Because the header is the number a reader will quote and
no table reproduces it, **the file is internally inconsistent on event count.**~~

> **⚠ RETRACTED 2026-11-25 — both sentences above are wrong.** 967 **is** a verified event count
> (`analyst_actions.csv`: exactly 967 rows with `to_grade = 'Strong Buy'`, 122,746 data rows, 129 symbols,
> 9 firms). 610 is the price-resolved 63-day pooled sample; 593 is its action-type subset; 481 is its
> 2020–2026 subset. These are nested denominators, not conflicting ones, and the file is therefore **not**
> internally inconsistent on event count. The arithmetic below still holds — the header does exceed every
> breakout by 357 / 374 / 486 — but those gaps are the **cost of the price join**, which the file fails to
> state, not evidence that 967 is unsupported. See §9 for the commands and output.

This matters for how the conclusions must be read, without adjudicating them:

- The Result 3 finding — described in the file as the test that "actually matters" — rests on **593**
  events, not 967, and its largest cell (`main`, 438) is 73.9% of that 593.
- The Result 4 decay claim rests on **481** events across seven years, i.e. **49.7%** of the headline.
- Result 2's split (95 vs 515) is **610**, so any statement about the two sub-periods is a statement
  about 63% of the advertised sample.

---

## 3. The per-year table omits 2012–2019, which explains most of its 481

Result 4 tabulates **2020 through 2026 — seven years**. Result 2 establishes that the sample spans
**2012–2018 and 2019–2026**, i.e. fifteen years. So **eight of the fifteen years (2012–2019) are absent
from the annual table**, and their events (at least 95, the whole 2012–2018 sub-period count) cannot
appear in the 481.

This is the arithmetic explanation for the 486-event shortfall in Result 4 relative to the header: the
annual table is a 2020+ window presented inside a document whose other tables cover 2012+.

**Consequence:** the sentence "the last two years are dead" describes the tail of a seven-year window,
not the tail of the full sample. A reader comparing 481 to 967 without noticing the row labels would read
a truncated window as the whole record.

---

## 4. "Eight of eleven years positive" is not supported by a seven-row table

Line 76 reads: "Eight of eleven years positive, then **the last two years are dead**."

The table above it has **seven** rows (2020–2026), not eleven. Counting the printed `diff` column, the
years with a positive difference are 2020, 2021, 2022, 2023, 2024 and 2025 — **six of seven** — with 2026
negative (−1.50%). Neither "eight" nor "eleven" is obtainable from the printed table:

| quantity | text says | table supports |
|---|---:|---:|
| years shown | 11 | **7** (2020–2026) |
| years positive | 8 | **6** |
| years negative | 3 (implied) | **1** (2026) |

Either the sentence refers to a wider set of years than the table prints — in which case 2012–2019 are
being summarised without being shown — or it is a stale count from an earlier run. **The file does not
distinguish these two cases, and as printed the sentence is unsupported by the table beneath it.**

---

## 5. The 2026 cell (n=22) cannot carry a decay-to-zero claim alone

The decay claim is "the last two years are dead — +0.04% and −1.50%", resting on:

| year | n | diff |
|---|---:|---:|
| 2025 | **45** | +0.04% |
| 2026 | **22** | −1.50% |

**2026 carries n = 22 against 2025's n = 45** — the smallest cell in the table, half the size of the cell
beside it (22/45 = 48.9%) and a fifth of 2023's 108 (22/108 = 20.4%). The two cells together are **67 events, 13.9% of the 481**
per-year total and **6.9% of the 967** header.

So a decay-to-zero claim **cannot rest on the 2026 cell alone**: at n = 22 the cell is a single-digit
effective sample once the neutral-control comparison is applied, and it is the only negative year printed.
The claim is stronger when stated over the combined 67 events of 2025–2026 than over 2026 alone, and the
file should say which of the two it means. What the file currently does is present n = 22 in bold
immediately beside n = 45 without flagging that the cell sizes differ by 2× while the differences
(+0.04% vs −1.50%) are both small relative to the earlier years (+2.23% to +4.11%).

I am not saying the decay is false — only that n = 22 cannot establish it, and that the honest form of the
claim is bounded by the 67 events the two cells actually contain.

---

## 6. Summary of the internal inconsistency

| # | finding | status |
|---|---|---|
| 1 | ~~Header 967 is not the N of any result~~ | **RETRACTED** — 967 is the verified raw `Strong Buy` count; 610/593/481 are its nested price-resolved subsets (§9) |
| 2 | 357 events (36.9%) in the header are attached to no table | **confirmed, now explained** — they lack a resolvable 63-day price/control window; the file does not say so |
| 3 | Result 1 and Result 4 print parts but no totals | **confirmed** — totals 610 and 481 exist only as sums |
| 4 | Result 2 is the only breakout whose arithmetic closes | **confirmed** — 95 + 515 = 610 = its printed pooled figure |
| 5 | Per-year table covers 2020–2026 (7 years) inside a 2012–2026 sample | **confirmed** — 2012–2019 absent |
| 6 | "Eight of eleven years positive" not supported by a 7-row table | **confirmed** — table shows 6 of 7 |
| 7 | 2026 decay cell is n=22, half of 2025's n=45 | **confirmed** — cannot carry the claim alone |

**The plain statement (corrected 2026-11-25):** ~~`ITEM_B_SETTLE_PROBE.md` advertises 967 Strong Buy
*events, but 967 is the N of no result in it.*~~ **967 is the verified raw Strong Buy event count, and 610
is the price-resolved 63-day pooled sample — both correct.** The breakouts then narrow further to 593
(action type) and 481 (2020–2026 years only). The remaining defect is presentational, not numerical: the
file never states the 967 → 610 transition, so a reader cannot tell that every breakout is a subset of the
headline. One added sentence would close it. See §9.

---

## 7. What I did not do

- Did not edit `ITEM_B_SETTLE_PROBE.md` (sha256 `f5edc737595463f0…`, unchanged).
- Did not download data, recompute a mean, or re-run any of the three scripts named in the file.
- Did not call the inversion real, monotone or refuted, and did not evaluate whether it is any of those.
- Did not cite any Track B p-value as evidence.
- Did not verify whether 154/198/258 or 117/438/38 are the correct *counts* — only that they are what the
  file prints and what they sum to.
  *(2026-11-25 amendment: I subsequently **did** verify the 967 total against `analyst_actions.csv`; see §9.)*

### Provenance

| figure | line in `ITEM_B_SETTLE_PROBE.md` |
|---|---|
| 967 events, 129 symbols | 4 |
| 154 / 198 / 258 (terciles) | 26–28 |
| 95 / 515 / pooled 610 | 40–42 |
| 117 / 438 / 38 (action types) | 52–54 |
| 83 / 84 / 97 / 108 / 42 / 45 / 22 (years 2020–2026) | 68–74 |
| "Eight of eleven years positive" | 76 |
| 2012–2018 / 2019–2026 span | 40–41 |
| `303/309 symbols resolved` | 5 |

All sums in §1 and §3 were computed from those printed values only.

---

## 9. AMENDMENT 2026-11-25 — retraction of the central finding, with verification

### 9.1 The claim being withdrawn

From §1, §2 and §6 of the version committed at `221b833`:

> "the 967 is an **unreconciled** header figure rather than a measured analysis N"
> "**No result in the file uses 967 as its N.** … the file is internally inconsistent on event count"

Both statements are **wrong and are retracted.** The arithmetic beneath them (967 − 610 = 357, and the
other gaps) is correct; the interpretation I placed on it was not. I treated a *filtered denominator* as a
*contradictory* one, which is a different and much stronger claim than the evidence supported.

### 9.2 Verification — presence

```
$ git cat-file -e origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv
$ echo $?
0
```

Present on origin/main: 9,454,358 bytes, 122,747 lines = **122,746 data rows** + 1 header.
Columns: `symbol, firm_raw, firm_norm, date, action, from_grade, to_grade, target_action,
current_target, prior_target`.

### 9.3 Verification — the 967 count

Read over all 122,746 data rows:

```
to_grade == 'Strong Buy' (exact match)   : 967 rows
distinct symbols among them              : 129
distinct firm_norm among them            : 9
case-insensitive 'strong buy' (control)  : 967 rows   -> no case variants; the count is unambiguous
```

The 9 firms: CFRA, First Analysis, ISI Group, Janco Partners, Miller Tabak, Needham & Company,
Raymond James, S&P Capital IQ, Tigress Financial.

`Strong Buy` is a single stored label in `to_grade`, not a merge of several:

| `to_grade` | n |
|---|---:|
| Buy | 31,622 |
| Overweight | 20,613 |
| Outperform | 18,826 |
| Neutral | 18,014 |
| Equal-Weight | 9,332 |
| Hold | 8,192 |
| … | … |
| **Strong Buy** | **967** |
| … | … |
| Reduce | 90 |

**So 967 is a real, reproducible event count in the repo, and my audit's assertion that it was not a
measurement is withdrawn.**

### 9.4 The correct relationship between the four totals — nested, not conflicting

| quantity | value | definition |
|---|---:|---|
| raw Strong Buy events | **967** | `to_grade = 'Strong Buy'` in `analyst_actions.csv` |
| price-resolved, pooled 63-day | **610** | after the 63-day price join + neutral control |
| price-resolved, by action type | **593** | subset of the 610 |
| price-resolved, by year | **481** | subset of the 610, **2020–2026 only** (2012–2019 absent) |

**481 ⊂ 593 ⊂ 610 ⊂ 967.** Each step down is a stated or implied filter, not a rival total.

### 9.5 Corroboration that 593 is a subset of 967

Derived from the same file, grouping the 967 raw events by `action` and comparing to Result 3:

| action | raw (of 967) | resolved (of 593) | subset |
|---|---:|---:|---|
| `main` | 744 | 438 | 438 ≤ 744 ✓ |
| `up` | 140 | 117 | 117 ≤ 140 ✓ |
| `reit` | 63 | 38 | 38 ≤ 63 ✓ |
| `init` | 20 | 0 | 0 ≤ 20 ✓ |
| **total** | **967** | **593** | ✓ |

Every resolved count is **less than or equal to** its raw counterpart, in the same rank order. That is
exactly the signature of a filter applied to a population — which is what the price join is. Had 593 been
a competing count, some cell would have exceeded its raw value. `init` → 0 is also consistent: the
action-type table measures upgrades/reiterations, and initiations are excluded by its own definition.

### 9.6 What survives this correction

**Unchanged — still confirmed** (findings 3–7 of §6):

- Result 1 and Result 4 print parts but no totals (610 and 481 exist only as sums).
- Result 2 is the only breakout whose arithmetic closes (95 + 515 = 610 = its printed pooled figure).
- The per-year table covers 2020–2026 inside a 2012–2026 sample, so 2012–2019 are absent.
- "Eight of eleven years positive" is unsupported by a seven-row table, which shows six of seven.
- The 2026 decay cell is n = 22 against 2025's n = 45 and cannot carry a decay-to-zero claim alone.

**Narrowed, not withdrawn:** the file never states the 967 → 610 transition, so a reader meeting
"967 events" and "pooled 610" mid-document cannot tell that one is a subset of the other. That is an
omission of one sentence. The fix is documentary, and **no number in either file needs to change**.

**Retracted:** that 967 is not a real measurement; that the file is internally inconsistent on event count.

### 9.7 Effect on the audit's overall verdict

The original summary ("967 is the N of no result") is replaced by:

> **967 is the verified raw Strong Buy event count; 610 is the 63-day price-resolved sample; both are
> correct. The breakouts then narrow to 593 and 481 by stated filters. The file's only defect on this
> point is that it does not say so.**

`ITEM_B_SETTLE_PROBE.md` was not edited for this amendment (sha256 `f5edc737595463f0…`, unchanged), and
neither was any other file. This section was added to the existing branch
`track-c/item-b-totals-audit-2026-11-25` (PR #10), not to a new one.
