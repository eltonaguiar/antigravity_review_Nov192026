# 37 — Buffy draft patches, 2026-11-23

**Nothing here is applied.** Three drafts, one decision each, for review. Every hunk is a real
`git diff` and every file passes `git apply --check` against its target tree (§Verified). Nothing is
pushed.

| # | Draft | Target | Needs |
|---|---|---|---|
| 01 | `01_contest_scorer_residual.patch` | `CONTEST/tools/assess_contest.py` (this repo) | contest owner, before R02 opens |
| 02 | `02_dsr_canonical_pointer.patch` | `alpha_engine/{deflated_sharpe.py,validation/sharpe_metrics.py}` (research tree) | operator, since it changes a pointer other gates read |
| 03 | `03_equity_cost_settlement.patch` + `03_equity_cost_settlement.md` | `tools/cost_of_record.py` (research tree) + COST_OF_RECORD rows | **operator decision** on the bracket rule |

---

## 01 — the peer fix works, and four residuals survive it

Commit `71da0b4` ("peer review caught 3 real defects in my scorer…") applied the round-start fill,
the fund horizon cap and net `$`. **Verified in the patched file, with `--round-start`, on the exact
panel that failed before:**

```
SPY   OK   entry=690.0  exit=730.0  R=+2.6358  usd=+28.65   tp
VTSAX OK   entry=100.0  exit=100.0  R=None     usd=  0.00   horizon
```

That is correct. Four things are not:

- **R1 — the fix is opt-in.** It is guarded by `if ROUND_START is not None`, and `--round-start`
  defaults to `None`. Omit the flag (as every existing invocation and my first probe did) and the
  fill silently reverts to `series[0]`, the oldest bar in the panel. A scorer whose correctness
  depends on a flag the caller may forget is the exact shape of the bug that produced R01.
  Draft makes the flag mandatory and exits 1 with a message.
- **R2 — the twin bug is still live.** The fund branch was fixed; the bracketed-pick branch was not.
  It still ends at `series[-1]["close"]`. Measured: QQQ, `horizon_hours=2`, panel running to
  2026-12-31 → **exit 945.0 from a 690 entry, R +2.83, labelled `reason="horizon"`**. A pick that
  touches no barrier is scored on the end of the file, not the end of its horizon.
- **R3 — `--fill-relative` rewrites the entrant's R:R.** `clamp_brackets` reads `p.get("entry")`,
  which the scorer never writes, then falls back to the bracket *midpoint*. `entry_ref_price` — the
  field the RULES define — is never read. Measured: tp 730 / sl 675 on a 690 market is risk 15,
  reward 40 = **2.67R**; the midpoint 702.5 yields risk 27.5, reward 27.5 = **1.00R**
  (`clamp_brackets -> (27.5, 27.5)`). The clamp silently symmetrises every asymmetric bracket, which
  is the opposite of its stated purpose.
- **R4 — crypto is charged one band.** `COST_BP` has a single `"crypto": 52.0`, but COST_OF_RECORD
  defines major 20 / alt 52. Every BTC/ETH pick is charged the alt band — 2.6× too much, in the
  direction that makes the class look worse. Draft adds `cost_bp_for()` with a majors set.

## 02 — the pointer is inverted, and circular

`alpha_engine/deflated_sharpe.py` says *"DEPRECATED: use `validation.sharpe_metrics` (canonical)"*.
`validation/sharpe_metrics.deflated_sharpe_ratio` takes **no trial count** and returns
Sharpe/SE — 31.0548 at N=1 and at N=4987 alike. And its own docstring says *"for a real deflation use
`alpha_engine.deflated_sharpe`"*. **The two point at each other; neither points at
`statistical_rigor.py`, which is the one that actually deflates.** That circular reference is the
entire cause of the "6 DSR values, 26.3× spread" dispute in `FINAL_PICKS/STATUS.md`.

Draft: repoint the deprecation to `statistical_rigor`, correct the circular docstring, and add
`sharpe_t_stat()` as the honest name (old name kept, so no call site breaks).

## 03 — equity cost: settle the bracket, not the number

See `03_equity_cost_settlement.md`. Short version: `tools/equity_cost_reconcile_191.py` already runs
all three estimators on the same 191 names, so 0.9756 / 4.0124 / 12.0749 are a **floor / central /
ceiling**, not three competing costs. The patch names them, makes the central estimate the
verdict-grade record, emits the bracket, and fixes a latent bug found on the way: stdout printed
`min(measured)` while the JSON printed `measured[0]`, which are different rows once more than one
measured cost is in flight.

---

## Verified

```
git apply --check  01_contest_scorer_residual.patch    (review repo)     -> APPLIES
git apply --check  02_dsr_canonical_pointer.patch      (research tree)   -> APPLIES
git apply --check  03_equity_cost_settlement.patch     (research tree)   -> APPLIES
```

No file in either tree was modified to produce these. Working copies were made under `/tmp`, edited,
diffed, and the patches checked against the real trees; the working copies were then discarded.

*Zero capital. Paper only. Not investment advice.*
