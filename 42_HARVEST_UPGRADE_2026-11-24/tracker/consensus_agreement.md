# Track C — analyst × crowd/user agreement

**Owner:** ghcopilot · **Date:** 2026-11-24 · **Reproducer:** `consensus_agreement.py` (this directory)
**Program:** `tracker/IMPROVEMENT_PROGRAM.md`, Track C

> ## Verdict: NOT COMPUTABLE — insufficient sample, n = 0 joinable rows
>
> There is no delta to report, and I am not going to manufacture one. Per gate 4 this is
> **INSUFFICIENT SAMPLE**, which is a different outcome from **NO EFFECT**. It is *not* evidence
> that agreement fails to add information, and it is *not* a licence to claim agreement works.

---

## 1. The counts per agreement bucket

| bucket | definition | n | mean net excess | 95% CI | placebo |
|---|---|---:|---:|---|---|
| **AGREE** | pick long AND analyst label ∈ {STRONG_BUY, BUY} | **0** | — | — | — |
| **DISAGREE** | pick long AND analyst label ∈ {SELL, STRONG_SELL} | **0** | — | — | — |
| EXCLUDED | analyst HOLD/neutral — can neither agree nor disagree | **0** | — | — | — |

**Delta (AGREE − DISAGREE): undefined, because both buckets are empty.** No CI, no placebo p, no
top/bottom agreements. Reporting "top and bottom agreements" would require agreeing rows; there
are none. Manufacturing a list from the level distribution would be exactly the substitution the
program forbids.

## 2. Why the buckets are empty — the chain, every step measured

| # | fact | measurement |
|---|---|---|
| 1 | Picks exist | 585 resolved picks, `picks_now_resolved_2026-11-24.json` |
| 2 | **All picks are long** | `direction` = `STRONG_BUY` on **585 of 585** — there is no short arm, so "disagree" can only arise from analyst *bearishness* |
| 3 | Analyst labels exist | `harvest_symbol_history.json`: 71 symbols × **4 monthly periods, 2026-08-01 … 2026-11-01** |
| 4 | Symbol overlap is thin | only **17 of 103** pick symbols appear in the analyst feed |
| 5 | **The dates do not overlap** | the 51 picks on covered symbols are dated **2026-06-06 onward (June)** — *before the earliest analyst period*. Picks at/after 2026-08-01 on covered symbols: **0** |
| 6 | No crowd leg either | `crowd_layer.json` `layer_a_direct_matches` = **0**; `best_picks.json` = **0 picks**; `crowd_consensus` in the feed is aggregate counts, not per-symbol |

Joining June picks to the current analyst snapshot would be **lookahead by up to five months**, so
the as-of join is mandatory and it returns nothing. Dropped: 534 picks (symbol absent from analyst
feed) + 51 picks (no analyst period at/before entry) = 585.

## 3. What sample size Track C needs (gate 3: quantify the null)

From the observed pick-return dispersion (n=585, sd = **4.348 pp**), required n **per bucket** at
80% power / α=.05:

| delta to detect | n per bucket | total |
|---|---:|---:|
| 5.0 pp | 12 | 24 |
| 3.0 pp | 33 | 66 |
| 2.0 pp | 75 | 150 |
| 1.0 pp | 297 | 594 |
| 0.5 pp | 1,186 | 2,372 |

**Structural ceiling:** the entire analyst feed is 284 symbol-periods. Even if every one carried a
pick, that is 284 rows split across buckets — so deltas below **~1 pp are unreachable by
construction**, independent of effort. This matches gate 5's logic: if a floor is unreachable, say
so and name what would reach it.

## 4. Cost and benchmark treatment (gate 1 and 2) — stated, and why it would not save the test

`exit_pnl_pct` is used as published; I did **not** apply a second cost, because it is not
established whether it is already net, and inventing a charge would be a fabricated adjustment.

The important point for the *difference* test: a **uniform** cost or benchmark subtraction cancels
exactly in `mean(AGREE) − mean(DISAGREE)`. So the delta would be invariant to it — but only if the
two buckets share a date range and a liquidity mix. They do not (all covered picks sit in June), so
this invariance could not have been relied on here even with data.

## 5. Context only — NOT a Track C finding

The pick population any agreement test would draw from is itself loss-making and stop-dominated:
mean **−1.410%**, sd 4.348%, with **473 of 585 exits (80.9%) at SL_HIT** and 112 at TP_HIT. Recorded
because it bounds what a future positive delta could mean, and because a positive level here would
have meant nothing on its own. It is a level, and Track C does not do levels.

## 6. What was checked so this reads as a finding, not an excuse

Read, not assumed: the pick file (direction distribution, date range, exit reasons), the analyst
history (periods, labels, symbol coverage, `fwd21` completeness 284/284), the crowd artifacts
(`layer_a_direct_matches`, `best_picks.json`, `crowd_consensus` shape), and the as-of join itself.
Every number in §2 and §3 is printed by `consensus_agreement.py` on demand.

## 7. Gates

1. **Net of cost** — policy stated in §4; not applicable at n=0, and no flat constant used.
2. **Characteristic-matched benchmark** — not reachable; no per-window SPY series is held here, and the picks' windows differ. Flagged, not faked.
3. **MDE published** — §3.
4. **`insufficient sample` ≠ `no effect`** — this is the whole verdict.
5. **No gate lowered** — the reverse: I am reporting that the 3 pp-and-below thresholds are unreachable at this universe size.
6. **No new DSR** — none computed.

---

next_probe: **acquire a pick stream that can disagree.** Specifically: ≥33 picks **per bucket** dated ≥2026-08-01, which requires either short-direction picks or picks on analyst-SELL names — because the current stream is 585/585 long on coverage averaging 67.7% buy-side, so the DISAGREE arm is empty *by construction*, not by absence of effect. Backfilling analyst history into June–July 2026 would recover the 51 existing covered picks but would very likely still leave DISAGREE near-zero (only 4 SELL-labelled symbol-periods exist in the whole feed). The binding constraint is the missing short/bearish arm, not the missing history.
