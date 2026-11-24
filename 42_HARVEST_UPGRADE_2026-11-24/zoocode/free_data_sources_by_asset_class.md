# Free data sources per asset class (for the tracking DB)

For whoever wires the SQL. Each row says what the source actually gives you, so an
analyst rating is never faked for a class that has none. "Free" means no key or a
free tier, verified where marked ✓.

| Asset class | Analyst ratings? | Free source | What it gives | Notes |
|---|---|---|---|---|
| **Stocks (equity)** | Yes | Yahoo `quoteSummary` (✓ verified) | `upgradeDowngradeHistory` (firm, from/to grade, action, PT), `recommendationTrend`, `financialData` (mean PT, n analysts) | Firm only, never the analyst's name. Needs an A3 cookie + crumb. |
| | | Finnhub `/stock/recommendation` | monthly consensus counts | free tier; upgrade feed is 403 |
| | | SEC EDGAR (✓ free, no key) | filings, Form 4 insider trades, 13F holdings | `data.sec.gov`, User-Agent required |
| **ETFs** | No | Yahoo chart API (✓ 200) | prices, volume | no fundamentals for SPY/QQQ etc. |
| | | Issuer CSVs / EDGAR N-PORT | full holdings + weights | enables a **holdings-weighted** consensus, labelled DERIVED |
| **Mutual funds** | No | SEC N-PORT / N-CSR | holdings, expenses | the 403 on the analyst feed is a plan limit, not absence |
| **Bonds / bond ETFs** | No (credit ratings instead) | FRED (✓ free, no key) | Treasury yields `DGS10`, IG/HY spreads `BAMLC0A0CM`, `BAMLH0A0HYM2` | `fred.stlouisfed.org` CSV download needs no key |
| | | TreasuryDirect | auction results, yield curve | |
| | | FINRA TRACE | corporate bond trades | |
| **Commodities / futures** | No | CFTC Commitments of Traders (✓ free, weekly) | commercial vs speculative positioning | repo already has `tools/cftc_cot_fetcher.py` |
| | | EIA, exchange inventories | energy / metals stocks | |
| **Forex** | No (bank research is paid) | CFTC COT currency futures | positioning | |
| | | FRED rate series | rate differentials | |
| **Crypto / meme coins** | No | Exchange public APIs (Binance, Coinbase) | OHLCV, funding rates, open interest | free, rate limited |
| | | alternative.me | Fear & Greed index | |
| | | DexScreener / CoinGecko | liquidity, volume, holders for meme coins | |
| **Crowd / prediction markets** | N/A | Polymarket Gamma API (✓ 200) | question, outcomePrices, volume, liquidity, endDate | |
| | | Kalshi `api.elections.kalshi.com` (✓ 200) | ticker, yes/no bid/ask, volume, open interest, close_time | `api.kalshi.com` is the wrong host (000) |
| **Options** | N/A | Exchange option chains | IV, skew, open interest, put/call | |

## The rule that keeps these honest

Each class gets **its own signal type**, stored with a `metric_type` label
(`sellside_consensus`, `holdings_weighted`, `credit_spread`, `cot_positioning`,
`funding_rate`, `crowd_probability`). A page can then show "BOND: credit spread +
yield" without ever implying an analyst rated the bond. Mixing them under one
column called "rating" is the failure mode to avoid.

## What is *not* freely available

- **Individual analyst names** -- no free source names the person. Firm only.
- **Per-analyst track records** -- TipRanks/LSEG/FactSet sell this. Build your own
  at firm level from dated actions + forward returns instead.
- **Real-time institutional flows** -- dated 13F filings are quarterly and lag 45 days.
