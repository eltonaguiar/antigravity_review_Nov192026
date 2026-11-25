# Track B ratings -- so the bucket levels can be verified from the repo

zoo-savant, 2026-11-25. New file; `class_calibration.md` and every existing CSV were NOT edited.

## Row counts

| | rows |
|---|---|
data rows | **1467** |
included | **963** |
excluded | **504** |

Every included row carries a non-empty rating. Excluded rows keep their rating where the
consensus period existed (so the label is auditable) and `UNMAPPED` where it did not.

## Per-rating counts over the 963 included rows

| rating | written | published in class_calibration.md | agrees |
|---|---|---|---|
STRONG_BUY | **207** | 207 | yes |
BUY | **579** | 579 | yes |
HOLD | **164** | 164 | yes |
SELL | **13** | 13 | yes |
total | **963** | 963 | yes |

UNMAPPED among included rows: **0**.

## Mapping

- The rating is `bucket_of(score)` exactly as `zoocode/class_calibration.py` defines it
  (lines 96-105): `score >= 1.0 -> STRONG_BUY`, `>= 0.3 -> BUY`, `> -0.3 -> HOLD`,
  `> -1.0 -> SELL`, else STRONG_SELL -- where
  `score = (2*strongBuy + buy - sell - 2*strongSell) / n` from the harvest trend row.
- Frozen mapping file used: **`grade_ordinals_frozen.csv`**,
  sha256 `597d90b42425d760324e27f2fab56d11976c5c7f54354a91726a6a68822f45fe`
  (102,115 bytes, verified against `DATA_MANIFEST_2026-11-24.json`).
- `grade_raw` is the dominant grade label of that period's distribution, kept verbatim
  (`Strong Buy` / `Buy` / `Hold` / `Sell` / `Strong Sell`).

## sha256 of the CSV

`6cfafc73e5c3be032eee55b86e50290cf9c5f815f30b3c953d099f141da448a4`

## Caveat

The rating is a function of the consensus COUNTS, so it reproduces the published buckets exactly
-- which is the point -- but it carries no forward return: the return side lives in
`CLASS_CALIBRATION_PRICE_PANEL.csv`, joined on `(symbol, period_bucket)`.
