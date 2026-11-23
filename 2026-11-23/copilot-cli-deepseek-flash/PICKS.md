# Final picks per asset class — copilot-cli-deepseek-flash

**Agent:** copilot-cli-deepseek-flash
**Generated:** 2026-11-23T02:4xZ
**Ticket size for every bp figure below:** **$25,000 USD** (matches the sibling entry, so bp are comparable)
**Verdict: 0 picks pass all five gates. This is my final answer, not a placeholder.**

Paper only. Zero capital sanctioned. Not investment advice.

---

## Why the list is empty

I will not put an entry in this table that fails the gates and call it a pick. Three
separate measured results drive the zero:

1. **Deflation.** Programme-level deflated Sharpe: **0 of 6 classes survive** at N=90.
   SR\* = 1.259–1.726 depending on which of the disputed trial counts is used
   (see `reports/TRIAL_N_RECONCILIATION_2026-11-23.md`); best observed Sharpe is ETF at 1.05
   with DSR 0.3191.
2. **Cost.** Five different equity round-trip costs are in circulation spanning
   **4.98bp → 50.00bp (10.04×)**, and four of them are verdict-grade. Production
   (`alpha_engine/backtest/engine.py:115`) runs on an **ASSUMED** 16.52bp model while the
   only *measured* model (4.98bp) has zero call sites.
3. **Beta masquerading as signal.** A paired bootstrap on `strategy − benchmark` passes a
   **1.5× index fund**, because `0.5·b` has a non-zero mean whenever `b` drifts. Any
   positive "excess return" I could show must first be beta-adjusted (Jensen's alpha).

---

## Per-class verdicts — all ten classes

| Class | Verdict | Deciding number | Pick |
|---|---|---|---|
| **EQUITY** (single name) | **DEAD** | Breakout PF **0.9917** at 25bp/side. A PF < 1 survives *any* cost reduction — signal failure, not cost failure. Value HML killed on GROSS: +0.11% gross, +0.02% net, SE 6.65%, 95%UB +10.96% vs 4.32% hurdle. | **NO PICK** |
| **ETF** | **NOT AN EDGE** | Best risk-adjusted *asset* (vol 16.2%, MDD −25.9%, SR 0.44) — but that is **beta**, not signal. Breakout margin: 4.7bp gross vs 5.1bp cost = **0.4bp**, inside the measurement error of any cost estimate. DSR 0.9543 collapses to **0.3191** at N=90. | **NO PICK** (hold cheaply, do not trade) |
| **BOND** | **NOT INVESTABLE** | Claimed 42.64bp RT with 94% fees; break-even 0bp/side, Sharpe −0.550. **UNMEASURED by me** — I did not reproduce the 42.64bp. | **NO PICK** |
| **CRYPTO** | **DEAD** | Vol 68.5%, MDD −87.8%. Carry net **3.07%** vs 4.32% hurdle across 4,235 intervals. DSR 0.0423 at N=90. Ledger also has 1,864 duplicate signal-ts groups and EXPIRED→WON mislabels. | **NO PICK** |
| **FOREX** | **CANDIDATE-CONDITIONAL** | Mean-rev gross 4.3038bp. Net **−0.68bp** at my 4.98bp cost of record, **−3.23bp** at subq's 7.53bp upper bound. Both negative but −0.68bp is inside noise, so **the sign is undetermined**. | **NO PICK** — pending one weekday London/NY spread run |
| **COMMODITY** | **DEAD** | PF **0.757 even at 0bp cost** — fails with cost set to zero, so it is cost-independent and unrecoverable. | **NO PICK** |
| **OPTIONS** | **UNMEASURED** | No measured cost, no backtest in this repo. Premium selling is short-vol beta. | **NO PICK** |
| **PREDICTION MARKETS** | **UNMEASURED** | Best calibration harness available, zero strategies measured. | **NO PICK** |
| **MEME / PENNY** | **KILLED** | 1 of 3 names quotable (rule needs 2); 0 instruments for penny. MEME cost unmeasurable (SHIB: 84.3% zero-range bars). | **NO PICK** |
| **MUTUAL FUNDS / PRIVATE CREDIT** | **FEES DOMINATE / NO DATA** | $100k over 10yr: ETF ≈ $1,050 vs active MF ≈ **$18,520** (17.6×). Private credit: no data exists. | **NO PICK** |

---

## The one thing I *will* defend — and why it is not in the picks table

**Buy-and-hold a low-cost broad-market index ETF.**

This is a **vehicle/fee decision, not an edge claim**, and putting it in `picks.json`
would be dishonest because it has no signal and would trivially fail G3. Stated cost
arithmetic on $100,000 over 10 years:

| Vehicle | 10-year cost |
|---|---:|
| Direct holdings | ≈ $50 |
| Broad index ETF | ≈ **$1,050** |
| Index mutual fund | ≈ $4,520 |
| Active mutual fund | ≈ **$18,520** |

The active fund costs **17.6× the ETF**. That is measured fee arithmetic, it is actionable,
and it is the only recommendation I will put my name to. It is beta by construction — which
is precisely why it is not a pick.

---

## UNMEASURED — declared, not hidden

| Item | State |
|---|---|
| Commission | `UNMEASURED` — needs ≥3 months of broker statements. My 4.98bp is a **lower bound** (spread only; commission/ECN/exchange fields are 0 by construction). |
| Capacity coefficient `k` | `UNMEASURED` — needs our own fills; live trading not sanctioned. |
| PIT universe survivorship | `UNMEASURED` — needs external constituent history. |
| BOND 42.64bp / 94% fees | `UNMEASURED` — cited, not reproduced by me. |
| σ_SR reconciliation | **Unresolved.** My SR\*=1.259 came from pooled σ_SR 0.031848; `deflation_programme.json` gets 1.6176@N90 from σ_sr 0.6488. Different scales — **not comparable even at equal N**. |

---

## Update rules followed

- No fabricated numbers; every figure is measured or marked `UNMEASURED`.
- Every class carries an explicit verdict and, where a number decides it, that number.
- Zero picks are reported as zero. To revise: append a `## Revision <ISO timestamp>`
  section below (old sections kept), or version the folder per the parent README.

---

## Revisions

_(none yet — this is revision 1)_
