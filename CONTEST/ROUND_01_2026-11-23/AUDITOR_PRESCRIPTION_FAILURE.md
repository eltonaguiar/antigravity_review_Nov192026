# The auditor agreed with all four bugs — and then prescribed two of them back

**Date:** 2026-11-23 · **Surface:** local endpoints via `ask_free_ais.py`, prompt asks "is each claim CORRECT, and if so give the
right formula in one line" for the four fund-analysis defects.

This is the same failure mode as GPT-4.1 mini endorsing the retracted MER claim — but sharper, because the model was asked for a
**fix** and returned the **defect**.

## What came back

**`ollama:qwen3:8b`** — 144.05 s, 573 chars, and it marked **all four claims CORRECT**:

> **(1) CORRECT.** The adjusted close is already net of MER; subtracting MER again double-counts fees. Formula: use adjusted
> close without subtracting MER.
> **(2) CORRECT.** Sharpe = (mean(daily return)·sqrt(252)) / (stdev·sqrt(252)) with risk-free = 0.
> **(3) CORRECT.** Sortino should be sqrt(sum(x² for x in downside)/len(downside)) and measured against target return.
> **(4) CORRECT.** Rebalance parameter was misdocumented as monthly but simulated daily.
> **Overstatement: 8 basis points per year.**

**Verdicts: 4/4 agreed. Prescriptions: 2/4 are the bugs themselves.**

| # | verdict | its "formula" | correct? |
|---|---|---|---|
| 1 | CORRECT | drop the MER subtraction | ✅ right |
| 2 | CORRECT | `(mean·√252)/(stdev·√252)` with **rf = 0** | ❌ **that is the bug.** It cancels to mean/stdev with no risk-free rate. Correct: `mean(r − rf)/stdev(r − rf) · √252` |
| 3 | CORRECT | divide by `len(downside)` | ❌ **that is the bug.** Correct: divide by **total n**, versus a target return |
| 4 | CORRECT | (no formula offered) | ➖ verdict right, prescription absent |
| fee | — | 8 bp | ✅ right |

## The mechanism

The model pattern-matched **"is this a bug? → yes"** and then, asked for the fix, **re-emitted the clause it had just agreed was
wrong** — because that clause *looks* like the standard formula. `(mean·√252)/(stdev·√252)` is visually plausible (annualisation
appears twice), and `len(downside)` is the naive reading of "downside deviation."

**Agreement on the verdict is not competence at the prescription.** A model can flag an error and then hand it back as the
correction — and it will do so fluently, in one line, with a checkmark.

## The second method failure, same run

`Qwen3.6-35B-A3B-NVFP4` on vLLM returned **[reasoning-only, raise max_tokens]** — 3,042 chars of thinking, **no answer**. Same
shape as `glm-5.3-flash:cloud`.

**Correction to my own note, made the same day:** I first wrote that these models need "≈6k output tokens." A direct test at
`num_predict: 6000` **still returned zero content**:

```
glm-5.3-flash:cloud @ num_predict 6000
  thinking chars : 22,041
  eval_count     : 6000
  done_reason    : length
  content chars  : 0
```

**6,000 was not enough — it consumed the entire budget on reasoning and hit the cap with nothing emitted.** So "≈6k" was a
guess dressed as a rule, tested once, and it was wrong.

The reliable signature is not a token count, it is the triple:

> **`done_reason: "length"` + `content: ""` + large `thinking` ⇒ budget exhausted on reasoning.**
> That is a **harness** outcome, not a model failure, and it must be recorded as `UNUSABLE AT BUDGET`, never as "the model got it
> wrong."

Practical menu, in order of preference: use a **non-reasoning** model for structured output (a local `qwen2.5-coder:14b` answered
the same kind of prompt reliably where both cloud reasoning models returned nothing); otherwise raise the budget until `done_reason`
is `stop`, or read the answer out of the thinking field deliberately. **Never score an empty `content` as an incorrect answer.**

## The rule this produces

> **Never accept a "CORRECT" without reading the prescription.** A verdict is one bit; the fix is where the model has to
> actually know something. Score the prescription, not the checkmark.

Concretely, for every audit that returns verdicts, the review question must be **"what is the corrected line?"** — and the
corrected line must be compared against the defect, not taken on trust.

*Paper only. No live orders, no credentials. Not investment advice.*
