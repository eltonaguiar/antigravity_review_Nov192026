# DEFECT: 46% of `at_pick_outcomes` are EXPIRED rows carrying `pnl_pct = 0`, not real outcomes

**Hermes · 2026-11-24 23:40 EST** · script `zero_mass_probe.py` · read-only DB queries

---

## What is wrong

| | rows | share |
|---|---:|---:|
| total | 63,792 | 100% |
| **`pnl_pct` exactly 0** | **29,577** | **46.4%** |
| positive | 14,166 | 22.2% |
| negative | 20,049 | 31.4% |

The zeros are not a market distribution. They are **one status**:

| status | n | rows with `pnl_pct = 0` | share zero |
|---|---:|---:|---:|
| **EXPIRED** | 29,654 | **28,531** | **96.2%** |
| FLAT | 1,046 | 1,046 | 100% |
| WON | 13,654 | **0** | 0.0% |
| LOST | 19,438 | **0** | 0.0% |

**`WON` and `LOST` are clean** — every one carries a real return. `EXPIRED` carries no P&L at all and is
stored as a flat **0**.

## Why this matters

Every per-class statistic computed over the full table includes 29,577 rows that are not outcomes:

- **Every median is 0.00** — because 46% of the mass sits exactly at zero, so the median *is* the zero mass
  rather than anything about the strategies. That is why the cost-gate table printed `median bp = 0.00`
  for 11 of 14 classes. It was not measuring a strategy; it was measuring the expired pile.
- **Every mean is diluted by roughly half** with rows that returned nothing and were never supposed to.
- **The cost-gate verdict table** (`COST_GATE_BY_CLASS.md`) is therefore built on the wrong denominator.
  Its conclusion may still be right, but not for the reason it states — and the breakeven-cost numbers
  per class are not usable as published.

Including this in the changelog's per-class section today was **my** error. It is corrected below and on
the page.

## What the data actually says — resolved trades only

`status IN ('WON','LOST')`, n = 33,092:

| status | n | mean | median | min | max |
|---|---:|---:|---:|---:|---:|
| WON | 13,654 | **+3.02%** | +3.00% | −3.81% | +427.95% |
| LOST | 19,438 | **−2.01%** | −1.66% | −100.00% | +2.34% |

Units are consistent and sane: percent, floor at −100 (total loss), a long right tail to +428%. That part
of the table was fine — the earlier "−12,300 bp" figures I flagged were −1.23%, correctly converted, and
I mis-read my own output before checking. **No units defect.**

Combined expectancy across resolved trades:

```
(13,654 × 3.02% + 19,438 × −2.01%) / 33,092 = +0.065%
```

**+0.065% per resolved trade, gross, before cost.** That is the honest headline number for the whole
book — and it is an order of magnitude below any realistic round turn (26 bp for the portfolio side,
36 bp for crypto).

## So the conclusion survives, but the table does not

**Cost still kills everything**, which is what the programme has been saying. But it now rests on
+0.065% gross expectancy over 33,092 genuinely resolved trades, not on a table where half the rows were
placeholder zeros. The distinction matters: one is a measurement, the other was an artefact that happened
to point the same way.

## Required repair

1. **Exclude `status = 'EXPIRED'` from every expectancy, cost and win-rate computation.** Expired is an
   *administrative* outcome, not a trading one. If an expired pick needs a return, it must be resolved
   against the price at expiry — storing 0 is not a resolution.
2. **Re-run `COST_GATE_BY_CLASS.md` on resolved trades only** and re-issue every per-class verdict and
   breakeven-cost figure.
3. **Add a row-count assertion at the filter step**: print `n` before and after the EXPIRED exclusion so
   a future reader can see the 29,577-row drop rather than discover it.
4. **Decide what EXPIRED should mean.** 29,654 picks (46% of the table) reaching neither TP nor SL and
   being written off as flat is itself a finding about the exit logic — `TIME_EXIT_MAX_HOLD` already holds
   31,421 picks in `trading_picks`. Two tables, same problem: positions that neither hit a target nor a
   stop and are simply timed out.
5. **Correct the published changelog** per-class section — done at this commit.

## Reproduce

```bash
python3 zero_mass_probe.py    # mass measurement, status breakdown, resolved-only stats
```

Read-only. No writes, no schema changes.
