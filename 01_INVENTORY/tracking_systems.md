# Inventory — Strategy / hypothesis / idea tracking systems

The project **does** have tracking — the problem is that it is fragmented and not unified
into one source of truth.

| System | Where | State |
|---|---|---|
| **Hypothesis registry** | `reports/hypothesis_registry.json` | **99 hypotheses** (H-001+, schema vX), each with id, asset_class, family, description, test_statistic, acceptance_criteria (min_wr/min_n/windows/eff_floor), economic_prior. Statuses are messy: prior review noted **28 raw spellings** for status. |
| **Hypothesis test harness** | `tools/hypothesis_test_harness.py`, `reports/hypothesis_test_results.json` | Exists; results in `reports/HYPOTHESIS_TEST_RESULTS.md` |
| **Idea tracker / theory tracker** | theory tracker section on `/audit` (H-020…H-025) | All KILL incl. H-024 G10 carry at n=950 — but tested as TP/SL picks, i.e. the wrong expression |
| **Strategy registry** | `strategy_registry/registry.py` + adapters; `tools/build_strategy_registry.py` | Registry envelope exists; strategy count ~47 `*strategy*.py` + ~400 root `.py` (heavy sprawl) |
| **Strategy graveyard** | `STRATEGY_GRAVEYARD.md`, `verified_strategies/`, `paper_pilot/` | Retired strategies + pilot states; 11 KILL strategies on the ledger |
| **audit3 tribunal** | `audit_dashboard/data/audit3_ledger.json`, kill_tribunal | **The only honest, consistent scoreboard** — it is the one place variance is actually controlled |
| **DSR / expectation gates** | `audit3_ledger.json.dsr_threshold` (0.95), `p_value` bootstrap | Built into audit3; 44 cells DSR-scored |
| **Per-class / per-strategy ledgers** | `audit_dashboard/data/*.json`, `cohort_reconciliation.json`, `blocked_registry.json` | Many sidecars; not all surfaced on any one page |
| **Paper trading / portfolio tracker** | `paper_trading/`, `portfolio_tracker/`, `positions.md`, `portfolio_history.html` | Paper records exist |

## The core tracking gap

- **There is no single ledger that unites hypothesis → variant → forward observation →
  outcome.** The 99 hypotheses, the 45 tested cells, the three outcome ledgers, and the
  theory tracker each count trials differently (`cumulative_trials` disagrees across
  `audit3`, `money_ready_verdict.py`, and the emitter — prior review, §2.4).
- Without that single forward-observation table, "did we tweak a variable and make money?"
  is unanswerable by the system; it can only be answered by re-running backtests, which is
  exactly what causes the "66,764 trades, only 11 retestable" problem.
- The **strategy-variable-tracking branch** (`add-strategy-variable-tracking`) exists as a
  git branch — i.e. the ownership recognises this gap but it is not merged into a canonical
  tracked table.
