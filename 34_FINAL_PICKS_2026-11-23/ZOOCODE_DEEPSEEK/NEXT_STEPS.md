# Next steps — ranked by expected value per hour, 2026-11-23

**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL.** Nothing here authorises a trade, a size, or a data
purchase.

The two paths that can produce **NEW evidence** come first. Cost refinement is deliberately **not**
on this list, because the standing bound forbids new data purchases, and because for BOND and
COMMODITY a cheaper cost estimate cannot change the verdict (break-even ≤ 0 bp; see §4).

---

## 1. Weekday FOREX spread sample — highest EV/hour, zero authoring cost

- **What it settles:** whether FX mean-reversion's break-even (**4.3038 bp**
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`) sits above or below the
  *representative* weekday spread. Today the only measured spread is the Sunday-reopen upper bound,
  **7.533 bp** `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:51-52]`.
- **State:** already automated. `.github/workflows/fx-cost-overlap.yml` runs weekdays inside
  13:00–16:00 UTC, six runs, first cron `48 13 * * 1-5`
  `[SRC: .github/workflows/fx-cost-overlap.yml:34-40]`. Next fire **Mon 2026-11-23 13:48Z**.
- **What it CANNOT produce:** `INVESTABLE`. By construction the sampler writes only
  `NOT_INVESTABLE`, `HUMAN_REVIEW_REQUIRED`, `BLOCKED_NO_REPRESENTATIVE_SESSION` or
  `UNCHANGED_UNKNOWN` `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:133]`.
- **Honest expectation:** even a cheaper weekday spread may not close it. The window-clustered CI
  includes zero at every cost tested so far (at 7.533 bp: **−10.85, +4.55**)
  `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:133]`, and at 1 bp it is
  **[−4.32, +11.09]** `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]`. The most
  likely outcome is a better-sourced `UNCHANGED_UNKNOWN`, which is still worth having.
- **Known defect:** the chained strategy re-run will record `CHAIN_FAILED` because
  `tools/fx_meanrev_research.py` is absent from `main`
  `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:293-297]`. The cost measurement itself is
  unaffected, but fixing the chain (restoring or repointing that module) would add a strategy re-run
  to the same cron for maybe 30–60 minutes of work.
- **ETA:** measurement fires automatically on the next weekday. Reading and classifying the result:
  ~1 hour. Fixing the chain: ~1 hour.
- **EV/hour: highest of anything on this list** — it converts the largest single assumption into a
  fact at no new-data cost.

## 2. Raise the crypto paper pilot's close rate

- **What it settles:** whether the pod can reach the **n ≥ 100** forward gate before it is irrelevant.
- **State:** **5 closed rows** (bollinger_mr 3, vwap_reversion 2, btc_4h_rsi_macd 0) and 2 open
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl]`,
  `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:3-32]`. It ticks every 30 min
  (`7,37 * * * *`) `[SRC: .github/workflows/crypto-intraday-sim.yml:17-20]`.
- **The date on main:** the n ≥ 100 date is `UNMEASURED` because no close rate is recorded
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:110]`. The brief quotes ~1.5 closes/day
  and derived dates **n≥20 ~2026-12-03** and **n≥100 ~2027-01-25**; those two dates and the rate are
  **not on origin/main**, so I report them as the brief's arithmetic, not as verified figures. Against
  the gates **2026-12-19** (day-30) and **2027-01-18** (day-60)
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:110]`, 1.5/day reaches n=20 in time for
  day 30 but n=100 only after day 60. That arithmetic is what makes the gate the binding constraint.
- **What would raise the rate:** more slots with signals (the sim only closes on signal-driven exits and
  TIME), or shorter holds. `vwap_reversion` is **HALTED** at **11.5229%** trailing drawdown vs a 10%
  limit `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_state.json:29-30]`, so it contributes
  nothing until a human reviews it.
- **Honest expectation:** raising the close rate raises the *count*, not the *quality*. The lagged lab
  PF is **0.957** with PBO **0.84–0.97** `[SRC: docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:322-324]`,
  so more rows are as likely to confirm a failure as to find an edge. The value is that a decision arrives sooner.
- **ETA:** review of the halted slot ~1 hour; a config change to add slots ~2 hours plus ~1 week to observe its effect.

## 3. Fix the shared working tree / branch hygiene (enabling, not research)

- **What it settles:** whether anyone can trust a number read from the checkout. The shared tree sits
  on `push/phase2-round-2026-11-22`, thousands of commits behind main, with untracked files that
  masquerade as repo content.
- **Why it is high EV:** every hour spent on a number read from the wrong tree is an hour lost, and
  this round's own discipline (read everything via `git show origin/main:`) exists because of it.
- **ETA:** ~30 min to check out a clean detached main or a fresh worktree and document it.

## 4. Not on the list, and why: cost refinement

- **For BOND and COMMODITY it cannot change the verdict.** Both momentum families have break-even
  `c* ≤ 0 bp/side` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:47]`,
  `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:96]`. With `cost > 0 ≥ c*`, net is
  negative at *any* positive cost, so a tighter spread estimate cannot cross it
  `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:149-155]`.
- **True NBBO needs a data acquisition:** a consolidated-quote feed (SIP/CTA or a vendor with
  historical NBBO) plus a historical store `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:107]`.
  **No NBBO/SIP/Databento/CME secret exists** in the repo `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:145]`,
  and the standing bound forbids new data purchases. So the current bar-range upper bounds are the best that can be had.
- **PENNY_STOCK** would gain a better cost but still has **no strategy** and N = 0, so a better number
  would still have nothing to evaluate `[SRC: updates/2026-11-23-nbbo-measurability-probe.md:157-163]`.

## 5. Queue behind those: the things that would actually create a new test

| Step | Settles | ETA |
|---|---|---|
| Roll-adjusted, back-adjusted commodity series with a pre-declared roll rule + per-contract commission | unblocks COMMODITY momentum and term-structure carry from `BLOCKED_MISSING_DATA` `[SRC: docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:119-121]` | 1–2 days, needs contract-level data |
| Point-in-time universe with delisted names | unblocks the HML preregistration (blocker B1) `[SRC: docs/preregistration/HML_VALUE_TEST_2026-11-22.md:21-38]` | days; needs historical membership |
| A specified ETF strategy with a forward ledger | gives ETF a first strategy at all `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:31]` | 1 day to specify + months to validate |
| Mutual-fund fee schedule | unblocks MUTUAL_FUND `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:134]` | hours, if a source is permitted |
| Second quotable MEME name | unblocks the MEME kill `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:67]` | hours |

## 6. What NOT to do

- **Do not run a new backtest on the roll-corrupted commodity series or a backfill-contaminated equity universe.** It would produce a number that cannot be trusted; see `TESTING_AND_BACKTESTING.md` §0.
- **Do not re-open a class whose break-even is ≤ 0.** Cheaper fills cannot flip it.
- **Do not manufacture a pick to fill the requested 3–5.** The watchlist is labelled, and its count of investable names is zero.

---

PROVENANCE: repo `eltonaguiar/antigravity_review_Nov192026`, branch `main`; all figures read from
`eltonaguiar/findtorontoevents_antigravity.ca` at `origin/main` =
`b508d25cd52eef7165499c1616b48f30e1169946` via `git show`. The n≥20 / n≥100 dates and the ~1.5
closes/day rate are not on main and are reported as the brief's arithmetic, unverified. Date 2026-11-23.
