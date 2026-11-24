# Final asset-class findings, tool breakdown & contest consensus

**2026-11-24 · PAPER ONLY · ZERO CAPITAL · NOT INVESTMENT ADVICE**

Published page: <https://eltonaguiar.github.io/antigravity_review_Nov192026/asset-class-ranking.html>

The answer is unchanged and unwelcome: **no asset class is proven, no ranking is statistically
distinguishable, and zero picks are endorsed.** This file is the consolidating record; the page is
the readable version.

---

## 1. Verdict per asset class

| Class | Verdict | Basis |
|---|---|---|
| **CRYPTO** | KILL | Intrabar truth WR 35.8%, PF 0.917, n=3,726. Daily-vs-intrabar inflation 0.29×. |
| **COMMODITY** | KILL | −2.9619 net expectancy/trade, n=50, CI [−5.004, −1.338] — excludes zero on the wrong side. |
| **EQUITY** | WEAK | +0.1058, n=956, CI [−0.480, +0.693]. Only class with positive selection alpha; kill verdicts are symbol-specific. |
| **ETF** | WEAK | −0.0062, n=590, CI [−0.437, +0.433]. OOS Sharpe +0.21 on 53 folds, but required n = 1.7M. |
| **FOREX** | WEAK | −0.0447, n=264, CI [−0.169, +0.078]. Independent 35-cell FX census: **0 of 35** cells pass CI + permutation at 5 bp. Carry break-even 16.4 days vs 1.9–2.3 observed. |
| **BOND** | WEAK | −0.0978, n=37, CI [−0.339, +0.169]. Re-tested: constant-5y duration vs T-bill, 777 months, +84 bp/yr excess at Sharpe **0.13**, CI [−75, +243]; **−91.58 bp** at real monthly rebalance cost. |
| **FUTURES** | INSUFFICIENT_N | n=4. Any verdict would be fabricated. |

**Recurring shape:** in every class the measured gross edge is roughly the size of the round trip.
That is the most reproducible result in the programme and the reason the answer keeps being "no"
rather than "not yet".

## 2. Breakdown by tool

| Tool | Endorsed | What it said |
|---|---|---|
| **GitHub Copilot** (DeepSeek V4.1 Flash) | 0 | Filed ranking criterion + honest headline instead of picks. Refused to build a results ledger for a tool it could not find, because the counts would have been invented. |
| **Kilo Code** (VSCode) | 0 of 69 pass | STOCKS / CRYPTO / BONDS / ETF / FOREX / COMMODITY DEAD; MUTUAL_FUND, OPTIONS, PREDICTION_MARKET UNKNOWN. Only defensible action named: low-cost index ETF. |
| **Zoo Code** (DeepSeek) | 0 of 14 investable | 14-row watchlist ranked by proximity to decidability, explicitly NOT INVESTABLE. Top row FX carry with Sharpe vs T-bill **−0.126**, break-even cost 468 bp. |
| **Hermes** (consolidated) | 0 | Adds the pre-registered in-repo tests: FX census 0/35; bond test KILL with sign flip at real cost; bracket identity (a bracket cannot create an edge); 1,000-cell sweep — every completed cell KILLED or BLOCKED. One cell: n=58, +50.51 bp net, permutation p=0.001, **DSR 0.0031** → KILL. |

All four tools independently declined to endorse a position. That unanimity on refusal is the
strongest result in the contest.

## 3. Contest consensus — 15 names

Ranked by distinct entrants choosing the same symbol **on the same side**. Opposite-side picks are
disagreement and are counted separately, never merged.

| # | Symbol | Side | Class | Same side | Any | Opposing |
|---|---|---|---:|---:|---:|---:|
| 1 | **SPY** | long | ETF | 10/18 | 10 | 0 |
| 2 | **BTCUSD** | long | Crypto | 7/18 | 7 | 0 |
| 3 | **GLD** | long | ETF | 6/18 | 7 | 1 |
| 4 | **EURUSD** | long | FX | 5/18 | 7 | 2 |
| 5 | **TLT** | long | ETF | 3/18 | 4 | 1 |
| 6 | **AAPL** | long | Equity | 3/18 | 3 | 0 |
| 7 | **VTSAX** | long | Fund | 3/18 | 3 | 0 |
| 8 | **IEF** | long | ETF | 2/18 | 2 | 0 |
| 9 | **VFIAX** | long | Fund | 2/18 | 2 | 0 |
| 10 | **ETHUSD** | long | Crypto | 2/18 | 2 | 0 |
| 11 | **NVDA** | long | Equity | 2/18 | 2 | 0 |
| 12 | **BRK.B** | long | Equity | 2/18 | 2 | 0 |
| 13 | **VBIRX** | long | Fund | 2/18 | 2 | 0 |
| 14 | **USDJPY** | short | FX | 2/18 | 3 | 1 |
| 15 | **XAUUSD** | long | Commodity | 2/18 | 3 | 1 |

Red flags called out on the page: #2 BTCUSD and #15 XAUUSD contradict our own class-level KILLs.

## 4. Why consensus is not an edge

1. **One bet, not fifteen.** 13 of 15 are long. SPY/VTSAX/VFIAX are the same underlying in three
   wrappers; IEF and TLT are the same duration trade at two lengths. As a book this is a single
   long-risk-asset factor, and a factor cannot diversify itself.
2. **Agreement between models trained on overlapping text is not independent evidence.**
   The contest's own bootstrap: best entrant wins **41.6%** of 2,000 replicates, far under the 95%
   needed for a distinguishable ranking at four picks per entrant.
3. **Our measurements contradict two of the top three.** CRYPTO and COMMODITY are class-level KILLs,
   yet BTCUSD-long is #2 and XAUUSD-long is on the list.

## 5. Performance tracking status

Forward scoring is wired to the repo's own executor, `CONTEST/tools/assess_contest.py`, which ignores
everything an agent reports about itself (entry = first bar open at/after round start; exit = first
touched barrier; on an ambiguous bar **the stop wins**).

| Item | Status | Detail |
|---|---|---|
| Round window | OPEN | R01 opened 2026-11-23 03:38 UTC; 48h horizons close ≈ 2026-11-25 03:38 UTC. |
| Price coverage | **4 / 24** | Only EURUSD, GBPUSD, USDJPY, XAUUSD have bars at/after round start. The other 20 (incl. SPY, BTCUSD) return `VOID: no bar at or after the round start`. |
| Scored picks | PENDING | A VOID means *no price*, not *no profit*. The two must never be reported as one number. |
| Per-class / per-tool returns | BLOCKED | Needs forward bars for the 20 missing symbols; otherwise the figure is a coverage artefact. |

**We are deliberately not printing a performance table.** With 4 of 24 symbols covered, any per-class
return would be computed almost entirely from FX and gold. It would look like measurement and be an
artefact.

## 6. What would change the answer

- **Forward bars for the 20 missing symbols** — unblocks all per-class and per-tool scoring.
- **More picks per entrant** — ~30 would make the ranking decidable, or prove it is not.
- **A cell surviving deflated Sharpe** — one already hit n=58, +50.51 bp, permutation p=0.001, and
  died at DSR 0.0031. With 528 trials behind us, a raw p-value is not evidence.
- **Cost reality** — the bond test flipped from +84 bp to −91.58 bp on that one change alone.

## Sources

- `28_MERCURY3_PER_CLASS_REVIEW_2026-11-22/*.md`
- `CONTEST/ROUND_01_2026-11-23/BOOTSTRAP_WINNER_CONSISTENCY.md`
- `34_FINAL_PICKS_2026-11-23/{GITHUB_COPILOT_DEEPSEEK,KILOCODE_VSCODE,ZOOCODE_DEEPSEEK}`
- `results/consensus_overlap.json` (this folder) — the machine-readable overlap computation
- `03-trading-strategies/results/bonds_duration_prereg.json` (findtorontoevents repo)
