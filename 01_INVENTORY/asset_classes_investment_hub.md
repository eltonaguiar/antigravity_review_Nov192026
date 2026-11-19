# Inventory — Investment Hub asset classes

The main site's Investment Hub advertises: *Stocks · Mutual Funds · Crypto · Forex ·
Goldmines · Multi-Asset ML · Graveyard*. Each maps to a family of scanners/strategies and a
set of class-scoped dashboards. The audit3 ledger registers seven class footprints
(CRYPTO, EQUITY, ETF, FOREX, COMMODITY, BOND, FUTURES) plus MEME, PENNY_STOCK,
MUTUAL_FUND in the slippage table.

| Hub category | Code footprint | audit3 status (measured) |
|---|---|---|
| **Stocks / EQUITY** | `alpha_engine`, `STOCKS/`, `STOCKSUNIFY/`, daily/weekly gainer reverse-engineering | EQUITY cells: high WR but PF < 1 (WR 59–60%, PF 0.94); breakout family ≈ 364 trades net +0.46%/trade, individual CIs straddle 0 |
| **Mutual Funds / MUTUAL_FUND** | `FUNDS_ETF_REPOS`, `funds.html` | Class registered (0.08% slippage); thin/no tested cells |
| **Crypto / CRYPTO** | `alpha_engine`, `paper_trading`, `crypto_*` | Class-aggregate CRYPTO KILL (n=1,851, net −0.51%); every major LONG symbol (BTC/ETH/SOL/BNB/BCH) killed; the only CANDIDATE is a SHORT |
| **Forex / FOREX** | FX scanners | Class registered (0.02% slippage); no positive cells |
| **Goldmines** | (mining stocks) | no live class in ledger; explored via equity scanner |
| **Multi-Asset ML** | `ml_consensus`, `ml_gatekeeper`, `quant_lab` | gatekeeper/consensus wrappers exist; the strict ledger sees no ML edge |
| **Graveyard** | `STRATEGY_GRAVEYARD.md`, `verified_strategies/` | 11 KILL strategies, 11 kill symbols, 2 kill classes |

Also present and reviewed: hydrotrader, polymarket/kalshi/prediction-market agents
(`prediction_market_agents/`), and reverse-engineered gainers. Notes:

- **Polymarket/Kalshi / prediction markets** — there is no `PREDICTION` class in the
  ledger. Rows are tagged CRYPTO (32 rows) and poison the CRYPTO cells. Per prior review,
  run these only as **maker** at ≥ 85¢ with Brier tracking, or purely as a probability
  oracle.
- **Hydrotrader** — `hyro_pick_performance.json` (2026-11-08) is stale (~157 h at last
  check); `hyrotrader_picks.json` has no timestamp field.
- **Diverse asset coverage exists; the problem is not breadth — it is that none of it has
  been promoted past the tribunal.**
