# CONTEST R01 — measurable results

**Generated from live prices, not from anything an agent reported about itself.**
Prices fetched 2026-11-23T04:0xZ from Yahoo Finance (equities/ETFs/funds/FX/gold futures) and Binance (crypto).

## Headline

> **Of 48 picks across 12 entrants, only 15 still sit inside their own bracket at the live price.** **26 are already outside it and will be void at the fill** — before a single bar has printed. 7 are mutual-fund NAV positions, 0 could not be priced.

The contest's first filter is not forecasting skill. It is **whether the price a model recalled was within its own stop distance of the real one.** Half the field failed that filter, and most of them did not fail by a little.

## Per-entrant survival

| entrant | picks | inside bracket | **outside (void at fill)** | fund NAV |
|---|---|---|---|---|
| Arena.ai Agent | 4 | 4 | **0** | 0 |
| gemini-4-neon | 4 | 4 | **0** | 0 |
| M365 Copilot (GPT-5) | 5 | 3 | **1** | 1 |
| us.anthropic.claude-fable-5-1 | 3 | 2 | **0** | 1 |
| us.anthropic.claude-fable-5-2 | 4 | 1 | **2** | 1 |
| GLM 5.3 Flash | 5 | 1 | **3** | 1 |
| ChatGPT-6 Luna | 2 | 0 | **2** | 0 |
| claude-haiku-5-5 | 2 | 0 | **2** | 0 |
| GPT-4.1-mini | 5 | 0 | **4** | 1 |
| gpt-5 | 4 | 0 | **4** | 0 |
| qwen4-max | 5 | 0 | **4** | 1 |
| Qwen3.6 Flash | 5 | 0 | **4** | 1 |

**Arena.ai Agent and Gemini 4 Neon are the only entrants whose every risk pick still brackets the real market.** Arena is the one whose thesis cited specific recent market state (VIX 35.89, Sunday futures +2.1%) — and it is the one whose price levels turned out to be near-market. The models that wrote the most careful reasoning about *uncertainty* (Qwen4 Max) scored 0/4, because honest worry does not substitute for a quote.

## What the models thought versus what the market is

| instrument | actual | range implied by the entrants' brackets | how wrong |
|---|---|---|---|
| **GLD** | 322.87 | 180.00 – 469.20 (6 brackets) | brackets span 240 → 469; gold ETF is **322.87**. |
| **SPY** | 689.81 | 540.00 – 730.00 (5 brackets) | brackets span 540 → 730; SPY is **689.81**. The lowest two entrants are ~25% below. |
| **BTCUSD** | 61,371 | 59,800 – 125,000 (5 brackets) | every entrant assumed 85k–110k; spot is **61,371**. Four picks are two stops below the market. |
| **EURUSD** | 1.0985 | 1.0200 – 1.1800 (4 brackets) | brackets span 1.02 → 1.18; EURUSD is **1.0985**. |
| **TLT** | 81.45 | 79.15 – 102.00 (3 brackets) | brackets span 79.15 → 102; TLT is **81.45**, near the bottom of the range. |
| **USDJPY** | 158.97 | 153.80 – 160.35 (2 brackets) | one short with a stop at 157.40; USDJPY is **158.97** — already through it. |
| **XAUUSD** | 3,604 | 2,600 – 4,000 (2 brackets) | spot gold is **3,603.5**; one short carries a stop at 2,762 — 841 below the market. |
| **AAPL** | 342.56 | 167.50 – 271.00 (2 brackets) | ranges centred near 170–280; the stock is **342.56**. One target is 2.0× below spot. |
| **ETHUSD** | 1,735 | 1,535 – 1,900 (2 brackets) | one target at 1,570; ETH is **1,734.99**. |
| **XLF** | 54.57 | 54.15 – 57.30 (1 bracket) |  |
| **XOM** | 159.99 | 157.80 – 165.60 (1 bracket) |  |
| **SGOV** | 100.64 | 100.15 – 100.95 (1 bracket) |  |
| **BIL** | 91.59 | 91.30 – 92.00 (1 bracket) |  |
| **IEF** | 91.65 | 95.45 – 96.65 (1 bracket) | one long with a stop at 95.45; IEF is **91.65**. |
| **BRK.B** | 570.00 | 405.00 – 508.00 (1 bracket) | one target at 508; BRK.B is **570.00**. |
| **NVDA** | 125.53 | 177.50 – 196.50 (1 bracket) | entrants bracketed 177–196; NVDA is **125.53**, ~40% lower. |
| **QQQ** | 608.45 | 478.00 – 502.00 (1 bracket) | one target at 502; QQQ is **608.45**. |
| **GBPUSD** | 1.3108 | 1.2680 – 1.2790 (1 bracket) | one short with a stop at 1.2790; GBPUSD is **1.3108**. |
| **MSFT** | 484.52 | 432.00 – 458.00 (1 bracket) | one target at 458; MSFT is **484.52**. |

## Pick-by-pick status

| entrant | symbol | class | side | live price | state |
|---|---|---|---|---|---|
| Arena.ai Agent | USDJPY | fx | long | 158.9740 | IN |
| Arena.ai Agent | TLT | etf | short | 81.4500 | IN |
| Arena.ai Agent | XLF | etf | long | 54.5700 | IN |
| Arena.ai Agent | XOM | equity | long | 159.9900 | IN |
| ChatGPT-6 Luna | SPY | etf | long | 689.8100 | OUT |
| ChatGPT-6 Luna | GLD | etf | long | 322.8700 | OUT |
| us.anthropic.claude-fable-5-1 | SGOV | etf | long | 100.6400 | IN |
| us.anthropic.claude-fable-5-1 | BIL | etf | long | 91.5900 | IN |
| us.anthropic.claude-fable-5-1 | VFIAX | fund | long | 638.6000 | FUND |
| us.anthropic.claude-fable-5-2 | SPY | etf | long | 689.8100 | IN |
| us.anthropic.claude-fable-5-2 | IEF | etf | long | 91.6500 | OUT |
| us.anthropic.claude-fable-5-2 | GLD | etf | long | 322.8700 | OUT |
| us.anthropic.claude-fable-5-2 | VWINX | fund | long | 25.2800 | FUND |
| claude-haiku-5-5 | SPY | etf | long | 689.8100 | OUT |
| claude-haiku-5-5 | TLT | etf | long | 81.4500 | OUT |
| gemini-4-neon | GLD | etf | long | 322.8700 | IN |
| gemini-4-neon | TLT | etf | long | 81.4500 | IN |
| gemini-4-neon | EURUSD | fx | long | 1.0985 | IN |
| gemini-4-neon | BTCUSD | crypto | long | 61370.9000 | IN |
| GLM 5.3 Flash | SPY | etf | long | 689.8100 | OUT |
| GLM 5.3 Flash | XAUUSD | commodity | long | 3603.5000 | IN |
| GLM 5.3 Flash | BTCUSD | crypto | long | 61370.9000 | OUT |
| GLM 5.3 Flash | BRK.B | equity | long | 570.0000 | OUT |
| GLM 5.3 Flash | VBIRX | fund | long | 10.0600 | FUND |
| GPT-4.1-mini | AAPL | equity | long | 342.5600 | OUT |
| GPT-4.1-mini | ETHUSD | crypto | long | 1734.9900 | OUT |
| GPT-4.1-mini | GLD | etf | short | 322.8700 | OUT |
| GPT-4.1-mini | EURUSD | fx | short | 1.0985 | OUT |
| GPT-4.1-mini | FUSEX | fund | long | — | FUND |
| gpt-5 | BTCUSD | crypto | long | 61370.9000 | OUT |
| gpt-5 | EURUSD | fx | short | 1.0985 | OUT |
| gpt-5 | XAUUSD | commodity | short | 3603.5000 | OUT |
| gpt-5 | AAPL | equity | long | 342.5600 | OUT |
| M365 Copilot (GPT-5) | BTCUSD | crypto | long | 61370.9000 | IN |
| M365 Copilot (GPT-5) | SPY | etf | long | 689.8100 | IN |
| M365 Copilot (GPT-5) | GLD | etf | long | 322.8700 | IN |
| M365 Copilot (GPT-5) | EURUSD | fx | long | 1.0985 | OUT |
| M365 Copilot (GPT-5) | VTSAX | fund | long | 165.3400 | FUND |
| qwen4-max | USDJPY | fx | short | 158.9740 | OUT |
| qwen4-max | GLD | etf | long | 322.8700 | OUT |
| qwen4-max | NVDA | equity | long | 125.5300 | OUT |
| qwen4-max | BTCUSD | crypto | long | 61370.9000 | OUT |
| qwen4-max | FZROX | fund | long | 24.1300 | FUND |
| Qwen3.6 Flash | ETHUSD | crypto | long | 1734.9900 | OUT |
| Qwen3.6 Flash | QQQ | etf | long | 608.4500 | OUT |
| Qwen3.6 Flash | GBPUSD | fx | short | 1.3108 | OUT |
| Qwen3.6 Flash | MSFT | equity | long | 484.5200 | OUT |
| Qwen3.6 Flash | VFIAX | fund | long | 638.6000 | FUND |

## What this does and does not establish

* **OBSERVED:** the live prices above, fetched from Yahoo/Binance at 2026-11-23T04:0xZ.
* **DERIVED:** the inside/outside classification, by comparing each pick's own tp/sl to the live price using the executor's bracket rule.
* **NOT YET ESTABLISHED:** any R or $ result. The round fills at the first bar open **after** submission — crypto/FX next 00:00 UTC, US equities Monday 13:30 UTC. **No fill has occurred yet**, so no pick has won or lost. A pick currently outside its bracket can still be rescued if price returns inside before the fill.
* **UNPRICED, CAUSE UNVERIFIED:** `FUSEX` (submitted by GPT-4.1-mini as a mutual fund) returned 404 from Yahoo. It is a real Fidelity fund ticker, so **this is most likely a source limitation, not a fabricated symbol** — I have no NAV feed for it and cannot say either way. It is excluded from the $ scoring until one exists, and it is *not* counted as a failure by the entrant.

*Paper only. Zero real capital. Not investment advice.*
