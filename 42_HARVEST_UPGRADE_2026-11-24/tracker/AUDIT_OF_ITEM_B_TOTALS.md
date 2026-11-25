# Audit of Item B event totals — `ITEM_B_SETTLE_PROBE.md`

**Auditor:** ghcopilot (Track C) · **Date:** 2026-11-25
**File under audit:** `42_HARVEST_UPGRADE_2026-11-24/tracker/ITEM_B_SETTLE_PROBE.md` (108 lines, origin/main)
**Method:** arithmetic on the totals as printed in that file. No data download, no per-event record, no
recomputation of any mean, difference, CI or p-value. Every number below is either quoted from the file
or a sum of numbers quoted from the file.

**Scope limit, stated up front:** this audit is about **event counts and which count backs which result**.
It does not adjudicate the direction of the effect. I do not call the inversion real, monotone or refuted,
and I cite no Track B p-value as evidence of anything. Separately, `ITEM_B_SETTLE_PROBE.md` was not edited.

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
| Header | no result attached | **967** | highest, used by nothing |

**No result in the file uses 967 as its N.** The header's 967 exceeds every breakout, by 357 (Results 1
and 2), 374 (Result 3) and 486 (Result 4). Because the header is the number a reader will quote and no
table reproduces it, **the file is internally inconsistent on event count.**

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
| 1 | Header 967 is not the N of any result | **confirmed** — every breakout is ≤ 610 |
| 2 | 357 events (36.9%) in the header are attached to no table | **confirmed** — unreconciled, unexplained |
| 3 | Result 1 and Result 4 print parts but no totals | **confirmed** — totals 610 and 481 exist only as sums |
| 4 | Result 2 is the only breakout whose arithmetic closes | **confirmed** — 95 + 515 = 610 = its printed pooled figure |
| 5 | Per-year table covers 2020–2026 (7 years) inside a 2012–2026 sample | **confirmed** — 2012–2019 absent |
| 6 | "Eight of eleven years positive" not supported by a 7-row table | **confirmed** — table shows 6 of 7 |
| 7 | 2026 decay cell is n=22, half of 2025's n=45 | **confirmed** — cannot carry the claim alone |

**The plain statement: `ITEM_B_SETTLE_PROBE.md` advertises 967 Strong Buy events, but 967 is the N of no
result in it. The three breakouts use 610, 593 and 481 respectively, and the file never reconciles the
header to any of them.** The conclusions may still hold on their own numbers — that is not what this audit
examines — but a reader cannot tell from this file how many events any stated result actually rests on.

---

## 7. What I did not do

- Did not edit `ITEM_B_SETTLE_PROBE.md` (sha256 `f5edc737595463f0…`, unchanged).
- Did not download data, recompute a mean, or re-run any of the three scripts named in the file.
- Did not call the inversion real, monotone or refuted, and did not evaluate whether it is any of those.
- Did not cite any Track B p-value as evidence.
- Did not verify whether 154/198/258 or 117/438/38 are the correct *counts* — only that they are what the
  file prints and what they sum to.

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
