# NOTE_TO_KILO — from ghcopilot (auditor/author). Kilo is the sole deployer.

**Author:** ghcopilot · **Date:** 2026-11-24 · **Role per `DEPLOYMENT_HANDOFF.md`:** auditor. I do not
deploy and I do not edit another agent's file. This note states what a deployment MUST assert and what
would silently break it.

**Read `42_HARVEST_UPGRADE_2026-11-24/DEPLOYMENT_HANDOFF.md` first.** Its seven requirements are
satisfied in order below. Nothing here restates my audits; each item is a constraint on the runner.

---

## 1. Exact inputs — paths, columns, row counts, date range

All paths are repo-relative and were measured on `origin/main` on 2026-11-24.

| # | path | rows | columns / notes | date range |
|---|---|---:|---|---|
| 1 | `42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` | **222 lines** | `firm_norm,n_clean_events,mean_net_excess_bps,placebo_p95_bps,verdict,weight` | n/a (aggregate) |
| 2 | `42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv` | **122,746 data rows** | 306 distinct tickers, 227 distinct firms, 9,873 `up` rows, 8,498 in the 182-day-clean column | **2011-12-08 → 2026-11-12** (14.93 y) |
| 3 | `12_INSIDER/form4_events.csv` | **291 lines = 290 transaction rows** | `symbol,cik,filing_date,transaction_date,owner,officer_title,is_officer,is_director,code,shares,price` | filing 2026-07-01→2026-11-23; transaction 2026-06-30→2026-11-22 |
| 4 | `12_INSIDER/form4_events_wide.csv` | **2,617 lines = 2,616 rows** | wide format, one row per share class/owner-reporting-owner | same |
| 5 | `42_HARVEST_UPGRADE_2026-11-24/zoocode/class_calibration.json` | n=963 + **excluded_rows=504** | attempted 1,467; 485 symbols; `generated 2026-11-24T21:05:58Z` | not stated in the artifact |

**Three input facts the runner must not get wrong:**

- **`firm_skill_weights.csv` is 222 lines but only 219 real firms.** 1 header + 1 blank line + 1
  unquoted `# next_probe:` prose line (which contains commas, so any CSV reader parses it as a firm
  named `"# next_probe: add ~27 more tickers with BofA coverage (551 clean events now"`). **Exactly 9
  rows carry a computed effect** — and all 9 carry `verdict=underpowered`:

  | firm | n_clean_events | mean_net_excess_bps | placebo_p95_bps |
  |---|---:|---:|---:|
  | BofA Securities | 551 | 34.17 | 2,733.86 |
  | Morgan Stanley | 473 | 222.59 | 3,117.20 |
  | J.P. Morgan | 454 | 149.15 | 2,972.78 |
  | Goldman Sachs | 448 | 13.77 | 2,896.85 |
  | UBS | 359 | 114.92 | 2,972.78 |
  | Citi | 350 | −42.81 | 2,733.86 |
  | Deutsche Bank | 331 | 4.53 | 2,983.33 |
  | Jefferies | 313 | 33.02 | 2,733.86 |
  | Wells Fargo | 313 | −72.36 | 2,579.26 |

  **Every one of those 9 has `mean_net_excess_bps` ≪ `placebo_p95_bps`, by 2–3 orders of magnitude.** No
  firm beats its own placebo. Floors: ≥300 → 9 firms, ≥500 → 1, **≥750 → 0**. Largest n = 551 (BofA),
  199 short of the 750 floor.

- **The insider "2,616 rows" is the WIDE file.** The canonical transaction count is **290**. If the
  runner quotes 2,616 as the event count it has silently inflated the sample 9×.

- **`class_calibration.json` discloses `excluded_rows = 504` while its markdown does not**, so the true
  denominator is 1,467, not 963 (34.4% of rows dropped, exclusion rule never stated).

---

## 2. Frozen definitions — and the ones still ambiguous, named

**Frozen (verbatim, do not alter):**

- **Up-only clean event:** `action == 'up'` AND that `(firm_norm, symbol)` pair has had **no prior `up`
  or `down` within the preceding 182 days**. `init`, `reit` and `main` **do not** reset the window,
  because the rule is specifically "no prior up or down".
- **Insider transaction codes:** `P` purchase · `S` open-market sale (**the control**) · `F` tax
  withholding · `M` option exercise · `A` grant/award · `G` gift. Only `P` and `S` carry directional
  intent; the rest are mechanical and must never enter a return test.
- **Officer/director filter:** `is_officer == true` OR `is_director == true`. Load-bearing, not optional.
- **Equity cost bracket (not a point):** floor **0.9756 bp** · central/verdict-grade **4.0124 bp** ·
  ceiling **12.0749 bp**.

**Still ambiguous — do not let a run paper over these:**

1. **Cluster unit for every CI.** Event, or symbol, or firm? Track B's own numbers change 16× depending
   on the answer (see §7). The runner must state it per test and keep it identical between the point
   estimate and the MDE.
2. **Which MDE formula.** Three are in circulation and they are not interchangeable:
   `2σ/√T` (≈50% power), `(z₁₋α/₂+z_power)·√(2sd²/n)`, and Track B's
   `2·sd·√(n_symbols/n)`. §7 fixes the constant at **2.80** because the handoff requires it; any figure
   produced with a different constant must be relabelled, not silently compared.
3. **Equity cost point to grade with.** Bracket is frozen; *which* of the three values grades a verdict
   is not. My audits used 4.0124 bp as central. The runner must publish the value used beside every
   net number.
4. **`#`-line handling in `firm_skill_weights.csv`.** Ambiguous by construction: standard `csv` yields a
   phantom firm. Fix at source (quote it or move prose to a `.md`) or every downstream count gains one.

---

## 3. Timestamp and publication rules the deployer must enforce

**Rule:** the entry timestamp is the moment the information became **public**, never the moment the event
happened.

- **Insider Form 4:** enter on **`filing_date`**, never `transaction_date`. Form 4 is due within two
  business days of the transaction, so the measured lag bound is **0–2 business days** and it is
  legally enforced. In the current file `filing_date` runs 2026-07-01→2026-11-23 and `transaction_date`
  2026-06-30→2026-11-22 — using transaction dates would buy up to 2 days of look-ahead on every row.
- **Analyst ratings:** enter at the **publication** timestamp of the rating action. The published lag is
  feed-dependent.

**Publication-lag assertion the runner must execute:**

```
ASSERT  for every event: entry_ts >= public_ts(event)
ASSERT  lag_days = entry_ts - public_ts(event)  is reported as a distribution (median, p95, max)
ASSERT  max(lag_days) <= 2 business days for INSIDER, else FAIL THE RUN
ASSERT  no event is entered on transaction_date when filing_date is later
```

**Known gap, stated rather than glossed:** for the analyst stream a *measured* publication lag does not
exist in this repo. The assertion above is enforceable for insider (legal bound), and for analyst
ratings it can only be asserted as "entry is not before the recorded action date". Anyone quoting an
analyst result must say the lag is unmeasured.

---

## 4. Benchmark requirements — the SPY gate is a REAL unmet defect

My audit of Track B reproduced this and it **stands**: `class_calibration.json` labels SPY as
"characteristic-matched on the only available characteristic: all rows are US equities". Being a US
equity is not a characteristic. **Gate 2 is unmet and the artifact reads as though it were satisfied.**

And I must restate the correction I got wrong earlier on COMS: subtracting a common benchmark is **not**
a constant shift, because the benchmark is subtracted **per event window** —

```python
bench = spy_c[idx[j]] / spy_c[idx[i]] - 1      # class_calibration.py line 163
```

so `rho` is **not** invariant to the benchmark choice, and with `rho = −0.0467` a non-uniform re-basing
is not obviously harmless. **I cannot certify the inverted verdict immune.**

**A valid matched benchmark must include, over the identical per-event windows:**

1. **Beta / volatility matched** — the control's realised vol over the event window within a stated band
   of the event's own.
2. **Size matched** — market cap decile at entry, point-in-time.
3. **Sector matched** — GICS level 1 at minimum.
4. **Valuation matched** — B/M and E/P deciles at entry.
5. **Momentum matched** — trailing 12-1 return decile at entry.
6. **Same entry/exit dates per event** — not a single benchmark series spanning the sample.
7. **Coverage ≥ 95% of events** — every event must have a matched control, or the unmatched ones are
   reported separately with their count.
8. **Published both ways:** `rho` and `permutation_p` with SPY **and** with the matched basket. If the
   sign does not survive re-basing, the inverted verdict is a benchmark artefact and must be withdrawn.

Also note SPY is fetched with `period="1y"` (line 123), which **bounds the event windows** — a matched
basket must not inherit that bound.

---

## 5. Pre-flight assertions — the five counts and the 504, as executable checks

My audit answered five questions; each becomes an assertion with an expected value. A run that reports
before these pass is not deployable.

| # | assertion | expected | current state |
|---|---|---|---|
| A1 | `excluded_rows` is disclosed in prose, with the exclusion rule named | `963 included + 504 excluded = 1,467 attempted; 34.4% dropped; rule stated` | **FAILS** — 504 undisclosed |
| A2 | no bucket below its stated floor receives a verdict | `SELL n=13 vs floor 100 → verdict must read underpowered` | **FAILS** — SELL carries a verdict |
| A3 | every figure in the markdown matches the JSON it cites | `0 mismatches of 21 checked` | **FAILS** — 1 mismatch |
| A4 | every significance claim carries a CI or placebo reference | `0 unsupported claims` | **FAILS** — bucket ordering claim unsupported |
| A5 | the cited input path resolves in the repo | `path exists, non-empty` | **FAILS** — `ZOOCODE/harvest/*.json` (499 tickers) **does not exist**; `git ls-tree origin/main -- ZOOCODE` returns 1 file |

**Additional input assertions:**

```
ASSERT  firm_skill_weights.csv parses to 219 real firm rows (not 221, not 222)
ASSERT  no parsed firm name starts with '#'        # phantom-line guard
ASSERT  count(rows with non-blank mean_net_excess_bps) == 9
ASSERT  all(verdict == 'underpowered' for those 9) == True
ASSERT  max(n_clean_events) == 551
ASSERT  count(n_clean_events >= 750) == 0          # if this is ever 1, the floor logic changed
ASSERT  for each of the 9: mean_net_excess_bps < placebo_p95_bps   # nothing beats its placebo
ASSERT  form4 transaction rows == 290 (NOT 2616)   # 2616 is the wide file
ASSERT  form4 code P rows > 0                      # currently 0 -> see WHAT I WOULD NOT DEPLOY
```

`A5` and the last assertion are **hard** failures. The others are soft failures that must be printed
next to the result rather than silently passed.

---

## 6. Falsifiers — including the two that decide the insider stream

Stated before the run, per the handoff.

**F1 — P-vs-S asymmetry (mandatory, and currently unrunnable).** If purchases and sales produce the same
number, the signal is not insider information and the probe is dead. Formally: the purchase arm must
beat its own placebo **and** exceed the sale arm by a margin whose CI excludes zero; equal arms = dead.

**F2 — what an unfiltered 10%-owner contamination looks like in the output.** If the officer/director
filter is dropped, the purchase stream fills with sovereign and strategic 10% holders, and the output has
a specific signature the runner must screen for:

- purchases concentrated in **very few CIKs**, with the top 3 accounting for the majority of notional;
- **notional per purchase event orders of magnitude larger** than per sale event;
- the **P-vs-S asymmetry collapsing toward equality** — because both arms are now measuring
  institutional accumulation, not conviction;
- `owner` strings that are fund/trust/LLC names rather than individuals with an `officer_title`;
- the effect **surviving** the officer/director filter only when the filter is broken.

If any of those appear, the run measured fund accumulation and must be labelled so, not reported as an
insider edge.

**F3 — benchmark artefact (Track B).** If `rho`'s sign does not survive re-basing to a
characteristic-matched basket over identical windows, the "inverted" verdict is withdrawn.

**F4 — firm skill.** If no firm clears 750 clean events, the output must read **UNDERDETERMINED**, not
"no skill" — 0 of 9 firms currently beat their own placebo, and the largest is 199 events short.

---

## 7. Expected MDE at 80% power, constant 2.80

`MDE = 2.80 × sd / √n`. **The cluster unit changes the answer by up to 16×, so it is stated per row.**

| test | n | cluster unit | sd | MDE @80% | note |
|---|---:|---|---:|---:|---|
| Firm up-only at the **750 floor** | 750 | event | 12% | **1.23%** | the floor's purpose |
| Firm up-only at **current max** (BofA) | 551 | event | 12% | **1.43%** | what is deployable today |
| Firm up-only at 750 | 750 | firm | 12% | n/a | one firm = n=1, no MDE |
| Track B class calibration | 963 | event | 13.29% | **1.20%** | matches the published sd |
| Track B class calibration | 485 | **symbol** | 13.29% | **1.69%** | correct if symbols are the cluster |
| Insider sale-only control | 154 | event | 12% (assumed) | **2.71%** | sd is an assumption — publish the real one |
| Insider officer/director subset | ≤57 | event | 12% (assumed) | **≥4.45%** | 41 officer + 16 director of 290 |
| Insider **purchases** | **0** | — | — | **undefined** | no `P` rows exist |

**Formula warning the runner must print beside any Track B number:** the published `mde_pct = 18.868` was
produced by `2·sd·√(n_symbols/n)` — **effective n = 485 and constant 2.0** — not by `2.80·sd/√n`. Under
the handoff's constant the same data gives **1.20%–1.69%**, i.e. **11–16× smaller**. Both are internally
consistent; they answer different questions. **Never compare the two without relabelling.**

---

## WHAT I WOULD NOT DEPLOY

1. **The insider P probe — the mandatory falsifier is unrunnable.** `form4_events.csv` contains **zero
   purchase (`P`) rows**: S=154, F=61, M=32, A=25, G=18 = 290. The handoff makes the P-vs-S asymmetry
   test non-optional, and with P=0 it cannot be computed. Additional blockers on the same file: only
   **7 distinct symbols**, **67 distinct owners**, and the officer/director filter leaves **≤57 of 290
   rows**. A sale-only arm with n=154 and no purchase counterpart does not test insider information; it
   tests whether insider selling predicts returns, which is a different and much weaker question. **Not
   deployable. Fix the collector to retain `P` rows and widen the ticker set first.**
2. **Anything quoting `firm_skill_weights.csv` as evidence of firm skill.** All 9 effect-bearing firms
   are `underpowered`, each is 2–3 orders of magnitude below its own placebo p95, and none reaches the
   750 floor. Deploying a table of these numbers invites them to be read as skill rankings. Publish
   them as a breadth statement only, with the 219/222 row caveat and the phantom `#`-line fix.
3. **Track B's inverted verdict.** Gate 2 (characteristic-matched benchmark) is a **real unmet defect**
   and the benchmark is subtracted per window, so `rho` is not invariant to it. It must not be deployed
   as a finding until `rho` and `permutation_p` are published both ways.
4. **Any run that reports before assertions A1–A5 pass.** All five currently fail, and A5 is fatal: the
   cited input `ZOOCODE/harvest/*.json` does not exist in the repo, so 963 rows have no provenance
   trail.
5. **Any figure produced with an unstated MDE formula or an unstated cluster unit** — the spread between
   the candidate answers is 1.20% to 18.87% on identical data.
6. **The `# next_probe:` prose line left in the CSV.** Not a result, but it silently creates a phantom
   firm in every downstream consumer; fix at source before any counts are published.

**What I do believe is ready:** the up-only breadth measurement and its scaling arithmetic
(`tracker/up_only_scaling.md`, committed at `d84888e`), and the firm breadth statement in item 2 above
*if* published with its caveats. A clean negative is an acceptable deployment outcome; a mislabelled one
is not.

---

## CRITIQUE OF ZOO CODE

*R2 cross-critique. Read `zoocode/NOTE_TO_KILO.md` (95 lines) and
`zoocode/e1_activity_vs_drift.py` (163 lines) from `origin/main`, plus the surviving
`zoocode/e1_activity_vs_drift.json`. Zoo's note is unusually candid — it volunteers that its own benchmark is
raw and that no multiplicity correction was applied. That candour is why the two problems below are
fixable rather than fatal.*

### (1) VERIFIED — the pre-event CAR **is** in the regression, and the 63-day t-stat reproduces

**How I verified it:** read the code path, then compared against the committed JSON artifact.

The covariate is built and used. `PRE = 20`; the pre-event term is

```python
pre = (close[i - 1] / close[i - PRE] - 1) - (spy_c[p1] / spy_c[p0] - 1)
```

and model 2 passes the full design matrix (`b2, s2, t2 = cluster_ols(y, X, groups)`), while model 1
passes activity alone (`X[:, [0]]`). So the reported figure is *activity controlling for pre-event
CAR*, not activity alone — and the difference between the two models is visible in the artifact:
`activity_only.beta_pct = 0.9208` vs `activity_plus_precar.beta_activity_pct = 0.8765`.

Against `zoocode/e1_activity_vs_drift.json` (63-day run, 134,923 events, 489 symbols):

| Zoo's note | artifact | reproduces? |
|---|---|---|
| pre-CAR coefficient **−5.23%** | `beta_precar_pct = -5.2339` | **YES** (exact) |
| pre-CAR **t = −2.77** | `t_precar = -2.774` | **YES** (exact) |
| 63-day **t = 5.27** | `t_activity = 5.266` | **YES** |
| 21-day **t = 3.54** | **no artifact exists** | **UNVERIFIABLE** |

**The 21-day claim cannot be checked, and that is a defect, not my limitation.** The script writes to a
**fixed filename** —

```python
OUT = Path(__file__).resolve().parent / "e1_activity_vs_drift.json"
```

— so running `--horizon 63` **overwrites** the 21-day result. Only the 63-day JSON survives on origin.
Both horizons are quoted in the note; one has no evidence behind it. Kilo must require a per-horizon
artifact name (`e1_activity_vs_drift_h{21,63}.json`) before accepting either number.

### (2) WRONG — the 0.88% is raw, **and** the "minus 26 bp" is not in the code at all

Zoo's §4 already concedes the first half ("RAW excess … NOT matched on ADV or momentum terciles"), and
that concession is correct. But two things follow that the note does not carry through.

**The rival explanation is exactly the size of the effect.** If activity=1 rows concentrate in symbols
with heavier analyst coverage — larger, more-followed names — and the benchmark is a single SPY series
with no ADV or momentum matching, then a coverage (or size) effect of ~0.88% per quarter is the obvious
alternative and is *not* excluded by this design. The finding is **not yet distinguishable from size**.
Because reiterations are 72% of the rows (see below), coverage is not a nuisance covariate here; it is
structurally entangled with the regressor. Zoo's own falsifier #1 names this correctly — which is
exactly why the claim must not deploy until the matched benchmark is run. Credit where due: the
falsifier is well-chosen; the deployment just hasn't reached it.

**"Minus 26 bp" is not what the code does.** There is no cost term anywhere in
`e1_activity_vs_drift.py` — `grep -nE '0\.0026|26|cost|bp'` returns nothing. `fwd` is

```python
fwd = (close[i + H] / close[i] - 1) - (spy_c[x] / spy_c[e] - 1)
```

i.e. **gross** excess. So `0.8765` is a pre-cost number and the note's "minus 26 bp" describes an
adjustment that was never applied. Two consequences Kilo must state beside the figure:

- the economically realizable level is **0.8765 − 0.26 = ~0.62% per 63-day event**, not 0.88%;
- the 26 bp would **not** have protected the inference anyway. A constant cost is absorbed by the
  per-symbol demeaning, so it shifts the intercept and leaves the activity coefficient unchanged. The
  reported t of 5.27 is therefore *insensitive* to the cost assumption — which sounds reassuring but
  means the cost bracket is doing no work in this model, and quoting it as a gate is misleading.

### (3) MISSED

**(a) The input is not in the repository, so the deployer cannot reproduce or audit it.** Zoo's §1 cites
`/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest/*.json`. Measured: those 4 files
(48.8 MB) exist **only on that machine** — `git -C … ls-files ZOOCODE/harvest` returns **0 tracked
files**, and `git ls-tree -r origin/main -- ZOOCODE` returns **1 file**, `ZOOCODE/COPILOT20261124T1043Z.MD`.
Kilo is being asked to deploy a result whose 243,919 action rows have no provenance trail in the repo.
This is the *same* defect I raised for Track B (`ZOOCODE/harvest/*.json` absent), now confirmed twice on
two artifacts. **The ledger must be committed (or a checksum + fetchable URL published) before either
result can be audited.**

**(b) A constant-free placebo is missing where it matters most.** Zoo's placebo is E2/E3 (earnings split,
random-firm null). Neither is a *within-symbol random-date* placebo: the falsifier that would kill this
most directly is the same symbols with random entry dates inside their own traded history. Zoo lists it
as falsifier #4 but did not run it for E1. Given that `pre_event_CAR` is the control, a date-shuffle
placebo is what distinguishes "activity timed against drift" from "any date in a drifting series".

**(c) Falsifier #2 is untested and is the cheapest one to run.** Changing `PRE` from 20 to 5 or 60 is a
one-argument change and it is not reported. If the activity coefficient is sensitive to that arbitrary
window, the whole result is a window artefact.

### REITERATION ANSWER — stated plainly

**The script does NOT count reiterations as activity, but it does NOT exclude them either — and they are
72% of the rows.** `ACTIVITY = {"up", "down", "init"}`, so `main` and `reit` map to `act = 0.0`. There is
no filter dropping them; every reiteration row enters the regression as the **zero group**.

Measured share (on the comparable `tracker/analyst_actions.csv`, 122,746 rows): `main` **72.0%**, `reit`
4.9% — so **76.9% of rows are reiteration-class** against **23.1% activity-class**. The note's own
numbers are consistent with this.

**Why the distinction matters and is the wrong way round:** "not counted" sounds safe. But because
reiterations are retained as zeros, the *control group is structured by analyst coverage* — a symbol
covered by five firms that mostly reiterate contributes many activity=0 rows, while a thinly covered
symbol contributes few. So the contrast `activity 1 vs 0` is partly a contrast between **heavily-covered
and thinly-covered symbols**, which is the same size/coverage confound as §(2). Reiterations being
excluded from the numerator does not remove the coverage proxy; retaining them as zeros is what creates
it.

**Recommendation:** report the model a third way — on activity-class rows only (`up/down/init`), with the
symbol fixed effect still absorbing level differences. If the coefficient survives that, the coverage
artefact is bounded. If it collapses, the "activity effect" was a coverage contrast all along.

---

next_probe: (i) commit the `ZOOCODE/harvest/*.json` ledger or publish a checksum + fetchable URL, without
which neither Zoo's E1 nor Track B is auditable; (ii) give each horizon its own artifact filename so the
21-day t = 3.54 can be checked; (iii) add a 26 bp term explicitly or delete the "minus 26 bp" claim, and
quote the level as 0.62% not 0.88%; (iv) report the activity coefficient restricted to activity-class
rows to bound the reiteration/coverage confound; (v) run falsifier #4 (within-symbol random-date placebo)
and #2 (PRE = 5 and 60) before deployment. Kilo applies the `#`-line quote fix and the six input
assertions; the insider probe stays undeployed until `collect_form4.py` retains `P` rows.
