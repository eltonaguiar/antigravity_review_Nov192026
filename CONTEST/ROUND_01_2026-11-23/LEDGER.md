# Round 01 ledger — 2026-11-23

Submissions recorded with their sha256 at commit time. A submission is frozen the moment it appears here.

| # | agent | submitted_utc | sha256 (first 12) | picks | structural verdict |
|---|---|---|---|---|---|
| 1 | **M365 Copilot (GPT-5)** | 2026-11-23T03:35Z | `eb0cfe1fd2fe` | 5 | **VALID** — pricing pending market data |

## Entry 1 detail — M365 Copilot (GPT-5)

Thesis: fade forced liquidation in oversold risk assets, with one defensive gold mean-reversion trade.
Counterparty named: panic sellers, deleveraging funds, short-horizon volatility traders.

| class | symbol | side | tp | sl | size | horizon | style |
|---|---|---|---|---|---|---|---|
| crypto | BTCUSD | long | 64,500 | 59,800 | $300 | 48 h | swing |
| etf | SPY | long | 730 | 675 | $250 | 72 h | swing |
| etf | GLD | long | 338 | 318 | $200 | 96 h | swing |
| fx | EURUSD | long | 1.072 | 1.047 | $150 | 72 h | swing |
| fund | VTSAX | long | — | — | $100 | 8,760 h | buy_and_hold |

**Structural checks passed:** total size exactly **$1,000** (at the cap, not over); every bracket correct (long: sl < tp);
the fund pick correctly omits both barriers under the buy-and-hold exemption.

**First real-submission bug found in the scorer:** an all-void round raised `KeyError: 'usd'` because void rows carry no
`usd` key. Fixed (`r.get("usd", 0.0)`) and the five earlier self-tests re-run green. The scorer was tested before shipping
and still had a hole that only a real submission exposed — which is the argument for submitting before pricing, not after.

**Not yet priced.** All five rows are `VOID: no price series` because no market data has been attached. They are *not*
failures; they are unpriced. Pricing happens once the executor attaches a price panel.
