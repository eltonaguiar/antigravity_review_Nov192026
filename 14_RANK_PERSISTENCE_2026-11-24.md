# Rank persistence across the 123 portfolios — the skill question, answered

**Ran 2026-11-24 ~19:05 EST.** Source: `PF_NAV_SNAPSHOT`, 14,839 rows, 2026-05-29 → 2026-11-24, 126
distinct dates. Read-only. Script: `rank_persistence.py` (method frozen before the run).

## The question

The portfolio engine's best performer returned **+7.58%** while SPY returned **−4.52%**. With 123
portfolios and no prior about skill, that single best result is indistinguishable from one lucky draw. The
test that separates them needs no new data: **rank every portfolio in the first half of the window, then
measure the second half.** If rank carries information, the engine has skill. If it does not, the leader
was variance.

## Method, fixed before running

- Split the window at the median snapshot date: **2026-08-28** (equal calendar halves).
- Return per portfolio per half, from first and last NAV in each half.
- Excluded: portfolios with **< 8 snapshots** in either half, and any starting a half with **NAV ≤ 0**
  (a ruined portfolio cannot be ranked — including it would make rank correlation meaningless).
- **Spearman rho** between half-one and half-two returns, with a **5,000-draw permutation p-value**.
- Top-quartile vs bottom-quartile mean second-half return.
- Every figure also expressed against **cash (~+2.2%** over the full window, the benchmark that actually
  matters in a down tape).

**n = 122** portfolios ranked in both halves (1 excluded).

## The result

| Statistic | Value |
|---|---:|
| **Spearman rho (H1 → H2)** | **−0.0199** |
| **Permutation p** | **0.8392** |
| n | 122 |
| Top-quartile H1 → mean H2 return | **−4.51%** |
| Bottom-quartile H1 → mean H2 return | **−9.48%** |
| Top-minus-bottom spread | +4.97 pp |
| All-portfolio H2 mean vs cash | **−5.98 pp** |
| Top-quartile H2 mean vs cash | **−6.71 pp** |

**rho is −0.02 with p = 0.84.** There is no rank information in half a year of NAV. The
top-minus-bottom spread of +4.97 pp is directionally right and statistically worthless — it is what a
no-information ordering produces when the whole cohort is falling.

## What happened to the leaders

The five best first-half portfolios, and their second half:

| Portfolio | H1 | H2 |
|---|---:|---:|
| pf36 | +8.07% | **−23.64%** |
| pf6 | +6.37% | −4.12% |
| pf99 | +5.93% | −3.19% |
| pf63 | +4.46% | −9.40% |
| pf57 | +3.90% | **−24.24%** |

Every one of them gave it back. The best first-half performer lost **23.6 percentage points** in the
second half. The bottom five were similarly uninformative: pf15 fell a further **−105.57%** (it is the
portfolio that ends at negative NAV), while pf45, the fourth-worst in H1 at **−77.22%**, returned
**+3.56%** in H2.

## What this settles, and what it does not

**Settles:** the portfolio engine has **no demonstrable stock-selection skill**. The +7.58% is variance.
Rank-based thinking — "find the best model and follow it" — has no support in this data, and neither does
"the ensemble is smart".

**Does not overturn:** the earlier finding that the *median* portfolio beat SPY by 4.0 pp. That is a
**level** result and it stands. But combined with rho ≈ 0, its interpretation is now pinned down: the
outperformance came from **where the portfolios were exposed**, not from which portfolio was good. In a
tape where QQQ fell 11.8% and GLD fell 20.2%, holding bonds and cash produced relative gains without any
skill being present. The rank test is precisely what distinguishes those two explanations, and it chose
exposure.

**Does not mean:** that no strategy in the database makes money. It means **these 123 portfolios, ranked
against each other, carry no forward information** — which is a statement about model quality, not about
the universe.

## The uncomfortable summary line

> Half a year of live NAV, 122 portfolios, and the ordering is noise. The engine's best result was luck,
> its median beat equities because it was defensively positioned, and it lost to cash anyway.

That is a clean negative, and it is the first **powered** negative in either programme: n=122, a fixed
split, a permutation test, and an effect indistinguishable from zero with p=0.84. It is worth more than
the provisional nulls that came before it, because those were nulls of sample size and this is a null of
information.

## next_probe

1. **Condition on exposure.** Regress H2 return on H1 return *plus* H1 average gross exposure and the
   bond share. If exposure absorbs the 4.97 pp spread, that is the end of the "skill" question and the
   engine should be judged as a beta-management tool.
2. **Test the one cohort that never fell** — conservative portfolios (median −0.07% overall vs cash
   +2.2%). If conservative *also* fails rank persistence, no cohort has skill and the model-comparison
   exercise can be closed in favour of a fixed allocation.
3. **Fix the negative-NAV defect first.** pf15 at −105.57% and pf54 at −156.65% mean the engine keeps
   sizing after ruin; every rank statistic is contaminated by portfolios that should have stopped trading.
