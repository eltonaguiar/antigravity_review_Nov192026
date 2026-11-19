# PLAN — Antigravity Financial-Prediction Recovery

**Date:** 2026-11-19
**Basis:** `FINDINGS_ROOT_CAUSE.md` + `EVIDENCE_INDEX.md` (this review)
**Goal:** turn "0 money-ready, no positive alpha" into a measurable, citable
path — starting by stopping the bleed and building the missing forward A/B harness.

This plan is deliberately a **sequencing plan, not a new-strategy plan.** The
repo's own reviewers agree the failure is *not* a missing strategy; it is cost,
exit geometry, leakage, and missing forward measurement. See
`docs/EDGE_IDEAS_BACKLOG_2026-11-19.md` (source repo) which this plan extends.

---

## Rule 0 (non-negotiable)

**No new strategy may be generated while a P0 item is open.** 700+ strategies is
a multiple-testing engine; every apparent winner dies because the p-values were
spent. Pre-register, then test once.

---

## Phase 0 — Stop destroying value (this week; no forward clock needed)

### P0-1. Stamp gate inputs at issue time (kill the leakage) — E13
- **Why:** `wf_verdict` scores +0.96%/trade but collapses to −0.19%/trade under
  point-in-time replay because `at_issue_strat_fwd_wr` is on 6% of rows.
- **Do:** write `at_issue_*` for 100% of rows at pick creation; re-run
  `alpha_engine/audit3_edge_hunt.py`.
- **Kill criterion:** if PIT replay still shows no discrimination after 100%
  stamping, retire `wf_verdict` as a gate.
- **Files:** `alpha_engine/audit3_edge_hunt.py`, the pick writer that stamps
  `at_issue_strat_fwd_wr` (see `audit_trail/pick_schema.py`), `audit_trail/`.

### P0-2. A/B the exit geometry — the user's core ask — E14
- **Why:** crypto LONG loses −0.44%/pick vs *holding the same coin* with median
  TP +2.50% / SL −1.50%. The exits cut winners short. This is the "switch the
  variable and see if we'd have made money" test, and it does not exist yet.
- **Do:** build a forward, point-in-time A/B harness that, for the **same signal**,
  emits two paper legs side-by-side:
  - **Leg A (control):** current TP/SL geometry.
  - **Leg B (treatment):** symmetric vol-scaled time exit (no early TP, trailing
    stop at k×ATR, or fixed holding window).
  - Score **selection alpha vs same-symbol hold** on realized rows only.
- **Existing infra to reuse, not rebuild:**
  - `whatif_scenarios`, `strategy_whatif_results`, `simulation_grid`,
    `ml_ab_tests` tables in `schema-baseline.sql`.
  - `strategy_variation_generator.py` (genetic recombination of DNA).
  - `audit_trail/universal_pick_resolver.py` (resolution), `trade_geometry.py`.
- **Kill criterion:** if Leg B does not clear alpha > 0 in two regimes, stop
  emitting the cell entirely.
- **Note:** branch `add-strategy-variable-tracking` exists but is empty of real
  work — this item is the actual implementation that branch name promises.

### P0-3. Backfill FX or retire it — E11
- **Why:** 211 forex picks have **zero** computable alpha (`fx_prices` ends
  2026-02-09; `AUDJPY=X` never maps to `AUDJPY`; `EURUSDT` mis-filed as FOREX).
- **Do:** backfill 2026-02→11 daily bars; map `XXXYYY=X`/`XXX-YYY` → `XXXYYY`;
  treat any `USDT` quote as CRYPTO.
- **Kill criterion:** < 90% coverage after backfill → declare forex unmeasurable,
  stop emitting it.

### P0-4. Hold-benchmark pilot — E12 (starts the 90-day clock immediately)
- **Why:** the only test that can answer "is the entry logic worth anything" is
  comparing the pick to holding the same instrument.
- **Do:** emit pick **and** same-symbol hold side by side in paper for a fixed
  window; promote only on alpha CI > 0.
- **Files:** extend `alpha_engine/audit3_selection_alpha.py` into a live pilot.

---

## Phase 1 — Agree the denominator (this week, unblocks every page)

### P1-1. One canonical resolved view — A2
- **Why:** `/audit` vs `/audit3` disagree (ETF WR 1.9% vs 43.1%). Two kill lists
  (42 vs 11) share one name. Until these reconcile, no tile is loadable.
- **Do:** `resolved_closed_picks_net` (already in `schema-baseline.sql`) queried
  by both surfaces, with exclusions explicitly flagged.
- **Files:** `alpha_engine/resolved_closed_view.py`, `audit_trail/dashboard_generator.py`,
  `audit_dashboard/index.html`, `audit_dashboard/audit3.html`.

### P1-2. Excluded-cohort panel — A1
- **Why:** audit3 judges 21.4% of the book (3,500/16,330) and 46% are
  integrity-excluded without explanation.
- **Do:** publish counts + reasons; state "judging X of Y picks" in the header.
- **Note:** partially done in #893; verify it renders on live `/audit3`.

### P1-3. Selection alpha as the per-class headline — A4
- **Why:** PF and WR are the wrong headlines (EQUITY 60% WR but PF 0.97 is not
  skill — it harvests small wins and eats tail losses).
- **Do:** surface selection-alpha-vs-hold per class; demote raw PF/WR.

---

## Phase 2 — Prove one premium (2–6 weeks, max 2 concurrent)

Choose **one** (do not parallelize both):
- **E8** Vol-targeted TSMOM across liquid futures/ETFs (strongest century-scale
  evidence; crisis alpha; monthly cadence survives ETF slippage).
- **E3** Market-neutral cross-sectional crypto (333 symbols × 1h bars already in
  DB; strips beta; dollar-neutral long-top-decile / short-bottom).

Both must be **pre-registered** (confirmatory namespace), with an economic reason
and a counterparty losing money — not a decorrelated equity curve.

Promotion gates (already defined in `docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md` §3):
1. n ≥ 100 forward trades
2. net CI lower bound > 0 at **2× measured slippage**
3. IR ≥ 0.5 vs SPY at matched exposure
4. 90-day forward clock (kill checks at day 30/60 on CI-LB ≤ 0)
5. BH q ≤ 0.10 in the confirmatory family, DSR ≥ 0.95

---

## Phase 3 — Only after a P1 pod survives

- E6 Polymarket/Kalshi cross-venue + bracket arb (maker-only; taker fees 3.5–6.3%
  kill it; resolved n=1 today → build the resolver first).
- E5 meta-labelling for regime filter (must be scored on Brier calibration).
- E4 cointegration pairs (ADF/Engle-Granger rolling stability, not correlation).
- E10 PEAD on large caps (needs 500+ names and SUE data).

---

## Governance fixes (cheap, high-leverage)

- **A5** One smart-picks definition (currently `total_scored=0` vs `95 picks 68.4% WR`).
- **A6** Retire `tier2_proven_strategies` until a card is actually `alive`.
- **Thread `cumulative_trials` through `TESTING_PROTOCOL.MD` §6–§8** — the rehab
  pipeline currently resets multiplicity so each child looks like a fresh trial.
- **Add an economic-prior pre-filter to `STRATEGY_DISCOVERY_PROTOCOL.md`** — it
  screens statistics, not "why should this edge exist."

---

## Timeline (measured, not guessed)

- Pod-1 resolved **364 rows / 265 days** ≈ **41 rows / 30 days**.
- At that rate the confirmation floor takes **~73 days** of emission, then a
  **90-day forward clock** → **~5.4 months** to any money-ready verdict, on the
  optimistic branch only.
- **Decision rule written now:** if at day 90 no pod shows positive net CI-LB at
  2× slippage and IR ≥ 0.5, the finding is **"no deployable edge on available
  data"** — a successful, citable result. Freeze (don't delete) the harness; move
  budget to a ≤0.20%-fee beta core.

---

## Out of scope for this review

Implementation is for the source repo's owner + the agents already working in
isolated worktrees. This review only (a) documents the root cause and (b) provides
the sequencing. No files in `findtorontoevents_antigravity.ca` were modified.
