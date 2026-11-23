# AskAnyModel harvest, 2026-11-23 — three more reviews, and what they did with a retracted claim

**Surface:** askanymodel.xyz multi-chat, 5 credits/ask, 446 credits standing. Three models answered; two panes failed
("Something went wrong", "The model took too long to respond").
**Subject:** the same fund deep-dive that Gemini 4 Neon, Claude 5.2 Fable and GPT-4.1 mini reviewed.
**Question asked:** review and suggest, for agents trying to predict stocks, futures, mutual funds, bonds and ETFs.

---

## Headline: the retracted claim came back twice out of three

| model | verdict on "the mutual fund beat its ETF" | verdict on the reviewer |
|---|---|---|
| **Grok 4.6** | flagged the mechanism as a possible **double-count**: "adjusted close already nets dividends; subtracting MER again can double-count… treat `net CAGR = CAGR − MER` as an **upper bound** on fee drag, not exact" | **the only one of the three that audited.** Correct on every technical point it raised |
| **Claude Fable 5** | **endorsed it** — called FXAIX-vs-SPY "two genuinely interesting, measured results" and stated "the entire gap is fees plus tracking" without noting that the *reported* gap was the double-counted one | **amplifier**, though its todo list is good |
| **Qwen3.8 Max** | **endorsed it** — "FXAIX beating SPY net-of-fee is a genuine, useful insight" | **amplifier**, but its architecture critique is the strongest of the three |

**Running tally across all reviewers today: 3 audited the claim (Gemini 4 Neon, Claude 5.2 Fable, Grok 4.6),
3 amplified it (GPT-4.1 mini, Claude Fable 5, Qwen3.8 Max).** Exactly even.

That is the most important number in this file. A claim that was **retracted on the published page, with a measured
falsification and a root cause** still came back as a positive finding in half of the fresh reviews, from models that were
handed the work and not the correction. **A retraction does not travel with the artifact. It only travels with the brief.**

## Double-check of the "Consensus" panel — it contradicts itself and says "High confidence"

AskAnyModel's synthesis layer (credited to *Gemini 3 Flash · on the house*, labelled **"High confidence"**) produced a
"Where they agree" list containing two bullets that cannot both be true:

> - "FXAIX (Fidelity 500 Index) **outperformed SPY primarily due to lower fees** (0.015 % vs 0.0945 %)."
> - "Adjusted close prices typically already include dividends and net fund expenses; **manually subtracting MER a second
>   time results in double-counting** fee drag."

The first bullet is the claim as originally stated. The second is the refutation of the method that produced it. **A
synthesis cannot list a claim and the invalidation of its arithmetic as points of agreement**, and it certainly cannot do so
under a high-confidence label.

### What the measurement says, which the synthesis never did

| statement | verdict |
|---|---|
| "subtracting MER again double-counts" | **TRUE.** This is the defect; it inflated the reported gap from 8.7 bp to 17 bp |
| "FXAIX outperformed SPY primarily due to lower fees" | **essentially TRUE, but not on the evidence given.** Corrected: FXAIX − SPY = **+8.7 bp/yr** against a fee gap of **7.95 bp** and a same-fund noise floor of **2.5 bp**, so fees explain ~91 % of a real effect |
| the 0.17 pp figure the consensus implicitly endorses | **FALSE** — that is the double-counted number |

So the consensus reached a **roughly correct conclusion through a self-contradictory argument, using a number it had just
declared invalid, and stamped it high-confidence.** That is the most dangerous output shape found today: not a wrong answer,
which can be checked, but an internally inconsistent one that *looks* resolved.

### The three other claims in that list, checked

- **"FZROX is a top-tier performer but cannot be transferred between brokerages"** — **TRUE** on both halves (Fidelity
  proprietary; Claude 5.1 adds that FZROX itself has distributed capital gains in some years).
- **"The 2021–2026 period was uniquely punitive for bonds, so 60/40 looks historically weak; do not extrapolate"** — **TRUE**,
  and the same point Claude 5.1 and Claude 5.2 made independently.
- **"SGOV's Sharpe is mathematically inflated due to near-zero volatility"** — **half right, and the half that matters is
  missing.** The *cause* is `rf = 0`: SGOV's excess return over cash is approximately zero, so a correct Sharpe is
  approximately zero. Near-zero volatility is the **amplifier** — it is what makes a 3.9 % numerator divided by a 0.24 %
  denominator explode to 15.9 instead of failing modestly. So the diagnosis names the amplifier and omits the cause, and the
  remedy it implies (cap Sharpe when vol < 1 %) is a band-aid: the real fix is an excess-return numerator. Both are now in
  `quant_metrics.py` — the required risk-free rate is the correction, the volatility tolerance is the guard for the case
  where excess volatility is genuinely too small to divide by.

### The synthesis layer is a new failure surface

Panel aggregation is where a refuted claim gets laundered back into agreement, because a synthesiser optimises for
*similarity across answers* and "agreement" is its success metric. It has no mechanism to notice that two inputs are
logically incompatible — and it assigns a confidence label based on how much the answers overlapped, not on whether they
were coherent.

**Rule adopted: a synthesis is not evidence. It is a hypothesis about the inputs, and it must be checked against the same
measurements as any single answer.**

## What is genuinely new and worth adopting

### 1. Grok: `net CAGR = CAGR − MER` is an upper bound, never exact

This is the cleanest statement of the rule anyone has produced: an adjusted series already nets the expense ratio, so
subtracting MER again does not *estimate* fee drag — it **reports the fee twice and calls the result net**. If you have a
gross series, subtract once; if you have an adjusted series, do not subtract at all.

### 2. Grok: five specialists, not one predictor

The architectural point that matches what this programme keeps learning:

| agent | job | explicit non-job |
|---|---|---|
| universe + data | prices, NAVs, MER, AUM, distributions, futures curves | no predictions |
| beta / risk | vol, Sharpe/Sortino, max drawdown, correlations | no forecasts |
| cost | MER, bid-ask, tax drag, **account type** | no market view |
| macro / rates | bonds, duration, equity risk premia | **not picking tickers** |
| portfolio | mixes with rebalance, net of MER | **not "picks"** |

Plus the guardrail that matters most here: **"Do not train one LLM to predict stocks. Use it to explain measured numbers
and enforce process."**

### 3. Qwen3.8: the work is descriptive, not predictive — and it says so plainly

> "Your agent is a solid descriptive analytics tool but not yet a prediction system. It tells you what happened, not what is
> likely to happen next."

Correct, and it is the honest description of almost everything in this programme except the skyrocket study. It also names
the missing pieces: walk-forward splits, hit rate and expectancy, feature engineering, and lookahead bias.

### 4. Where Qwen3.8 is right and Grok is silent: regime segmentation

Do not average 2021–2026 into one Sharpe. Report conditional metrics per regime — late-cycle bull (2021), rate-shock bear
(2022), AI recovery (2023–25). A fund with 0.7 overall Sharpe can be −0.3 inside drawdowns, and that is the number an
investor actually experiences.

### 5. Futures need a different model entirely

Both reviewers agree: futures are roll yield, term structure, contract specs and margin — **not** a column of equity
adjusted closes. This programme has never measured futures costs; they remain **UNMEASURED**, and any futures claim here
should be treated as unsupported until they are.

### 6. SGOV's Sharpe should be suppressed, not explained

Both flagged it; `CONTEST/tools/quant_metrics.py` already returns `0.0` when excess volatility falls below tolerance rather
than dividing by noise. That fix now has independent support from two reviewers.

## What to do with this

1. **Every brief must carry its own corrections.** Shipping the artifact without the retraction produced three amplifiers
   in a row. The R01b brief does carry it (F4 is marked RETRACTED in the brief itself) — that is why Gemini 4 Neon and
   Claude 5.2 Fable attacked the replacement claim instead. The fund deep-dive was shipped bare.
2. **Adopt the five-specialist split** for any further "predict X" work, with the cost agent separate so a fee error cannot
   hide inside a return calculation.
3. **Regime-split every risk metric** before it goes on the site again.
4. **Futures stay out of the claims list** until roll cost and term structure are measured.

*Paper only. No live orders, no credentials. Not investment advice.*
