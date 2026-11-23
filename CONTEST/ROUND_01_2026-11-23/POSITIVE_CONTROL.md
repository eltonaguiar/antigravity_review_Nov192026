# Positive control — does the gate recover a KNOWN alpha?

**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/positive_control.py` · every number below is printed by that script.
**Data:** real SPY monthly adjusted close (Yahoo, same source as `dca_vs_lumpsum.py`): **406 months, 33.8 years, annualised
vol 14.77%.** We **demean** the real returns (so the 0% case is a true null, mean ≈ 0) while keeping the real dispersion and
tails, then inject α/12 per month. Gate is **identical to `POWER_ANALYSIS.md`**: `SE = vol/√T`, `t = mean/SE`, significant
iff `|t| ≥ 2`.

| injected α/yr | recovered α/yr | vol | SE | t | 95% CI | significant? | reading |
|---:|---:|---:|---:|---:|---|---|---|
| **0.00%** | **0.00%** | 14.8% | 2.54% | **0.00** | [−4.98, +4.98] | **No** | **null honoured — reports nothing** |
| 1.00% | **1.00%** | 14.8% | 2.54% | 0.39 | [−3.98, +5.98] | No | below MDE — invisible |
| 2.00% | **2.00%** | 14.8% | 2.54% | 0.79 | [−2.98, +6.98] | No | below MDE — invisible |
| 3.00% | **3.00%** | 14.8% | 2.54% | 1.18 | [−1.98, +7.98] | No | **real 3%/yr, still invisible over 33.8y** |
| **10.00%** | **10.00%** | 14.8% | 2.54% | **3.94** | [+5.02, +14.98] | **Yes** | **harness works above MDE** |

**Minimum detectable effect at this sample length: t=2 → MDE = 5.08%/yr.**

## What this proves (one paragraph)
The harness is **correct and unbiased**: it recovers every injected alpha at the *exact* magnitude (0→0, 1→1, 2→2, 3→3,
10→10), the **0% null reports nothing** (t = 0.00), and a large **10%/yr effect is correctly flagged significant** (t = 3.94)
— so the gate is not simply broken, and it does not manufacture false positives. But on **real SPY volatility (14.8%) over
even 33.8 years**, the minimum detectable effect is **5.08%/yr**, so injected **1%, 2% and 3%/yr are all statistically
invisible**. That is the whole point of `POWER_ANALYSIS.md` made concrete on the audit's own data: **a "strategy X failed"
verdict from a few-year sample is a statement about the gate's power, not about the market** — a genuine 3%/yr premium would
need roughly **44 years at 10% vol and ~100 years at 15% vol** to reach t = 2. Any future edge claim must therefore state the
MDE its sample can actually resolve; below that, "no effect found" is uninformative.
