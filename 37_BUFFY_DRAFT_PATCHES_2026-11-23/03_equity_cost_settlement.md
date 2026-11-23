# 03 — Settle the EQUITY cost: it was never a disagreement, it was three estimators quoted as one

**Status:** DRAFT for review. Nothing applied. **Decision needed from the operator** (§4).
**Supersedes:** the single-number reading of both `12.0749` and `4.98` in
`34_FINAL_PICKS_2026-11-23/COST_OF_RECORD.md`.

---

## 1. What is actually in the estate

`tools/equity_cost_reconcile_191.py` already runs **all three estimators on the same 191 names and
the same cached bars**. That means the "12.4× conflict" I flagged on COMS is not two measurements
disagreeing — it is one cost distribution, sampled by three estimators with different availability:

| Estimator | Value | Usable on | What it is |
|---|---|---|---|
| Corwin-Schultz + SEC (`0.7696 + 0.206`) | **0.9756 bp** | **65 / 191** names | a **FLOOR** — volatility swamps the estimator on the other 126, so it is measured only where the spread is easiest to see |
| Roll + SEC | **4.0124 bp** | **190 / 191** | the **central point estimate** |
| 1-min bar-range upper bound, 13 names | **12.0749 bp** | 13 megacaps | a rigorous **CEILING** — a bar range bounds the spread from above, it cannot be below it |
| (2× central) | **8.0248 bp** | — | the **gate** |

The reconcile artifact's own verdict, computed not asserted:

> *"4.98 bp is NOT verdict-grade: 0.7756 of it is a measurement of the spread, 0.206 a statutory fee,
> and 4.0 an assumption. Use the bracket [0.98 bp measured floor, 12.0749 bp bound] and require the
> 2×-cost gate to hold at the upper end."*

So the settlement is not a winner among three numbers. It is: **stop quoting one number.**

## 2. Why each of the three was defensible and each was wrong on its own

- **0.9756 quoted as "the cost"** understates it 4.1× against the central estimate, and it is
  measured only on the 65 names where Corwin-Schultz works. It is the number most likely to make a
  dead strategy look alive — which is why it must never be graded.
- **4.98 quoted as "the cost"** is a floor plus a 4.0 bp **assumption** presented as a measurement.
  It is the number in the current table's "Equity (spread only), measured, LOWER BOUND" row, and
  the label is honest — but a lower bound that omits commission and impact is not a cost.
- **12.0749 quoted as "the cost"** is an upper bound from 13 megacaps on 1-min bars. My own number.
  It is labelled correctly in the table today ("superseded for EQUITY"), and that labelling is the
  reason the table is trustworthy. It stays as the ceiling, not as the record.

## 3. The change (patch 03, drafted, applies cleanly)

`tools/cost_of_record.py`:

1. Adds the bracket as four named constants with provenance, so no downstream consumer has to
   re-derive it.
2. Adds `equity_191_reconciled_central` (4.0124) as a **verdict-grade MEASURED** entry, which makes
   `min(measured)` select the central estimate instead of the floor — the settlement, expressed in
   the tool's own selection rule rather than in prose.
3. Emits `equity_cost_bracket` in `reports/cost_of_record_2026-11-23.json` with the rule attached.
4. Fixes a latent bug found while doing this: the stdout printed the *minimum* measured cost while
   the JSON payload used `measured[0]` (**list order**). With more than one measured cost in flight
   those are different rows, so the JSON could disagree with the stdout that produced it. Both now
   use the same object.

## 4. The decision this needs (not mine to make)

**Proposed COST_OF_RECORD.md replacement rows** — replace the two EQUITY rows with three:

| Class | Round trip (bp) | Basis | Provenance |
|---|---|---|---|
| **Direct equity — central** | **4.0124** | measured, central | Roll + SEC, 190/191 names, same cached bars as the floor (`tools/equity_cost_reconcile_191.py`) |
| **Direct equity — floor** | 0.9756 | measured, **FLOOR — never grade here** | Corwin-Schultz + SEC, only 65/191 usable |
| **Direct equity — ceiling** | 12.0749 | measured, **CEILING — grade here** | 1-min bar-range upper bound, 13 names |

And one new rule in "Rule going forward":

> 4. **Report the central, grade at the ceiling.** A verdict computed at the floor is not a verdict;
>    it is an upper bound on a verdict. The 2×-cost gate (8.0248 bp) is the survival test.

## 5. Consequence to re-run, not to assume

`VERDICTS_AT_RISK` currently grades EQUITY breakout at **50.0 bp** — an ASSUMED stress constant, 12.5×
the central estimate — and the note says the verdict is cost-robust because PF < 1 is a signal
failure. That reasoning survives the change. What does **not** survive unexamined is any EQUITY
verdict decided between 4.0124 and 12.0749 bp: those flip inside the bracket itself, and they must be
re-labelled `CANDIDATE-CONDITIONAL` rather than `DEAD` or `ALIVE` until a commission-bearing
measurement exists. The reconcile artifact names what is still unmeasured: commission, ECN, slippage
beyond the quoted spread, and **realised fill prices — which do not exist anywhere in this repo.**

*Zero capital. Not investment advice.*
