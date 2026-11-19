# Implementation status & next actions (2026-11-19)

Reconciled against the source repo **after** the peer work landed. Two of the "missing
table / missing wiring" gaps identified earlier are now partially built; the rest is open.

## What already exists in the source (peer-built, verified)

| Item | Status | Evidence |
|---|---|---|
| `forward_observations` schema + validator + promotion rule | **built** | `alpha_engine/forward_observations.py`; `tests/test_forward_observations.py` (24 tests); `reports/forward_observations.jsonl` exists but is **0 rows** |
| Canonical resolved view (`resolved_closed_picks_net`) | **built** | `alpha_engine/resolved_closed_view.py`; `tests/test_resolved_closed_view.py` |
| audit3 tribunal now splits confirmatory/discovery + gates on forward rows | partially | `alpha_engine/audit3_tribunal.py`; pre-registered pod `POD-EQUITY-BREAKOUT` in `reports/audit3_confirmatory.json` |
| H-119 registry vintage refreshed (n=431) | built | `updates/2026-11-19-forward-observations-contract.md` |

## Remaining gaps (the actual next coding steps)

1. **Forward-ledger ingestion adapter.** `forward_observations.py` "cannot read MySQL
   here" — the ledger is empty and `PROVEN_T2` is unreachable from forward evidence. Add a
   MySQL ingestion adapter + a connector that appends resolved, intrabar-true, benchmarked
   rows from the live ledger feeding the clinical clock.
2. **Wire the promotion rule into `audit3_tribunal`** so `PROVEN_T2` is *gated* on
   forward rows (not merely defined). This is deliberately separate and next.
3. **Adopt the audit2 page** (`06_AUDIT2_PAGE/audit2.html`) — register `/audit2` in the
   deploy manifest and point its fetches at `reports/audit3_confirmatory.json` +
   `reports/forward_observations.jsonl`.
4. **Fix the crypto stop-fill overshoot** (98.8% of the crypto class loss): resolve stops
   against intrabar OHLCV (fill at stop when bar breaches; at close on gap). This moves
   crypto PF 0.768 → ≈1.00 and unblocks all crypto signal work.
5. **Cost gate on every record** (2× costs, one-bar delay) wired into
   `money_ready_verdict.py`; benchmark legs everywhere.
6. **Crypto POSITION-horizon forward test** (a=33, WR 69.7%, PF 3.18) after #4; kill
   SWING.
7. **Schema-spec redaction** before any external paste.

## What I am shipping now

- `06_AUDIT2_PAGE/` — standalone audit2 page + sample data sidecars (this turn).
- `06_IMPLEMENTATION_STATUS.md` — this reconciliation (this turn).
- Earlier turns: findings, tunable variables, forward path, audit2 content spec, evidence
  index, peer review.

No source-repo files were changed by this work; everything lives in the review repo.
