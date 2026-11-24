# HARVEST universe — what we want to cover, and what each class can actually give

Goal: an extensive list of investable instruments per asset class, with the metric
that is *meaningful* for that class (analyst consensus is meaningful for single
stocks, not for ETFs or T-bills), and an explicit coverage status.

Status legend: **LIVE** = measured in this repo; **FREE-SOURCE** = public API/file
available; **PAID** = requires a licence; **NOT-MEANINGFUL** = the metric does not
exist for that instrument; **NOT-RELIABLE** = data/fill realism insufficient.

## 1. Single stocks (equities)
- **Large cap (US):** all S&P 500 names (e.g. AAPL, MSFT, NVDA, AMZN, GOOGL, META, BRK-B, JPM, XOM, JNJ, WMT, COST).
- **Mid/small cap:** S&P 400/600 samples (e.g. IWM constituents), Russell 2000 sample.
- **International DM/EM ADRs:** TSM, ASML, SAP, BABA, INFY, SHOP, TM.
- **Penny / OTC:** sub-$1 and OTC names (no stable list; liquidity and dilution dominate).
- Metrics: analyst consensus (**LIVE**, Finnhub), price targets (PAID), earnings estimates (PAID), insider Form 4 (**FREE-SOURCE**, SEC), 13F holdings (**FREE-SOURCE**, SEC), short interest (**FREE-SOURCE**, FINRA), options IV (**FREE-SOURCE**, CBOE delayed).
- Penny stocks: **NOT-RELIABLE** for ranking; show filings/liquidity, not “coverage”.

## 2. ETFs
- **Broad:** SPY, VOO, IVV, VTI, ITOT, VXUS, VEU, EFA, EEM, ACWI.
- **Sector:** XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB, XLRE, XLC.
- **Factor:** MTUM, QUAL, VLUE, SIZE, USMV, SPLV, RSP.
- **Bond:** TLT, IEF, SHY, BND, AGG, LQD, HYG, JNK, TIP, MUB, EMB.
- **Commodity:** GLD, IAU, SLV, USO, UNG, DBC, DBA, CPER.
- **Thematic/other:** SMH, SOXX, ARKK, ICLN, TAN, JETS, XBI, IBIT.
- Metrics: analyst consensus **NOT-MEANINGFUL**; use expense ratio (FREE), AUM, holdings (issuer), tracking difference, premium/discount, flows (issuer/ETF.com), liquidity (spread/ADV).
- Crowd: ETF flows are the closest thing to a crowd vote.

## 3. Mutual funds
- **Index:** FXAIX, VFIAX, VTSAX, FZROX, VOO-equivalent funds.
- **Active:** AGTHX, AIVSX, ANCFX, AWSHX, DODGX, VWELX, VWINX.
- **Target-date/balanced:** VFIFX, VFORX, TRBCX, FBALX.
- **Bond funds:** VBTLX, PTTRX, DODIX.
- Metrics: analyst consensus **PAID/403**; use expense ratio, 1/3/5/10y NAV returns, category, turnover, manager tenure (Yahoo/Morningstar), and index-vs-active comparison (LIVE page).
- Note: mutual funds price once daily; no intraday crowd metric.

## 4. Bonds and rates
- **Treasuries:** SHY, IEF, TLT, GOVT, TIPS (TIP), STRIPS.
- **Credit:** LQD (IG), HYG/JNK (HY), EMB (EM), MUB (muni), PFF (preferred).
- **Single bonds:** on-the-run USTs, agency MBS, corporate CUSIPs.
- Metrics: **NOT-MEANINGFUL** as “analyst consensus”; use yield, duration, spread, credit rating (S&P/Moody’s/Fitch), issuance, FRED yield curves.
- Crowd: CFTC futures positioning, fund flows.

## 5. Commodities
- **Energy:** WTI (CL), Brent (BZ), nat gas (NG), gasoline (RB).
- **Metals:** gold (GC/GLD), silver (SI/SLV), copper (HG/CPER), platinum (PL).
- **Agriculture:** corn (ZC), wheat (ZW), soybeans (ZS), coffee (KC), sugar (SB).
- Metrics: **NOT-MEANINGFUL**; use futures curve/roll yield, CFTC COT (weekly, FREE), inventories (EIA/USDA, FREE), seasonality, USD.

## 6. Foreign exchange
- **Majors:** EURUSD, USDJPY, GBPUSD, USDCHF, AUDUSD, USDCAD, NZDUSD.
- **Crosses/EM:** EURJPY, EURGBP, USDMXN, USDTRY, USDZAR.
- Metrics: **NOT-MEANINGFUL**; use rate differentials, central-bank calendar, CFTC COT, realized vol, retail positioning (IG/DailyFX, scraping risk).
- Note: this repo’s FX feed was dead after 2026-02-09 — fix data before any claim.

## 7. Crypto and meme coins
- **Majors:** BTC, ETH, SOL, XRP, BNB, DOGE, ADA, AVAX, LINK.
- **Alts/meme:** SHIB, PEPE, WIF, BONK, FLOKI, TRUMP, etc.
- Metrics: **NOT-MEANINGFUL** analyst consensus; use funding rates + open interest (Binance/Bybit public), DEX liquidity, on-chain flows (PAID: Glassnode/Nansen), token unlocks, social sentiment.
- Meme coins: **NOT-RELIABLE** for ranking; rug/honeypot/liquidity checks required.

## 8. Futures
- **Equity index:** ES, NQ, YM, RTY. **Rates:** ZT, ZF, ZN, ZB. **FX:** 6E, 6J, 6B. **Energy/metals/ags:** CL, NG, GC, SI, ZC, ZS.
- Metrics: **NOT-MEANINGFUL**; use term structure/roll yield, COT, open interest, contract specs.
- Note: no roll-adjusted series in this estate; cannot rank yet.

## 9. Options
- **Index/ETF:** SPX, SPY, QQQ options. **Single-stock:** AAPL, NVDA, TSLA.
- Metrics: **NOT-MEANINGFUL** consensus; use implied vol surface, skew, put/call, OI, gamma exposure (dealer positioning, PAID/estimated).
- Note: no options data layer here.

## 10. Prediction markets (crowd metrics)
- **Polymarket:** public Gamma API (`gamma-api.polymarket.com/markets`), implied probability + volume + liquidity.
- **Kalshi:** public trade API (`api.elections.kalshi.com/trade-api/v2/markets`), implied probability + volume.
- Map events to classes: rates/Fed (bonds), recession (equities), crypto prices (crypto), elections/geopolitics (macro).
- Caveat: event contracts are **not** asset forecasts; use as a crowd overlay, filter by liquidity/volume, never as a price target.

## 11. Real assets / other
- **REITs:** VNQ, SCHH, PLD, AMT, SPG. Metrics: NAV premium, cap rates, occupancy, AFFO.
- **Private credit / private equity:** interval funds/BDCs (e.g. ARCC, BXSL). Metrics: NAV, distribution yield, leverage; **PAID/illiquid**.

## 12. Analyst track record (the missing layer)
Free dated firm-by-firm actions are largely paywalled:
- Finnhub `/stock/upgrade-downgrade` → **403** on this plan.
- FMP upgrades-downgrades → **429** on this plan.
- Yahoo `upgradeDowngradeHistory` → **FREE** and dated (used in this repo for 12 stocks).

DIY track record (feasible now):
1. Collect dated actions per firm/symbol from Yahoo.
2. Join to forward returns (Yahoo chart) at +30/+90/+180 days, minus SPY.
3. Aggregate per firm with n≥20: hit rate, mean excess, CI.
4. Caveats: no exact publication timestamp, no position sizing, survivor/selection bias.
Paid alternatives: TipRanks, Zacks, Estimize, Visible Alpha.

## Coverage status summary
| Class | Analyst consensus | Crowd metric | Best free substitute | Status |
|---|---|---|---|---|
| Stocks | YES (71 live) | 13F/short interest | price targets (paid) | LIVE |
| ETFs | NO | fund flows | ER/AUM/holdings/spread | substitute |
| Mutual funds | 403 | none | ER + NAV returns | LIVE comparison page |
| Bonds | NO | COT/flows | yield/duration/spread/rating | substitute |
| Commodities | NO | CFTC COT | curve/inventories | substitute |
| FX | NO | CFTC COT | rate differentials | data blocked |
| Crypto | NO | funding/OI | on-chain (paid) | substitute |
| Meme coins | NO | social | liquidity/rug checks | NOT-RELIABLE |
| Futures | NO | COT | term structure | data blocked |
| Options | NO | put/call/OI | IV surface | data blocked |
| Prediction markets | n/a | Polymarket/Kalshi | implied probability | FREE-SOURCE |
