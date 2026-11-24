# Audit of Track B's three flagged defects — reproduce / no-reproduce

**Auditor:** ghcopilot (Track C) · **Date:** 2026-11-24
**Target:** `42_HARVEST_UPGRADE_2026-11-24/zoocode/class_calibration.{json,md,py}` (origin)
**Method:** read the code that produces each figure, then recompute from the published fields. Where a
recomputation needs the row-level data, I say so rather than presenting arithmetic as verification.

| defect | reproduces? | changes the "inverted" verdict? |
|---|---|---|
| (a) `design_effect` 0.38 is below 1 | **Arithmetic: YES.** As a *defect*: **NO** | No |
| (b) `mde_pct` 18.868 looks like a units error | **NO — retracted. My flag was wrong** | No (it explains the verdict) |
| (c) benchmark SPY fails the characteristic-matched gate | **YES — claim reproduces, gate genuinely unmet** | **Cannot certify immunity** |

---

## (a) `design_effect = 0.38` being below 1

**Reproduces (arithmetic).** The code computes `design = (t_raw / t_clust) ** 2` (line 210) and
publishes `t_raw = 4.117`, `t_cluster = 6.709`. So
`(4.117 / 6.709)² = 0.3766 → rounded 0.38` ✓.

**But it is not a defect, and it is not inconsistent.** A design effect below 1 means the *clustered*
standard error is **smaller** than the naive one, which happens when the clustered estimator collapses
repeated observations to one value per group (here, per symbol). Collapsing averages away idiosyncratic
within-symbol noise, so the symbol-level mean is cleaner and its t-statistic is larger. That is a
legitimate outcome; it simply means the **naive** t (4.117) is the conservative one. In the usual
"clustering hurts" framing DE ≥ 1 comes from positive intra-cluster correlation; DE < 1 is the
opposite regime, not a mistake.

**What I could not verify:** the two t-statistics themselves. Recomputing them needs the per-event
`nets` array, which is not in the repo. So I verified the *relation* between the three published
numbers, not their inputs.

**Verdict impact: none.** The "inverted" verdict is driven by `rho = −0.0467` with
`permutation_p = 0.9995` — a permutation test on rank correlation. The t-statistics feed the design
effect and the CIs, not the sign call.

## (b) `mde_pct = 18.868` — I was wrong, and I am withdrawing this one

**Does not reproduce. This was my error, on COMS, and it should not stand.**

I flagged 18.868 % as implausible because I tested it against the two-sample z-sum formula
(`(z₁₋α/₂ + z_power) · √(2·sd²/n)`), under which an MDE of 18.868 % would require `sd ≈ 148 %` — absurd
for a return, hence "units error".

Their actual formula is different (code line 234):

```python
mde = 2 * (statistics.stdev(nets) / math.sqrt(n / max(res["n_symbols"], 1)))
mde_pct = round(100 * mde, 3)
```

i.e. `mde = 2 · sd · √(n_symbols / n)`. Inverting with their own `n = 963`, `n_symbols = 485`:

`sd = 0.18868 / (2 · √(485/963)) = 0.1329 = 13.29 %`

A **13.3 % standard deviation for forward net excess returns of single stocks is entirely ordinary.**
So `mde_pct = 18.868` is internally consistent, correctly labelled in percent, and not a units error.
My earlier flag compared their number against a formula they never used. **Retracted.**

**Verdict impact: none — and it actually explains the verdict.** An MDE of ~18.9 pp means the study
could only detect very large effects; the pairwise bucket differences (HOLD +2.88 vs BUY +1.67 vs
STRONG_BUY +1.28, i.e. ~1–1.6 pp) are an order of magnitude below it. So "no bucket ordering
established" is exactly what a correct MDE predicts.

## (c) SPY as a "characteristic-matched" benchmark

**Reproduces, and the gate really is unmet.** `class_calibration.json` states:

> `benchmark = "SPY (characteristic-matched on the only available characteristic: all rows are US equities)"`

Being a US equity is not a characteristic. Beta, size, sector, valuation and momentum are; none are
matched. So the artifact labels a single-index benchmark as characteristic-matched, and program
**gate 2 is not satisfied** even though the file reads as though it is.

**The part I got wrong earlier, and am correcting here.** I previously told COMS that this could not
change the verdict because subtracting a common benchmark is a constant shift, and Spearman rho is
invariant to a constant shift. Reading the code, that is false: the benchmark is subtracted
**per event window**, not once globally —

```python
bench = spy_c[idx[j]] / spy_c[idx[i]] - 1      # line 163: index window per event
```

Because each event has its own entry/exit pair, the subtraction differs row by row, so it is *not* a
constant shift and **rho is not invariant to the benchmark choice**. With `rho` as small as −0.0467,
a non-uniform re-basing is not obviously harmless.

**Verdict impact: I cannot certify the inverted verdict is immune.** This is the one of the three
that could move it, and settling it requires a re-run with a characteristic-matched benchmark
(β/size/sector-matched basket over the same windows). Note also that SPY is fetched with
`period="1y"` (line 123), which bounds the event windows.

## Summary of what changes

- (a) is a **non-defect**; the arithmetic reproduces and the negative design effect is an artefact of
  collapsing to symbol means. No action needed beyond a one-line explanatory note.
- (b) is **my error**; retracted. Their MDE is right, and it justifies the absence of a pairwise
  ordering claim.
- (c) is a **real defect**: wrong label, gate 2 unmet, and — contrary to what I said earlier — the
  verdict is *not* shielded from it. This is the only one worth spending effort on.

---

next_probe: re-run `class_calibration.py` with a beta/size/sector-matched benchmark over the identical per-event windows and publish `rho` and `permutation_p` both ways; if the sign does not survive the re-basing, the "inverted" verdict is a benchmark artefact and should be withdrawn, and if it does survive, the artifact gains the one thing it currently lacks — a gate-2-compliant result.
