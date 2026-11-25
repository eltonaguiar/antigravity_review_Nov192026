# Is the 96.4% TIME_EXPIRED zero rate a defect, or a natural terminal state?

zoo-savant, 2026-11-25. Measured read-only from `ejaguiar1_stocks.at_pick_outcomes`.

## The measurement

| status | resolution_method | n | zero | zero % | non-zero n | non-zero mean | non-zero median |
|---|---|---|---|---|---|---|---|
| EXPIRED | TIME_EXPIRED | 29,506 | 28,430 | **96.4%** | 1,076 | -1.3035 | -0.0678 |
| LOST | SL_HIT | 18,537 | 0 | 0.0% | 18,537 | -2.0414 | -1.7300 |
| WON | TP_HIT | 12,417 | 0 | 0.0% | 12,417 | +3.2681 | +3.0000 |
| EXPIRED | MANUAL | 51 | 4 | 7.8% | 47 | +0.0006 | +0.0014 |

## The case FOR "natural terminal state"

- A pick whose window closes without touching TP or SL has no *realised* event, so
  a resolver could legitimately record 0 as "nothing happened".
- If that were the rule, the zeros would be a deliberate encoding of "unresolved",
  and 96.4% is simply the share of picks that expired quietly -- which for
  mean-reverting or wide-bracket picks could genuinely be most of them.
- Supporting detail: the **1,076 non-zero TIME_EXPIRED rows** show this code path
  *can* mark to market (median -0.07%, mean -1.30%). So the capability exists, and
  the zeros are then a choice rather than an inability.
- The EXPIRED/MANUAL rows (51 total, only 7.8% zero) behave like a proper mark.

## The case FOR "defect"

- **The same table stores real marks elsewhere.** TP_HIT and SL_HIT are 0% zero,
  and 1,076 TIME_EXPIRED rows are non-zero. So 0 is not the table's only way to say
  "expired" -- it is one of two encodings for the same state, which is the classic
  signature of a placeholder rather than a definition.
- **0 is also a real return.** A pick that closed exactly flat is indistinguishable
  from "never priced". 96.4% of expiries being exactly flat is not credible for
  volatile assets: CRYPTO's median resolved return is -100 bp elsewhere in the same
  table, so exact zeros at this rate are an encoding, not outcomes.
- **It corrupts aggregates in a measurable way.** Including them halves every class
  mean and forces every median to 0.00 (the cost-gate repair on origin measured
  exactly this), and `status` was the only field that identified them.
- **The non-zero expiries are not neutral**: mean -1.30% says that when the window
  closes and the row *is* priced, the pick is usually under water. Storing 0 instead
  is a systematic optimistic bias, not a random omission.

## Which does the data favour?

**The defect reading, and the deciding evidence is the mixture.** If TIME_EXPIRED
meant "window closed, nothing happened", the rows would be homogeneous. They are
not: 96.4% are exactly 0 and 3.6% carry a mark whose mean is -1.30% -- i.e. the
priced ones are clearly negative while the unpriced ones are recorded as exactly
neutral. A natural terminal state would not produce that split; a resolver that
writes 0 when it fails to obtain a price would. The 7.8% zero rate for
EXPIRED/MANUAL reinforces it: when a human resolves the same terminal state, the
zeros nearly disappear.

## What EXPIRED should mean

EXPIRED should record the **mark-to-market return at window close** (the same
`pnl_pct` a TP_HIT or SL_HIT records), with a separate status or flag for
"no price was available". Storing 0 is not a resolution: it asserts a flat outcome
that was never measured. A defensible schema keeps three distinct states --
`EXPIRED_PRICED` (window closed, has a mark), `EXPIRED_UNPRICED` (window closed,
no price -- excluded from aggregates, never counted as 0), and `FLAT` (a genuine
0.00 return, which is what the 1,044 FLAT/MANUAL rows are).

next_probe: backfill the 28,430 unpriced expiries from historical bars where the
symbol still resolves, and report how many can be priced -- if most can, the 0 was
purely an ingestion gap and every class mean published before the exclusion was
biased toward zero by roughly half.
