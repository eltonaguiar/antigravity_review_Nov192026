# MANIFEST — top-gainers harvest, 2026-11-23

**Question asked of four agents** (verbatim, from the operator):

> If you were tasked to reverse engineer the daily or weekly top gainers for stocks, crypto mutual funds etc, how would
> you go about? i.e. you want to be able to give signals including a TP/SL for stocks/crypto, maybe forex, and determine
> first of all which asset class is more predictable.. is a particular "symbol" more predictable, or a symbol and a
> direction like long vs short? what is "proven", would you back-test, and how can you forward-test, and which metrics
> would you need to measure

## What was captured

| File | Surface | Tab URL | Bytes | Completeness at harvest |
|---|---|---|---|---|
| `harvest_1min.txt` | 1min.AI | `app.1min.ai/chat-with-ai/70e8483c…` | 11,225 | answer present, ends with an offer to expand |
| `harvest_arena.txt` | arena.ai | `arena.ai/agent/01a20666-cf03…` | 21,982 | **prose complete; agent still writing code** (`gainers_research/src/…`, `Trade` dataclass with `entry/exit/reason∈{tp,sl,time}/r/bars`) |
| `harvest_askanymodel.txt` | AskAnyModel | `askanymodel.xyz/dashboard/multi-chat` | 51,158 | multi-model; one pane showed `Thinking` |
| `harvest_chatplayground.txt` | ChatPlayground | `web.chatplayground.ai` | 32,616 | three panes showed **`finished responding`** |

## Attribution

Verified by distinctive opening phrases, not by memory or label:

| File | Model | Evidence |
|---|---|---|
| `harvest_askanymodel.txt` / `_r2` | **GPT-6.1 Terra (OpenAI)** | operator identification; contains *"research and trading-system design problem"* at offset 26,847, in no other file |
| `harvest_askanymodel_full.txt` | **six panes: Claude Opus 5.5, Grok 4.6, Command A+, GPT-6.1 Terra, Inkling Small, Gemini 3.5 Flash Lite** | operator paste 2026-11-23T03:18Z, 12,668 tokens — authoritative for citation; contains Opus's IC calibration ("0.02–0.05 realistic, above 0.1 is a bug or leakage") and Grok's mandatory baseline |
| `harvest_1min.txt` | **GPT-4.1 mini (OpenAI)** | contains *"can be a complex but systematic endeavor"* — the phrase unique to its pasted reply (14.1 s, 8,391 credits) |
| `harvest_1min_gemini4neon.txt` | **Gemini 4 Neon (Google AI)** | contains *"classic quantitative finance problem"* — unique to its pasted reply (37.4 s, 105,111 credits) |
| `harvest_1min_r2.txt` | **Qwen4 Max (Alibaba Cloud)** — *operator-identified* | later portion of the same 1min.ai transcript; **neither opening phrase is present**, so this attribution rests on the operator's identification, not on a quote match. Contains the extended data-integrity passage (no backfilled restatements, retroactive split adjustment changing distance-from-52w-high, LULD halts) |
| `harvest_arena.txt` / `_r2` | arena.ai agent | its own plan step is in the transcript: *"a detailed response plus maybe a workspace scaffold"* |
| `harvest_chatplayground.txt` | **all four panes** (see below) | round-1 capture, partial — page has since reset |
| `harvest_chatplayground_full.txt` | **Luna (ChatGPT-6), Claude (latest), Qwen3.6 Flash, GLM 5.3 Flash** | operator paste 2026-11-23T03:17Z, 9,762 tokens — the authoritative full text, now replacing the partial capture for citation |

**Attribution correction (recorded because it nearly propagated):** `harvest_1min.txt` was initially logged as
"1min.ai, model undisclosed". The GPT-4.1 mini paste proved it by exact opening phrase. **The 1min.ai tab contained at
least two different answers** — GPT-4.1 mini and Gemini 4 Neon — so a single capture of that tab silently mixed sources.
Any later reader of these files should key on the opening phrase, not the filename.

**Consequence for counting:** the answers are **seventeen models across four surfaces** — GPT-6.1 Terra, GPT-4.1 mini,
Gemini 4 Neon, Qwen4 Max, GLM 5.3 Flash and two unlabelled ChatPlayground panes, plus the arena.ai agent. The **1min.ai
tab is multi-model**, like AskAnyModel, not a single model. No result in `SYNTHESIS.md` depends on the count — it depends
on which claim came from which model, which the table above fixes.

**Cost per answer on 1min.ai**, which is the pricing lesson of this exercise:

| Model | Latency | Credits | Verdict at that price |
|---|---|---|---|
| **Claude 5.1 Fable** | 151.7 s | **1,511,466** | **most complete research programme of the sixteen** — three-task A/B/C build order, BTC-beta stripping, the size-x-catalyst 2x2, and Lo-MacKinlay variance ratio over Hurst (§2.8) |
| **Claude 5.2 Fable** | 71.4 s | **897,257** | **best answer of the set** — reframed the problem to an event study, cited the MAX/lottery effect that argues for *fading* gainers, and supplied the P(TP before SL) = SL/(TP+SL) arithmetic (§2.5) |
| **Mistral Small** | 25.4 s | **3,471** | **best value per credit** — the only operational predictability battery (Ljung–Box, Hurst, entropy, HMM regimes, naive baseline) plus the smoothing argument against mutual funds (§2.4) |
| GPT-4.1 mini | 14.1 s | **8,391** | generic syllabus — but it asked the one question we could answer today (§2.3) |
| Gemini 4 Neon | 37.4 s | **105,111** | the only explicit class ranking and the only complete TP/SL design (§2.1, §2.2) |
| Qwen4 Max | **277.7 s** | **166,402** | *not yet read in full* — only a partial capture exists (`_r2`), so nothing is claimed from it |

**Price did not predict quality — but the extremes were the best answers.** The cheapest (3,471) and the most expensive
(897,257) were the two that mattered: one supplied the measurement battery, the other supplied the reframing and the
arithmetic. The mid-priced answers were competent and non-decisive. **The only reliable predictor of a good answer was
whether it committed to a number or a test** — and whether it was willing to argue against the premise of the question.

## Final state of the four surfaces (verified ~03:2x UTC, after all four reportedly finished)

| Surface | Live page at final check | Implication |
|---|---|---|
| arena.ai | **still running** — 73,038 B, now at `python3 run_study.py 2>&1 \| sed -n '/2b\./,/2c\./p'` | only surface still producing |
| 1min.ai | **blank** — 2,362 B, app shell + a *new* chat ("How can I assist you today?"), unrelated leftover prompt visible | transcript gone |
| AskAnyModel | **blank** — 738 B, app shell only; credits read **460** (was 498) | transcript gone; 38 credits spent on the answers |
| ChatPlayground | **blank** — 917 B, app shell only | transcript gone |

**This is the finding that justifies the whole capture discipline:** within roughly an hour of answering, three of the
four surfaces had lost their rendered transcripts — two reset to an empty composer, one navigated to a new chat. **The
committed files are now the only surviving record of GPT-6.1 Terra's, GPT-4.1 mini's, Gemini 4 Neon's, Qwen4 Max's and
GLM 5.3 Flash's answers.** Had these been summarised in chat instead of captured and committed, they would be gone.

Arena is captured at three points (`_r1` 21,691 · `_r2` 55,285 · `_r3` 73,038 B); a fourth capture is required when it
finishes, before any of its numbers are cited.

## Round 2 capture (`*_r2.txt`) — same evening, re-harvested

| File | Bytes | Change |
|---|---|---|
| `harvest_arena_r2.txt` | **54,889** | grew from 21,982 — now running `python3 run_study.py`, with a `purged_walk_forward(panel, n_folds=5, embargo=10, horizon=5)` implementation using an embargo gap so overlapping labels cannot leak |
| `harvest_1min_r2.txt` | 27,990 | grew from 11,225 — continued the answer into data-integrity detail (no backfilled restatements, retroactive split adjustment, LULD halts) |
| `harvest_askanymodel_r2.txt` | 49,574 | unchanged (same pane state) |
| *(chatplayground)* | — | **page reset to a blank composer** ("Ready when you are"). The 32,616-byte round-1 capture is now the only copy of those three answers — which is precisely why raw harvests are committed rather than summarised in place. |

## Method

CDP on the agent Chrome profile (`127.0.0.1:9222`, Chrome/157.0.8103.79), 4 page targets, `Runtime.evaluate` of
`document.body.innerText` per target via `websocket-client` with `suppress_origin=True` (Chrome rejects a default
`Origin` header with 403). Script: `harvest_tabs.py`; paragraph/keyword digest: `digest_tabs.py`.
**No clicks of any kind were issued** — read-only extraction, so the A/B vote rows on the comparison surfaces were never
touched.

## Caveats that must travel with these files

1. **`document.body.innerText` captures rendered text, not the full transcript.** Long answers that virtualise (lazy-render
   on scroll) may be truncated at the top. The 1min.ai capture in particular begins mid-page.
2. **arena.ai was mid-work.** Its code output is not captured. Re-harvest before quoting anything about its implementation.
3. **AskAnyModel renders multiple panes.** The file is a concatenation of all of them in DOM order; it does not attribute
   cleanly per model without diffing the panes.
4. **None of this is evidence.** These are model opinions about methodology. The only measured facts in this folder are in
   `SYNTHESIS.md` §1, §2 and §5, and each of those cites an artefact from this estate.

## Files

- `SYNTHESIS.md` — the merged answer, the predictability-vs-tradability reframing, the power arithmetic nobody supplied,
  and the five things to build first.
- `harvest_*.txt` — raw captures, unedited.

*Paper only. Zero capital. Not investment advice.*
