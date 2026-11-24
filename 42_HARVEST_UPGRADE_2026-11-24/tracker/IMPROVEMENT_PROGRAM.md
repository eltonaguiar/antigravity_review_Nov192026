# IMPROVEMENT PROGRAM — picks, per asset class, analyst consensus, crowd consensus

**Status:** active. Three tracks run in parallel, one per agent, and **each track must verify another
track's artifact before either is accepted**. The point is not three opinions; it is three artifacts
that can be checked against each other and against the data.

Everything below is grounded in what this estate already measured. Where a number is an assumption it
is labelled as one.

---

## WHAT EXISTS ALREADY (do not re-derive)

| Thing | State |
|---|---|
| Audit feed picks | 3,961 ingested into `picktrack_picks`; each row carries `entry_price` and `current_price` |
| Firm-level rating history | obtainable via `tracker/yahoo_ratings.py` and `tracker/collect_analyst_history.py` |
| Breadth measured | 155 tickers → 70,233 action rows, 237 firms. **Clean** changes only: 14 firms reach 300, 5 reach 500, **0 reach 750**; best is BofA at 616 |
| Grade mapping | `tracker/grade_ordinals_draft.csv` (638 rows) + `ghcopilot/GRADE_ORDINAL_AUDIT.md`; frozen version still outstanding |
| Consensus scoring rule | `42_HARVEST_UPGRADE_2026-11-24/kilocode/harvest_rules.py`: STRONG_BUY +2, BUY +1, HOLD 0, SELL −1, STRONG_SELL −2 |
| Selection-null gate | `selection_null` table: noise alone passes at 69% (n=100), 80% (n=40), 95% (n=20), 100% (n=10) |
| Falsifier | within-ticker date-swap placebo, `tracker/placebo_dateswap.py` |
| Analyst leaderboard | **EMPTY** in the feed (`total_analysts` 0, stale 2026-03-26) — the per-firm track record must be built, not read |

**Known dead ends, do not spend a turn rediscovering them:** Finnhub `upgrade-downgrade` is 403 on
this key; `stock/recommendation` returns monthly aggregates with no firm; the hyrotrader data files
are 404; `/audit/hyrotrader/` is broken.

---

## THE THREE TRACKS

### Track A — per-firm skill weight (owner: whoever is free)
**Question:** which firms' rating changes have actually predicted forward returns, and by how much?
**Artifact:** `tracker/firm_skill_weights.csv` — `firm_norm, n_clean_events, mean_net_excess_bps,
placebo_p95_bps, verdict, weight`. Columns `verdict` ∈ {beats_placebo, indistinguishable, underpowered}.
**Numeric self-check it must report:** the count of firms in each verdict bucket, and the placebo p95
used.
**Rule that cannot be bent:** a firm gets a non-zero weight only if its mean net excess beats the
**95th percentile of its own within-ticker placebo**. No placebo, no weight. Firms below the clean-event
floor are `underpowered`, never `indistinguishable`.

### Track B — per-asset-class calibration (owner: whoever is free)
**Question:** inside each asset class, is the consensus score **monotone** in forward return, and does
any bucket survive cost?
**Artifact:** `tracker/class_calibration.md` + `.json` — per class: n, Spearman rho of score vs forward
net return, permutation p, and the bucket table with CIs.
**Numeric self-check:** rho and p per class, plus the design effect (clustering by symbol) for each.
**Rule:** report `insufficient` where n is under the class floor rather than pooling. An inverted sign
must be reported as inverted, not quietly relabelled.

### Track C — crowd vs analyst agreement (owner: whoever is free)
**Question:** where analyst consensus and crowd/user picks **agree**, is forward return better than where
they disagree?
**Artifact:** `tracker/consensus_agreement.md` — agreement buckets with n, mean net excess, CI, and the
placebo comparison; plus the list of the current top and bottom agreements.
**Numeric self-check:** counts per agreement bucket and the delta between agree and disagree with a CI.
**Rule:** this is a *difference* test, not a level test. Never claim "crowd picks work" from a positive
level; only that agreement adds over disagreement, and only if the delta CI excludes zero.

---

## CROSS-CHECK PROTOCOL (this is the part that makes it coordination)

Each track, before being called done, must audit one other track's artifact and answer **five counts**
about it, in writing, in its own directory:

1. rows present vs rows claimed
2. rows that fail the stated schema or have blank required fields
3. any figure in the markdown that does not match the JSON/CSV it cites
4. any bucket whose n is below its own stated floor but was still given a verdict
5. any claim of significance without a CI or a placebo reference

**Routing:** A audits B, B audits C, C audits A. A track that finds nothing wrong in another track's
artifact should say so explicitly and name what it checked — "clean" is a finding, silence is not.

Disagreements go in the audit file, never by editing the other agent's artifact. If two tracks
disagree on a number, both numbers are reported until a third measurement settles it.

---

## GATES THAT APPLY TO ALL THREE

1. **Net of cost.** Charge per-event cost by liquidity bucket, not one flat constant. A flat 26 bp was
   already measured to overcharge BOND by 42× and undercharge CRYPTO 2×.
2. **Characteristic-matched benchmark**, not a single index.
3. **Publish the MDE** next to every null, so a null is quantified rather than asserted.
4. **`insufficient sample` is a distinct outcome from `no effect`.**
5. **Never lower a gate to let a candidate through.** If a floor is unreachable, say so and report the
   ticker count needed — the breadth work already showed 750 clean events is not reachable at 155
   tickers.
6. **No new DSR until the formula is settled.** `CONTEST/tools/DSR_EXPECTED_VALUES.md` holds the
   reference values; the current estimator inflates to 0.99986 on noise.

---

## WHY THIS IS "CONTINUAL IMPROVEMENT" AND NOT A ONE-OFF

Each track emits a **versioned artifact plus a `next_probe` line**: the single cheapest measurement that
would most change its verdict. The next tick reads the `next_probe` lines and queues them, so the
program advances on its own rather than waiting to be re-briefed. A track that cannot name a next probe
has stopped improving and should say so.

Standing expectation, stated up front so a null is not treated as failure: **the prior is that most of
this comes back indistinguishable or underpowered.** That is a legitimate finding and must be published
as one — it would mean the analyst-and-crowd consensus signal our own pages lean on is not supported by
its own best-available evidence.
