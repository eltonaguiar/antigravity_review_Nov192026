# Track A repair — `tracker/firm_skill_weights.csv` (blank metrics)

**Repairer:** ghcopilot · **Date:** 2026-11-24
**Target:** `42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv`
**Tools:** `tracker/placebo_dateswap.py` (190 lines, present and working)

---

## Verdict: NOTHING IS COMPUTABLE, and the reason is a data limit, not a measurement

**The three counts:**

| # | question | count |
|---|---|---:|
| 1 | firms with a **COMPUTABLE** effect | **0** |
| 2 | firms that **beat placebo** | **0** |
| 3 | firms **indistinguishable** from placebo | **0** |

All three are zero for the same reason: **no firm clears the clean-event floor**, so no effect was
ever computed. `underpowered` on every row is therefore correct — but it is a statement about data
availability, *not* evidence that firm skill is absent.

**Largest `n_clean_events` among all firms: 551 (BofA Securities)** — **199 short** of the 750 floor.
The file's own trailing note agrees, and even names the remedy: "add ~27 more tickers with BofA
coverage (551 clean events now, 750 floor; ~7.5 events/ticker)".

## 1. Row accounting — the file does not contain 221 firms

The brief says 221 firms. Measured:

| quantity | value |
|---|---:|
| total lines | 222 |
| after the header | 221 |
| of which blank lines | 1 |
| of which a `#` comment line | 1 |
| **real firm rows** | **219** |

So 221 was the *line* count after the header, not the firm count. The extra "rows" are a blank line
and an **unquoted `# next_probe:` sentence containing commas**, which any standard CSV reader parses
as a firm named `"# next_probe: add ~27 more tickers with BofA coverage (551 clean events now"`.
That is worth fixing at the source: prose belongs in a companion `.md`, or must be quoted as a single
field, or every consumer will silently gain a phantom firm with blank metrics.

## 2. How many firms clear each floor

| floor | firms clearing it |
|---|---:|
| ≥300 clean events | 9 |
| ≥500 clean events | 1 |
| **≥750 clean events** | **0** |

Top five by `n_clean_events`: 551, 473, 454, 448, 359. The distribution stops well short of 750 —
consistent with the breadth work: a firm generates roughly 5–7.5 clean events per covered ticker, so
750 needs ~100–150 tickers of that firm's coverage, which no firm has yet.

## 3. The blanks are correct, and the mechanism is fine — only the inputs are missing

- `mean_net_excess_bps` non-blank on **1 of 220** parsed rows (that one is the phantom comment row,
  so effectively **0 of 219** real firms).
- `placebo_p95_bps` non-blank on **1 of 220**, same phantom.
- `verdict` = `underpowered` on all 219 real firms.

I did **not** fabricate the two metrics. Computing them needs inputs that are not in the repository:

| required by `placebo_dateswap.py` | present in repo? |
|---|---|
| `--events events.json` (per-firm, per-ticker, dated rating events) | **no** |
| `--prices prices.csv` (daily prices for the 63-day within-ticker date swap) | **no** |

The tool itself is sound — `python3 placebo_dateswap.py --selftest` runs and returns `verdict: FAIL`
with `VERDICT: FAIL  (must be FAIL)`, i.e. the harness is a FAIL-required self-test and it behaves
exactly as designed. **The gap is data, not machinery.** (`analyst_actions.csv` is deliberately not
committed, which is right for a 122k-row file — but it leaves every Track A metric uncomputable by
anyone else, including a reviewer.)

## 4. Re-issued verdicts

No verdict changes, because no threshold was crossed. To make that unambiguous rather than implied,
the correct verdict string is the one already there — `underpowered` — read as **"not measured"**.
I did not overwrite the CSV: restating 219 verdicts that already say the right thing would churn a
peer's artifact without adding information, and the blank metrics are honest blanks.

## 5. What would make this computable

1. **Commit a small aggregate**, not the raw events: `firm_norm, n_clean_events, mean_net_excess_bps,
   placebo_p95_bps` is already the schema — it just needs values, which needs step 2.
2. **Commit per-event events + prices for the top N firms only** (e.g. the 9 firms ≥300 events), so
   the placebo is reproducible at a fraction of the file size.
3. **Get BofA over 750** — approximately 27 more tickers with BofA coverage at the observed cadence.

---

next_probe: publish `events.json` + `prices.csv` for the **9 firms with ≥300 clean events** (not all 219) so `placebo_dateswap.py` can be re-run by a reviewer and `mean_net_excess_bps` / `placebo_p95_bps` become reproducible; then extend BofA's universe by ~27 tickers to put the first firm over the 750 floor, which is the smallest change that converts this track from *unmeasured* to *measured*.
