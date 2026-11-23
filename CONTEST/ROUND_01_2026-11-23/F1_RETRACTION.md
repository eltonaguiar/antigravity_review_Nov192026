# F1 RETRACTED — the contest measured my prompt, not the models

**Date:** 2026-11-23 · **Status:** supersedes F1 in `R01B_REVIEW_RESULTS.md`, `RESULTS_R01B.md` and the site's `#r01b`.

## What F1 claimed

> **Price recall, not forecasting, is what the field fails first.** 69 picks across 18 entrants; **41 were void at the fill**
> because the bracket had already passed before a bar printed. Reproduced across 18 entrants on two surfaces, which makes it
> *"the most robust finding in the programme."*

A reviewer objected that I had never run the arm **where the price is supplied**, and that the separating experiment costs
nothing. That was correct, so I ran it.

## The experiment

Same model (`qwen2.5-coder:14b`, local, GPU), same rules, same symbols (SPY, BTCUSD, EURUSD), same instant, one variable:
**whether the prompt contains a timestamped quote.**

| arm | picks | inside their bracket | void at fill |
|---|---|---|---|
| **bare** — "use realistic price levels near the current market" | 3 | **0** | **3** |
| **stamped** — identical prompt **plus** current quotes at 11:05Z | 3 | **3** | **0** |

**A 0/3 → 3/3 flip on a single change.** Supplying the price does not make the model better; it makes the answer
*well-posed*.

## What this means

1. **F1 was a harness finding, not a model finding.** The void rate measured whether my prompt supplied a price. It did not
   measure a capability, a tendency, or a failure of reasoning.
2. **The "18 entrants on two surfaces" was never evidence.** Three independent reviewers had already said so —
   **pseudoreplication**, because the entrants share training data and price priors. The experiment now supplies the
   mechanism: they were all answering the same malformed question.
3. **Neither arm tests forecasting.** Given the price, placing a bracket around it is arithmetic, not prediction — a model
   that can subtract will score 3/3 and has demonstrated nothing. So the contest, as designed, measures *bracket
   construction*. Both arms are uninformative about skill; one is merely better-posed.
4. **The honest description of the contest is the one subq.ai proposed:** it is a **bracket-calibration test**, not a
   paper-trading contest. Renaming it makes the finding *stronger*, because it is then a true statement about the thing it
   actually measures.

## What survives, and what does not

| claim | status |
|---|---|
| "Models cannot recall prices accurately" | **not established.** The bare arm fails, but that is the prompt's doing |
| "The field fails at price recall first" | **RETRACTED** |
| "Reproduced across 18 entrants → robust" | **RETRACTED** — pseudoreplication, now with a mechanism |
| "An out-of-bracket pick is void at the fill" | **stands** — that is the rule, and it is a real scoring defect (F2/F3 remain) |
| "The contest measures bracket construction, not forecasting" | **stands, and is now the headline** |

## The limits of this experiment, stated honestly

- **n = 3 per arm, one model, one moment.** A 0/3 vs 3/3 flip is striking but it is three observations each side.
- It does **not** show that the stamped arm would produce brackets that *survive the horizon* — only that they straddle the
  quote at issue.
- It says nothing about whether the picks are **good**, only that they are **well-formed**. A trade well-formed around
  today's price can still be a bad trade.

The correct next test is the one already logged: run the stamped arm over several models and score the brackets **out of
sample** — do they resolve at target or stop, net of cost? That is a forecasting test. This was a well-posedness test.

## The warning I ignored for three hours

Before any large model reviewed it, I ran F1 past three local endpoints as separate subprocesses. I recorded the run as a
**reviewer collapse** — and I was right about that, but I understated it and then used it to throw the content away.

All three headers, from the saved outputs:

```
review_pollinations.txt  --- ollama:qwen3:8b [200] 58.15s 1543 chars
review_router_local.txt  --- ollama:qwen3:8b [200] 100.16s 1799 chars
review_vllm_local.txt    --- ollama:qwen3:8b [200] 87.6s 1731 chars
```

**The vLLM arm was also `ollama:qwen3:8b`** — not `Qwen3.6-35B-A3B-NVFP4` as intended. My earlier note said "one model
reported twice." It was **one model, three times.** The corroboration problem was total, not partial.

But look at what that one model actually said — all three times, unprompted, in the same words:

> **F1: OVERSTATED** — *"Void picks may reflect bracket timing, not forecasting failure; the test doesn't isolate forecasting
> ability."*

That is **exactly the objection** that later killed F1. A local 8B model reached it in 58 seconds, for free, and I had it in a
file on disk for three hours.

**So the reviewer who killed F1 was not Claude. It was `qwen3:8b`, and I dismissed it on provenance.**

The reasoning I used was: *three identical model names means no corroboration, therefore discard the round.* The first half is
true. The second half is a **non sequitur** — a provenance defect invalidates **corroboration**, not **content**. Right rule:

> **Duplicate provenance tells you not to count the answer as n=3. It does not tell you the answer is wrong.**

I had one well-reasoned objection and threw it out for failing to be three objections.

## Why this one is worth the damage

F1 was the claim I liked most: it was vivid, it reproduced, and it made the models look worse than the referee. It was also
a measurement of my own prompt. **The most quotable finding was the least load-bearing one**, and it took a reviewer asking
"did you run the other arm?" to find that out.

The rule that follows, and it generalises: **before attributing a failure to the subject, run the arm where the subject's
job is well-posed.** If the answer flips, you measured the question.

*Paper only. No live orders, no credentials. Not investment advice.*
