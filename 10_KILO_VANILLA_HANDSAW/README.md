# 10_KILO_VANILLA_HANDSAW — measured confirming review

**Reviewer:** Kilo, worktree `vanilla-handsaw`
**Source checkout:** `findtorontoevents_antigravity.ca` @ `f9e6c8202a1` (branch
`add-strategy-variable-tracking`, 2026-11-19 06:13 UTC)
**Artifact repo:** `eltonaguiar/antigravity_review_Nov192026`, branch `kilo-review`
**Date:** 2026-11-19

This is a **third independent pass** over the financial-prediction surfaces
(`/audit`, `/audit2`, `/audit3`, `/audit/hyrotrader`, recent `.MD`, DB schema).
It exists to (a) re-derive the headline numbers from files rather than memory,
and (b) add measured evidence the other folders did not carry.

## Files

| File | Purpose |
|---|---|
| [`FINDINGS_MEASURED.md`](FINDINGS_MEASURED.md) | Diagnosis + new measured evidence (§A–§J), verified against source files |
| [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) | Every claim → exact file path / line / value / commit |
| [`../METHODOLOGY_NOTE.md`](https://github.com/eltonaguiar/AGENT_FOLDERFRAMEWORK/blob/main/2026-11-19-KILO_MEASURED_AUDIT_METHODOLOGY.md) | Methodology applied (in the framework repo) |

## What this pass adds (not already in `02_FINDINGS/` or `05_KILO_REVIEW/`)

- **Reproducibility gap (§A):** `audit_dashboard/data/dashboard_data.json` is
  absent from the repo and untracked; `/audit` cards cannot be re-derived from
  any committed artifact. `cohort_reconciliation.json` flags
  `published_disagreement` (ETF 14d PF 1.0158 vs 0.345; EQUITY 0.6576 vs 0.30).
- **Different denominators (§A/A2):** `audit3_ledger.json` scores a
  `payload_slice` (3,500/16,330 = 21.43%) and says so — "NOT the same
  denominator as /audit". Comparing tiles across surfaces compares different
  populations. Verified verdicts: 0 proven / 1 candidate / 34 weak / 10 kill;
  CRYPTO KILL (n=1,851, WR 40.19%, PF 0.7474, DSR 0.0); 3,467 expired-zero-PnL
  resolver rows, 44 exits beyond the planned stop, 23 clamped losses.
- **Ghost-row cohort detail (§B):** 22,947 rows; top cohort MEMECOIN
  `meta_strategy` DOGEUSDT LONG, n=3,569 from **one** distinct entry. The
  `db_health.json` harness itself reports `checks_failed=2`, `any_red=true`,
  `harness_healthy=false`, `banner_should_show=true`.
- **Blocklist bypass (§C):** 165 retired-strategy picks still emitting
  (e.g. `multi_asset_forex_rsi2_mean_reversion::AUDJPY=X::2026-11-19_0222`),
  proving the kill tribunal is advisory, not wired to emission.
- **Batch artefacts (§D):** 7-row `kimi_riseoftheclaw` batch swings PF
  0.1246→0.2926; small-N batches distort the surfaced PFs.
- **`strategy_perf_by_class.json` is self-declared non-edge (§E):** 961 cells
  whose own `note` says "NOT edge-proven".
- **Hyrotrader staleness (§H):** account snapshot 2026-04-08 (equity 4,929.34,
  −70.66 USDT, 0 trading days logged), backtests 2026-04-07, ledger files 359 B /
  222 B — far from any "123 closed picks / $123.45" claim.
- **Schema Appendix A (§J):** `fx_prices` ends 2026-02-09 → 211 forex picks have
  no computable alpha; all 285 `bt_backtest_runs` tagged CRYPTO incl. FX symbols;
  `bt_backtest_trades` ≈32.7M rows.

## Reconciliation with the other folders

- **Agrees** with `02_FINDINGS/why_no_wins.md` (ratchet-to-zero, WR gate
  mis-specified, TP-first exits, data debt, no forward ledger) and with
  `05_KILO_REVIEW/FINDINGS_ROOT_CAUSE.md` (no positive selection alpha; exit
  geometry + cost; leaky walk-forward; fragmented tracking).
- **No contradiction found.** Where numbers overlap they match (0 PROVEN,
  22,947 ghost rows, 0/9 money-ready, ~21% audit3 coverage).
- **Scope note:** `00_CHARTER.md` puts source-repo code changes out of scope.
  This folder therefore proposes no edits to `findtorontoevents_antigravity.ca`;
  `05_KILO_REVIEW/PLAN.md` already holds the sequenced recovery plan.
- **Checkout note:** `05_KILO_REVIEW` cites main tip `1cd4f6527ee`; this pass
  cites worktree `f9e6c8202a1` on `add-strategy-variable-tracking`. Both postdate
  the same 2026-11-19 data generation, but a future reader should re-run the
  evidence index against whichever tip they check out.

## Verification status

Every numeric claim in `FINDINGS_MEASURED.md` was re-read from its source file on
2026-11-19. Three first-draft errors were caught and corrected during that pass:

| Draft claim | Verified reality |
|---|---|
| `dashboard_data.json` "3,500 rows, 44 MB, not tracked" | File is **absent** from the worktree and untracked; live copy recorded 3,500 records @ 2026-11-19T04:04Z |
| `paper_trading.csv` "symbols COINBASE:FILUSD, BITSTAMP:BTCUSD" | 14 rows across **6** symbols, all placed 2026-03-06 |
| "price/market-data tables absent" | They **exist in the DB** (crypto_ohlcv 1.7M, …) but are **omitted from the spec**; `fx_prices` is stale |

*Not personalized investment advice.*
