# Shadow-control harness spec (reference)

**Purpose:** generate the forward rows audit3 needs to promote, without pausing emission.
The forward ledger is empty today; a shadow cohort that emits at paper size — including
known-losers as negative controls — is the only way to accrue the observations that make
`PROVEN_T2` reachable.

## Why

- audit3 can only re-score history; promotion needs forward rows.
- "Pause emission everywhere else" is in tension with needing forward data — so keep a
  *shadow* subset emitting.

## Design

| Component | What it is |
|---|---|
| Shadow cohort | The 3 pre-registered pods (P1/P2/P3) + 2 known-negative controls (e.g. crypto SWING, a coin-flip random-entry control) |
| Size | Paper only, ≤1% notional per name; never real capital |
| Benchmark leg | Every shadow pick records `benchmark_leg_ret` vs its class leg (SPY/BTC/AGG/GSG) |
| Cadence | Emit at the same cadence the production scanner uses (daily/hourly) |
| Resolver | Same `resolver_version` as production; intrabar-true first-touch required |
| Output | Appends to `forward_observations` via the ingestion adapter |

## Negative controls (mandatory)

1. **Random-entry control** — same symbols, same windows, random entry/exit; establishes
   the timing-null baseline.
2. **Known-KILL control** — e.g. CRYPTO SWING (already proven-harm). If the shadow harness
   shows it *winning* forward, that is a red flag on the resolver/ledger, not a real edge.

## Acceptance

The harness is "working" when:
- forward rows accrue daily (log shows `n_forward > 0`),
- ≥90% of rows carry `benchmark_leg_ret`,
- 100% have `intrabar_first_touch = 1`,
- the random-entry control's net CI straddles 0 (valid null).

## Wiring (source-repo changes, not done here)

1. Point the ingestion adapter at the shadow cohort's resolved rows.
2. Emit shadow rows to the same `forward_observations` pipeline as production.
3. Surface `n_forward` + the control CI on the audit3/audit2 pages.
