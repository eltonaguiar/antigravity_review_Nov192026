# Free data sources per asset class (for the ejaguiar1_stocks implementer)

Rules: check licence + rate limit before ingesting; store `source`, `as_of`,
`raw_hash`. Yahoo endpoints are unofficial and can change; issuer/SEC/FRED/CFTC
are the most stable free sources. Redistribution is often prohibited even when
read access is free.

## Equities (stocks)
- **SEC EDGAR** companyfacts/submissions (free, US): fundamentals, filings, Form 4 insiders, 13F.
- **Stooq** EOD CSV (free, global stocks/indices); **Yahoo chart v8** (unofficial, delayed).
- **Alpha Vantage** free key (25 req/day); **Finnhub** free tier (60/min; some endpoints paid);
  **Tiingo** free tier; **Twelve Data** free (8/min); **Polygon.io** free (5/min, delayed).
- **OpenFIGI** for FIGI/ISIN/CUSIP mapping; **Nasdaq** public quote/analyst endpoints.
- Canada: Yahoo/Stooq + **Bank of Canada Valet** (FX); TMX delayed quotes.

## ETFs
- **Issuer pages** (iShares, Vanguard, SPDR, BMO, Horizons): holdings, NAV, ER, distributions (CSV/JSON where offered).
- **Yahoo/Stooq** prices; **ETF.com / JustETF** (scrape, ToS); **OpenFIGI** identifiers.
- Free substitute for “analyst rating”: ER, AUM, tracking difference, premium/discount, spread/ADV, flows.

## Mutual funds
- **SEC N-PORT / N-CSR** (free): holdings, fees; **issuer NAV history** (Vanguard/Fidelity/Fidelity funds).
- **Yahoo funds** NAV; **Morningstar** (scrape restricted); FINRA fund data (limited).

## Bonds & rates
- **US Treasury FiscalData API** (auctions, debt), **TreasuryDirect** rates; **FRED** (yields, spreads, TIPS).
- **Bank of Canada Valet** (CAD curves), **ECB SDW** (euro curves), **MSRB EMMA** (munis, public).
- **FINRA TRACE** (delayed/paid); credit ratings from agency pages/SEC filings (issuer-level, not analysts).

## Commodities
- **CFTC COT** weekly positioning (free); **EIA API** (energy inventories); **USDA NASS/AMS** (ags).
- **CME/ICE delayed settlements** (free pages), **World Bank Pink Sheet** monthly, **Stooq** futures.

## FX
- **ECB reference rates** (daily), **Bank of Canada Valet**, **FRED** FX series, **Frankfurter** API.
- **exchangerate.host** free tier; **OANDA practice** API; **Alpha Vantage** FX; broker APIs (IBKR/OANDA) with account.

## Crypto
- **CoinGecko** demo API (30/min, 10k/mo); **Binance/Bybit/OKX** public (klines, funding, OI).
- **Coinbase Exchange** public; **CryptoCompare** free tier; **DefiLlama** (TVL/yields); **Dune** free tier; **Etherscan** key.

## Meme coins
- **DexScreener API** (free), **GeckoTerminal**, **RugCheck** (Solana), **honeypot.is** (BSC).
- Label **NOT_RELIABLE** for ranking; require liquidity/rug checks and short windows.

## Futures
- **CME/ICE delayed** settlements, **CFTC COT**, Yahoo `=F` symbols, **Stooq**, Barchart (ToS).

## Options
- **CBOE delayed quotes**, **Yahoo options** (delayed), **Deribit** public (crypto options), Nasdaq option chain.

## Prediction markets / crowd
- **Polymarket** Gamma + CLOB API (public), **Kalshi** trade API v2 (public read), **Manifold** API, **Metaculus** API.
- **CFTC COT** (futures/FX/commodities), **FINRA short interest**, **13F**, congressional disclosures, **Form 4**.
- **alternative.me** Fear & Greed (crypto), CNN Fear & Greed (scrape), **NAAIM** weekly, **pytrends** (unofficial).

## Top-trader histories (reverse engineering)
- **Hyperliquid** public API (leaderboard/positions), **Binance Futures leaderboard / copy trading**, **Bybit copy trading**.
- **Darwinex DARWINs**, **Myfxbook/FX Blue**, **Collective2**, **eToro popular investors** (public pages, ToS).
- Caveats: hidden hedges/leverage, survivorship, disclosure lag, ToS; require CPCV/DSR before claiming a pattern.

## Stable “boring” core
- **FRED** (macro/rates/FX), **SEC EDGAR** (filings/fundamentals), **CFTC COT**, **EIA/USDA**,
  **Treasury FiscalData**, **issuer ETF pages**, **CoinGecko/Binance public**.
