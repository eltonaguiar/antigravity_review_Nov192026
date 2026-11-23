# REVIEW BRIEF — R01b findings, for adversarial review

**What this is:** six findings from a paper-trading contest and a strategy-validation programme, put to independent
reviewers for exactly one job: say which are solid, which are overstated, what would falsify each, and what single
measurement is missing. Do not summarise them back. Do not praise them. Attack them.

**Standing facts:** everything is paper-only, $1,000 notional per entrant, zero real capital, no live orders, no
credentials. Nothing here is investment advice. 0 of 18 entrants are endorsed.

---

## F1 — Price recall, not forecasting, is what the field fails first

69 picks across 18 AI entrants were scored against live prices using each pick's own bracket. **41 were void at the
fill** — the bracket had already been passed before a bar printed. The cleanest version of the test is SPY, the most
liquid ETF in the world, live at **689.81**: five sets quoted targets between **541 and 715** in the same week, a
174-point spread. Only one straddled reality.

## F2 — A bracket thinner than the round-trip cost

One entrant went long EURUSD with a target 6.4 bp from the live price, facing a 7.53 bp round-trip cost. The pick is
INSIDE its bracket and still loses by construction if it wins. Claim: such a pick is not a trade and must not score as
neutral.

## F3 — A bracket that cannot resolve, and the mean-R exploit

One entrant went long gold with a bracket 54% wide at R ≈ 0.37. It can neither win nor lose; it books ≈0 R. **Clam:
under a mean-R metric, zero silently beats a field that is mostly negative**, so an unreachable bracket is a scoring
exploit rather than a strategy. A second entrant reached the same exploit by a different route (0–3 month T-bill ETFs
whose bracket cannot be reached in 72 hours).

## F4 — RETRACTED BY THIS REVIEW: "an index mutual fund beating its own ETF"

Originally claimed on two independent measurements (11.66% vs 11.49% and 11.67% vs 11.59%, corr 0.998) over a ~5-year
window. A reviewer objected that a gap of that size cannot be the fee gap alone, and named the settling test: compare the
fund-vs-ETF difference against the spread **across several ETFs tracking the same index**.

That test was run. Aligned window 2020-11-23 → 2026-11-20, 1,506 sessions, total return: **VOO 13.269%, IVV 13.245%,
FXAIX 13.236%, VFIAX 13.201%, SPY 13.149%**. An ETF (VOO) beat both mutual funds. Best fund minus SPY is **+8.7 bp/yr**
against a predicted fee gap of **7.95 bp/yr** (~91% explained), but the spread among three ETFs is **12.0 bp/yr**, larger
than the whole fund-vs-ETF gap. The original claim is **withdrawn**. What survives: **fee drag is real and worth ~8 bp/yr;
wrapper type is not the edge, expense ratio is.** Full working in `F4_CORRECTION_2026-11-23.md`.

**Reviewers: F4 is therefore no longer something to rule on — it is an example of what this review process catches. If
you think the replacement claim is also wrong, attack that.**

## F5 — "0 of 362 candidate cells pass the alpha gate" is a power statement, not proof of zero alpha

A programme rejected 100% of 362 candidate strategy cells. Re-analysis says the gate is sound but **underpowered** at the
alpha magnitudes present: roughly **126 closed trades** are needed to resolve a 0.5% per-trade alpha at 80% power, and
about **784** for 0.2%. Observed n in the relevant bucket was ~34. Claim: "zero alpha exists here" is not supported;
"we cannot detect alpha this small with this data" is.

## F6 — The contest measures rule-understanding, not trading skill

One entrant optimised the published scoring function itself rather than the market — explicitly designing picks to pad
the net-positive count and to survive the same-bar tie-break. Claim: as written, the contest's leaderboard ranks
comprehension of the rules, so round 2 must randomise the bar-resolution rule, the cost band, and the tie-breaks.

---

# WHAT I WANT BACK

For **each** of F1–F6, in a compact block:

```
F<n>: SOLID | OVERSTATED | WRONG | UNVERIFIABLE
why (<= 2 sentences)
falsifier: the specific observation that would kill it
```

Then, once, at the end:

1. **The single most important missing measurement** across all six, and the cheapest way to obtain it.
2. **Which finding, if true, matters most for someone with real money** — and which is merely interesting.
3. **One thing in this brief that is probably wrong and that the author cannot see from inside his own data.**
