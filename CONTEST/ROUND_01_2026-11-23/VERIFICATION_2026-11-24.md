# Round 01 ledger verification — 2026-11-24

Command: `python3 CONTEST/tools/verify_ledger.py`
(canonical sha256 = LF-normalised `picks.json`, first 12 hex)

## Result
**12/18 entries verified. 6 are NOT RECORDED in `LEDGER.md`; 0 recorded entries changed.**

| Submission | actual sha256 (12) | in LEDGER.md |
|---|---|---|
| CP_PANEL_CHATGPT | `a5781e67417e` | no |
| CP_PANEL_CLAUDE_A | `bb60a5e1fead` | no |
| CP_PANEL_CLAUDE_HAIKU | `019bc0c6c4b7` | no |
| MUSE_MUSE_EMBER | `c19a6c6869c6` | no |
| MUSE_MUSE_SPARK | `d167ab9ffd6a` | no |
| MUSE_MUSE_SPARK_1_0_META_AI | `24fdb7384c29` | no |

Per the ledger's own rule ("a submission is frozen the moment it appears here"),
these six were **never frozen** — no recorded hash exists to violate. They are an
unrecorded-entry gap, not evidence of tampering with a recorded submission.

## Verifier bug found and fixed
`verify_ledger.py` had the two labels **swapped**: a slug whose name was absent
from the ledger was reported as "MISMATCH (file changed or hash wrong)", and a
slug recorded with a different hash was reported as "NOT RECORDED". Fixed so
that:

- name absent at all  -> `NOT RECORDED` (never committed)
- name present, hash absent -> `MISMATCH` (file changed after commitment)

Re-run after the fix gives the table above.

## Recommended action (operator)
1. Decide per submission whether it was legitimately in Round 01.
2. If yes, record it in `LEDGER.md` explicitly marked **late-recorded
   2026-11-24** with the hash above — do not backdate it.
3. If no, move it out of `ROUND_01_2026-11-23/` so it cannot be scored.
4. Keep the verifier fix; it is required for any future CI gate.
