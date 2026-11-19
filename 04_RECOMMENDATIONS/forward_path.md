# Recommendations — 90-day forward path

Ordered by leverage. The first block is infrastructure (fix the machine so it can say
yes/no correctly); the second is the pre-registered pods (the only things worth trading
forward); the third is capital discipline.

## Phase 1 — Fix the machine (weeks 1–2)

1. **Fix audit3 gates (cheap, high leverage):**
   - G1 → G2: bootstrap net-expectancy CI > 0 is the primary edge test; WR becomes a
     descriptor.
   - Split the ledger into `confirmatory` / `discovery` namespaces; BH per namespace;
     promotion gates apply only within `confirmatory`.
   - Add the 2× slippage stress gate (already computed, make it a gate).
   - Embed provenance (commit SHA + input SHA-256 + generator version).
   - Publish a selection-adjusted CI (Bonferroni over the 65-segment screen).
2. **Wire the tribunal into emission:** KILL cells → scanner denylist; KILL symbols →
   drop dominance. This single change makes audit3 interventionist instead of a web page.
3. **Declare the system of record** for the three outcome ledgers (`at_signal_outcomes`),
   and **add the `forward_observations` table** (spec in `03_VARIABLES/tunable_variables.md`
   E2). This is what makes "winning" measurable.
4. **Raise scoring coverage** > 90% (currently 21.4%); resolve ghost rows; fix the
   EXPIRED→WON resolver mislabel; pin the resolver version.
5. **Redact + merge the schema spec** (strip hosts/credentials to a private appendix);
   kill the `bt_backtest_trades` duplication (pre-aggregate to (strategy, symbol, class,
   month)); add staleness assertions that fail CI.

## Phase 2 — Pre-registered pods (weeks 2–3; signed before any new data)

| Pod | Expression | Gate |
|---|---|---|
| **A. CRYPTO ensemble-grade LONG** | long when ensemble grade ∈ {A,B}/score≥60; symmetric vol-scaled exit (2×ATR trail or time stop); **no fixed TP**; dedup A⊂B | forward CI-LB>0 at day 90 |
| **B. `luxalgo_confluence` SHORT** | SHORT-only with BTC-regression + funding-rate covariates; require a second source; re-express as vol-targeted short sleeve | kill if forward CI-LB ≤ 0 at day 60 |
| **C. Equity/ETF breakout family** | family-level test vs a random-entry timing null | 30-day decision: promote or retire |

Concentrate emission to these 3 pods in 2 classes (CRYPTO SHORT + EQUITY/ETF LONG). Pause
emission everywhere else — the tribunal already shows those streams are negative net of
slippage.

## Phase 3 — Capital (weeks 4+)

- 70–85% low-cost beta core (index ETFs, TFSA/RRSP sheltering) + ≤25% satellites.
- Pods ≤5% sleeve, vol-targeted, −15%/−25% drawdown circuit-breakers.
- Paper sleeve tracked monthly vs benchmarks; **IR and down-capture on every card**; the
  benchmark leg is mandatory (BTC-hold for crypto SHORT, SPY for equity/ETF LONG).

## Realistic prize

If a pod survives, it is a **Sharpe ~0.5–1.0, low-correlation sleeve at small capacity** —
plus beta discipline and cost elimination. That, not "finding the winner", is the whole
game. audit3's job is to make sure nothing is mistaken for noise again, and that when
something real arrives, it is recognised.

*Not personalized investment advice.*
