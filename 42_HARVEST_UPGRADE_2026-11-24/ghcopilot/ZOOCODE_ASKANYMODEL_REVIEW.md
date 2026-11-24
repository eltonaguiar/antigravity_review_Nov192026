# External review (AskAnyModel ×4 / zoocode) — independent verification

**Reviewed:** 2026-11-24 · **Source:** zoocode's critique of four model answers on
"which instruments suit which budget" · **Method:** every numeric claim checked against
this repo's own cost-of-record and against live API probes; arithmetic recomputed.

Scripts: `cost_of_hurdle.py` → `out/cost_of_hurdle.json`

---

## 1. What survives untouched

The qualitative frame is sound and I would keep it: funds/ETFs as compounding vehicles vs
penny stocks/options/meme coins/futures as trading-or-hedging vehicles; core–satellite
80–95 / 5–20; 1–2% risk per trade; exits defined before entry; futures sized on notional
not margin; correlation watched. Nothing to add.

## 2. Claim-by-claim verification

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1a | Costs are decisive and were omitted by all four models | **RIGHT** | this repo's cost-of-record table exists precisely because a thesis died on it: T-bill carry 5.89–6.09 bp vs a 6.71 bp ETF round trip = net −0.6 to −0.8 bp |
| 1b | "~40 bp and weekly turnover ≈ 2%/yr of drag" | **WRONG by 10.1×** | 40 bp × 50.4 turns/yr = **20.16%/yr**. 2.02%/yr is what **equity at the central 4.0124 bp** produces weekly. The 2% figure belongs to equity, not to the crypto band |
| 1c | equity round turn = 12.07 bp | **WRONG as stated** | 12.0749 is our **CEILING** (1-min bar range, 13 megacaps). Central = **4.0124 bp** (Roll+SEC, 190/191 names), floor = **0.9756 bp**. Ceiling/central = **3.01×**, ceiling/floor = **12.38×** |
| 2 | Stops fail where they warn: gaps and liquidity | **RIGHT, UNMEASURABLE for the classes that matter** | no penny-stock or meme-coin series exists in this repo. Liquid-instrument **floor** measured below |
| 3 | Options spreads are 5–20% of premium | **UNVERIFIED** | no options chain data in this repo; plausible but must not be printed as ours |
| 4 | Meme coins have no analyst coverage anywhere we probe | **VERIFIED** | Finnhub `/stock/recommendation`: DOGE, SHIB, PEPE, BONK, WIF, FLOKI all return `http=200 records=0`; controls AAPL/COIN/MSTR return 4 each. Our feed holds **0** meme coins (71 US large caps) |
| 5 | Futures hurdle is zero, not the cash rate | **RIGHT, and quantified** | margin earns cash; measured cash proxy SGOV CAGR **3.89%/yr** over the same window, so grading futures excess return against an equity total return demands **3.89pp too much** |

### The 12.07 bp misquote is a repo defect, not just a reviewer error

`README.md` "Cost of record — measured, not assumed" still lists **equity 12.0749 bp** as
the equity row. `37_BUFFY_DRAFT_PATCHES_2026-11-23/03_equity_cost_settlement.md` supersedes
that single-number reading and names the exact error the reviewer then made:

> *"12.0749 quoted as 'the cost' is an upper bound from 13 megacaps on 1-min bars. My own
> number."* — and, of the three estimators: *"stop quoting one number."*

So the reviewer quoted our own table faithfully. **The table is what is wrong.** Anyone
reading `README.md` alone will overstate equity cost 3× against the central estimate and
12× against the floor. Fix the README row to carry the bracket, or the same misquote will
recur with the next external reviewer.

### Gap risk — the floor we *can* measure

1255 daily bars, 2021-11-15 → 2026-11-13, close-to-close as a proxy for gap-through-stop
(a true test needs open prices, which the file does not carry):

| instrument | \|move\| > 5% | \|move\| > 10% | max move |
|---|---|---|---|
| SPY | 3 / 1254 = 0.24% | 1 / 1254 = 0.08% | 10.5% |
| VTI | 4 / 1254 = 0.32% | 1 / 1254 = 0.08% | 10.1% |
| FXAIX | 3 / 1254 = 0.24% | 0 / 1254 | 9.5% |
| BND | 0 / 1254 | 0 / 1254 | 2.1% |
| SGOV | 0 / 1254 | 0 / 1254 | 0.4% |

Even SPY jumped a 5% stop once in five years and exceeded 10% once. That is the **floor**
of gap risk on the most liquid instruments we hold — so the qualitative claim is
directionally confirmed, and penny/meme gap risk is strictly worse and still unmeasured.

## 3. The table they asked for — with the cost bracket done properly

Cost of record, annualised drag at the point estimate, and the column that actually decides
things: the **gross edge required just to net a 4.32% hurdle**.

| asset class | round trip (point) | drag @ 1 week | drag @ 1 month | gross needed @ 1 week | gross needed @ 1 month |
|---|---:|---:|---:|---:|---:|
| fund | 0.00 bp | 0.0% | 0.0% | 4.3% | 4.3% |
| bond ETF | 0.61 bp | 0.3% | 0.1% | 4.6% | 4.4% |
| equity | 4.01 bp *(bracket 0.98–12.07)* | 2.0% | 0.5% | 6.3% | 4.8% |
| ETF | 6.71 bp | 3.4% | 0.8% | 7.7% | 5.1% |
| FOREX | 7.53 bp | 3.8% | 0.9% | 8.1% | 5.2% |
| commodity | 20.00 bp | 10.1% | 2.4% | 14.4% | 6.7% |
| crypto | 36.00 bp *(band 20–52)* | 18.1% | 4.3% | 22.5% | 8.6% |

At **1-day** turnover the same table reads: crypto needs **95.0% gross/yr** to net 4.32%,
commodity 54.7%, FOREX 23.3%, ETF 21.2%, equity 14.4%, bond ETF 5.9%, fund 4.3%.

**That is the finding that matters more than any of the five corrections.** The reviewer
says "costs are decisive" and then illustrates it with a number 10× too small. The
correct framing is stronger than theirs: at the turnover implied by "scalping", the
required gross return exceeds anything this estate has ever measured, so the suggestion is
not merely expensive — it is arithmetically foreclosed. Note also the **inversion** at 1 day:
equity needs 14.4% gross but ETF needs 21.2%, purely because the ETF point cost (6.71 bp)
sits above the equity central estimate (4.01 bp). Any per-class guidance that assumes
"ETF is cheaper than stock" is wrong at the instrument level we actually trade.

## 4. Corrections to the reviewer's own list

1. **Do not quote a single equity cost.** Use the bracket and grade at the upper end; that
   is what our settlement doc already requires.
2. **Separate the 2%/yr from the 40 bp.** They are different classes. Stating them together
   makes the crypto case look 10× cheaper than it is.
3. **Both the options-spread and penny/meme gap claims belong on the "what we cannot
   measure yet" list**, not on the table. They are reasonable priors, not our measurements,
   and printing them beside measured columns borrows credibility the number has not earned.
4. **Futures cost is still unmeasured** — the reviewer notes this and is right. It should
   stay blank rather than be estimated.

## 5. For the proposed page

Their proposed page shape is good with one addition: the *"gross edge required to net the
hurdle"* column, because measured cost alone does not tell a reader whether a strategy is
viable — it tells them what to subtract. And the failure-mode column should distinguish
**measured** failure modes (gap-through-stop floor, 0.24% of SPY days) from **asserted**
ones (penny-stock gaps, meme-coin liquidity, options spread as % of premium).
