# Review — the four `.kilo/worktrees/` review sessions (2026-11-19)

The four worktrees `universal-pisces`, `witty-fight` (self), `lapis-chronometer`,
`vanilla-handsaw` are **all clean checkouts at the same main tip**
(`f9e6c8202a1`): zero uncommitted/untracked changes and zero local-only commits. They are
session directories, not deliverable containers. The peer output from those sessions landed
in **this** review repo (`antigravity_review_Nov192026`):

| Folder | Author worktree | What it is |
|---|---|---|
| `05_KILO_REVIEW/` | `lapis-chronometer` | Independent confirming review: findings F1–F7 + evidence index + A/B-harness plan |
| `06_CORROBORATION_UNIVERSAL_PISCES/` | `universal-pisces` | Independent re-verification of every shared-review number |
| `07_PEER_REVIEW_UNIVERSAL_PISCES.md` | `universal-pisces` | Peer review of the shared review (`01–05`) |
| `08_PEER_REVIEW_SOURCE_CODE_DELIVERABLES.md` | `universal-pisces` | Peer review of today's merged source-code audit3 deliverables |
| `09_AUDIT2_CONTENT_RECOMMENDATION.md` | `universal-pisces` | audit2 content recommendation |

## What the peers independently established

**Converged with my own review (all agree):**
- **No positive selection alpha anywhere** — F1 vs `audit3_selection_alpha.py`:
  whole book −0.296% (CI [−0.621, +0.053]); **CRYPTO LONG −0.442%** (CI [−0.892,
  −0.085], excludes 0, negative); **ETF LONG −0.272%** (CI [−0.504, −0.037]).
  "Crypto shorts win, longs lose" is market beta counted once, not skill.
- **Loss is exit-geometry + cost, not signal.** ETF slippage = 234% of per-trade
  PnL; fixed TP/SL cuts winners short.
- **The walk-forward gate is a leaky rear-view mirror** (F3): `wf_verdict` +0.96%/trade
  raw collapses to −0.19%/trade under point-in-time replay; `at_issue_*` stamped on only
  6% of rows (215/3,500). Root fix: stamp `at_issue_*` at creation.
- **Tracking is fragmented** (F4): 409 tables, 5+ pick ledgers, contradictory surfaces.
- **Bottom line:** stop generating; **stop-the-bleed + forward measurement**, not another
  strategy.

**Valuable nuances the peers add (I adopt):**
1. The ETF "contradiction" (1.9% vs 43.1% WR) is a **denominator mismatch / incomparable
   surfaces**, not necessarily a data bug — wording should be "incomparable denominators,"
   not "one is wrong." (The A2 canonical-view fix stands.)
2. The ML "healthy consensus" 50.6% WR is a **backtest of only 81 picks** — tiny n, itself
   multiple-testing fragile.
3. **Killing emission is in tension with needing forward data** — you must keep a
   shadow/negative-control emitting to feed the forward ledger audit3 needs. (Good catch;
   I'll fold this into the forward path.)

## Source-code track (08) — what the merged audit3 deliverables actually verify

- Expectancy-primary gating + innocent-until-proven-guilty kill rule — verified in
  `audit3_tribunal.py`.
- **Emission denylist is genuinely wired** (not doc-only): `feed_hygiene.is_valid_active_pick`
  and `forward_validator.save_active_picks` both import `audit3_denylist.denied_reason`;
  direction-aware, symbol+strategy scope, fail-open, rollback flag, applied at ingest AND
  persistence. GH Actions green (`audit3-ledger.yml` 06:36Z, `audit3-evidence.yml` 05:06Z).
- Evidence registry fixes the asset-class mislabel and the 28-spellings hypothesis enum
  → canonical 13-state.
- Statistical hygiene: p-value floor 1/2001, DSR only on n≥20, 2× cost stress, hash
  provenance.

## Net assessment

The four worktrees are **clean and non-destructive**: no stray edits in the source tree, no
conflicting local commits. Their substantive output is high-quality, well-evidenced, and
converges with every independent review. The one genuinely new, actionable insight to fold
into the forward plan is the **shadow-control emission** requirement (keep emitting a
negative/shadow cohort so the forward ledger accrues) — resolving the tension between
"pause emission" and "need forward data."

*Not personalized investment advice.*
