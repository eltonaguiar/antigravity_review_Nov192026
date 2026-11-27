# 39 — Enhanced Strategy Opportunities + Live Audit-Surface Cross-Check

**2026-11-27 · PAPER ONLY · ZERO CAPITAL · NOT INVESTMENT ADVICE**
Author: Kimi Code CLI session in `findtorontoevents_antigravity.ca`, reviewing this repo against the
live surfaces it audits: `findtorontoevents.ca/audit`, `/audit2`, `/audit3`.

Two deliverables in one file: **Part A** — the live-surface cross-check the operator asked for;
**Part B** — the enhanced strategy opportunities mined from this repo, ranked, with the cross-check
results folded in. Sources cited as `(path §section)`.

---

## Part A — Cross-check: live /audit, /audit2, /audit3 vs this review's claims

Method: fetched all three pages + their data endpoints on 2026-11-27 ~17:40 UTC; compared freshness,
content, and internal consistency against the review's documented expectations
(`18_FINAL_REPORT_COMS.md`, `12_AUDIT3_REVIEW_NEXTGEN.md`, `05_AUDIT2_SPEC.md`, `09_AUDIT2_CONTENT_RECOMMENDATION.md`,
`README.md` TL;DR). Data-layer checks only — render-level claims (what a browser actually paints)
need a Playwright pass, not scheduled here.

| Surface | Data generated (UTC) | Verdict |
|---|---|---|
| `/audit` | `dashboard_data.json` **2026-11-27T17:36Z** | ✅ fresh; review-era staleness (~34 d) is fixed |
| `/audit2` | `audit2_forward.json` / `audit2_pods.json` **2026-11-27T12:35Z** | ✅ fresh, ❌ one broken fetch (below) |
| `/audit3` | `audit3_ledger.json` / `forward_book.json` **2026-11-27T12:35Z** | ✅ fresh; tribunal expanded |

### A.1 `/audit` — the wide scoreboard

- **Freshness fixed.** Live payload regenerated today (27.4 MB, 135 systems, 24 active, 15,284 closed,
  9,072 resolved). The review's "~34 days stale" complaint (`README.md` TL;DR) no longer holds —
  the hourly cron is landing.
- **Ghost rows now quarantined, not hidden.** The review's hardest `/audit` finding was the hardcoded
  "0 / GREEN" over 22,947 ghost rows (`GHOST_ROW_PROVENANCE.md`). The live page now states ghost rows
  are quarantined out of the canonical view, and `/audit/data/denominator.json` (`audit.denominator.v1`,
  generated today) publishes the exclusions with reasons: **12,232 `invalid_row`**, 228 mirror
  duplicates, 86 non-performance exits, 76 resolver-breakeven-fallback → **9,034 canonical of 15,345
  closed**, with the canonical SHA-256 on the wire. This is exactly the single-denominator honesty
  the review demanded. ✅
- **⚠ `asset_class_health` is now EMPTY in the live payload.** The review flagged this block as a
  stale snapshot with contradictory cohorts (COMMODITY dashboard PF 5,624 vs ledger 0.12; ETF n=15 vs
  n=590). Today the key returns `[]`. The contradiction is gone, but so is per-class health entirely.
  If removal was deliberate, say so in the changelog; if it's a generation regression, restore it
  from the canonical denominator — an empty tile and a lying tile are equally unreadable.
- Division of labour (`/audit` = wide, `/audit3` = judge, `/audit2` = candidates) is intact.

### A.2 `/audit2` — candidate & methodology library

- **Forward clock is live and honest:** `audit2_forward.json` today: **456 forward rows**, of which
  H-119 n=435, 100% intrabar, benchmark coverage 80.0%. H-119 remains **orphan — no pod owns it**,
  `gate_ready=false` on the published numbers (net PF CI-LB 0.9325 ≤ 1.0, IR 0.05 < 0.5). This is the
  review's strongest open recommendation still unexecuted: create **POD-H119-FORWARD-ALPHA**
  (`README.md` Part 2; §B.5 below).
- **Pod registry matches the review's direction:** 11 pods — 2 `declined` (incl. POD-EQUITY-BREAKOUT,
  the non-reproducing one, now formally declined ✅), 1 `post_hoc` (POD-LUXALGO-SHORT — the audit3
  CANDIDATE), 8 `observe` (VWAP-MR, Bollinger-MR, Faber-TAA, USDJPY momentum, roll-yield,
  CRYPTO-POSITION, ETF dual momentum, BTC4H RSI+MACD). None have minted PROVEN — correct per spec
  (no PROVEN_T1 labels anywhere ✅).
- ❌ **Bug: the canonical-denominator strip on `/audit2` is broken.** `audit2.js` fetches
  `"denominator.json"` relative to `/audit2/` → **HTTP 404** (verified live). The canonical file lives
  at `/audit/data/denominator.json`. The review's spec is explicit: one class-verdict table on one
  canonical denominator, never a second source (`11_AUDIT2_SPEC_CONSOLIDATED.md`). Either deploy a
  copy to `/audit2/data/` or point the fetch at `/audit/data/denominator.json`. One-line fix; until
  then the "population:" strip shows an error string.

### A.3 `/audit3` — the kill tribunal

- **Fresh and stricter than at review time:** today's ledger reads **0 PROVEN / 1 CANDIDATE / 5 KILL /
  60 WEAK / 307 INSUFFICIENT_N**, 66/373 cells tested, 65 DSR-scored (review recorded 0/1/10 KILL over
  45 cells — the tribunal has been re-run and widened). `audit3_evidence.json` 2026-11-26T08:30Z,
  `forward_book.json` 2026-11-27T12:35Z. The single CANDIDATE remains the `luxalgo_confluence` crypto
  short (now POD-LUXALGO-SHORT, `post_hoc`). The page is still engineered to say no, and it still does. ✅
- The E1–E5/F1–F6 next-gen asks (`12_AUDIT3_REVIEW_NEXTGEN.md`) are code-level and cannot be verified
  from the wire; the data contracts they depend on (forward clock, canonical ledger, trial counts) are
  all live and same-day, which is the necessary condition.

### A.4 Cross-surface consistency

All three surfaces now regenerate within the same hourly window from one canonical source
(`dashboard_data.resolved_closed_picks_net`, SHA-256 published in `denominator.json`). The review-era
complaint that "each surface quoted its own denominator" is resolved at the data layer. Remaining
wire-level defect: the `/audit2` denominator path (A.2). Remaining honesty gap: H-119's 435 intrabar
rows certifying nothing for want of a pod to own them.

---

## Part B — Enhanced strategy opportunities, ranked

Ranking principle: impact × (1/effort) × unblockedness, with falsifiability as a precondition — the
review's binding-constraint finding is that **recording, not statistics, is the gate**
(`31_VERIFICATION_AND_BINDING_CONSTRAINT_2026-11-22/PROMOTION_GATE_2026-11-22.md`). Nothing below is
money-ready; everything is paper-gated behind the 90-day decision rule (B.6).

### Tier 0 — Infrastructure that unblocks everything else (do these first)

**B.1 Emit-time provenance ledger — the only gate that currently matters.**
`resolved_closed_picks_net` (10,968 picks) ships no `created_at`; the one testable artifact (H-119
forward, 430/435 rows) is 100% backfilled with median write-lag 103 days. `mega_mutation` proves the
cost: TP-first 56.4% where a driftless random walk implies 40.9% (binomial p = 1.7×10⁻³) — genuine
skill or hindsight-placed TP/SL, and no test can separate them. `tools/provenance_ledger.py` already
exists (append-only, hash-chained, refuses caller timestamps, rejects inverted TP/SL at source)
(`32_PROVENANCE_LEDGER_2026-11-22/`). Wire it into emission. Until then every positive result below
is unfalsifiable.

**B.2 Crypto stop-fill intrabar fix — the single largest PnL artifact in the estate.**
Stops must fill at stop-price on breach, at close on gap (`NEXT_STEPS.md` P0-1). This one artifact is
**+828.0pp of the −837.8pp CRYPTO class loss (98.8%)** (`FINAL_SYNTHESIS.md` root cause #3). Target:
crypto PF 0.768 → ≈1.00. Cheapest high-impact change in the repo. Also kills the "high WR / PF<1"
pathology from fixed TP/SL labeling (EQUITY WR 59–60%, PF 0.94) and the EXPIRED→WON banner inflation
(78–88% banner vs 33% raw).

**B.3 Re-specify the scoring gates (validation methodology).**
- G1 (WR>50%) → **G2 bootstrap net-expectancy CI as the primary edge test**; WR is a descriptor.
  Trend/premia cells run WR ~35% at RR ~2.5 and can never pass G1 (`FINAL_SYNTHESIS.md` root cause #2).
- **Selection alpha as a hard gate (G8)** so beta-only cells can't promote (`NEXT_STEPS.md` P0-4;
  `12_AUDIT3_REVIEW_NEXTGEN.md` E1 — fall back to the random-entry timing null when price tables are absent).
- **DSR n_trials = global N (658), not tested cells (45)** (P0-5); the trial-count spread across
  agents was 26.3× (120/154/122/362/658/25) (`README.md` §"Where they disagree").
- **Power-based `required_n` per cell** replacing flat n≥100 — the current kill gate passes effects it
  cannot detect (TPR 10% at n=80 → 3.3% at n=500) (`README.md` Part 7/8; `POWER_ANALYSIS.md`).
- Promote **2×-cost stress from report-only to a hard promotion gate** (P1-5; E5).
- Every verdict **quotes its MDE**; prefer cross-sectional IC tests (~40× the power of a single equity
  curve; equity-curve MDE over 33.8y SPY is 5.08%/yr — a genuine 3%/yr alpha is invisible, t=1.18).

**B.4 Cost-model fixes — two concrete defects manufacture nulls.**
(a) The Questrade model applies the **1.75% FX conversion spread per trade** → every US equity trade
costs 175bp; spread/slippage are hardcoded guesses — a ~30× error every "net of costs" equity
conclusion inherits (`33_VALUE_PEAD_AND_COST_GAPS_2026-11-23/2026-11-23-equity-cost-blocker.md`).
(b) Adopt the **cost of record** (`README.md` §"Cost of record"): fund 0 · bond ETF 0.6144bp · ETF
6.7122bp · FOREX 7.533bp · equity bracket 0.9756/4.0124/12.0749bp (floor/central/ceiling — grade at
ceiling, report at central) · commodity 20bp · crypto 20–52bp. **Wrapper selection is an alpha
decision**: T-bill carry nets −0.6 to −0.8bp in an ETF wrapper vs +5.9bp in a money-market fund.
"Edge per trade rises monotonically with horizon" (15m +2.48 → 1D +24.21bp) — the cost-horizon
ladder explains every prior result. Hard rule: reject any class whose per-trade PnL < 3× measured
round trip (`07_FUND_MANAGER_PLAYBOOK.md` §0.3).

**B.5 Stand up the forward-observation machine — adopt the orphan H-119 clock.**
The strongest OOS signal in the book certifies nothing: **H-119, +1.79% selection alpha, n=435,
73.3% alpha WR, 100% intrabar, live on `/audit2` today** (`README.md` Part 2; verified Part A.2).
Action: create **POD-H119-FORWARD-ALPHA**; convert the 8 `observe` pods to emitting paper legs with
benchmark legs; keep known-loser cells as shadow negative controls; kill rule = forward CI-LB ≤ 0 at
day 30/60. Concentrate emission on ≤3 pods in 2 classes; pause everything else
(`04_RECOMMENDATIONS/forward_path.md` Phase 2). Also: wire the retired-strategy blocklist to emission
(165 bypasses recorded, incl. `forex_rsi2_mean_reversion`).

### Tier 1 — The open threads (feed the forward clock, all pre-registered or design-frozen)

**B.6 `SOLUSDT/breakout/1d` — the single open thread in the 1000-cell sweep.** Net +71.90bp/trade
(gross +97.90), the only cell positive in all three sequential walk-forward folds, pre-registered
2026-11-24, at 0/30 forward trades. DSR 0.0045 against 1000 trials, CI [−29, +184] — "awaiting
out-of-sample data; it is the single open thread" (`31_SWEEP_CLOSURE_2026-11-24/SWEEP_CLOSURE.md`).
Feed it first.

**B.7 Insider Form-4 purchase probe (INSIDER-P) — the first powered design in the equity programme.**
Analyst-ratings programme is dead by arithmetic (8,498 events, **0 firms reach 500** — every
firm-level conclusion underpowered by construction). The DB already holds **10,735 insider
transactions across 119 tickers** (205 purchases; officer/director flags), point-in-time — read
`gm_sec_insider_trades`, don't re-scrape SEC (`13_EXEC_SUMMARY_DB_2026-11-24.md` §7.4). Frozen design:
code-P open-market purchases, officer/director only, **filing-date timestamp never transaction date**,
cluster variant (≥2 insiders/30d), matched benchmark = same-date ADV-tercile × 126d-momentum-tercile
forward returns, costs at the equity bracket. Sales are the control, not a strategy.

**B.8 Top-gainers event study — trade *after* the list, not before.** Predicting gainers pre-move needs
IC ≈ 0.05+ against news/tail events; trading continuation/reversal *after* a name appears is a large,
clean sample and now the primary study (`35_TOP_GAINERS_HARVEST_2026-11-23/SYNTHESIS.md` §2.5). Three
independent arrivals at the fade hypothesis: MAX/lottery effect (Bali–Cakici–Whitelaw 2011), "'Top
Gainer' is a mean-reversion trap", and the size×catalyst 2×2 (small-cap no-news → mean-revert;
large-cap earnings-catalyst → drift). Mandatory baseline to beat: buy previous day's top-10 gainers,
hold 5 days, 2-ATR stop. Plus the one-day probe: repeat-gainer persistence P(reappear in k days | on
list today) vs base rate (`ML_TOP_GAINERS_BRIEF.md` §0.6).

**B.9 Polymarket mid-range deviation — the only live SHADOW hypothesis.** Prices carry real
information (Brier skill +0.4956 vs base rate, n=362, tails calibrated) but contracts priced
0.20–0.50 delivered YES far less often than priced (gaps −0.223, −0.171). Not yet an edge: 2/10
buckets, binomial p≈0.086, spread UNMEASURED — "unmeasured cost can support a rejection, never a
promotion" (`29_LEDGER_MINE_2026-11-22/2026-11-22-prediction-market-calibration.md`). Promotion path:
pre-register bucket 0.20–0.50 YES-short, fixed 7-day lead, n≥200 OOS, measured spread.

**B.10 `luxalgo_confluence` SHORT (the one CANDIDATE) — needs its two bars lifted.** Live on audit3
today as POD-LUXALGO-SHORT, `post_hoc`. Promotion requires: (a) **BTC-beta regression + funding
covariates** — n=476, WR 54.4%, PF 1.61, but if its PnL correlates ≈ −0.8 with BTC it is short-beta,
not alpha; every crypto row must report BTC-residual or be unattributed; (b) a **second independent
source** (currently single-source 98% — the gate that alone eliminates all 166 cells in the peer
quant-audit) (`05_AUDIT2_SPEC.md` P6; `02_FINDINGS/measured_verdicts.md`).

**B.11 Build the TP/SL engine on a vol forecast, not a direction forecast.** "Volatility is far more
predictable than direction" (four-model consensus). Machinery: triple-barrier labels (López de
Prado), MAE/MFE-empirical stop/target placement, GARCH/HAR-RV forecast, SL-first on ambiguous bars.
Corollary from the optional-stopping theorem: TP/SL "optimizers" that show profit on random-walk data
are overfitting or leaking — run the whole pipeline on shuffled/GBM returns to get the overfitting
floor and subtract it (`SYNTHESIS.md` §2.5d/§2.9).

**B.12 HML/value as the first premium test — designed, frozen, data-blocked.** Three independent
models agree value beats PEad as a first test (large-cap PEAD is dead post-2006 by 3-model consensus —
a null is the finding). Kill rule is usable as written (kill if OOS annualized net on committed
capital ≤ 4.3%, or the one-sided 95% upper bound ≤ 4.3%; state collateral yield, base 4.32%).
Blocker: no book equity, no shares outstanding. Build the fundamentals store — it also unblocks
PEAD on the 500+ name screen (`33_VALUE_PEAD_AND_COST_GAPS_2026-11-23/`).

### Tier 2 — Paper-gated sleeves for the 90-day shadow (benchmark leg mandatory on every card)

**B.13 Delta-neutral funding carry — the only measured positive-expectancy stream that isn't equity
beta.** +7.28%/yr gross, Sharpe 3.423, independently reproduced; funding negative 26.8% of days,
carry sleeve drew −10.5%. Sizing rules already stated: 10%, raise to 20% only if measured drag ≤
0.5bp/day, cut to 0 if > 1.0 (`THE_DECISION_2026-11-22` §2/§4). Refuted as a *stable cash-beater*
(+3.555% mean vs 3.50% bill; cross-venue harvest ≤ +1.56%/yr) — the edge is the delta-neutral basis,
not the carry.

**B.14 Equity daily breakout continuation — a real family effect that is mostly a cost arbitrage.**
Pre-2010 positive in 7/7 markets (US t=3.61, Canada 3.21, HK 2.15, Japan 2.13), robust across five
decades, honest size +12–20bp/trade — **but only at round-trip ≤ ~8bp; at 10bp/side it is gone in
5/7**. Viable only under the fixed cost model (B.4) and monthly-or-daily cadence
(`THE_DECISION` §7 addendum). Already represented live by the (now declined-then-rebuilt) equity
breakout pod family — re-run it under the corrected costs before spending forward rows.

**B.15 CRYPTO mean-reversion — the strongest in-repo crypto candidates, conditional on B.2.** VWAP MR
4h (OOS 516/953, Sharpe 3.10, DSR 21.4, PBO 0.18) and Bollinger MR (Sharpe 1.38)
(`14_QUANT_FUND_MANAGER.md` Part 2). Live as POD-CRYPTO-VWAP-REVERSION and POD-CRYPTO-BOLLINGER-MR
(observe). Do not promote any crypto row until the intrabar stop-fill fix lands — the −18.17bp class
number was manufactured mostly by fill fantasy (B.2).

**B.16 TSMOM / managed futures + 10-month SMA overlay.** TSMOM is the strongest documented premium +
crisis alpha (`05_AUDIT2_SPEC.md` P1). The Faber overlay is drawdown control, not alpha: ΔSharpe
+0.143, MDD cut 61% (−50.9→−19.7%), ΔCAGR −0.71pp, worse than B&H in 31% of rolling 10y windows, and
currently whipsawing (2025-01→2026-11: B&H +17.5% vs overlay +0.5%). Live as POD-FABER-TAA and
POD-ETF-DUAL-MOMENTUM (observe). Watch the two failure regimes: fast (5-week) crashes, and chop.

**B.17 FX G10 carry + 200d trend filter** (gross Sharpe 1.102 → net 1.035; needs the FX backfill
first — FX prices stale to 2026-02-09 with broken symbol mapping, and the independent 35-cell census
went 0/35 at 5bp). Live as POD-FOREX-USDJPY-MOMENTUM (observe) — fix the feed before trusting the pod.

**B.18 Roll-yield harvesting** — "#1 quick-win idea" (class WR 55.6%, PF 1.06)
(`14_QUANT_FUND_MANAGER.md`); live as POD-COMMODITY-ROLL-YIELD (observe). Commodity class is KILLED
directionally (−346.51bp, PF 0.12) — roll yield is the only commodity sleeve worth shadowing.

**B.19 Rank-persistence probe across the 123 model portfolios — no new data needed.** Done once:
ρ = −0.0199 (p=0.8392, n=122) — **zero rank information; the portfolio engine has no skill**
(`14_RANK_PERSISTENCE_2026-11-24.md`). Re-run quarterly as the engine's honesty check; use the engine
for beta management, not alpha. Median portfolio beat SPY (+4.0pp) but **lost to cash** — regime
window Aug–Oct 2026 collapsed in November (−3,160, 25% WR).

### Tier 3 — Stop-doing list (graveyard enforcement; the review's strongest meta-finding)

The 1000-cell sweep proved a **signal problem, not a cost problem**: 39/44 (89%) negative net, median
gross −1.51bp (`30_COST_STRUCTURE_2026-11-24/COST_VS_SIGNAL.md`). Stop mining daily-crypto technical
rules; stop re-litigating: VRP short-vol (RUINED 2020-03), GDX/SLV pairs, 12-1 L/S momentum (negative
gross), large-cap PEAD (dead post-2006), funding-as-cash-beater, Connors RSI-2, ICT/SMC alone, KSS
cointegration, meme-scanner "580%". The audit2 graveyard panel exists precisely so these stay dead
(`09_AUDIT2_CONTENT_RECOMMENDATION.md` §4).

### B.6 The 90-day decision rule (restated from the review — it is the operating contract)

Pre-register ≤3 pods, shadow 90 days with benchmark legs and known-loser shadow controls. Promote
only on: positive net-CI lower bound **at 2× measured slippage**, IR ≥ 0.5 vs SPY, own forward rows
only. If nothing clears at day 90, the finding is "no deployable edge on available data" — a citable
result: freeze the harness, keep capital in a ≤0.20%-fee beta core. The only tracked allocation pick
stands: **40% cash floor / 50% broad index B&H / 10% funding carry** (reconstruction 8.38% CAGR,
Sharpe 1.07, MDD −11.61% — all-equity beats it on wealth by 24%; the justification is drawdown and
sequence risk, stated openly) (`THE_DECISION` §2–3; `tools/recommended_portfolio_tracker.py`).

---

## Appendix — cross-check inventory (2026-11-27 ~17:40 UTC)

| Artifact | URL | generated_at (UTC) | Headline |
|---|---|---|---|
| dashboard | `/audit` + `data/dashboard_data.json` | 11-27 17:36 | 135 systems, 15,284 closed, 9,072 resolved; `asset_class_health` empty |
| denominator | `/audit/data/denominator.json` | 11-27 12:35 | canonical 9,034/15,345; 12,232 invalid_row quarantined; SHA-256 published |
| pods | `/audit2/audit2_pods.json` | 11-27 12:35 | 11 pods: 2 declined, 1 post_hoc, 8 observe |
| forward | `/audit2/audit2_forward.json` | 11-27 12:35 | 456 rows; H-119 n=435 orphan, gate_ready=false |
| tribunal | `/audit3/audit3_ledger.json` | 11-27 12:35 | 0 PROVEN / 1 CANDIDATE / 5 KILL / 60 WEAK / 307 INSUFF (66/373 cells) |
| evidence | `/audit3/audit3_evidence.json` | 11-26 08:30 | n_records + class-mismatch accounting live |
| forward book | `/audit3/forward_book.json` | 11-27 12:35 | fresh |

**Defects filed from the wire (actionable, in order):**
1. `/audit2` fetches `denominator.json` → 404; canonical file is at `/audit/data/denominator.json`.
   Fix path or deploy a copy. (Breaks the single-denominator strip the spec requires.)
2. `asset_class_health` empty in live `/audit` payload — confirm deliberate removal vs generation bug.
3. H-119 forward rows (435, intrabar-true) still orphan — no pod owns them; the +1.79% selection-alpha
   signal the review called the strongest in the book still certifies nothing.

**Coverage note:** synthesized from `README.md`, `FINAL_SYNTHESIS.md`, `THE_DECISION`, `NEXT_STEPS.md`,
02–14, 16–18, 28–33, 35, 38 doc families. The `26_ASSET_CLASS_DOSSIERS` and `42_HARVEST_UPGRADE`
families were read via their consolidating docs (28/38); deep per-dossier harvest mechanics
(e.g., scraping-kit specifics) were not independently re-derived. Render-level page verification
requires a browser pass. Two exploration agents covering the playbook and dossier families were
lost to an API concurrency limit mid-review; their territory is covered second-hand via the synthesis
docs and the 28/38 consolidations.
