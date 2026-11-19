# audit3 — Next-Gen Enhancements & Fixes (2026-11-19)

**Scope:** deep review of the audit3 machinery (`alpha_engine/audit3_*.py`,
`audit_dashboard/audit3.html`, `.github/workflows/audit3-ledger.yml` +
`audit3-evidence.yml`, `tools/audit3_denylist_health.py`). Ranked fixes below.
What is already correct is listed first, so the enhancements are scoped to the
actual gaps, not re-work.

---

## What audit3 already gets right (do not re-do)

- **Gates G0–G7 are sound:** sample floor, expectancy-primary (WR demoted to
  descriptor), BH multiplicity, DSR (G4), stability, concentration, cost realism
  (`audit3_tribunal.py` lines 400–435 rendered in `audit3.html`).
- **Denylist is real enforcement**, direction-aware, applied at ingest
  (`feed_hygiene.py:194`) and persistence (`forward_validator.py:763`), fail-open.
- **Selection alpha is now computed *and displayed* in the scheduled ledger**:
  `audit3-ledger.yml` lines 89–97 run `audit3_selection_alpha.py` and pass
  `--alpha`; the page renders "Selection alpha vs hold" as the class headline.
- **Provenance hashes** (`input_sha256`, `git_sha`, `generator_version`),
  coverage denominator, doctrine, and the "innocent until proven guilty" rule.

---

## P0 — Correctness (before any new strategy)

### 1. Make selection alpha a **gate**, not a display column  ← highest value
- **Today:** `audit3_tribunal.py` stores alpha as a cell field (line 1070) but
  the verdict logic (lines 775–785) tests **net expectancy only**
  (`boot.get("mean")`). A cell that is profitable purely because the underlying
  rose (beta) can still reach CANDIDATE/PROVEN_T2.
- **Fix:** add **G8 = selection alpha**: a cell may not reach PROVEN_T2 (and
  CANDIDATE should carry a `beta_dominant` flag) unless its selection-alpha CI
  is > 0 against direction-adjusted hold. This is the one gate that separates
  "skill" from "market beta", and it is already measured — it is just not used.
- **Evidence:** edge-hunt showed whole-book alpha −0.296% while EQUITY's *gross*
  PF was positive; the two tell opposite stories.

### 2. DSR `n_trials` must be the **global** trial count, not "tested cells"
- **Today:** `audit3_tribunal.py` line 25 — "`n_trials = tested cells`" (45 in
  the current ledger).
- **Fix:** feed a global counter (700+ strategies ever tried, across every
  historical run) into `deflated_sharpe`. A cell that clears DSR at n=45 fails
  at n=700. This is backlog item **E1** and the single most understated
  multiplicity correction in the system.
- **Consequence:** on the true count, the single CANDIDATE
  (`luxalgo_confluence` SHORT, n=476) will very likely fail DSR — which is the
  correct, if painful, answer.

### 3. Independent denylist-staleness watchdog (not inside the same cron)
- **Today:** `tools/audit3_denylist_health.py` runs *inside* `audit3-ledger.yml`
  (line 121). If that cron stops, the health check stops with it — the denylist
  then fails open after `MAX_AGE_DAYS` (14) **silently**.
- **Fix:** move the health assert to a **separate** scheduled job (or the
  existing `db-freshness-guardian.yml`) so a dead `audit3-ledger` cron is itself
  a loud failure. This repo's history (`db_freshness.json` 6 months stale) is the
  proof this is not theoretical.

---

## P1 — Measurement depth

### 4. Stamp gate inputs at issue time (E13) — kill the last leak
- `at_issue_strat_fwd_wr` is present on **215/3,500** rows (6%); `strat_fwd_wr`
  fills in later, so the walk-forward-derived gate input partly knows the answer.
  Until 100% stamped, `wf_verdict` cannot be a gate.

### 5. Extend selection-alpha coverage (backfill price tables)
- Selection alpha prices **2,213/3,500** rows. Unpriced: FOREX (211), BOND (34),
  COMMODITY (55), FUTURES (4). `fx_prices` ends 2026-02-09 and `AUDJPY=X` never
  maps to `AUDJPY` (E11). Until backfilled, FOREX/COMMODITY verdicts are
  "unknown", not "safe".

### 6. Re-audit the excluded cohorts
- audit3 judges 3,500/16,330 (21.4%); **7,502 integrity-excluded (46%)** and
  **9,100 auto-expired** are quarantined with no re-audit path. Excluding half
  the book is a selection decision; add a periodic re-derive of those cohorts.

---

## P2 — Governance / completeness

### 7. Promotion → emission allowlist (mirror of the denylist)
- The denylist blocks KILL cells, but a pre-registered pod that reaches PROVEN_T2
  has **no positive wiring** to a production size cap. The page's "only pipeline
  that can promote anything" card describes the path; nothing in code turns a
  PROVEN_T2 into a sizeable emission. Add a `promoted` allowlist + size cap
  (≤1% NAV/trade) keyed off `reports/audit3_confirmatory.json`.

### 8. Forward-observation table + shadow-emission guarantee
- `docs/MONEY_READY_STATE_AND_TIMELINE_2026-11-19.md` states the forward clock
  "does not exist yet". The class-gate default (`positive_cells`) is ≈ a full
  production freeze; **guarantee shadow/paper rows keep writing for every cell,
  including KILL cells**, or the forward ledger starves and no pod can ever clear.

### 9. Evidence registry: label backtest vs live as non-comparable
- `audit3_evidence.py` ingests `bt_backtest_*` / `at_large_backtest_results` but
  not the live closed-pick ledger. Side-by-side on the Evidence tab this can
  re-introduce the F6 backtest-n vs realized-n confusion. Label the two cohorts
  explicitly, or split tabs.

---

## One-line recommendation

The audit3 scaffolding is genuinely strong; the three fixes that change
decisions are **P0-1 (alpha as a gate)**, **P0-2 (true-n DSR)**, and **P0-3
(independent watchdog)**. Everything else is depth or hygiene.

*Not investment advice.*
