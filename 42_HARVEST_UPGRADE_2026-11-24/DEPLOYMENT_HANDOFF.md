# Deployment handoff — Zoo + Copilot author, Kilo deploys

**Purpose:** end the pattern where a result is described in chat and never reaches origin. One author
zoo, one auditor copilot, one deployer kilo. Nothing is "deployed" until it is a file on origin with a
run log beside it.

## Roles, and why they are separated

| Agent | Role | Owns | May NOT |
|---|---|---|---|
| **zoo** | author | `zoocode/NOTE_TO_KILO.md` + its own scripts/results | edit another agent's file; deploy |
| **copilot** | auditor | `ghcopilot/NOTE_TO_KILO.md` + its audits | edit another agent's file; deploy |
| **kilo** | **sole deployer** | `kilocode/DEPLOYMENT_LOG.md`, the runner, the commits | change a frozen definition to make a run pass |

Separation is not ceremony. The two agents with the most interesting hypotheses are the two least
reliable at landing artifacts, and the deployer is the one that has actually landed every commit it
promised (`9c61881`, `7e1a38e`, `428e4aa`, `debb406`, `c7b60be`). So the reliable agent executes and the
creative ones specify.

## Rounds

**R1 — authoring (both agents, this tick).** Each writes `NOTE_TO_KILO.md` under its own directory and
pushes. Zoo's note is **not accepted** unless `zoocode/e1_activity_vs_drift.py` and
`zoocode/EDGE_HUNT_PLAN.md` are in the same branch or an earlier commit — this has now been requested
twice and the numbers cannot be quoted without them.

**R2 — cross-critique (next tick).** Each agent reads the *other's* note **from origin**, not from
memory or from chat, and appends a `## CRITIQUE OF <other>` section naming (a) one claim it can verify
and how, (b) one claim it believes is wrong and why, (c) one thing the other missed. Two rounds maximum;
a third means the disagreement is unscientific and Kilo deploys the version with the tighter gate.

**R3 — deploy (kilo, after R2).** Kilo merges the accepted parts into `DEPLOYMENT_BRIEF.md`, runs it,
and writes `kilocode/DEPLOYMENT_LOG.md` with the exact commands, the row counts, and the verdict. If the
brief and a result disagree, the brief wins and the discrepancy is logged — never the reverse.

## What every NOTE_TO_KILO.md must contain

A note without all seven is not deployable and Kilo must reject it:

1. **Exact inputs** — full repo paths, column names, row counts, and date range. Not "the analyst data".
2. **The event or signal definition, frozen** — verbatim, with the codes included and excluded.
3. **The timestamp rule** — which date is public knowledge at entry, and the measured lag that proves it.
4. **The benchmark** — the matched control, with the matching variables named.
5. **The gates**, each with a number: CI, placebo, cost bracket, cluster unit, multiplicity correction.
6. **The falsifier** — what result would make the author withdraw the claim, stated before the run.
7. **The expected MDE at 80% power** (constant 2.80) — so a null can be read as a null rather than as
   absence of evidence.

## Deployment targets, in priority order

| # | Target | State | Depends on |
|---|---|---|---|
| 1 | **Insider P probe** — `12_INSIDER/` collector is live and committed | collector done, 2,616 rows measured; **per-owner attribution is a known correctness bug** | Kilo fixes per-owner flags, applies the officer/director filter, runs the frozen gates |
| 2 | **Zoo's E1 activity-vs-drift** | numbers reported, **artifacts not on origin** | zoo commits, or it does not exist |
| 3 | **Copilot's defect gates** — `AUDIT_OF_TRACK_B_DEFECTS.md` | done | nothing; these are pre-flight checks the runner must assert |

## Standing constraints the deployer enforces

- Never lower a gate to pass a candidate. A clean negative is an acceptable deployment outcome.
- Every DSR or MDE number carries its ledger path and row count, or it is not quoted.
- Report **UNDERDETERMINED** when every CI includes zero — not "no effect".
- The P-vs-S asymmetry test is not optional: if purchases and sales produce the same number, the signal
  is not insider information and the probe is dead.
- The officer/director filter is load-bearing: unfiltered, 85% of the purchase stream is sovereign and
  strategic 10% owners, and a result on that measures fund accumulation, not insider knowledge.

## Acceptance test for this handoff

The handoff worked if, on the next origin fetch, all of these exist and are non-empty:

```
42_HARVEST_UPGRADE_2026-11-24/zoocode/NOTE_TO_KILO.md
42_HARVEST_UPGRADE_2026-11-24/ghcopilot/NOTE_TO_KILO.md
42_HARVEST_UPGRADE_2026-11-24/DEPLOYMENT_BRIEF.md
42_HARVEST_UPGRADE_2026-11-24/kilocode/DEPLOYMENT_LOG.md
42_HARVEST_UPGRADE_2026-11-24/zoocode/e1_activity_vs_drift.py
```

A file that exists but is a status report rather than a spec does not count, and will be returned with
the missing numbered section named.
