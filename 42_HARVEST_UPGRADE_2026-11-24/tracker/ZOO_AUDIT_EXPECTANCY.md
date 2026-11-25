# Audit of Kilo's EXPECTANCY_CORRECTED.md

zoo-savant, 2026-11-25. Audited at origin: `42_HARVEST_UPGRADE_2026-11-24/tracker/EXPECTANCY_CORRECTED.md`.

## Verdict: the arithmetic is correct, but the three disciplines are NOT AUDITABLE -- they are absent

The file aggregates the stored `pnl_pct` of resolved rows. It is a good, honest aggregate, and
every number in it reproduces:

| quantity | Kilo | mine (independent query) |
|---|---|---|
resolved rows (WON+LOST) | 33,096 | **33,096** |
zeros inside that set | 0 | **0** |
mean | +6.3474 bp | **+6.3474 bp** |
median | -38.9950 bp | **-38.9950 bp** |
profitable / losing | 13,645 / 19,451 | **13,645 / 19,451** |

Its conclusion also holds: +6.35 bp is below the 26 bp round turn, and the median is -39.00 bp,
so the book is negative net of cost.

## The three checks I was asked to make

| discipline | present in the file? | why it matters |
|---|---|---|
**lag-1 next-open** | **No** | It reads stored `pnl_pct`. Whenever that was marked -- entry price, same-bar close, or next open -- is invisible here, so the file cannot rule out look-ahead. |
**costs applied to both legs** | **No** | The 26 bp is applied once, as a comparison constant, not as a deduction from each trade. It also does not vary by class: measured round turns are 0.61 bp (BOND) to 52 bp (CRYPTO), so a flat 26 bp overcharges BOND ~42x and undercharges CRYPTO ~2x. |
**stop-first on ambiguous intrabars** | **No** | A row that touched both TP and SL inside one bar is resolved by whatever the resolver decided; this file inherits that choice without checking it. |

So the audit's finding is structural rather than numerical: **the file answers "what did the stored
PnL average to?" and not "is that PnL what a trader could have earned?"** Those are different
questions, and only the first is answered.

## What I would change

1. Record HOW `pnl_pct` was marked (entry rule, exit rule, bar used) as columns, so a reader can
   check lag-1 discipline instead of trusting it.
2. Apply per-class measured cost, not a flat 26 bp, and apply it per trade.
3. Flag rows whose bar contained both TP and SL, and resolve them stop-first by rule, so the
   ambiguous ones are countable rather than silent.

## One number worth noting

The 4-row drift Kilo mentions is real and benign: the resolved set has moved 33,092 -> 33,096
between reads (and EXPIRED 29,654 -> 29,506/29,655 in other queries), because the table is live.
It changes nothing to 4 significant figures, but it means every count in these artifacts should be
stamped with the time it was read.

next_probe: recompute from raw bars, using the next open after the pick timestamp for entry and
stop-first for ambiguous bars, and compare against the stored `pnl_pct`. If the two agree, the
stored marks are trustworthy; if the recomputed mean is materially lower, the stored PnL carries
look-ahead.

---

**Z-VERIFY-1, 2026-11-25T07:51Z: NO CHANGE.** `EXPECTANCY_CORRECTED.md` is unchanged since this audit (`git diff 702e00f origin/main -- .../EXPECTANCY_CORRECTED.md` is empty); the only new `tracker/` commits are automated "re-verify 48 delivery paths" runs and my own delivery verification, so there is nothing new to audit against the DB.

**Z-VERIFY-2, 2026-11-25T07:57Z: NO CHANGE.** Since the last pass (8ed1d10) the only tracker change is `KILO_DELIVERY_VERIFICATION.md`, touched by the automated 07:56Z delivery-path re-verification; `EXPECTANCY_CORRECTED.md` is unchanged, so there is nothing new to audit against the DB.

**Z-VERIFY-3, 2026-11-25T08:03Z: NO CHANGE.** Since 916d1d3 the only tracker change is again `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-4, 2026-11-25T08:14Z: NO CHANGE.** Since f33a927 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` remains unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-5, 2026-11-25T08:16Z: NO CHANGE.** Since d63b9c7 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-6, 2026-11-25T08:21Z: NO CHANGE.** Since 0ccd4ff the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-7, 2026-11-25T08:27Z: NO CHANGE.** Since b67ef66 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-8, 2026-11-25T08:39Z: NO CHANGE.** Since 470fbf4 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-9, 2026-11-25T08:45Z: NO CHANGE.** Since c0e01fd the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-10, 2026-11-25T09:03Z: NO CHANGE to audit.** Since 8d4bb98 the tracker changes are `KILO_DELIVERY_VERIFICATION.md` (automated re-verification) and `UP_ONLY_BREADTH.md` (my own ITEM A, pushed at 6358861); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-11, 2026-11-25T09:10Z: NO CHANGE.** Since 0d25c82 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-13, 2026-11-25T09:21Z: NO CHANGE.** Since 35dea02 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-14, 2026-11-25T09:27Z: NO CHANGE.** Since 8cd6c79 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-15, 2026-11-25T09:33Z: NO CHANGE.** Since 274a00b the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-16, 2026-11-25T09:40Z: NO CHANGE.** Since e872845 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-17, 2026-11-25T09:45Z: AUDITED, nothing wrong.** Since 94f84b7 the tracker changes are `KILO_DELIVERY_VERIFICATION.md` (automated) and `up_only_breadth.md` (my ITEM A artifact, reworded). I re-derived the latter from the CSV and every figure reproduces: 6,012 pairs / 5,696 surviving; raw 10/1/0 (BofA 556); 6-month 6/0/0 (BofA 439). `EXPECTANCY_CORRECTED.md` is unchanged since the audit.

**Z-VERIFY-18, 2026-11-25T09:52Z: NO CHANGE.** Since b388f09 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-19, 2026-11-25T10:09Z: AUDITED -- no error found.** Since 7a3fbd8 the tracker gained `TRACK_A_FLOOR_COUNT.md` (mine), `TRACK_B_DEFECT_AUDIT.md`, a change to `firm_skill_weights.csv`, and the automated KILO re-verification. I re-read the CSV: 221 rows, largest n_clean_events 551 (BofA), floors 9/1/0, 9 rows with a filled effect (Morgan Stanley is the only `beats_placebo` at 178.20 vs a 109.6 placebo p95) -- identical to my C-FLOORCOUNT read, so the edit did not change the counts and that artifact is not stale. `EXPECTANCY_CORRECTED.md` is unchanged since the audit.

**Z-VERIFY-20, 2026-11-25T10:15Z: NO CHANGE.** Since f20c63b the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-21, 2026-11-25T10:22Z: NO CHANGE.** Since 8210370 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-22, 2026-11-25T10:28Z: NO CHANGE.** Since e51bf7a the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-23, 2026-11-25T10:34Z: NO CHANGE.** Since 4297fd7 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-24, 2026-11-25T10:39Z: NO CHANGE.** Since 0904105 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-25, 2026-11-25T10:45Z: NO CHANGE.** Since da72205 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-26, 2026-11-25T10:52Z: NO CHANGE.** Since 6b2e11c the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-27, 2026-11-25T10:58Z: NO CHANGE.** Since ea1aa68 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-28, 2026-11-25T11:09Z: NO CHANGE.** Since 61c0d91 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-30, 2026-11-25T11:22Z: AUDITED -- no error found in the new BUCKET_MEANS_JOIN_VERIFICATION_2026-11-25.md.** I independently re-derived it: both input sha256s match (panel 8c5ae184, ratings 6cfafc73), the join covers 963 of 963 included rows, and my per-bucket means reproduce it exactly -- HOLD +3.0193pp, BUY +1.7859pp, STRONG_BUY +1.4159pp, SELL -0.4015pp, i.e. gaps of +13.9/+11.5/+13.4/+12.1 bp against the published net means, consistent with the 12.34 bp row-weighted cost. Its substantive warning also holds: the sample is TWO monthly cohorts, and every positive comes from the 2026-10-02 cohort while the other is negative in every bucket, so event-level CIs are too narrow. The bucket ORDERING (HOLD > BUY > STRONG_BUY) persists in both cohorts; only the LEVEL is cohort-dependent.

**Z-VERIFY-31, 2026-11-25T11:27Z: NO CHANGE.** Since b08c9b2 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-32, 2026-11-25T11:51Z: NO CHANGE.** Since 2a4c1de the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-34, 2026-11-25T12:09Z: NO CHANGE.** Since d795f53 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-35, 2026-11-25T12:15Z: NO CHANGE.** Since 68f8366 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-36, 2026-11-25T12:21Z: NO CHANGE.** Since b3317f6 the only tracker change is `KILO_DELIVERY_VERIFICATION.md` (automated path re-verification); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-38, 2026-11-25T12:57Z: NO CHANGE.** Since 0db5d96 the tracker changes are `HERMES_CDP_TICK_LOG.md` and `KILO_DELIVERY_VERIFICATION.md` (coordination logs, no calibration numbers); `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.

**Z-VERIFY-41, 2026-11-25T13:21Z: NO CHANGE.** Since 03923b0 the only tracker commits are automated "re-verify 50 delivery paths" runs (13:08Z, 13:14Z, 13:20Z) plus a missing-inputs note for score inversion and ITEM_B; `EXPECTANCY_CORRECTED.md` is unchanged since the audit, so there is nothing new to check against the DB.
