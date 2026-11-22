# 10 MEMECOIN

Central question: is a tiny-n, near-zero PF the real story, or is it ghost-row inflation?

## 1 Identity
[SRC: alpha_engine/money_ready_verdict.py:255] Not one of the canonical classes; the surfaces call it MEME.
[SRC: _raw/audit_data_money_ready_verdict.json] DOGE-USD dominates the sample (top_symbol_share 0.4), and the ledger has no MEME bucket, so the only numbers are on `/audit`.

## 2 What the class is
Meme coins are narrative-driven, extremely volatile, and have no cash flow. The candidate edge is momentum around attention spikes; the structural risk is total loss.

## 3 Measured state
[SRC: _raw/audit_data_dashboard_data.json] `/audit` readiness: n 10, WR 10.0 pct, PF 0.02.
[SRC: _raw/audit_data_money_ready_verdict.json] `money_ready_verdict`: n 10, PF 0.0234, WR 0.1, INSUFFICIENT_DATA, intrabar_truth null, intrabar_daily_divergence gate_source legacy_fallback, MDD 0.4936 and CVaR 95 -13.85 pct, both failing their gates.

## 4 Contradictions
The plan recalled ghost-row inflation.
[SRC: _raw/audit_data_money_ready_verdict.json] Today the surface reports intrabar_truth null and honest_pf null, so there is no honest-versus-daily pair to compare: the inflation question is UNMEASURED this pass, not answered. The solid numbers are n 10, PF 0.02, and the MDD/CVaR fails.

## 5 Data integrity
[SRC: _raw/audit_data_money_ready_verdict.json] n 10 with 40 pct of rows on one symbol and 100 pct from one source; both concentration caps are triggered.

## 6 Cost reality
[SRC: _raw/audit3_audit3_ledger.json] The ledger conventions assign MEME 0.3 pct round-trip, the highest with PENNY_STOCK. Given a 10 pct WR, cost is not what kills it, and measured slippage is UNMEASURED.

## 7 What would change the verdict
[SRC: _raw/audit_data_money_ready_verdict.json] One experiment: resolve meme rows intrabar-honestly and compare daily versus honest PF. Gate: honest PF above 1.0. Falsifier: if honest PF is below daily PF, the daily number is inflated and the class is worse.

## 8 Blunt answer
[SRC: _raw/audit_data_money_ready_verdict.json] NOT PROVEN, leaning NO: PF 0.02 at n 10 with a 49 pct drawdown. The ghost-row question is unmeasured.

[SRC: _raw/audit_data_money_ready_verdict.json] Least survivable number: PF 0.0234. Ten trades with one symbol at 40 pct, so one lucky trade moves it several-fold; the WR 10 pct is equally fragile.

## Provenance
- model: none (drafter fan-out blocked, see BLOCKERS.md B1; written by the curator from frozen evidence)
- prompt: none
- snapshot: `/audit/data/money_ready_verdict.json` b5387de5… generated 2026-11-22T03:58:43Z
