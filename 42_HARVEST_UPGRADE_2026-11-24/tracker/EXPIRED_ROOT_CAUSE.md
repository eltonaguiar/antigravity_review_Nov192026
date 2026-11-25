# EXPIRED root cause — CORRECTED: it is a backfill bug with recoverable data, not a lost schema

**Hermes · 2026-11-25 00:20 EST** · scripts `expired_diag.py`, `pickid_structure.py`, `zero_mass_probe.py`
Cross-checked by an independent model (`local router, free-mode-large`) which challenged the first diagnosis and
was right to.

---

## Three things I got wrong, stated first

| my earlier claim | what is actually true |
|---|---|
| "the table has no date column, so the dates are gone" | **Wrong.** `resolved_at` is populated on **28,395** of the 33,092 resolved rows (WON 11,570 + LOST 16,825), ranging 2026-02-22 to 2026-11-25. And `pick_id` **embeds the date** on 43.2% of rows as `::SYMBOL::YYYY-MM-DD`. |
| "the expired rows are unrecoverable as stored" | **Wrong.** The prices to resolve them exist: `crypto_ohlcv` **1,721,830** rows, `stock_ohlcv` **471,495**, `equity_daily_ohlcv` **315,802**. The top expired symbol BTCUSDT has 1,954 expired picks; USDCAD=X 1,120 with **4,321 price bars** in `stock_ohlcv`. |
| "compromised at the schema level — recomputing cannot fix it" | **Too strong.** It is a **write-path defect with recoverable inputs**, not lost information. Recomputation is exactly what fixes it. |

I published those claims to the user and to COMS before checking. The independent model's specific objection —
*"you asserted unrecoverability without running the join"* — was correct, and running it reversed the conclusion.

## The actual mechanism: two backfill scripts wrote the zeros

Zeros are **not** spread across the resolver. They concentrate in the backfills:

| `resolver_version` | n | zeros | % zero |
|---|---:|---:|---:|
| **backfill_widened_202…** | 25,529 | 20,835 | **81.6%** |
| **backfill_updated_202…** | 7,891 | 7,621 | **96.6%** |
| universal_v2 | 22,280 | 408 | **1.8%** |
| v2.1 | 3,607 | 16 | **0.4%** |
| backfill_2026-06-01 | 3,695 | 600 | 16.2% |
| v2.2_sync_2026-06-05 | 421 | 97 | 23.0% |
| signflip_purge_2026… | 369 | 0 | 0.0% |

The two `backfill_*_202*` scripts account for **28,456 of the 29,577 zeros**. The genuine resolver versions
(`universal_v2` 1.8%, `v2.1` 0.4%) are nearly clean. So this is a **backfill that marked unresolved picks
EXPIRED and wrote 0 instead of resolving them** — one specific bad write path, not a systemic design failure.

And the branch is isolated:

| `resolution_method` | n | zeros | % zero |
|---|---:|---:|---:|
| **TIME_EXPIRED** | 29,505 | **28,430** | **96.4%** |
| SL_HIT | 18,534 | **0** | 0.0% |
| TP_HIT | 12,448 | 2 | 0.02% |
| MANUAL | 2,882 | 1,048 | 36.4% |

`SL_HIT` and `TP_HIT` are **clean**. The defect lives entirely in the expiry branch.

## Root cause of the non-resolution: prices never arrived

`trading_picks`, `TIME_EXIT_MAX_HOLD`: **31,421** picks, of which

- **31,378 have a take-profit set**
- **31,387 have a stop-loss set**

So the exits were **configured correctly on 99.9% of them and the picks expired anyway**. That is not an
exit-logic defect — the logic never ran because no price arrived to test against it. Corroborated by
**1,664** picks in `RESOLVE_FAILED_MAX_RETRIES`.

**Root cause: a price-resolution failure, not a strategy or logic failure.** The picks were never evaluated.

## What this means for every number in the programme

The 46% is **recoverable**, which changes the picture materially:

- `pick_id` gives symbol + date for 27,572 rows directly.
- `resolved_at` gives an exit timestamp for 28,395 resolved rows.
- Price coverage is deep: 1.72M crypto bars, 471K stock bars, 316K equity bars, plus dedicated
  `fx_prices`, `futures_daily_ohlcv`, `etf_daily_ohlcv`.
- The expired pile is dominated by instruments with **years** of bars (USDCAD=X 4,321, AUDUSD=X 4,320,
  EURJPY=X 4,317, GBPJPY=X 4,317, GC=F 3,879).

So the honest statement is not "the measurement apparatus is broken beyond repair". It is:

> **A backfill wrote 0 into 28,431 rows that had resolvable prices, and nothing since has re-resolved them.
> The 33,092 resolved rows give +6.34 bp mean / −38.98 bp median, which is the only number that currently
> means anything, and the remaining 46% can be recovered by re-resolving from the price tables.**

## Repair, in order

1. **Re-resolve the EXPIRED pile from prices.** For each expired pick, parse `pick_id` for symbol + date,
   pull the bar at the intended expiry, and write the actual return. Report the parse rate — it will be
   ~43% from `pick_id` alone, and the remaining 56% (opaque hashes) need a symbol/date source before they
   can be touched. **Do not fabricate a window for the unparseable ones.**
2. **Fix the write path** so `TIME_EXPIRED` never stores `pnl_pct = 0`. Zero must mean "flat outcome",
   which should be rare and *measured*, not a default. Add a check constraint or an assertion in the
   resolver: writing 0 for a status of EXPIRED should raise.
3. **Add a row-count assertion** at the expiry step, per the discipline of the last eight defects.
4. **Re-run the cost gate after re-resolution** — the per-class verdicts may move materially once 46% of
   the book is priced instead of zeroed. FOREX in particular: it is dominated by the FX pairs that make up
   most of the expired pile.

## The lesson, recorded plainly

Eight verdicts today printed a right number over a wrong denominator, and this one was the ninth — except
this time I got the *diagnosis* wrong in the opposite direction: I declared the data unrecoverable without
running a single join. An independent model asked the one question I had not asked ("is `resolved_at` NULL on
WON/LOST?") and it came back 28,395 rows populated.

**Under-claiming damage is also an error.** It produces a false terminal state — "unfixable" — which is worse
than a wrong number, because a wrong number invites a recheck and "unfixable" invites nothing.
