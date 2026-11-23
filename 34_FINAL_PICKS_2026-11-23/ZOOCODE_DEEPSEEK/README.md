# ZOOCODE_DEEPSEEK (Zoo Code, subq-savant-1.4) — final picks, 2026-11-23

```
filed_utc:       2026-11-23T02:35Z
filed_local:     2026-11-23T02:35Z (host UTC)
repo_at:         findtorontoevents_antigravity.ca:origin/main@b508d25cd52eef7165499c1616b48f30e1169946
ranked_list:     docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md (0 entries) + docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md (criterion)
honest_headline: 0 INVESTABLE / 11 NOT_INVESTABLE / 3 UNKNOWN (14 rows) — no asset class clears all four eligibility gates, so the ranked list is empty and the correct count of investable picks is ZERO.
endorsed_count:  0
```

**This folder is not a buy list.** Nothing in it is an allocation, a size, or an order. It is a
research ordering of the least-refuted candidates, every one of which is labelled
NOT INVESTABLE / PAPER-ONLY / NO CAPITAL. If you skim only one line, read the headline above:
**zero picks are investable.**

---

## 1. What this folder is

My final per-class picks and overall ordering for the 2026-11-23 window, filed in the fixed
schema that [`34_FINAL_PICKS_2026-11-23/README.md`](../README.md) defines, plus the testing
record the operator asked for. Five files:

| File | What it answers |
|---|---|
| `README.md` (this file) | one-screen summary, criterion, headline, watchlist, pointers |
| `PER_ASSET_CLASS_PICKS.md` | all 12 classes, ordered by the doc-24 lower-bound key, each with verdict, deciding number, cost provenance, best in-class candidate, what would move it, proximity score |
| `OVERALL_TOP_PICKS.md` | the top 5 overall as a WATCHLIST — each with the gate it fails, what would have to become true, and what would go wrong |
| `TESTING_AND_BACKTESTING.md` | per class: what was actually backtested, what it proved, what it did NOT prove, the cost overlay method, the gate arithmetic, and why no new backtest was run this round |
| `NEXT_STEPS.md` | next work ranked by expected value per hour, with ETAs, including the two paths producing new evidence |

## 2. The ranking criterion (reproduced, not invented)

From [`24_EXECUTION_PLAN_2026-11-23.md`](../../../../docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md), the key is the
**lower bound** of the Sharpe-vs-policy-rate construct on committed capital:

```
S(c)   = ( NetCAGR_cc(c) − r_f ) / σ_net,cc(c)              r_f = 4.32%
LB(c)  = ( LB95(NetCAGR_cc(c)) − r_f ) / UB95(σ_net,cc(c))  ← the RANK KEY
```
— formula at `docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:494-495`; `r_f = 4.32%`
at `docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:494` and its source
`tools/capacity_model.py:49` (cited `docs/preregistration/HML_VALUE_TEST_2026-11-22.md:117`).

I rank on `LB(c)`, never on the point estimate. Tie-breaks, in the order doc 24 adopts
(`docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:529-536`): (1) higher 95% LB on net excess,
(2) lower turnover, (3) larger margin under 2× costs, (4) larger deflated Sharpe,
(5) higher capacity headroom.

**An empty ranked list is permitted and is the correct answer when everything fails its gate**
(`docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:518-519`). It is what I return.

## 3. Why the list is empty

A class earns a ranked entry only if all four hold (`docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:511-516`):
measured cost, per-class kill rule cleared, 2×-cost survival, and a CI on net return.
**No class has a CI on net return on committed capital**, so `LB(c)` is undefined for all 12
(`docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:97-99`). The one class where the
arithmetic can be pushed to a bound at all is FX CARRY, and it is **≤ −0.248**
(`docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:109`).

## 4. Settled tally

`0 INVESTABLE / 11 NOT_INVESTABLE / 3 UNKNOWN (14 rows)` — `docs/edge_research/23_DEFINITIVE_ANSWER_2026-11-22.md:195`,
enforced by `tests/test_edge_research_tally_consistency.py:1-18`. The tally split was disputed
in older notes (doc 23 lines 9–10 still carry a stale `10/4` correction note); the 14-row total
never was, and doc 26 recounts the rows to 11/3 from the table itself
(`docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:144-167`).

## 5. The watchlist (top 5 by evidence quality and proximity to decidability)

**NOT INVESTABLE / PAPER-ONLY / NO CAPITAL.** No allocation is implied. The correct count of
investable picks is zero. Ordering and reasons are in `OVERALL_TOP_PICKS.md`.

| # | Name | Class | Verdict | The number that decides it |
|---|---|---|---|---|
| 1 | FX carry quintile | FX CARRY | NOT INVESTABLE | Sharpe **−0.126** vs 4.32%; `LB(c) ≤ −0.248` `[SRC: docs/edge_research/26_FINAL_RANKED_LIST_2026-11-23.md:89,109]` |
| 2 | FX mean-reversion 5d/5d | FOREX | UNKNOWN | break-even **4.3038 bp** vs cost **7.533 bp** `[SRC: docs/edge_research/22_FINAL_SYNTHESIS_2026-11-22.md:30]` |
| 3 | Equity breakout / HML value | EQUITY | NOT INVESTABLE | PF **0.9917 @25 bp/side**, PF **1.2865 @0 bp** `[SRC: docs/edge_research/15_PROGRAMME_SCOREBOARD_2026-11-22.md:34]` |
| 4 | Bond momentum B1/B2/B3 | BOND | NOT INVESTABLE | break-even **0 bp/side**, B1 Sharpe **−0.5497** `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:92,96]` |
| 5 | Crypto VWAP-reversion paper pod | CRYPTO | PENDING (PENDING_N) | **5** closed rows, 0 forward rows on the pod's own hypothesis `[SRC: verified_strategies/paper_pilot/crypto_intraday_sim_paper_log.jsonl]`; `[SRC: docs/edge_research/25_DRAFT_RANKED_LIST_2026-11-23.md:106]` |

## 6. What every number here rests on

Costs are **round-trip 1-minute bar-RANGE UPPER BOUNDS, not NBBO and not Corwin-Schultz**
(`updates/2026-11-23-cost-estimator-description-correction.md:19-31`). `COMMISSION_UNKNOWN` for
every class (`docs/edge_research/24_EXECUTION_PLAN_2026-11-23.md:562`). Every figure below carries a
`[SRC: path:line]` marker or the word `UNMEASURED`.

---

PROVENANCE: repo `eltonaguiar/antigravity_review_Nov192026`, branch `main`; every number read from
the MAIN repo `eltonaguiar/findtorontoevents_antigravity.ca` at `origin/main` =
`b508d25cd52eef7165499c1616b48f30e1169946` via `git show`, never from the shared working tree
(which sits on `push/phase2-round-2026-11-22`). Date 2026-11-23.
