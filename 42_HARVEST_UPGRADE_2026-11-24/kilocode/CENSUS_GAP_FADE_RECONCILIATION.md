# gap_fade classification reconciliation (2026-11-24T16:01Z)

Where the “BLOCKED with bars>0” contradiction comes from: **the source, not the
artifact writer.** `1000_TODOS.json` already marks these cells `blocked_no_data`
before any result JSON is written.

## Counts
- `gap_fade` cells: **100**.
- `bars > 0`: **12** — BTC 1h 2,161 / 4h 541 / 1d 365 / 1w 53; ETH 1d 365, 1w 53;
  SOL 1d 250, 1w 36; plus DOGE and others.
- `bars = 0` or unknown: **88**.
- **All 100 notes end with the reason `None`** (e.g.
  `BLOCKED_NO_DATA: bars=2161; None`), so the block is documented by neither a
  data gap nor a semantic reason.

## Verdict
This is a **classification defect**, not legitimate blocking:
1. Twelve cells have enough bars to be measured at their horizon yet are
   `blocked_no_data`.
2. Even the 88 with zero bars carry no reason code; “blocked” with a null reason
   is not auditable.

The artifact-level “12 BLOCKED with bars>0” is a faithful copy of this source
defect.

## Fix
1. Reclassify the 12 cells with bars: run `gap_fade` at that horizon, or state the
   real constraint (e.g. requires next-bar open) as a reason code.
2. Replace the null reason on all 100 with a `reason_code`
   (`NO_COVERAGE_STRUCTURAL`, `STRATEGY_UNSUPPORTED`, …).
3. Then regenerate artifacts and rollup; validator should drop
   `blocked_with_bars` to 0.
