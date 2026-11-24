# Analyst-pick harvesting + track-record rating plan

## 0. Principle
Win rate is neither skill nor profit. A record is a **vector**, judged on
`(firm, symbol, asset_class, horizon, direction, regime)`, with `n` shown next to
every number, benchmark-adjusted, and stress-tested for its worst plausible loss rate.

## 1. What can be harvested, per asset class
| Class | Analyst record source | Unit | Free? | Horizon |
|---|---|---|---|---|
| Equities | Yahoo upgrade history; Finnhub/FMP (firm); Benzinga/TipRanks/LSEG/FactSet/Bloomberg (person) | firm (free) / person (paid) | firm only | 1d–12m |
| ETFs | no sell-side; look-through consensus of holdings + fund flows | basket | yes (issuer) | 1m–12m |
| Mutual funds | no analyst names; manager tenure + NAV vs index | fund | yes | 1–10y |
| Bonds | credit-rating actions (Moody’s/S&P/Fitch); no “analyst pick” | issuer | agency pages | until rating change |
| Commodities/FX/Futures | bank research (not machine-readable free); use CFTC COT + trend | positioning | COT free | 1w–3m |
| Crypto | exchange leaderboards (Hyperliquid/Binance/Bybit), KOL posts, on-chain | trader/KOL | partly | hours–4w |
| Meme coins | social/KOL only; **NOT_RELIABLE** for ranking | KOL | no | hours–days |
| Prediction markets | market-implied probability per event | market | yes (Polymarket/Kalshi) | event |

**Person-level track record is paid** (Benzinga, TipRanks, LSEG I/B/E/S, FactSet,
Bloomberg ANR) and only for equities. Free feeds are firm-level and sparse
(Yahoo: 52 buy-ish actions / 37 firms / max n=4 over 540d for 12 mega-caps).
Never infer a person’s record from a firm’s.

## 2. Event schema (per call)
`event_id, source, entity_id (firm|person|trader), instrument_id, asset_class,
wrapper, direction, grade_from, grade_to, action (up/down/init/reiterate/close),
published_at, as_of, horizon, price_target, entry_px (next open after publish),
exit_px, benchmark_id, ret_pct, excess_pct, hold_days, status, reason_code`.

Gaps are **rows with a status** (`NOT_APPLICABLE`, `PLAN_LIMITED`, `SOURCE_ERROR`,
`NO_TRADES_IN_WINDOW`), never missing rows.

## 3. Metrics (all with CIs)
- `n_calls` (rank only when **n ≥ 30**; forward-proof at n ≥ 100)
- hit rate + **Wilson 95% CI**
- mean/median excess vs benchmark + bootstrap CI
- **expectancy** and **expectancy_worst**: recompute at the Wilson **upper bound
  on loss rate** (the worst loss rate the sample still allows)
- profit factor `sum(wins)/|sum(losses)|`; payoff ratio; max drawdown (1% risk/trade)
- average hold days (a “1-week” claim is checked against bars held)
- specificity z with **BH correction** across class × horizon × firm
- base-rate comparison: `P(up | class, horizon)`, not 50% (sell-side is bullish)

## 4. Rating tiers (vector, not one star)
- **A_SURVIVES_STRESS**: n ≥ 30, expectancy_worst > 0, excess CI-low > 0.
- **B_POSITIVE_BUT_TAIL_UNPROVEN**: expectancy > 0 but CI straddles 0 or worst ≤ 0.
- **C_NO_EDGE**: expectancy ≤ 0.
- **INSUFFICIENT_N**: n < 30 (or slice n < 20).
Score (0–100) = reliability 40 (Wilson LB) + magnitude 30 (CI-low of mean) +
profit-factor 15 + consistency 10 (both halves positive) + sample 5; **−15 if
expectancy_worst ≤ 0**. Specialist tag requires slice n ≥ 20, slice CI-low > 0,
and slice contribution dominating the overall record.

## 5. Worked examples (from `analyst_rating.py`)
| Profile | n | hit | Wilson LB | mean | worst-bound | PF | rating | score |
|---|---|---|---|---|---|---|---|---|
| A: BTC 1-week specialist | 41 | 97.6% | 0.874 | +0.341% | **−1.568%** | 1.78 | **WATCH** | 40.4 |
| B: generalist (49.4% WR) | 500 | 49.4% | 0.450 | +1.657% | **+1.230%** | 2.03 | **A_SURVIVES_STRESS** | 58.2 |

A’s 97.6% is a short-volatility profile: one average loss costs ~22 wins, and 41
trades cannot rule that tail out. B’s lower hit rate is more trustworthy because
its expectancy survives the worst plausible loss rate. This is why hit rate alone
must never rank an analyst.

## 6. Pattern registry
A pattern is `(entity, instrument|class, direction, horizon, regime, action type)`.
Track rolling n/hit/expectancy/drawdown, current streak, and persistence. Promote
a pattern only after: forward n ≥ 100, expectancy_worst > 0, excess CI-low > 0,
DSR ≥ 0.95 at the honest trial count, PBO < 0.5, and BH survives. Otherwise it
stays `WATCH` / `SPECIALIST_UNPROVEN`.

## 7. Harvest pipeline
1. Probe source; land raw JSON verbatim (`raw_hash`).
2. Normalise grades: Buy/Outperform/Overweight = +1, Hold = 0,
   Sell/Underperform = −1 (keep vendor string).
3. Emit `recommendation` rows with `published_at`.
4. Resolve outcomes: entry at **next open**, exit at 21/63/126 days or next action,
   split/benchmark adjusted.
5. Score per slice; BH-correct; write `analyst_performance`.
6. UI: filters (class, horizon, n, rating, recency), always show n and the CI;
   separate *Consensus*, *Dated actions*, *Track record*, *Crowd* tabs.

## 8. Guardrails
Trailing-window ranking, evaluate on the next window; next-open entry; keep
delisted symbols and dead firms; normalise per day/trade before comparing a
1-week BTC call with a 6-month bond call; don’t infer person-level from firm-level;
paid redistribution rules apply (Finnhub/FMP/Benzinga/TipRanks).

## 9. Phases
P0: consensus + dated firm actions (done). P1: paid person-level ledger.
P2: crowd markets (Polymarket/Kalshi) + mapping. P3: trader leaderboards +
style clustering, gated by CPCV/DSR/BH.
