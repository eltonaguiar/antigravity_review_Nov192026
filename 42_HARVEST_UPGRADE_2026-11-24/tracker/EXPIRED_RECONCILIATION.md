# Reconciliation — the agent's EXPIRED diagnosis supersedes my price-gap hypothesis

**Hermes · 2026-11-25 00:35 EST**

Kilo's `EXPIRED_ROOT_CAUSE.md` (`2463ecb`) reached the correct diagnosis while I was reaching a wrong one. Its
verdict stands. This note exists only so the record shows why, and so my earlier claims are formally withdrawn
rather than quietly dropped.

## What the agent found that I did not

| mode | rows | share of EXPIRED |
|---|---:|---:|
| **STATUS MISLABEL** | **26,608** | **89.7%** |
| RESOLVER BUG (`RESOLVE_FAILED_MAX_RETRIES`, has `exit_price`, pnl=0) | 1,664 | 5.6% |
| PRICE GAP (no join, no price bar at/after expiry) | 2,623 | 8.8% |
| LOGIC DEFECT (closed ≤24h, TP/SL unreachable) | 369 | 1.2% |

The dominant mode is **stale status synchronisation**: `at_pick_outcomes` says `EXPIRED` / `pnl_pct = 0`,
while the joined `trading_picks` row already holds the real outcome.

Its worked example — pick `004093a29134452d`, SOLUSDT:

```
at_pick_outcomes : EXPIRED   pnl_pct 0.0000
trading_picks    : TIME_EXIT pnl_pct +0.2132  exit_price 88.93
```

**The return was already computed. The outcome table simply never received it.**

## Where my hypothesis was wrong

I claimed the fix was to re-fetch prices and re-resolve from the bar tables. For **89.7% of the pile that is
unnecessary** — the PnL is sitting in `trading_picks` and only needs a sync. My plan would have re-derived
26,608 returns that already existed, from price series that in 8.8% of cases don't cover the symbol at all.

I also wrote "no parent table has `pick_id`". Technically true and practically misleading: the join is
`at_pick_outcomes.pick_id = trading_picks.id`, which matches **26,748** expired rows. I declared the key
orphaned without testing the obvious alternative column, which is the same mistake in miniature as declaring
the dates absent without checking `resolved_at`.

## Consequences — and this is the part that matters

If 26,608 of the zeros have a real return available:

1. **The +6.34 bp mean and −38.98 bp median are not the book's expectancy.** They are the expectancy of the
   33,092 rows that happened to be synced. The mislabelled majority is excluded from that figure by nothing
   but a failed sync.
2. **The corrected figure may be computed immediately** — no price fetching, just a join and a status
   reconciliation over `trading_picks`.
3. **The cost-gate verdicts are provisional.** FOREX at +32.45 bp mean and crypto at +8.85 bp were computed
   on the synced subset; both classes are heavily represented in the mislabelled set.
4. **The expired pile is therefore not a data-loss problem at all — it is a sync bug**, which is a far
   cheaper and faster fix than anything I proposed.

## What I would do next, in one step

Recompute the per-class table by **unioning** `trading_picks` outcomes into `at_pick_outcomes` on
`pick_id = id`, preferring the `trading_picks` PnL wherever the outcome row is `EXPIRED` with zero. Report
`n` added per class. That single query replaces the entire re-resolution plan I wrote, and it is the right
thing to have done before any of my price-fetching machinery.

## Record

- My earlier claims — "no dates", "unrecoverable", "compromised at the schema level" — are **withdrawn**.
- Kilo's four-mode diagnosis at `2463ecb` is authoritative for this question.
- The independent-model cross-check that prompted this reversal was correct on all three of its objections.
