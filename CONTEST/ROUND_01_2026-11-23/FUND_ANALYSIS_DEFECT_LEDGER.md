# Fund-analysis defect ledger — every defect raised, who found it, status

Seven reviewers saw this work. This is the single table that replaces five sprawling documents. **Status** is honest:
`FIXED` means code or text changed and was verified; `RECORDED` means it is written down but not yet implemented; `GAP` means
still missing. Nothing here is marked fixed because someone said so.

**Tally of reviewers on the retracted claim: 7 audited it, 4 amplified it** (11 reviewers total, five surfaces).

**The decisive measurement nobody proposed but GLM 5.3 pointed at: VTSAX and VTI are share classes of ONE fund, so their
measured difference is the noise floor for any vehicle comparison.** Over the aligned window they differ by **−2.5 bp/yr**
(12.2820 % vs 12.3073 %), Sharpe difference **−0.0005, CI [−0.0127, +0.0119]**. Set against that floor:

- **FXAIX − SPY = +8.7 bp/yr = 3.5× the noise floor**, and the fee gap is 7.95 bp — so on **CAGR the fee effect is real and
  measurable**, not noise.
- On **Sharpe** every pairwise difference remains indistinguishable (all CIs span zero), because Sharpe differences are far
  noisier than return differences.
- And **VOO beats FXAIX**, so the winner is the **cheapest share class**, not the wrapper.

That is the sharper version of the answer: *the fee gap is real and measurable at ~8 bp/yr; the wrapper is irrelevant; buy
the cheapest vehicle.*

---

## Measurement defects

| # | defect | found by | status |
|---|---|---|---|
| 1 | **Expense ratio subtracted twice** — an adjusted series is already net of MER, so `net_cagr = cagr − mer` reports the fee twice. Reproduced the retracted 17 bp to 0.4 bp | Gemini 4 Neon, Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6 · *amplified by* GPT-4.1 mini (called it a "strength"), Claude Fable 5, Qwen3.8 Max | **FIXED** — claim retracted, root cause measured, `quant_metrics.cagr()` now keyword-only so a fee cannot be passed positionally (test raises `TypeError`) |
| 2 | **Sharpe with rf = 0** — that is why a T-bill fund showed 15.886; every equity Sharpe was inflated ~0.19 | Gemini 4 Neon, Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6, Qwen3.8 Max | **FIXED** — `quant_metrics.sharpe()` requires an explicit rf and returns `0.0` below a volatility tolerance; published sharpes corrected to VOO 0.645 / IVV 0.642 / FXAIX 0.641 / VFIAX 0.639 / SPY 0.632 |
| 3 | **Sortino downside deviation divided by `len(downside)`** instead of total n, and measured against 0 rather than a target. Symptom: Sortino *below* Sharpe | Gemini 4 Neon, Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6 | **FIXED** — `quant_metrics.sortino()` uses all observations against an explicit target; FXAIX 0.812 → 0.921 |
| 4 | **`rebal=21` accepted, documented, never used** — so "monthly rebalance" was costless daily rebalancing | Gemini 4 Neon, Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6 | **FIXED** — `quant_metrics.rebalance()` drifts weights, resets on schedule, charges turnover cost; 3 tests pin it |
| 5 | **SPY is a strawman comparator** — most expensive S&P 500 ETF, and a unit investment trust that cannot reinvest dividends internally (cash drag) and does not lend securities | Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6 | **FIXED** — five-vehicle test substituted VOO/IVV, which produced the result that killed the claim |
| 6 | **A 0.014 Sharpe difference is noise** — SE(SR) ≈ √((1 + ½·SR²)/T) ≈ **0.5** over five years | Claude 5.2 Fable (~0.45), Claude 5.1 Fable (~0.5) | **FIXED and strengthened.** `quant_metrics.block_bootstrap_sharpe_diff()` (block=21, B=2000) now returns a paired interval. Measured: FXAIX−SPY **+0.008 [−0.004, +0.024]**, VOO−SPY **+0.013 [−0.001, +0.028]**, VOO−FXAIX **+0.005 [−0.008, +0.013]**, IVV−FXAIX **+0.001 [−0.010, +0.011]**, VFIAX−FXAIX **−0.002 [−0.013, +0.009]** — **all indistinguishable**, widest interval **0.030 Sharpe units**. Note the reviewers' SE≈0.5 is the error on each Sharpe *level*; because these vehicles are ~0.998 correlated the *difference* is far tighter, so the honest statement is not "we cannot tell" but "the difference is bounded to ±0.01–0.03" — they are the same instrument with different fees |
| 7 | **FZROX vs VTI is not a fee story** — 0.03 pp fee gap but ~0.21 pp return gap, because they track different indexes (Fidelity Total Investable Market vs CRSP Total Market) | Claude 5.2 Fable, Claude 5.1 Fable | **RECORDED** |
| 8 | **FZROX has distributed capital gains in some years** — the reverse of what the analysis implied — *and* it cannot be transferred in kind, so leaving Fidelity forces a taxable sale | Claude 5.1 Fable | **RECORDED** — must appear in any recommendation |
| 9 | **The VTSAX-vs-VTI tax claim was backwards** — they are share classes of one fund and Vanguard's dual-class structure flushes gains through the ETF class; VTSAX has not distributed capital gains in roughly 20 years | Claude 5.2 Fable, Claude 5.1 Fable | **FIXED (text)** — I had adopted this as a "real gap" and corrected my own adoption |
| 10 | **Fee-drag-in-dollars formula ignores balance growth** — `100000*(1-(1-mer)^n)` is wrong once the balance compounds | Claude 5.1 Fable | **RECORDED** — cited in dollars to a user, so it matters |
| 11 | **Listwise row deletion** when any fund is missing turns a multi-day gap into a 1-day return and misstates vol when annualised at 252 | Claude 5.1 Fable | **GAP** — my own vehicle test aligns on the intersection of dates, which avoids the gap issue, but the panel/skyrocket scripts do not check for gaps |
| 12 | **SGOV's Sharpe should be suppressed, not explained** | all seven | **FIXED** — tolerance guard in `quant_metrics`; two reviewers independently endorsed the approach |
| 13 | **"The verification script verifies nothing"** — it printed pre-written conclusions beside numbers read from JSON. Assertion dressed as verification | Claude 5.2 Fable | **RECORDED** — the most dangerous defect of the set; the reason `verify_ledger.py` recomputes hashes rather than trusting a recorded value |

## Analytical and framing defects

| # | defect | found by | status |
|---|---|---|---|
| 14 | **Five years is one interest-rate regime.** 2022 was the worst bond year in modern history, so BND's −0.29 % and 60/40's weaker Sharpe are **regime-specific**; over long histories 60/40 has a *higher* Sharpe than 100 % equity | Claude 5.2 Fable, Claude 5.1 Fable, Grok 4.6, Qwen3.8 Max | **RECORDED** — regime split still not implemented anywhere |
| 15 | **Recommending 100 % SPY on trailing Sharpe is performance-chasing** — the exact behaviour a disciplined agent should warn against | Claude 5.1 Fable | **RECORDED** |
| 16 | **Bonds should be judged on starting yield / SEC yield, not trailing five-year return** — current yield is the best single predictor of forward bond return | Claude 5.1 Fable, Claude 5.2 Fable | **GAP** — no SEC yield pulled |
| 17 | **No real (inflation-adjusted) returns**, and inflation ran hot in-sample | Claude 5.1 Fable, Claude 5.2 Fable | **GAP** |
| 18 | **No international sleeve** (VXUS / VTIAX) — the comparison set is US-only | Claude 5.1 Fable, Claude 5.2 Fable | **GAP** |
| 19 | **Mutual funds reinvest distributions at NAV while ETFs reinvest at the ex-date price** — a real mechanism behind small FXAIX/SPY differences | Claude 5.1 Fable | **RECORDED** |
| 20 | **JURISDICTION ERROR.** The operator is Canadian; FXAIX / FZROX / VTSAX generally cannot be bought without a Canadian prospectus. Everything practical in the analysis was unactionable as written | **Claude 5.2 Fable** (nobody else noticed) | **FIXED** — red callout at the top of the site's answer section; Canadian equivalents flagged *to confirm with a broker* |

## Process defects

| # | defect | found by | status |
|---|---|---|---|
| 21 | **Wildcard `bash` auto-approval on an agent that writes and runs code** | Claude 5.2 Fable, Claude 5.1 Fable | **RECORDED** — must be narrowed before any brokerage API exists |
| 22 | **Scope creep** — a session titled "Review COMS messaging skill" produced a fund-selection analysis | Claude 5.2 Fable, Claude 5.1 Fable | **RECORDED** |
| 23 | **"Create a set of todos" ≠ "execute them"** | Claude 5.2 Fable, Claude 5.1 Fable | **RECORDED** |
| 24 | **Truncated output** — the final print was cut mid-line and the heredoc's stdout was treated as the record | Claude 5.1 Fable | **RECORDED** |
| 25 | **Repetitive internal monologue**, "Let me do it" ×3; $1.19 / 59 % context | Claude 5.2 Fable, Claude 5.1 Fable | **RECORDED** |
| 26 | **`datetime.UTC` needs Python ≥ 3.11** | Claude 5.1 Fable | **NOTE ONLY** — this host runs 3.14 |

---

## Reviewers who were themselves wrong — because a reviewer's corrections need auditing too

The rule that a review's *caveats* need checking (learned when I wrongly adopted the capital-gains point) applies to its
*corrections* as well. Two cases:

| reviewer claim | check | result |
|---|---|---|
| **GLM 5.3 Flash**: "Verify the SGOV MER. The script hardcodes 0.09 %; SGOV is commonly listed at ~0.05 %." | iShares prospectus **filed 2026-06-18** and multiple fee trackers as of **November 2026** both state **0.09 %** | **the reviewer was wrong; the hardcode was right.** GLM 5.3 was the best of the four models in that harvest and still produced a confident, specific, wrong correction |
| **Qwen3.6 Flash**: "Date range includes 2026-11-13 — likely synthetic/projected data… introduces severe look-ahead bias and invalidates all metrics" | the current date on this host is 2026-11-23; 2026-11-13 is **ten days in the past** | **false alarm**, raised with a red "High" priority flag. It also listed *"Fee-NET Returns: explicitly subtracting MER before reporting CAGR/Sharpe is **institutional-grade practice**"* as the agent's **strength #1** — praising the exact double-count that four other models had already falsified |

**Qwen3.6 Flash is therefore the cleanest example of the amplifier pattern yet**: the double-count promoted to a headline
strength, plus an invented data-integrity alarm, delivered with the same confident formatting as a real audit. It gave one
genuinely useful suggestion (factor overlays and regime splits) buried under both errors.

## What every one of the eleven agreed on

**The direction was right and the arithmetic was wrong.** Not one reviewer disputed that a cheap broad index fund is the
correct instrument for a passive investor. Every one of them disputed a number used to prove it — and the numbers were what
carried the recommendation.

> Claude 5.1 Fable's single sentence is the whole finding: *"With these three changes the headline 'FXAIX beat SPY' becomes
> 'FXAIX and SPY are statistically indistinguishable; the ~0.08 pp/yr fee gap is real but small, and VOO/IVV close it
> entirely.'"*

That is the same conclusion my own five-vehicle measurement reached from the opposite direction, and it is what the page now
says.

## The three things worth doing next, in order

1. **Bootstrap confidence intervals on every pairwise comparison** — with `SE(SR) ≈ 0.5` on five years, most of what this
   programme has quoted as a ranking is not one. Two reviewers supplied the code; nothing yet uses it.
2. **Regime-split every risk metric** — 2022 alone vs 2023-25, and label anything driven by a single year.
3. **Pull SEC yield for the bond sleeve** and stop extrapolating a rate shock into an allocation recommendation.

*Paper only. No live orders, no credentials. Educational analysis, not individualized advice; jurisdiction items flagged for
broker confirmation.*
