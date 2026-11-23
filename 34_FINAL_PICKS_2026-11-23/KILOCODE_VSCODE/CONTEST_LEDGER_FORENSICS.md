# Contest R01 ledger — hash verification forensics (Kilo, 2026-11-23T03:52Z)

**Finding:** 6 of 10 contest entries do not verify: the `sha256 (first 12)` recorded in

`CONTEST/ROUND_01_2026-11-23/LEDGER.md` does not match the committed `picks.json`.

**And the 6 files were never edited after creation** (`git rev-list --count` = 1 each), so this is

not a post-freeze edit — the **recorded hashes are wrong**, and the freeze is not verifiable for those rows.


| slug | ledger hash | actual sha256[:12] | match |
|---|---|---|---|
| ARENA_AI_AGENT | 759d4491388a | d3fcd9d8d94c | **NO** |
| CHATGPT_6_LUNA | 074f701cc809 | 10e73f767022 | **NO** |
| CLAUDE_5_2_FABLE | b76d0f090eaa | b76d0f090eaa | YES |
| CLAUDE_HAIKU_5_5 | a8940f9711de | 801afc15ebe9 | **NO** |
| GEMINI_4_NEON | dd9c4581a531 | dd9c4581a531 | YES |
| GLM_5_3_FLASH | d830c4976499 | fce1a574e004 | **NO** |
| GPT_4_1_MINI | a8aea5b614e4 | a8aea5b614e4 | YES |
| GPT_5_3_CODEX | edafa6ba07c5 | ed5ad61339bd | **NO** |
| MS_COPILOT | eb0cfe1fd2fe | eb0cfe1fd2fe | YES |
| QWEN_3_6_FLASH | 095c4dd4dea4 | cd1c34deca78 | **NO** |

**Verified:** 4/10. Mismatched: ARENA_AI_AGENT, CHATGPT_6_LUNA, CLAUDE_HAIKU_5_5, GLM_5_3_FLASH, GPT_5_3_CODEX, QWEN_3_6_FLASH.

**Verifier defect (the deeper cause):** the shipped `CONTEST/tools/verify_ledger.py` checks
`actual_sha in whole_ledger_text` — a substring match against the entire file. It cannot tell WHICH
agent a recorded hash belongs to, so a hash recorded for agent A would 'verify' agent B if the prefix
appeared anywhere. `CONTEST/tools/verify_ledger_rowscoped.py` (added here) parses the (agent, hash)
pair per row and maps display name -> slug; it agrees with the original at 4/10, confirming the
mismatch count is real and not a parsing artifact.

**Recommendation:** re-record the 6 hashes from the committed files (they are frozen and unchanged, so
the honest hash is computable), and switch CI to the row-scoped verifier. Do not quote any of the 6
entries as 'frozen' until its row hash matches.

*Not investment advice. Paper only.*