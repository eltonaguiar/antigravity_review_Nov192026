# Picktracking schema — round 2 review (pick-level fix + horizon)

**Audited:** 2026-11-24 · **DB:** `ejaguiar1_stocks` · **Method:** live `information_schema` +
`VIEW_DEFINITION`, not the description. Companion to `DB_SCHEMA_GAP_REVIEW.md` (round 1).

## Objects verified

12 views exist: `v_pick_last_mark_date`, `v_pick_latest_mark`, `v_pick_level`,
`v_pick_stats_by_source`, `v_mark_recomputed`, `v_picktrack_latest`,
`v_analyst_symbol_history`, `v_trader_symbol_history`, `v_trader_symbol_stats`,
`vw_all_enhancements`, `vw_all_incidents`, `vw_picks_now_dedup`.

New tables: `screened_candidate` (0 rows), `horizon_ref` (6 rows).
New columns: `picktrack_picks.horizon_min_days`, `.horizon_max_days` (**NULL on all 3,992**),
`.screened_by_run`; `screened_candidate.passed/.reject_reason`; `v_mark_recomputed.drift_bps`.

Row counts: `picktrack_picks` 3,992 · `picktrack_marks` 494 · `pick_resolution` **0** ·
`picktrack_scores` **0** · `screened_candidate` **0**.

## View dependency graph (measured, not read off a diagram)

| view | reads | references `pick_resolution`? |
|---|---|---|
| `v_pick_last_mark_date` | `picktrack_marks` | no |
| `v_pick_latest_mark` | `picktrack_marks` + `v_pick_last_mark_date` | no |
| `v_pick_level` | `picktrack_picks` LEFT JOIN `v_pick_latest_mark` | **no** |
| `v_pick_stats_by_source` | `v_pick_level` | no |
| `v_mark_recomputed` | `picktrack_marks` JOIN `picktrack_picks` | no |

---

## (A) Does `v_pick_latest_mark` + `v_pick_level` recreate the second-source-of-truth problem?

**No — the view chain avoids it.** Zero of the five views reference `pick_resolution`;
none writes anything. A view is recomputed on read and therefore cannot drift from its base
rows, so the original failure mode (three tables each *storing* "the outcome", whose labels
diverge) is structurally impossible here. The mark-row weighting is also genuinely fixed:
`v_pick_latest_mark` enforces one row per pick via a `MAX(mark_date)` self-join, and
`v_pick_stats_by_source` uses `SUM(is_win IS NOT NULL)` as the denominator — marked picks
only, with unmarked picks counted in `picks` but excluded from the rate. That is the correct
pick-level denominator, and `WR=NULL` when `marked=0` rather than `0`.

Three things make the word "avoids" narrower than it sounds:

1. **A third outcome vocabulary now exists, computed rather than stored.**
   `v_pick_level.outcome` = `UNMARKED`/`WIN`/`LOSS` from `sign(net_bps)`;
   `pick_resolution.outcome` = `varchar(16)` terminal; `picktrack_picks.status` =
   `open`/`unscored`. Only one is stored, so storage cannot diverge — but the *definitions*
   can and will, and the view is the one people will query.
2. **`v_pick_level` is horizon-blind.** It selects `horizon_min_days`/`horizon_max_days`
   but the outcome CASE never uses them, and both are NULL on all 3,992 picks. A mark at
   `days_held=3` contributes to the win rate identically to `days_held=300`.
3. **One-row-per-pick is true today but unenforced.** 494 marks across 494 distinct picks,
   and `v_pick_level` reports exactly 494 marked (3,498 UNMARKED + 383 LOSS + 111 WIN =
   3,992). Nothing prevents a second mark on the same `(pick_id, mark_date)`, which the
   `MAX()`-join would silently return twice — re-introducing the exact weighting just fixed.

## (B) `pick_resolution` vs `picktrack_marks`: which is authoritative?

**`pick_resolution` is authoritative for the outcome; `picktrack_marks` is authoritative for
the observation series.** They answer different questions and neither can be deleted.

- `pick_resolution` = the verdict: one row per (pick, horizon), carrying `outcome`,
  `exit_reason`, `exit_price`, `pnl_bps`, `bench_pnl_bps`. It is the only object that can
  express *when* a pick ended and *why*.
- `picktrack_marks` = the evidence: immutable price observations at time *t*. It must be
  retained; `v_mark_recomputed` — the drift guard — depends on it, and recomputation is
  impossible without it.

**What to do to the other one:** keep `picktrack_marks` exactly as-is and **re-point
`v_pick_level`** so it LEFT JOINs `pick_resolution` first and falls back to the latest mark
only when no resolution exists, exposing `outcome_source` (`'RESOLVED'` | `'MARK_FALLBACK'`).
Add `UNIQUE (pick_id, horizon)` and an FK to `picktrack_picks.id` on `pick_resolution`
(both absent — it has no foreign key at all).

The reason this is urgent rather than tidy: today `v_pick_level` is the *only* readable
outcome, so it is the de facto authority by default. When `pick_resolution` starts writing,
nothing forces the view to consult it — so the page would keep showing mark-fallback rates
while a second, better-defined rate exists in a table nobody queries. That is the divergence,
arriving quietly, exactly one layer above where it was fixed.

## (C) Can `screened_candidate` reconstruct a multiple-testing denominator?

**No.** Its columns are `id, source, screened_at, symbol, asset_class, strategy, passed,
reject_reason, rule_hash, source_run_id, notes`. It has **0 rows**, **no `pick_id`**, and
**no foreign key in either direction** — nothing references it, it references nothing.

Five concrete reasons it cannot serve as a denominator:

1. **No link to the surviving pick.** The only join candidate is `(source, symbol)` with
   proximity between `screened_at` and `published_at` — a fuzzy join, the same inference
   class that gave 1-of-105 on the N-PORT ticker join and the 4 false layer-A matches from
   the ticker `DE` inside Spanish prepositions.
2. **`rule_hash` widths do not match.** `screened_candidate.rule_hash` is `varchar(32)`;
   `rule_version.rule_hash` is `char(64)`. A DSR/BH denominator has to be scoped to the rule
   version whose label was published, and that join is impossible. Decisive on its own.
3. **N_trials is bounded but not identified.** The same `(source, symbol, screened_at)` can
   be screened by several `strategy`/`rule_hash` values, and one pick may correspond to 0, 1
   or N candidates. `COUNT(*)` gives an upper bound, not the trial count.
4. **Zero rows today**, so any DSR computes against 0 — dividing by zero or silently
   defaulting `trials=1`, which manufactures significance.
5. **`passed` is two-valued but the denominator needs three states:** rejected by rule,
   passed but not selected, selected. Without the middle state you cannot separate
   selection bias from rule rejection — different statistical meaning, same `passed=0`.

Sufficient design: nullable `pick_id` FK set on promotion; `rule_hash` widened to `char(64)`
matching `rule_version`; a `decision` enum `REJECTED`/`NOT_SELECTED`/`PROMOTED`; population;
and an index on `(source, screened_at)`.

## (D) The one fix before any number is published

**Give every pick an explicit horizon and make the published stats fail closed on it:**
add `picktrack_picks.horizon_code varchar(32)` FK → `horizon_ref.horizon_code`, backfill it,
and change `v_pick_stats_by_source` to count only picks whose latest mark's `days_held` falls
inside that horizon's `[min_days, max_days]`, reporting the remainder as
`immature_or_unclassified` and returning NULL rather than a rate when eligible n is below the
applicable `pick_type_ref.min_n`.

Why this and not the others: both external-review findings reduce to one defect — an
ineligible row counted as a result. Mark-row weighting was that error at the row level;
horizon-blindness is the same error one level up, counting a 3-day mark as a 3-month outcome.
The table as it stands would publish:

| source | class | marked | WR |
|---|---|---|---|
| audit | COMMODITY | **8** | **75.00%** |
| audit | CRYPTO | 331 | 22.36% |
| audit | EQUITY | 70 | 28.57% |
| audit | ETF | 33 | 15.15% |
| audit | BOND | 24 | 12.50% |
| audit | FOREX | 23 | 8.70% |

`75.00%` on 8 marks is precisely the `n<30 is not a verdict` rule being violated in a view
that reads as authoritative. And the fix is the prerequisite for everything else: `horizon_ref`
is referenced by **NOTHING**, `pick_type_ref` is referenced only by the empty `trader_rating`,
and `picktrack_picks` has neither `pick_type` nor `horizon_code` — so today a pick physically
cannot express which horizon it belongs to, and every eligibility filter would be undefined.

Minimal stopgap if only one statement is allowed: gate `win_rate_pct` on
`marked_picks >= min_n` and return NULL below it. That alone stops 75%/n=8 escaping, but it
still lets a 3-day mark be published as a 3-month outcome.
