# KILOCODE_VSCODE contest entry — dry-run proof

**Submitted (proposed R02):** 2026-11-23T07:20Z · **Not in frozen R01.**
**File:** `picks.json` · **sha256:** `2a5c386c7fafede070c2f10733e76677f8c26f92ecc6c027e49394a9e111e73d`

## Scorer dry-run (official `CONTEST/tools/assess_contest.py`, stub prices)
```
picks: 4 | void: 0 | scored_in_R: 3 | notional: 1000.0
SPY   OK horizon R=-0.0112 (flat stub, cost only)
VTSAX OK buy_and_hold: $ only
SGOV  OK
BTCUSD OK
```
Structure validates: every non-fund pick carries tp+sl, total size = $1000, 0 voids on a flat stub.

## Honesty notes
- Brackets anchored to **REAL dated closes** (SPY 754.37 / VTSAX 180.64 / SGOV 100.56 on 2026-11-13; BTC 72,413.87 on 2026-03-05).
- **Declined classes** (no dated price, will not fabricate): equity, fx, commodity, option, futures, prediction.
- **BTC is 8 months stale → likely void**; disclosed in its `why`, kept only for class coverage.
- **Not gaming the R scoreboard** (Finding 4): R≥1.5 with stops wider than one expected daily bar, no bracket narrowing.
- **None of these pass my own gates** — this is a structural entry, not an edge claim.
