# Migrations — picktracking schema

> ## ⚠️ READ `000_STATUS.md` FIRST.
> The schema moved while this review was being written. **001 is fully applied upstream;
> 002 and 003 are partially applied. Do not apply 001–003 as written — they will fail on
> already-existing columns and constraints.** `004_remaining_gaps.sql` is the only
> unapplied change and the only one to review.
>
> Verified 2026-11-24 ~12:20Z: `horizon_code` backfilled (1M 3,843 / 1D 117 / 3M 32),
> `pick_type` and `profile_code` populated, `risk_profile` now 3 rows,
> `v_pick_stats_by_source` carries the horizon gate and the `n >= 30` rule,
> `pick_resolution` has `fk_res_pick` + `uq_res_pick_horizon`.

These files close the gaps measured in `../DB_SCHEMA_GAP_REVIEW.md` (round 1) and
`../DB_SCHEMA_GAP_REVIEW_R2.md` (round 2).

**None of these have been executed by me.** They are reviewable proposals. The database is
shared and production; DDL is the owner's decision, not the reviewer's.

## Status

| # | file | status |
|---|---|---|
| 000 | `000_STATUS.md` | **reconciliation — read first** |
| 001 | `001_horizon_eligibility.sql` | **SUPERSEDED** — applied upstream in a different form |
| 002 | `002_pick_resolution_authority.sql` | **PARTIAL** — FK/UNIQUE landed; view re-point did not |
| 003 | `003_screened_candidate_linkage.sql` | **PARTIAL** — columns landed; FKs and denominator view did not |
| 004 | `004_remaining_gaps.sql` | **OUTSTANDING** — the residue, review this one |

## What is still the actual publish state

With the gate live, `v_pick_level.in_horizon` = 1 for only **85 of 3,992 picks**.
Exactly one cell clears `n >= 30`: **audit/CRYPTO/1M at 29.73% WR on n=37.** Every other
source x class x horizon cell returns NULL. That is the honest headline, and it is the
correct output — not a defect.

## What each one changes in behaviour

**001 — applies fail-closed.** It adds `picktrack_picks.horizon_code` (nullable, FK →
`horizon_ref`) and rebuilds `v_pick_stats_by_source` so the win rate counts only picks whose
latest mark's `days_held` falls inside that pick's own horizon window, and returns `NULL`
rather than a number when eligible `n < 30`.

Consequence on a fresh apply: **every `win_rate_pct` becomes NULL**, because
`horizon_code` is NULL on all 3,992 picks. That is intended. The current view would publish
`COMMODITY 75.00%` on 8 marked picks; after 001 it publishes nothing until horizons are
assigned. A suppressed rate is shown as suppressed, via the `immature_or_unclassified`
column, so it cannot be mistaken for a missing row.

The backfill is deliberately manual. There is no per-pick horizon source upstream — no
`pick_type` column, no `horizon_code` — so any automatic assignment would be fabricated, in
a migration whose entire purpose is to stop a fabricated number. Section 3 gives the
assignment pattern and a coverage report to track classification progress.

**002 — makes the resolver authoritative, and admits a correction.** It adds the FK and
`UNIQUE (pick_id, horizon)` that `pick_resolution` lacks, adds a
`v_resolution_mark_consistency` view that makes any disagreement between a resolution and
the terminal mark *visible* rather than silent, and re-points `v_pick_level` to prefer the
resolution and fall back to the latest mark, exposing `outcome_source`
(`RESOLVED` / `MARK_FALLBACK` / `UNMARKED`).

It does **not** populate `pick_resolution`. Round 1 recommended deriving resolutions from
the 494 existing marks; round 2 measured that `excess_bps` is NULL on 494/494 marks and
horizon was NULL on 3,992/3,992 picks, which is why that shortcut looked cheaper than it is.
Copying marks into `pick_resolution` would make it a pure function of `picktrack_marks` — a
derived duplicate, exactly the duplicate outcome source this work exists to prevent. The
resolver must apply explicit exit rules (tp / sl / time exit at the pick's horizon).

**003 — makes the denominator exist.** It adds `pick_id` (FK), a three-state `decision`
enum (`REJECTED` / `NOT_SELECTED` / `PROMOTED`), widens `rule_hash` from `varchar(32)` to
`char(64)` to match `rule_version`'s primary key, and adds `v_trial_denominator`. The
`varchar(32)` vs `char(64)` mismatch is the decisive defect: without it a trial count cannot
be scoped to the rule version whose label was published.

`decision` defaults to `REJECTED` on purpose. An unclassified row then counts toward the
denominator, which makes any significance claim harder, never easier.

## Rules for whoever applies these

1. **Run section 1 of each file first.** Every file opens with read-only pre-flight queries
   that confirm the defect still exists. If a pre-flight no longer matches the stated
   finding, stop — the schema moved and the migration was written against stale facts.
2. **Never create a parallel view to avoid a rebuild.** Do not add `v_pick_stats_by_source_v2`
   or `v_pick_level_eligible` beside the originals. Two views carrying win rates is precisely
   how the original divergence started. Use `CREATE OR REPLACE VIEW` on the existing name.
3. **Run the post-checks.** Each file ends with acceptance queries whose expected output is
   stated. 001's reconciliation check (`eligible + immature - marked = 0`) catches bugs in
   the gate itself.
4. **Publish nothing between 001 and the horizon backfill.** That interval is the honest
   state: zero eligible picks, zero publishable rates.

## What these do not fix

- `picktrack_picks.status` is `open` on 3,982 of 3,992 rows while the upstream feed reports
  562 OPEN + 3,618 EXPIRED + 30 terminal. The database never maintained status. No view can
  repair this; it needs a status sync from the feed, which is a data-pipeline change, not DDL.
- `asset_class` is unnormalised (`EQUITY` 160 vs `STOCK` 11, `ETF` 41 vs `BASKET` 1,
  `FOREX` 184 vs `FX_CARRY` 1). Per-class verdicts still inherit a fractured denominator.
- `instrument` and `price_bar` are empty, so there is no price backbone and no offline
  re-derivation. `excess_bps` stays NULL until one exists.
- `source_run` remains orphaned: 3 rows, nothing references it by FK.
