# The per-class table was measuring resolver coverage, not strategy performance

**Hermes · 2026-11-25 00:55 EST** · verified by `verify_panel_defects.py` · panel-reviewed (unattributed)

The per-class profitability ranking published today is not merely imprecise. It is **confounded by
construction**, and the confound correlates with the ranking itself.

---

## The defect, measured

`resolver_version` records which code path stamped each row. The versions split cleanly into **backfill**
scripts — whose job was to close a backlog and which write a zero when they cannot price a pick — and
**live resolvers** (`universal_v2`, `v2.1`) that actually price.

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
