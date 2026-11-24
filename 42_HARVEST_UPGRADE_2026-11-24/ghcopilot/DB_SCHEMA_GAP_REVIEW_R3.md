# Round 3 — the pick_type_ref gate, and the two remaining defects

**Measured:** 2026-11-24 ~12:55Z · on `main` @ `fb96ab9` · live `ejaguiar1_stocks`

## Is "reportable cohorts fell to zero" correct?

**Yes — arithmetically correct, right in direction, and it should stay zero for now.**
But the reason deserves precision, because it is not "the signal disappeared".

The gate now reads `COALESCE(pt.min_n, 30)` from `pick_type_ref` per published cell:

| pick_type | min_n | picks | with horizon |
|---|---:|---:|---:|
| BUY_AND_HOLD | 10 | 0 | 0 |
| LONG_TERM | 20 | 0 | 0 |
| POSITION | 40 | 32 | 32 |
| SWING_TRADE | 60 | 3,812 | 3,812 |
| DAY_TRADE | 100 | 117 | 117 |
| UNCLASSIFIED | 999999 | 31 | 31 |

Against a total eligible population (`in_horizon = 1`) of **85 picks**, the best cell holds
**37**. 37 < 60, so zero cohorts report. The previous number — `audit/CRYPTO/1M` 29.73% on
37 — has been correctly retracted: it was a rate published at 62% of the required sample.

**The direction is right.** One global `n >= 30` was the wrong instrument. A day-trade verdict
needs far more resolved observations than a 3-month position verdict, because per-unit-time
cost and noise swamp a day-trade edge. `pick_type_ref` encodes exactly that ordering
(100 > 60 > 40 > 20 > 10) and applying it per cell is more defensible than 30 everywhere.

**But two things must be said plainly:**

1. **`min_n` is defined on the pick type and applied to a triple-stratified cell.** The cell is
   already sliced by (source x asset_class x horizon). With 85 eligible picks estate-wide and a
   threshold of 60 on the dominant type, at most one cell can ever report, and only if >= 71% of
   all eligible picks land inside it. So the gate is currently unsatisfiable *by construction*,
   not merely unmet. That is fine while it tells the truth — but the reporting grain should be
   declared, because a cell of 60 SWING_TRADEs and a cell of 100 DAY_TRADEs are not equally
   credible and the current output cannot express that difference beyond the threshold itself.
2. **The binding constraint is data maturity, not the threshold.** 3,907 of 3,992 picks have no
   mark inside their own horizon window, and the ledger is days old against a 7-day minimum for
   `1M`. Lowering `min_n` to make a number appear would be the exact error this gate exists to
   prevent. Zero is the honest answer and will remain so for weeks.

## The one fix to make before any number is published

**Close the fail-open fallback: `COALESCE(pt.min_n, 30)` -> `COALESCE(pt.min_n, 999999)`.**

Any `pick_type` value not present in `pick_type_ref` — a typo, a newly introduced type, a
backfill that wrote a label before the ref row existed — silently reverts to the permissive
`n = 30` and becomes publishable at half the standard for its own type. `UNCLASSIFIED` is
correctly pinned at 999999 precisely so it can never report; the `COALESCE` default undoes that
guarantee for every type nobody has enumerated yet. This is a one-token change to a view, it
touches no data, and it is the only remaining path by which a cohort can publish without meeting
its type's threshold.

Ranked next, once that is closed: re-point `v_pick_level` at `pick_resolution` (see B below).

## (A) Does `v_pick_latest_mark` recreate the second-source-of-truth problem?

**No.** Verified against the live definitions: `v_pick_latest_mark` reads `picktrack_marks` joined
to `v_pick_last_mark_date`, and none of the view chain references `pick_resolution`. Views are
recomputed on read and cannot drift from base rows, so the diverging-win-rate failure — three
tables each *storing* "the outcome" — remains structurally impossible.

**One implementation hazard, which round-3 review also raised and I agree with.** The
`MAX(mark_date)` self-join returns **both** rows when two marks share a `(pick_id, mark_date)`,
silently restoring mark-row weighting. Measured today: 494 marks across 494 distinct picks, and
**0 duplicate `(pick_id, mark_date)` groups** — so it holds right now, unenforced.
`ROW_NUMBER() OVER (PARTITION BY pick_id ORDER BY mark_date DESC)` is the correct fix, with one
addition the proposal omits: **a deterministic tiebreak on `id DESC`**, or ties inside the same
date still fan out. `ROW_NUMBER` alone changes the failure mode rather than removing it.

## (B) `pick_resolution` or `picktrack_marks` — which is authoritative?

**`pick_resolution` for the verdict; `picktrack_marks` for the observation series.** Neither is
deletable: `v_mark_recomputed` — the drift guard — depends on marks, so recomputation dies
without them.

**The live defect: `v_pick_level` still does not read `pick_resolution`** (verified `False` in the
view text, and no `outcome_source` column). So the table designated authoritative is ignored by
the view that produces every published number. Today that is harmless because
`pick_resolution` holds 0 rows. The moment a resolver starts writing, two live outcome
definitions exist and the page continues to show the mark-derived one.

Action on "the other": leave `picktrack_marks` untouched, re-point `v_pick_level` to LEFT JOIN
`pick_resolution` on `(pick_id, horizon_code)` and fall back to the latest mark only when no
resolution exists, exposing `outcome_source` (`RESOLVED` / `MARK_FALLBACK` / `UNMARKED`).
Also drop the duplicate unique index `uq_resolution` — byte-identical in purpose to
`uq_res_pick_horizon`, both `(pick_id, horizon)`, both unique. It is the signature of a migration
applied twice and doubles the write cost of every resolution insert.

## (C) Can `screened_candidate` reconstruct a multiple-testing denominator?

**Still no, but my round-2 reasoning is now partly stale and should be corrected.**

What changed: `pick_id` and `decision` columns now exist, and `rule_hash` has been widened from
`varchar(32)` to `char(64)` matching `rule_version`. That removes the two structural objections I
raised in round 2 — the link column exists and the rule version is scopeable.

What still blocks it:
1. **`screened_candidate` has 0 rows.** `N_trials` is literally zero. Any DSR computed today
   divides by zero or silently defaults `trials = 1`, which manufactures significance.
2. **`pick_id` is unconstrained.** The only FK on the table is `run_id -> source_run`. Nothing
   stops a `pick_id` that does not exist, so the linkage is nominal rather than enforced.
3. **`decision` has three states but nothing populates them**, so selection bias
   ("passed the rule, lost the ranking cutoff") remains indistinguishable from rule rejection.

So: structure is now adequate; data is absent. The denominator is a logging problem at scan time,
not a schema problem — the scanner must record every candidate decision as it happens, because it
cannot be reconstructed after the fact without exactly the fuzzy join that produced the
1-of-105 N-PORT miss.

## Still unfixed, needs a pipeline change not DDL

`picktrack_picks.status` remains `open` on 3,982 / 3,992 while the feed reports 3,618 EXPIRED +
30 terminal. Status was never synced; any active-picks count from this DB inherits the 7.5x
overstatement. Also: `asset_class` unnormalised (`EQUITY`/`STOCK`, `ETF`/`BASKET`,
`FOREX`/`FX_CARRY`); `instrument` and `price_bar` empty so `excess_bps` stays NULL and nothing is
re-derivable offline; `source_run` orphaned (3 rows, no consumers beyond the new
`screened_candidate.run_id`).
