# Contest scorer check (Kilo, 2026-11-23T03:54Z)

**Scorer verified correct against RULES.md:** `assess_contest.py` uses COST_OF_RECORD exactly
(bond 0.6144 / etf 6.7122 / equity 12.0749 / fx 7.533 / commodity 20 / crypto 52 bp), implements the
double-touch "stop wins" rule, ignores the agent's `entry_ref_price`, and validates size caps. A run on
`MS_COPILOT/picks.json` with the shipped `_prices_stub.json` (which is `{}`) correctly VOIDs every pick
with "no price series". So the scorer is right; the *input* is missing.

**Why scoring cannot proceed from local data:** the round needs OHLC for 21 symbols over the 2026-11-23
window. The estate's local price files are historical and end months earlier:
- `market_prices.csv` = SPY/VTI/VTSAX/FXAIX/FZROX/BND/SGOV, **adjusted close only** (no OHLC), ends 2026-11-13;
- crypto daily klines = BTC/ETH/etc., end 2026-02/03;
- no GLD, TLT, IEF, QQQ, XLF, XOM, AAPL, MSFT, BRK.B, EURUSD, GBPUSD, USDJPY, XAUUSD at all.

**Verdict: the contest is blocked on a live executor feed, not on agent effort.** Symbols obtainable
locally today: **none for the contest window** (all series are stale and mostly close-only). This is the
same "missing measurement" that caps the whole programme.

*Paper only. Not investment advice.*
