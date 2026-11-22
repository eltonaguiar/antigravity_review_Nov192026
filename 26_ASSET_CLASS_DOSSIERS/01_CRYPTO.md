# 01 CRYPTO

Central question: why is PF published three ways, and does selection alpha stay negative
after intrabar-honest resolution?

## 1 Identity
[SRC: alpha_engine/money_ready_verdict.py:255] CRYPTO is one of the canonical classes.
[SRC: _raw/audit3_audit3_ledger.json] The ledger symbol bucket holds CRYPTO symbols such as BTC, AVAX, XRP, ARB, so membership is by symbol string, not by a stored class column.
[SRC: _raw/audit_data_money_ready_verdict.json] `/audit` also carries a separate MEME class, so a DOGE-style symbol can appear under either label depending on the producer.

## 2 What the class is
Crypto trades around the clock, has no closing auction, and has funding carry that equities lack. The structural edge candidates are funding carry, momentum, and mean-reversion.
[SRC: alpha_engine/funding_rate_arb.py] A funding-rate module exists, but no carry PnL is measured at class level this pass, so the carry hypothesis is UNVERIFIED.

## 3 Measured state
[SRC: _raw/audit3_audit3_ledger.json] Ledger class bucket: n 6926, WR 0.3939 CI [0.3824, 0.4054], PF net 0.7886 at class cost 0.0994 pct, gross expectancy -0.3189 pct, net -0.4183 pct, net CI [-0.699, -0.1602], 2x-cost CI [-0.7984, -0.2595] with stress_2x_ok false, DSR 0.0 against 374 trials, q 1.0, split-half unstable (first -0.2871, second -0.5496), verdict KILL.
[SRC: _raw/audit3_audit3_ledger.json] Selection alpha: pick -0.698 pct versus hold -0.1431 pct, alpha -0.5549 pct, CI [-0.9095, -0.208], alpha WR 0.4283.
[SRC: _raw/audit_data_dashboard_data.json] `/audit` readiness: gate_state MONITORING, sizing_allowed false.
[SRC: _raw/audit_data_money_ready_verdict.json] `money_ready_verdict` class verdict: NOT_READY.
The central question's second half is answered: selection alpha is negative and its CI excludes zero, so picking did worse than buying and holding the same symbols over the same windows.

## 4 Contradictions
[SRC: _raw/audit_data_dashboard_data.json] `/audit` readiness publishes CRYPTO PF 0.26 on n 22985.
[SRC: _raw/audit_data_money_ready_verdict.json] `money_ready_verdict` publishes PF 0.2621 on n 22287.
[SRC: _raw/audit3_audit3_ledger.json] `/audit3` publishes PF 0.7886 on n 6926.
These are three different statistics: the first two count all picks on the dashboard's own aggregation, the third counts canonical closed rows after per-class slippage. The plan's recalled values 0.83 and 0.92 do not appear in today's payload and are UNMEASURED.

## 5 Data integrity
[SRC: _raw/audit3_audit3_ledger.json] The ledger scores 8827 of 14914 closed picks (59.19 pct). Excluded cohorts: invalid_row 5891, mirror_duplicate 93, non_performance_exit 44, resolver_breakeven_fallback 59.
[SRC: _raw/audit3_audit3_ledger.json] Denylist hits for CRYPTO: 205 between 2026-11-19 and 2026-11-22.
[SRC: manifest:consistency_checks] The ledger's provenance path is `/tmp/audit3/dashboard_data.json`, but its recorded input_sha256 equals the live `/audit/data/dashboard_data.json`, so the input is exactly what is now served.

## 6 Cost reality
[SRC: _raw/audit3_audit3_ledger.json] The flat constant for CRYPTO is 0.0996 pct round-trip, labelled measured from `payload.slippage_validation` with 75 strategy costs and a minimum sample of 30.
[SRC: _raw/audit3_audit3_ledger.json] Mean hold is about one day, and even at 2x cost the CI stays negative, so the kill does not depend on the constant being right. Per-trade fill slippage is UNMEASURED.

## 7 What would change the verdict
[SRC: _raw/audit3_audit3_ledger.json] One experiment: rebuild the CRYPTO bucket from intrabar-honest first-touch resolution over the same 6926 rows, with the gate net PF CI-LB above 1.0 (the forward gate requires n 100). Falsifier: if the rebuilt CI still lies entirely below zero, the class stays killed regardless of cost assumptions.

## 8 Blunt answer
NO defensible edge today: negative selection alpha with a CI that excludes zero, and a class KILL.

Least survivable number: PF net 0.7886. It is an average over a bucket that mixes symbol cells with different cost models and sources, and verdict_churn already shows two CRYPTO cells flipping WEAK to KILL in one run [SRC: _raw/audit3_audit3_ledger.json].

## Provenance
- model: none (drafter fan-out blocked, see BLOCKERS.md B1; written by the curator from frozen evidence)
- prompt: none
- snapshot: `/audit3/audit3_ledger.json` 88606e1e… generated 2026-11-22T06:35:41Z; `/audit` payloads 2026-11-22T04:00Z
