# Expiry semantics — what is a pick that expires without hitting TP or SL?

**Author:** copilot · **Date:** 2026-11-25 · **Scope:** one question, argued from first principles,
with the cross-class comparability consequence of each answer.

**The question.** A pick has an entry, a take-profit, a stop-loss and a time limit. The time limit
arrives with neither TP nor SL touched. Should its return be recorded as **0**, as the
**mark-to-market return at expiry**, or **excluded** from the class average?

**Answer up front: record the mark-to-market return at expiry as the primary value**, publish 0 and
exclusion as sensitivity columns, and never let a missing expiry price become a 0. The reasoning
below is why the other two are wrong as primaries.

---

## 1. What is the estimand?

The ledger exists to answer: *if someone had followed this pick exactly as specified, what would they
have experienced?* The specification includes the time limit. A pick is not "enter and wait
indefinitely"; it is "enter, and if neither barrier is touched, be flat by time T". So the realised
outcome of following the rule **is** the position's value at T.

That single sentence settles the question. Any recording rule that is not the value you would
actually have received is not measuring the strategy — it is measuring a different strategy that
nobody was told to run.

## 2. Choice A — record 0

**What it asserts:** that nothing happened.

**Why it is false:** the position existed. A pick that drifted from 100 to 103 and never touched a
barrier at 105 has made 3%. Recording it as 0 states you made nothing. The only world in which 0 is
correct is the world where the position was never opened, which is a data-integrity condition, not a
return.

**Why it is tempting:** it is the cheapest value to write, and it makes "win rate" look tidy because
0 is obviously not a win. That is the tell — a recording rule chosen for how it makes a summary
statistic look rather than for what it measures.

**Second-order damage:** a 0 is neither a win nor a loss, so it silently corrupts every hit-rate
statistic that treats "not a loss" as "a win". A record with a large mass of expired picks recorded
as 0 will show a win rate computed on a denominator that includes non-events. And any payoff-ratio or
breakeven-hit-rate comparison built on top inherits the distortion, because the mean loss is
understated by every expired pick that actually lost 2%.

**Cross-class consequence — this is the decisive argument against it.** The size of the distortion
scales with how much a position typically moves inside the time limit. Over an identical 21-day
limit, a bond ETF that expires flat is genuinely near 0 (error ≈ a few bp), while a crypto pair that
expires "flat" against its barriers may still have travelled 8% (error ≈ 800 bp). Recording 0
therefore applies a **small correction to low-volatility classes and a large one to high-volatility
classes**, always in the direction of making the high-vol class look worse. Any cross-class ordering
produced under a 0 rule is partly an artefact of the volatility difference, not a difference in edge.
This is the same failure as comparing a bond's round-trip cost to crypto's: the two numbers are
computed on different scales and then sorted.

## 3. Choice B — mark-to-market at expiry (recommended)

**What it asserts:** you held to the time limit and closed at the market. This is exactly what the
rule specified, and it is the only choice whose value a follower would have realised.

**Why it is the right primary:** it is the unique choice that is (a) unbiased for a fixed horizon,
(b) defined for every pick that has a price series, and (c) comparable across classes once the
horizon is held constant.

**What it requires to be trustworthy — all four are load-bearing:**

1. **A defined mark.** Expiry value must come from a named price series (same source as the entry
   price, same timestamp convention, e.g. the close of the expiry bar). A different source for entry
   and exit injects a systematic bias that is indistinguishable from edge.
2. **Barrier detection on high/low, not closes.** If TP/SL touching is judged on closing prices, a
   pick that traded through the stop intrabar but closed above it will be misclassified as expired —
   and it will be recorded as a small MTM loss instead of a full stop-out. That understates losses.
3. **Both barriers in the same bar ⇒ assume the stop.** Intrabar sequence is unknowable at this
   resolution; the conservative assumption is the one that does not flatter the record.
4. **A missing expiry price is UNMEASURED, never 0.** This is the trap that has bitten this programme
   repeatedly: absent data silently becoming a zero and then entering an average. If the expiry bar
   is missing or stale, the pick must be reported as `UNMEASURED` with the reason attached, and it
   must not enter the average.

**Cross-class consequence:** comparability is preserved **only at a common horizon**. MTM at T for
two classes with different T is not comparable — a 7-day crypto pick and a 126-day equity pick are
different measurements. Either fix the horizon across classes, or report per-day normalised returns
with the raw horizon printed beside them. Report both the count and the share of picks reaching
expiry, because a class where 90% expire is mostly a buy-and-hold measurement wearing a trading
label.

## 4. Choice C — exclude expired picks

**What it asserts:** that only barrier-resolved picks are evidence.

**Why it is the worst of the three for a class average:** the excluded set is not random. It is
precisely the picks whose outcome was **small** — the ones that did nothing much. Removing them
leaves a sample that is **tail-conditional**: every survivor is either a full winner (TP) or a full
loser (SL). The mean of that sample is an estimate of the average barrier-to-barrier move, and it
will be reported as "expectancy" while having nothing to do with the expectancy of following the
rule. If TP and SL are symmetric, expect the retained mean to sit near a mix of +R and −1R, which
can be positive or negative for reasons entirely unrelated to skill.

**Second-order damage:** the effective sample size becomes class-dependent and undisclosed. A class
with a generous time limit will expire most picks and retain few, so its "average" carries the widest
variance while looking equally authoritative. And the exclusion rule invites exactly one form of
gaming: widen the time limit until only the decisive outcomes remain.

**Cross-class consequence:** comparability is destroyed, and destroyed unevenly. The class with the
longest time limit loses the most observations, so cross-class ranking is dominated by retention
rate rather than by performance. Two classes with identical true edge can be ordered arbitrarily by
their time-limit choices alone.

## 5. Recommendation, stated as a rule the ledger can enforce

1. **Primary value** = mark-to-market return at expiry, from the same price source as entry, marked
   at a named timestamp convention.
2. **Flag it**: `exit_reason ∈ {TP, SL, EXPIRED}` on every record, so expiry outcomes remain
   separable in every downstream table.
3. **Publish three companion columns**: primary MTM, the 0-rule mean, and the excluded-bars-only
   mean. If the three disagree materially, that disagreement is the finding and it belongs in the
   report.
4. **Never** let an absent expiry price enter as 0 — that record is `UNMEASURED` and excluded from
   the average with its count disclosed.
5. **Compare classes only at a common horizon**, or on per-day normalised returns with the raw
   horizon printed. Print the expiry share per class beside every class average.
6. **Barrier touching on intrabar high/low**, with SL assumed when both are touched in one bar.

## 6. What each choice does to cross-class comparability, in one table

| choice | unbiased for a fixed horizon? | what it does to the class ranking | failure it invites |
|---|---|---|---|
| **0** | no — biases every class toward zero | penalises the **high-volatility** class hardest; ordering partly reflects vol, not edge | hit rates computed on non-events; mean loss understated |
| **MTM at expiry** | yes, if the mark and horizon are fixed | preserves ordering at a common horizon; breaks if horizons differ | source/timestamp mismatch; intrabar barrier misses; missing price silently zeroed |
| **exclude** | no — tail-conditional | dominated by **retention rate**; classes ordered by time-limit choice | mean becomes barrier-to-barrier move reported as expectancy; widest variance looks most authoritative |

---

**One-line summary:** record the mark at expiry, flag it, keep 0 and exclusion as sensitivity
columns, and treat a missing price as unmeasured — because the only question the ledger can answer is
what a follower would have received, and neither 0 nor exclusion answers it.
