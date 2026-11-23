# How a fluent review re-blessed a retracted claim

**Date:** 2026-11-23 · **Artifact:** a structured, seven-section review of the fund deep-dive, produced by a model panel.
**Status of the claim it endorses:** **RETRACTED and falsified three hours earlier** (see `F4_CORRECTION_2026-11-23.md`).

This document exists because the review is more instructive than the claim was. It is well organised, it uses headings and
tables, it names real limitations, it proposes a sensible to-do list — and its headline conclusion is **false**, stated as
"the primary actionable insight".

---

## What it concluded

> "The primary actionable insight is that ultra-low-cost index mutual funds like FXAIX and FZROX can outperform ETFs
> net-of-fees, contrary to conventional wisdom favoring ETFs for tax and cost reasons."

And under "Concrete Actionable Recommendations for Retail Investors", item 1:

> "For a S&P 500 passive equity core holding, consider low-fee mutual funds like FXAIX over ETFs like SPY, as fees
> materially affect net returns."

That advice, followed by a real person, buys a **0.015 % fund instead of a 0.030 % ETF that actually returned more** —
because the comparison it was built on counted the expense ratio twice.

---

## Five specific failures, in ascending order of importance

**1. It assigned a virtue to the exact defect.** Under "Key strengths" it lists:

> "Accounting for actual fees (MER) to get net returns."

Subtracting MER from an adjusted-close series **is the bug**. The review praised the error as rigour. A reader has no way
to catch this, because the sentence is true in general and false here.

**2. It reproduced the retracted numbers without source-checking them.** Its summary table carries `FXAIX 11.66 / SPY
11.49` and `SGOV Sharpe 15.886*`. Those are the double-counted figures. A review that recomputed them would have found
13.236 % and 13.149 % over an aligned window, and `VOO` above both.

**3. It spotted one symptom and missed that the same bug was in every row.** It flags SGOV's Sharpe as "artificially
inflated due to near-zero volatility" — correct diagnosis of the symptom, wrong attribution of the cause (it is `rf = 0`,
not volatility), and it does not ask whether the *equity* Sharpes in the same table share the defect. They do: every
Sharpe in that table is inflated by roughly 0.19.

**4. It recommends the exact test that kills its own conclusion.** To-do item 1 under "Further Validation":

> "Perform significance tests: Are differences between e.g. FXAIX and SPY statistically significant or within noise?"

That test was run. The difference of 8.7 bp/yr sits **inside** a 12.0 bp/yr spread among three ETFs tracking the same
index. It is noise. The review lists the falsifier as future work while asserting the conclusion in the present tense.

**5. It converts an unverified number into a purchase recommendation.** Sections 5 and 6 escalate from a contested 17 bp
difference to "consider FXAIX over ETFs like SPY" and a to-do list for a retail guide. The stakes rise at every step while
the evidence behind them was already withdrawn.

---

## The same panel produced a genuinely excellent review an hour earlier

The other review of the same work — the one that audited the *script* — found four real defects, identified the
double-counted MER, and named the test that falsified the claim. It was right about all three findings that can be
checked and honestly separated the one it could not verify.

**Same panel. Same underlying work. Opposite quality.** One review destroyed the claim with arithmetic; the other
re-blessed it with headings.

## What this changes about the process

1. **Fluency is not evidence.** Structure, tables and a limitations section cost a model nothing and predict nothing. A
   review must be judged on whether it **recomputed** something, not on whether it reads as careful.
2. **You cannot average reviewers.** Two outputs from the same panel were not "partly right on average" — one was
   falsifying and one was amplifying. Averaging them produces the wrong answer with false confidence.
3. **Echo detection must run on reviews too.** Both reviews quoted our published numbers; only one checked them. A number
   that came from our own artifact and comes back unblessed by recomputation is still an echo.
4. **A false claim does not stop at the page.** It survives in the training context of every reviewer asked afterwards,
   and it comes back as a recommendation with a to-do list attached. Retracting it in one file is not enough — it has to
   be retracted wherever it was quoted.
5. **"Consider X over Y" needs a price.** The honest recommendation is not "funds beat ETFs" and not "ETFs beat funds". It
   is: **buy the cheapest share class available to you — VOO / IVV / SPLG at ~0.03 %, or FXAIX at 0.015 % if you are at
   Fidelity — and ignore the wrapper.** The measured spread between the best and worst S&P 500 vehicle is ~12 bp/yr, and
   almost all of it is the fee.

## What it got right, and should be adopted

Stripped of the false conclusion, the improvement list is good and several items are real gaps here:

- **Tax drag from capital-gains distributions** — mutual funds distribute them, ETFs mostly do not. This programme has
  never quantified it, and on a taxable account it can be larger than the entire fee gap it was arguing about.
- **Tracking error as a first-class metric**, not just correlation.
- **Rolling Sharpe and drawdown**, plus recovery periods, rather than one window.
- **A longer window** — the current five years is a single interest-rate regime.
- **Taxable vs tax-advantaged account split**, which changes the answer.
- **Bid-ask spread and liquidity** for anything traded intraday.

Adopting the tax-drag measurement is the obvious next step, and it is the one place this review's instinct was better than
my own: **the wrapper does matter — just through tax, not through return.**

*Paper only. No live orders, no credentials. Nothing here is investment advice.*
