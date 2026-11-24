# Pick-surface audit + SQL data-quality checks (2026-11-24)

Sources checked live (all HTTP 200):
- `https://findtorontoevents.ca/audit/` and `/audit/data/dashboard_data.json`
  (27,246,263 bytes, generated `2026-11-24T10:03:34Z`, age 70 min at check time)
- `https://findtorontoevents.ca/audit/data/audit3_ledger.json`
- `https://findtorontoevents.ca/audit2/` — **retired** page (title says so)
- `https://findtorontoevents.ca/audit3/`
- `https://findtorontoevents.ca/investments/` and `/investments/all-dashboards.html`

## Headline counts (`summary`)
- systems 135 · active picks **13** · closed **15,063**
- valid closed **8,203** · integrity-excluded **6,016** · headline coverage **59.4%**
- zero-PnL count **136** · total resolved 8,947

## Defects found (verified)
1. **49 rows have TP/SL on the wrong side of entry** (mostly crypto shorts where
   stop-loss < entry, e.g. `STXUSDT` SHORT entry 0.2596, SL 0.25926; `GC=F` SHORT
   TP 3726.88 > entry 3653.80). These should be rejected at ingest.
2. **40 CLOSED rows have P/L = 0.00%** with a real exit price and `TIME_EXIT`
   (e.g. GBP-USD 1.335, EUR-USD 1.153). Resolution wrote the exit but not the P/L.
3. **Analyst bridge is empty**: `analyst_leaderboard.total_analysts = 0`,
   `total_predictions = 0` while HARVEST has 71 covered symbols. The pipeline is
   not joining analyst data into `/audit`.
4. **`/audit2` is retired** but still returns 200; it must not be counted as a
   live pick surface.
5. **Honest performance is negative-to-flat** in the money-ready block:
   EQUITY intrabar PF **0.9935** (n=261), FOREX **0.6292** (n=651),
   ETF **0.0187** (n=56, flagged 93.75× inflation vs daily). Nothing here is worth
   tracking as an edge; it is useful only as a paper/negative control.
6. **13 direction conflicts** in active picks (e.g. BTCUSDT 8 long / 7 short
   “CONTESTED”) — the resolver output must be stored, not recomputed by consumers.
7. **6 performance alerts**: kimi_signal_tracking 7d WR 17% vs 41% baseline;
   mega_mutation_ema_momentum_m006 33% vs 48%; four systems stale 85–224h.

## US Equity picks (`/audit` EQUITY)
783 closed, mean **+0.061%**, median **−0.896%**, wins 357 (45.6%),
exit mix SL 339 / TP 213 / TIME 226. Consistent with PF 0.9935: no edge.

## audit3
366 cells, 68 tested, **0 proven**, 0 candidates, 67 DSR-scored; classes:
CRYPTO KILL (n=7,009), COMMODITY KILL (52), EQUITY/ETF/FOREX/BOND WEAK,
FUTURES INSUFFICIENT_N. Matches the “nothing proven” conclusion.

## Investment Hub
`/investments/` is a portal (crypto, stocks, forex, funds, meme, ML, goldmines)
with links to per-desk portfolios; there is **no single pick ledger** to ingest.
Track it as a set of dashboards, not as a pick source, unless a JSON feed exists.

## SQL checks
See `DQ_CHECKS.sql` in this folder: freshness, zero-P&L-aged, closed-without-P&L,
TP/SL side, duplicates, orphans, coverage ratio, analyst-bridge emptiness, crowd
staleness, consensus arithmetic, ingest failures. Each check returns offending
rows plus a one-row severity summary.
