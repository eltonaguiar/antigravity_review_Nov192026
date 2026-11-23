# Triage of three independent reviews of the same work — and the one finding that invalidates the advice

Three models reviewed the fund deep-dive without seeing each other. Same input, three outputs, and they were not
equivalent. This file records which reviewer did what, what converged, and the single point that changes the practical
recommendation outright.

| reviewer | credits | verdict on the work | verdict on the reviewer |
|---|---|---|---|
| **Gemini 4 Neon** (Google AI) | 110,052 | found 4 defects, reproduced the retracted 17 bp to 0.4 bp | **audit** — the one that killed the claim |
| **Claude 5.2 Fable** (AWS Bedrock) | 1,029,415 | same 4 defects plus 6 findings nobody else raised | **best of the three.** Corrected *both* the claim and my adoption of a bad caveat |
| **GPT-4.1 mini** (OpenAI) | 14,720 | endorsed the retracted claim, called the double-count a "strength" | **amplifier** — fluent, structured, wrong |

---

## What all three converged on, and my own arithmetic confirms

**The expense ratio was subtracted twice.** Claude 5.2 supplied the cleanest proof of the three:

> the raw FXAIX–SPY gap is 11.67 − 11.59 = 0.08 pp/yr, almost exactly the 0.0795 % fee gap — so the "net" figure of 0.17 pp
> counts the fee twice.

That is the same conclusion my own aligned measurement reached from the other direction: raw 8.7 bp vs fee gap 7.95 bp,
double-counted prediction 16.6 bp, retracted claim 17.0 bp. **Two independent routes, established by different methods.**
The `rf = 0` Sharpe, the Sortino denominator and the unused `rebal=21` were each confirmed by both models.

## Six findings only Claude 5.2 raised, and I am adopting all of them

### 1. The advice is US-only, and the operator is Canadian — **this invalidates the recommendation**

Claude inferred jurisdiction from two things I never noticed: the repo path references **Toronto**, and the analysis uses
the term **"MER"**, which is Canadian usage. On that basis:

> FXAIX, FZROX and VTSAX **generally cannot be purchased by Canadian residents** — US mutual funds are typically not
> sold without a Canadian prospectus.

Everything this programme has said about "buy the cheapest share class — FXAIX at Fidelity" is therefore **unactionable
for the person it was written for.** The equivalent question in Canada involves:

- **Canadian-listed index ETFs**: VFV, XUU, ZSP (S&P 500), XEQT / VEQT (all-equity asset allocation), VUN (US total market)
- **Registered accounts**: TFSA vs RRSP placement changes the after-tax answer
- **US dividend withholding tax**: 15 % withheld by default; **US-listed ETFs held in an RRSP are exempt under the treaty —
  which a TFSA is not**
- **Currency conversion cost**, which for a retail investor can exceed the entire fee difference being argued about

I have not verified each product's availability or the exact withholding mechanics against a specific broker, so those
lines are flagged **to confirm before acting**, not asserted. What is certain is the category error: **a fee-gap argument
conducted entirely in US mutual funds, delivered to a Canadian investor.**

### 2. FZROX vs VTI is not a fee story at all

The fee gap is 0.03 pp but the measured return gap is ~0.21 pp. They track **different indexes** — Fidelity's proprietary
Total Investable Market index versus CRSP's Total Market index — so most of that gap is index construction, not cost. FZROX
is also non-portable: it can only be held at Fidelity, and moving means liquidating in a taxable account.

### 3. SPY's structure explains part of the FXAIX–SPY gap

SPY is a **unit investment trust**: it cannot reinvest dividends internally, so it carries cash drag, and it does not lend
securities. So FXAIX-versus-SPY was never a clean fee comparison. Against **VOO / IVV / SPLG (0.02–0.03 %)** the gap shrinks
to roughly nothing — which is exactly what my own five-vehicle measurement found when VOO came out ahead of both funds.

### 4. "The verification script verifies nothing"

The second script was supposed to compute correlation and tracking error and instead **printed pre-written conclusions
next to numbers it read from the JSON**. This is the most dangerous defect of the set, because a verification step that
asserts rather than derives converts an unchecked number into a checked-looking one. It is also the reason to keep
`verify_ledger.py` recomputing hashes rather than trusting a recorded value.

### 5. A five-year Sharpe has a standard error of roughly 0.45

So **0.728 vs 0.714 is noise**, stated quantitatively rather than hand-waved. Only same-index pairs can be compared
tightly, and even then only within their spread.

### 6. Process: the analysis was under-governed

- **A wildcard bash auto-approval rule on an agent that writes and runs code** — restrict to read/analysis commands.
- **Scope creep**: asked to create todos, it created them *and* executed them. Decide "plan then wait" versus "plan and go".
- **Repetitive reasoning** restating the plan three or four times — wasted tokens.
- **No tests**; a single synthetic Sharpe test and a "Sortino ≥ Sharpe for symmetric returns" check would have caught two
  of the four bugs.
- Bare `except`, hard-coded paths, `tail -20` truncating output.

## What changes as a result

1. **No "what to buy" output ships until jurisdiction is settled.** The current recommendation is US-vehicle-only and the
   operator is in Canada. This is not a caveat to footnote; it is a category error to fix.
2. **The claim recorded in F4 stands retracted**, now with two independent confirmations of the mechanism.
3. **The tax-drag point I was ready to adopt was itself wrong** (`REVIEW_AMPLIFICATION_2026-11-23.md` corrected): VTSAX and
   VTI are share classes of one fund and VTSAX has not distributed capital gains in ~20 years. A review's *caveats* need
   auditing as much as its conclusions.
4. **The reviewer ranking is now evidence-based**: Claude 5.2 Fable first (corrected the claim *and* my adaptation),
   Gemini 4 Neon second (killed the claim), Grok 4.6 third (audited independently, cleanest statement of the fee rule),
   then the amplifiers: GPT-4.1 mini, Claude Fable 5, Qwen3.8 Max. Cost was not a reliable proxy — the cheapest was
   worst, the middle-cost one was best.
5. **A third harvest made the pattern explicit: the retracted claim came back in 2 of 3 fresh reviews.** Across every
   reviewer asked today the tally is **3 audited, 3 amplified** — an even split, from models handed the work without the
   correction. See `ASKANYMODEL_HARVEST_2026-11-23.md`. **A retraction does not travel with the artifact; it only travels
   with the brief.** The R01b brief carried F4 marked RETRACTED, which is why its reviewers attacked the replacement claim
   instead of repeating the original. The fund deep-dive was shipped bare.

*Educational analysis only. Paper only. No live orders, no credentials. Not individualized investment advice, and the
jurisdiction-specific items above are flagged for confirmation with a broker before anything is acted on.*
