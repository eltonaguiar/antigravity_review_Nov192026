# `ZOO_UNJOINED_PATTERN` correction — per-class EXPIRED counts under `UPPER(asset_class)`

**Auditor:** ghcopilot (Track C) · **Date:** 2026-11-25
**Corrects:** `42_HARVEST_UPGRADE_2026-11-24/tracker/ZOO_UNJOINED_PATTERN.md`, §"Distribution of the 820"
and finding 2 (that file was **not** edited; sha256 `c60ce59437e157ed…` unchanged)
**Source:** `ejaguiar1_stocks`, MySQL 8.4.7, read-only. Password read at runtime from the shell
variable `DB_PASS_STOCKS`; never printed, logged or written to any file.
**Status: MEASURED** — the database was reachable, so this is not a BLOCKED report.

---

## 1. What was asked, and the one thing the brief got wrong

The brief asks for the same per-class EXPIRED count re-run with `UPPER(asset_class)`, on the
assumption that raw-string grouping undercounts CRYPTO and FOREX. **The re-run was done, and the
assumption does not survive contact with the schema:**

> `at_pick_outcomes.asset_class` is `varchar(20)` with collation **`utf8mb4_unicode_ci`** —
> case-**insensitive**.

Because the collation is CI, a plain `GROUP BY asset_class` **already merges** `crypto` with
`CRYPTO`, and `forex` with `FOREX`. `UPPER()` therefore changes **no count at all**. The split that
`ZOO_UNJOINED_PATTERN.md` reports was produced by that file's own **case-sensitive** grouping
(`BINARY` / `COLLATE …_bin`), not by the data or by a naive query.

Measured both ways on the full EXPIRED population to prove it:

| grouping method | distinct labels returned |
|---|---:|
| plain `GROUP BY asset_class` (collation-driven) | **13** |
| `GROUP BY BINARY asset_class` (case-sensitive) | **18** |

Five case-pairs exist in the stored values and are silently merged by the default collation. So the
case-inconsistency is **real in the data** but **harmless in the default query path**, which is the
opposite of what the source file concluded.

---

## 2. Population drift — 820 became 816

Before any comparison, the population is not stable. `ZOO_UNJOINED_PATTERN.md` measured **820**
unjoined EXPIRED rows; the identical query returns **816** today.

| | rows |
|---|---:|
| unjoined EXPIRED now (pre-pillar table as the NOT EXISTS target) | **816** |
| as reported in `ZOO_UNJOINED_PATTERN.md` | 820 |
| drift | **−4** |

All EXPIRED rows: **29,649** (the source file cites 29,655 — a further drift of −6). This is a live
database and the resolver keeps writing; exact reproduction of the file's absolute counts is not
possible, only of their structure. Every "before" below is therefore given twice: **as the file
printed it**, and **as re-measured now**.

---

## 3. Before and after, every class — unjoined set

### 3a. As row labels (what the source file's table literally prints)

| label as printed | n in source file | n now (case-sensitive) | collapses to (UPPER) |
|---|---:|---:|---|
| `crypto` | 570 | 567 | `CRYPTO` **573** |
| `CRYPTO` | 7 | 6 | `CRYPTO` **573** |
| `forex` | 80 | 80 | `FOREX` **122** |
| `FOREX` | 42 | 42 | `FOREX` **122** |
| `equity` | 69 | 69 | `EQUITY` **69** |
| `futures` | 46 | 46 | `FUTURES` **46** |
| `bond` | *(absent)* | 3 | `BOND` **3** |
| `COMMODITY` | *(absent)* | 3 | `COMMODITY` **3** |
| **total** | **820** | **816** | **816** |

The file's six printed labels sum to 814, not 820 — the missing 6 are the `bond` (3) and
`COMMODITY` (3) rows that its table omitted, which is itself a small completeness gap in the
original.

### 3b. As classes (the merged, correct view)

| class | before — file's BINARY grouping | before — BINARY, re-measured now | after — `UPPER`, now | Δ caused by `UPPER` |
|---|---:|---:|---:|---:|
| **CRYPTO** | 570 + 7 = **577** | 567 + 6 = **573** | **573** | **0** |
| **FOREX** | 80 + 42 = **122** | 80 + 42 = **122** | **122** | **0** |
| EQUITY | 69 | 69 | 69 | 0 |
| FUTURES | 46 | 46 | 46 | 0 |
| BOND | — | 3 | 3 | 0 |
| COMMODITY | — | 3 | 3 | 0 |
| **total** | 820 | 816 | 816 | **0** |

Note that the file's own arithmetic already gives 122 for FOREX (80 + 42) and 577 for CRYPTO
(570 + 7) — i.e. the source file's numbers, added up correctly, agree with `UPPER()` and disagree
with the two-row presentation it led with.

---

## 4. CRYPTO and FOREX deltas

There are two defensible ways to state the delta, and they differ only in which "before" is used:

| comparison | CRYPTO | FOREX |
|---|---|---|
| file's uppercase-labelled row → `UPPER` count now | 7 → 573 (**+566**) | 42 → 122 (**+80**) |
| case-sensitive grouping re-measured now → `UPPER` now | 6 → 573 (**+567**) | 42 → 122 (**+80**) |
| **`UPPER` vs the correct default `GROUP BY` (collation)** | **573 → 573 (0)** | **122 → 122 (0)** |

The +566 / +80 figures are the size of the merge, **not** a gain from `UPPER`. Against the query a
reader would actually write — a plain `GROUP BY` on this CI column — `UPPER()` is worth **exactly
zero** on both classes. The 566/80 is the amount the source file's case-sensitive table was
under-reporting its own merged data by.

Correctness checks, so the zero-delta is not an artefact of my own query:

- `asset_class` has **0** NULLs and **0** blank/whitespace-padded values in both populations
  (`asset_class <> TRIM(asset_class)` returns 0), so `UPPER(TRIM(x))` returns exactly the same
  counts as `UPPER(x)` — whitespace is not a hidden factor.
- The merged totals reconcile exactly: 573 + 122 + 69 + 46 + 3 + 3 = **816**, and
  13,200 + 8,718 + 4,947 + 1,721 + 424 + 311 + 145 + 125 + 30 + 19 + 4 + 3 + 2 = **29,649**.

---

## 5. The same measurement on all EXPIRED rows (29,649), for scale

The file's finding 2 was about the unjoined subset, but the claim ("any per-class aggregate") is
general, so it was tested on the whole population too.

| class | BINARY (case-sensitive) | `UPPER` | Δ |
|---|---:|---:|---:|
| FOREX | 13,026 + 174 = **13,200** | **13,200** | 0 |
| CRYPTO | 8,017 + 701 = **8,718** | **8,718** | 0 |
| COMMODITY | 4,947 | 4,947 | 0 |
| EQUITY | 1,652 + 69 = **1,721** | **1,721** | 0 |
| FUTURES | 378 + 46 = **424** | **424** | 0 |
| INDEX | 311 | 311 | 0 |
| ETF | 145 | 145 | 0 |
| BOND | 122 + 3 = **125** | **125** | 0 |
| MEME | 30 | 30 | 0 |
| STOCK | 19 | 19 | 0 |
| STOCKS | 4 | 4 | 0 |
| PENNYSTOCK | 3 | 3 | 0 |
| PENNY | 2 | 2 | 0 |
| **total** | **29,649** | **29,649** | **0** |

Five case-pairs collapse (CRYPTO/crypto, FOREX/forex, EQUITY/equity, FUTURES/futures, BOND/bond),
18 labels become 13, and not one count changes. `UPPER()` is a no-op everywhere.

---

## 6. Verdict on finding 2 — one sentence

**Finding 2 is CONFIRMED that `asset_class` is genuinely case-inconsistent (18 stored labels collapse
to 13 under the column's own `utf8mb4_unicode_ci` collation, across five case-pairs), but REFUTED that
this undercounts CRYPTO and FOREX in a per-class aggregate — a plain `GROUP BY` already returns the
merged 573 and 122, so `UPPER()` changes no count and the split the file reported is an artefact of
its own case-sensitive grouping, not a property of the column.**

---

## 7. A real defect in this column that `UPPER()` does not fix

While measuring, a worse normalisation problem than case showed up, and it is worth recording because
`UPPER()` leaves it untouched:

| synonym group (all EXPIRED) | stored labels and counts |
|---|---|
| stock-equity | `STOCK` 19, `STOCKS` 4 — and neither is counted as `EQUITY` (1,721) |
| penny | `PENNY` 2, `PENNYSTOCK` 3 — two spellings, five rows total |
| commodity | `COMMODITY` 4,947 only — no lower-case pair, so no case issue here |

`UPPER()` merges 5 case-pairs and **0** of these spelling variants. So if the concern is
"per-class aggregates are wrong", the case issue is the smaller half of it: the label set has at
least three near-synonym groups that survive any case normalisation, and a `STOCK` row is not
counted as `EQUITY`. That is a mapping problem, not a casing problem, and no amount of `UPPER`
will close it.

---

## 8. What would actually be required

1. `UPPER()` is unnecessary for correctness on this column — the collation already does it. It is
   harmless, so adding it as belt-and-braces is fine, but it fixes nothing on its own.
2. The genuine hazard is **case-sensitive** grouping (`BINARY`, `COLLATE utf8mb4_bin`), which is what
   produced the source file's split. That is the pattern to avoid, not the raw column.
3. The remaining defect is a **label-alias map** (`stock`/`stocks`→`equity`, `penny`/`pennystock`→
   whichever class is intended), applied before aggregation. Until that exists, per-class counts
   should be quoted with the label list beside them rather than the class total alone.

---

### Provenance / reproduce

Read-only; no file in the tracker directory other than this one was created or modified.

```sql
-- 13 groups (case-insensitive). BINARY makes it 18.
SELECT asset_class, COUNT(*) FROM at_pick_outcomes
WHERE status='EXPIRED' GROUP BY asset_class ORDER BY 2 DESC;

-- the unjoined population: 816 now, 820 in ZOO_UNJOINED_PATTERN.md
SELECT COUNT(*) FROM at_pick_outcomes o
WHERE o.status='EXPIRED'
  AND NOT EXISTS (SELECT 1 FROM at_pick_outcomes_pre_pillar_migration_2026_06_09 p
                  WHERE p.pick_id = o.pick_id);

-- the requested re-run
SELECT UPPER(asset_class) c, COUNT(*) FROM at_pick_outcomes o
WHERE o.status='EXPIRED'
  AND NOT EXISTS (SELECT 1 FROM at_pick_outcomes_pre_pillar_migration_2026_06_09 p
                  WHERE p.pick_id = o.pick_id)
GROUP BY c ORDER BY 2 DESC;

-- collation, the fact the source file's finding turns on
SELECT COLLATION_NAME FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA='ejaguiar1_stocks' AND TABLE_NAME='at_pick_outcomes'
  AND COLUMN_NAME='asset_class';   -- utf8mb4_unicode_ci
```

| figure | source |
|---|---|
| 820 / crypto 570 / CRYPTO 7 / forex 80 / FOREX 42 | `ZOO_UNJOINED_PATTERN.md` lines 34–36 |
| 816 unjoined / 29,649 EXPIRED | measured 2026-11-25 |
| 13 vs 18 distinct labels | measured, plain vs `BINARY` grouping |
| `utf8mb4_unicode_ci` | `information_schema.COLUMNS` |
| 0 NULL / 0 blank / 0 padded | measured |
