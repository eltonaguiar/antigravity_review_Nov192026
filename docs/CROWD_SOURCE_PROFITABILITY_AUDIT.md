# Crowd and news pick sources — measured profitability

**Status:** 2026-11-24. Educational, not advice. Two new tests: a Polymarket crowd-favorite
backtest and a post-publication audit of a meme-coin "analyst picks" listicle. Both are
pre-registered in code before fetching.

## 1. Polymarket: does the crowd favorite win?

**Rule (frozen in `poly_crowd_backtest.py`):** closed binary markets, volume ≥ $1M, end date
2024-01-01..now; take the last daily price at or before **T−7 days** (no older than T−30);
buy the side priced ≥ 0.50; hold to resolution; return `(payoff − entry) / entry`; no fee.
Falsifier: mean ≤ 0 with a 95% CI excluding 0 → no edge.

**Result (n=50 usable of 195 fetched; 145 skipped for no T−7 price point):**

| metric | value |
|---|---:|
| mean net return per market | **−15.96%** |
| median | +4.91% |
| 95% bootstrap CI | **[−31.78%, −0.87%]** |
| win rate | **70.0%** |
| one-sided sign test (mean > 0) | p = 0.998 |

**Why 70% winners still lose:** the favorite is bought near 0.94 in the largest bucket. A win
pays ~+6%, a loss costs −100%; at 80% realised wins that is ≈ −15% per trade.

**Calibration (favorite price bucket → realised win rate):**

| bucket | n | mean predicted | realised |
|---|---:|---:|---:|
| 0.5–0.6 | 7 | 0.560 | 0.429 |
| 0.6–0.7 | 4 | 0.650 | 0.750 |
| 0.7–0.8 | 6 | 0.786 | 0.500 |
| 0.8–0.9 | 8 | 0.861 | 0.750 |
| 0.9–1.0 | 25 | 0.944 | **0.800** |

The high-confidence bucket is overpriced by ~14 pp. The low bucket is also overpriced, but n is
too small to rank buckets. **Verdict: no crowd-favorite edge; negative skew, not a coin flip.**

Caveats: top-volume selection; markets with no T−7 price are excluded; resolution of sports
O/U markets can be ambiguous; no fee but gas ignored; overlapping markets (same event) are
treated as independent.

## 2. bmic.ai "Analyst Picks" listicle

**Source:** https://bmic.ai/listicles/analyst-pick-meme-coin-2026/ — page says *Updated
2026-08-29*; "BMIC Research Desk"; no named author. It names DOGE, SHIB, PEPE, BONK, FLOKI,
then promotes **BMIC**, the publisher's own presale token.

**Rule (frozen):** enter at the first daily close on/after 2026-08-30; hold to the latest
close; 20 bp round trip; benchmark BTC.

| asset | 7d | 30d | to date | max DD | excess vs BTC |
|---|---:|---:|---:|---:|---:|
| DOGE | +10.81% | +14.43% | **−32.57%** | −45.85% | −9.84 pp |
| SHIB | +11.49% | +16.13% | **−27.82%** | −41.41% | −5.09 pp |
| PEPE | +7.35% | +25.29% | **+0.59%** | −36.80% | +23.32 pp |
| BONK | +22.22% | +30.47% | **−22.94%** | −48.21% | −0.21 pp |
| FLOKI | +10.25% | +14.60% | **−31.91%** | −47.13% | −9.18 pp |
| BTC (benchmark) | +3.42% | +7.70% | −22.73% | −31.94% | — |
| BMIC (presale) | — | — | **unmeasurable** | — | — |

Mean to-date across the five measurable picks: **−22.93%**; median −27.82%; mean excess vs
BTC **−0.20 pp**. Four of five fell more than BTC; PEPE is the only positive absolute return.
The 7d/30d columns were mostly positive — the call looked good for a month, then gave it back.

**Source-quality rubric (0–2 each, total /10):**

| dimension | score | reason |
|---|---:|---|
| transparency | 2/2 | desk name + update date, though no author |
| specificity | 1/2 | tickers only; no entry, horizon, target, sizing |
| independence | **0/2** | ends by promoting the publisher's own BMIC presale |
| verifiability | 1/2 | no archived dated call; only the page's "Updated" date |
| measurable track record | **0/2** | no prior calls or outcomes |
| **total** | **4/10** | advertorial, not a track record |

## 3. Yahoo Finance / CryptoQuant context piece

**Source:** https://finance.yahoo.com/markets/crypto/articles/meme-coin-dominance-hits-record-092635858.html
— *Meme Coin Dominance Hits a Record Low* (2026-11-24). No picks. Attributable data:
meme share of altcoin market ~11% (Nov 2024) → **below 3%** now; Binance meme selling exceeds
buying by about **$1.5B**; Solana meme caps roughly halved since late August; only **1 in 5**
Binance alts above the 200-day; **367 hacks** logged in 2026; US spot DOGE ETFs with no new
inflows since late September.

This is **context, not a pick source**: high transparency and attribution, zero actionable
calls, so it cannot be scored on realised returns.

## 3b. openPR press release — “7 Best Meme Coins to Buy” (2026-11-23)

**Source:** https://www.openpr.com/news/4697189/from-market-favourites-to-new-contenders-7-best-meme-coins-to-buy
— paid release distributed by “Crypto Presale PR”; published **2026-11-23 11:52 +01:00**. Picks:
DOGE, SHIB, PEPE, BONK, WIF, FLOKI, plus **Apeing ($APEING) Stage-13 presale** at $0.00095.

**Rule (frozen):** entry at the close of the first full 1h Binance bar after publication; latest
close; 20 bp round trip; BTC same window. This is a **~32-hour** window, so it cannot rank the
source; it can only catch immediate damage.

| asset | return since publication | excess vs BTC | quoted Nov-19 vs actual close |
|---|---:|---:|---:|
| DOGE | −0.56% | +1.86 pp | +1.24% |
| SHIB | −1.11% | +1.31 pp | +0.16% |
| PEPE | −1.45% | +0.97 pp | +0.92% |
| BONK | −0.93% | +1.50 pp | +2.16% |
| WIF | −1.22% | +1.20 pp | +1.50% |
| FLOKI | −1.51% | +0.91 pp | +2.01% |
| BTC | −2.42% | — | — |
| APEING | **unmeasurable** (presale, no market price) | — | — |

All six measurable picks fell in absolute terms over 32h, but all beat a falling BTC by 0.9–1.9 pp.
That is not a win; it is beta with a short window. The quoted Nov-19 prices are 0.2–2.2% above
the actual daily close — consistent with intraday quoting, not fabricated, but not entry prices.

**Source quality:** transparency 1/2 (paid release, no author), specificity 2/2 (named assets,
dated prices, targets), independence **0/2** (promotes Apeing and is distributed by a presale PR
service), verifiability 2/2 (timestamped and price-checkable), track record **0/2** → **5/10**.

## 4. Source ranking (quality vs measured edge)

| source | type | quality | measured edge |
|---|---|---:|---|
| Yahoo/CryptoQuant | news/context | high (named data, dates) | none claimed; not testable |
| Polymarket crowd | market-implied | high (prices, resolutions) | **−15.96%/market, CI < 0** |
| HARVEST analyst consensus | monthly sell-side | medium (71 names, provenance) | 21d BUY +0.589% q=0.135; nothing q<0.05 |
| bmic.ai listicle | sponsored listicle | **4/10** | −22.9% mean to date; 4/5 below BTC |
| openPR / Apeing release | paid press release | **5/10** | −0.6% to −1.5% in 32h; all beat BTC; too short |
| Copy-trading leaderboards | self-reported | low (survivorship) | not measured; no PIT data |

**Rule for future sources:** do not rank a source by how confident it sounds. Require a dated
claim, a named entry price, a horizon, a disclosed conflict, and enough closed calls to compute
a post-cost return. The listicle fails four of five; the Polymarket crowd passes the data test
and still loses.

## Provenance

- `42_HARVEST_UPGRADE_2026-11-24/kilo/poly_crowd_backtest.py` → `poly_crowd_backtest.json`
- `42_HARVEST_UPGRADE_2026-11-24/kilo/news_source_pick_audit.py` → `news_source_pick_audit.json`
- Polymarket Gamma/CLOB APIs, fetched 2026-11-24; Binance daily klines, fetched 2026-11-24.
- HARVEST numbers: `docs/data/harvest_backtest.json`; costs: `README.md`.
