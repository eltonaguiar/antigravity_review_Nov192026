# Unified pick-tracking DB + HARVEST analyst tracking — design

Goal: one database that tracks every pick across `findtorontoevents.ca/audit`,
`/audit2` (retired) and `/audit3`, the review site's pages, HARVEST analyst
signals, crowd markets and copy-trading sources — with provenance and as-of time.

## 1. Core tables (Postgres)

| Table | Purpose | Key fields |
|---|---|---|
| `instruments` | symbol master | `instrument_id`, `figi`, `isin`, `cusip`, `cik`, `symbol`, `asset_class`, `wrapper`, `exchange`, `currency`, `status` |
| `entities` | who made the call | `entity_id`, `entity_type` (analyst_firm, analyst_person, agent, model, trader, institution), `name`, `external_id`, `metadata` |
| `sources` | feed registry | `source_id`, `name`, `kind`, `license`, `status`, `last_success`, `next_retry`, `reason_code` |
| `recommendations` | one analyst/agent action | `rec_id`, `source_id`, `entity_id`, `instrument_id`, `action` (up/down/init/reiterate), `from_grade`, `to_grade`, `score`, `price_target`, `horizon`, `published_at`, `as_of`, `url`, `raw_hash` |
| `picks` | our own filed picks | `pick_id`, `surface` (audit1/audit2/audit3/harvest/contest), `agent`, `strategy`, `instrument_id`, `direction`, `entry_px`, `tp`, `sl`, `opened_at`, `closed_at`, `status`, `provenance` |
| `outcomes` | resolved result | `rec_id`/`pick_id`, `horizon_days`, `exit_px`, `ret_pct`, `excess_pct`, `benchmark_id`, `resolved_at`, `method`, `reason_code` |
| `prices` | bars | `instrument_id`, `ts`, `o,h,l,c,v`, `adj`, `source` |
| `consensus_snapshots` | HARVEST months | `instrument_id`, `period`, `sb,b,h,s,ss`, `n`, `score`, `buy_side`, `label`, `direction`, `delta_pp`, `n_prior`, `churn_flag`, `source_id` |
| `analyst_performance` | rolling track record | `entity_id`, `window_days`, `n_calls`, `hit_rate`, `mean_excess_pct`, `ci_low`, `ci_high`, `updated_at` |
| `crowd_markets` | prediction markets | `venue` (kalshi/polymarket), `market_id`, `question`, `close_time`, `mapped_instrument_id`, `mapping_confidence` |
| `crowd_snapshots` | crowd prices over time | `market_id`, `ts`, `implied_prob`, `volume`, `liquidity` |
| `trader_positions` | copy-trading / leaderboards | `platform`, `trader_id`, `instrument_id`, `side`, `size`, `entry_px`, `ts`, `is_public` |
| `ingest_runs` | ops | `source_id`, `started`, `finished`, `status`, `rows`, `http`, `error`, `reason_code` |

**Idempotency:** unique `(source_id, external_id, published_at)` on recommendations;
`(surface, pick_id)` on picks; `(instrument_id, period, source_id)` on consensus.
**Append-only:** recommendations, outcomes, crowd_snapshots, trader_positions.
**Views:** `v_all_picks` (audit1/3 + harvest + contest), `v_analyst_leaderboard`,
`v_crowd_vs_analyst` (analyst label vs implied probability for the same event).

## 2. HARVEST: can we track an analyst **by name**?

| Source | Names? | Asset classes | Cost / status |
|---|---|---|---|
| Yahoo `upgradeDowngradeHistory` | **firm-level only** | US/global equities | Free; sparse (52 buy-ish actions / 37 firms / max n=4 for 12 mega-caps over 540d) |
| Finnhub upgrade/downgrade | firm-level | equities | **403 on free**, paid |
| FMP upgrades-downgrades | firm-level | equities | **429** on free |
| Benzinga Analyst Ratings API | **analyst person + firm** | equities | paid |
| TipRanks | **analyst person + success rate** | equities | paid; scraping restricted |
| LSEG I/B/E/S, FactSet, Bloomberg ANR | **analyst person** | global equities | enterprise paid |
| MarketBeat / WallStreetZen | analyst person (site) | US equities | scraping; ToS risk |
| Estimize / SumZero / Seeking Alpha | named contributors | equities | paid/community; ToS |
| Credit ratings (S&P/Moody's/Fitch) | issuer, not analyst | bonds | agency data; paid |

**Conclusion:** a per-analyst *person* track record is a paid-data feature. Free
feeds give firm-level, sparse actions — enough for an attribution table, not for
ranking people. Do not display a person-level hit rate without a licensed source.

## 3. Crowd consensus sources

| Source | What | Access | Notes |
|---|---|---|---|
| **Polymarket** | event contracts, implied prob, volume, liquidity | public Gamma/CLOB API | crypto/macro/politics; few single-stock markets |
| **Kalshi** | regulated US event contracts (Fed, CPI, elections, index/crypto levels) | public trade API v2 (read) | KYC to trade; mapping to assets is manual |
| PredictIt / Manifold / Metaculus | event forecasts | public/limited | academic/play-money; not tradable size |
| CFTC COT | futures/FX/commodity positioning | free weekly | the best free "crowd" for non-equities |
| FINRA short interest, 13F, congressional/insider | positioning/disclosure | free, lagged | 13F 45-day lag; congressional ~45d; Form 4 ~2d |
| StockTwits / Reddit / AAII / NAAIM | retail sentiment | API/scrape, ToS | noisy; contrarian at extremes |
| Fund/ETF flows | crowd allocation | issuer/ICI/EPFR | EPFR paid |
| Options put/call, OI, funding/OI | derivatives crowd | CBOE/OPRA (paid), exchanges (free) | best for crypto perps |

**Rule:** crowd data is an *event-level overlay*, not a per-symbol price target.
Store `mapped_instrument_id` + `mapping_confidence`; never imply a stock forecast
from a macro contract without saying so.

## 4. Top-trader reverse engineering — feasible, with caveats

Public track records exist:
- **Hyperliquid** leaderboard/positions (public API) — perp positions, PnL.
- **Binance Futures leaderboard / copy trading**, **Bybit copy trading** — public
  trader lists and ROI; exact fills often hidden.
- **Darwinex DARWINs**, **Myfxbook/FX Blue**, **Collective2**, **eToro popular
  investors** — public verified histories (ToS-limited).
- **13F / congressional / insider** — institutional and political "smart money",
  but stale and incomplete.

Method: ingest positions/fills → reconstruct holding periods → compute
risk-adjusted returns and factor exposures → cluster into styles (momentum,
mean-reversion, carry) → test whether the style persists out-of-sample with CPCV
and DSR. **Caveats:** survivorship (losers delist), hidden hedges/leverage,
disclosure lag, copy-trading ToS, and the multiple-testing trap — a "pattern" found
across 500 traders is likely noise unless it clears DSR/PBO.

## 5. Phasing
1. **P0 (now):** consensus + audit picks ledger; reason codes; ingest runs.
2. **P1:** paid analyst actions (Benzinga/TipRanks) → `analyst_performance` by person.
3. **P2:** crowd market ingestion (Polymarket/Kalshi) + mapping table.
4. **P3:** top-trader ingestion (Hyperliquid/Darwinex) + style clustering, gated by CPCV/DSR.
