# FX backfill — dry-run result and blocker (2026-11-19)

**Tool:** `tools/fx_backfill.py` (already on `main`).
**Status:** dry-run **PASS**; `--apply` **BLOCKED on DB credentials** (by design — no
secrets are read by this agent).

## Dry-run output

```
pairs to backfill: 15
estimated rows (business days x pairs): 3045
No network and no database were contacted. Re-run with --apply to write.
```

Per-pair plan (`symbol -> vendor -> days`): AUDJPY, EURJPY, GBPJPY, EURCHF,
AUDCAD, CADJPY, GBPCAD, EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD,
USDMXN — each `203` business days (from 2026-02-09, where `fx_prices` stops).

## Exact command to apply (operator, with creds)

```bash
# from a checkout of main, with the DB env used by the other tools
python3 tools/fx_backfill.py --apply
# then re-run the ledger so forex selection-alpha can compute:
python3 -m alpha_engine.audit3_tribunal --picks /tmp/audit3/dashboard_data.json \
  --out audit_dashboard/data/audit3_ledger.json \
  --history audit_dashboard/data/audit3_verdict_history.json --history-write \
  --prev-ledger audit_dashboard/data/audit3_ledger.json --max-churn 0.30
```

## Why it matters

FOREX is KILL on the canonical book and its selection alpha is uncomputable
because `fx_prices` ends 2026-02-09 and the symbol mapper was broken. The mapper
is already fixed (`AUDJPY=X`/`AUD-USD`/`AUD/JPY` → `AUDJPY`, PR #910); the
backfill is the remaining half. Until it runs, every FOREX pod stays `observe`
and no forex window can clear the forward gate.

## Follow-ups
- Review the USDT→CRYPTO carve-out in `audit_trail/asset_classification.py`
  (`EURUSDT` currently classified FOREX) — reclassifies rows, needs its own PR.
- After the backfill, re-run `alpha_engine/audit3_selection_alpha.py` and confirm
  FOREX alpha is no longer null.

*Not investment advice.*
