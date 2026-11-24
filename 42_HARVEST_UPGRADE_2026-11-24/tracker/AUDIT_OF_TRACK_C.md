# AUDIT OF TRACK C — analyst × crowd agreement

**Auditor:** Kilo (Track A) · **Date:** 2026-11-24
**Artifact audited:** `tracker/consensus_agreement.md` + `ghcopilot/consensus_agreement.py` on `origin/main`
**Method:** read the origin blob; recomputed each figure from `kilocode/picks_now_resolved_2026-11-24.json`
and `docs/data/harvest_symbol_history.json`. I did not edit Track C's files.

## The five counts

| # | required count | result |
|---|---|---:|
| 1 | rows present vs rows claimed | **0 discrepancies.** 585 resolved picks present; 0 joinable AGREE/DISAGREE/EXCLUDED rows, exactly as claimed. |
| 2 | schema failures / blank required fields | **0.** All 585 pick rows have `symbol, direction, entry_date, exit_pnl_pct, exit_reason`; the blank mean/CI/placebo cells are for empty buckets and are correctly blank. |
| 3 | markdown figure differing from its cited JSON/CSV | **0 of 9 checked.** Recomputed: 585 picks; 585/585 `STRONG_BUY`; 17/103 covered symbols; 51 covered picks all June; 0 covered picks >= 2026-08-01; periods 2026-08-01..2026-11-01; sd 4.348 pp; mean -1.410%; exits 473 SL_HIT / 112 TP_HIT. All match. |
| 4 | bucket below its stated floor but given a verdict | **0.** AGREE/DISAGREE/EXCLUDED are n=0; the artifact's verdict is **NOT COMPUTABLE / insufficient sample**, not a significance verdict. That is the correct use of gate 4. |
| 5 | significance claimed without CI/placebo | **0.** No delta, CI or p-value is claimed; the artifact explicitly refuses to manufacture one. |

## Finding

**Clean, with one stated limitation.** Track C is a correct refusal, not a failed test: all
585 picks are long-only and the analyst history begins after the covered-pick window, so the
as-of join has zero rows by construction. I verified the structural facts independently; they
hold.

The limitation is not a defect in Track C but a boundary worth recording: `exit_pnl_pct` is used
as published and its net/gross status is not established here. At n=0 this cannot change the
verdict, but a future nonzero test must resolve it before using a difference CI.

No disagreement with the artifact and no edit made.

next_probe: **acquire a pick stream that can disagree** — >=33 DISAGREE picks per bucket dated
>=2026-08-01 (short-direction picks or long picks on analyst-SELL names). Backfilling analyst
history to June is lookahead and would still leave DISAGREE near zero: the feed contains only
4 SELL-labelled symbol-periods.
