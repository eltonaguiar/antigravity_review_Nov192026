# Look-through consensus for funds — method and limits

**Code:** `lookthrough_consensus.py` · **Output:** `out/lookthrough_consensus.json`
**Run:** 2026-11-24T11:06:45Z · consensus universe: 71 symbols (`../../docs/data/harvest_signals.json`)

## Why this exists

Sell-side analysts rate companies, not funds. That is why every ETF on the HARVEST page shows 0%
coverage. The zero is honest but useless. This computes a fund-level number from the equity ratings
we already hold:

```
fund_share_buy = Σ(w_i · share_buy_i) / Σ(w_i)      over holdings i that are in the consensus feed
coverage_pct   = Σ(w_i) covered / Σ(w_i) all        the share of fund weight the above speaks for
```

Everything produced is **DERIVED**. It is not a published fund rating, no analyst issued it, and it
must carry its coverage share wherever it is displayed.

## Identifiers — the part that has to be got right

SSGA files carry `Ticker` *and* `Identifier` (= CUSIP). SEC N-PORT carries `cusip`/`isin` and, for
QQQ, a ticker on only **1 of 105** positions. So neither source alone spans the join.

`lookthrough_consensus.py` builds a CUSIP→ticker crosswalk from the SSGA files (which have both) and
applies it to N-PORT. **Crosswalk size this run: 1,621 CUSIPs.** QQQ needed 86 translations, VTI 35.
This is why a naive ticker join returned 0 matches for QQQ on the first attempt.

## Results

| fund | source | positions | matched | coverage | derived share Buy | status |
|---|---|---:|---:|---:|---:|---|
| SPY | SSGA xlsx | 505 | 70 | 60.07% | 77.35 | DERIVED_OK |
| XLK | SSGA xlsx | 78 | 14 | 65.46% | 77.44 | DERIVED_OK |
| QQQ | SEC N-PORT | 105 | 22 | 54.98% | 75.95 | DERIVED_OK |
| JNK | SSGA xlsx | 1117 | 0 | 0.00% | — | NOT_APPLICABLE_BOND_FUND |
| VTI | SEC N-PORT | 551 | 0 | 0.00% | — | BLOCKED_WRONG_SERIES |
| EEM | — | — | — | — | — | BLOCKED |

### Limits that matter more than the numbers

1. **The three derived values agree to within 2.5 points — and that is not evidence of anything.**
   SPY, QQQ and XLK are all large-cap funds, and the 71-symbol universe is itself large-cap
   mega-caps. The aggregate is close to the universe average by construction. The coverage share is
   the informative column; the value is not.
2. **Coverage is a filter on the answer.** SPY's 77.35 describes 60% of its weight. The missing 40%
   is mostly smaller constituents with no analyst coverage, and they are not missing at random.
3. **Weights are taken as filed**, not rescaled across the covered subset except in the denominator
   of `fund_share_buy`.
4. **N-PORT is quarterly-ish, SSGA is daily.** SPY/XLK/JNK weights are fresher than QQQ's. Do not
   compare across rows without noting that.
5. **JNK's 0% is correct.** A high-yield bond ETF holds no equities, so an equity look-through is
   undefined for it. Bond funds need credit ratings and yield data, which is a different product.

### VTI — why the number is withheld

The newest `NPORT-P` under Vanguard CIK `0000036405` (accession `0000036405-26-000483`) parses to 551
positions whose names are ExlService, Six Flags, Globalstar, Tempur Sealy, Outfront Media. Those are
small/mid caps, not VTI's constituents. Vanguard files one N-PORT per series under a single CIK, so
the newest filing for the CIK belongs to a sibling fund. Publishing "VTI: 0% coverage" would be a
false statement about VTI, so it is flagged `BLOCKED_WRONG_SERIES` and withheld. Resolving the
correct series requires matching `seriesName` across the filing batch; that resolution is
unfinished, not impossible.

### EEM — blocked at the source

`iShares` daily holdings returned `HTTP 200` with `content-type: text/csv` and an **HTML body**
(`<!DOCTYPE html>` interstitial). Invesco's download endpoint returned `HTTP 406`, 0 bytes.
`data.sec.gov/submissions/CIK0000872664.json` returned non-JSON. No credential-free source was
verified, so no figure is produced.

## Reproduce

```bash
python3 lookthrough_consensus.py --feed ../../docs/data/harvest_signals.json
```

Parses `.xlsx` with stdlib `zipfile` + `ElementTree` — no `openpyxl`, no `pandas` required. Writes
only to `./out/`.
