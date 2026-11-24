# Recommendation-pattern tests — P1/P3

**Status:** tested 2026-11-24. No candidate. Same lag/controls/cost as `score_inversion_test.md`.
**Data:** `tracker/analyst_actions.csv` (122,746 rows) + Yahoo daily prices; 2023-06-01..2026-10-01.

## Patterns

- **P1 — upgrade + target raise:** action=up, strict ordinal increase, current target > prior record target by >0.1%. Events 4,128; usable with price/controls **1,257**.
- **P2 — repeat upgrade within 90d:** 126 events, near the 100 floor; **not tested** (underpowered).
- **P3 — contrarian downgrade:** action=down, strict ordinal decrease, no other downgrade on the same symbol within 20 days. Events 5,202; usable **951**.

Entry next session open; exit close 21 trading days later; benchmark = same-date mean of other symbols in the same ADV and 126-day momentum tercile; cost 10/30/100 bp by ADV tercile; 2,000 symbol-cluster bootstrap.

## Results

| pattern | n | mean net excess | 95% clustered CI | symbols | design effect |
|---|---:|---:|---|---:|---:|
| P1 upgrade+target | 1,257 | **+59.47 bps (+0.595%)** | **[-5.7, +121.2]** | 253 | 1.76 |
| P3 contrarian downgrade | 951 | **+27.30 bps (+0.273%)** | **[-30.2, +84.3]** | 249 | 1.00 |

Both point estimates are positive, but **both 95% CIs include zero**. P1 is the stronger candidate only by point estimate; it does not clear the gate.

## Verdict

**No candidate.** P1 and P3 fail the net CI-low > 0 requirement; P2 is underpowered. This is not evidence that the patterns are absent — it is an underpowered/near-miss result, and it must not be published as an edge.

## Next

Non-overlapping 63-day horizon; add 2026 H2 events; BH across P1-P3; publish q and MDE; require CI-low > 0 after costs before any forward harness.

next_probe: add 2026 H2 events and run non-overlapping 63d with BH q across P1-P3; P1 needs CI-low > 0, not just a positive mean.
