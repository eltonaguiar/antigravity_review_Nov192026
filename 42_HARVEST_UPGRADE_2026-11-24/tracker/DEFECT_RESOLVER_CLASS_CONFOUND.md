# The per-class table was measuring resolver coverage, not strategy performance

**Hermes · 2026-11-25 00:55 EST** · verified by `verify_panel_defects.py` · panel-reviewed (unattributed)

The per-class profitability ranking published today is not merely imprecise. It is **confounded by
construction**, and the confound correlates with the ranking itself.

---

## The defect, measured

`resolver_version` records which code path stamped each row. The versions split into **backfill** scripts —
whose job was to close a backlog — and **live resolvers** (`universal_v2`, `v2.1`).

**Refinement, because the first version of this paragraph overstated it.** The backfill scripts did not zero
everything they touched. `backfill_widened_202` priced **2,420 SL_HIT and 1,929 TP_HIT rows correctly** and
wrote a zero on only the **20,589 TIME_EXPIRED** rows. So the defect is not "the backfill could not price" —
it is narrower and more precise:

> **The `TIME_EXPIRED` branch stores `0` instead of a mark-to-market return at expiry.** A pick that hit
> neither take-profit nor stop-loss still has a return at the moment its window closed, and the resolver
> discarded it.

That distinction matters for the fix: the repair is not to rewrite a broken backfill, it is to give the
expiry branch a return — from `exit_price`/`entry_price` where the parent holds them, otherwise from the
price bar at expiry. It also explains why the zero mass sits exactly on one `resolution_method` value
(96.4%) while `SL_HIT` and `TP_HIT` are clean (0.0% and 0.02%).

| asset class | n | backfill rows | other rows | **% backfill** |
|---|---:|---:|---:|---:|
| INDEX | 314 | 314 | 0 | **100.0%** |
| ETF | 181 | 179 | 2 | 98.9% |
| BOND | 154 | 150 | 4 | 97.4% |
| COMMODITY | 5,882 | 5,721 | 161 | **97.3%** |
| FOREX | 16,039 | 15,427 | 612 | **96.2%** |
| EQUITY | 1,984 | 1,792 | 192 | 90.3% |
| FUTURES | 473 | 404 | 69 | 85.4% |
| **CRYPTO** | 38,213 | 12,730 | 25,483 | **33.3%** |
| UNKNOWN | 141 | 0 | 141 | 0.0% |

Now compare with the ranking that was published:

- **"Worst" classes:** COMMODITY (−607 total) at **97.3% backfill**, EQUITY (−175) at **90.3% backfill**.
- **"Best" class:** CRYPTO (+1,109) at **33.3% backfill**.

**The classes that looked bad are the classes that were mostly never priced.** The ordering was measuring
how much of each class the resolver had actually reached, not how the strategies performed. Any class with
a high backfill share is mechanically dragged toward zero by placeholder rows, and a class that was mostly
priced correctly competes against that.

This is worse than a wrong number in one cell. A wrong cell is visibly odd and gets checked; a confound
that *aligns with the conclusion* looks like a finding.

## Second defect: the two tables disagree, and the disagreement flips the sign

Where both tables hold a non-zero return for the same pick:

| | value |
|---|---:|
| rows where both non-zero | 7,945 |
| agree | 6,682 (84.1%) |
| **disagree** | **1,263 (15.9%)** |
| **largest disagreement** | **187.18 percentage points** |
| mean, from `at_pick_outcomes` | **−0.0929** |
| mean, from `trading_picks` | **+0.0172** |

**The two tables' means have opposite signs.** So "which table is authoritative" is not a bookkeeping
preference — it decides whether the book is profitable at all. Any fix that COALESCEs one over the other
without reporting the disagreement rate is choosing an answer, not measuring one.

## Third defect: the unjoined rows are not missing at random

| EXPIRED rows | n | mean return as stored |
|---|---:|---:|
| joins to `trading_picks` | 26,748 | −0.0435 |
| **no join at all** | **2,906** | **−0.0828** |

The rows that cannot be repaired are **nearly twice as negative** as those that can. Dropping them — which
every join-based fix does — biases the result **upward**. The panel's objection on this point was correct
and it is measurable, not theoretical.

## Fourth: 1,664 rows have a price and no return

`RESOLVE_FAILED_MAX_RETRIES`: n = 1,664, **exit_price present on all 1,664, entry_price present on all
1,664**, `pnl_pct` dead on all 1,664. These are computable from prices — they simply never were. Copying
`t.pnl_pct` for them fixes nothing, because it is also zero.

## What the panel contributed, honestly weighted

The router answers came from **one backend, three times** (`free-mode-large` and `free-mode` both route to
`deepseek-flash`; `deepseek-chat-direct` is the same family). Agreement between them is evidence about a
shared backend, not corroboration — so I verified every claim against the database instead of trusting the
convergence.

Two of its claims did not survive contact:

- *"`trading_picks.id` may not be unique — the join may fan out."* **Tested: unique.** 152,283 rows,
  152,283 distinct ids. No fan-out. Its own confidence was "medium-high, depends on DDL" — correctly hedged.
- *"`COALESCE(t.asset_class, ...)` cannot compile."* **Confirmed.** `trading_picks` has no `asset_class`
  column; its columns are `category`, `direction`, `sector`, `source_system`, etc. My SQL would have thrown
  `Unknown column`. A real error in my fix, caught before it ran.

A genuinely independent model — `qwen3:30b-a3b` on the Linux host, no shared backend, given the mechanism
**with my numbers withheld** so it had to supply its own reasoning — named the same defect first:

> *"Backfill scripts writing zeros for unresolved picks, disproportionately affecting asset classes with
> high backfill usage... this corrupts entire classes, making the ordering fundamentally invalid."*

and recommended exactly the control this document leads with: **publish the backfill resolution rate next
to every per-class average.** That is the defect **corroborated across two independent model families**
while their proposed remedies differed — which is the correct way to read panel agreement.

## What replaces the published table

1. **Publish the backfill share beside every per-class stat.** A reader must be able to see that COMMODITY's
   number rests on 161 genuinely-priced rows out of 5,882.
2. **Restrict the comparison to live-resolver rows** (`resolver_version NOT LIKE 'backfill%'`) and report `n`
   per class after that filter. For most classes this shrinks the sample to 2–4% — which is the honest
   sample, and the honesty is the point.
3. **Report the two-table disagreement rate and both means.** If they disagree in sign, no single figure
   may be published.
4. **Recompute the 1,664 from `exit_price`/`entry_price`** rather than copying a zero.
5. **Flag the 2,906 unjoined rows as an explicit, directional bias** rather than dropping them silently.

## Status of the published figures

The per-class table on `docs/changelog-2026-11-24.html` is **withdrawn** as a measure of strategy
performance. It may remain as a measure of *what the resolver had reached by class*, which is what the
numbers actually describe — and that is a useful thing to know, just not the thing it was labelled.

The `+6.34 bp` mean and `−38.98 bp` median over 33,092 resolved rows are unaffected by this confound
(they pool all classes), but they inherit the two-table disagreement and the unjoined-row bias, so they
carry a stated range rather than a point value until those are resolved.

---

## Third independent corroboration — and the formula that quantifies the bias

A third model family (Meta's Muse Ember, via OpenRouter's playground, answering a differently-worded
prompt that contained no measured figures at all) named the same defect first and supplied something the
other two did not — **an expression for the dilution**:

> *"A backfill 0 is not a realised breakeven; it's missing data coded as 0. If class A is 90% backfilled
> and class B 10%, their published means are roughly `observed_mean ≈ true_mean × priced_share`. The
> ranking therefore sorts classes largely by resolver coverage / backfill usage, not profitability. A
> genuinely strong but poorly backfilled class is pulled to 0; a weak but fully priced class can rank
> above it."*

That is the mechanism stated as arithmetic, and it inverts into a screening correction:

```
true_mean  ≈  published_mean / priced_share
```

Applied to the withdrawn table, using priced share = non-zero returns ÷ class rows:

| class | rows | priced rows | priced share | published mean | implied true mean |
|---|---:|---:|---:|---:|---:|
| CRYPTO | 38,213 | 29,567 | **77.4%** | +0.029% | **+0.037%** |
| FOREX | 16,039 | 2,947 | **18.4%** | +0.056% | **+0.30%** |
| COMMODITY | 5,882 | 922 | **15.7%** | −0.103% | **−0.66%** |
| EQUITY | 1,984 | 244 | **12.3%** | −0.088% | **−0.72%** |

**The published spread between classes was compressed by up to 6×.** FOREX's +0.056% and COMMODITY's
−0.103% are 18% and 16% complete respectively; dividing through moves them to +0.30% and −0.66%. The
ordering happens to survive the correction, but the magnitudes were wrong by a factor of five to six, and
that is before any cost is applied.

Caveat, and it matters: this division is only valid if unpriced picks are missing at random within a
class. We know they are not — the unjoined rows average nearly twice as negative as the joined ones — so
these implied figures are a **sanity bound on the distortion**, not corrected estimates. The correct
computation remains the one in "What replaces it": recompute from prices, publish coverage, never treat a
backfill zero as a return.

### Panel accounting, stated plainly

Three model families independently identified this defect:

| source | backend | independent? | contributed |
|---|---|---|---|
| router ×3 | deepseek-flash / deepseek-chat-direct | **no** — one family, three samples | D1 (SQL would not compile), D5 (resolver confound), D7 (1,664 recomputable), D9 (join fan-out — refuted by test) |
| `qwen3:30b-a3b` on the Linux host | Qwen | **yes** — different vendor, numbers withheld | named the confound first; recommended publishing the backfill resolution rate |
| Muse Ember (OpenRouter playground) | Meta | **yes** — different vendor, different prompt, no figures supplied | the dilution formula `observed ≈ true × priced_share` and `priced_coverage` as the mandatory companion statistic |

Two of the three were genuinely independent, and all three converged on the same defect **while proposing
different remedies** — which is the reading that matters. Their agreement corroborates the defect; it does
not corroborate any particular fix.
