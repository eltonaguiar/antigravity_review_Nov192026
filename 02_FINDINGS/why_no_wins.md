# Findings — Why there are no solid wins

The answer is not "not enough strategies". It is that the pipeline is **internally
inconsistent**: it can deny but cannot certify, it tests the wrong expression for the
strategies most likely to work, and its data layer cannot support the measurement even when
a real edge exists.

## Root cause 1 — The audit is a one-way ratchet to zero (no promotion path)

- audit3 pre-declares cells, applies a strict kill rule, and reports **0 PROVEN / 1
  CANDIDATE**. Every gate is tuned to *deny*.
- There is **no promotion/certification path**: `PROVEN_T2` has no route to a production
  cap, so the dashboard can never graduate anything. Kill switches that can't certify "this
  survived" turn the system into a ratchet to zero — statistically safe, strategically
  sterile.
- The tribunal is **not wired to block emission**: its output is a web page, not a
  denylist the scanner reads. `non_crypto_policy.passes_non_crypto_policy()` historically
  had **0 call sites**. So even the KILL verdicts don't stop the pipeline from emitting.

## Root cause 2 — The edge gate is mis-specified for the strategies that work

- Gate G1 (`WR > 50%`, one-sided binomial) is only a break-even test for **symmetric
  payoffs**. 
- A genuine trend/premia cell (`WR 35%, RR 2.5`) has positive expectancy but can never
  clear G1 — so the tribunal **structurally cannot prove the one family with real evidence
  behind it**.
- The correct edge test is **bootstrap net-expectancy CI > 0** (that is already G2). WR
  should be a descriptor, not the gate.

## Root cause 3 — Fixed TP/SL expression destroys edge

- The recurring "high WR but PF < 1" pathology (EQUITY: WR 59–60%, PF 0.94) is a fixed
  TP-first labeling artifact.
- The resolver mislabels `EXPIRED → WON`, inflating surface numbers (raw WR 33% vs the
  78–88% shown on banner surfaces per the honesty layer). 
- Expectancy, not win rate, is the only honest definition of edge. Exits should be
  time/vol-based and symmetric, not fixed take-profit.

## Root cause 4 — Data & infrastructure debt limits what can be scored

- Only **21.4%** of closed picks (3,500/16,330) are scored by audit3.
- **22,947 ghost rows** in `trading_picks` vs a hardcoded 0/GREEN on the page (per data
  quality correction).
- `bt_backtest_runs` stale since 2026-03-06; duplicated `bt_backtest_trades` mirror
  (~27M rows); per-DB users block cross-DB joins; no declared system of record among the
  three outcome ledgers; no forward-observation table.
- The audit3 window is recent-biased (a recent crypto drawdown killed structural longs —
  BTC/ETH/SOL/BNB/BCH all killed); nothing is measured against the 21,988 policy-clean
  CRYPTO rows in the full registry.

## Root cause 5 — No forward-observation ledger ⇒ PROVEN can never be minted from live data

- All "winner" claims are backward-looking. The only forward-confirmation claims
  (`TRUE_PROFITABILITY_VALIDATED.md`) contradict the strict ledger (see
  `contradictions.md`).
- Without a `forward_observations` table, "did we tweak X and make money?" cannot be
  answered by the system.

---

## The net effect

The project is good at *disproving* things (11 strategies killed with genuine statistical
discipline) and poor at *proving* them. That is why the surface shows a lot of "activity"
(331k commits, dozens of branches, 99 hypotheses, ~47 strategies) yet **0 verified wins**:
the machine is designed to never say yes.
