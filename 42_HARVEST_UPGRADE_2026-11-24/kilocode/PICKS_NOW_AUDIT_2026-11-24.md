# Audit: picks-now “−1.41% per pick” (2026-11-24T17:25Z)

Source: `ejaguiar1_stocks.vw_picks_now_dedup`, every resolved row
(`exit_pnl_pct IS NOT NULL`) — **585 rows**, 103 symbols, 123 entry dates.
Raw rows saved: `picks_now_resolved_2026-11-24.json`; computation:
`audit_picks_now.py`.

## 1. Cost
- Gross mean: **−1.4103%/pick** (reproduces the published −1.41%).
- Net of **26 bp** round turn: **−1.6703%/pick**.

## 2. Clustering and design effect
- Two-way cluster-robust SE (symbol + entry date): **0.4339%**, vs iid SE 0.1796%.
- **Design effect = 5.84×** (symbol alone 5.25×, date alone 1.59×).
- 585 rows are **not** 585 independent experiments: 103 symbols, 123 dates,
  5,170 symbol-days tracked.

## 3. Mean with cluster-robust CI
- Two-way 95% CI: **[−2.521%, −0.820%]** (net).
- Symbol-cluster bootstrap: [−2.469%, −0.843%].
- Date-cluster bootstrap: [−2.094%, −1.205%].
- **Sign test on per-symbol means: 21 positive / 82 negative, p = 1.07e−9.**

## 4. Clustered win rate
- Pooled: **23.93%**.
- Mean of per-symbol win rates: **22.86%**; median **0.0%** (many symbols never won).
- Mean of per-date win rates: **29.27%**; median **12.5%**.
The 23.9% is not inflated by independence; clustering lowers it slightly.

## 5. Verdict
**−1.41% survives, and net becomes −1.67%.** The defect was understated
uncertainty, not a hidden positive: even the upper bound of the cluster-robust CI
is **−0.82%/pick**. The budget conclusion is unchanged — allocation to the picks
is zero; the page’s −0.404% portfolio impact (24.2% × −1.67%) is correct.
No republish needed for sign; optionally add the clustered CI and design effect
to the page so the uncertainty is stated.
