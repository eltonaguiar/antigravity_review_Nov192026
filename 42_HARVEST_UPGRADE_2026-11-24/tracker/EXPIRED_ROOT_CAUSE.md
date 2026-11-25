# EXPIRED root cause — diagnosis, not another table

**Read-only** query of `ejaguiar1_stocks`, 2026-11-25. Credentials read at runtime; never printed or committed.
No writes, no schema changes.

## Filter counts (n at every step)

| step | n |
|---|---:|
| at_pick_outcomes raw | 63,792 |
| status EXPIRED | 29,654 |
| EXPIRED with pnl_pct = 0 | 28,531 |
| EXPIRED with pnl_pct != 0 | 1,123 |
| EXPIRED with resolved_at NULL | **28,198** |
| EXPIRED join to trading_picks | 26,748 |
| join with exit_price/pnl/status WON-LOST | **26,608** |
| EXPIRED with no trading_picks join | 2,906 |
| no-join with a price bar at/after resolved_at | 283 |
| no-join without price/date (price gap or undated) | 2,623 |
| RESOLVE_FAILED_MAX_RETRIES | 1,664 |
| expired joins closed <=24h | 369 (<=72h: 466; <=7d: 579) |

## The four modes — counts (overlapping, not additive)

1. **STATUS MISLABEL — 26,608 rows (89.7% of EXPIRED).** `at_pick_outcomes` says EXPIRED/pnl=0, but
   the joined `trading_picks` row has `exit_price`, non-zero `pnl_pct`, or status WON/LOST/TP/SL.
   Example: SOLUSDT `004093a29134452d` — at_pick EXPIRED/0, trading TIME_EXIT +0.2132, exit 88.93.
   This is the dominant cause: the outcome table is stale or the status sync is wrong.
2. **RESOLVER BUG — 1,664 rows.** All `RESOLVE_FAILED_MAX_RETRIES`, all EXPIRED, all have an
   `exit_price` but pnl=0. The resolver gave up after retries instead of writing the P&L.
3. **PRICE GAP — 2,623 rows.** No trading_picks join and no price bar at/after the expiry date;
   many are FX/crypto symbols absent from `stock_ohlcv`/`daily_prices`/`equity_daily_ohlcv`.
4. **LOGIC DEFECT — 369 rows (strict 24h window; 466 at 72h).** Joined trades closed within 24h
   with status EXPIRED, often `GRADE_GATE`/time exits, so TP/SL could not be reached by construction.

These overlap: the 1,664 resolver failures and 369 short-window rows are inside the 26,608 mislabel
set; the counts are evidence per mode, not a partition.

## Recoverable set

**26,891 of 29,654 (90.7%)** can be resolved retroactively: **26,608** already have an exit/PnL in
`trading_picks`, plus **283** no-join rows with a price bar at/after `resolved_at`. Only **2,763**
remain unpriceable/undated (2,623 no-join gap + 140 residual), so the problem is mostly wiring and
status sync, not missing market data.

## Five sample pick IDs per mode

**Status mislabel**
- `004093a29134452d` SOLUSDT — TIME_EXIT +0.2132%
- `0071cccca711574f` PEPEUSDT — TIME_EXIT −0.2519%
- `0085206374e6399b` TAOUSDT — TIME_EXIT −0.5274%
- `0087a96e877ab19f` ZECUSDT — TIME_EXIT +0.0354%
- `009de30df574e803` SUIUSDT — TIME_EXIT −0.0211%

**Resolver bug (RESOLVE_FAILED_MAX_RETRIES)**
- `bond-a0cc0dd1597a` USDJPY=X — exit 159.882, pnl 0
- `cnn_lite_pattern_signal::MTUM::2026-06-01` MTUM — exit 316.93, pnl 0
- `iso_battleground_luxalgo_ADAUSDT_7522283794` EURGBP=X — exit 0.85643, pnl 0
- `iso_regime_terminal_LCID_2908857906` LCID — exit 6.65, pnl 0
- `iso_regime_terminal_QUBT_4467106109` QUBT — exit 11.96, pnl 0

**Price gap / undated**
- `0d30efbc60f0fcd74735e04e041178e6` OPUSDT
- `0dc0de4572d5ae02cc373cd93ce759dc` LINKUSDT
- `1076283131efe512b67f661f6852cce0` LINKUSDT
- `130be76f708dac8c209054bb1d438308` MATICUSDT
- `15f3994ce24d4b86c6c802a6edaca37a` ETHUSDT

**Logic defect (closed <=24h)**
- `ai_ema_pullback::BNB-USD::2026-03-16` BNB-USD — GRADE_GATE
- `ai_ema_pullback::LTC-USD::2026-03-16` LTC-USD — GRADE_GATE
- `autocorrelation_exploiter::AMC::2026-03-16` AMC — GRADE_GATE
- `autocorrelation_exploiter::GBPJPY=X::2026-03-16` GBPJPY=X — GRADE_GATE
- `autocorrelation_exploiter::NVDA::2026-03-16` NVDA — GRADE_GATE

## Recommendation

1. **Reconcile `at_pick_outcomes` from `trading_picks` by pick_id** where trading has an exit_price,
   PnL, or resolved status; this alone recovers 26,608 rows. Do it as a read-only report first, then a
   backfill after owner approval.
2. **Never write EXPIRED with pnl=0 when `trading_picks.exit_price` exists.** Add a status/PnL
   consistency check to the resolver; fail loudly if they disagree.
3. **Fix the resolver's retry terminal state:** `RESOLVE_FAILED_MAX_RETRIES` must carry the computed
   P&L from the exit price, not zero.
4. **Populate `resolved_at`** (28,198 nulls). Without an expiry timestamp, no score can be audited.
5. **Resolve no-join rows from price at expiry**; for FX/crypto add the missing price source rather
   than treating zero as flat.
6. **Do not change exit windows to hide GRADE_GATE expiry**; if a trade cannot reach TP/SL in the
   window, record that as a logic failure, not a flat outcome.

**Bottom line:** roughly **90.7% of EXPIRED rows are recoverable**, mostly from `trading_picks` — this
is a resolver/status-sync defect, not primarily a price-data problem. Every statistic computed on
EXPIRED=0 is contaminated and must be recomputed after reconciliation; the denominators are the first
thing to fix.

next_probe: produce the pick_id-level reconciliation report (trading exit vs at_pick EXPIRED) and
verify the 26,608 recovered rows before any backfill.
