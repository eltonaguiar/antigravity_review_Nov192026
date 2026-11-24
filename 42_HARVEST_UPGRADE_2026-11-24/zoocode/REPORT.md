# HARVEST independent verification — 2026-11-24

**Subject:** [`docs/data/harvest_signals.json`](../../docs/data/harvest_signals.json), 71 rows, `generated_at` 2026-11-24T11:00:15Z.
**Method:** derived only from the feed and its own `definitions` block. I did not read the generator or Kilo's code.
**Artifacts:** [`results.json`](results.json) (full ledger) · [`verify_harvest.py`](verify_harvest.py) (re-runnable, fixed seed).

Reproduce:

```bash
python3 42_HARVEST_UPGRADE_2026-11-24/zoocode/verify_harvest.py
```

## Headline

| # | Check | Verdict |
|---|---|---|
| 1 | Label recomputed from raw counts | **0 mismatches of 71** |
| 2 | Claimed rule reproduces every label | **HOLDS** — 71 pass / 0 fail |
| 3 | BRK-B `0/1/3/3/3` on 10 analysts | **Arithmetically consistent**; SELL is the rule applied correctly |
| 4 | DUK −2.1 STABLE vs WMT +2.1 IMPROVING | **Premise does not match the feed**: DUK is DETERIORATING; KPI counts agree with rows |
| 5 | Noise floor `100/analysts` | Median **2.94 pp**; **7 of 30** labels sit inside the noise floor |
| 6 | Monte Carlo + BH at 5% | **0 of 71 survive** (best raw p = 0.214) |

The label logic is correct. The weakness is not a bug in the arithmetic, it is that the *revision* signal is statistically empty at this sample size.

## 1–2. Label ledger and the claimed rule

The claimed rule (from the task statement and the feed's `definitions.consensus`):

```
score = (2*SB + B - S - 2*SS) / n ;  share = (SB + B) / n
STRONG_BUY  score >= 1.0 and share >= 0.75
BUY         score >= 0.3 and share >= 0.50
STRONG_SELL score <= -1.0 and share <= 0.15
SELL        score <= -0.3 and share <= 0.30
else HOLD
```

Tested against all 71 rows: **it holds exactly**. No row's stored label differs from the rule's output, and every stored `consensus_score` equals the recomputed score to 1e-6. There is no mismatch ledger to publish because there are no mismatches.

This matters because an earlier version of the page *did* have a documented-rule vs implementation mismatch: the legend showed score-only thresholds while the code also required buy-side agreement. That was fixed upstream (commit `06faf4e`, "consensus label must agree with buy-side share"), and the feed's `definitions` block now states both conditions. My check confirms the documentation and the data now agree.

## 3. BRK-B

Raw: `SB 0 / B 1 / H 3 / S 3 / SS 3`, n = 10, buy-side 10%, score −0.80, label SELL.

Evidence gathered:

- **Arithmetic is consistent**: the five counts sum to `analysts` (10), score −0.8 matches `(−3 − 6)/10`, share 0.10 matches `1/10`, and the rule maps −0.8 with 10% share to SELL. Nothing is miscalculated.
- **The scale is plausible, not broken**: three Strong Sells on Berkshire is a bearish stance, but it is expressible on the same −2..+2 scale as every other row (NVDA has 25 Strong Buys). No row uses an out-of-range bucket.
- **Cross-vendor**: Yahoo reports `n=3` analysts with `key=hold` for BRK-B, while this feed reports 10. That is a real disagreement in *coverage*, documented in [`harvest_targets.json`](harvest_targets.json), and both sources agree the name is not a buy.
- **Coverage is genuinely thin**: 10 analysts is the smallest on the page (median 34, peers PLD 21, BLK 24, SPG 25, PM 26, DUK 27).

Verdict: **not a symbol-mapping or rating-scale error that I can demonstrate**. It is a low-coverage row whose label is mechanically right and statistically fragile. The honest fix is a thin-coverage badge (already present) and a minimum-n filter, not a change to the rating.

## 4. Direction

- **DUK** is `mom_change_pp = −2.1` → **DETERIORATING**, not STABLE. **WMT** is `+2.1` → IMPROVING. The two rows are symmetric, as they should be.
- The threshold is exactly ±2.0 pp: the smallest |value| labelled IMPROVING is **2.1**, the largest labelled STABLE is **1.9**. No value sits on the boundary to create an off-by-rounding asymmetry.
- **Row vs recomputed direction: 0 mismatches.**
- **KPI cards vs rows agree**: 14 improving and 16 deteriorating rows against KPI 14 / 16, net −2 against KPI −2, 71 covered against KPI 71.

I could not reproduce the reported direction bug against the current feed. If it was real, it has since been fixed.

## 5. Noise floor

The smallest change one analyst can produce is `1/n` of the distribution, i.e. **100/n pp**. Median floor here is **2.94 pp** (n = 34), and it is **3.7 pp for DUK** (n = 27).

Seven rows are labelled IMPROVING or DETERIORATING on a move smaller than one analyst's worth of noise:

| symbol | n | floor pp | \|MoM\| pp | label |
|---|---|---|---|---|
| HD | 46 | 2.17 | 2.1 | IMPROVING |
| GE | 32 | 3.12 | 3.1 | DETERIORATING |
| T | 32 | 3.12 | 2.4 | DETERIORATING |
| NEM | 31 | 3.23 | 3.2 | DETERIORATING |
| JNJ | 30 | 3.33 | 3.3 | DETERIORATING |
| PEP | 29 | 3.45 | 3.4 | IMPROVING |
| DUK | 27 | 3.70 | 2.1 | DETERIORATING |

The ±2.0 pp threshold is below the median noise floor, so on a typical row a label can be triggered by a single analyst changing their mind.

## 6. Monte Carlo

**Null (stated so it can be attacked):** analyst opinion is unchanged, so the next month's distribution is a fresh draw of the same size from the current multinomial. **Statistic:** the shift in the score-weighted mean. **p-value:** two-sided, `(extreme + 1)/(N + 1)`. **Seed 20261124, 20,000 draws**, `numpy.random.default_rng`.

Result: **0 of 71 have raw p < 0.05**, and 0 survive Benjamini–Hochberg at 5%. The smallest p-values are PLD 0.214, INTC 0.341, BLK 0.532, TMO 0.551, NFLX 0.560.

A **charitable variant** (observed shift rounded up to one analyst, one notch, since a sub-analyst shift cannot really happen) gives a **median p of 0.909**. So even granting the most favourable interpretation, the month-over-month "revisions" are indistinguishable from resampling noise.

**Conclusion:** no revision on this page is significant. The ±2.0 pp threshold labels noise.

## Recommendation

`direction` should be the *effect size* description it claims to be, but it should not be read as a revision. A defensible change: keep the label, append the noise floor (`IMPROVING (2.1 pp, noise 2.2)`), or require `|MoM| >= 100/n` before labelling at all. That would relabel HD, GE, T, NEM, JNJ, PEP and DUK as STABLE-at-this-n.

## Design: simulating the endorsed picks of high-performing analysts

Requested follow-up. Sketch, with the parts that are currently impossible called out.

**Stage A — build the track record (the prerequisite).** Per `(firm, date, toGrade)` from [`ZOOCODE/HARVEST_2026-11-24T1040Z_starter.MD`](../../../findtorontoevents_antigravity.ca/ZOOCODE/) style runs:

1. Entry at the next open after the action date (never the same close, to avoid look-ahead).
2. Exit at +21, +63, +126 trading days, and at rating change.
3. Excess return vs the class benchmark (SPY for equity, not the raw return).
4. Aggregate per firm: `n`, hit rate, mean excess, bootstrap CI. **Suppress below n = 30**; a firm with 4 calls is noise.

**Stage B — select "high-performing" analysts.** Rank firms only when the CI lower bound exceeds 0. Because of the selection effect, the rank must come from a trailing window and be evaluated on the *next* window, or the "winners" are winners by construction (this is the PBO problem the repo already has tooling for in [`alpha_engine/anti_overfit_validator.py`](../../../findtorontoevents_antigravity.ca/alpha_engine/anti_overfit_validator.py)).

**Stage C — simulate the endorsed book.** Take the latest `kept` picks from those firms, equal-weight or inverse-vol, apply the repo's COST_OF_RECORD, and path-simulate:

- **block bootstrap** of daily returns (preserves autocorrelation, unlike iid resampling),
- **trade-count uncertainty**: resample the analysts' calls themselves, so the book's composition varies as it would in reality,
- report drawdown distribution and ruin probability, not a single equity curve,
- a **null control**: the same simulation on randomly chosen analysts of the same n. If the "high performers" do not beat that null, the ranking is noise.

**What blocks it today:** Stage A needs dated per-firm actions at scale, and [ZOOCODE/HARVEST files](../../../findtorontoevents_antigravity.ca/ZOOCODE/) cover only 179 equity symbols from one source; the upgrade/downgrade feed on the page itself is 403/429. Stage B also needs *history* of the ranking, not one snapshot. So the honest sequence is: collect the actions daily into the [`experiment_tracker`](../../../findtorontoevents_antigravity.ca/tools/experiment_tracker.py) ledger (it was built for exactly this: immutable run rows with a git SHA and config hash), and only run the simulation once the ledger has months of actions. Running it now would produce a number with no power behind it, which is the failure mode section 6 already demonstrates.
