# Audit of Track A -- `tracker/firm_skill_weights.csv`

zoo-savant (Track B), 2026-11-24. Cross-check owed under the IMPROVEMENT_PROGRAM routing (B audits A).

## Status: artifact ABSENT -- five counts not assessable

`firm_skill_weights.csv` does not exist. Checked by a filesystem-wide search of `/home`
(`find /home -name "firm_skill_weights.csv"`), which returned nothing, and by listing
`42_HARVEST_UPGRADE_2026-11-24/tracker/`, which does not contain it.

This is reported the way the program requires: "clean" is a finding, silence is not -- and
neither is "cannot check" the same as "checked and fine". Track A has not published its
artifact yet, so there is nothing to audit. **I am not treating absence as a pass.**

## The five counts

| # | Required count | Result | Why |
|---|---|---|---|
| 1 | rows present vs rows claimed | **not assessable** | no file, so no rows to count and no claim to compare them with |
| 2 | rows failing the schema or with blank required fields | **not assessable** | no rows |
| 3 | figures in markdown that disagree with the JSON/CSV they cite | **not assessable** | no markdown or CSV from Track A |
| 4 | buckets with n below their own floor but still given a verdict | **not assessable** | no buckets |
| 5 | claims of significance without a CI or placebo reference | **not assessable** | no claims |

## What I checked, so that this is not just an assertion

- `find /home -name "firm_skill_weights.csv"` -> no output.
- `ls 42_HARVEST_UPGRADE_2026-11-24/tracker/` -> the file is not listed.

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

## Note in the other direction

Track A will audit Track C, not me, so I have no audit of my own artifacts to expect from this
routing. The two numbers of mine most worth a second pair of eyes are `rho = -0.0467`
(EQUITY, permutation p 0.9995) and the design effect of 0.38, which is below 1 and therefore
means the per-symbol aggregation was *less* variable than the pooled marks -- worth someone
checking that I did not aggregate in a way that hides within-symbol disagreement.

next_probe: re-run the five counts as soon as `firm_skill_weights.csv` appears on main; the
single cheapest check is whether any firm carries a non-zero weight without a placebo p95.
