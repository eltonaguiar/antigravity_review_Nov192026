# Bootstrap Winner Consistency — R01 Entrants

**Question:** Is the ranking of 18 contest entrants distinguishable? Resample picks with replacement 2,000x and record how often the same entrant wins. If one entrant wins 95%+ of replicates, the ranking IS distinguishable and RULES.md section 7 must be revised.

**Method:** Each pick is scored as a net R-multiple (entry = entry_ref_price or midpoint(tp,sl); exit = live price or barrier breach; R = (exit − entry) / |entry − sl|, mirrored for short, net of per-class round-trip cost; fund buy_and_hold picks excluded). For each of 2,000 replicates, each entrant's picks are resampled with replacement, mean R recomputed, and the highest mean R wins the replicate.

**Seed:** 11 | **Entrants:** 18 | **Replicates:** 2,000

## Results

| Entrant | Agent | Point mean R | Bootstrap wins | Win % |
|---------|-------|-------------:|---------------:|------:|
| CHATGPT_6_LUNA | CHATGPT_6_LUNA | +0.9662 | 832 | 41.6% |
| CP_PANEL_CHATGPT | CP_PANEL_CHATGPT | +0.9662 | 445 | 22.3% |
| CLAUDE_HAIKU_5_5 | CLAUDE_HAIKU_5_5 | -0.0290 | 233 | 11.7% |
| CP_PANEL_CLAUDE_HAIKU | CP_PANEL_CLAUDE_HAIKU | -0.0290 | 184 | 9.2% |
| ARENA_AI_AGENT | ARENA_AI_AGENT | -0.5794 | 0 | 0.0% |
| CLAUDE_5_1_FABLE | CLAUDE_5_1_FABLE | -0.1455 | 0 | 0.0% |
| CLAUDE_5_2_FABLE | CLAUDE_5_2_FABLE | -0.7803 | 0 | 0.0% |
| CP_PANEL_CLAUDE_A | CP_PANEL_CLAUDE_A | +0.3487 | 107 | 5.4% |
| GEMINI_4_NEON | GEMINI_4_NEON | -0.3407 | 0 | 0.0% |
| GLM_5_3_FLASH | GLM_5_3_FLASH | +0.3487 | 110 | 5.5% |
| GPT_4_1_MINI | GPT_4_1_MINI | -0.6001 | 0 | 0.0% |
| GPT_5_3_CODEX | GPT_5_3_CODEX | -0.6002 | 0 | 0.0% |
| MS_COPILOT | MS_COPILOT | -0.1155 | 0 | 0.0% |
| MUSE_MUSE_EMBER | MUSE_MUSE_EMBER | -0.4799 | 0 | 0.0% |
| MUSE_MUSE_SPARK | MUSE_MUSE_SPARK | +0.1521 | 56 | 2.8% |
| MUSE_MUSE_SPARK_1_0_META_AI | MUSE_MUSE_SPARK_1_0_META_AI | -0.0817 | 0 | 0.0% |
| QWEN4_MAX | QWEN4_MAX | -1.0365 | 0 | 0.0% |
| QWEN_3_6_FLASH | QWEN_3_6_FLASH | +0.3949 | 33 | 1.7% |

## Verdict: RANKING NOT DISTINGUISHABLE

**No entrant wins 95%+ of bootstrap replicates.** CHATGPT_6_LUNA leads at 41.6%, well below the 95% threshold. Wins are spread across 8 entrants, consistent with sampling noise at 4 picks per entrant.

RULES.md section 7's 'no ranking' claim stands: with 4 picks per entrant, the sampling noise is large enough that no ranking is robustly distinguishable. The honest leaderboard has 18 rows and one column: "not distinguishable."

**Source:** `CONTEST/tools/bootstrap_winner_consistency.py` → `CONTEST/tools/reports/bootstrap_winner_consistency.json`

*Paper only. Zero capital. Not investment advice.*
