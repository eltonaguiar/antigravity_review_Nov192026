# Open items from the Windows re-review

Reviewed `eltonaguiar/findtorontoevents_antigravity.ca` `main` @ `e2d552093172`
(`6abfa22364e` + `77718be66922`). No source changes were made by this review.
These are recommendations with owners; each line names the file to change.

## P1 — Forward ingest can stay green with zero admissible rows

**File:** `.github/workflows/forward-observations-ingest.yml`
**Evidence:** `alpha_engine/forward_observations_ingest.py:466` returns 0 on a successful
run regardless of `n_admissible`; the workflow prints `admissible=` at line 71 but the only
assert is `assert rows` at line 76, which passes on the existing 430-row ledger.

**Suggested change:** in the “Summarise ledger health” step, after loading
`/tmp/forward_ingest.json`, add:

```python
assert rep.get("n_admissible", 0) > 0, (
    "no admissible rows this run - the forward writer is not accruing")
```

Keep `added==0` legal when `n_admissible>0` (all rows may already be duplicates). If a
zero-admissible run can be legitimate (e.g. nothing closed in the window), gate the assert
on `write.added == 0 and duplicates == 0` or raise a `::warning` plus a separate weekly
alarm instead of a hard failure. The current state is the one to avoid: no signal at all.

**Owner:** kilo / financial side (the workflow is theirs).

## P1 — The ingest workflow does not pin `ref: main`

**File:** same workflow, line 39 (`uses: actions/checkout@v4`).
**Evidence:** the handoff and the explainer say `ref: main`; the YAML has no `ref`.
`workflow_dispatch` therefore checks out the selected ref and still pushes `HEAD:main`
(line 87). A manual run from a feature branch could commit that branch's ledger to main.

**Suggested change:** add

```yaml
with:
  ref: main
  fetch-depth: 1
```

to the checkout step. This also makes the schedule immune to a default-branch change.

## P1 — `audit3-ledger.yml` only exports `DB_PASS_STOCKS`

**File:** `.github/workflows/audit3-ledger.yml` lines 104 and 157.
**Evidence:** `tools/db_env.py` prefers `DB_PASSWORDS_JSON["stocks"]` and explicitly calls
the individual `DB_PASS_STOCKS` value potentially stale. Both the price-backfill and the
selection-alpha steps gate on `DB_PASS_STOCKS` being non-empty, so if only the canonical
JSON secret is configured, alpha is skipped and `require_alpha=True` demotes every
`PROVEN_T2`.

**Suggested change:** in both steps:

```yaml
env:
  DB_PASS_STOCKS: ${{ secrets.DB_PASS_STOCKS }}
  DB_PASSWORDS_JSON: ${{ secrets.DB_PASSWORDS_JSON }}
```

and change the skip guard to `if [ -z "$DB_PASS_STOCKS" ] && [ -z "$DB_PASSWORDS_JSON" ]`.
This mirrors the new ingest workflow, which already passes both.

Live ledger currently has `gate.applied=true`, so the alpha secret works today; this is a
resilience fix, not a current outage.

## P2 — Confirm the 357/359 `beta_dominant` rate

**Evidence:** the live ledger reports `beta_dominant=357`, `proven=1`, `unmeasured=1`.
That is a very strong prior that either (a) selection alpha is genuinely negative across
the fleet, or (b) the measurement window/coverage/cost model is systematically biased.
With `require_alpha` on, (b) would mean the gate is measuring the wrong thing and zero
PROVEN is not evidence of no edge.

**Suggested check:** pick the largest historically-profitable cohort and print its
`alpha_ci`, `alpha_n`, `need_n`, hold benchmark and coverage from the sidecar; compare with
a hand-computed pick-vs-buy-and-hold on five rows. Owner: financial side.

## P2 — The live ledger has zero CANDIDATE rows

**Evidence:** `n_candidate=0` alongside `n_proven=0`. The stated reason for CANDIDATE using
the bucket width (`dsr_local`) is to keep the forward-paper queue non-empty. On this
payload the split is inert (0 cells pass local while failing global; 2/66 pass either).

**Suggested check:** count cells by the gate that removed them (q over threshold, global
DSR, forward gate, harm, n). If the 658 floor alone empties the queue, that is a policy
call rather than a bug, but it should be stated on the page/metrics.

## P3 — Workflow race surface is acceptable but undocumented

`audit3-ledger.yml` (`:23 */6`, 15-min timeout, group `audit3-ledger`) and
`forward-observations-ingest.yml` (`:41 */6`, 20-min timeout, group
`forward-observations-ingest`) use different concurrency groups and both push to `main`.
Their file sets are disjoint and both retry, so this is low risk. If a push collision is
ever observed under delayed cron, put both on one concurrency group or let the ingest
consume the ledger job's lock. Owner: kilo.

## COMS notes for the next handoff

- `send` is **QoS 1**, non-retained (not QoS 0). `--retain` exists on both platforms.
- Do not retain `mentions/all`: last-writer-wins replaces the previous broadcast.
  Retain per-direct-inbox instead, then `check` the seat.
- `check` reads only the seat inbox, worktree `/all`, and `mentions/all`.
- B6 warns on self-refresh of your own seat; harmless noise, not a duplicate agent.
