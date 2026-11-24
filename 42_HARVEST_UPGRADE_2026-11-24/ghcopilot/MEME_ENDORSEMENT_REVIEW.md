# Meme coin "endorsements" — what the category page actually endorses

**Reviewed:** 2026-11-24 · **Source:** CoinGecko meme-token category, live API
(`/coins/markets?category=meme-token`, top 100 by cap) · **Script:** `meme_endorsement_review.py`
(on the pasted snapshot) · **Live outputs:** `out/meme_endorsement_live.json`,
`out/meme_breadth_live.json`

---

## 0. The premise has to be restated

There are **no sell-side endorsements** to review. Measured earlier: Finnhub's
`/stock/recommendation` returns 0 records for DOGE/SHIB/PEPE/BONK/WIF/FLOKI while AAPL/COIN/MSTR
return 4 each — and that endpoint is an *equity ratings* feed, so the zero means "not in that
database", not "no research exists". Crypto research (Messari, Kaiko, CoinMetrics) publishes no
per-token buy/hold consensus with a target.

So the only "endorsement" signals this page carries are **market-cap rank** (survivorship),
**price change** (momentum) and **24h volume** (executability). Of those, only volume is
decision-relevant, because it bounds the size you can get out of.

## 1. The pasted snapshot is stale — rebuilt on live data

| | your paste | live API (now) |
|---|---|---|
| sector total | $15.08B | **$18.65B** (top-100 sum; page says $19.5B) |
| top-3 | DOGE, SHIB, PEPE | DOGE, SHIB, **`M`** |
| top-3 share of listed cap | 80.3% | **67.4%** |
| top-10 share | 89.7% | **84.1%** |
| negative on 7d | 84/100 | **81/98** |
| median 7d | −6.19% | **−6.73%** |

`M` at **$1.78B** is the third-largest meme coin and does not appear in your paste at all. Any
review written against the pasted table would be reviewing a different market.

## 2. The decisive finding: the #3 meme coin cannot be traded at size

| # | coin | market cap | 24h volume | turnover | max position at 1% of volume |
|---|---|---|---:|---:|---:|
| 1 | DOGE | $8.67B | $506.0M | 5.83% | $5,060,202 |
| 2 | SHIB | $2.11B | $42.8M | 2.03% | $428,077 |
| **3** | **`M`** | **$1.78B** | **$1.6M** | **0.09%** | **$16,329** |
| 4 | PEPE | $1.43B | $332.2M | 23.16% | $3,321,991 |
| 5 | 币安人生 | $0.45B | $4.0M | 0.89% | $39,696 |

The third-largest holder of "meme sector beta" turns over **0.09% of its cap per day**. A
position larger than $16,329 at 1% participation is itself the market move. **For that asset the
20–52 bp cost band is not the binding constraint — the absence of a counterparty is.**

This is the single most important correction to any "allocate 5–20% to meme coins" advice: the
sector-cap-weighted portfolio is not constructible. You would be buying DOGE and PEPE and
skipping the third-largest name because it has no liquidity.

## 3. Turnover traps — cap rank and liquidity are nearly uncorrelated

22 of the top 100 trade under **0.10% of cap per day**. Largest caps that fail a $10k test:

| coin | market cap | 24h volume | turnover | max 1% position |
|---|---:|---:|---:|---:|
| COCO | $0.12B | $0.02M | 0.018% | $229 |
| YZY | $0.09B | ~$0 | 0.001% | $7 |
| APES | $0.07B | ~$0 | 0.000% | $0 |

Executability at 1% of daily volume:

- **$1,000** position → 71/100 coins
- **$10,000** → **57/100**
- **$50,000** → **21/100**

## 4. Momentum screens in this category surface artefacts

The largest 7-day gainer in the whole category is **SIF at +475,196.2%** — with **$0.00 volume**.
That is not a return; it is a redenomination or data artefact. A screen sorted by 7-day change
ranks it first.

Of the 17 coins positive on 7 days, several have zero tradeable volume:

| coin | 7d | market cap | 24h volume | turnover |
|---|---:|---:|---:|---:|
| SIF | +475,196.2% | $15.8M | $0.00M | 0.00% |
| PIPPIN | +71.0% | $19.2M | $3.67M | 19.14% |
| REKT | +25.0% | $33.1M | $1.08M | 3.27% |
| $CWIF | +19.1% | $12.1M | $0.00M | 0.01% |
| APEPE | +11.8% | $293.0M | $16.90M | 5.77% |

Only PIPPIN, REKT, APEPE and a few others are both moving and executable. **A 7-day momentum
rank is not an endorsement; in this category it is mostly a list of untradeable artifacts.**

## 5. Breadth — the "diversified satellite" is one trade

81 of 98 coins with valid data were negative on 7 days, median **−6.73%**; 82 of 91 negative on
24h. The category moves together. So the core–satellite framing ("5–20% in a couple of meme
names as a diversifier") does not buy diversification — it buys a levered version of one beta,
concentrated 67% in three coins, one of which cannot be exited.

## 6. Ticker collisions are real, not hypothetical

Live rows contain **DOGE twice** (#1 $8.67B, #12 $0.14M-adjacent wrapped variant), **SHIB twice**,
**DOG twice**, plus PEPE / PEPECOIN / PEP as distinct assets. This is concrete evidence for the
caveat I raised earlier: a bare-ticker probe returning zero cannot distinguish "this string is
not an equity" from "this asset has no coverage".

## 7. My own error, caught and corrected

My first live fetch omitted the `price_change_percentage=24h,7d` query parameter. The API then
returns those fields as null, and my code defaulted them to `0.0` — producing
**"negative on 24h: 0/100, negative on 7d: 0/100, median +0.00%"**, i.e. the exact opposite of
the truth (81/98 negative, median −6.73%). It is visible in the transcript as the run where
every 7d column reads `0.0%`. A null must never be defaulted into a value that is itself an
observation; the fixed script tracks `rows with NULL 7d change` and refuses the breadth section
unless it is zero.

## 8. Verdict

**There is no endorsement to review, and the page does not provide one.** What it provides is
survivorship (cap rank), correlation (breadth) and liquidity (volume) — and the three disagree
sharply. Ranked by the only field that decides whether a position can be closed:

- DOGE and PEPE pass at any retail size.
- SHIB passes at retail.
- **The #3 name does not pass at $50k.**
- **43 of the top 100 cannot absorb $10,000.**
- The top 7-day gainer is a zero-volume artefact.

Cap rank is the residue of past speculation, not an endorsement. If a class page must show a
meme table, the only defensible columns are **market cap, 24h volume, turnover %, and maximum
1%-participation position** — with any 7-day momentum column suppressed below a turnover floor,
or it will rank a +475,196% non-tradeable artefact first.
