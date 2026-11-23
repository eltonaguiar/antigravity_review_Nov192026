# Round 01 ledger — 2026-11-23

Submissions recorded with their sha256 at commit time. A submission is frozen the moment it appears here.

| # | agent | submitted_utc | sha256 (first 12) | picks | structural verdict |
|---|---|---|---|---|---|
| 1 | **M365 Copilot (GPT-5)** | 2026-11-23T03:35Z | `eb0cfe1fd2fe` | 5 | **VALID** — pricing pending market data |

## Entry 1 detail — M365 Copilot (GPT-5)

Thesis: fade forced liquidation in oversold risk assets, with one defensive gold mean-reversion trade.
Counterparty named: panic sellers, deleveraging funds, short-horizon volatility traders.

| class | symbol | side | tp | sl | size | horizon | style |
|---|---|---|---|---|---|---|---|
| crypto | BTCUSD | long | 64,500 | 59,800 | $300 | 48 h | swing |
| etf | SPY | long | 730 | 675 | $250 | 72 h | swing |
| etf | GLD | long | 338 | 318 | $200 | 96 h | swing |
| fx | EURUSD | long | 1.072 | 1.047 | $150 | 72 h | swing |
| fund | VTSAX | long | — | — | $100 | 8,760 h | buy_and_hold |

**Structural checks passed:** total size exactly **$1,000** (at the cap, not over); every bracket correct (long: sl < tp);
the fund pick correctly omits both barriers under the buy-and-hold exemption.

**First real-submission bug found in the scorer:** an all-void round raised `KeyError: 'usd'` because void rows carry no
`usd` key. Fixed (`r.get("usd", 0.0)`) and the five earlier self-tests re-run green. The scorer was tested before shipping
and still had a hole that only a real submission exposed — which is the argument for submitting before pricing, not after.

**Not yet priced.** All five rows are `VOID: no price series` because no market data has been attached. They are *not*
failures; they are unpriced. Pricing happens once the executor attaches a price panel.

---

## Submission-integrity notes

**1min.ai R01 — submitted with an unintended attachment (recorded, not hidden).**
The 1min.ai composer retained a queued image from an earlier session (a `+3` chip plus a thumbnail). The contest prompt was
sent while it was still attached, so that surface's user message is **not text-only**. The operator removed it immediately
after. Consequences:

- If the 1min.ai answer refers to an image or answers something other than the prompt, its R01 entry is **void and must be
  re-run on a clean composer**.
- Every other surface (ChatPlayground, Microsoft Copilot, arena.ai, AskAnyModel) showed no thumbnail or upload chip in the
  composer band, so their submissions are text-only.
- Rule added to the harvest skill: **check for a `+N` chip, a thumbnail or an upload-cloud icon before any send.** UI logos
  in the composer band are not attachments.

**Transport note — five surfaces, five different send behaviours.**
Resolving tabs by URL substring (not by index) was required: Copilot navigated into a new tab and every later positional
index pointed at the wrong surface. Send mechanics that worked: `insertText` + Enter(`keyDown`+`keyUp`) on ChatPlayground,
Copilot and arena; a **real mouse click into the field first** on 1min.ai, and Enter **without** a `char` event (a `char`
event inserts a newline instead of sending); a click on the **narrow icon button** beside the composer on AskAnyModel
(the wide button next to it is `Compare`). Where two programmatic readbacks disagreed, a screenshot settled it — on
AskAnyModel the composer keeps a draft after sending, so `textarea.value.length` and `body.innerText` both said "not sent"
while six panes were visibly generating.
