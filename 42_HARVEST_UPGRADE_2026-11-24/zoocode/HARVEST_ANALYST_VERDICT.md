# HARVEST analyst-action verdict table

zoo-savant · 2026-11-24 · source [`backtest_results.json`](backtest_results.json) from
[`backtest_analyst_actions.py`](backtest_analyst_actions.py) (153 symbols, 72,108 dated actions,
SPY benchmark, identical entry/exit dates for pick and benchmark).

**Cost convention:** a class mean is one position's excess return over SPY, so the net figure
subtracts **26 bp** (one round turn on the position leg; the SPY leg is shared by every class and
cancels in comparisons *between* classes). Every cell shows **raw then net**; neither appears alone.

**Inference:** `t_clust` is the t-statistic over **per-symbol** means (one value per symbol), not over
marks. `design` = (t_raw / t_clust)² is the variance inflation from overlapping windows. A cell is
publishable only if `|t_clust| ≥ 1.96` **and** n_symbols ≥ 30.

## Verdict table

| h | class | n_raw | n_sym | raw % | net % | t_raw | t_clust | design | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 5 | UP | 4,111 | 147 | −0.044 | −0.304 | −0.66 | −0.93 | 0.5× | **NOT PUBLISHABLE** |
| 5 | DOWN | 3,942 | 146 | −0.049 | −0.309 | −0.67 | −1.16 | 0.3× | **NOT PUBLISHABLE** |
| 5 | INIT | 3,807 | 146 | −0.253 | **−0.513** | −3.46 | **−0.86** | **16.4×** | **NOT PUBLISHABLE** |
| 5 | MAINTAIN | 44,719 | 149 | +0.009 | −0.251 | +0.40 | +0.54 | 0.6× | **NOT PUBLISHABLE** |
| 21 | UP | 4,094 | 147 | +0.601 | +0.341 | 4.40 | 1.88 | 5.5× | **NOT PUBLISHABLE** |
| 21 | DOWN | 3,916 | 146 | +0.515 | +0.255 | 3.46 | 1.25 | 7.7× | **NOT PUBLISHABLE** |
| 21 | INIT | 3,807 | 146 | +0.526 | +0.266 | 3.06 | 2.08 | 2.2× | **PUBLISHABLE** |
| 21 | MAINTAIN | 43,952 | 149 | +0.160 | −0.100 | 3.67 | −0.50 | 53.3× | **NOT PUBLISHABLE** |
| 63 | UP | 4,056 | 147 | +2.186 | +1.926 | 7.77 | 2.45 | 10.1× | **PUBLISHABLE** |
| 63 | DOWN | 3,876 | 146 | +1.727 | +1.467 | 6.58 | 3.69 | 3.2× | **PUBLISHABLE** |
| 63 | INIT | 3,741 | 146 | +2.058 | +1.798 | 6.67 | 3.36 | 3.9× | **PUBLISHABLE** |
| 63 | MAINTAIN | 42,811 | 149 | +1.157 | +0.897 | 14.54 | **0.46** | **1,013.5×** | **NOT PUBLISHABLE** |

## The two cells asked about specifically

**(1) INIT at 5d: it does NOT survive, so it is not an AVOID signal.** Raw −0.253% (t_raw −3.46) looks
strong, but net it is **−0.513%** and once clustered by symbol `t_clust = −0.86`, with a **16.4×**
design effect. The raw significance is an artifact of overlapping windows: 146 symbols carrying 3,807
marks. Since it fails after clustering, I would not publish it as an avoid signal. Its cost-adjusted
direction is still mildly negative, so I also would not publish it as a long.

**(2) MAINTAIN at 63d: it does NOT survive.** Raw +1.157% and net +0.897% look like a solid return,
but `t_raw = 14.54` collapses to **`t_clust = 0.46`** at a **1,013.5×** design effect. MAINTAIN has
~28,000 marks per symbol, nearly all overlapping the same few market moves, so the pooled t is
essentially counting the same observation thousands of times.

## The uncomfortable pattern

Every action class at 63d is positive against SPY, including DOWN (+1.467% net). A signal that says
*buy* and *sell* with equal confidence is not directional: the levels carry survivorship (the universe
is today's ticker list applied to 2012-2026) and shared beta. The defensible comparison is
**within-symbol UP minus DOWN**, which is survivorship-immune because both arms share the same
universe: measured at 63d as **+0.099% raw / −0.161% net**, sign test p = 0.796 over 134 symbols. That
is no evidence of direction.

So the only three "PUBLISHABLE" cells above (21d INIT, 63d UP, 63d DOWN, 63d INIT) are publishable as
*descriptions of the sample*, with a stated design effect, and **not** as evidence that an analyst's
direction predicts returns. Any claim of the latter would need the within-symbol contrast to clear
zero, and it does not.

## Reasons, exactly, for each NOT PUBLISHABLE cell

| cell | reason |
|---|---|
| 5d UP, DOWN, MAINTAIN | `\|t_clust\| < 1.96` (0.93, 1.16, 0.54) |
| 5d INIT | `t_clust = −0.86` after a 16.4× design effect; the raw t of −3.46 is inflated by overlapping windows |
| 21d UP | `t_clust = 1.88`, just below 1.96 |
| 21d DOWN | `t_clust = 1.25` with a 7.7× design effect |
| 21d MAINTAIN | `t_raw` 3.67 is positive but `t_clust = −0.50` at 53.3×: the pooled sign is not the symbol-level sign |
| 63d MAINTAIN | `t_clust = 0.46` at a 1,013.5× design effect |
