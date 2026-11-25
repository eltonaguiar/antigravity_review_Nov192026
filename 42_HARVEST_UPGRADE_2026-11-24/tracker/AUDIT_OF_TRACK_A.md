# Audit of Track A -- `tracker/firm_skill_weights.csv`

zoo-savant (Track B), 2026-11-24. Cross-check owed under the IMPROVEMENT_PROGRAM routing (B audits A).

## Status: artifact PRESENT at a92a51b -- 222 lines, five counts assessed

`firm_skill_weights.csv` exists on `origin/main` at **a92a51b**. Exact-path evidence:
`git cat-file -e origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv`
returns success, and `git show` returns **222 lines** (header + 219 firm data rows + 2 comment lines).
The earlier `/home` filesystem search was the wrong check and is retracted.

Head:
`firm_norm,n_clean_events,mean_net_excess_bps,placebo_p95_bps,verdict,weight`

Key rows:
- `Morgan Stanley,473,178.20,109.6,beats_placebo,1.0`
- `BofA Securities,551,-40.61,99.6,indistinguishable,0`
- `Barclays,297,,,underpowered,0` (n below the 300 clean-event floor)

There are **9** rows with both effect columns filled, and **210** below-floor rows blank/underpowered
at a92a51b. This is a **discrepancy with the dispatch**, which stated 12 effect rows and 209
underpowered; the exact-path file wins. The audit below uses the file content, not the dispatch count.

## The five counts

| # | Required count | Result | Why |
|---|---|---|---|
| 1 | rows present vs rows claimed | **222 lines; 219 data; 9 effect rows; 210 underpowered** | exact-path `git show`; dispatch's 12/209/221 does not match a92a51b |
| 2 | rows failing schema or blank required fields | **0 schema failures; effect blanks only on 210 below-floor rows** | header has all 6 columns; 9 above-floor rows have mean + p95; Barclays 297 is blank and marked underpowered |
| 3 | markdown figures disagreeing with cited CSV | **0 of 3 spot-checks** | MS 178.20/109.6, BofA −40.61/99.6, Barclays blank/underpowered all match |
| 4 | buckets below floor given a verdict | **210 below-floor rows are `underpowered`; 0 wrongly given an effect verdict** | Barclays 297 < 300 and has no effect |
| 5 | significance without CI/placebo | **0** | only Morgan Stanley claims `beats_placebo`, and its own p95 109.6 is present |

## What I checked, so that this is not just an assertion

- `git cat-file -e origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` -> success.
- `git show origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` -> 222 lines.
- `git rev-parse origin/main` -> a92a51b.
- Spot-checked the three key rows above against the file; no values were inferred from memory.

## What Track A must publish for this audit to be possible

Per the program, the artifact is `firm_skill_weights.csv` with columns
`firm_norm, n_clean_events, mean_net_excess_bps, placebo_p95_bps, verdict, weight`,
`verdict` in {beats_placebo, indistinguishable, underpowered}, plus the count of firms in
each verdict bucket and the placebo p95 used.

Two things I would check first once it exists:
1. that a non-zero `weight` appears **only** where `mean_net_excess_bps` exceeds that firm's own
   `placebo_p95_bps` -- the program's unbendable rule ("no placebo, no weight");
2. that firms below the clean-event floor are marked `underpowered`, **never** `indistinguishable`,
   since those are different statements (one says the test lacked power, the other says it found
   nothing).

Both hold at a92a51b: Morgan Stanley is the only non-zero weight and clears its own p95; Barclays
(297) and the other below-floor rows are `underpowered`.

## Note in the other direction

Track A will audit Track C, not me, so I have no audit of my own artifacts to expect from this
routing. The two numbers of mine most worth a second pair of eyes are `rho = -0.0467`
(EQUITY, permutation p 0.9995) and the design effect of 0.38, which is below 1 and therefore
means the per-symbol aggregation was *less* variable than the pooled marks -- worth someone
checking that I did not aggregate in a way that hides within-symbol disagreement.

## Append: exact evidence tested

- SHA: **a92a51b**
- `git cat-file -e origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` -> success
- `git show origin/main:42_HARVEST_UPGRADE_2026-11-24/tracker/firm_skill_weights.csv` -> 222 lines
- `git rev-parse origin/main` -> a92a51b

next_probe: reconcile the dispatch's 12/209 count against the exact-path 9/210; if another branch
has 12 effect rows, name it and re-run the five counts against that branch -- not a `/home` search.
