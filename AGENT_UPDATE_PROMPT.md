# AGENT_UPDATE_PROMPT — the exact question each agent answers when reporting

**Purpose:** get a comparable, gate-checked status line out of every agent (Zoo Code, Kilo Code, GitHub Copilot, the
Antigravity swarm, and the operator), instead of a prose summary that cannot be audited.

**Why this prompt replaced the old one.** The previous "what are your picks" prompt produced three failure modes:
picks with no `n`, picks costed at invented bands labelled *measured*, and backtest results presented as if they were
live evidence. Each question below closes one of those.

Answer in the numbered structure. **If a field is unknown, write `UNKNOWN` — do not estimate it.** `UNKNOWN` is an
accepted answer; a guessed number is a rejected answer.

---

## Part A — current best picks, per asset class

For **each** of: `STOCKS · ETFs · BONDS · MUTUAL_FUNDS · FOREX · CRYPTO (incl. meme) · COMMODITIES · OPTIONS ·
FUTURES · PREDICTION_MARKETS` — one row, even if the row is `none`:

| Field | Requirement |
|---|---|
| `CLASS` | as listed |
| `VERDICT` | one of `DEAD / UNKNOWN / CANDIDATE / VEHICLE` |
| `PICK` | symbol or `none`. One name only — no "or" |
| `n` | number of independent observations. `0` means the row is inadmissible |
| `EDGE_NET_BP` | net of cost, in basis points, **and the cost you used** |
| `COST_BASIS` | `measured` or `assumed` — `measured` must match `COST_OF_RECORD.md` |
| `DSR` and `N_TRIALS` | deflated Sharpe and the trial count you deflated at |
| `PBO` | and whether it is better or worse than the **0.51** noise baseline |
| `EXEC` | `BUY_AND_HOLD` / `ENTRY_ONLY` / `ENTRY+TP/SL` / `REBALANCE_MONTHLY` |
| `KILL_RULE` | the **frozen** condition that ends it, with a number |
| `EVIDENCE` | path or commit sha for every number above |

## Part B — the five questions, per **endorsed** pick only

Skip this section entirely if you endorse nothing (**that is the expected answer today**).

1. **Mechanism** — one paragraph. Why does this edge exist?
2. **Counterparty** — who is on the other side, and why do they accept a negative expected return?
3. **Why this symbol** — not "why this class". What makes this instrument the right expression?
4. **Why now** — what state is the market in that makes it live today, and what would end that state?
5. **What kills it** — the specific number that ends this thesis.

If you cannot answer #2, you have a correlation, not a strategy.

## Part C — tracker / paper-trading status ("future testing")

Backtests are not evidence. This section is the only place live evidence is reported.

| Field | Requirement |
|---|---|
| `TRACKER_NAME` | identifier |
| `STATE` | `RUNNING / HALTED / NOT_STARTED / DEAD` |
| `STARTED_UTC` | date the clock started |
| `OBS_CLOSED` | closed observations so far |
| `OBS_NEEDED` | observations required before a verdict is permitted, **and the power calculation behind it** |
| `NET_PNL_PCT` | and `MAX_DD_PCT` |
| `SIZE` | `$0` unless real capital is deployed — paper must be labelled paper |
| `FILLS_VS_MODEL` | realised slippage vs the backtest's assumed slippage, in bp |
| `NEXT_CHECKPOINT` | date |
| `KILL_RULE` | frozen |

State plainly which of the following you have: **backtest only / paper forward / micro-live / live**. An agent that
reports three of four and does not name which one is the finding.

## Part D — the overall ranking

Answer in this exact shape, because it is the shape a human can act on:

> "My top five across stocks, mutual funds, meme coins, bonds, ETFs, options, forex and commodities — after extensive
> research and backtesting, tested against **\[name the variables\]** — was **\[list\]**. Across each asset class we have
> a ranking, however the overall picks worth spending money on were **\[list, or `none`\]**. The reason for this is
> **\[the number\]**."

Requirements on that answer:

- Name the **variables actually tested** (data integrity, cost model, deflation, walk-forward, regime, capacity…).
- Give **one overall ranking**, not five class rankings stapled together.
- The reason must be **a number**, not an adjective. "Not enough edge" is rejected; "DSR 0.318 against a 0.95 gate" is
  accepted.
- If the honest answer is `none`, say `none` and say what would change it. **Zero endorsed picks is a valid, respectable
  answer** — it is the answer four agents gave independently on 2026-11-23.

## Part E — class-specific notes the operator has asked about

- **Mutual funds:** state the fee arithmetic (expense ratio + minimums + maintenance) against the index-ETF
  alternative over 10 years. Current record: **$18,520 active vs $1,050 index ETF per $100k/10yr = 17.6×**.
- **Meme coins:** admissibility requires `n ≥ 30` and net above the **20–52 bp** crypto round trip. If the row cannot
  clear that, it is `UNKNOWN`, not `CANDIDATE`.
- **Options / futures:** if there is no cost layer, there is no row. Write `UNKNOWN` and name the missing input.

## Part F — what you refuse to claim

One short list of the things you were asked for and will **not** assert, with the reason. This is where a good agent
distinguishes itself: it is the section that prevents a fabricated number from entering the record.

---

## Scoring the answers

| Check | Rejects the answer if… |
|---|---|
| Cost labelled `measured` but ≠ `COST_OF_RECORD.md` | mismatch without reconciliation |
| `n` absent, or `n=0` with a verdict other than `UNKNOWN`/`DEAD` | inadmissible row |
| Net edge **below** the class round trip | arithmetic is broken |
| DSR quoted without the trial count | unattributable |
| PBO compared to nothing | no baseline |
| Backtest presented as forward evidence | category error |
| Overall ranking with an adjective instead of a number | unauditable |
| Empty list with no reason | incomplete — but an empty list **with** a reason passes |

*Paper only. Zero capital. Not investment advice.*
