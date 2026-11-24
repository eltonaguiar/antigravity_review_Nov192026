# Edge search plan — pre-registered, net-of-cost, forward-gated

**Status:** proposed 2026-11-24. This is a search plan, not an edge claim.
The programme currently has **0 proven** active strategies. Analyst consensus predicts
attention, not direction; the Polymarket crowd-favorite point estimate is negative but
not significant; the score-inversion test is underdetermined; and Track A has no firm
above the 750 clean-event floor (max BofA 551). Do not call anything "edge" until it
clears the gates below.

## Objective

Find a repeatable, net-of-cost signal with out-of-sample evidence. Accept a clean null.
Three candidate families, in order of testability:

### A. Top-trader persistence
**Hypothesis:** traders in the top decile of trailing 30/90-day realised PnL continue to
outperform the median trader over the next 30 days, after fees/slippage.

- Data: Polymarket Data API v2 `/leaderboard` snapshots (daily) plus `/positions`,
  `/activity`, `/trades` for ranked wallets. Record snapshot time, PnL, volume, rank,
  wallet. Do not backfill ranks from later data.
- **Measured API defect (2026-11-24):** `window=1d|1w|1m|3m|all` returns the SAME 100
  rows and the SAME PnL/volume on every value. The window parameter is ignored (or the
  endpoint is all-time only). Do not use it to claim trailing-30/90-day performance.
  Compute period PnL from each wallet's dated `/activity`/`/trades` rows instead; the
  leaderboard is only a candidate list.
- Test: rank IC (Spearman) between trailing rank and forward PnL/ROI; top-decile mean
  minus median; hit rate; net of a stated fee/slippage. Cluster by wallet and by event;
  bootstrap CI. Require **≥100 wallets** and **≥30 daily snapshots** before a verdict.
- Falsifiers: rank IC ≤ 0 with CI excluding 0; top-decile advantage disappears after
  event/topic clustering; the result is driven by one market or one wallet.
- Failure mode to control: survivor/leaderboard selection; wallets that stop trading;
  wash/self-trades; open positions marked at stale prices.

### B. Recommendation-pattern mining
**Hypothesis:** specific dated analyst-action patterns predict 21-day net excess return
after lag-1 entry, matched controls and costs.

Pre-register only three patterns (no fishing):
1. **Upgrade + target raise:** action=up, strict ordinal increase, `pt` above prior record.
2. **Repeat upgrade:** a second strict upgrade by the same firm-symbol within 90 days.
3. **Contrarian downgrade:** action=down on a name with no other downgrade in 20 days.

- Data: `tracker/analyst_actions.csv` + PIT target fields; matched control = same date,
  same ADV and 126-day momentum tercile, as in `score_inversion_test.md`.
- Cost: 10/30/100 bp by ADV tercile; entry next open; exit 21 trading days.
- Stats: symbol-cluster CI; BH across the three patterns; report n and MDE.
- Falsifiers: any pattern with n<100 is `underpowered`, not "works"; CI-low ≤0 after cost
  is a reject; a single firm/sector driving the result is a confound.

### C. Pick-source persistence
**Hypothesis:** a system/agent with above-median net performance over a trailing 90-day
window stays above median over the next 90 days.

- Data: audit closed picks with resolved net PnL; group by system/source; require ≥100
  closed picks per source and ≥3 rolling windows.
- Test: rank persistence, top-vs-rest difference, cluster by symbol and date.
- Falsifiers: no persistence after controlling for asset-class mix and market beta.

## Gates that apply to every candidate

1. Point-in-time inputs; no look-ahead; entry lag-1.
2. Net of measured costs and benchmark (matched control, not a single index).
3. **n ≥ 100** independent-ish observations; report effective/clustered n.
4. Net CI-low > 0; **DSR ≥ 0.95** with a frozen trial registry and honest N.
5. **PBO < 0.5** where the configuration set supports CSCV; otherwise do not report PBO.
6. Survives two sub-periods and a negative control (date/label shuffle, random entry).
7. Forward paper n ≥ 100 after the rule is frozen; backtest is `CANDIDATE` only.
8. No live capital until all of the above.

## Immediate sequence

1. Commit the daily leaderboard snapshot collector; start collecting; do not analyse
   persistence until ≥30 snapshots exist.
2. Run the three recommendation-pattern tests on existing actions; publish n, net means,
   CIs, BH q, MDE; expect mostly underpowered.
3. Audit pick-source persistence; if no source has ≥100 closed picks, say so.
4. Fix the forward harness and promotion path; publish the trial registry.
5. Report `0 candidates` or a candidate that cleared every gate. No other headline.

## Non-negotiables

- Do not reuse a backtest as forward evidence.
- Do not choose a correction because it produces the desired answer.
- Do not label a contaminated cell KILL/DEAD; label it INVALID DATA.
- Do not quote a single-number equity cost; use the 0.98 / 4.01 / 12.07 bp bracket.
- If the search returns null, publish that; a null after this design is informative.

next_probe: collect 30 daily Polymarket leaderboard snapshots and run the pre-registered
rank-IC test; in parallel, run the upgrade+target-raise pattern with n and BH.
