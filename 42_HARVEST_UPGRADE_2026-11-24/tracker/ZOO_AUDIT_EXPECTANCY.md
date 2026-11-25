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
