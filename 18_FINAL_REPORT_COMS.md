# FINAL REPORT — audit3/audit2 consolidation, deploy & monitoring

**Author:** Kilo (worktree `universal-pisces`) · **Date:** 2026-11-19
**Merged:** PR #910 → `main` (`dc788e372b4`)
**Live:** https://findtorontoevents.ca/audit3/ · https://findtorontoevents.ca/audit2/

---

## 1. What shipped (summary)

### audit3 — gates and evidence
- **2×-cost stress is a required gate** for `PROVEN_T2`/`CANDIDATE` (an edge that
  dies at doubled slippage is a cost assumption, not skill). Live rebuild showed
  no cell changed today (the only candidate survives at 2× CI +0.28).
- **Per-cell `required_n` + `mde_pct`** (80% power at the cell's observed effect),
  so "n≥100" now has an effect-sized number behind it (candidate: `required_n=196`).
- **Selection-alpha gate**: a confirmatory cell whose class alpha CI includes zero
  is demoted to `CANDIDATE` (beta ≠ skill).
- **N1 repeated-looks persistence**: a `CANDIDATE`/`PROVEN_T2` must persist across
  2 consecutive runs; the first passing run is recorded as `first_pass_at`.
- **N2 verdict-churn monitor**: exits 3 if raw-verdict churn exceeds 30% (≥20
  tracked cells) — catches a noisy judge.
- **N3 recency/regime gate**: trailing-window net mean < 0 caps `PROVEN_T2` at
  `CANDIDATE`.
- **N4 cost-scaled materiality floor**: the promotion floor is
  `max(0.05%, 0.5 × mean cost)`, so a 6bp edge on a 15bp-cost class cannot promote.
- **Block bootstrap (F1)**: circular moving-block CI so overlapping picks do not
  overstate precision.
- **Canonical full-book guard**: the run fails if the payload declares a canonical
  view but the sidecar was not fetched — no silent 21.4% slice ledger.
- **Observation discipline**: an `observe` pod status; only `pre_registered`
  confers confirmatory status; real hypotheses `H-2026-11-19-01..05` filed.
- **FX symbol-mapping fix** (`AUDJPY=X`/`AUD-USD`/`AUD/JPY` → bare `AUDJPY`) and a
  **stop-fill overshoot** measurement module.
- **Strategy freeze gate** (P0: E11/E13/E14) + a **canonical strategy registry**
  materialized (`trading/data/strategy_registry.json`, 17 strategies).

### audit2 — the positive surface (was a 404)
Deployed, data-live from `/audit3/audit3_ledger.json`, with: doctrine banner,
class verdict table (n, net expectancy, net CI, 2×-cost OK, DSR, `required_n`),
candidate/observe pod registry (with contesting evidence, e.g. VWAP reversion
fails under a 1-bar lag), **forward-evidence clock** (430 H-119 rows; 343 with a
benchmark leg; 100% intrabar), **trial budget**, **benchmark-leg table**, **3×
cost-gate note**, measures library, traps/graveyard, retired-with-reason, and
provenance/freshness (warns on a `/tmp` source path). No hardcoded live numbers.

### Monitoring
- `.github/workflows/audit3-health.yml` — 2×/day: denylist armed (hard fail),
  ledger parses + canonical coverage (hard fail on missing, warn on slice),
  forward-ledger freshness (warn), freeze status (report).
- Freeze gate wired into `forward-test-new-strategies.yml` (intentionally red
  while E11/E13/E14 are open).
- 20-minute local cron: `tools/preserve_peer_worktrees.sh` snapshots all peer
  worktrees (status, log, code diff, untracked text, COMS handovers) into
  `reports/peer_snapshots/<ts>/`.

## 2. Live state (verified after deploy)

```
GET /audit2/                        -> 200 (6.7 KB)
GET /audit2/audit2.js               -> 200 (11.4 KB)
GET /audit2/audit2_forward.json     -> 200 (430 rows)
GET /audit3/                        -> 200 (37.7 KB)
GET /audit3/audit3_ledger.json      -> 200
  generated_at 2026-11-19T08:51Z
  coverage.denominator.mode = canonical, scored_rows = 8,735
  summary: proven 0, candidate 0, weak 59, kill 8, kill classes 3
  persistence.available = false   <-- PENDING (see §6)
```

Rebuild provenance in the review repo: `15_PREMERGE_RESEARCH_POC.md`,
`16_CONSOLIDATION_MERGED.md`, `17_SUBAGENT_RECONCILIATION.md`.

## 3. Test plan

### Unit / integration (must be green)
```bash
python3 -m pytest \
  tests/test_audit3_tribunal.py tests/test_audit3_expectancy_gates.py \
  tests/test_audit3_cost_basis.py tests/test_audit3_coverage_alpha.py \
  tests/test_audit3_enforcement.py tests/test_audit3_selection_alpha.py \
  tests/test_stop_fill_overshoot.py tests/test_audit3_forward_gate.py \
  tests/test_forward_observations.py tests/test_forward_observations_ingest.py \
  tests/test_strategy_freeze_gate.py -q
# expected: 141 passed
```

### Live rebuild (canonical)
```bash
mkdir -p /tmp/a3 && cd /tmp/a3
curl -o dashboard_data.json https://findtorontoevents.ca/audit/data/dashboard_data.json
curl -o resolved_closed_picks_net.json https://findtorontoevents.ca/audit/data/resolved_closed_picks_net.json
python3 -m alpha_engine.audit3_tribunal --picks dashboard_data.json --out ledger.json
# expected: "This run scores the canonical resolved view", scored_rows 8735
```

### Persistence path (two-run smoke)
```bash
python3 -m alpha_engine.audit3_tribunal --picks dashboard_data.json --out l1.json \
  --history hist.json --history-write --persistence-runs 2 --max-churn 0.30
# expect rc=0, hist.json written, verdict_churn.n_flipped=0 on the first run
```

### Gate sanity
```bash
python3 tools/strategy_freeze_gate.py; echo "rc=$?"     # expect rc=1 (frozen)
python3 tools/audit3_denylist_health.py --max-age-days 2 --min-strategy-kills 1
```

## 4. How to check GitHub Actions

```bash
gh run list --workflow=audit3-ledger.yml --limit 5
gh run list --workflow=audit3-health.yml --limit 5
gh run list --workflow=forward-test-new-strategies.yml --limit 5   # red = freeze enforced
gh run view <id> --log-failed
```

What to look for in `audit3 ledger`:
- `Fetch canonical resolved view` prints `canonical view: audit.canonical.v1 rows: 8735`;
- `Build audit3 ledger` prints `coverage: ... canonical resolved view (sha256 ...)`;
- `Deploy /audit3` prints four `uploaded ...` lines (audit3 index, ledger, audit2
  index, audit2.js, audit2_forward.json);
- the commit step pushes `chore(audit3): refresh kill-tribunal ledger [skip ci]`.

Schedules: `audit3-ledger` every 6h; `audit3-health` 05:20/17:20 UTC;
`forward-test-new-strategies` 6-hourly (blocked by the freeze until P0s close).

## 5. Affected pages and how to verify each

| Page | Verify | Expected |
|---|---|---|
| `/audit3/` | open page, check the class table + coverage line | coverage says canonical, 8,735 scored; CRYPTO/FOREX/COMMODITY KILL |
| `/audit3/audit3_ledger.json` | `jq '.coverage.denominator.mode, .summary'` | `"canonical"`, proven 0/candidate 0 |
| `/audit2/` | open page | verdict table loads, forward clock shows H-119 430 rows, no console errors |
| `/audit2/audit2_forward.json` | `jq '.n_rows, .by_hypothesis'` | 430, `H-119` |
| `/audit/` | unchanged by this merge | still the wide dashboard (do not treat `.audit2`-style numbers as canonical) |

## 6. PENDING — persistence wiring (small, not yet on main)

The merged workflow does **not** yet pass the persistence flags, so the live
ledger reports `persistence.available=false`. The exact change (verified locally:
rc=0, 444-cell history, churn 0) is:

```yaml
# in .github/workflows/audit3-ledger.yml, Build audit3 ledger step
          history_arg=""
          if [ -f audit_dashboard/data/audit3_verdict_history.json ]; then
            history_arg="--history audit_dashboard/data/audit3_verdict_history.json --history-write --persistence-runs 2 --prev-ledger audit_dashboard/data/audit3_ledger.json --max-churn 0.30"
          fi
          python3 -m alpha_engine.audit3_tribunal \
            --picks /tmp/audit3/dashboard_data.json \
            --out audit_dashboard/data/audit3_ledger.json $alpha_arg $history_arg
```
and in the commit step: `git add ... audit3_verdict_history.json`.

**Caution for whoever applies it:** during this session the `universal-pisces`
worktree was switched to another agent's branch (`update-cmdb-guide`) by a
concurrent process, and a local (unpushed) commit on that branch captured `.env`,
`.env.dbpw`, and `__pycache__`. Nothing secret reached the remote (the pushed
branch `audit3-persistence-wiring` stayed at `5acdfc3`). Do not push
`update-cmdb-guide`; apply the snippet above from a clean branch off `main`.

## 7. How these changes help performance, per asset class

The point is not a new signal — it is that every class is now judged on the same
honest, cost-aware axis, so capital can be allocated by class instead of by
apparent win rate.

| Class | What the merged gates make visible | Action it enables |
|---|---|---|
| **CRYPTO** | class KILL on the canonical book (n≈6,851); directional LONG has negative alpha vs holding; stop-fill overshoot ≈ +1.06pp | stop adding directional LONG; keep only the market-neutral/mean-reversion pods that pass the forward gate; fix the fill model first |
| **EQUITY** | the one live-positive class (breakout momentum); n small | pre-registered `POD-EQUITY-BREAKOUT` is the default first pod; grow n on the forward clock |
| **ETF** | intraday cost artefact (measured slippage ≈234% of PnL) | monthly cadence only; 3× cost gate blocks the rest |
| **FOREX** | class KILL on the full book; data stale to 2026-02-09 and symbol mapper was broken | backfill then re-measure; do not trade until the forward clock has rows |
| **COMMODITY/FUTURES** | class KILL (COMMODITY); momentum live PF ≈1.1 | roll-yield/TSMOM pods only after a contract feed exists |
| **BOND** | WEAK, tiny n | core beta / steepener as a research pod, not a sizing sleeve |

Cross-cutting: every promotion now needs net-of-cost positive CI at **2×**
slippage, a **materiality floor** scaled to the class cost, **stability** across
halves, **recency** (no stale regime), **multiplicity** (BH/DSR), **persistence**
across runs, and a **benchmark leg**. That is what makes a per-class allocation
decision defensible rather than hopeful.

## 8. Known issues / next steps

1. Apply the persistence snippet (§6) from a clean branch.
2. Emit the observe pods into `forward_observations` with an **intrabar
   first-touch resolver** — close-only rows are rejected as forward evidence.
3. Apply `tools/fx_backfill.py --apply` (DB creds) and review the USDT→CRYPTO
   carve-out.
4. Retire `audit_dashboard/v2/index.html` (orphaned, contradicts audit3).
5. Fix `bt_backtest_runs.asset_class` source mislabel (`NZDUSD=X` stored CRYPTO).
6. Normalise the hypothesis registry's 30+ status spellings and remove its
   duplicate archive tail (own reviewed change).
7. One-week denylist shadow-log review.

*Not investment advice.*
