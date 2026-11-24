# Deployment log — R1 insider Form 4 per-owner fix

**Deployer:** Kilo · **Date:** 2026-11-24
**Target:** `12_INSIDER/collect_form4.py` per-owner attribution
**Source handoff:** `42_HARVEST_UPGRADE_2026-11-24/DEPLOYMENT_HANDOFF.md`

## Commands

```bash
python3 12_INSIDER/collect_form4.py \
  --tickers AAL,AFRM,CCL,COIN,CVNA,F,HOOD,INTC,LCID,M,MU,PARA,PFE,PLUG,PTON,RIVN,RUN,SMCI,SOFI,T,UPST,VZ \
  --max-filings 60 \
  --out /tmp/form4_fixed.csv \
  --summary /tmp/form4_fixed.md
```

Parser change: each `reportingOwner` block is parsed separately (`rptOwnerCik`/`rptOwnerName`,
`isOfficer`, `isDirector`, `isTenPercentOwner`, `officerTitle`), then one row is emitted per owner per
non-derivative transaction. The old code used the first owner's flags for every transaction.

## Counts

| measure | fixed run |
|---|---:|
| total transaction rows | **2,640** |
| distinct P transactions (symbol/filing/date/shares/price key) | **46** |
| P owner-rows (after per-owner expansion) | **52** |
| P owner-rows with officer-or-director true | **48** |
| distinct P transactions with at least one O/D owner | **44** |
| distinct P transactions with O/D and not 10%-owner | **31** |

Frozen context: **46 purchases**, **7 officer-or-director rows**, 2,616 rows.

## Discrepancy against the brief, stated explicitly

- **46 purchases: REPRODUCED.** The fixed run has 46 distinct P transactions despite 52 owner-rows;
  six P transactions have more than one reporting owner.
- **7 officer/director: NOT REPRODUCED.** The fixed parse gives 48 O/D owner-rows (44 distinct
  transactions), not 7. I did not adjust the filter to force 7.
- **2,616 rows: NOT REPRODUCED.** Fixed run has 2,640 rows; the +24 is per-owner expansion of
  multi-owner filings plus normal filing drift. The old one-row-per-transaction file had 2,616.

Investigation: the committed old file (`12_INSIDER/form4_events_wide.csv`, before this deploy) already
shows **44** O/D P rows by the same truthy test, not 7. So 7 cannot be recovered from the artifact the
brief cites; it likely came from a different owner/flag definition that is not stated. The old parser
also used the first owner for all transactions, which is exactly the bug fixed here: it loses an
officer in a multi-owner filing and counts an entity as an insider. The fixed per-owner result is
therefore expected to be **higher** than the old first-owner count, not lower.

Decision: keep the frozen `is_officer == true OR is_director == true` filter. Report both the owner-row
count (48) and the distinct-transaction count (44). Do not use 7 as a gate input until the definition
that produced it is supplied.

## Artifacts

- `12_INSIDER/form4_events_wide.csv` — replaced with the fixed per-owner rows (2,640 lines incl. header)
- `12_INSIDER/form4_summary_wide.md` — fixed summary (P=52 owner-rows; filtered P=48)
- This log.

## Next

1. Decide whether the analysis unit is the owner-row (48) or the distinct transaction (44); the probe
   should state it before returns.
2. Exclude 10% owners explicitly if the claim is "insider knowledge", not "fund accumulation"
   (31 distinct transactions remain).
3. Run the P-vs-S asymmetry and price probe on the chosen unit; no return claim has been made.

next_probe: run the P-vs-S asymmetry on the 44 distinct O/D transactions and the 31 non-10%-owner
subset, with the frozen 21/63/126-day horizons and symbol-cluster CI.
