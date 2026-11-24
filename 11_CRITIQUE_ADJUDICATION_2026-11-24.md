# Adjudication of 13 external model critiques (2026-11-24)

**Purpose:** the compressed "core findings" summary that circulated for critique is a **pre-retraction
snapshot**. Verified below. Handing it to agents as-is produces critiques of a project state that no
longer exists, and spends the cycle re-litigating concessions the page already published.

## A. The meta-finding, verified against origin (not asserted)

| Claim made by three models | Verified? | Evidence on origin |
|---|---|---|
| The void-rate finding was retracted | **YES** | `CONTEST/ROUND_01_2026-11-23/F1_RETRACTION.md` exists; `f1_quote_arm.py` is the repair |
| The headline was softened | **YES** | "no effect was detectable" present in `POWER_ANALYSIS.md` **and** `docs/index.html` |
| "41 void at fill" was pseudoreplication | **YES** | `R01B_REVIEW_RESULTS.md` + `docs/index.html` carry "bracket-calibration" |
| Equity cost is a bracket, not 12.07 bp | **YES** | 0.98 floor / 4.0124 central / 12.0749 ceiling in findings files |
| Ghost rows ≈ 22,947 | **YES** | `02_FINDINGS/data_quality_resolver.md`, `02_FINDINGS/contradictions.md` |

So the summary's strongest sentences ("every active attempt fails", "only the index survives") are
**stale**. The page's current position is "no effect detectable at this sample size", all ten nulls
provisional. Any critique round must start from that, not from the summary.

## B. Where the critiques are correct, and worth acting on

Ranked by consequence, not by how forcefully they were argued.

1. **The DSR gate rejects every known premium by construction.** Computed independently: DSR ≥ 0.95
   requires an annualised Sharpe of **1.63–2.14** (N = 25–658, 5–10 years). Published factor premia run
   Sharpe **0.3–0.5**. A gate that cannot admit anything real is not a test. This is the single most
   important finding in the whole set, and it mirrors our own result that **0 ratings survive the
   selection-null gate** — the same defect in two programmes.
2. **The index is exempt from the gates, not a survivor of them.** Applying DSR ≥ 0.95 to SPY would
   fail it too. The honest claim is "we cannot reject the beta default", not "the index survives". The
   page concedes this in prose; the table does not.
3. **The trial count is unstable, so every DSR value is unreproducible.** N circulates with a
   multi-decade spread; a 30% swing in the required Sharpe depending on which N is used. Fix the
   registry before quoting any DSR — the same defect we already logged as `dsr_correct.py` never having
   executed.
4. **Multiplicity is corrected twice (three times in places).** DSR deflates for trials and BH-FDR
   corrects again over overlapping families; the t-scaling adds a third. Choose one framework.
5. **Verdict labels conflate three states.** KILL (significantly negative), INCONCLUSIVE (underpowered),
   UNMEASURABLE (no data). The page's own table distinguishes them; its headline does not. Terminally
   labelled verdicts with no stated revival condition are not accountability.
6. **The MDE constant is the 50%-power one.** `POWER_ANALYSIS.md` states "Per-class MDE table (t = 2)"
   explicitly, so this is a disclosed choice, not an error — but a reader takes it as conventional.
   At 80% power the constant is 2.80: 5 years @ 10% vol is **12.5%/yr**, not 8.9; 10 years is
   **8.9%/yr**, not 6.3. Four independent models converged on this.
7. **Cost of ownership ≠ round-trip cost.** SPY's MER is ~9.45 bp/yr against a quoted 6.71 bp round
   trip. For a buy-and-hold endorsement the recurring drag is the expense ratio. Same omission on the
   bond sleeve.
8. **The value "correction" is likely wrong on its own arithmetic.** Adding the 2.78%/yr dividend yield
   to a long/short return ignores that the **short leg owes dividends**; the right adjustment is the
   yield spread between legs (~0.84%/yr on the page's own table). If so, the corrected +2.89% is
   overstated and lands suspiciously close to the expected 3%.
9. **VFV.TO does not escape US withholding in a TFSA.** It holds a US-listed ETF, so 15% withholding is
   paid inside the fund and is unrecoverable. Only US-listed funds held in an RRSP avoid it. Verify
   against a Canadian tax source before repeating the claim.

## C. Where a critique is wrong, and should not be carried forward

- **"DSR = SR/√N" and "N_eff = 73 × 10 = 730, so SR ≥ 2.53".** That is not the DSR formula, and
  multiplying picks by asset classes is not an effective-trial count. Reject.
- **"The pipeline is structurally blind at 8.9%/yr" applied to the whole harness.** The page documents
  that the harness pools **191 names × 250 days ≈ 47,750 observations per year, ~40× the power of a
  single equity curve** (`POWER_ANALYSIS.md` §6). The MDE critique is correct for single-curve tests
  and overstated for the cross-sectional harness. Several models assumed an annual-return series.
- **"Positive control is missing."** It exists and **failed**: HML at +0.11%/yr, root-caused to a
  price-only feed. The page already published this. Not a new finding.

## D. The one claim that would be most productive to test next

Not another critique — a measurement. **Inject synthetic edges of 1 / 2 / 4 / 8 %/yr through the entire
gate stack and publish the empirical pass-rate curve.** That converts "the gates are a one-way ratchet"
from an assertion into a number, and it is the only way to distinguish "no edge" from "no power". Three
models independently asked for it. Until it exists, every null in the estate is unfalsifiable.

## E. What NOT to re-litigate in the next round

Already published by the page, so re-raising them wastes a cycle: the soft headline, the contest
retraction, the commodity verdict withdrawal, the ghost-row contamination, the failed positive control,
the cost bracket, Gate 1 being red, and consensus not being evidence.
