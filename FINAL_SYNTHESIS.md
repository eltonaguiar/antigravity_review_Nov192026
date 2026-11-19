# Final synthesis — findtorontoevents financial-prediction review (Nov 19, 2026)

## The verdict in one sentence

**The system has no positive selection alpha; its losses are exit-geometry + cost artifacts,
and the single most valuable fix is to make the forward ledger accrue so the audit can
graduate or retire strategies honestly.**

## What we verified (measurements, not opinions)

- **audit3 ledger:** 3,500 of 16,330 picks scored (21.4%); 0 PROVEN / 1 CANDIDATE / 10 KILL / 126 INSUFFICIENT.
- **Selection alpha (audit3 edge hunt):** whole book −0.296% (CI [−0.621, +0.053]);
  CRYPTO LONG −0.442% (CI [−0.892, −0.085]); ETF LONG −0.272% (CI [−0.504, −0.037]).
  "Crypto shorts win, longs lose" is market beta counted once, not skill.
- **quant-audit peer:** 0 of 166 strategy×class×direction cells pass all money-ready gates;
  single-source gate alone eliminates all 166.
- **Per-class (3,500 picks):** ALL PF 0.895, t=−2.53; EQUITY +238pp but t=1.52 (not significant).
- **Crypto stop-fill overshoot:** +828.0pp of the −837.8pp class loss (98.8%) — a mechanical,
  fixable risk-model error.
- **ETF slippage:** 234% of per-trade PnL → monthly cadence only.

## The 5 root causes (02_FINDINGS/why_no_wins.md)

1. The audit is a one-way ratchet to zero — no promotion path; tribunal not wired to emission.
2. The edge gate (WR>50%) is mis-specified for trend/premia cells (WR 35%, RR 2.5).
3. Fixed TP/SL expression + EXPIRED→WON resolver mislabels destroy edge.
4. Data & infra debt limits what can be scored (22,947 ghost rows vs hardcoded 0; stale backtests).
5. No forward-observation ledger ⇒ PROVEN can never be minted from live data.

## What the repo already built (and what's left)

Already in code: expectancy-primary gates, namespace split, provenance SHA, measured
slippage + 2× stress, forward-gate block, source-concentration cap, emission denylist
(wired at ingest + persistence), `forward_observations` schema + promotion rule,
`resolved_closed_view`, pre-registered pod manifest.

Still open (P0→P2): **forward-ledger ingestion adapter (P0)**, per-cell random-entry MC,
selection-alpha as enforced gate, benchmark legs, unified trial counter, data-integrity
pre-filter, decay monitor, graduation state machine.

## What we're shipping (review repo)

| Artifact | What it is |
|---|---|
| `01_INVENTORY/` | audit pages, asset classes, data stores, tracking systems |
| `02_FINDINGS/` | why_no_wins, measured_verdicts, data_quality_resolver, contradictions, agent_work, peer_worktree, peer_kilo_worktree_output, audit3_nextgen |
| `03_VARIABLES/` | tunable-variable table (A–E, 30+ knobs) |
| `04_RECOMMENDATIONS/` | forward_path, evidence_index |
| `05_AUDIT2_SPEC.md` | curated audit2 content spec |
| `06_AUDIT2_PAGE/` | standalone audit2 page + sample feeds |
| `07_FUND_MANAGER_PLAYBOOK.md` | per-asset-class strategies tiered Conservative/Moderate/Aggressive |
| `08_IMPLEMENTATION_PACKAGE/` | pre-registered pods P1/P2/P3, forward-ledger SQL + ingest adapter, benchmark/cost-gate SQL, shadow-harness spec, audit2 adoption checklist |

## The honest next 90 days

1. **Weeks 1–2:** ship the forward-ledger ingestion adapter (P0); stamp `at_issue_*`
   at creation; wire the 3× cost gate; fix crypto stop fills (98.8% of loss).
2. **Weeks 2–3:** pre-register pods P1 (futures TSMOM), P2 (FX carry), P3 (PEAD);
   stand up the shadow-control cohort (negative controls + beta benchmark).
3. **Weeks 4–12:** forward paper all three; weekly audit3 cards (IR, down-capture, net CI
   at 2× slippage); kill any pod with forward CI-LB ≤ 0 at day 30/60.
4. **Capital:** 70–85% low-cost beta core + ≤25% satellites; pods ≤5% sleeve, vol-targeted,
   −15%/−25% drawdown circuit-breakers.

## Realistic prize

If a pod survives: **Sharpe ~0.5–1.0 on the sleeve, low correlation to equities, 10–20%
max drawdown, adequate capacity for <$50M.** That is what "real edge" looks like in 2026 —
unglamorous, diversifying, boring. The institutions you envy don't forecast better; they
harvest risk premia, eliminate cost, size honestly, and survive.

*Not personalized investment advice.*
