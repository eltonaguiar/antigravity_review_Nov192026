# Parity items and provenance record (2026-11-23)

## Kilo - parity items 1-3

| Item | Result |
|---|---|
| P0-2 - audit3-ledger is the only writer | **exactly 1** history-write site; no disagreement with the plan's expected number. Files changed: **none** (verification only) |
| P0-3 - compounded drawdown F1 | 4 new tests; **38 total tribunal tests green**; no files changed for the block - already implemented and committed in `ca01ddbc182` |

Kilo reported "no files changed" twice rather than manufacturing a diff to look productive. That is the
behaviour this programme needs: an agent measuring a no-op is a measurement, an agent inventing a change
to match a plan is a fabrication.

## Zoo Code - the push and the correction

- **12 commits pushed**, each by explicit `sha:refs/heads/<branch>` and verified with `ls-remote` before
  moving to the next: refs **259 -> 271**, exactly 12 added, zero modified, zero deleted
- `push/phase2-round-2026-11-22` correctly **not** pushed (diverged local ref)
- main moved during the window (`55229d1cb -> 294523e93`) by two bot commits, verified as a genuine
  fast-forward, not a rewrite
- **Self-correction worth recording**: "pushing did NOT activate the FX cron" - GitHub `schedule`
  triggers only fire from the default branch. It had claimed otherwise and wrote the correction itself:
  "that is the second time I stated a scheduling consequence without checking the mechanism, and it is
  the same prose-as-evidence failure I flagged in the session record."
- **PR #1065 merged** (HML pre-registration + collateral treatment)
- **Doc lint refused the amendment**: 9 missing headings, ~31 bare numbers, so it drafted in `/tmp`
  instead of committing a failing doc to the shared tree

## Known dependency gap (blocks the FX verdict)

`tools/fx_cost_sampler.py` lazily imports `tools.fx_meanrev_research.run_in_strategy_chain`, and **that
module does not exist on main**. The runtime guard ("no chdir -> dry-run") landed, but the measurement
path is not exercised, so the chained strategy re-run will record `CHAIN_FAILED` rather than a verdict.
Reported, not fixed - restoring it would mean pulling another agent's tools from a branch that was
deliberately refused.
