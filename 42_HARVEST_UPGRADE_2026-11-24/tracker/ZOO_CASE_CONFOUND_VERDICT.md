> PROVENANCE (added by the coordinator 2026-11-25 when landing this file): compiled in the findtorontoevents_antigravity.ca workspace on host eltonsGX10, where the cited data/ and tools/ paths live. Those paths are not present in this review repository. The body is unchanged; only this header was added.

# Case-confound verdict: could not be measured

**Date:** 2026-11-25T15:57Z
**Verdict: UNVERIFIED-DB-UNAVAILABLE**

## The claim under test

Published on the site changelog, attributed to kilo: in `at_pick_outcomes`, every backfilled row
carries the exact uppercase `asset_class` label `CRYPTO` while every lowercase `crypto` row is
live. The stated counts: 16,360 uppercase rows (12,730 backfilled, 3,630 live) and 21,858
lowercase rows (0 backfilled).

## What I ran

Each command was a single bare `sqlite3` invocation, no pipe, no redirect, no shell chain.

1. `sqlite3 data/live_picks.db "SELECT name, type FROM sqlite_master WHERE name LIKE '%at_pick_outcomes%';"`
   → returned **no rows**. The tables in `data/live_picks.db` are `live_picks` and `pick_history`
   (confirmed with `.tables`).

2. I then checked `sqlite_master` for `at_pick_outcomes` in every other non-empty SQLite file in
   the workspace (`audit_trail.db`, `data/audit_trail.db`, `alpha_engine.db`,
   `audit_trail/audit_trail.db`, `alpha_engine/data/alpha.db`,
   `alpha_engine/data/audit_consolidated.db`, `trading/data/positions.db`,
   `incubator/forward_test.db`, `battleground/data/dna_factory.db`,
   `quan_engine/data/quan_engine.db`, `meta_strategy/data/meta_strategy.db`,
   `coinglass_strategies/data/coinglass.db`, `crypto_data.db`, `.local/spend/spend.db`,
   `mlflow.db`, `swarm_runs/_sessions.db`, `blogwatcher/blogwatcher.db`) → **no database contains
   the table**.

3. `command -v mysql` → exit **127** (MySQL client not installed), so the MySQL server that does
   hold the table cannot be queried from here either.

## Why it is unavailable

`at_pick_outcomes` is a **MySQL** table, not a SQLite one. [`tools/mysql_resolve_at_pick_outcomes.py`](tools/mysql_resolve_at_pick_outcomes.py:1)
describes it as "Resolve stale OPEN rows in at_pick_outcomes", connects with `mysql.connector`
(`:114` `host=DB_HOST`, `:118` `database=DB_NAME`) and issues `FROM at_pick_outcomes po` (`:306`)
and `UPDATE at_pick_outcomes` (`:373`). The brief's suggestion that `data/live_picks.db` is the
likely owner is incorrect: that file holds `live_picks` and `pick_history` only. No SQLite copy of
the table exists in this workspace, and no MySQL client or reachable credentials are configured
in this session, so the case-sensitive grouping could not be run.

Exact error for the record: `sqlite3 data/live_picks.db "SELECT name, type FROM sqlite_master WHERE name LIKE '%at_pick_outcomes%';"` returned an empty result set (exit 0), and `mysql` returned `exit 127: command not found`.

## priced_coverage: data quality or pipeline identity?

I could not measure this, so I will not answer it as a finding. What can be said without the
data: if the claimed confound is real (uppercase `CRYPTO` ⇔ backfilled, lowercase `crypto` ⇔ live),
then `priced_coverage` computed per `asset_class` would be measuring **which ingestion pipeline
wrote the row** rather than how well the row is priced, because the label would be a pipeline
stamp in disguise. That is a conditional statement about the claim, not a measurement of it. The
test that would decide it needs the table: group by `asset_class` with a case-sensitive
comparison (`BINARY asset_class` in MySQL), cross-tabulate against the backfill flag, and compare
`priced_coverage` computed within each pipeline cohort. Until that runs on the MySQL database, the
question is open and this document records it as open.
