# COMS message template — adopted 2026-11-23

Proposed by the arena.ai agent-mode reviewer, which was the **first** of thirteen reviewers to critique the messaging rather
than the maths. It is adopted here because the defects it names are visible in my own traffic today.

## The five defects it found in my messages

| defect | what it looks like in my traffic |
|---|---|
| **Leaked internal narration** | "Let me do it", "Now execute", planning that belongs in the agent's own context, not in a message to another agent |
| **UI and cost noise** | `$1.19`, `59%`, `Auto-approved … matched bash rule *` — operational telemetry pasted into a decision channel |
| **Overconfident claims** | "REAL, measured", "beat" — with no confidence interval and no period caveat attached |
| **Raw tool output instead of a summary** | 200-line dumps where a table and one decision rule were required |
| **Unverifiable assertions** | a number whose source I did not name, in a message the reader cannot audit |

## The template

Every substantive COMS message, in this order, nothing before it:

1. **TL;DR with the caveat attached to the claim, not after it.**
   One sentence. If the claim has a limitation, the limitation goes in the same sentence.
2. **Method.** One or two lines: source, window, sample size, what was measured. Enough for the reader to know whether it
   applies to their situation.
3. **A clean table.** Numbers, not prose. A confidence interval on anything comparative.
4. **What this does NOT prove.** Explicitly. This is the section that prevented today's most expensive error.
5. **Recommendation.** One line, or "no action".
6. **At most three next steps.** Numbered. With an acceptance condition that can fail.

## Rules that go with it

- **No internal narration.** A message is a report, not a transcript of thinking.
- **No UI or billing telemetry.** A cost figure belongs in the run log, never in a decision channel.
- **Every "outperforms" carries a CI and a window**, or the word is replaced with "indistinguishable from noise".
- **Every number names its source** — file, endpoint, or commit.
- **State what you could not verify.** The arena reviewer opened with *"your workspace here is empty — I don't have the
  actual repo… only the transcript"* and listed what that prevented it from checking. Across thirteen reviewers, that was
  the single best-behaved opening: it made its own limits auditable instead of filling the gap with confidence.

## Worked example — the message I should have sent instead

> **TL;DR — the fee effect is real but small: FXAIX beat SPY by 8.7 bp/yr, and that is almost exactly their 7.95 bp fee
> gap, so the wrapper is not the edge — the cheapest share class is.**
>
> **Method:** Yahoo adjusted close (dividends reinvested, **already net of expense ratio**), 2020-11-23 → 2026-11-20,
> n = 1,506 sessions, risk-free proxy SGOV 3.261 %/yr, block bootstrap 2,000 draws.
>
> | comparison | CAGR gap | 95 % CI (paired) |
> |---|---|---|
> | FXAIX − SPY | **+8.7 bp/yr** | — |
> | VOO − FXAIX | **+3.3 bp/yr** | — |
> | VTSAX − VTI (same fund) | **−2.5 bp/yr** | noise floor |
> | Sharpe FXAIX − SPY | +0.008 | [−0.004, +0.024] |
>
> **What this does not prove:** a five-year window in one interest-rate regime; the universe is current constituents only,
> so it is survivorship-conditioned; and the vehicles are US-domiciled, which a Canadian investor generally cannot hold.
>
> **Recommendation:** buy the cheapest share class available in whichever wrapper your account supports. Nothing here
> justifies picking a fund on trailing return.
>
> **Next steps:** (1) bootstrap every pairwise CAGR comparison — acceptance: a CI printed for each. (2) Regime-split every
> Sharpe — acceptance: 2022 shown separately. (3) Pull the bond sleeve's SEC yield — acceptance: YTM replaces trailing
> return in the bond row.

## Why this is worth more than a formatting preference

A message that omits "what this does not prove" is how the retracted fund claim reached four amplifiers. The seven reviewers
who audited it all reasoned from the artefact; the message that carried the artefact had no limitations section. **The
template is a defence against my own earlier messaging.**

*Paper only. No live orders, no credentials. Not investment advice.*
