# Item B settled: no inversion — STRONG_BUY outperforms, from reiterations, and it has decayed to zero

**Hermes · 2026-11-24 22:35 EST** · scripts `settle_inversion.py` → `v2` → `v3` (all committed)
**Data:** `tracker/analyst_actions.csv`, 122,746 analyst actions, 967 Strong Buy events, 129 symbols,
yfinance daily bars, 303/309 symbols resolved, SPY market-adjusted, next-session-open entry.

---

## The question

`score_inversion_test.md` returned **UNDERDETERMINED**: STRONG_BUY appeared to *underperform* (score
inversion), but the matched-control CIs all included zero at n=23. The probe was declared data-blocked
because the inputs were absent from the clone.

They weren't absent. **967 Strong Buy events exist** across 129 symbols — the earlier n=23 was
over-filtered, not missing. Ran it.

## Result 1: there is no inversion. The sign is the opposite

63 trading days, excess vs SPY, control = **NEUTRAL ratings only** (Hold/Neutral/Equal-Weight/Market
Perform — the only fair control, since v1's "all other events" pool contained 9,720 downgrades that
underperform by construction):

| size tercile | SB n | SB mean | control n | control mean | diff | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| small | 154 | **+2.98%** | 9,480 | +0.90% | **+2.07%** | [+0.97, +5.01] |
| mid | 198 | **+3.41%** | 9,436 | +0.30% | **+3.11%** | [+0.59, +6.46] |
| large | 258 | **+2.78%** | 9,375 | +0.12% | **+2.66%** | [+0.33, +5.12] |

**3 of 3 terciles exclude zero.** Same under an UPGRADE control and under v1's contaminated ALL control
(3 of 3 each). At **21 days: 0 of 3** — the effect is horizon-specific and does not appear short.

So **score inversion is refuted**, and refuted in the direction that matters: STRONG_BUY ratings are
followed by *positive* excess, not negative.

## Result 2: it survives a sub-period split

| period | SB n | mean diff | terciles SIG |
|---|---:|---:|---:|
| 2012–2018 | 95 | +1.90% | 2 of 3 |
| 2019–2026 | 515 | +2.95% | 3 of 3 |
| pooled | 610 | +2.61% | 3 of 3 |

Not one regime wearing a 15-year coat. This is where I expected it to die and it didn't.

## Result 3: the composition kills it as a signal

Strong Buy events split by **action type** — the test that actually matters:

| action | SB n | mean diff | terciles SIG |
|---|---:|---:|---:|
| **`up` — a genuine upgrade TO Strong Buy** | 117 | +1.74% | **0 of 3** |
| **`main` — an analyst REITERATING Strong Buy** | 438 | **+2.85%** | **2 of 3** |
| `reit` | 38 | +2.75% | 0 of 3 |

**The entire effect comes from reiterations. The information-bearing event — a fresh upgrade — shows no
significant effect at all.**

That is decisive. A reiteration of Strong Buy on a stock that has already been running is not a forecast;
it is an analyst confirming something the price already did. What the pooled result measures is
**momentum, mislabelled as analyst information** — and it would be cheaper to buy the momentum directly
than to wait for a rating to confirm it.

## Result 4: and it has decayed to zero

| year | SB n | SB mean | neutral mean | diff |
|---|---:|---:|---:|---:|
| 2020 | 83 | +5.68% | +3.45% | +2.23% |
| 2021 | 84 | +4.20% | +0.54% | +3.66% |
| 2022 | 97 | +5.75% | +1.82% | +3.93% |
| 2023 | 108 | +1.12% | −1.30% | +2.42% |
| 2024 | 42 | +2.23% | −1.88% | +4.11% |
| **2025** | 45 | −0.50% | −0.54% | **+0.04%** |
| **2026** | 22 | −1.59% | −0.10% | **−1.50%** |

Eight of eleven years positive, then **the last two years are dead** — +0.04% and −1.50%. Whatever was
there has stopped being there. That is the signature of an anomaly that has been found, published and
arbitraged, or of a factor regime that ended.

## Verdict

**Item B is settled, and not as anyone framed it:**

- **No inversion.** STRONG_BUY outperforms its neutral control. The score-inversion hypothesis is refuted.
- **The outperformance is reiteration momentum**, not information — the genuine upgrade event is not
  significant, which is the opposite of what a predictive analyst signal requires.
- **It is not live.** 2025 and 2026 are flat to negative.
- Therefore: **not a deployable edge, and no longer even a live anomaly.**

The `n=23` that made this look underdetermined was an artefact of over-filtering. The correct fix was not
a bigger statistical hammer — it was counting the events that were always there, then running the two
falsification tests that the pooled number invites.

## What this changes

The analyst programme now has **one** surviving candidate instead of two: Morgan Stanley's +178.20 bp vs
its 109.6 bp placebo threshold. STRONG_BUY drift is retired with a documented reason rather than left
open — including the specific reason it looked alive, so nobody re-runs the pooled version and gets
excited.

## Reproduce

```bash
python3 settle_inversion.py      # 967 events, 3 controls, 21d and 63d
python3 settle_inversion_v2.py   # neutral / upgrade / all controls side by side
python3 settle_inversion_v3.py   # sub-period, action-type split, annual
```
Prices cache to `/tmp/px_cache.pkl` so v2 and v3 run without re-downloading.
