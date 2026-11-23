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
| `harvest_1min.txt` | **GPT-4.1 mini (OpenAI)** | contains *"can be a complex but systematic endeavor"* — the phrase unique to its pasted reply (14.1 s, 8,391 credits) |
| `harvest_1min_gemini4neon.txt` | **Gemini 4 Neon (Google AI)** | contains *"classic quantitative finance problem"* — unique to its pasted reply (37.4 s, 105,111 credits) |
| `harvest_1min_r2.txt` | **Qwen4 Max (Alibaba Cloud)** — *operator-identified* | later portion of the same 1min.ai transcript; **neither opening phrase is present**, so this attribution rests on the operator's identification, not on a quote match. Contains the extended data-integrity passage (no backfilled restatements, retroactive split adjustment changing distance-from-52w-high, LULD halts) |
| `harvest_arena.txt` / `_r2` | arena.ai agent | its own plan step is in the transcript: *"a detailed response plus maybe a workspace scaffold"* |
| `harvest_chatplayground.txt` | unlabelled ×3 | one pane named **GLM 5.3 Flash**; the other two are not labelled in the capture |

**Attribution correction (recorded because it nearly propagated):** `harvest_1min.txt` was initially logged as
"1min.ai, model undisclosed". The GPT-4.1 mini paste proved it by exact opening phrase. **The 1min.ai tab contained at
least two different answers** — GPT-4.1 mini and Gemini 4 Neon — so a single capture of that tab silently mixed sources.
Any later reader of these files should key on the opening phrase, not the filename.

**Consequence for counting:** the answers are **seven models across four surfaces** — GPT-6.1 Terra, GPT-4.1 mini,
Gemini 4 Neon, Qwen4 Max, GLM 5.3 Flash and two unlabelled ChatPlayground panes, plus the arena.ai agent. The **1min.ai
tab is multi-model**, like AskAnyModel, not a single model. No result in `SYNTHESIS.md` depends on the count — it depends
on which claim came from which model, which the table above fixes.

**Cost per answer on 1min.ai**, which is the pricing lesson of this exercise:

| Model | Latency | Credits | Verdict at that price |
|---|---|---|---|
| GPT-4.1 mini | 14.1 s | **8,391** | generic syllabus — but it asked the one question we could answer today (§2.3) |
| Gemini 4 Neon | 37.4 s | **105,111** | the only explicit class ranking and the only complete TP/SL design (§2.1, §2.2) |
| Qwen4 Max | **277.7 s** | **166,402** | *not yet read in full* — only a partial capture exists (`_r2`), so nothing is claimed from it |

**Gemini 4 Neon at 105K credits was the best value in this set by a wide margin** — 12.5× the price of GPT-4.1 mini for
the only two artefacts (a class ranking and a TP/SL construction) that can be implemented. Qwen4 Max cost 1.6× Gemini and
58× GPT-4.1 mini, and produced a longer answer whose distinctive content is currently unverified because the capture is
partial. **A paste of the Qwen4 Max opening line would let it be verified like the other two and added to §2.**

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
