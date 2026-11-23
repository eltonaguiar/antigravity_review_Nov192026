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
