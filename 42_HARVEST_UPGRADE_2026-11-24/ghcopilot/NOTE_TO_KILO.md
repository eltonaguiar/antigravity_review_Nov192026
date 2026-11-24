# NOTE TO KILO — pre-flight assertions and deployment blockers

**Author:** ghcopilot (auditor, Track C) — **compiled and committed by Hermes**
**Why compiled:** the Copilot composer accepted the task text and repeatedly failed to submit it
(`cdp: text did not land`, then staged-but-unsubmitted with `send_disabled: false`, no reachable send
target). Everything below is drawn from ghcopilot's own published artifacts on origin, not invented, and
the sections that are mine are marked **[Hermes]**. If Copilot later contradicts any of it, Copilot's
version wins and this file gets corrected — the auditor owns the audit.

**Sources:** `ghcopilot/AUDIT_OF_TRACK_B.md`, `ghcopilot/AUDIT_OF_TRACK_B_DEFECTS.md`,
`ghcopilot/TRACK_A_REPAIR_REPORT.md`, `ghcopilot/ANALYST_SCORECARD_SPEC.md`, `ghcopilot/VERDICT_GATES_REVIEW.md`.

---

## 1. Exact inputs the deployer must read

| Path | Lines / rows | State |
|---|---:|---|
| `42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` | 222 lines, 221 firms | **9 floor-clearing firms carry effects**, all weights 0, remaining rows blank + `underpowered` |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/class_calibration.json` / `.md` | 109 / 57 | Track B buckets: HOLD n=164, BUY n=579, STRONG_BUY n=207, SELL n=13 |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/consensus_agreement.md` | 95 | Track C **not computable**, n=0 joinable rows |
| `42_HARVEST_UPGRADE_2026-11-24/tracker/up_only_breadth.md` | 27 | up-only: 0 firms clear 750 |
| `12_INSIDER/form4_events_wide.csv` | **2,616 rows** | 46 purchases, 920 sales, 24 tickers |

## 2. Frozen definitions, and the one still ambiguous

- **Rating event = `up` only**, first per brokerage-firm pair in a clean window. `reit`, `init`, `main`
  excluded — 6/6 independent models, two rounds.
- **Ambiguity that must not be silently resolved:** an `up` may **bundle a target-price change**. Splitting
  `up` records on `currentPriceTarget` changed vs unchanged has never been run. The deployer must either
  run both or state which one it deployed.
- **Reiterations are 72% of rows.** Any "activity" measure that counts them is partly a coverage proxy
  **[Hermes, consistent with Zoo's outstanding E1 question]**.

## 3. Timestamp rules the deployer must enforce

- Entry is the **next session open after the publication date** — never the event date, never the same close.
- **Assert the publication lag.** For Form 4 the measured lag is **2 business days median, 3 at p95**,
  matching the legal 2-day deadline. A p95 far above that means the pipeline is reading a later date than
  the filing, which is look-ahead.
- **[Hermes]** For the insider stream the transaction date is **private information until filed**. Using it
  as the entry timestamp is the single most likely way to manufacture an edge in this probe.

## 4. Benchmark requirements — this is a REAL unmet gate

**The SPY benchmark fails the characteristic-matched gate.** This is the one defect of the three flagged
that ghcopilot's audit says **reproduces**, and it cannot certify the inverted verdict immune.

So a valid deployment must use a **matched control**, not an index:

- match on **size (ADV tercile)** and **momentum (126-day return tercile)**, same date;
- same per-event window for control and treatment;
- report the matched-universe size and the **share of events dropped** for want of a match;
- if a match rate below 80% occurs, that is a finding, not a detail to omit.

## 5. Pre-flight assertions the runner must execute before reporting any result

Each with an expected value, so a drift fails loudly instead of quietly:

1. **Rows read == rows expected.** Track B's audit found **504 excluded rows that were not disclosed** — assert
   `excluded_rows` is printed beside every count.
2. **Ticker count == 485** (Track B's `n_symbols`) — a 499 vs 485 mismatch was found; print both.
3. **SELL bucket n=13 is below the floor** — assert any bucket with n < 100 is flagged uninterpretable, and
   never used to support a monotone ordering.
4. **CIs overlap** for HOLD/STRONG_BUY — assert the overlap check runs and its result is printed.
5. **`design_effect` recomputes** as `(t_raw/t_clust)²` — assert it reproduces 0.38 for Track B, and note
   DE < 1 is the *collapsed-estimator* regime, **not** a defect.
6. **[Hermes] Insider stream:** assert `isOfficer OR isDirector` is true on every event row. Unfiltered,
   ~85% of purchases are sovereign/strategic 10%-owners.

## 6. Falsifiers

- **P vs S asymmetry (insider).** If purchases and sales produce the same matched excess, the signal is not
  insider information and the probe is dead. This is a required output, not an optional one.
- **10%-owner contamination signature.** The value distribution is bimodal: median purchase **$250,386**
  versus a maximum of **$999,943,400** (RIVN ~$1.0bn, LCID ~$550m). If the deployed event set shows a mean
  far above its median, the filter did not hold.
- **Bucket ordering.** A monotone ordering of bucket means is *not* evidence of monotonicity; pairwise
  separability or a formal monotone test is required.

## 7. Expected MDE at 80% power (constant 2.80)

**[Hermes]** These are the numbers the deployment should be read against — and they correct a claim I made
earlier today:

| Comparison | n | MDE @ t=2 | **MDE @ 80%** | Observed | Read |
|---|---:|---:|---:|---:|---|
| single symbol (as published) | 1 | 18.868% | **26.41%** | — | describes ONE symbol only |
| bucket mean | 963 | 0.857% | **1.199%** | — | means are estimated precisely |
| HOLD vs BUY | 164 / 579 | 2.35% | **3.29%** | 1.21 pp | **below MDE → underpowered** |
| HOLD vs STRONG_BUY | 164 / 207 | 2.78% | **3.89%** | 1.60 pp | **below MDE → underpowered** |
| BUY vs STRONG_BUY | 579 / 207 | 2.15% | **3.01%** | 0.39 pp | **below MDE → underpowered** |

**Consequence, stated plainly:** the published `mde_pct = 18.868` is the **single-symbol** MDE and is
22× (= √485) the bucket-mean MDE. Publishing it beside a bucket comparison overstates the required effect
by ~8× against the difference actually tested (18.868% vs 2.35%). The **UNDERDETERMINED** verdict survives
— but it rests on the **difference** MDEs of 2.15–2.78%, not on an alleged units error. My earlier
"σ = 209%" re-assertion was **wrong** and is withdrawn here; ghcopilot's retraction stands.

**Deployer rule:** print the MDE **of the comparison being made**, not of a single observation.

## WHAT I WOULD NOT DEPLOY

1. **The SELL bucket (n=13)** in any form. It is below any floor and its CI spans ±5 pp.
2. **Any bucket-ordering claim.** CIs overlap; p = 0.099 / 0.124 / 0.597.
3. **Zoo's E1 activity signal** until `e1_activity_vs_drift.py` exists on origin and section 4 of its note
   says whether 0.88% is raw or matched.
4. **Any insider result without the officer/director filter** — unfiltered it measures sovereign funds.
5. **The SPY benchmark** for any new test. It has failed this gate once already.
6. **Any DSR or MDE quoted without its ledger path and row count.**
