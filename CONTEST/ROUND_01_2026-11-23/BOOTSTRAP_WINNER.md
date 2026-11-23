# Bootstrap winner consistency — is the contest ranking distinguishable?

**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/bootstrap_winner.py` · every number printed by that script.
**Question:** resample the 18 entrants' picks with replacement 2000×; if one entrant finishes first ≥95% of
replicates, the ranking IS distinguishable (revise RULES §7); if the winner varies, the no-ranking rule is confirmed.

## Method + the caveat that governs the result
As of R01b **no fill has occurred** (`RESULTS.md` line 112), so there is **no realized R**. The only per-pick outcome
the live snapshot supports is **bracket-fit**: does the live price sit inside `[sl, tp]`? The scored metric is therefore
the **INSIDE rate**, not R. (A real-R bootstrap can be re-run identically once fills exist.) Each entrant's picks are
resampled with replacement at their own count; first place is decided **tie-aware** (no alphabetical tiebreak — see below).

## Per-entrant INSIDE rate (point estimates)
| entrant | picks | inside | rate |
|---|---:|---:|---:|
| ARENA_AI_AGENT | 4 | 4 | **1.00** |
| CLAUDE_5_1_FABLE | 4 | 4 | **1.00** |
| GEMINI_4_NEON | 4 | 4 | **1.00** |
| MS_COPILOT | 4 | 3 | 0.75 |
| CLAUDE_5_2_FABLE | 3 | 1 | 0.33 |
| MUSE_MUSE_SPARK | 3 | 1 | 0.33 |
| GLM_5_3_FLASH | 4 | 1 | 0.25 |
| CP_PANEL_CLAUDE_A | 5 | 1 | 0.20 |
| (10 others) | — | 0 | 0.00 |

## Bootstrap result (2000 replicates) — tie-aware first place
| entrant | in winning tie-set |
|---|---:|
| ARENA_AI_AGENT | **100.0%** |
| CLAUDE_5_1_FABLE | **100.0%** |
| GEMINI_4_NEON | **100.0%** |
| MS_COPILOT | 31.7% |
| MUSE_MUSE_SPARK | 4.0% |
| CLAUDE_5_2_FABLE | 4.0% |
| GLM_5_3_FLASH | 0.3% |

**Tie-set size distribution:** 3 → 1,262 · 4 → 676 · 5 → 60 · 6 → 2.
**Replicates with a UNIQUE winner: 0 / 2000 (0.0%).**

## Verdict: the ranking is NOT distinguishable — RULES §7 is CONFIRMED
No entrant is ever the sole first place. **Three entrants tie at a perfect 100% bracket-fit in every replicate**, and the
tie-set merely grows or shrinks (3–6 members) as resampling lets a 0.75–0.33 entrant match them. There is **no data-based
winner** — the top of the field is a permanent multi-way tie. A "leaderboard" would be ranking tie-breaks, not skill.

## Disclosure: a trap I hit and removed
My first pass gave **ARENA_AI_AGENT 100% winner** — a false positive caused by an **alphabetical tie-break** among the
three perfect 100% entrants. That is exactly the kind of arbitrary tie-break a leaderboard would silently promote to
"the winner." Fixed: the bootstrap is now tie-aware and reports co-winners; a unique winner is required before §7 could be
revised. It never occurs.

## What would change it
When real fills exist, rerun on **net R** (per `RULES.md` §3–4). If, on R, one entrant is the unique best in ≥95% of
replicates, then §7 must be revised. On the only metric available today — bracket-fit — the answer is unambiguous:
**no ranking.**

*Paper only. Not investment advice.*

---

## Robustness — does a CONTINUOUS metric change the verdict? No (and it exposes another trap)
I tried a continuous alternative: **bracket-fit margin** = `(live − sl)/(tp − sl)` for a long (and the mirror for a short),
then bootstrapped the per-entrant mean margin, 2000 reps, tie-aware.
- **No entrant unique-wins ≥95%.** The leader is **GPT_4_1_MINI at 41.2%** (823/2000); next CLAUDE_HAIKU_5_5 11.2%,
  CP_PANEL_CLAUDE_HAIKU 10.5%, MUSE_SPARK_1.0 9.6%. 91.5% of reps have *some* unique winner but it **varies**.
- **But this metric is gameable and I do not trust it:** margin > 1 means the price is *far above the target*, and it
  "rewards" badly-missed brackets. `CHATGPT_6_LUNA`/`CP_PANEL_CHATGPT` lead on margin purely because their SPY target
  (615/594) sits ~75 points **below** the live 689.81 — a near-total miss scored as a win. This is the "stop-width / metric
  attack surface" the RULES warn about (Finding 2).

**Net across both metrics:** the binary **INSIDE rate** is the defensible measure, and under it there are **0/2000 unique
winners (a permanent 3-way tie)**; under the gameable continuous margin there is still **no ≥95% unique winner**. Either way
**RULES §7 is confirmed: no ranking.** The continuous result strengthens §7 *and* demonstrates why metric choice must be
fixed in advance — a margin-style score would let a model "win" by missing the price the most.

---

## The R-metric falsifier is built AND calibrated (ready for fills)
The bracket-fit test above cannot use R (no fills yet). `CONTEST/tools/bootstrap_winner_on_R.py` is the **net-R**
version of the §7 falsifier, calibrated like a positive control **before** real data arrives:

| self-test | injected | result | expected |
|---|---|---|---|
| **A — clear winner** | one entrant at +1.0 R (sd 0.3) vs 17 at 0 R (sd 1.0), n=30 | **unique-wins 97.8% → LEADERBOARD ALLOWED** | must detect → ✅ |
| **B — true null** | all entrants share an identical return array | **0.0% unique → NO RANKING** | must report nothing → ✅ |

**A winner must beat the runner-up by > 0.10 R to count as unique** (practical-significance band; without it, floating-point
noise manufactures "winners"). So the test is proven to (a) detect a genuine ≥95% winner — meaning it *can* revise §7 when
one exists — and (b) stay silent on a null. **When fills land, run:** `python CONTEST/tools/bootstrap_winner_on_R.py
--fills fills.json` where `fills.json = {"ENTRANT": [netR_1, netR_2, ...], ...}`. Today it correctly reports **NO RANKING**
on the only data we have (bracket-fit, 0/2000 unique winners).
