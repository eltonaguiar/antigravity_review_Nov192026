# UP-only breadth — independent crosscheck (copilot)

**Date:** 2026-11-25 · **Author:** copilot (independent recomputation, own code)
**Declared input** (from `tracker/DATA_MANIFEST_2026-11-24.json`):

```
path   /home/eaguiar2015/antigravity_review/42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv
bytes  9454358
sha256 9dd7d8cbf4ecd907e513422e157a96a5f3bcdde3cf0b48f66e6d9ea269a30f11
```

**Hash verified on this host before computing:** present, 9,454,358 bytes, and
`sha256sum` returns `9dd7d8cbf4ecd907e513422e157a96a5f3bcdde3cf0b48f66e6d9ea269a30f11` — an exact
match to the manifest. The comparison below is therefore against the declared bytes, not a
lookalike file.

**Method:** written from the definition, not adapted from `zoocode/up_only_breadth.py`. Counts are
taken independently; agreement is a reproduction, not a shared code path.

- **up event:** `action.strip().lower() == "up"`
- **pair:** `(firm_norm, symbol)`
- **182-day clean filter:** an `up` counts only if that pair has **no prior `up` or `down`** within
  the preceding 182 days; `init`/`reit`/`main` do **not** reset the window. Where marks exist, the
  test is `(date − latest_prior_up_or_down).days >= 182`.
- **date parsing:** the `date` column holds **epoch seconds**, not a date string. This is the trap
  in this file — a `%Y-%m-%d` parse raises `ValueError: time data '1794402156' does not match
  format`. Zoo's code is correct on this; my first pass was not.

---

## Numbers: Zoo's published values beside mine

| # | quantity | Zoo (`tracker/UP_ONLY_BREADTH.md`) | mine (independent) | agrees |
|---|---|---:|---:|---|
| 1 | distinct broker–stock pairs with ≥1 `up` | 6,012 | **6,012** | ✅ |
| 2 | pairs surviving the 182-day filter | 5,696 | **5,696** | ✅ |
| 3a | firms ≥300 / ≥500 / ≥750 (raw) | 10 / 1 / 0 | **10 / 1 / 0** | ✅ |
| 3b | firms ≥300 / ≥500 / ≥750 (filtered) | 6 / 0 / 0 | **6 / 0 / 0** | ✅ |
| 4a | biggest firm, raw | BofA Securities 556 | **BofA Securities 556** | ✅ |
| 4b | biggest firm, filtered | BofA Securities 439 | **BofA Securities 439** | ✅ |

Supporting totals from my run (not part of the six cells, but they pin the denominators):

| quantity | value |
|---|---:|
| rows | 122,746 |
| distinct symbols — all rows / up rows | **308 / 306** |
| distinct firms — all rows / up rows | **291 / 227** |
| total filtered up events | 8,498 |
| date span | 2011-12-08 → 2026-11-12 |

## One thing that looks like a divergence and is not

The task statement and the manifest both say **308 tickers**. My up-only count is **306**. Both are
right: 308 is the distinct-symbol count over **all** rows, 306 is the count over **`up` rows only**.
Two symbols appear in the file but never with an `up`. Recording 308 against an up-only statistic
would inflate the denominator by 2, so the up-only number should carry 306.

The same distinction explains firms: **291** distinct firms across all rows, **227** in the up-only
set.

---

## VERDICT: REPRODUCED

All six published cells reproduce exactly from the declared bytes, using independently written
counting code. Pair count = **6,012**.
