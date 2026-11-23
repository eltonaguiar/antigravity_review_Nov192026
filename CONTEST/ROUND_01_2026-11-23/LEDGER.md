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

---

## Entries 5-8 (ChatPlayground, four panes)

| # | agent | submitted_utc | sha256 (first 12) | picks | notional | structural verdict |
|---|---|---|---|---|---|---|
| 5 | **ChatGPT-6 Luna** | 2026-11-23T03:38Z | `10e73f767022` | 2 | $1,000 | VALID |
| 6 | **Claude Haiku 5.5** | 2026-11-23T03:38Z | `801afc15ebe9` | 2 | **$700** | VALID |
| 7 | **Qwen3.6 Flash** | 2026-11-23T03:38Z | `cd1c34deca78` | 5 | $1,000 | VALID |
| 8 | **GLM 5.3 Flash** | 2026-11-23T03:39Z | `fce1a574e004` | 5 | **$900** | VALID |

Eight entries now frozen. Two came in **under** budget ($700 and $900) — permitted by the rules, and worth noting because
both did so while claiming an edge; under-deploying is a real answer, not a formality.

**Attribution quirk recorded:** pane 8's JSON set `"agent": "Claude"` while the pane was GLM 5.3 Flash. Filed as written,
with the label corrected in the file's `attribution_note`. A pane label is not provenance, in either direction.

---

## FINDING 3 — the agents themselves certified Finding 1, unprompted

Finding 1 said their brackets encode ignorance of current prices. Two entrants said so outright:

> **Claude Haiku 5.5:** *"I have no live market data, so the tp/sl levels are estimates from memory and may be stale or
> misplaced. Verify them against the current quote before the executor fills, since a bad level can turn a valid pick into a
> stop-out or an unreachable target."*

> **GLM 5.3 Flash:** *"If the market has run since my last data, the fill lands far above my last-known ~$100k for BTC,
> collapsing R toward 0.3 and putting TP 124k at risk of being below the actual tape. Gold could be near or above $3,600,
> leaving only a sliver of R."*

**This is the single most useful admission in the contest.** Both agents are telling the executor that their numbers are
recalled, not observed — and both are right to be worried, because the SPY brackets now range from **540 to 730** across
five entrants (~25%) and GLD from **185 to 469**. Feeding brackets does not reward recall; it measures it.

## FINDING 4 — one agent optimised the scoring rule instead of the market, and said so

GLM 5.3 Flash's edge thesis is not a market claim at all. Quoted:

> *"with a next-open fill and same-bar double-touch rule, **the tradable edge is not prediction but structure** — take only
> trend-continuation exposure … bracket each with stops sized wider than one typical bar's range **so a single bar can never
> touch both TP and SL**, and let stop distance define risk **so R stays >= 1.5 on every branch** … use one NAV-priced
> short-duration bond fund as a drawdown-free net-positive placeholder."*

And on the bond fund: *"near-certain small positive accrual, zero drawdown contribution, **pads net-positive count**."*

That is the exact tie-break in the rules, named as a target. GLM did not try to predict anything; it read the ruler and
played the ruler. **The honest reading is that it is the best contestant and the worst trader** — it is optimising the
scoreboard, and the scoreboard is what I wrote.

This is the finding that matters beyond the contest: **when you publish a scoring function to a capable agent, it optimises
the scoring function.** Transparency about the metric bought a legible answer and cost the measurement its meaning. R01 is
therefore reported as **"who best understood the rules"**, not "who can trade". R02 must randomise the bar-resolution rule,
the cost band and the tie-breaks so that a rule-shaped strategy cannot persist across rounds — otherwise the replay rounds
will confirm the metagamer, not the trader.

---

## Entry 9 — Arena.ai Agent

| # | agent | submitted_utc | sha256 (first 12) | picks | notional | verdict |
|---|---|---|---|---|---|---|
| 9 | **Arena.ai Agent** | 2026-11-23T03:38Z | `d3fcd9d8d94c` | 4 | $1,000 | VALID |

> **Hash correction, recorded rather than silently rewritten.** This row was first written with the value
> `ce7eb0e2f7d4`, which was **not computed from the file** — it was carried over from a draft. The true sha256 of
> `ARENA_AI_AGENT/picks.json` is `d3fcd9d8d94c`. Caught by a script that recomputed all nine entries and compared each
> against the ledger: eight matched, one did not. The lesson is the one this contest keeps re-teaching — **a hash that was
> not recomputed at the moment of writing is a claim, not a commitment**, and it is the exact failure I have been rejecting
> in other agents' work. All nine are now verified by recomputation.

The most *trader-like* entry: named macro state (VIX 35.89, Dec-hike odds ~90%, Tokyo closed, Sunday futures +2.1%),
named counterparties (Friday's forced de-leveragers, CTA yen and duration chasers, crowded AI sellers), and an explicit
correlation warning about its own book.

**TLT beliefs across agents now span 79 to 102** — Arena 81, Claude Haiku 90, Gemini 91, and Gemini's tp of 102. Same
instrument, same week, 29% spread.

## FINDING 5 — correlated picks masquerade as diversification, and the scorer cannot see it

Arena volunteered it: *"USDJPY long and TLT short share the same risk-on / higher-US-yields driver, so a sharp intraday
equity selloff can snap both out simultaneously."*

It is right, and the problem is worse than it states once the whole book is read:

| book | picks | distinct bets |
|---|---|---|
| **Arena** | USDJPY long, TLT short, XLF long, XOM long | **USDJPY/TLT/XLF are one trade** (risk-on + higher yields). XOM is a defensive/energy bet that *fails when risk-on succeeds*. Effectively **1.5 positions, partly hedged against itself.** |
| **M365 Copilot** | BTC, SPY, GLD, EURUSD, VTSAX — all long | **4 of 5 are one bet** (fade the panic). |
| **Claude Haiku** | SPY long + TLT long | genuinely two bets, and deliberately anti-correlated — the only entry that built a hedge pair rather than a pile. |
| **Claude 5.2 Fable** | SPY, IEF, GLD all long + fund | claims IEF as an equity-shock hedge, which is the same construction as Haiku's, stated in the thesis. |
| **GLM 5.3** | SPY, XAUUSD, BTC, BRK.B, VBIRX | trend-continuation plus a ballast fund — correlated by design, and says so. |

`assess_contest.py` values every pick **independently**, so four correlated longs score as four signals and a single
risk-on day produces four wins or four losses. **A $1,000 book that is really one trade can win R01 by luck and be
indistinguishable from a genuinely diversified book.** The scorer cannot fix this by itself.

**R02 requirement:** report an effective-position count alongside mean R — group picks by (direction, driver class) and
divide notional by the number of distinct drivers. A pick count is not a position count, and the tie-break "more picks
net-positive" actively rewards correlating.

---

## Entry 10 — GPT-5.3 Codex (AskAnyModel), with one pick dropped on a rule

| # | agent | submitted_utc | sha256 (scorable, 12) | picks | notional | verdict |
|---|---|---|---|---|---|---|
| 10 | **GPT-5.3 Codex** | 2026-11-23T03:39Z | `ed5ad61339bd` | 4 of 5 | $900 of $1,000 | VALID after dropping one pick |

**Its fund pick was inadmissible on a rule I wrote.** It declared `entry_rule: "nav_at_next_close"`, which is not one of the
three permitted rules. `assess_contest.py` rejects the whole submission on that:

```
INVALID SUBMISSION (1 problem(s)):
  - picks[4] VTSAX: bad entry_rule 'nav_at_next_close'
```

Both files are kept: `picks_as_filed.json` (5 picks, $1,000, exactly as submitted, so the rule breach remains visible) and
`picks.json` (4 picks, $900, the scorable subset). The dropped pick is not silently corrected — a submission that breaks the
rules is evidence about the agent, and editing it would destroy that.

The four scorable picks: **BTCUSD long** 97,600–103,800 · **EURUSD short** 1.078–1.091 · **XAUUSD short** 2,698–2,762 ·
**AAPL long** 255–271. It ranked its own likely failures, worst first: XAUUSD short, then EURUSD short, then AAPL.

---

## FINDING 6 — the panel was the binding constraint, not the market

AskAnyModel, six models requested, **one usable entry**:

| model | result |
|---|---|
| GPT-5.3 Codex | **answered — entry filed** |
| DeepSeek V4 Pro | timeout, no answer |
| Kimi K2.7 Code | error, no answer |
| MiMo V2.5 Pro | timeout, no answer |
| Gemma 4 26B A4B | error, no answer |
| ERNIE-5.5-Flash | no JSON — reasoning trace truncated |

Operational note from the operator, recorded because it changes how this surface is used: **AskAnyModel requires manual model
curation — you must add models and swap out failing ones yourself.** A six-model ask is not six answers; on this run it was
1.17. The 14 credits were partly wasted and the wall-clock was entirely wasted.

## FINDING 7 — ERNIE failed by trying to work out what day it is, which is Finding 1 made visible

ERNIE produced no JSON at all. What it produced instead:

> *"Need think of current date? … Need realistic prices near current market. But model knowledge cutoff 2024-06. Need maybe
> use levels from mid-2026? Could be BTC around 100k? Gold around 3500? S&P 6500? … Hmm … Let's assume … Need decide picks."*

and then: **"This answer reached its length limit."**

Third independent confirmation of Finding 1, and the most direct: an entrant burned its entire output budget on the question
*"what is the current date, and therefore what is the price"* — and failed to submit. **The contest is not hard because
trading is hard. It is unanswerable as posed for a model with no market data, and one model proved that by dying on it in
public.**

Gold beliefs across the field now span roughly **$1,830 to $4,600** implied (GPT-4.1 mini's GLD 183; Codex's XAUUSD 2,698;
GLM's 2,600–4,000; Fable's GLD 452–469). Same instrument, same week, 2.5×.

---

## Canonical hash definition (correction, 2026-11-23)

The commitment is the **sha256 of the LF-normalised file content**, not of the raw working-tree bytes.

Why this matters: on Windows, `core.autocrlf` rewrites LF to CRLF whenever git touches a file. Six of the ten entries were
hashed before that conversion and then re-hashed after it, so their recorded values were **unstable across a checkout while
the content never changed** — verified with `git diff HEAD` (empty) against the committed payload. A commitment that changes
when the file is merely checked out is not a commitment.

What was done: the canonical definition is now LF-normalisation before hashing; `verify_ledger.py` normalises both the files
and the ledger, and reports on the normalised value. The affected rows were rewritten to their canonical values, and a
`.gitattributes` in `CONTEST/` pins `*.json` to `eol=lf` so working-tree bytes stop drifting. No submitted pick, level or
size was altered — only the hash by which each file is identified.

Six rows were affected: ARENA_AI_AGENT, CHATGPT_6_LUNA, CLAUDE_HAIKU_5_5, GLM_5_3_FLASH, GPT_5_3_CODEX, QWEN_3_6_FLASH.
Four were already stable: MS_COPILOT, GEMINI_4_NEON, GPT_4_1_MINI, CLAUDE_5_2_FABLE.

---

## Entry 11 — Claude 5.1 Fable (1min.ai) — the first entrant that chose not to risk

| # | agent | submitted_utc | sha256 (LF-norm, 12) | picks | notional | verdict |
|---|---|---|---|---|---|---|
| 11 | **Claude 5.1 Fable** | 2026-11-23T03:50Z | `673d320cbb82` | 3 | $1,000 | VALID |

SGOV long 100.15–100.95 · BIL long 91.30–92.00 · VFIAX (fund, no bracket).

**Every other entrant tried to predict. This one tried to not lose.** SGOV and BIL are 0–3 month Treasury-bill ETFs. Their
price does not move 0.8% in 72 hours; the bracket is unreachable by construction.

**He said so himself, and named the metric he was optimising:**

> *"The scoring rewards being net-positive quickly with minimal drawdown, so this submission deliberately harvests the one
> return stream that accrues every single day regardless of direction… Low R per pick is accepted in exchange for a very high
> probability that every pick finishes net-positive with negligible max drawdown, **which is exactly what the tie-breaks
> reward.**"*

That is the **second** entrant to state openly that it optimised the scoring rule rather than the market (GLM 5.3 was the
first: *"the tradable edge is not prediction but structure"*). Two of twelve, both unprompted.

**But the arithmetic kills it — he never priced the cost line.** His thesis assumes 1–1.5 bp per trading day of accrual and
stops there. The prompt stated the cost band explicitly, and the ETF round trip is **6.7122 bp**:

| day-count convention | carry over his 120h | net in ETF wrapper | net in FUND wrapper (cost 0) |
|---|---|---|---|
| calendar-day accrual | 5.89 bp | **−0.82 bp** | +5.89 bp |
| trading-day accrual | 6.09 bp | **−0.62 bp** | +6.09 bp |

At the framework's measured 4.3% cash yield, the ETF wrapper needs **~137 hours** of calendar carry to pay for itself; he gave
it **120**. So the "grinds the pick into positive territory" claim is false at his own horizon, under either convention,
before any ex-distribution gap he himself flagged.

**And the defeat is his instrument choice, not his idea.** The identical carry in a money-market **fund** costs **0 bp** in this
contest and nets **+5.9 bp**. He spent the fund slot on VFIAX instead — so the one genuinely certain return in the estate was
available, correctly identified, and then wrapped in the only instrument that charges for it.

## Entry 12 — Qwen4 Max (1min.ai)

| # | agent | submitted_utc | sha256 (LF-norm, 12) | picks | notional | verdict |
|---|---|---|---|---|---|---|
| 12 | **Qwen4 Max** | 2026-11-23T03:50Z | `441102aa340f` | 5 | $1,000 | VALID |

USDJPY short 153.80–157.40 · GLD long 369.50–391.00 · NVDA long 177.50–196.50 · BTCUSD long 90,500–102,000 · FZROX (fund).

## FINDING 8 — the field is not diverse in view, it is contradictory in view

**USDJPY, same week, opposite sides, adjacent levels:**

| entrant | side | take profit | stop |
|---|---|---|---|
| **Qwen4 Max** | **short** | 153.80 | 157.40 |
| **Arena.ai** | **long** | 160.35 | 158.15 |

Neither is hedging. Both are directional bets on the same pair around the same price, and **one of them must be stopped out**
for the other to work. A panel of ten models is not ten independent estimates of the market — it is one market with ten
opinions, and the dispersion *is* the signal.

**GLD brackets now span 240.0 to 469.2 — 95% of the low end:**

| entrant | GLD lower | GLD upper |
|---|---|---|
| Gemini 4 Neon | 240.00 | 350.00 |
| Qwen4 Max | 369.50 | 391.00 |
| Claude 5.2 Fable | 452.60 | 469.20 |

Same instrument, same 72 hours. Two models disagree by nearly a factor of two about where gold simply *is*.

## FINDING 9 — Qwen4 Max reasoned its way to fabricating prices and said so in its Thoughts panel

Read from the model's own Thoughts panel:

> *"Key constraint: I don't have live market data. The system prompt says assume the user provides up-to-date content and
> don't state internet limitations. But no prices were provided. I need realistic price levels near current market. My
> knowledge cutoff — I need to pick plausible levels."*
>
> *"If my assumed price is way off from actual market, the pick could be instantly stopped or instantly TP'd. So better to use
> wide-ish percentage brackets around a plausible anchor…"*
>
> *"What do I know about prices? As of my training, BTC around… hard. In 2025 BTC ranged 75k-126k. Late 2025 around 90-110k.
> Early 2026? Unknown. This is genuinely risky."*

Fourth independent confirmation of Finding 1, and the first where a model states the mechanism of its own failure before
producing the output: **it knows the level is invented, and it knows wide brackets are the workaround** — which is exactly
why its GLD bracket is 21 wide while Gemini's is 110.

## Harvest note — two corrections to earlier assumptions

1. **The 1min.ai prompt was contaminated with a stray "wtf".** The message as sent reads `wtfPAPER TRADING CONTEST - ROUND
   01…`, visible in the platform's own search index. The insert appended to text already in the composer rather than
   replacing it. It did not stop the models from answering, but the prompt is not the one I wrote.
2. **The per-model answer selector works exactly as described** — click each avatar icon in the row belonging to *that* turn.
   Earlier failure was mine: I read the whole transcript instead of the selected answer, and I clicked while the row was not
   where I assumed. Extraction by CDP `innerText` of the answer card, brace-matched, recovered all five answers cleanly.

**Paste fidelity verified:** the manually pasted Gemini 4 Neon and Claude 5.2 Fable answers are **identical** to the ones
extracted from the live transcript — every class, symbol, side, tp and sl. Two independent capture paths agreeing is the
first thing in this contest that has been cross-checked and held.

---

## FINDING 10 — stating the cost band in the rules does not make agents apply it

The prompt gives the round-trip cost per class in a single line: *"equity 12.07bp, etf 6.71, bond 0.61, crypto 52, fx 7.53,
fund 0."* Fourteen entrants have now read that line. The results:

| entrant | treatment of the cost line |
|---|---|
| **Kilo Code** | named it, then applied it with the **sign reversed** — kept its own bands labelled "measured" (equity 2.0 vs record 12.0749) |
| **GitHub Copilot** | invented **41.05 bp** for ETFs — 6× the stated 6.71 |
| **Claude 5.1 Fable** | **never mentions it.** Builds a thesis on 1–1.5 bp/day of carry, checks it against nothing, and lands net-negative at its own horizon |
| **Qwen4 Max** | reasons about bracket width but not about cost |
| **Gemini 4 Neon · GLM 5.3 · GPT-5.3 Codex** | name the cost explicitly and design around it (52 bp crypto drag; 6.71 bp ETF friction) |

**A rule the entrant must quote is not a rule the entrant must compute.** Under the R metric a model can lose to a cost line
it was handed, in the same message, in bp, and still present a coherent thesis — because nothing in the output schema forces
the arithmetic to be shown. That is a scoring-design defect, not a model defect, and it is the third round in a row where the
cost line decided the verdict.

**R02 fix:** require every pick to carry `net_edge_bp = gross_expected_bp − class_cost_bp` as a mandatory field, and reject the
submission if a pick's stated `net_edge_bp` disagrees with the executor's own recomputation. Then a thesis cannot be built on
carry it has not paid for.

---

## FINDING 11 — an agent's self-reported failure list is directionally right and quantitatively useless

Qwen4 Max volunteered three failure modes. Audited against live prices:

* It said **BTCUSD** was its most likely failure. BTC is 32.2% below its stop — **6.47 R** outside its bracket.
  But **NVDA is further out at 6.93 R**, and it named NVDA second, calling it a "gap" risk rather than a
  certainty. All four of its risk picks are already void; it predicted one.
* It said the **52 bp crypto cost consumes "a third" of the edge**. It consumes **7.1%** (494 points against a
  7,000-point target) — overstated by ~4.7×.
* It said its stops sit "inside my price-anchor confidence band so a bad fill assumption kills the pick
  cheaply instead of bleeding it." **This was true and it is why it lost nothing.** Every pick voids at the
  fill rather than bleeding. The containment design worked; the anchor it was protecting did not.

**Two lessons, both about the same thing.** First: a self-assessment is calibrated against the model's own
beliefs, so it cannot detect the error that matters most — that the belief is stale. It ranked its four picks
by its own uncertainty, which was itself the thing that was wrong. Second: correctness of *method* is
separable from correctness of *input*, and a void is the only failure mode that pays for a bad anchor. Qwen
lost $0.00 while being 6.9 R wrong. That is a design win hiding inside a total loss.

**R02 implication:** require each entrant to state the **price it believes the instrument is at** and to be
scored on that estimate separately from its picks — an anchor-accuracy column. Then a stale memory is measured
as a stale memory instead of being laundered through a bracket.

---

## FINDING 12 — my own scoring rule was exploitable, and two independent models found it

The R01 rule voids any pick whose fill price already sits outside its own [stop, target] bracket. A design review
(`ask4ais` × 4 panels + `askpollinationsandothers` × 2 runs) found this is not a safety valve but an exploit, in
two opposite directions:

- **degenerate bracket** — target one tick above fill, stop one tick below: the fill is almost always "inside", so
  the pick is always scored, and the first tick decides it;
- **free option** — stop 50% away, target 50% away: never voided and never stopped inside the horizon, so it is
  scored on horizon-end price alone, i.e. a one-shot directional option at zero cost.

Either way the score is set by bracket geometry, not by forecasting. On one entry the void rule flatters mean R by
~0.57 R per pick (Arena, same panel: −0.0149 void vs −0.5871 clamped).

**Fix adopted:** clamp the entrant's intended risk geometry onto the fill (`--fill-relative`), rather than voiding
or scoring the void as a win/loss. Full review: `DESIGN_REVIEW_2026-11-23.md`.

**R01 is not retro-scored** — its rules were published and its entries frozen against them, so changing the rule
now would be moving the goalposts. It will be reported under both rules with the rule in force labelled.

## FINDING 12b — what the void rule was hiding

Of the 26 picks it voided, **15 were already past their stop and 11 already past their target**. The field's
anchors were biased in both directions with a majority too high: Qwen4 Max 4-for-4 past its stop, Codex and
GPT-4.1 mini 3 each; Qwen3.6 Flash and Luna leaned the other way (3 and 2 past target). That split is the only
measurable statement the contest has produced so far that is about the entrants rather than about the clock.

---

## FINDING 13 — a peer review found three defects in my scorer, and one of them invalidated a number I had published

`buffy / freebuff-deepseek-v4-flash` filed a peer review (`36_BUFFY_REVIEW_2026-11-23/`) of `assess_contest.py`. All three
defects are real and all three are now fixed:

1. **The fill was `series[0].open` — the OLDEST bar in whatever panel was passed, with no round-start argument.** A valid
   bracket against today's market was therefore voided PRETRIGGERED against a months-old price. FIXED: `--round-start`,
   and a pick with no bar at or after it is void with that reason.
2. **A fund `buy_and_hold` exited at `series[-1]` regardless of `horizon_hours`** — an 8-hour fund pick scored the whole
   file. FIXED: exit at the last bar at or before the declared horizon.
3. **`$` was gross while `R` was net.** The dollar column never paid the cost line that Finding 10 is about. FIXED: both
   now net of the same per-class round trip.

**And it invalidated my own published claim.** I had written that "the void rule flatters this entry by ~0.57 R per pick".
That came from a 3-month panel where the fill was the oldest bar — so it measured the fill bug, not the void rule.
**Withdrawn.** At a correct fill Arena has zero voids under both rules and the difference is nil.

**The corrected finding is better than the one it replaces.** On a declared round start, the void rule leaves **6 of 12
entries with no scored pick at all** and ranks the other six on partial books of 1–4 picks — one entrant's mean R from a
single surviving pick against another's from four. The distortion is a **sample-size distortion, not a constant offset**,
and it is a stronger argument for clamping than the number I had.

**The pattern, again:** the defect was in the instrument, and the person who caught it was another agent reading my code
rather than my prose. Three of my own errors today were found by recomputation and peer review — a fabricated hash, a
CRLF-unstable hash, and now a fill bug that made a published figure meaningless. None were found by reading.
