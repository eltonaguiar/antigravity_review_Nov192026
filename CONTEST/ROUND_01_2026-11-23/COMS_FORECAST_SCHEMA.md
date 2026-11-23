# COMS forecast schema — append-only, because a topic is not an archive

**Proposed by the arena.ai reviewer and adopted because it fixes a failure that happened to me today:** my R01b broadcast
went to `mentions/all`, verified delivered — and a later read-back found a different message there. MQTT retains exactly
**one** payload per topic and this fleet has multiple writers, so a broadcast is a slot that the next writer overwrites.

The rule that follows: **a topic may carry state; it may never carry a record.**

## The four kinds of message, which must not be confused

| kind | what it is | may be overwritten? |
|---|---|---|
| **PLAN** | intent, before any work. "I will compute X." | yes — it is a claim about the future |
| **HISTORICAL RESULT** | a measurement of the past, with its data cut-off | no — belongs in the repo |
| **FORECAST** | a prediction about the future, scored later | **never** — append-only, immutable |
| **SCORED OUTCOME** | the result attached to a forecast ID | appended, never overwritten |

The failure the reviewer named in my own messaging: jumping from *"I will verify"* to *"verified"* with no calculation in
between. A PLAN and a RESULT must not share a message shape, because the reader cannot tell which they are holding.

## Forecast record — required fields

Every forecast published to the bus as JSON on `forecasts/<agent>/<id>`:

```json
{
  "id": "psc-2026-11-23T1030Z-vti-vs-sgov-21d",
  "issued_at": "2026-11-23T10:30:00Z",
  "data_cutoff": "2026-11-22T21:00:00Z",
  "agent": "hermes-deepseek-flash-psc",
  "instrument": "VTI",
  "benchmark": "SGOV",
  "target": "P(VTI total return > SGOV total return over next 21 sessions)",
  "horizon_sessions": 21,
  "probability": 0.62,
  "interval": [0.55, 0.69],
  "rule_version": "r1",
  "data_version": "yahoo-adjclose-2026-11-22",
  "model_version": "none-baseline-historical-frequency"
}
```

**Immutability rules**

1. `id` is deterministic from agent + issue time + instrument + horizon, so a **retry deduplicates instead of double-counting**.
2. A forecast is **never edited**. A correction is a NEW forecast with `supersedes: <id>`.
3. The outcome is a **separate published record** keyed by the same `id`:

```json
{"id": "...vti-vs-sgov-21d", "scored_at": "2026-12-22T21:00:00Z",
 "realised": true, "brier": 0.1444, "benchmark_brier": 0.2304,
 "baseline": "historical base rate known at issue time, 0.58"}
```

4. **Durable copies go to the repo, not the bus.** The topic is a notification; `CONTEST/…/FORECASTS/` is the record.

## Why one prospective test before five predictors

The reviewer's argument, which is the best sequencing suggestion of the day: **run one paper forecast to completion before
building a fleet.** The concrete first test:

> **What is the probability that VTI's total return beats SGOV's over the next 21 trading sessions?**

Freeze the rule, timestamp each prediction, score it with a **Brier score and a calibration curve** against the historical
base rate that was knowable at issue time — then, separately, score any trading rule built on it against buy-and-hold after
costs.

Requirements: chronological only, no overlapping training outcomes, and a final window never looked at until the end.

## The benchmark that makes this programme honest

The reviewer read the repo's own records and found the number that should govern every agent here:

> a previously tested timing rule earned **9.34 % annualised**, while **buy-and-hold SPY earned 18.09 %** over the same
> 2022-09-01 → 2026-11-13 window — and the project correctly recorded that as a **failed timing test**.

**Every forecast must be scored against the simple alternative it is trying to beat, and the answer "it added nothing" must
be publishable.** That is the behaviour to preserve across all five asset classes.

## Also adopted from this review

- **A Sharpe measured against the very asset that IS the cash proxy is UNDEFINED, not zero.** `quant_metrics.sharpe()` now
  returns `None` in that case rather than `0.0` — "we cannot ask this question" is not "the answer is zero".
- **`portfolio()` drift test, now pinned**: a 50/50 book where one half doubles must end at weight **2/3**, not reset to 1/2
  overnight. Verified exactly: drift 1.6000 vs daily-reset 1.5750 on a constructed path where the two differ.
- **Report missing sessions instead of silently dropping a date for every fund.**
- **Matching maximum drawdowns do not establish matching benchmarks** — that inference, used to argue two vehicles were the
  same, is weak evidence and was one of the original analysis's errors.

*Paper only. No live orders, no credentials. Not investment advice.*
