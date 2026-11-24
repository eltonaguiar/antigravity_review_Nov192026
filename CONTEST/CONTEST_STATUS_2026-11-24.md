# Contest status — 2026-11-24 (applied findings)

## 1. Ledger integrity (Round 01)
Ran `CONTEST/tools/verify_ledger.py`: **12/18 submissions verified**.

- **6 NOT RECORDED** in `LEDGER.md` (never frozen, so no commitment was broken):
  `CP_PANEL_CHATGPT`, `CP_PANEL_CLAUDE_A`, `CP_PANEL_CLAUDE_HAIKU`,
  `MUSE_MUSE_EMBER`, `MUSE_MUSE_SPARK`, `MUSE_MUSE_SPARK_1_0_META_AI`.
- **0 recorded entries changed** (no hash mismatch among committed submissions).
- Actual hashes are listed in `ROUND_01_2026-11-23/VERIFICATION_2026-11-24.md`.

**Action taken:** fixed `verify_ledger.py`, which had `NOT_RECORDED` and
`MISMATCH` labels swapped; added a regression test
(`CONTEST/tools/test_verify_ledger.py`, 1 passed) using three fixtures
(correct hash / name-with-wrong-hash / absent).

**Operator decision required:** either record the six explicitly as
**late-recorded 2026-11-24** with their hashes, or remove them from Round 01.
Do not backdate; do not silently re-hash.

## 2. Can the contest produce a winner? (No.)
`CONTEST/tools/contest_mde.py`: with the current design,
- price-accuracy of the SPY anchor spread across entrants: **yes**;
- ranking entrants by return: **no**;
- "entrant X beat entrant Y": **no**;
- a winner: **no**.

`positive_control.py` shows why: only a **10%/yr** injected edge is detectable
(t=3.94, CI [+5.02,+14.98]); 1% (t=0.39), 2% (t=0.79) and 3% (t=1.18) are all
indistinguishable from zero. The honest leaderboard is 18 rows, one column:
**"not distinguishable"**.

**Action taken:** the self-executing metrics script was renamed
`test_quant_metrics.py` -> `selftest_quant_metrics.py` (it called `sys.exit()`
at import, breaking pytest collection). It still runs standalone: 0 failures;
`pytest CONTEST/tools` now collects cleanly (1 passed).

## 3. What would make a winner defensible
Pre-register a return rule, require n>=100 independent picks per entrant, and
size the contest so the minimum detectable edge is below the expected edge
(currently MDE ~10%/yr is larger than any plausible edge). Until then, publish
"not distinguishable" rather than a ranking.

## 4. Preflight gate (applied)
`CONTEST/tools/check_round_integrity.py` runs the canonical verifier and exits
non-zero if any submission is NOT RECORDED or MISMATCHED, so a round cannot be
scored on unrecorded entries. Current run:
`round=CONTEST/ROUND_01_2026-11-23 ok=False not_recorded=6 mismatched=0` (exit 1).
`--json` emits the machine-readable list for CI.
