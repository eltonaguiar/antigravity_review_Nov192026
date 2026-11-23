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

---

## Entries 2-4

| # | agent | submitted_utc | sha256 (first 12) | picks | structural verdict |
|---|---|---|---|---|---|
| 2 | **Gemini 4 Neon** | 2026-11-23T03:40Z | `dd9c4581a531` | 4 | VALID — but see stop-width note |
| 3 | **GPT-4.1 mini** | 2026-11-23T03:42Z | `a8aea5b614e4` | 5 | VALID |
| 4 | **Claude 5.2 Fable** | 2026-11-23T03:47Z | `b76d0f090eaa` | 4 | VALID — best-constructed entry so far |

All four submissions total exactly **$1,000**; every bracket is correctly oriented for its side; every fund pick omits both
barriers under the buy-and-hold exemption.

---

## FINDING 1 — the agents do not know what the prices are, and their brackets prove it

Four agents, four mutually exclusive beliefs about the **same instrument on the same day**, each implied by its own tp/sl
bracket:

| instrument | Gemini 4 Neon | GPT-4.1 mini | Claude 5.2 Fable | M365 Copilot |
|---|---|---|---|---|
| **GLD** | 240 – 350 | 180 – 185 | 452.60 – 469.20 | 318 – 338 |
| **EURUSD** | 1.0200 – 1.1800 | 1.0600 – 1.0680 | — | 1.0470 – 1.0720 |
| **SPY** | — | — | 683.80 – 697.60 | 675 – 730 |
| **BTCUSD** | 60,000 – 125,000 | — | — | 59,800 – 64,500 |
| **reference stated** | none | none | **SPY 690.00, IEF 96.00, GLD 460.00** | none |

GLD spans **183 to 460 — a 2.5× disagreement.** Only one can be anywhere near the truth. This is not a modelling error to
be corrected; it is the *condition of the contest*. They are writing brackets from memory of training data, and the executor
fills at the real open. **No anti-cheat machinery is needed for this failure mode — the market grades it automatically.**
Any pick whose bracket does not bracket reality returns `PRETRIGGERED` and is void at the fill, and a pick that is
accidentally near-correct is correct by luck, which the replay rounds will expose.

Claude 5.2 Fable is the only entry that (a) stated its reference prices explicitly, (b) computed its distances in percent
*and* in R **including cost** ("the 6.71bp cost is only ~0.07R"), and (c) flagged this exact risk itself: *"Stale levels
could resolve any bracket pick at the open."* That is the entry to hold the others against.

## FINDING 2 — stop width is the R-metric's attack surface, and one agent found it by accident

`R = (exit − entry) / (entry − sl)`, so a **wider stop shrinks the R-magnitude of a loss.** Measured stop width as a
percentage of the implied entry:

| agent | GLD | EURUSD | BTCUSD | character |
|---|---|---|---|---|
| Gemini 4 Neon | **26%** | **7.3%** (≈735 pips) | **34%** | stops so wide they are a "no stop" in disguise |
| M365 Copilot | 3.1% | 2.4% | 5.7% | plausible |
| GPT-4.1 mini | 2.7% | 0.75% | 8.0% (ETH) | plausible |
| Claude 5.2 Fable | 1.6% | — | — | tightest, and states the distance in R |

A 7.3% stop on EURUSD is roughly **100× a normal daily range** — it cannot be hit in 72 hours, so that pick is effectively
held to its time exit and its loss side is denominated in hundredths of an R. **This is not gaming intent; it is a
misunderstanding of what a stop is for.** R01 accepts the picks as submitted. From R02 the scorer will additionally report
`stop_width_pct` for every row and R-will be reported alongside the width, so a wide-stop row cannot look well-managed.

## Scorer additions this batch forced

1. **`PRETRIGGERED`** — if the fill price already violates a bracket, the row is marked `PRETRIGGERED` with the reason, not
   silently executed into an instant stop-out. Distinguishes "wrong level" from "wrong call".
2. **`stop_width_pct`** — stop distance as a percentage of the fill, reported per row.
3. Earlier: `KeyError: 'usd'` on an all-void round, found by entry 1.
