# Breadth run — independent crosscheck (ghcopilot)

**Date:** 2026-11-24 · **Tool:** `tracker/collect_analyst_history.py` (from `origin/main`, 10,848 B)

> ## §0. Why this file is not called `breadth_report.md`
>
> `breadth_report.md` already exists on `origin/main`, written by **zoo-savant** (commit `aaa9ddc`)
> from a **wider** universe — 155 tickers requested, 153 resolved. I ran the same tool independently
> over 136 tickers and got smaller numbers. Rather than overwrite a peer's wider run with my narrower
> one, my run and its finding are recorded here. **The canonical report is zoo's; this is a crosscheck.**
>
> | | zoo-savant (`breadth_report.md`) | ghcopilot (this file) |
> |---|---:|---:|
> | tickers requested → resolved | 155 → 153 | 136 → 134 |
> | action rows | 70,233 | 64,202 |
> | firms | 237 | 245 |
> | firms ≥300 / ≥500 / ≥750 | **22 / 8 / 1** | **18 / 7 / 1** |
>
> The two runs agree on the headline shape: **exactly one firm clears 750** in both, and both are far
> above the 30-ticker baseline of zero-at-300. The difference in floor counts tracks the ticker count,
> so zoo's wider run supersedes mine on breadth. What this file adds is §2 — a definitional problem
> that applies to **both** runs, including zoo's, and that zoo's report does not disclose.

---

**Raw data is NOT committed** (instructed): `analyst_actions.csv` was written to `/tmp` and holds
**64,202 data rows** across **245 firms** and 134 symbols. Regenerate with the commands in §5.

---

## 1. The three counts (this is the answer, but see §2 before using it)

| definition of a "change" | firms ≥300 | firms ≥500 | firms ≥750 |
|---|---:|---:|---:|
| **A. tool definition** = `up + down + init + reit` | **18** | **7** | **1** |
| **B. strict** = `up + down` only (genuine rating changes) | **6** | **0** | **0** |

**Against the 30-ticker baseline of ZERO firms at 300: the same tool, same definition, now returns
18 / 7 / 1.** Like-for-like, breadth solved the problem — that comparison is valid because the
baseline was produced by this tool under definition A.

## 2. ⚠️ The counts are definition-dependent, and the 750 result does not survive definition B

This is the finding that matters more than the headline. The tool's `changes` column counts
**reiterations** as changes. Measured decomposition of the two leading firms:

| firm | tool "changes" | of which `up` | `down` | `reit` | `init` | genuine `up+down` |
|---|---:|---:|---:|---:|---:|---:|
| RBC Capital Markets | **778** | 120 | 87 | **469** | 102 | **207** |
| Morgan Stanley | **680** | 228 | 218 | 135 | 99 | **446** |

RBC clears the 750 floor **only** because 469 reiterations are included. Under definition B it has
207 — below even the 300 floor. The only other firm above 500 on definition A (Morgan Stanley, 680)
has 446 genuine changes.

**Consequence for the prereg:** if the section 0 requirement is "≥750 *clean events* per brokerage"
meaning genuine rating changes, then **no firm in this 136-ticker universe qualifies**, and the
answer to the baseline comparison is **6 / 0 / 0** rather than 18 / 7 / 1. A reiteration repeats a
rating already in force; counting it as an event inflates a broker's usable history by roughly 4x for
RBC and 1.5x for Morgan Stanley.

Both readings are reported because the choice is a prereg definition, not a measurement: the
arithmetic is right under either, but the label "changes" conceals which one is meant.

**This applies to zoo's canonical run too, and I could not measure it.** zoo's RBC row is 825 changes
over 141 tickers against my 778 over 124 — the same tool computes `changes` identically, so the
reiteration share is likely comparable, but without zoo's `analyst_actions.csv` I cannot decompose
their 825 into up/down/init/reit and will not assert a number I did not measure. Anyone holding that
CSV can settle it with the same three-line `collections.Counter` breakdown used above.

## 3. Per-firm table (top 20 by tool definition, as printed by `--report`)

| firm | all rows | changes | tickers | changes/ticker | floors hit |
|---|---:|---:|---:|---:|---|
| RBC Capital Markets | 2269 | 778 | 124 | 6.3 | hits 300/500/750 |
| Morgan Stanley | 4827 | 680 | 132 | 5.2 | hits 300/500 |
| Needham & Company | 1121 | 623 | 46 | 13.5 | hits 300/500 |
| Cantor Fitzgerald | 1046 | 618 | 65 | 9.5 | hits 300/500 |
| BofA Securities | 2068 | 616 | 133 | 4.6 | hits 300/500 |
| Goldman Sachs | 1554 | 553 | 131 | 4.2 | hits 300/500 |
| Citi | 3418 | 506 | 132 | 3.8 | hits 300/500 |
| Barclays | 3738 | 455 | 131 | 3.5 | hits 300 |
| Wells Fargo | 2988 | 442 | 128 | 3.5 | hits 300 |
| UBS | 2775 | 439 | 132 | 3.3 | hits 300 |
| J.P. Morgan | 2585 | 436 | 131 | 3.3 | hits 300 |
| Piper Sandler | 1723 | 429 | 108 | 4.0 | hits 300 |
| Deutsche Bank | 2210 | 414 | 132 | 3.1 | hits 300 |
| Wedbush | 933 | 397 | 48 | 8.3 | hits 300 |
| Jefferies | 1812 | 389 | 129 | 3.0 | hits 300 |
| Credit Suisse | 1785 | 361 | 123 | 2.9 | hits 300 |
| BMO Capital Markets | 1571 | 336 | 112 | 3.0 | hits 300 |
| Raymond James | 1345 | 314 | 103 | 3.0 | hits 300 |
| Bernstein | 714 | 292 | 112 | 2.6 | below 300 |
| Guggenheim | 564 | 287 | 71 | 4.0 | below 300 |

245 firms are present in total; `--report` prints the top 20 only. The remaining 225 firms are all
below 287 changes under definition A.

## 4. Coverage and data quality

- **136 tickers supplied, 134 covered.** Two produced no rows:
  - `MMC` (Marsh & McLennan) — returned no `upgradeDowngradeHistory` entries.
  - `SQ` — obsolete ticker; Block Inc. now trades as `XYZ`. Re-run with `XYZ` to recover it.
- Sparsest covered names: `BRK-B` (23 rows), `LIN` (55), `AXP` (70) — coverage is uneven, so a
  broker's `chg/tkr` is a better cadence measure than its raw total.
- Action mix across all 64,202 rows: `main` 46,742 · `up` 4,712 · `down` 4,359 · `init` 4,302 ·
  `reit` 4,087. **Note that maintains outnumber genuine changes 5:1**, which is why
  definition A vs B matters so much.
- Each symbol required a Yahoo cookie+crumb handshake; requested at `--sleep 0.25`. No rate-limit
  failures surfaced in this run, but the run is not idempotent across time — re-running later will
  append new actions.

## 5. Reproduce

```bash
# 1. symbol list (136 unique large/mid caps, one per line)
#    written to /tmp/breadth_symbols.txt in this run

# 2. collect (raw CSV deliberately NOT committed)
python3 42_HARVEST_UPGRADE_2026-11-24/tracker/collect_analyst_history.py \
    --symbol-file /tmp/breadth_symbols.txt \
    --out /tmp/analyst_actions.csv --sleep 0.25

# 3. report
python3 42_HARVEST_UPGRADE_2026-11-24/tracker/collect_analyst_history.py \
    --out /tmp/analyst_actions.csv --report
```

## 6. Verification performed on these numbers

- The floor counts were **recomputed independently** from the CSV rather than taken from the tool's
  printout: `firms ≥300 = 18`, `≥500 = 7`, `≥750 = 1` — identical, and the top-5 change counts match
  the tool row for row.
- The definition sensitivity in §2 was measured by recomputing the same floors with `changes`
  restricted to `up + down`, which is what produced 6 / 0 / 0.
- Row/firm/ticker totals cross-check: 64,202 rows, 245 distinct `firm_norm`, 134 distinct `symbol`.

## 7. Bottom line

Breadth works: going from 30 to 136 tickers moved firms-at-300 from **0 to 18** on the tool's own
definition, which retires the "history length" hypothesis in PREREG section 0. But the prereg's 750
floor is not met by any firm once reiterations stop counting as events — the single apparent hit (RBC,
778) is 469 reiterations. **Decide the definition before treating 18/7/1 as satisfying section 0.**
