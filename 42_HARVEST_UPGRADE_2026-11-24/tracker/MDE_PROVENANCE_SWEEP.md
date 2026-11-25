# MDE provenance sweep — every citation of `18.868` and `148.5`

**Author:** ghcopilot · **Date:** 2026-11-25 · **Type:** audit sweep, no edits to other files
**Scope:** every path under `42_HARVEST_UPGRADE_2026-11-24/` on `origin/main` at `c3bb11f`
**Repo state at sweep time:** `git rev-parse HEAD` = `c3bb11f`, clean detached worktree (no dirty files,
so the sweep reflects committed content, not a working tree).

---

## 1. Commands run

Both were run bare — no pipes, no redirects — as specified:

```
git grep -n 18.868 -- 42_HARVEST_UPGRADE_2026-11-24
git grep -n 148.5 -- 42_HARVEST_UPGRADE_2026-11-24
```

---

## 2. First finding: the patterns are **regexes**, and that fabricates hits

`git grep` compiles its pattern as a **basic regular expression**. The `.` in both `18.868` and `148.5`
is therefore a wildcard matching any character, and the analyst CSV's epoch-second `date` column is full
of strings that match. This inflates the naive hit count enormously:

| file | regex hits | **literal hits** | why they differ |
|---|---:|---:|---|
| `tracker/analyst_actions.csv` — `148.5` | 132 | **1** | `148?5` matches every `148xxxxxx` epoch (e.g. `1480528333` → `14805`) |
| `tracker/analyst_actions.csv` — `18.868` | 1 | **0** | epoch `1618486885` contains `184868`, which matches `184868` under `18?868` |
| `tracker/CLASS_CALIBRATION_PRICE_PANEL.csv` | 1 | 1 | genuine price `148.5800018310547` |
| `ghcopilot/out/crowd_layer.json` | 1 | 1 | genuine "Over 148.5 points" market question |

Re-verified with fixed-string mode (`git grep -cF`):

| string | regex hits | literal hits |
|---|---:|---:|
| `18.868` | 33 (10 files) | **32 (9 files)** |
| `148.5` | 141 (5 files) | **10 (5 files)** |

**All classification below uses the 42 literal hits.** The regex totals are reported only so the
difference is visible; a sweep that trusted them would have reported 132 phantom `148.5` citations in a
price CSV that has exactly one.

---

## 3. Classification summary

Exactly one class per hit. Totals over the 42 literal hits:

| class | hits | files |
|---|---:|---:|
| **STALE** | **1** | 1 |
| **HISTORICAL** | **9** | 3 |
| **CORRECTIVE** | **29** | 8 |
| **COINCIDENCE** | **3** | 3 |
| total | **42** | 12 distinct files |

---

## 4. `18.868` — 32 literal hits

### 4a. CORRECTIVE — 22 hits, 5 files

Files that state the value in order to withdraw, supersede or retain-as-erratum it.

| file | lines | evidence that it is corrective |
|---|---|---|
| `tracker/class_calibration.md` | 31, 72, 73, 105, 120, 121, 122 | line 31: "MDE 8.78 pp/yr is the measured value … 18.868 was a row-level-SD error, retained there for the record"; lines 120–122 (MDE SIGMA AUDIT) compute that 18.868 requires σ = 148.3 pp/yr, **2.15×** the measured 69.01 |
| `tracker/TRACK_B_DEFECT_AUDIT.md` | 1, 28, 30, 70, 83, 99, 109 | line 87 withdraws the 148.5 σ; line 99 "18.868 is therefore **2.15x** the measured MDE"; line 109 next_probe "replace every remaining citation of 18.868 / 148.5" |
| `tracker/AUDIT_TRACK_B_CALIBRATION_2026-11-25.md` | 43, 75, 84, 90 | line 75 "**Supersedes these two sentences** … kept for the record, not deleted"; line 90 "**The figure to cite is 8.78 pp/yr**, not 18.868" |
| `tracker/class_calibration.json` | 73, 74 | `"mde_pct": 8.78` (line 34); the value survives only as `mde_pct_published_2026-11-24: 18.868` plus `mde_pct_note: "…is 2.15x the measured MDE"` |
| `zoocode/class_calibration.json` | 82, 83 | same structure; `"mde_pct": 8.78` at line 43 |

### 4b. HISTORICAL — 9 hits, 3 files

Dated audits that predate the correction. Not stale, but two of them assert things now known false.

| file | lines | note |
|---|---|---|
| `ghcopilot/AUDIT_OF_TRACK_B.md` | 58 | dated **2026-11-24**; lists `mde_pct 18.868` among figures verified as *matching the JSON* — which was true then |
| `ghcopilot/AUDIT_OF_TRACK_B_DEFECTS.md` | 11, 38, 42, 43, 58 | dated **2026-11-24**; concludes "`mde_pct = 18.868` is internally consistent … not a units error" — a verdict later **superseded** by the σ audit. **Highest residual risk in this set**: it defends the value and carries no pointer to the correction |
| `ghcopilot/NOTE_TO_KILO.md` | 88, 94, 96 | pre-correction note; it already disputes 18.868 as "**~8×** against the difference actually tested", so it is not stale — but it predates the measured 8.78 |

### 4c. STALE — 1 hit

See §5.

---

## 5. THE ONLY STALE HIT — exact replacement required

**`42_HARVEST_UPGRADE_2026-11-24/zoocode/class_calibration.md:25`**

Presents `18.868%` as the current MDE in the canonical per-class results table, while its *own sibling*
`zoocode/class_calibration.json` already carries `"mde_pct": 8.78`. The `.md` is out of sync with the
`.json` beside it.

Exact line as it stands:

```
| EQUITY | 963 | 485 | -0.0467 | 0.9995 | inverted | 0.38 | 18.868% | inverted |
```

**Exact replacement text:**

```
| EQUITY | 963 | 485 | -0.0467 | 0.9995 | inverted | 0.38 | 8.78% | inverted |
```

That is byte-identical to the already-corrected `tracker/class_calibration.md:25`, so the two copies
would then agree. **One cell, one edit.** No other line in `zoocode/class_calibration.md` contains
either swept value.

---

## 6. `148.5` — 10 literal hits

### 6a. CORRECTIVE — 7 hits, 2 files

| file | lines | note |
|---|---|---|
| `tracker/class_calibration.md` | 74, 106, 135 | 74 and 106 quote the σ = 148.5% assumption to refute it; 135 says "delete the 148.5% figure wherever it is still cited" |
| `tracker/TRACK_B_DEFECT_AUDIT.md` | 31, 84, 87, 109 | line 87: "**The 148.5 percent sigma is not measured by anything in the repo and is WITHDRAWN.**" |

### 6b. COINCIDENCE — 3 hits, 3 files

Numeric prices or unrelated fields — not the MDE sigma at all.

| file | line | what it actually is |
|---|---|---|
| `tracker/analyst_actions.csv` | 17803 | a **target price**: `C,JP Morgan,…,Raises,148.5,147.0` (`current_target = 148.5` USD) |
| `tracker/CLASS_CALIBRATION_PRICE_PANEL.csv` | 877 | a **close price**: `MHK,…,exit_close 148.5800018310547` |
| `ghcopilot/out/crowd_layer.json` | 1687 | a **prediction-market question**: "…no Over 148.5 points…" |

### 6c. STALE — 0

No file presents `148.5` as a current σ. It is withdrawn everywhere it appears as a claim.

---

## 7. `tracker/class_calibration.md` — IN-FLIGHT no longer applies

The brief asked that this file's table cell be marked **IN-FLIGHT** rather than STALE if `18.868` were
still present there. Checked, and it is **already fixed**: line 25 reads `| … | 0.38 | 8.78% | inverted |`.
The other panel's commit (`c3bb11f`, "class_calibration.md summary table now cites measured MDE 8.78
pp/yr") landed before this sweep ran. Its remaining 7 hits are prose in the defect ledger and the MDE
SIGMA AUDIT, all corrective. **Nothing IN-FLIGHT remains.**

---

## 8. Known state, verified rather than assumed

| claim | verified | result |
|---|---|---|
| `tracker/class_calibration.json` → `mde_pct` 8.78 | line 34 | ✅ |
| `tracker/class_calibration.json` → `mde_pct_published_2026-11-24` 18.868 | line 73 | ✅ |
| `tracker/class_calibration.json` → gate 2 UNMET | line 8: "SPY (single-index market benchmark; characteristic-match gate 2 **UNMET**)" | ✅ |
| `zoocode/class_calibration.json` → `mde_pct` 8.78 / published 18.868 / gate UNMET | lines 43 / 82 / 8 | ✅ |
| `zoocode/class_calibration.py` already fixed | 0 literal hits for either figure; line 295 uses `2.802 * sd_symbol_means / math.sqrt(n_symbols)` | ✅ |
| `tracker/class_calibration.md` in-flight | table cell already `8.78%` | ✅ landed, no longer in flight |

---

## 9. Residual risk this sweep cannot remove

1. **`ghcopilot/AUDIT_OF_TRACK_B_DEFECTS.md` is the dangerous historical hit.** It affirmatively
   concludes 18.868 is correct and is not marked as superseded. Under the given taxonomy it is
   HISTORICAL (dated 2026-11-24), but a reader who lands there first will believe the wrong number. It
   needs a one-line superseded pointer; I did not add one, because this sweep may not edit other files.
2. **`zoocode/class_calibration.md:25` remains wrong until someone applies §5.** Until then the `zoocode`
   `.md` and `.json` disagree with each other.
3. **Scope limit.** The sweep covers only `42_HARVEST_UPGRADE_2026-11-24/`. `18.868` and `148.5` are not
   swept anywhere else in the repository (e.g. `reports/`, `docs/`, the audit dashboard). A repo-wide
   `git grep -F` is the obvious follow-up.
4. **Regex vs literal is itself a recurring hazard** (§2): a future audit that uses the same two commands
   unchecked would report 141 `148.5` hits of which 131 are epoch seconds. Recommend `git grep -Fn`.

---

### Provenance

| figure | source |
|---|---|
| 33 regex / 32 literal `18.868` hits; 9 files | `git grep -n 18.868`, `git grep -cF 18.868` |
| 141 regex / 10 literal `148.5` hits; 5 files | `git grep -n 148.5`, `git grep -cF 148.5` |
| 132 → 1 `analyst_actions.csv` inflation | per-line field-4 check over the CSV |
| all line numbers above | measured at `origin/main` = `c3bb11f` |

No file was edited except this one.
