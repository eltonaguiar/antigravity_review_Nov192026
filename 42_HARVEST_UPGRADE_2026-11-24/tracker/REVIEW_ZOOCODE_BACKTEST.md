# Review of zoocode's `backtest_analyst_actions.py` and its results

**Reviewed:** 2026-11-24 · **Script:** `42_HARVEST_UPGRADE_2026-11-24/zoocode/backtest_analyst_actions.py` (11,405 B)
**Results:** `backtest_results.json`, generated 2026-11-24T11:53:58Z, 151 symbols, 4 action classes, 3 horizons
**Status:** the run **finished**; it was not stalled. A 90-minute stall check was scheduled and then cancelled once the output file was found.

---

## What the script gets right

Credit where it is due, because these are the parts that usually go wrong:

| Correct decision | Evidence |
|---|---|
| **No lookahead** | Header line 16: entry = close on the FIRST trading day AFTER the action date, never the action day itself |
| **Identical benchmark window** | Line 19-20: excess = stock return − benchmark return *over the same entry/exit dates, identical by construction* |
| **Random-entry control** | Line 168-171: same symbol, same horizon, random date — answers "is this the signal or just the symbol?" |
| **Within-symbol control** | Compares UP against DOWN *within the same symbol*, which is the only control that survives a survivorship-biased universe |
| **Bootstrap CI** | 10,000 resamples per bucket rather than a normal approximation |
| **Dedupe** | `(firm, date)` key, highest grade kept |

## The results

| Horizon | Class | n | Mean excess | t | 95% CI |
|---|---|---|---|---|---|
| 5d | UP | 4,111 | −0.044% | −0.66 | [−0.178, +0.091] |
| 5d | INIT | 3,807 | **−0.253%** | **−3.47** | [−0.390, −0.102] |
| 21d | UP | 4,094 | +0.601% | 4.40 | [+0.338, +0.866] |
| 63d | UP | 4,056 | +2.186% | 7.77 | [+1.653, +2.719] |
| 63d | DOWN | 3,876 | +1.727% | 6.58 | [+1.204, +2.242] |
| 63d | MAINTAIN | 42,811 | +1.157% | 14.54 | [+1.004, +1.322] |

**The tell is on the DOWN row.** At 63 days, both upgrades (+2.19%) and downgrades (+1.73%) beat SPY by about
two points, with t-statistics of 7.8 and 6.6. A signal that says "buy" and "sell" with equal confidence is not
a direction signal — whatever is producing +2% is producing it for every class simultaneously.

Controls: within-symbol UP−DOWN = **+1.38 pp at 63d, 91 of 138 symbols positive, sign-test p = 0.00023**.
Random-entry edge at 63d = +1.55 pp.

---

## Confirmed defects

### 1. No transaction cost — returns are gross
`grep` for `0.0026`, `COST`, `fee`, `slippage`, `bps` returns nothing. Every number is before the 26 bp
round turn this programme uses as its house cost. At 63 days this removes ~0.26 pp from every bucket: the
within-symbol difference falls from 1.38 pp to about **1.12 pp**.

### 2. Overlapping windows are treated as independent observations
`t_stat` is `m / (sd / sqrt(n))` and `boot_ci` resamples individual observations. Both assume independence.

But at 63 days there are 4,056 observations from 151 symbols — roughly **27 overlapping observations per
symbol**, where consecutive monthly actions share two thirds of their forward window. The design effect is
approximately `1 + (m−1)·ρ`; at m=27 and a modest ρ≈0.3 that is **≈8.8×** variance inflation, which turns
t = 7.77 into roughly **t ≈ 2.6**. Still positive, no longer overwhelming.

The sign test is the most robust statistic here, but 138 symbols are not 138 independent experiments either —
they share the 2020 crash, the 2022 drawdown, the same rate cycle. Its p = 0.00023 is optimistic.

### 3. The universe is today's tickers, so both levels are survivorship-inflated
Symbols come from the current harvest universe. Companies delisted, acquired or bankrupt between 2012 and
2026 are absent by construction, so every class inherits a positive drift. This is exactly why UP **and**
DOWN both show +2%.

The important consequence: **the levels are unusable as alpha, and the difference is largely immune** — both
arms carry the same survivorship bias, so it cancels in UP−DOWN. That is the one number worth pursuing.

---

## Not present (checked and cleared)

- **Lookahead:** next-close entry, correct.
- **Benchmark window mismatch:** windows identical by construction.
- **Join explosion / row-weighted hit rate:** results are means over action rows, not marks, and the unit is
  one action — no pick-day multiplication here.
- **Divide-by-zero on trial count:** no DSR-style statistic is computed, so no defaulted denominator.

---

## CORRECTION — zoocode re-ran with the fixes, and my 1.38 pp claim does not survive

I wrote above that the within-symbol UP−DOWN difference was "the one number worth keeping" at +1.38 pp.
zoocode then rebuilt the script (11,405 → 14,060 B) and re-ran it with exactly the three fixes: the 26 bp
cost applied, cluster-robust inference by symbol, and a design effect reported per bucket. The corrected
result kills the claim:

| Horizon | raw UP−DOWN | **net of 26 bp** | 95% CI (by symbol) | symbols positive | sign-test p |
|---|---|---|---|---|---|
| 5d | +0.029% | **−0.231%** | [−0.263, +0.307] | 68 / 134 | 0.931 |
| 21d | +0.104% | **−0.156%** | [−0.424, +0.678] | 68 / 134 | 0.931 |
| 63d | +0.099% | **−0.161%** | [−0.936, +1.200] | 65 / 134 | 0.796 |

**The difference is about one tenth of a percentage point before cost, and negative after it.** The sign
test — 68 of 134 symbols positive at 21 days, 65 of 134 at 63 days — is indistinguishable from a coin flip.
My earlier +1.38 pp came from the coarse within-symbol summary in the first results file; once the
comparison is paired per symbol and charged the round turn, there is nothing left.

The design-effect measurement also confirms defect 2 quantitatively: at 63 days the bucket-level t-statistic
of **7.77 collapses to 2.45** with a **design effect of 10.07**. My estimate of ~8.8× from m=27 and ρ≈0.3 was
in the right place; the measured value is 10.07.

zoocode's own output now marks the bucket levels **`PUBLISHABLE: false`** with the reason
*"survivorship-contaminated levels; use within-symbol controls"* — and the within-symbol control it was
pointed at returns a clean negative. That is the correct end state: no analyst-action edge survives cost
and clustering.

**Revised verdict: discard the levels and discard the difference. This is a clean negative result, joining
the crypto, commodity and coverage-change findings.** Nothing in the analyst-action programme is fundable.

---

## Verdict (superseded by the correction above)

**Do not publish the bucket levels.** "+2.19% excess for upgrades" is not a finding; the downgrade bucket
says +1.73%, and both are survivorship artefacts of using the current ticker list across 14 years.

**The within-symbol difference is the only candidate**: UP beats DOWN by ~1.38 pp over 63 days on 91 of 138
symbols. Net of 26 bp cost that is ~1.12 pp. It survives survivorship by construction and survives the
random-entry control, but its significance is overstated by window overlap and shared market history.

**Minimum fix before this number is quoted anywhere:**
1. Apply the 26 bp round turn on both legs.
2. Replace the t-test and bootstrap with a **cluster-robust** version — resample by symbol, or aggregate to
   one observation per symbol per month, and report the resulting effective n.
3. Publish only the difference (UP−DOWN), never the level, and state the horizon where it holds (63d, not 5d
   or 21d).
4. Note that 5d INIT is reliably *negative* (−0.253%, t=−3.47) — if it survives clustering, that is an avoid
   signal, not a long signal, and it belongs on the page next to the crypto/commodity negatives.

**Trust level: usable with caveats, as a directional hypothesis only — not as a return forecast.**
