# Multi-model deliberation: what counts as a rating EVENT?

**Status:** evidence for a decision, not the decision itself. Produced by a three-round multi-model
protocol on 2026-11-24. The owner freezes the definition; this file records what three independent
models concluded, where they converged without prompting, and the cost of the answer they did not
know about.

## Protocol

| Round | What happened |
|---|---|
| 1 | Three models answered the same question independently. **Our measured numbers were withheld** so they could not echo them back. |
| 2 | Each model was shown the other two answers anonymised as A / B / C and asked to rank them, name what **all three** missed, state one final definition, and give the settling measurement. |
| 3 | This file: synthesis, plus the one fact the models could not see. |

**Sources (all keyless, local router `127.0.0.1:4000/v1`):** `free-mode-large`, `free-mode`,
`deepseek-chat-direct` — all returned 200. Two other endpoints are recorded as failures rather than
silently dropped: `openrouter-ring-1t` returned **401** (no cookie auth) and `nvidia-deepseek-v4-pro`
returned **410** (model end-of-life 2026-08-07). A failed round is still a result about routing.

## Round 1 — the three answers

| Model | Event definition | Notable content |
|---|---|---|
| `free-mode-large` | `up` only | Named four distinct selection biases: direction-selection from dropping `down`, new-coverage selection from `init`, staleness from `reit`, maintenance noise from `main` |
| `free-mode` | `up` only | Weakest of the three — vague on context, no operational rule |
| `deepseek-chat-direct` | first `up` per broker-stock after **≥6 months** with no prior `up`/`down` | Named coverage-initiation bias, silent-maintenance bias, and selection on the dependent variable |

## Round 2 — the convergence

All three independently produced **the same ranking: C > A > B**, and all three named **the same
thing all three had missed**:

> **Pre-event drift / anticipation.** Brokerages upgrade after price and earnings momentum, so forward
> returns partly reflect continuation that was already in the price. The control variable they each
> proposed: **cumulative abnormal return over the pre-event window (e.g. t−20 to t−1)** as a covariate,
> or matched non-event controls.

This is the third independent surface to reach that conclusion in one day: the ChatPlayground panel
(Gemini 3.1 Pro, Claude Opus 5.5) proposed the identical covariate unprompted, and it is what our own
`selection_null` work was built for. **Nine model instances across three tools, no shared context,
same defect.** That is corroboration of the safest kind.

All three also chose the **same final definition** and the **same settling measurement**:

- **Definition:** first `up` for a broker-stock pair after ≥6 months with no prior `up` or `down`,
  requiring a tradeable price at the t+1 open.
- **Measurement:** compare forward 1-month abnormal returns for clean-window `up` events against all
  `up` events (including those following `reit`/`main`), report the difference with its t-statistic,
  with pre-event drift in the model.

## What this settles — and it is not the question I asked

I framed the choice as "reiterations in or out" (definition A = `up`+`down`+`init`, B = those plus
`reit`). The deliberation answers that clearly and then goes further:

1. **`reit` does not count. Unanimous, 3/3.** Every model treated a restated unchanged rating as
   contamination, not signal — "silent-maintenance bias: reaffirmations cluster after good news."
   The blocker is resolved in the direction of A, not B.
2. **`init` does not count either. Unanimous, 3/3** — "new coverage concentrates on stocks the broker
   expects to perform." **This means definition A was itself too loose**: it includes `init`.
3. So the defensible event is **`up` only**, which is narrower than either option I put to the panel.
   `down` is excluded from the primary and belongs in a separate symmetry test, otherwise the design
   selects on the dependent variable.

**Consequence:** the zoo figures already on origin (300 = 14 firms, 500 = 5, 750 = 0 under
`up/down/init`) are computed on a definition the deliberation rejects. Those numbers are not wrong,
they answer a different question. Under `up`-only they will be **lower**, and the 750 floor may become
unreachable at any practical ticker count.

## The one fact the models could not see

Pre-registration also has to be **implementable**. Each model ranked option C first — first `up` after
a 6-month clean window — while its own stated weakness was "conditioning on no prior action selects
stocks with stale coverage." Neither round knew our measured event density, because I withheld it.

The cost: a six-month no-prior-action rule does not filter rows, it **deletes most of them**. At 308
tickers the looser `up/down/init` definition cleared 750 events for 11 firms; `up`-only inside a
6-month window will plausibly leave **single digits or zero** firms above the floor. The most
defensible definition may therefore be the least measurable one, and the choice becomes a genuine
trade-off rather than a correctness question:

| Option | Defensibility | Implementability |
|---|---|---|
| `up` only, 6-month clean window | highest — unanimous 1st choice | **unknown, likely below floor** — must be measured |
| `up` only, no clean window | high — removes `init`/`reit` contamination | same row counts as today's `up` subset |
| `up`+`down`+`init` (current zoo figures) | rejected by 3/3 on `init` | proven: 28/18/11 at 300/500/750 |
| add `reit` | rejected by 3/3 | the most events, the least defensible |

## Recommended decision, for the owner to accept or reject

1. **Freeze the event as `up` only.** `init`, `reit` and `main` are excluded; `down` is excluded from
   the primary and reported as a separate symmetry test.
2. **Do not adopt the 6-month clean window until it is measured.** Run it and report the firm counts
   under it; if it leaves fewer than ~5 firms above their floor, fall back to no clean window and say
   so in the prereg rather than quietly loosening the floor.
3. **Add pre-event drift (CAR over t−20..t−1) as a required covariate**, with results reported both
   raw and drift-adjusted. This is now corroborated across three independent tools.
4. **Keep the falsifier as the within-ticker date-swap placebo.** The 6-month window is a
   contamination control, not a falsifier, and the two should not be conflated.

## The measurement that settles it (next probe)

On the collected data, count distinct **broker-stock pairs** with at least one `up`, versus the count
surviving a 6-month no-prior-`up`/`down` filter, and report firms above 300/500/750 for both. That
single table converts this from an argument about definitions into a statement about what is
measurable — and it is the number that should decide, not a vote of models.
