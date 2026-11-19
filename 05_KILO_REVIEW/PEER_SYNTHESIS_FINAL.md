# Peer-Work Synthesis (final pass) — 2026-11-19

Second review of the peers' work, run after the newest wave landed. This
consolidates the converged consensus, flags what is genuinely new, and
reconciles overlaps/discrepancies with my own `05_KILO_REVIEW/` and
`AUDIT3_NEXTGEN_ENHANCEMENTS.md`.

## What the peers added this wave (reviewed)

| File | Author | Verdict |
|---|---|---|
| `10_KILO_VANILLA_HANDSAW/FINDINGS_MEASURED.md` | vanilla-handsaw | **Excellent** — measured, not recalled; adds new evidence (below) |
| `02_FINDINGS/peer_worktree_review.md` | peer | Reviews *other* worktrees (quant-audit, copilot); surfaces the stop-fill finding |
| `12_AUDIT3_REVIEW_NEXTGEN.md` | universal-pisces | Superset of my audit3 enhancements; 5 main + 6 small fixes |
| `11_AUDIT2_SPEC_CONSOLIDATED.md` | universal-pisces | Merges competing audit2 specs; Tier A/B/C pods + measures + page rules |
| `06_AUDIT2_PAGE/` (audit2.html + sidecars) | peer | A standalone audit2 page **prototype** already built |
| `06_IMPLEMENTATION_STATUS.md` | peer | Two gaps already partially built (`forward_observations.py`, `resolved_closed_view.py`) |

## The converged consensus (all peers + me agree)

1. **0 money-ready / 0 PROVEN / no positive selection alpha.** Multiple independent
   counts: audit3 0 PROVEN + 1 CANDIDATE; quant-audit **0/166 cells** pass the full
   gate (single-source gate alone eliminates all 166); per-class ALL PF 0.895, t=−2.53.
2. **The cause is cost/exit/data, not missing signal.** Fixed TP/SL cuts winners
   short; crypto LONG −0.44%/pick vs hold; no forward-observation ledger.
3. **Data debt is the floor.** 409 tables, 5+ pick ledgers, ghost rows, stale
   snapshots, 63% of picks never resolve.
4. **The fix is stop-the-bleed + forward measurement, not another strategy.**

## Genuinely new findings from the peers (not in my earlier files)

1. **Crypto stop-fill overshoot = 98.8% of the crypto class loss** — the single
   most actionable fact in this review. Planned risk 1.919% vs realized loss 2.990%
   on stopped trades → +1.071pp overshoot/trade, +828pp total vs a −837.8pp class.
   Fixing the fill model alone moves crypto PF 0.768 → **≈1.00**. This reframes
   crypto from "no signal" to "the signal is drowned by a mechanical fill bug".
   (source: `02_FINDINGS/peer_worktree_review.md` §1.3, `quant-audit`
   `console_r_multiples.txt`.)
2. **Blocklist is bypassed** — `cohort_reconciliation.json`
   `blocklist_bypass.flagged=true`, **165** retired-strategy picks still emitting.
3. **Ghost rows = 22,947**, not the hard-coded 0/GREEN on the audit page; a single
   MEMECOIN `meta_strategy` DOGEUSDT entry stamped n=3,569 with `distinct_entries=1`.
4. **Reproducibility gap** — `dashboard_data.json` (44 MB) is not in git; the
   `/audit` headline cards cannot be re-derived from any committed artifact.
5. **Multiple-testing is uncorrected on the live surface** — 658 distinct
   strategies; 21 clear Bonferroni but **all 21 are the single-source artifact
   cluster**; BH-FDR gates disabled; DSR `n_trials=80` vs true 658 (under-corrects).

## Reconciliation of my audit3 next-gen vs the peer's (12_)

They overlap on the top items; neither list is a subset of the other. Merged,
non-duplicate priority list:

| # | Fix | My file | Peer 12_ |
|---|---|---|---|
| 1 | Selection alpha as a **gate** (not optional/display) | P0-1 | E1 |
| 2 | DSR `n_trials` = true global N (658), not tested cells | P0-2 | — (in 10_F) |
| 3 | Independent denylist staleness watchdog | P0-3 | F1 |
| 4 | Full-book reconciled ledger (not 21.4% slice) | P1-6 | E2 |
| 5 | Power-based `required_n` per cell | P2-8 | E3 |
| 6 | Forward-observation clock + shadow emission | P2-8 | E4 |
| 7 | **2×-cost stress → hard gate** (I called it report-only; peer promotes it) | — | E5 |
| 8 | Log `denied_reason()` hits (verify it works) | — | F2 |
| 9 | Pin canonical path, never emit `/tmp` in ledger | — | F3 |
| 10 | Single bootstrap engine across surfaces | — | F5 |
| 11 | Pre-registration hard-fail (not flag) | — | F6 |

## Discrepancies that must be resolved before anything ships

1. **`forex_rsi2_mean_reversion` n-count conflict.** `11_AUDIT2_SPEC_CONSOLIDATED.md`
   lists it as Tier A "LIVE n=523, cum +34.6" (`per_asset_class…:124`); but
   `walkforward_results.json` scores it **n=24** (STRONG). Meanwhile forex has **zero
   computable selection alpha** (`fx_prices` ends 2026-02-09). This is either
   backtest-n vs realized-n (the F6 trap) or two different tables. Do **not** ship it
   as a Tier-A candidate until the n=523 source is identified and reconciled.
2. **Denylist "wired" vs "bypassed" timing.** `universal-pisces` verified the denylist
   is wired at `feed_hygiene.py:194` / `forward_validator.py:763` (merged today);
   `vanilla-handsaw` found 165 blocklist bypasses in `cohort_reconciliation.json`.
   Most likely the bypass snapshot predates today's wiring. Needs a re-run of the
   bypass check against the post-deny-list pipeline before either claim is cited.
3. **EQUITY verdict strength.** Peer review calls EQUITY the one positive-OOS class
   (+0.608 Sharpe); quant-audit says +238pp but t=1.52 (not significant). Both agree
   it is the only *candidate* class — treat as candidate, not a win.

## Bottom line

The peer work is high-quality and **converges** on my verdict; it adds one
mechanically decisive fact (stop-fill overshoot ≈ the entire crypto loss) and
closes the loop on audit3 (the 12_ list is the merged next-gen plan; adopt E5/F2/F3/
F5/F6 alongside my P0-1/P0-2/P0-3). The two items to verify before citing anywhere:
the `forex_rsi2` n-count and the denylist-bypass timing.

*Not investment advice.*
