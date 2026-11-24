# Migration status — what landed upstream, what remains

**Re-measured 2026-11-24 ~12:20Z**, after the objects changed underneath the R2 audit.
The schema is moving while this review is being written. Re-run the pre-flights before
applying anything here; two of my three original migrations are already superseded.

## Reconciliation

| my file | status | evidence |
|---|---|---|
| `001_horizon_eligibility.sql` | **SUPERSEDED — fully applied upstream** | `picktrack_picks.horizon_code`, `.pick_type`, `.profile_code`, `.stop_pct`, `.reward_risk` all exist; `v_pick_stats_by_source` now carries `horizon_code`, `marked_in_horizon`, and a `< 30 → NULL` gate |
| `002_pick_resolution_authority.sql` | **PARTIALLY applied** | `fk_res_pick` and `uq_res_pick_horizon` exist; `v_pick_level` still ignores `pick_resolution` and has no `outcome_source`; `v_resolution_mark_consistency` absent; **duplicate** unique index `uq_resolution` present |
| `003_screened_candidate_linkage.sql` | **PARTIALLY applied** | `pick_id`, `decision`, and `rule_hash char(64)` all exist — but **no foreign keys**, and `v_trial_denominator` absent |
| `004_remaining_gaps.sql` | **NEW — this is the residue** | the only things still missing |

## The publish blocker is closed, and the honest result is worse than the broken one

Horizon backfill landed: `1M` 3,843 · `1D` 117 · `3M` 32 (3,992 total). `pick_type`:
`SWING_TRADE` 3,812 · `DAY_TRADE` 117 · `POSITION` 32 · `UNCLASSIFIED` 31.
`profile_code`: `AGGRESSIVE` 3,555 · `MODERATE` 361 · `CONSERVATIVE` 76.
`risk_profile` now has 3 rows (was 0).

With eligibility live, `v_pick_level.in_horizon` splits:

- `in_horizon = 1` → **85 picks** (2.1% of 3,992)
- `in_horizon = 0` → **3,907 picks**

`v_pick_stats_by_source` as it stands right now — every row below is what the gate
actually returns:

| source | class | horizon | picks | marked_in_horizon | wins | WR |
|---|---|---|---|---|---|---|
| audit | CRYPTO | 1M | 3,424 | **37** | 11 | **29.73%** |
| audit | EQUITY | 1M | 98 | 28 | 14 | **NULL** |
| audit | BOND | 1M | 31 | 15 | 1 | NULL |
| audit | ETF | 1M | 35 | 3 | 2 | NULL |
| audit | CRYPTO | 1D | 69 | 2 | 0 | NULL |
| audit | FOREX | 1M | 177 | 0 | 0 | NULL |
| audit | COMMODITY | 1M | 35 | 0 | 0 | NULL |
| audit | EQUITY | 3M | 24 | 0 | 0 | NULL |
| harvest | STOCK | 1M | 5 | 0 | 0 | NULL |

**Exactly one cell in the entire estate clears `n >= 30`: CRYPTO/1M at 29.73% on n=37.**

Two things worth stating plainly:

1. **The gate earned its keep immediately.** `audit/EQUITY/1M` shows 14 wins of 28 — a
   50.0% win rate, the single most quotable number the old view would have produced. It is
   suppressed because 28 < 30. Under the previous horizon-blind definition EQUITY read
   `28.57%` on 70 marked picks; under the correct definition it is 50% on 28. Both readings
   are wrong to publish, but only the new one says so.
2. **97.9% of the ledger is not yet eligible.** 3,907 picks have no mark inside their own
   horizon window. This is not a gate fault — it is the ledger being 0–3 days old against a
   horizon of 7 days minimum for `1M`. The correct statement today is "one class has a
   borderline-defensible 30-day number, and nothing else is measurable yet."

## What 004 fixes

1. `v_pick_level` re-pointed to prefer `pick_resolution`, exposing `outcome_source`
   (`RESOLVED` / `MARK_FALLBACK` / `UNMARKED`). Without this, `pick_resolution` can start
   filling while the page keeps showing mark-derived outcomes — the divergence one layer up.
2. `v_resolution_mark_consistency` added, so any disagreement between a resolution and its
   terminal mark is *visible* rather than silent.
3. Duplicate unique index `uq_resolution` dropped — it is byte-identical in purpose to
   `uq_res_pick_horizon` (both `(pick_id, horizon)`, both non-unique=false). It doubles the
   write cost of every resolution insert and is the signature of a migration applied twice.
4. `screened_candidate` foreign keys restored — `pick_id` and `rule_hash` were widened and
   added **without** constraints, so the linkage is nominal: nothing stops a `pick_id` that
   does not exist, and nothing stops a `rule_hash` that is not a published rule version.
5. `v_trial_denominator` added, so `N_trials` becomes queryable once the scanner logs.

## Still not fixed by 004

- `picktrack_picks.status` remains `open` on 3,982 / 3,992 while the feed reports
  3,618 EXPIRED + 30 terminal. Status was never synced. This is the highest-severity
  remaining defect and it is a pipeline change, not DDL.
- `asset_class` still unnormalised (`EQUITY`/`STOCK`, `ETF`/`BASKET`, `FOREX`/`FX_CARRY`).
- `instrument` and `price_bar` empty — no price backbone, `excess_bps` stays NULL.
- `source_run` still orphaned (3 rows, no FK consumers).
- `screened_candidate` still 0 rows, so `N_trials` = 0 and no DSR is defensible.
