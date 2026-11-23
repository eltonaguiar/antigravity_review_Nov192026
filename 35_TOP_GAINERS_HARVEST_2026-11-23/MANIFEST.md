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

- **AskAnyModel → GPT-6.1 Terra (OpenAI)**, per operator identification. The pane carries OpenAI-house framing
  ("volatility is much more predictable than direction") and is the source attributed throughout `SYNTHESIS.md`.
- **1min.ai → Gemini 4 Neon (Google AI)**, per operator identification of the reply pasted at 2026-11-23T03:16Z
  (105,111 credits, 37.4 s). Saved as `harvest_1min_gemini4neon.txt`. **This is the only respondent that ranked the
  classes explicitly, and the only one that specified a complete TP/SL construction** — see synthesis §2.1 and §2.2.
- arena.ai's own transcript records its plan step verbatim: *"a detailed response plus maybe a workspace scaffold"* — it
  chose to build, not just describe.
- ChatPlayground pane timings name **GLM 5.3 Flash** as one of the responding models; the other two panes are unlabelled
  in the capture.

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
