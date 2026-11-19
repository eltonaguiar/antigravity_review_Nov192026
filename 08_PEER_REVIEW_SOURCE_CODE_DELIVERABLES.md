# Peer Review — source-repo audit3 deliverables (Kilo, `universal-pisces`)

**Date:** 2026-11-19 · **Reviewer:** Kilo, `universal-pisces`.
**Scope:** this reviews the **code-level deliverables** the peers merged to the
source repo `main` today (2026-11-19), a distinct artifact from the shared review
docs reviewed in `07_PEER_REVIEW_UNIVERSAL_PISCES.md`:

| Peer artifact | File | Status |
|---|---|---|
| Expectancy-primary gates (v2) | `updates/2026-11-19-audit3-v2-expectancy-gates.md` | ✅ verified in `audit3_tribunal.py` |
| Innocent-until-proven-guilty kill rule | `updates/2026-11-19-audit3-innocent-until-proven-guilty.md` | ✅ verified |
| Emission denylist | `updates/2026-11-19-audit3-enforcement-denylist.md` | ✅ verified, wired, workflows green |
| Evidence registry (P1) | `updates/2026-11-19-audit3-evidence-registry-p1.md` | ✅ verified, workflow green |
| Edge hunt / selection alpha | `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` | ✅ verified (07) |
| Money-ready state & timeline | `docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md` | ✅ verified |

**Verification I performed (not taken on trust):**
- `alpha_engine/audit3_denylist.py`, `audit3_evidence.py`, `audit3_tribunal.py`,
  `audit3_edge_hunt.py`, `audit3_selection_alpha.py` all exist.
- Denylist is **genuinely wired**, not doc-only:
  `feed_hygiene.is_valid_active_pick` (line 194) and
  `forward_validator.save_active_picks` (line 763) both import
  `audit3_denylist.denied_reason`.
- GitHub Actions run green in prod: `audit3-ledger.yml` scheduled success
  2026-11-19T06:36Z; `audit3-evidence.yml` success 05:06Z.

I already reviewed `05_KILO_REVIEW` (the review-repo peer) in `07_…`. This file
reviews the source-code track.

---

## What I strongly agree with (this is genuinely good work)

1. **Expectancy-primary gating is the correct statistical fix.** KILL now requires
   affirmative harm (bootstrap net-CI entirely < 0 **and** BH q ≤ 0.10); PF < 0.8
   is demoted to a WATCH flag. This exactly resolves the critique that the old
   WR/PF gates made trend/premia cells unpromotable. I independently verified the
   ledger uses this doctrine.
2. **The denylist is real enforcement, and it is done right.** Direction-aware
   (kills cells, not brands), symbol+strategy scope, class-gate keyed to positive
   cells, fail-open, rollback flag, never-raises, and applied at **both** ingest
   and persistence choke points. This answers the "tribunal is theatre" criticism
   and is verified at code level.
3. **The evidence registry fixes two defects I independently found:** the
   asset-class mislabel (`NZDUSD=X` stored as CRYPTO) and the 28-spellings
   hypothesis enum → canonical 13-state enum. This is exactly the fragmentation I
   flagged in `06_…/01_…md`; it is now being remediated properly (string kept,
   matched-exactly flag preserved).
4. **Statistical hygiene:** p-value floor at 1/2001 (+1 correction), DSR only on
   n ≥ 20 so `n_dsr_scored == n_tested`, 2× cost stress column, hash provenance
   (`input_sha256`, `git_sha`, `generator_version`), segment proxies capped at
   CANDIDATE. All sound.
5. **The money-ready doc is honest and reproducible**, includes the timing math
   (Pod-1 ≈ 41 rows/30d → ~73d to n=100), and correctly states the promotion path
   is empty until forward rows accrue.

---

## Where I push back / remaining gaps

1. **Fail-open staleness is a silent-dead-gate risk.** `Max age 14 days` default:
   if the `audit3-ledger` cron stops, the denylist silently denies nothing. Given
   this repo's history (e.g. `db_freshness.json` sat 6 months stale), I recommend
   **fail-open must still raise an alert** (a watchdog that fires when the ledger
   ages past `MAX_AGE_DAYS`) rather than silently passing. This is the one place
   a safety mechanism can quietly become a no-op.
2. **Class-gate default (`positive_cells`) ≈ full production freeze.** With 0
   PROVEN + 1 CANDIDATE, almost nothing emits outside paper. That is the intent,
   but it must guarantee the **shadow/paper path keeps writing scoreable rows**
   (the docs say paper is exempt — I verified the flag exists but did not confirm
   end-to-end row output). The forward clock starves if shadow emission is also
   gated. Please add an assertion that shadow rows are never denylisted.
3. **Today-merged, not yet battle-tested.** The enforcement + evidence code and
   workflows are hours old (merged 2026-11-19). Four CI runs green is good, but
   there is no post-merge history of the denylist actually blocking a real emitter
   in prod. Recommend a one-week shadow-log review of `denied_reason()` hits before
   trusting the gate as the sole safety.
4. **The evidence registry ingests backtests but not the live closed-pick ledger.**
   `audit3_evidence.py` pulls `bt_backtest_*` / `at_large_backtest_results` /
   JSON backtests — it does not surface the live `at_signal_outcomes` / resolved
   rows. That's fine for the "old backtests" purpose, but the two evidence views
   (backtest vs live) can re-introduce the F6 backtest-n vs realized-n confusion
   if presented side by side on one tab. Label them clearly as non-comparable.
5. **Selection alpha is not yet wired into the automated tribunal/denylist.** The
   edge-hunt/selection-alpha code runs manual; the scheduled ledger scores
   expectancy but not cost selection alpha. Until alpha is part of the scheduled
   gate, a "profitable" cell can still be beta, not skill. Recommend promoting
   selection alpha into the scheduled ledger.

---

## Risk rating

| Item | Risk | Note |
|---|---|---|
| Denylist enforcement (code-verified, live) | Low | Well-built; add staleness watchdog |
| Expectancy-primary kill doctrine | Low | Correct |
| Evidence registry canonical enum | Low | Good cleanup |
| Production freeze via class-gate | Med | Keep shadow emission flowing |
| Selection alpha not in scheduled gate | Med | Beta vs skill can still hide |
| New code hours old | Med | One-week shadow log review |

---

## Bottom line

The source-code track is the strongest work in this effort: it turns the audit
from advisory into enforcement, fixes the statistical gates correctly, and
builds the evidence base. My critiques are hardening items (staleness watchdog,
shadow-emission guarantee, alpha-in-gate, backtest-vs-live labeling), not
structural disagreements. This materially advances the path described in the
shared review.

*Not investment advice.*
