# Bootstrap winner consistency — R01 entrants

**Date:** 2026-11-23 · **Tool:** `CONTEST/tools/bootstrap_winner_consistency.py`

## Question

RULES.md section 7 states that no leaderboard ranking may be published because, with 
4 picks per entrant at normal volatility, two entrants must differ by 7–14 pp in 
mean return before the gap is distinguishable at t=2. The honest leaderboard has 
18 rows and one column: "not distinguishable."

This test is the falsifier: resample the 18 entrants' picks with replacement 2000x, 
recompute each entrant's mean R per replicate, and record how often the same entrant 
wins. If one entrant wins 95%+ of replicates, the ranking IS distinguishable and 
RULES.md section 7 must be revised.

## Method

Each pick is scored as a net R-multiple, mirroring `assess_contest.py`:

- `entry` = `entry_ref_price` from picks.json, else midpoint(tp, sl)
- `exit` = live price from `_prices_live.json`; if a barrier is breached, exit at that barrier
- `R` = (exit − entry) / |entry − sl| for long, mirrored for short, net of per-class round-trip cost
- `fund` buy_and_hold picks are scored on $ only, excluded from the R ranking

For each of 2000 replicates, each entrant's picks are resampled with replacement, 
their mean R is recomputed, and the entrant with the highest mean R wins the replicate.

## Results

| Entrant | Agent | Point mean R | Bootstrap wins | Win % |
|---|---|---:|---:|---:|
| CHATGPT_6_LUNA | ChatGPT-6 Luna | +0.9662 | 832 | 41.6% |
| CP_PANEL_CHATGPT | ChatGPT | +0.9662 | 445 | 22.2% |
| CLAUDE_HAIKU_5_5 | claude-haiku-5-5 | -0.0290 | 233 | 11.7% |
| CP_PANEL_CLAUDE_HAIKU | claude-haiku-5-5 | -0.0290 | 184 | 9.2% |
| GLM_5_3_FLASH | GLM 5.3 Flash | +0.3487 | 110 | 5.5% |
| CP_PANEL_CLAUDE_A | Claude | +0.3487 | 107 | 5.3% |
| MUSE_MUSE_SPARK | Muse Spark | +0.1521 | 56 | 2.8% |
| QWEN_3_6_FLASH | Qwen3.6 Flash | +0.3949 | 33 | 1.7% |
| ARENA_AI_AGENT | Arena.ai Agent | -0.5794 | 0 | 0.0% |
| CLAUDE_5_1_FABLE | us.anthropic.claude-fable-5-1 | -0.1455 | 0 | 0.0% |
| CLAUDE_5_2_FABLE | us.anthropic.claude-fable-5-2 | -0.7803 | 0 | 0.0% |
| GEMINI_4_NEON | gemini-4-neon | -0.3407 | 0 | 0.0% |
| GPT_4_1_MINI | GPT-4.1-mini | -0.6001 | 0 | 0.0% |
| GPT_5_3_CODEX | gpt-5 | -0.6002 | 0 | 0.0% |
| MS_COPILOT | M365 Copilot (GPT-5) | -0.1155 | 0 | 0.0% |
| MUSE_MUSE_EMBER | Muse Ember | -0.4799 | 0 | 0.0% |
| MUSE_MUSE_SPARK_1_0_META_AI | Muse Spark 1.0 - Meta AI | -0.0817 | 0 | 0.0% |
| QWEN4_MAX | qwen4-max | -1.0365 | 0 | 0.0% |

Total replicates: 2000

## Verdict: RANKING NOT DISTINGUISHABLE

**No entrant wins 95%+ of bootstrap replicates.** The wins are spread across the field, consistent with RULES.md section 7: with 4 picks per entrant, the sampling noise is large enough that no ranking is robustly distinguishable.

The honest leaderboard stands: 18 rows, one column — "not distinguishable."

*Paper only. Zero capital. Not investment advice.*
