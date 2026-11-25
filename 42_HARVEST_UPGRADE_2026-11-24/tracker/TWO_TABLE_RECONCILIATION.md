# Two-table reconciliation — which PnL is authoritative?

**Read-only** comparison of `at_pick_outcomes` and `trading_picks`, 2026-11-25.
Credentials read at runtime; never printed or committed. No writes.

## The disagreement

| measure | value |
|---|---:|
| rows where both tables have a non-zero PnL | **7,945** |
| rows that disagree | **1,263** |
| disagreement rate | **15.9%** |
| largest absolute gap | **187.18 pp** |
| mean from `at_pick_outcomes` | **−0.0929%** |
| mean from `trading_picks` | **+0.0172%** |

The means have **opposite signs**, so choosing a table decides whether the book looks profitable.

## Price-arithmetic test

For each overlapping row, compute direction-aware return from `trading_picks.entry_price`,
`exit_price`, and direction: long `(exit/entry−1)*100`; short `(entry−exit)/entry*100`.

- **6,049** rows had a usable price pair for this test.
- **`at_pick_outcomes` matches the price arithmetic: 5,833 / 6,049 = 96.4%.**
- **`trading_picks` matches: 4,626 / 6,049 = 76.5%.**

The disagreements are not rounding. The largest are **sign flips** in `trading_picks`:

| pick_id | symbol | entry | exit | computed | at_pick | trading |
|---|---|---:|---:|---:|---:|---:|
| `battleground_btcusdt_buy_..._2026_03_04t22_00_00_00_0` | BTCUSDT | 72,708.30 | 140,755.998 | **+93.59** | **+93.59** | **−93.59** |
| `battleground_ethusdt_buy_drawdown_..._2026_03_27` | ETHUSDT | 1,984.20 | 3,708.271 | **+86.89** | **+86.89** | **−86.89** |
| `2240` | DOGE-USD | 0.09467 | 0.1656725 | **+75.00** | **+75.00** | **−75.00** |
| `5` | SOL-USD | 84.8558 | 22.2831 | **−73.74** | **−73.74** | **+73.74** |
| `18` | BNB-USD | 618.6505 | 1059.6245 | **+71.28** | **+71.28** | **−71.28** |

These rows carry resolver lineage `signflip_purge_20260` (360 rows among the overlapping set) or
backfill versions; the sign was flipped in `trading_picks.pnl_pct` while `at_pick_outcomes` kept the
price-consistent sign.

## Which table is authoritative?

**Neither table's `pnl_pct` should be quoted unverified. The authoritative source for prices and
resolution is `trading_picks`; the authoritative *reported* PnL is the one recomputed from those prices.**
In practice:

- **`trading_picks` is authoritative for schema-level evidence:** it stores `entry_price`, `exit_price`,
  `take_profit`, `stop_loss`, `created_at`, `closed_at`, `exit_reason`, `intrabar_*`, direction. Neither
  PnL column can be audited without those fields.
- **`at_pick_outcomes` is closer to correct as a PnL projection:** 96.4% price-arithmetic agreement vs
  76.5% for trading. It also carries `resolver_version`/`resolution_method`.
- **The disagreement is a defect in `trading_picks.pnl_pct`, not evidence that at_pick is wrong:** the
  worst gaps are sign flips where entry/exit prices clearly support at_pick.
- **Resolution:** recompute `pnl_pct` from `trading_picks` entry/exit/direction, quarantine
  `signflip_purge_20260` PnL, then compare to `at_pick_outcomes`. Do not COALESCE one table over the other
  without reporting the 15.9% disagreement and both means.

### Table-level verdict

| table | role | trust |
|---|---|---|
| `trading_picks` | price/timestamp/exit-reason source | **authoritative for prices and resolution** |
| `trading_picks.pnl_pct` | derived field | **NOT reliable** — sign-flip corruption |
| `at_pick_outcomes` | reported PnL + resolver lineage | **closer to price-consistent**, but not auditable without prices |
| Recompute from `trading_picks` prices | canonical result | **use this** |

## Why the lineage supports this

`at_pick_outcomes.resolver_version` records the resolver path; `trading_picks` records the execution
fields. The `signflip_purge_20260` version appears on the overlapping rows and is associated with the
sign-flipped PnL. The repair is not to pick a winner between two stored means but to make the stored PnL
a deterministic function of entry/exit/direction, then assert the two tables agree or fail loudly.

## Recommendation

1. Recompute PnL from `trading_picks.entry_price/exit_price/direction` for every overlapping row.
2. Quarantine `signflip_purge_20260` rows from any published mean until re-derived.
3. Publish the 15.9% disagreement and both means beside any class result until reconciled.
4. Never use `COALESCE(t.pnl_pct, o.pnl_pct)` as a fix; that silently chooses an answer.
5. Re-run the cost gate after the recomputation; the current +6.34 bp/−38.99 bp figures inherit this
   disagreement.

next_probe: generate a pick_id-level canonical PnL table from trading prices, count agreements with
at_pick, and report the corrected class means before any table write.
