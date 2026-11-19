# MD Survey — buried strategies, statistical measures, methodologies (2026-11-19)

**Scope:** 3,951 `.md` files in `eltonaguiar/findtorontoevents_antigravity.ca`.
Question: what in them is worth surfacing — viable strategies, statistical
measures, or quoted methodologies — and what deserves to go into an audit2.

---

## 1. The statistical vocabulary (this is the real buried treasure)

The MD corpus is saturated with an academic-grade measurement vocabulary. Raw
mention counts (case-insensitive, `grep -rhoiE` over all `.md`):

| Measure / method | Mentions | What it is |
|---|---|---|
| Walk-forward analysis | 3,617 | OOS test via rolling re-fit; the repo's only decision-grade signal |
| Kelly criterion | 3,297 | Position sizing from edge + odds |
| PBO (Prob. of Backtest Overfitting) | 2,656 | Bailey–López de Prado; chance a backtest is overfit |
| Expectancy | 2,043 | Net PnL per trade — the honest edge definition |
| Sharpe ratio | 1,667 | (see DSR for the corrected form) |
| Calibration | 1,546 | Brier / reliability of probability forecasts |
| Profit factor | 1,432 | Gross win / gross loss (misleading alone) |
| Bonferroni | 1,183 | FWER multiplicity correction |
| Sortino | 688 | Downside-vol Sharpe |
| IC (information coefficient) | 643 | Rank correlation of forecast vs outcome |
| Deflated Sharpe Ratio (DSR) | 418 | Bailey–López de Prado; Sharpe haircut for #trials |
| CSCV | 321 | Combinatorially Symmetric Cross-Validation (PBO) |
| Kelly criterion (explicit) | 291 | — |
| Benjamini–Hochberg | 100 | FDR multiplicity correction (audit3's kill gate) |
| Triple-barrier | 82 | López de Prado labeling (TP/SL/time) |
| Fama–French | 73 | Factor model (size/value/momentum) |
| Purged CV + embargo | 70 + 494 | Leakage-safe cross-validation |
| Probabilistic Sharpe | 59 | Bailey–López de Prado |
| Black–Litterman | 58 | Prior-informed allocation |
| Holm–Bonferroni | 34 | Step-down FWER |
| Harvey et al. / Harvey–Liu | 28 + | Multiple-testing haircut on t-stats |
| Markowitz | 17 | Mean-variance |
| Newey–West | 16 | HAC standard errors |
| White's Reality Check | 7 | Data-snooping test |
| Meta-labeling | 225 | López de Prado — ML on a primary signal's correctness |

**Takeaway:** the repo already *names* the full institutional measurement stack.
The gap is not vocabulary — it is that most of these are implemented in
scattered files but only **four** are wired into the one page that matters
(audit3): expectancy-primary gate, Benjamini–Hochberg, DSR, and walk-forward.
`docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §3 confirms DSR/PBO/pairs/meta-labeling
exist in code but are **not** in audit3.

---

## 2. "Viable strategies" buried in the MDs — and why they are mostly illusions

The freshest machine-scored status artifact is
`alpha_engine/data/walkforward_results.json` (generated 2026-11-19T04:11Z):
**52 strategies → 0 ELITE / 3 STRONG / 11 VIABLE / 3 MARGINAL / 35 FAILING.**

The 3 STRONG + 11 VIABLE names and their sample sizes:

| Verdict | n | WR | PF | Strategy |
|---|---|---|---|---|
| STRONG | 24 | 83.3% | 10.78 | `forex_rsi2_mean_reversion` |
| STRONG | 48 | 72.9% | 3.72 | `strong consensus (alpha_engine, luxalgo_filters)` |
| STRONG | 14 | 64.3% | 5.98 | `drawdown_recovery_rsi_eth` |
| VIABLE | 21–43 | 50–71% | 1.5–2.7 | `clone_hl_copy_lb`, `macd_rsi_m048`, `post-earnings-rev-scout`, `vix-mean-rev-scout`, `mtf-align-scout`, `crypto_liquidity_wick_reversal_v1`, `golden-cross-stocks`, `forex-rsi-ema-scout`, `vwap-reversion-scout`, `gap-and-go-stocks` |
| VIABLE | 136 | 52.2% | 1.58 | `rs-breakout-scout` (the only n>100) |

**The honest caveat (F6 again):**
- Every STRONG and 10 of 11 VIABLE cells have **n < 50**. Sharpe 20 on n=24 is a
  small-sample illusion, not an edge.
- `crypto_liquidity_wick_reversal_v1` (VIABLE, n=43) is the exact case the review
  already flagged: cited elsewhere at n=4,904 (backtest) vs realized n=43 at
  +0.15%/trade — **below round-trip cost**.
- `forex_rsi2_mean_reversion` (STRONG) is FOREX — the class whose `fx_prices`
  table ends 2026-02-09 and has **zero computable selection alpha**.
- `rs-breakout-scout` (n=136) is the one name that is both large-n and belongs to
  the EQUITY class — the only class with positive OOS Sharpe (+0.61, 33 folds).

So the "buried viable strategies" reduce to: **the same recurring strategy
*families*, not 700 distinct winners.** The families with a real economic prior
(and where they recur in the MDs):

| Family | Economic prior | Recurring names in the MDs |
|---|---|---|
| Trend / TSMOM | 140-yr evidence, crisis alpha | `rs-breakout-scout`, `donchian-*`, `golden-cross-stocks`, `mtf-align-scout` |
| Carry | paid to hold risk | `forex_carry_momentum`, funding/basis arb, `sentinel_fund_strategy` |
| Mean reversion | overreaction, capacity-capped | `forex_rsi2_mean_reversion`, `vwap-reversion-scout`, `vix-mean-rev-scout` |
| PEAD | post-earnings drift (Bernard–Thomas) | `post-earnings-rev-scout`, `pead_strategy.py` |
| Value / quality | risk premium | `multi_asset_institutional`, `alpha_fundamentals` |
| Breakout / momentum | volatility clustering | `vol-contraction-scout`, `adx-trend-scout` |

Other scattered claims found via grep (with their status): `quan_engine_swing`
"PF 1.57, the ONLY strategy with positive expectancy at scale"; Bollinger bounce
"65.3% WR on 501 OOS trades"; RSI reversal "60.6% on 165"; "6 strategies show
statistically significant edge (p<0.05)". None of these survived audit3's
beta-separated, 2×-cost gate — so they are **discovery-namespace candidates at
best**, not deployable edges.

---

## 3. What is actually worthy of an audit2 page

audit2 should **not** be another strategy list (that is what created 700+
p-values). It should be the **methodology + measure glossary that the strategy
list keeps ignoring**. Concretely, three things are worth surfacing:

1. **The measurement stack as first-class content.** A table of the §1 measures
   with: definition, the file where it is implemented, and whether it is wired
   into audit3's gate (`alpha_engine/audit3_tribunal.py`). This turns the
   scattered vocabulary into a single auditable "here is how we test an edge".

2. **Strategy *families* as pre-registered pods, not strategy names.** One card
   per family in §2 (trend/carry/value/PEAD/mean-reversion), each with its
   economic prior and its kill criterion — mirroring
   `docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` §4 (E8/E9/E10/E3/E14). No card for any
   n<50 backtest winner.

3. **The honest verdict as the headline** (already audit3's job): 0 PROVEN,
   1 CANDIDATE, 10 KILL; no positive selection alpha; EQUITY the only positive
   OOS Sharpe. audit2's role is to explain *why* the measures say that — not to
   paste stale PF tiles.

Given `/audit2` is currently a 404 (see `PAGES_AUDIT2_AUDIT3.md` and
`SWARM_AUDIT2_HISTORY.md`), the cleanest path is to **fold this content into
audit3's "Method & Limits" tab** rather than resurrect a second, divergent
surface. If a separate audit2 must exist, it is a *methodology page* (measures +
pods + verdict), never a live-PnL dashboard — that is audit3's job and they must
not disagree.
