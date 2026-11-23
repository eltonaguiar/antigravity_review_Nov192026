# F4 CORRECTION — 2026-11-23 · "a mutual fund beats its own ETF" was too strong

**Status: PUBLISHED CLAIM RETRACTED AND REPLACED.** The weaker claim that survives is about **fee drag**, not about
mutual funds.

## What was claimed

> A low-cost index **mutual fund** can beat its own ETF net of fees. Kilo measured FXAIX net CAGR 11.66% vs SPY 11.49%;
> buffy independently measured 11.67% vs 11.59% at corr 0.998. The durable mechanism is the fee gap (~0.08 pp/yr).

Two independent implementations agreed, so it was published as "the first claim in this programme to survive independent
replication". **Agreement between two implementations is not the same as a valid inference** — both could share the same
error, and here they did.

## What broke it

An adversarial reviewer responded to the fee-gap argument with the right structural objection: if the measured gap is
large relative to the fee gap, then either the vehicles do not track the index identically (sampling vs full
replication, securities lending income, share class, dividend conventions) or the gap is sampling error. It then named the
test that settles it: **compare the fund-vs-ETF gap against the spread across several ETFs tracking the same index.**

(That review also inherited a number I gave it wrong. I described the fee difference as "roughly one basis point per
year"; the real gap is 0.0945% − 0.015% = **7.95 bp/yr**. Its arithmetic was correct on the input it was handed, which is
a reminder that a reviewer can only be as good as the brief.)

## The measurement

Total return from Yahoo adjusted close (dividends reinvested), common window **2020-11-23 → 2026-11-20, 1,506 sessions,
5.98 years**, all five vehicles fully aligned:

| vehicle | wrapper | CAGR | vol | Sharpe | max DD | expense ratio |
|---|---|---|---|---|---|---|
| **VOO** | ETF | **13.269%** | 16.451% | **0.840** | −24.52% | 0.030% |
| IVV | ETF | 13.245% | 16.524% | 0.836 | −24.53% | 0.030% |
| FXAIX | mutual fund | 13.236% | 16.545% | 0.835 | −24.50% | 0.015% |
| VFIAX | mutual fund | 13.201% | 16.548% | 0.833 | −24.53% | 0.040% |
| SPY | ETF | 13.149% | 16.674% | 0.825 | −24.50% | 0.0945% |

Pairwise annualised differences, bp/yr:

```
          FXAIX    VFIAX      SPY      VOO      IVV
FXAIX      +0.0     +3.5     +8.7     -3.3     -0.9
VFIAX      -3.5     +0.0     +5.2     -6.8     -4.4
SPY        -8.7     -5.2     +0.0    -12.0     -9.6
VOO        +3.3     +6.8    +12.0     +0.0     +2.4
IVV        +0.9     +4.4     +9.6     -2.4     +0.0
```

## What this means

- **A mutual fund did NOT beat its ETF.** VOO, an ETF with a 0.030% expense ratio, beat *both* mutual funds
  (+3.3 bp/yr over FXAIX, +6.8 bp over VFIAX). The original claim is **falsified**.
- **The fee explanation survives, and quantifies well.** Best fund minus SPY = **+8.7 bp/yr** against a predicted fee gap
  of **7.95 bp/yr** — fees account for ~91% of that difference. SPY is last and is the most expensive by almost exactly
  its fee disadvantage. That is the systematic part, and it is real.
- **Everything else is inside the noise.** The spread among three ETFs tracking the same index (SPY/VOO/IVV) is
  **12.0 bp/yr**, which is *larger* than the whole fund-vs-ETF gap of 8.7 bp/yr. Vehicle choice beyond expense ratio
  cannot be resolved at this sample size.
- **The earlier 11.66% vs 11.49% figure (17 bp) was window-specific.** Over this aligned 5.98-year window the same pair
  differs by 8.7 bp. A 17 bp gap was itself evidence that the two implementations had not measured identical windows —
  the correlation of 0.998 was high enough to hide it.

## The claim that replaces it

> **Fee drag is real and worth about 8 bp/yr between the cheapest and most expensive S&P 500 vehicle. That is the entire
> resolvable effect. Wrapper type — mutual fund versus ETF — is not the edge; expense ratio is, and it sets the ceiling
> on how much vehicle choice can matter.**

Practical consequence, and it is the opposite of the retracted framing: **pick the cheapest vehicle in whichever wrapper
suits your account**, and do not pay for a fund on the theory that funds beat ETFs.

## Process notes, kept because they are the point

1. **Two independent implementations agreeing raised confidence without raising validity.** They shared a design error,
   not just a number. Replication across *implementations* is weaker than replication across *questions*.
2. **The falsification test was one API call and five symbols.** It cost minutes and had never been run, because the
   claim felt settled once two agents agreed.
3. **The published page said "the one claim that replicated".** It now says what the measurement supports. A page that
   keeps a retracted claim in its headline is worse than a page with no headline.
4. **A reviewer's structural objection beat my own arithmetic** even though the reviewer was working from a fee number I
   had supplied incorrectly. Attack the argument, not the premise, and both can be wrong at once.

*Paper only. No live orders, no credentials. Nothing here is investment advice.*
