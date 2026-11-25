# Placebo audit — the Track A null was partly an artifact

**Date:** 2026-11-25 · **Scope:** `firm_skill_weights.csv`, 9 firms at n>=300
**Status:** corrected effects and verdicts; one firm clears. This supersedes the old p95 column.

## 1. What the placebo code actually computed

Two independent defects, both in the ad-hoc `firm_effects.py` path used to fill the file:

1. **Date-unit mismatch.** Price dates were stored as nanoseconds (`DatetimeIndex.view('int64')`
   ≈ 1.7e18), but the event date was converted to **days** (`datetime64[D]` ≈ 20,000).
   `searchsorted` therefore returned index 0 for every event and every placebo, so both the
   "real" and "placebo" returns were measured from the **first price bar**, not the event date.
   This is why the old means (34.17, 222.59, 149.15, …) are not event-date returns.
2. **Wrong statistic for p95.** `placebo_p95_bps` was the 95th percentile of **per-event**
   placebo draws, then compared with a **mean** of 551/473 events. The mean-null threshold is
   `1.645 * sd / sqrt(n)`, not a per-event percentile. `placebo_dateswap.py` has the same
   per-event-p95 issue; its `real_exceeds_p95` comparison is therefore not a mean test.

The old p95 range (2,579–3,117 bp) implies per-event sd = `p95*sqrt(n)/1.645` ≈ **390–412%**,
which is physically impossible. The programme's realistic per-event sd is **13.29%**.

## 2. Corrected results

Entry next session after the event, 63 calendar days, adjusted close, SPY benchmark, 26 bp;
mean-null p95 = `1.645 * 13.29% / sqrt(n_priced)`.

| firm | n clean/priced | old mean (bug) | old p95 (bug) | **corrected mean** | **corrected p95** | old verdict | **new verdict** |
|---|---:|---:|---:|---:|---:|---|---|
| BofA Securities | 551/482 | 34.17 | 2733.86 | **−40.61** | **99.6** | underpowered | **indistinguishable** |
| Morgan Stanley | 473/398 | 222.59 | 3117.20 | **+178.20** | **109.6** | underpowered | **beats_placebo** (weight 1.0) |
| J.P. Morgan | 454/374 | 149.15 | 2972.78 | **+70.45** | **113.0** | underpowered | **indistinguishable** |
| Goldman Sachs | 448/400 | 13.77 | 2896.85 | **−2.06** | **109.3** | underpowered | **indistinguishable** |
| UBS | 359/323 | 114.92 | 2972.78 | **+97.15** | **121.6** | underpowered | **indistinguishable** |
| Citi | 350/309 | −42.81 | 2733.86 | **−71.76** | **124.4** | underpowered | **indistinguishable** |
| Deutsche Bank | 331/295 | 4.53 | 2983.33 | **+2.58** | **127.3** | underpowered | **indistinguishable** |
| Jefferies | 313/278 | 33.02 | 2733.86 | **−125.55** | **131.1** | underpowered | **indistinguishable** |
| Wells Fargo | 313/288 | −72.36 | 2579.26 | **−87.23** | **128.8** | underpowered | **indistinguishable** |

**Which firms clear:** **Morgan Stanley only** (+178.20 > 109.6). At the brief's n=clean
thresholds (BofA 93.1, MS 100.5), MS still clears; no other firm does.

## 3. Discrepancy the brief expected

The brief said **JPMorgan at 149.15 clears**. That 149.15 came from the same date-unit bug;
the corrected event-date mean is **70.45**, below its **113.0** mean-null threshold. JPMorgan
does **not** clear. The brief's 222.59 Morgan Stanley also changes (to 178.20), but MS still clears.

## 4. Guard added

`input_assertions.require_placebo_p95(metric, p95_bps, n, expected_sd=0.1329)` computes the
expected mean-null p95 and calls `require_unit_scale`. The old BofA value is **27.45×** the
expected and raises **DATA_INVALID**; the corrected 99.6 bp passes. Self-test now includes both.

## 5. File state

`firm_skill_weights.csv` remains **222 lines** = header + 219 data + 2 comments.
9 measured rows now carry corrected means/p95; 210 below-floor rows stay blank + underpowered.
Only Morgan Stanley has a nonzero weight (1.0, eligibility placeholder; sizing policy is separate).

next_probe: rerun the corrected event-date placebo for all 9 with the actual per-event sd, and
independently replicate Morgan Stanley before any capital or promotion decision.
