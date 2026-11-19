# Independent Corroboration — Kilo (worktree `universal-pisces`)

**Date:** 2026-11-19 · **Reviewer:** Kilo, from the `universal-pisces`
isolated worktree (detached at main tip `f9e6c8202a1`).
**Status:** additive corroboration of the existing review in this repo
(`00_CHARTER.md` + `02_FINDINGS/` + `05_KILO_REVIEW/`). It **confirms** the
consensus root causes and adds fresh, machine-generated evidence not yet in the
shared review, plus a short list of gaps. It edits no existing file.

## 1. Consensus confirmed (with my own direct pulls)

I re-read the live artifacts directly (not from the prior review) and the numbers
match the shared review:

| Claim | My measurement | Source |
|---|---|---|
| 0 PROVEN, 1 CANDIDATE, 10 KILL, 34 WEAK, 126 INSUFFICIENT_N | same | `audit_dashboard/data/audit3_ledger.json` → `summary` |
| Candidate = `luxalgo_confluence SHORT` (n=476, WR 54.4%, PF 1.61, net +0.72%, single-source 97.7%, discovery namespace) | same | ledger → `cells` (verdict=CANDIDATE) |
| Class verdicts: CRYPTO KILL (n=1,851, net −0.46%/trade, CI<0), COMMODITY KILL (n=55, −3.2%), EQUITY/ETF/FOREX/BOND WEAK, FUTURES INSUFFICIENT_N | same (see `01_FRESH_TRACKING_GAPS.md` for the table) | ledger → `classes` |
| No positive selection alpha; whole book net −0.188%/trade; CRYPTO LONG −0.44%/pick vs holding | consistent with `updates/2026-11-19-audit3-edge-hunt-no-positive-alpha.md` | same |
| Coverage: 3,500 / 16,330 closed scored (21.4%); valid 7,901; integrity-excluded 7,502; auto-expired 9,100 | same | ledger → `coverage` |

**Conclusion:** the shared review's core verdict — *machinery exists but there is
no promotion path and no positive measure edge today* — is accurate.

## 2. Fresh evidence added by this review (not in the shared set)

These come from artifacts I probed that are absent from the existing `02_FINDINGS`
and `05_KILO_REVIEW` write-ups. Full tables are in `01_FRESH_TRACKING_GAPS.md`.

1. **`alpha_engine/data/walkforward_results.json` (generated 2026-11-19) — the
   only current machine-scored status artifact:** 52 strategies → 0 ELITE,
   3 STRONG, 11 VIABLE, 3 MARGINAL, 35 FAILING. This is the closest thing to a
   "current strategies" ledger and it is **not** referenced by the shared review.
2. **`strategy_perf_by_class.json` (2026-11-18): 961 cells across 11 classes.**
   The highest-n cells are net-negative (`luxalgo_confluence` CRYPTO n=5,505
   +0.18%; `forex_rsi2_mean_reversion` n=1,095 −0.12%), confirming the large-N
   book is not net-positive. A few tiny high-pnl cells (n<30) are the usual
   small-sample illusion.
3. **Missing canonical files (integrity gaps):**
   - `audit_dashboard/data/dashboard_data.json` — **absent** at the canonical
     path; the audit3 source is `/tmp/audit3/dashboard_data.json`. Downstream
     readers (`dashboard_generator._hf_stats_summary`) read the canonical path.
   - `audit_trail/data/universal_resolved_picks.json` — **absent** (resolver
     output file not on disk).
   - `trading/data/strategy_registry.json` — **declared** by
     `trading/strategy_registry.py` but **never materialized**.
   - `paper_trading/data/paper.db` (+ `equity_snapshots` table) — **never
     created**; there is no persisted time-series equity curve.
4. **Hypothesis registry fragmentation:** `reports/hypothesis_registry.json` has
   ~141 ids but ~138 status values across **30+ distinct vocabularies**, with a
   duplicated archive-append tail (same ids re-scored under different verdicts).
   `audit_trail/data/hypothesis_registry.json` is an **empty stub**.
5. **Freshness kernel:** `audit_dashboard/data/db_freshness.json` is **6 months
   stale** (2026-05-23); `signal_outcomes` last resolved 2026-03-04 (121 rows,
   ~80 days stale). The resolver's *own* output file is absent (item 3).

## 3. What this adds to the shared review

- Confirms that the "no current-strategy registry" finding is not just conceptual:
  there are **two** declared-but-absent registries and a resolver-output file that
  does not exist.
- Quantifies the paper-trading tracking gap: no equity-curve persistence.
- Adds the 52-strategy walk-forward verdicts and the 961-cell per-class table as
  the freshest machine-readable status sources.

## 4. My delta recommendations (pointers into the shared plan)

These reinforce `03_VARIABLES/tunable_variables.md` and
`05_KILO_REVIEW/PLAN.md`:

1. **Declare and materialize `trading/data/strategy_registry.json`** as the single
   "current strategies" source (or delete the declaration). Right now the source
   of truth is 6+ files with incompatible taxonomies.
2. **Repair the canonical output paths:** make the pipeline emit
   `audit_dashboard/data/dashboard_data.json` and
   `audit_trail/data/universal_resolved_picks.json` to the repo (not only `/tmp`),
   so downstream readers and the evidence ledger are reproducible.
3. **Persist a paper-trading equity curve** (`paper.db` / `equity_snapshots`) on
   every close; a point-in-time `portfolios.json` snapshot is not a track record.
4. **Normalize hypothesis-registry statuses** to a single controlled vocabulary and
   remove the duplicate archive tail (the 30+ spellings make status counts
   unreliable).
5. **Make freshness green or loud:** auto-fail CI when `db_freshness.json` is
   older than a day; backfill or retire the `signal_outcomes` surface (121 rows).

*Not investment advice.*
