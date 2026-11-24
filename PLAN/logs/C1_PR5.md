# C1 — PR #5 claim-vs-committed audit

**Repo:** `eltonaguiar/antigravity_review_Nov192026`
**PR:** #5 (`proveit-extended-scenarios-2026-11-24` → `main`), state OPEN, MERGEABLE
**Branch HEAD audited:** `95452d2`
**Auditor date:** 2026-11-24
**Method:** every number below was read out of the committed JSON with `json.load`, never copied from prose. Claims were taken from the live PR body (`gh pr view 5 --json body`) and the committed `README.md`.

## Evidence files

| file | role |
|---|---|
| `PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_2026-11-24T0350Z.json` | scenario sims, keyed `scenarios["<size>"]["buy_hold"\|"annual_rebalance"\|"tp_sl"\|"trend_200"]` |
| `PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/paramscan_2026-11-24T0350Z.json` | same 6 sizes, `summary["<size>"].edge_pp`, `trials_total` |
| `PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/README.md` | prose claims + tables |

Fee model as committed: `commission=0.0`, `spread_bp=5.0`, `fractional_shares=false`, MER `SPY 0.000945 / TLT 0.0015 / GLD 0.004 / BIL 0.00136`. Window `2021-11-15 → 2026-11-13`.

## Claim table

| # | Claim (as written) | Location | Committed value | Source field | Verdict |
|---|---|---|---|---|---|
| C1 | buy-and-hold "identical **9.18% CAGR**" at $10K / $20K / $50K | body + README | `9.18`, `9.18`, `9.18` | `scenarios[*].buy_hold.cagr_pct` | **VERIFIED** — independent geometric recompute over the 1824-day calendar window gives 9.1571% (Δ 0.023pp); over a 252-day trading year gives 9.1817%. Basis-sensitive at the 0.02pp level only. |
| C2 | trend edge "**+1.31 / +1.42 / +1.50pp**" at $10K / $20K / $50K | body + README | `1.31`, `1.42`, `1.50` | `paramscan.summary[*].edge_pp`; equals `best_cagr_pct − hold_cagr_pct` = 10.49−9.18, 10.60−9.18, 10.68−9.18 | **VERIFIED** exactly, arithmetic and stored field agree |
| C3 | TP/SL "**$44.61 / $90.23 / $226.80**" at $10K / $20K / $50K | body + README | `44.61`, `90.23`, `226.80` | `scenarios[*].tp_sl.fees_and_spread` | **VERIFIED** exactly |
| C4 | TP/SL "returns **9.02–9.05%**" attached to all three costs | body + README | $10K = **8.56**, $20K = 9.02, $50K = 9.05 | `scenarios[*].tp_sl.cagr_pct` | **FAILS** — the range silently drops the $10K row. 8.56% is **0.62pp BELOW** the 9.18% hold, so at the size most retail accounts actually have, TP/SL loses to doing nothing. |
| C5 | TP/SL "**indistinguishable from holding**" / "statistically indistinguishable" | body + README | no CI, no bootstrap, no test statistic anywhere in the artifacts | — | **UNSUPPORTED** — single window, one path, no dispersion estimate. "Statistically" is unearned. README's stronger wording is the worse of the two. |
| C6 | "**16 trades**" at those three sizes | body | `16`, `16`, `16` | `scenarios[*].tp_sl.trades` | **VERIFIED** for $10K/$20K/$50K (note: 9 at $300, 18 at $500 — the figure is size-specific, correctly scoped in the sentence) |
| C7 | "a single SPY share cost **$374.84**" | body + `docs/PROVEIT/index.html` | **absent** — 0 hits for `374.84` under the committed PR directory | — | **NOT IN COMMITTED FILES** — unverifiable from the PR. The conclusion it supports (`idle_cash_pct = 72.3`) *is* in the JSON, so the claim is probably right and simply unsourced. |
| C8 | "SPY went **437 → 754**" | body | **absent** — 0 hits | — | **NOT IN COMMITTED FILES** |
| C9 | "idle_cash **72%**" at $300 | body | `72.3` | `scenarios["300"].buy_hold.idle_cash_pct` | **VERIFIED** |
| C10 | "0 PASS / 47 cells … every candidate failed walk-forward" | body + README | cross-reference to the sweep, not asserted from these two files | — | out of scope for C1; not evidence-bearing for this PR |

## Committed data, for reference

| size | hold final | hold CAGR | hold DD | hold fee | TP/SL fee | TP/SL CAGR | TP/SL DD | TP/SL trades | trend CAGR | annual-rebal CAGR |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 300 | 286.50 | −0.92 | −6.98 | 0.05 | 0.96 | −2.04 | −20.71 | 9 | 0.00 | −0.94 |
| 500 | 473.01 | −1.11 | −8.37 | 0.09 | 2.92 | **11.88** | −15.43 | 18 | 9.48 | −1.14 |
| 2000 | 3,030.04 | 8.70 | −13.51 | 0.93 | 8.83 | 8.55 | −13.75 | 16 | 9.29 | 6.17 |
| 10000 | 15,489.06 | 9.18 | −14.20 | 4.99 | 44.61 | **8.56** | −13.80 | 16 | 10.49 | 7.52 |
| 20000 | 30,978.12 | 9.18 | −14.20 | 9.99 | 90.23 | 9.02 | −14.29 | 16 | 10.60 | 7.56 |
| 50000 | 77,445.30 | 9.18 | −14.20 | 24.97 | 226.80 | 9.05 | −14.28 | 16 | 10.68 | 7.67 |

## Defects found

**D1 — the $10K TP/SL row is hidden by a two-size range (C4).** The sentence places three costs next to a range that only two of them fit. A reader concludes TP/SL is flat-to-holding at every size; the committed data says it *underperforms* by 0.62pp at $10K. This is the third time in this programme that a label placed the wrong quantity on one side of a comparison — the same failure class as gross-CAGR-as-net and distribution-yield-as-YTM.

**D2 — "statistically indistinguishable" with no statistic (C5).** There is no CI, no bootstrap, no permutation test in either JSON. The word "statistically" must go, or a dispersion estimate must be committed.

**D3 — `n_days = 1255` is a trading-day count, not calendar days.** Reading it as calendar days (the field's plain meaning) yields 3.436 years and a 13.58% CAGR — a **4.40pp error** against the stored 9.18%. `1255 / 252 = 4.98` years matches the window; `1824` calendar days does not appear. Any downstream consumer that recomputes CAGR from `n_days` gets a wrong answer. Rename to `n_trading_days` or add `n_calendar_days`.

**D4 — $374.84 and 437→754 are asserted but not committed (C7, C8).** The 72.3% idle-cash figure is in the JSON; the share price that causes it is not. Add the entry price to the sim output rather than to prose.

**D5 — selectivity in the body.** The body quotes only the three trend edges. The committed `paramscan.summary` also contains `$500: best_variant = tp_sl, edge = +12.99pp` — the largest edge in the table, an order of magnitude above the ones quoted, and omitted. That row is almost certainly granularity noise (18 trades at $500), but omitting the single most flattering-to-the-strategy number without saying so reads as cherry-picking, and the README does disclose it. The body should either cite it and dismiss it, or say the table is abridged.

## What is solid

The three headline figures the PR is built on — **9.18% hold, +1.31/+1.42/+1.50pp, $44.61/$90.23/$226.80** — all reproduce from the committed files. The arithmetic is correct. The problem is entirely in the framing sentence around C3/C4 and in two unsourced prose numbers.

## Required before merge

1. Replace C4's range with all three values and state that $10K is below holding.
2. Delete "statistically" or commit a dispersion estimate.
3. Rename `n_days` → `n_trading_days` (or add `n_calendar_days`).
4. Commit the SPY entry price ($374.84) into the sim JSON, or drop the number from prose.
5. Add one sentence to the body acknowledging the `$500 / tp_sl / +12.99pp` row.
