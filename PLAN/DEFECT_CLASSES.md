# Defect classes — why every wrong number in this programme was wrong

**Rule of this document:** a number that is arithmetically correct can still be
false. Twelve defects were found across the fund report, the 1000-cell sweep and
the PROVEIT scenarios. **Not one was a miscalculation.** Each was a label placed
on the wrong quantity, and each survived review by prose because the prose was
internally consistent.

That is not a discipline problem — it is a *detection* problem. You cannot catch
a mislabelled number by reading; you catch it by reconciling the artifact against
itself. `PLAN/tools/artifact_lint.py` does that.

## The five classes

### 1. Estimand mismatch — two different quantities, one name

The two costliest defects in the programme.

| what was claimed | what the field actually held | damage |
|---|---|---|
| fund CAGR as *net* | `cagr_pct` — **gross**; `net_cagr_pct` was a sibling | produced a false "non-deterministic CAGR" claim, retracted |
| BND "4.11% YTM" | a **distribution yield** (`bnd_yield_source: "yield"`) | understated the bond case |
| wrapper cost −1.67pp | ZAG.TO (**Canadian** bonds) vs BND (**US** bonds) | false finding; corrected to exposure-matched pairs, −3.31pp also withdrawn |
| "SPY rose 437.19 → 754.37" beside a CAGR | account entered at **374.84**, not 437.19 | a different pair of quantities from the one annualised |
| "72% in cash" | `idle_cash_pct` is cash over **ending NAV** (72.3%), not over starting capital (69.0%) | directionally fine, materially ambiguous |

In every case **both numbers were present in the artifact.** Nothing was missing.
The error was choosing which one to quote, and no reader could tell.

→ lint rule `R7-ESTIMAND` fires when qualifier pairs (`gross`/`net`,
`ytm`/`yield`, `local`/`usd`, `nominal`/`real`, `arithmetic`/`geometric`) coexist
in one object with different values.

### 2. Denominator mismatch — the same count, two year-lengths

`n_days = 1255` is **trading** days. Divided by 252 it is 4.98 years and
reproduces the stored 9.18% CAGR. Divided by 365.25 — the plain reading of a
field called `n_days` — it is 3.44 years and yields **13.58%**. A 4.40pp error
available to anyone who trusts the field name.

→ `R1-DURATION` compares a `*_days` field against both conventions and against
the `window`, and flags the field when only one reading matches.

### 3. Data-source substitution — asked for one thing, silently served another

- 15-minute and 4-hour cells were measured on **daily** bars. `breakout/15m` and
  `breakout/1d` both returned n=82. Four cells were invalidated and re-measured.
- The 1-hour price cache is a yfinance CSV with **two** header rows and a blank
  trailing row.

Both are silent: no error, no null, just a plausible number computed from the
wrong resolution.

→ Not statically detectable. Guarded instead by an explicit *intraday returns
`bars=0` rather than falling back to daily* contract in `measure_cell.py`, and by
a regression test that asserts the 15m and 1d cell counts differ.

### 4. Inert parameter — accepted, recorded, ignored

- `rebal` was passed to the fund backtest and never read; MER was charged
  unconditionally in `metrics()`.
- `merblend` — the same defect a second time, in the same file.

Any sensitivity analysis across an inert parameter is fabricated evidence: the
output cannot change. `merblend` produced a table of identical rows that looked
like a finding of insensitivity.

→ Not statically detectable without instrumenting the engine. Guarded by a test
that perturbs each parameter and asserts the output moves.

### 5. Provenance loss — a path that only existed once

`SRC` was written as an absolute path. Every other checkout therefore judged the
artifact **STALE** — not because the data was old, but because the path did not
resolve on that machine.

→ `R5-PROVENANCE` flags absolute paths in provenance-ish keys.

## What the linter actually caught, unaided

Run against the committed PROVEIT artifacts before any of the above was
explained to it:

- **`R1-DURATION`** → the `n_days` defect, HIGH, in both JSONs. Rediscovered
  independently.
- **`R6-UNSOURCED`** → **15** numbers in the README present nowhere in the
  artifacts: the entry closes (SPY 374.84, TLT 92.83, GLD 157.87, BIL 76.38),
  the leftover cash ($207.12), idle-vs-starting-capital (69.0%), the
  trading-day years (4.98), and the wrong-denominator CAGR (13.58%).

That second one is the important result. `$374.84` had been asserted in the PR
body for hours with **nothing committed behind it**. The linter found it by
asking a question no reviewer asks: *which file contains this number?*

Fixing it properly meant generating the values rather than typing them —
`PLAN/tools/derive_provenance.py` re-fetches the prices, recomputes the entry
bar and allocation, cross-checks its own output against the committed sim, and
**refuses to write if the check fails**. After that, `R6` reports **0**.

## Honest limitations

1. **`R6` is noisy on HTML.** Run against `docs/PROVEIT/index.html` it reports
   `404`, `600`, `128128` — CSS values, HTTP status codes in prose, and digit
   runs from adjacent numbers. It is reliable on markdown. Do not point it at a
   stylesheet-heavy page and trust the output.
2. **Classes 3 and 4 are not caught at all.** They need instrumented engines, not
   static analysis. Pretending otherwise would be the worst possible outcome for
   a tool whose purpose is to stop people trusting unverified numbers.
3. **`R2-CAGR` only verifies internal consistency.** A CAGR that reconciles with
   its own start/final/duration can still be computed from the wrong window. It
   catches mislabelled durations, not mislabelled periods.
4. **The 1254-vs-1255 bar drift is real.** Re-fetching today returns one bar
   fewer than the committed run, so terminal closes differ (757.12 vs 754.37).
   The provenance file records them under `refetch_last_bar_closes` and says
   explicitly that they are not interchangeable. Substituting one for the other
   would be an instance of class 1, committed by the tool built to catch class 1.

## Use

```bash
# report
python3 PLAN/tools/artifact_lint.py ARTIFACT.json [MORE.json ...] [--claims README.md]

# CI: fail on NEW findings only
python3 PLAN/tools/artifact_lint.py ... --baseline PLAN/lint_baseline.json

# accept current findings as the baseline (do this only for documented ones)
python3 PLAN/tools/artifact_lint.py ... --write-baseline PLAN/lint_baseline.json
```

A baseline exists so one known, documented upstream defect does not block every
future change — the failure mode that gets a gate switched off. It is not a way
to make a finding go away: the two acknowledged entries are `R1-DURATION` on the
committed JSONs, which are generated upstream and cannot be renamed without
regenerating the results.
