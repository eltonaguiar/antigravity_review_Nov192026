# CONTEST R01b — the multi-model panel wave, scored against live prices

**Generated from live prices. Nothing here comes from what a model reported about itself.**
Prices fetched 2026-11-23T10:20:42Z from Yahoo Finance (equities, ETFs, funds, FX, gold futures) and Binance (crypto).

## Headline

> **21 new picks across 6 sets: 3 inside their own bracket, 15 void at the fill, 3 mutual-fund NAV.**
>
> Cumulative across R01 and R01b: **69 picks, 18 inside, 41 void at fill, 10 fund NAV**.

The pick sets were **pasted into a multi-model chat surface by the operator and captured by CDP** —
read out of the page, not retyped by the referee. Each set is filed as its own entrant with its sha256 recorded
in `_panel_wave_2026-11-23b.json`.

## The SPY anchor test, now with six more models

SPY is the most liquid ETF in the world and needs no forecasting skill to quote. Live: **689.81**.

| entrant | SPY target | SPY stop | verdict |
|---|---|---|---|
| ChatGPT-6 Luna | 615 | 594 | **VOID** |
| Claude (Latest Model) | 562 | 540 | **VOID** |
| GLM 5.3 Flash | 655 | 549 | **VOID** |
| Muse Spark | 715 | 615 | **INSIDE** |
| Muse Spark 1.0 - Meta AI | 541 | 528 | **VOID** |

Five sets quoted SPY between **541 and 715** in the same week — a **174-point spread** on one instrument,
with the market at 689.81. Only one bracket straddles reality. This is not a forecasting failure;
it is a **price-recall failure**, and it is now reproduced across 18 entrants on two different surfaces.

## Per-set results

| entrant | symbol | side | tp | sl | live | verdict |
|---|---|---|---|---|---|---|
| ChatGPT-6 Luna | SPY | long | 615 | 594 | 689.8100 | **VOID** |
| ChatGPT-6 Luna | GLD | long | 310 | 296 | 322.8700 | **VOID** |
| Claude (Latest Model) | SPY | long | 562 | 540 | 689.8100 | **VOID** |
| Claude (Latest Model) | TLT | long | 93 | 88 | 81.4500 | **VOID** |
| GLM 5.3 Flash | SPY | long | 655 | 549 | 689.8100 | **VOID** |
| GLM 5.3 Flash | XAUUSD | long | 4000 | 2600 | 3621.4000 | **INSIDE** |
| GLM 5.3 Flash | BTCUSD | long | 1.24e+05 | 8.6e+04 | 61364.0000 | **VOID** |
| GLM 5.3 Flash | BRK.B | long | 508 | 405 | 570.0000 | **VOID** |
| GLM 5.3 Flash | VBIRX | long | — | — | — | **FUND-NAV** |
| Muse Spark | SPY | long | 715 | 615 | 689.8100 | **INSIDE** |
| Muse Spark | AAPL | long | 305 | 235 | 342.5600 | **VOID** |
| Muse Spark | EURUSD | long | 1.19 | 1.11 | 1.0973 | **VOID** |
| Muse Spark | VTSAX | long | — | — | — | **FUND-NAV** |
| Muse Spark 1.0 - Meta AI | NVDA | long | 138.5 | 131.5 | 125.5300 | **VOID** |
| Muse Spark 1.0 - Meta AI | SPY | long | 541 | 528 | 689.8100 | **VOID** |
| Muse Spark 1.0 - Meta AI | BTCUSD | long | 1.065e+05 | 1.018e+05 | 61364.0000 | **VOID** |
| Muse Spark 1.0 - Meta AI | EURUSD | long | 1.092 | 1.08 | 1.0973 | **VOID** |
| Muse Spark 1.0 - Meta AI | VTSAX | long | — | — | — | **FUND-NAV** |
| Muse Ember | EURUSD | long | 1.098 | 1.09 | 1.0973 | **INSIDE** |
| Muse Ember | USDJPY | short | 149 | 151.5 | 159.1340 | **VOID** |
| Muse Ember | IEF | long | 96.4 | 95.5 | 91.6500 | **VOID** |

## Two pathologies that currently score as "fine"

### (a) A bracket thinner than the round-trip cost

**Muse Ember · EURUSD long** — target sits **6.4 bp** from the live price against a **7.53 bp** round trip.

It is INSIDE its bracket and still **loses by construction**: a winning pick nets a loss. A pick that cannot
pay for its own execution is not a trade.

### (b) A bracket that cannot resolve

**GLM (pane "GLM 5.3 Flash") · XAUUSD long 4000 / 2600** against live 3621 — the bracket is **54% wide**,
R ≈ 0.37, and it is marked INSIDE. A bracket outside the instrument's 48–72 h range can neither win nor lose;
it books ≈0 R and hides among the real picks. Under a mean-R metric **zero silently beats a field that is
mostly negative** — the identical exploit as Claude 5.1 Fable's T-bill play. This is a scoring defect, not a
strategy, and R02 must close it by requiring the bracket to be reachable **and** to exceed round-trip cost by
a stated multiple.

## The one result that replicated

A low-cost index **mutual fund** can beat its own ETF net of fees:

| source | fund vs ETF, net CAGR | MaxDD | Sharpe | n |
|---|---|---|---|---|
| kilo | **11.66% vs 11.49%** | identical −24.5% | .728 vs .714 | 1254 daily returns |
| buffy (independent) | **11.67% vs 11.59%** (corr 0.998) | — | — | — |

Two implementations, two data paths, same conclusion. The durable mechanism is the **fee gap (~0.08pp/yr)**;
the residual tracking difference should be labelled *possibly noise*, not edge. First claim in this programme
to survive independent replication.

## Filed artefacts

| entrant | sha256 (first 12) | bytes |
|---|---|---|
| CP_PANEL_CHATGPT | `a5781e67417e` | 1360 |
| CP_PANEL_CLAUDE_HAIKU | `019bc0c6c4b7` | 1490 |
| CP_PANEL_CLAUDE_A | `bb60a5e1fead` | 2971 |
| MUSE_MUSE_SPARK | `d167ab9ffd6a` | 1911 |
| MUSE_MUSE_SPARK_1_0_META_AI | `24fdb7384c29` | 2226 |
| MUSE_MUSE_EMBER | `c19a6c6869c6` | 1602 |

## Standing position

**0 endorsed. No live orders, no credentials, paper only.** Every pick above is hypothetical and none is
investment advice. A pick marked INSIDE is inside its bracket, which is a *geometric* statement — it is not a
recommendation and not evidence of skill.
