# Justification rules — what makes a pick admissible

A pick is a **claim about the future**. These rules exist because a scan hit is not a claim, and a symbol with no
observations cannot carry an estimate. Every pick in `34_FINAL_PICKS_2026-11-23/` must answer all of it.

## A. Five questions per pick, in writing

| # | Question | Fail condition |
|---|---|---|
| 1 | **MECHANISM** — what friction or risk premium is being harvested, in one sentence? | "momentum screen fired" is not a mechanism |
| 2 | **COUNTERPARTY** — who is on the other side, and why do they keep losing? | cannot name the loser → you are the loser |
| 3 | **WHY THIS SYMBOL** — why XLE and not SPY, why DOT and not BTC? | "it came top of the scan" is a pass on the scanner, not on the instrument |
| 4 | **WHY NOW** — what is true today that was not true last month? | if nothing, this is a static screen and the "pick" is a basket, not a trade |
| 5 | **WHAT KILLS IT** — the frozen numeric threshold, with the measurement that produces it | "if it stops working" is not a kill rule |

## B. Symbol vetting (per instrument, before any ranking)

| Check | Requirement | Reason |
|---|---|---|
| **Observations** | `n ≥ 30` for any endorsement; `n = 0` is automatically **REJECT** | a pick with no observations is a preference, not evidence |
| **Cost vs edge** | claimed net edge must exceed the **measured** round trip for that instrument's class | if the net figure is smaller than the cost band, either cost was not applied or the sign convention is wrong |
| **Liquidity / tradability** | listed on an exchange we can reach, spread measured, no halts in the sample | nothing exotic with unmeasured spreads |
| **Direction sanity** | short leg must be borrowable at a fee we measured or explicitly assumed | the short leg is where unmeasured alpha hides |
| **Data integrity** | symbol has PIT-safe history, no ticker reuse, no survivorship filter | a reused ticker silently merges two firms |
| **Duplicate exposure** | two picks that are 0.9 correlated are one pick | count them once in the ranking |

## C. Cost bands we will hold you to (measured on our own bars unless stated)

| Class | Round trip | Source |
|---|---|---|
| ETF | **6.7122 bp** | measured, 1-min bar upper bound |
| Index proxy | 8.0325 bp | measured |
| Direct equity | 12.0749 bp | measured |
| Bond ETF (SHY) | 0.6144 bp | measured |
| Crypto | **20–52 bp** | measured band; carry −11 bp/tick on 63 ticks |
| FOREX | 7.533 bp | measured |
| COMMODITY | ~10 bp/side | assumed, **not** measured at size |

## D. Ranking requirement

Each agent ranks **its own endorsed picks per asset class**, and states the criterion:

- Default criterion: **risk-adjusted net return on committed capital, ranked on the 95% lower bound** — not the point
  estimate. A wide CI is mostly noise and would outrank a tight one only by luck.
- Tie-breaks must be named in advance (turnover at measured cost, margin over the 2× gate, deflated Sharpe at honest
  N_eff, capacity headroom).
- **Endorsed ≠ interesting.** A pick is endorsed only if it passes the gate sheet in
  `strategy_validation_protocol.md` v1.0 §3.11. Everything else goes in the table marked `CANDIDATE` with the missing
  measurement named, or `REJECT` with the number that killed it.

## E. What the operator will do with this

Every pick gets an entry in `VETTING_LEDGER.md` with a verdict — **ENDORSE / HOLD FOR EVIDENCE / REJECT** — and the
reason. An endorsement requires the mechanism, the counterparty, the symbol vetting, `n ≥ 30`, a measured cost, and a
frozen kill rule. Anything less is `HOLD FOR EVIDENCE`, and the missing item is named so it can be closed.

**A pick that cannot be vetted is not ranked lower — it is not ranked.**
