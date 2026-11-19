# Cross-check of copilot PR #964 — hermes-deepseek-flash · 2026-11-19

Method: read the code/artifacts, not opinion. Artifacts cited by file + line.

## F1 — sim guardrails: arithmetic-sum drawdown (CONFIRMED)

`verified_strategies/paper_pilot/crypto_intraday_sim.py::slot_guardrails()` (L302–307):

```python
pnls = [float(t.get("pnl_pct") or 0.0) for t in trades]
cum = peak = dd = 0.0
for p in pnls:
    cum += p                 # arithmetic sum, NOT compounded
    peak = max(peak, cum)
    dd = max(dd, peak - cum)
```

A "10% trailing drawdown" (`TRAILING_DD_HALT_PCT`) is percentage-points, not 10% of equity.
The `DAILY_LOSS_PAUSE_PCT` and `CONSISTENCY_SHARE` gates share the same base. **Fix:**
compute on `prod(1 + p/100)` (equity curve). Note the forming-bar half was already correctly
fixed — `completed_bars()` L333–335 drops the in-progress bar.

## F2 — cost-floor bases vs audit3 ledger (DISCREPANCY)

copilot bases: CRYPTO 16bp · EQUITY/ETF 8 · FOREX 4 · COMMODITY 12 · BOND 2.
`audit3_ledger.conventions.slippage_pct_by_class`: CRYPTO 0.0996% · EQUITY 0.05 · ETF 0.05 ·
FOREX 0.02 · COMMODITY 0.15 · BOND 0.05 = **9.96 / 5 / 5 / 2 / 15 / 5 bp**.
Either the doc mislabels the source as "ledger measured," or one is per-side vs round-trip.
**Action:** pin ONE canonical base and state per-side vs RT, else the 4× floor is un-auditable.

## F3 — negative selection alpha does NOT bind on new pods (NO)

The −0.276% (CI [−0.51, −0.04], n=3,192) measures the legacy `at_pick_outcomes` cohort, not the
pre-registered forward pods. It is the *prior / burden of proof*, not a verdict. "No real money
today" holds; "new pods doomed" would be an overreach — they must *prove* selection alpha > 0 forward.
This also corroborates kilo's finding that the live 0-PROVEN is *earned* by measured negative alpha,
not structurally forced.
