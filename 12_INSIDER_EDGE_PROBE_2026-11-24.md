# INSIDER-P: the first probe with enough events to detect a real edge

**Status:** design frozen below before any return is computed. Nothing in this file is a result.

## Why this probe exists

Every prior test in this estate died of the same disease, and it was not a weak signal — it was
**sample size**. Measured today:

| Test | Events | Firms clearing the 750 floor |
|---|---:|---:|
| Analyst ratings, `up`/`down`/`init`, 308 tickers | 28 / 18 / 11 firms at 300/500/750 | 11 |
| Analyst ratings, **up-only + 182-day clean window** | **8,498** | **0** (best: BofA, 439) |

The defensible definition — the one six models converged on — is **not measurable at the current ticker
count**. At 8,498 events across 220 firms, no firm reaches even 500, so every firm-level conclusion is
underpowered by construction. Reporting "no edge" there is reporting the sample, not the market.

**Insider filings have the events analyst ratings never will.** Measured from SEC EDGAR for one issuer
(Apple, CIK 0000320193): **598 Form 4 filings** in the recent window alone, out of 1,005 total filings.
Parsed cleanly, keyless, with every field needed:

```
issuer: Apple Inc. | owner: Newstead Jennifer | title: SVP, GC and Government Affairs
officer: true | director: false | date: 2026-11-17 | code: S | shares: 2,398 | price: 352.77
```

That is the unlock: a free, complete, structured, point-in-time feed of voluntary insider decisions,
scaling to tens of thousands of events per year across a few hundred tickers.

## The hypothesis, stated so it can die

**Insiders buy when they know something the market has not yet priced, so open-market purchases predict
positive abnormal returns; sales do not, because sales are driven by liquidity, diversification and tax.**

- Purchases are **voluntary and costly** to the buyer — they concentrate information.
- Sales are **asymmetric in motive** — option exercise, diversification, house purchase, tax.
- This asymmetry is the standard finding (Lakonishok & Lee; Jeng et al.), and it is the reason a
  purchase-only signal is worth testing and a sale signal is a **control, not a strategy**.

The probe fails if purchases are indistinguishable from a matched control, or if purchases and sales
behave the same way (which would mean the feed is measuring size/liquidity, not information).

## Event definition, frozen

- **Source:** SEC EDGAR. Per-CIK submissions JSON → Form 4 raw XML (strip the `xslF345X06/` prefix from
  `primaryDocument`; the rendered path returns HTML, not XML).
- **Event = transaction code `P`** — open-market purchase. **Excluded:** `S` (sale, kept as control),
  `A` (award/grant), `M` (option exercise), `F` (tax withholding), `C` (conversion), `G` (gift).
- **Actor:** officer or director only (`isOfficer` or `isDirector` true). Ten-percent owners excluded —
  their filings are frequently fund plumbing.
- **Timestamp = FILING DATE, never the transaction date.** The transaction date is private information
  until filed. **This is the look-ahead trap**, and it is why the two dates must never be swapped.
  Measured lag from the sample above: filed within 2 business days, as required.
- **Cluster variant:** ≥ 2 distinct insiders purchasing the same issuer within 30 calendar days. This is
  the variant with the strongest prior, because one purchase can be a small position adjustment.
- **Entry:** next session's open after the filing date. **Exit:** close at 21, 63 and 126 trading days.
- **Benchmark:** same-date mean forward return of other symbols in the same **ADV tercile × 126-day
  momentum tercile** — the same matched control already built for the score-inversion test, so results
  are directly comparable across the two programmes.
- **Costs:** the published bracket, reported at all three — **0.98 / 4.01 / 12.07 bp** round turn — not a
  single number. A result that only survives the floor estimate is not a result.
- **Inference:** symbol-cluster bootstrap (2,000 draws), CI reported with the **design effect actually
  obtained**, and a within-symbol **date-shift placebo** (purchase dates moved by a random offset inside
  the same symbol) as the falsifier.
- **Power:** MDE reported at **80% power**, constant 2.80, not the 2.0 rule of thumb. A null is only
  reported as a null if the MDE is small relative to the effect being claimed.

## Pre-registered gates

A variant is a candidate only if **all four** hold, and each is reported with its number:

1. Net excess at the **ceiling** cost (12.07 bp) has a 95% symbol-cluster CI excluding zero.
2. The date-shift placebo's 95th percentile is **below** the observed effect.
3. The effect survives at every horizon tested (21/63/126) in sign, even if only significant at one.
4. **Purchases beat sales on the same matched benchmark** — the asymmetry test. If `P` and `S` produce
   the same number, the signal is not information and the probe is dead.

## Known ways this will look like an edge and not be one

Listed in advance so they cannot be discovered post hoc and narrated as alpha:

- **Small-cap concentration.** Insider purchases cluster in small, illiquid names where the matched
  control is weak and impact is understated. Report the ADV distribution of the event set.
- **Cluster-then-announce.** Insiders sometimes buy before a known catalyst; that is not a tradable
  signal unless the announcement is also unpredicted. Report the share of events followed by an 8-K
  within 60 days.
- **Survivorship in the ticker list.** The universe is a current listing, so delisted issuers — which is
  where insider buying is most often *wrong* — are absent. This biases **toward** finding an edge; state
  it beside every positive.
- **Filing-date staleness.** A purchase filed on day t is known on day t; if the data pipeline uses a
  later date, the result is look-ahead. Assert the lag distribution from the parsed filings.

## What would be groundbreaking, stated honestly

Not "an edge in analyst ratings" — that question is now answered *unmeasurably*, and no amount of
further analysis changes that. The two results worth having are:

1. **A powered test that finally has a verdict**, positive or negative. Every gate in this estate has
   been untestable rather than failed; insider filings are the first domain where the machinery can
   actually return a verdict.
2. **A conditional result**: if the unconditional purchase signal is weak but *clusters* and *officer-only
   purchases* and *small-cap purchases* separate cleanly, that is a real, testable structure — and the
   sample is large enough to test those conditions without the multiple-testing penalty swallowing them.

A clean negative here is worth more than every provisional null in the estate, because it would be the
first null that was actually powered.

## next_probe

Collect Form 4 `P` and `S` for the current 308-ticker universe over the longest available window, report
the event count per ticker and the filing-lag distribution, then run the matched-benchmark test at the
three horizons with the four gates above. Publish the MDE beside every cell.
