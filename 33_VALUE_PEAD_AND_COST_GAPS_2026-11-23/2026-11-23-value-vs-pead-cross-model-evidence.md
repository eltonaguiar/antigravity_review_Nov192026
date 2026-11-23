# Value vs PEAD - cross-model evidence (2026-11-23)

Three independent surfaces, one prompt, deliberately **without** our own numbers in it (a previous
harvest returned our own statistics relabelled as findings - an "echo" - so the prompt now states only
the constraint: 12-20 bp round trip, deflated-Sharpe gate, paper only).

| Source | Value premium | PEAD | Decay claim |
|---|---|---|---|
| duck.ai / GPT-6 Luna | 3-5%/yr = **25-42 bp/month** gross; HML 1927-2024 | positive in 41/48 quarters, 1974-85 | HML lost ~half cumulative value after 2007; **Martineau: large-cap PEAD non-existent since 2006** |
| Router `ULTRA_FREE_OPENROUTER` | **0.5-0.7%/month = 50-70 bp/month** gross (Fama-French 1992/2019, Asness et al 2013) | Ball & Brown 1968; Bernard & Thomas | HML ~ -0.3%/month 2007-2020; net of 15-20 bp/mo turnover the alpha is **30-40 bp/month** |
| Router `ULTRA_FREE_CLOUD_LARGE` | (answer truncated before this section) | **20-30 bp/month** SUE1 decile spread, 1971-2005 | "post-2005 SUE spread compressed" |

## The disagreement that matters

**25-42 vs 50-70 bp/month is a factor of ~2** for the same factor. Both cannot be right about the same
portfolio. Most plausible cause: annualised HML over a 97-year sample versus a per-month quintile spread
over ~56 years. This decides whether value clears a 12-20 bp round trip comfortably or barely, so the
magnitude must be **measured on our data, not imported**.

## Where all three agree

1. **Large-cap PEAD decayed post-2005/2006.** Three models, three different citation sets, one verdict.
2. **Value is the better first test** and it is monthly - the horizon our own cost ladder says can
   survive (+24.21 bp at 1D vs -0.57 bp at 15m).
3. **Turnover costs are the binding constraint**, not signal strength.

## Pre-registered kill rule (usable as written)

After fixing portfolio, rebalance, universe and cost model **before** looking at the holdout:

> kill if OOS annualised net return **on committed capital** <= 4.3%, **or** if the one-sided 95%
> **upper confidence bound** <= 4.3% - the optimistic bound then also fails.

Count turnover costs once; do not double-subtract. Compare against **committed capital including cash
collateral**, not a raw T-bill yield - a market-neutral long-short return is not comparable to a T-bill
unless capital, leverage, collateral and financing are specified.

## Collateral treatment (Zoo Code, PR #1065)

The pre-registration must state collateral yield explicitly:

- `COLLATERAL_BASE` = **4.32%** (policy rate)
- `COLLATERAL_CONSERVATIVE` = **0%**
- If collateral earns 0%, the forgone interest is added as a **cost**, so the hurdle is not flattered.

Without that line the 4.3% hurdle is measured against a base that under-counts cash.

## Citations to verify at source (none checked against the papers yet)

Fama & French 1992 *J Finance*; Fama & French 2019 *JFE*; Asness, Moskowitz & Pedersen 2013 *J Finance*;
Ball & Brown 1968 *JAR*; Bernard & Thomas 1989 *JAR*; Ball & Bartov 1996 *JAE*; Livnat & Mendenhall 2006
*TAR*; Martineau (SSRN).
