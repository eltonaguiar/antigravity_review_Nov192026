# Findings — Peer worktree reviews (financial-prediction worktrees)

Reviewed 2026-11-19. This notes the *committed deliverable* each peer worktree produced,
what it found, and where it agrees or disagrees with the audit3/surface review. The
`.kilo/worktrees/` review sessions (universal-pisces, vanilla-handsaw, witty-fight) are
clean at the main tip and have not yet landed unique commits; the substantive peer work is
in the standalone worktrees below.

---

## 1. `quant-audit-2026-11-14` — branch `docs/final-v2-per-asset-class-profitability`
### (the most complete peer review)

Commit `b8d7d03343e` "final_v2 — per-asset-class profitability, and two corrections to my
own audit" and `ef2621a6134` "final 2026-11-14 package — review of every peer claim"
(`final_v2/` + `final_2026_11_14/quant-audit-2026-11-14/`).

### 1.1 Core finding — 0/166 cells pass the money-ready gate

Using `tools/money_ready_screener.py` on `recent_closed_array.json` (3,447 decisive picks)
and the full Tier-2 gate contract, across all 166 strategy×class×direction cells:

| Gate | Threshold | Cells passing |
|---|---|---|
| n ≥ 100 decisive | ≥ 100 | 1 / 166 |
| WR ≥ 50% | ≥ 50% | ~12 / 166 |
| PF ≥ 1.5 | ≥ 1.5 | ~5 / 166 |
| Net expectancy > 0 (CI-LB > 0) | > 0 | ~3 / 166 |
| MDD < 20% | < 20% | ~2 / 166 |
| Single-source < 60% | < 60% | **0 / 166** |
| Multi-source ≥ 2 | ≥ 2 | **0 / 166** |
| **ALL GATES** | | **0 / 166** |

The **single-source gate alone eliminates all 166 cells**. Returns 0 asset classes
money-ready, consistent with `money_ready_verdict.json` (`money_ready: []`).

### 1.2 Per-class profitability table (3,500 closed picks, 2026-02-21 → 11-14)

| Class | n | WR | PF | mean/trade | total | t |
|---|---|---:|---:|---:|---:|---:|---:|
| CRYPTO | 1,966 | 39.3% | 0.768 | −0.426 | −837.8 | −4.84 |
| EQUITY | 738 | 47.0% | 1.154 | +0.323 | +238.3 | +1.52 |
| ETF | 567 | 44.3% | 1.036 | +0.040 | +22.9 | +0.34 |
| FOREX | 187 | 39.0% | 0.634 | −0.155 | −29.0 | −2.29 |
| BOND | 35 | 37.1% | 0.586 | −0.221 | −7.7 | −1.47 |
| COMMODITY | 7 | 42.9% | 0.604 | −0.598 | −4.2 | −0.53 |
| **ALL** | 3,500 | 41.7% | 0.895 | −0.176 | −617.5 | −2.53 |

Every class decays first-half → second-half; none improves. **EQUITY is the only positive
total, but it is not statistically distinguishable from zero (t=1.52, p=0.12).** Four
classes are 9–16pp short of their cost-adjusted breakeven WR (FOREX/BOND risk more than
they stand to make).

### 1.3 The most transferable mechanical finding — crypto stop-fill overshoot

- Planned risk (|entry − stop|): mean **1.919%**
- Realized loss on the same stopped trades: mean **2.990%**
- Overshoot = **+1.071pp per stopped trade = +828.0pp total**
- Crypto class total = −837.8pp → **overshoot is 98.8% of the entire class loss**.
- `exit_price` ≠ `stop_loss` in 703/773 stopped trades (median gap 0.324%, p90 4.43%).
- This is faithful stop *polling* (record the price found), not a formula bug — it means
  **every strategy's risk model is off by ~1.56×**, degrading planned R:R 1.69 → 1.08 and
  raising the required WR from 37.2% to 48.0%. Fixing fills moves crypto PF 0.768 → ≈1.00
  (breakeven ceiling); signal selection must do the rest.

### 1.4 Reconciliation with peers — research vs production gap

Peers (childlike-airport/kilo) found *statistically valid profitable approaches in
research* (e.g. regime-filtered VWAP MR Sharpe 3.76; vol-targeted trend Sharpe 2.13;
walk-forward variant C PF 1.26). **None are deployed in the live ledger.** The gap is
research → production:
- Research: profitable approaches exist (in `/tmp/kilo/*.py` harnesses / deepAI).
- Production ledger: 0/166 cells pass; live curated picks 100% LONG-biased in RISK_OFF,
  80% with zero forward validation; live open P&L −1.42% avg across 4,310 open picks.

**Consensus across all 9 peers:** not money-ready; data pipeline broken; highest-value
first fixes = PnL-unit contract + NULL-tombstone zombie drain; no "solid" claim until the
horizon harness passes.

---

## 2. `copilot-financial-review-20261115` — branch `docs/copilot-profitability-20261115`
### (WIRED_IN research specs + elimination record)

Commits `770a3f1a30a` / `59f9224060d` add shadow-monitoring paper cards
(`WIRED_IN/2026-11-15T0150Z_childlike-airport/`, `_0128_buffy/`) wired into the audit
pipeline via `universal_pick_resolver` (system `wired_in_childlike`, flagged `paper_only`).

- **What's wired (paper only, `sizing_allowed=false`):** XLV LONG, LLY LONG, SHY LONG —
  three trend/ballast cards. Crypto/forex/commodity/futures/MF/prediction-markets all
  **eliminated** (see `ELIMINATION.md`).
- **H-143 tactical algorithm eliminated:** net CAGR 9.34% vs same-window SPY 18.09% (lost
  ~8.75pp/yr at base cost); MDD 11.86% vs 18.76% was insufficient compensation; every
  paired block lower bound negative → removed from the alpha-forward queue. This is the
  right, honest way to retire a strategy (research rejection, not production change).
- **Fund/ETF reference baseline** (5 bps/side): FXAIX +73.05% (CAGR 11.61%), SPY +72.38%,
  VTI +64.39%, BND −1.51%, SGOV +20.86%. Notes that broad equity wrappers are correlated,
  not independent alpha — a useful caution against labeling index returns as edge.
- Reproducibility pins commits + SHA-256 hashes for the simulation and results. Good
  methodology hygiene.

---

## 3. Other financial worktrees (lighter, in-progress)

| Worktree / branch | What it has |
|---|---|
| `ghcopilot-fund-strategy-profile` (`feat/ghcopilot-fund-strategy-profile`) | "explain fund strategy mandates and missing evidence" commit — fund mandate rationale; no completed gate pass |
| `p0-audit-json-2026-11-16` (`docs/audit-publish-gate-cards-2026-11-16`) | gate-card publishing; untracked reports (`forex_carry_backtest_20261116.json`, `value_screener_runs/`) |
| `recent-picks-stats` (`feat/recent-picks-by-date-class-stats`) | class-performance deep-dive tool; `CLASS_PERFORMANCE_VERDICT_2026-10-06.md` |
| `wt-audit-prediction-system` (`audit-prediction-system-20261114-154529`) | untracked `audit_output/`; sealed prospective ledger; paper_pilot state churn |
| `quant-risk-improvements` (`quant/risk-improvements`) | new `build_bootstrap_ci.py` + migration `004_add_quant_risk_fields.sql` (risk fields) |

These are unfinished; none changes the headline verdict.

---

## 4. Synthesis — where peers agree with this review

| Finding | My review | Peer evidence |
|---|---|---|
| 0 money-ready / 0 PROVEN | audit3: 0 PROVEN, 1 CANDIDATE | quant-audit: 0/166 cells pass all gates |
| Not money-ready on any class | audit3 class kills | quant-audit per-class table (ALL PF 0.895, t=−2.53) |
| Single-source blocks everything | candidate barred at 98% single-source | quant-audit: single-source gate eliminates all 166 |
| Resolver mislabel `EXPIRED→WON` | data_quality_resolver.md | quant-audit §3 (78.93% vs 39.38%) + surface review |
| No promotion path / research↔production gap | why_no_wins root cause 5 | quant-audit reconciliation (research valid, not deployed) |
| EQUITY is the only positive-OOS class | surface review +0.608 (33f) | quant-audit +238pp but t=1.52 (not significant) |
| Retire weak houses honestly | 11 KILL strategies | copilot H-143 elimination record |

The peers also add one **new, concrete, mechanical** finding my review did not have:
**crypto stop-fill overshoot is 98.8% of the crypto class loss** — a specific, fixable
risk-model error worth adding to the tunable-variable set (variable: "rested stop vs
polled stop / fill model").

---

## 5. Disagreements / caveats

- **EQUITY verdict differs in strength.** Surface review calls EQUITY the one positive OOS
  class (+0.608); quant-audit says +238pp total but t=1.52 not significant. Both agree it is
  the *only candidate class*; they differ on whether it is already "real". Treat EQUITY as
  a candidate, not a win.
- **Counts differ by survey** (166 cells vs 171/45 cells; 3,500 vs 3,447 picks) because the
  peers used different payloads/gates. The *direction* is identical everywhere.

*Not personalized investment advice.*
