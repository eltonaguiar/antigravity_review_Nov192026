# Page Review — /audit2 and /audit3 (2026-11-19)

**Scope:** review of the two pages an agent was reportedly working on — the
"Statistical Edge per Asset Class v2" dashboard and the "Quant Kill Tribunal" —
assessed for (a) what it is, (b) whether it has live data, (c) whether it is
correct and deployed, and (d) how the two reconcile.

---

## TL;DR

- **audit3 is the honest, current, wired scoreboard.** It fetches live JSON at
  runtime, leads with selection alpha, states its denominator, and its kill
  verdicts now actually block emission.
- **audit2 (v2) is a stale, hard-coded dashboard frozen at 2026-05-16.** It bakes
  numbers into JS, has a "refactor to fetch live" TODO that was never done, is
  not referenced by any deploy workflow, and shows class verdicts that
  **directly contradict** audit3.
- **A reader hitting both URLs sees opposite conclusions** about CRYPTO, EQUITY,
  ETF, and COMMODITY. That is the single biggest remaining trust problem on the
  audit surface.

---

## 1. /audit3 — "Quant Kill Tribunal" (`audit_dashboard/audit3.html`)

**Files:** `audit_dashboard/audit3.html` (645 lines) → deployed to `/audit3/index.html`;
`audit_dashboard/data/audit3_ledger.json` (276 KB); `audit_dashboard/data/audit3_evidence.json` (2.5 MB);
workflow `.github/workflows/audit3-ledger.yml` (6-hourly cron `23 */6 * * *`), `.github/workflows/audit3-evidence.yml`.

**What it is:** a static single-file tribunal that renders 9 tabs — Overview,
Kill Tribunal, Strategy Cells, Symbols, Sections×Class, Source Families,
Evidence Registry, Hypotheses, Method & Limits — from two client-side JSON fetches
(`fetch('audit3_ledger.json', {cache:'no-store'})`, same for evidence).

**Current state (ledger summary, live build):**

| Metric | Value |
|---|---|
| rows scored | 3,500 |
| cells tested / total | 45 / 171 |
| PROVEN_T2 | 0 |
| CANDIDATE | 1 |
| WEAK (no claim) | 34 |
| KILL | 10 |
| INSUFFICIENT | 126 |
| kill classes | 2 |
| symbol kills | 11 |

**Strengths (verified in source):**
- **Selection alpha is the headline** — PF is *demoted* and greyed; the page
  explains why (`audit3.html` lines 326–364).
- **Denominator stated:** a "What this ledger does *not* score" card renders
  `coverage.excluded_cohorts`, `row_drops`, and `resolver_anomalies` (lines 366–399),
  so the "21.4% of the book" fact is on the page.
- **Provenance + doctrine + multiplicity** are rendered (Method & Limits tab).
- **Honest null handling:** no-data case renders "Not enough resolved picks to
  test anything", not a fabricated table.

**Correction to the peer review:** the claim "the tribunal is not wired to block
emission (output is a web page)" is **now stale**. As of main tip `1cd4f6527ee`:

- `alpha_engine/audit3_denylist.py` — the read path (`denied_reason(pick)`),
  direction-aware, class-kills-as-stronger-bar, fail-open.
- Called from the emission path:
  - `alpha_engine/feed_hygiene.py:190` — "audit3 kill tribunal … a KILL cell is a
    denylist entry".
  - `alpha_engine/forward_validator.py:760` — "never persist a pick the tribunal
    proved [harmful]".
- `tools/audit3_denylist_health.py` — fails CI loudly if the denylist is not
  actually armed/recent/carrying kills.

So audit3's kill verdicts are no longer theatre; they gate persistence.

**Deployment:** `audit3-ledger.yml` uploads `audit3.html → /findtorontoevents.ca/audit3/index.html`
and the ledger JSON to `/audit3/audit3_ledger.json` (FTP; warns if credentials absent).
Deliberately independent of `audit-dashboard.yml` (own concurrency group, no push trigger).

---

## 2. /audit2 — "Statistical Edge per Asset Class — v2" (`audit_dashboard/v2/index.html`)

**File:** `audit_dashboard/v2/index.html` (1,136 lines), Chart.js + Inter font,
dark "Kimi UI" shell. Title: "Statistical Edge per Asset Class — v2".

**Critical problems:**

### P1 — Data is baked in, not fetched (6 months stale)
`REAL_DATA` is a hard-coded JS constant at line 827, stamped:
```
// Generated at: 2026-05-16T06:07:50.128053+00:00
```
The page itself carries the unfinished refactor note (lines 796–801):
> "It reads from `dashboard_data.json` which is already refreshed hourly …
> refactor to `fetch('/audit/data/dashboard_data.json')` for live pulls."

That refactor was **never done**. The numbers are frozen at May 2026.

### P2 — The baked numbers contradict audit3 on the same classes

| Class | audit2 (baked, 2026-05-16) | audit3 (live, 2026-11-19) |
|---|---|---|
| CRYPTO | PF **1.35**, WR 47.2%, `sizing_allowed: true`, Kelly 7.5% | PF 0.72, **KILL**, selection alpha **−0.44%/pick** |
| EQUITY | PF **1.65**, "T2 met (PF=1.56, WR=51.5%)", **INVEST** | alpha-neutral (+0.11%, CI spans 0), no positive alpha |
| COMMODITY | "**T1-candidate**", z=+4.626, **INVEST-WITH-CAVEAT** | **KILL class**, −3.17%/trade |
| ETF | OOS Sharpe **9.184**, "Near-T2, INVEST-LIMITED" | selection alpha **−0.27%/pick**, slippage = 234% of PnL |

audit2 tells a reader CRYPTO/COMMODITY are sizeable; audit3 says they are proven
harmful. Both pages are live-facing. This is a live contradiction, not a stale-vs-
fresh nuance — the two surfaces disagree on the *sign* of the edge.

### P3 — No deployment path
`grep` for `audit2` / `v2/index` across `.github/workflows/*`, `tools/deploy_audit_files.py`,
and manifests returns **nothing**. The file is committed but not referenced by any
deploy step; its last commit is an `auto: signal integrator report` (`8d61be0f275`,
2026-11-18) — i.e. it was dragged in by an auto-commit, not built/deployed by a
dedicated "audit2" workflow. Either `/audit2` is served from a path this review
could not trace, or the page is effectively orphaned.

### P4 — Partially self-aware, but not enough
The page *does* carry a "Kimi synthetic vs real" comparison table (lines 697–786)
that calls the Kimi `edge_summary.json` Sharpe/PF "fiction" and correctly flags
FOREX "DO NOT TRADE: PF=0.86". But its own "real" column is the same stale baked
data in P2, so the page refutes one source of fiction while displaying another.

---

## 3. Reconciliation verdict

| Question | Answer |
|---|---|
| Which page has data? | **audit3** (live-fetched, 3,500 scored rows). audit2 has frozen May data. |
| Which page is trustworthy? | audit3 — it states its denominator, leads with selection alpha, and its kills gate emission. |
| Which page is deployed? | audit3 is (FTP to `/audit3/`). audit2 has no discoverable deploy path. |
| Do they agree? | **No.** Opposite signs on CRYPTO/COMMODITY/ETF. |

## 4. Recommended actions (fold into `PLAN.md`)

1. **Retire or re-point /audit2.** It cannot stay live next to audit3 while
   disagreeing on the sign of CRYPTO/COMMODITY. Minimum: banner "stale, superseded
   by /audit3" and link; better: 301/302 → `/audit3/`.
2. **If /audit2 must survive,** do the refactor its own TODO promises — fetch
   `dashboard_data.json` at runtime (or better, consume the canonical
   `resolved_closed_picks_net` + `audit3_ledger.json`), and never bake class
   verdicts.
3. **One definition of "sizeable/tradeable"** across surfaces — audit3's
   `KILL`/`CANDIDATE`/`PROVEN_T2` is the only defensible vocabulary; audit2's
   `T1/T2/Kelly` tiers predate beta-separation and must not be shown unqualified.
