# Findings — Review of the agent work on the audit2 & audit3 pages

The user flagged that an agent had been working on an "audit2" page and an "audit3" page.
This note reviews that work as found in the repo (branches, PRs, docs), and reconciles it
with the live surfaces.

---

## 1. audit3 — real, active, agent-built lineage

audit3 is not a static page; it is the product of an extended, well-documented build over
~20 pull requests (PRs #884–#905, Nov 2026). The lineage, oldest → newest:

| PR / branch | What it added |
|---|---|
| #884 `audit3-kill-tribunal` | Quant kill-tribunal **ledger**, page, and independent refresh job |
| #885 `audit3-innocent-until-proven-guilty` | Doctrine: require proven harm before killing; section-by-class matrix |
| #886 `audit3-evidence-p1` | Register backtest evidence the tribunal could not see |
| #887 `audit3-evidence-doc-counts` | Measured evidence-registry counts |
| #888 `audit3-edge-hunt` | Prove the ledger has **no positive selection alpha** |
| #891 `docs-audit-surface-review` | Merged doc `docs/AUDIT_SURFACE_REVIEW_2026-11-19.md` (the surface review) |
| #893 `feat/audit3-coverage-alpha` | State share of book judged; lead classes with selection alpha |
| #895 `feat/audit3-v2-expectancy-gates` | Test **expectancy** instead of win rate; stop leaking DB host |
| #896/#897 bootstrap p-floor | Fix over-strict bootstrap p assertions |
| #898/#900 `emission-denylist` + writer | Enforce KILL cells at **emission**, split multiplicity, unify symbols; apply denylist at the writer |
| #901 `class-gate-pods` | Enforce class kills behind a stronger bar; register pods; guard the gate |
| #902/#903 `docs/audit3-v3-delta`, `docs-audit3-feedback-v3` | v3.1 feedback rewrite (39.5 KB) — **OPEN/unmerged** |
| #904 `feat/audit3-canonical-denominator-and-gates` (merged) | One declared denominator; gates on by default; dead tiles out |
| #905 `feat/wr-semantics-measured-cost-timeline` (merged) | WR-means-class rows; measured cost in audit3; one smart-picks def |

### 1.1 What the agent got right (strengths — keep)

- **Statistically honest core:** pre-declared method, Wilson CIs, bootstrap net-expectancy
  CI (2,000 seeded resamples) after slippage, BH-FDR, split-half stability, concentration
  caps, "innocent until proven guilty" doctrine, kill rule = net-CI entirely < 0 **and**
  BH harm q ≤ 0.10. This is genuinely better statistics than the main page.
- **Conservative kills where it matters:** audit3's flat slippage constants sit *above*
  measured values for CRYPTO/ETF/BOND/EQUITY/FOREX, so its kills are not artifacts of cost
  overestimation (verified in `dashboard_data.json.slippage_validation`).
- **Directionally-correct crypto call:** the walk-forward panel backs the CRYPTO LONG
  kills — OOS Sharpe **−2.077 across 32 folds** (EQUITY +0.608 on 33 folds). The kills
  were not a spurious recent-window artifact.

### 1.2 What is still open (gaps the agent itself documented, all verified)

| Issue | Detail |
|---|---|
| **Scope** | judges **21.4% of the closed book** (3,500/16,330 rows, 246-day window); 7,502 integrity-excluded (46%) and 9,100 auto-expired are analysed on **neither** page. A0-PnL expiry is not a neutral observation (3,467 expired-zero-PnL rows). |
| **Denominator disagreement** | `/audit` and audit3 disagree on the same classes (ETF n=52 WR 1.9% vs n=584 WR 43.1%; EQUITY n 3× diff; COMMODITY opposite signs). Until fixed, no per-class conclusion loads. |
| **G1 mis-specified** | `WR > 50%` binomial gate can never certify a trend/premia cell and misjudges the EQUITY class in reverse. Expectancy CI (G2) should be the gate. |
| **Multiplicity** | BH pooled across all cells mixes confirmatory + discovery; promotion requires a separate confirmatory namespace. |
| **Selection bias unpriced** | grade A/score≥60 and elite_grade B CRYPTO segments overlap (A⊂B) from a 65-segment screen; nominal 95% CIs are optimistic post-selection; require SL-wins-ties labels before nomination. |
| **Stability weak** | split-half only; add rolling monthly cohort check. |
| **Provenance** | ledger `source` leaks `/tmp/audit3/dashboard_data.json`; should embed commit SHA + input hashes. |
| **Not wired to emission** | the tribunal's output is a page, not a denylist the scanner reads (PR #6 allowlist historically had 0 call sites). Some emission enforcement now exists (#898/#900, #901) but the full "KILL cells → auto-denylist + PROVEN_T2 forward-clock promotion path" is still absent. |
| **No promotion path** | `PROVEN_T2` has no forward-clock route (30/60/90d, size cap), so nothing can graduate. |

### 1.3 The v3.1 feedback rewrite (PR #903) — the sharpest single artifact

`AUDIT3_FEEDBACK_2026-11-19.md` v3.1 (39.5 KB, **on the open PR #903 / branch
`docs-audit3-feedback-v3`**, not yet merged to main) is the most complete review in the
repo. It cross-checks audit3 against the merged surface-review (PR #891), adds a measured-
slippage table, the OOS Sharpe table, the podcast-tile contradictions, and a P0/P1/P2
priority list. Key additions over v1:
- **Measured slippage** (per-strategy where available, class fallback): ETF edge is
  **234% consumed by slippage** (only monthly-cadence rotation survives); FUTURES and
  COMMODITY flat constants are *below* measured, so audit3's futures verdicts are **not**
  conservative and should be adjusted; `luxalgo_confluence` book-wide measured slippage
  0.10% = 2,175.8% of per-trade PnL — the SHORT cell (+0.67%/trade) must clear 2×-measured
  slippage before nomination.
- **Reordered pod priority:** EQUITY first (only positive OOS Sharpe on real folds), not
  CRYPTO.
- **New verified defects:** smart-picks tile contradiction (`total_scored=0` vs snapshot
  68.4% WR); dead `tier2_proven_strategies` panel under a "proven" label; kill-list
  reconciliation (kill_switch 42 vs audit3 11, share only 1 name); gate pressure
  (134 → 15 active, 119 filtered; PCG5 rejects 89%).
- **Spec status correction:** `docs/FINANCE_DB_SCHEMA_SPEC.md` is on main (PR #890), not
  on a branch.

---

## 2. audit2 — no page ever existed; superseded by audit3

- **There is no `audit2.html` anywhere in git history.** Live `https://findtorontoevents.ca/audit2/`
  returns **404**. The only surviving audit2 artifacts are helper scripts:
  - `score_audit2.py` (repo root) — an audit *helper* that flags `elite_score=0` for
    high-confidence ML picks (used by scoring automation, not a page).
  - `tmp/check_audit2.py`, `tmp/db_audit2.py` — ad-hoc audit scripts.
- The "audit2" concept (a second audit view) was effectively **superseded by audit3**.
  The audit3 lineage above *is* the continuation of that effort under a stricter statistical
  design. No separate audit2 page work exists to review beyond the legacy scripts.

---

## 3. What this changes in the overall picture

- The evidence for the "0 PROVEN / 1 CANDIDATE" conclusion is now **triple-confirmed**:
  the audit3 ledger, the merged surface-review (PR #891), and the v3.1 feedback (PR #903)
  all agree.
- The **highest-leverage engineering fix** (from both the surface review and v3.1) is
  **A2: one canonical `resolved_closed_picks_net` view** that both `/audit` and audit3
  query — because the two surfaces currently can't even agree on the denominator, let alone
  a verdict.
- The **single most decision-relevant table** (walk-forward OOS Sharpe) exists on neither
  page's headline; it points squarely at **EQUITY** (+0.608, 33 folds) as the only class
  with positive out-of-sample statistics — not CRYPTO (60% of volume, −2.08).

*Not personalized investment advice.*
