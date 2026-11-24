# READ THIS FIRST — the analyst-upgrade test, in plain language, with a maintenance guide

Companion to `PREREG_ANALYST_UPGRADE_TEST.md`. That file is the locked spec. This file explains
*why* the spec looks the way it does, in ELI5 terms, and documents every artifact so someone else
can maintain or extend this without re-deriving it.

---

## 1. THE QUESTION, IN ONE SENTENCE

When a bank's analyst says "we like this stock more than we did yesterday," does the stock actually
go up over the next month — **more than the market, more than similar stocks, and after trading
costs?**

If yes, the upgrade is information. If no, the upgrade is either already priced in, or just noise
dressed up in a suit.

## 2. WHY THIS IS HARDER THAN IT SOUNDS — SIX TRAPS, EACH IN ELI5

**Trap 1 — Buying at a price that never existed.**
The feed gives you a *date*, not a time. If you say "buy at the closing price on the day of the
upgrade," you have quietly assumed you knew about the upgrade before the close — while the market
was moving on it. You could not have. This is called **lookahead bias**, and it is the single most
common way a backtest invents money. Our rule: **buy at the next day's open.** You give up the
first-day jump on purpose. The question is whether an outsider could profit, not whether the bank's
own clients could.

**Trap 2 — Crediting the analyst for momentum that was already there.**
Analysts upgrade stocks that have already been rising. If a stock ran up 8% and then drifts up
another 1%, a lazy test says "the upgrade worked!" — but the drift was the stock's own momentum
continuing. Two of the six models spotted this independently. Our fix: **measure how much the stock
moved in the 20 days before the upgrade, and subtract that effect.** What's left is the only part
the analyst could have caused.

**Trap 3 — Comparing to the wrong thing.**
"The stock went up 3%" means nothing if the whole market went up 4%. So compare to the market — but
even that is not enough. Banks cover particular kinds of stocks: big ones, or tech ones, or cheap
ones. If a bank only covers high-beta tech, its upgrades will look great in a bull market for
reasons that have nothing to do with the analyst. Our fix: compare each upgraded stock against a
**bundle of look-alike stocks** — same size, same industry, same valuation, same recent momentum.
That bundle is the "characteristic-matched benchmark." Every one of the six models insisted on this,
and none of them used a plain index.

**Trap 4 — Forgetting that trading costs money.**
A 0.5% edge that costs 0.6% to capture is a 0.1% loss. Costs come from the gap between buy and sell
prices (the "spread") and from your own order moving the price ("impact"). Big liquid stocks cost
maybe 0.1%; tiny ones can cost 0.75% or more. Our fix: **charge each event its own cost by
liquidity bucket**, not one flat number — because we already measured that a flat constant
overcharged bonds by 42× and undercharged crypto by 2× in our existing marks. Repeating that mistake
with a different constant is not a fix.

**Trap 5 — Mistaking small samples for evidence.**
Four coin flips landing 3 heads is not proof the coin is biased. With noisy daily stock data you
need a *lot* of events before a small edge is distinguishable from luck. That is why the spec
demands **750 events per broker** — and why §0 of the prereg matters so much (see §4 below).

**Trap 6 — Testing 40 brokers and reporting the winner.**
If you test 40 brokers at the 5% significance level, about 2 will look like geniuses by pure chance.
This is **multiple testing**. Our fix: cluster the standard errors properly, and require the winner
to beat a **placebo** — fake upgrade dates drawn from the same stock's own history. If the best
"broker" cannot beat its own placebo, it is not a broker effect, it is the stock's ordinary
behaviour.

## 3. WHAT "THE ONE FALSIFIER" MEANS

Not "what would confirm my idea" — the opposite. It is **the single measurement that, if it comes
out this way, kills the whole claim and we stop.** Ours: for each real upgrade, invent 1,000 fake
upgrade dates for the *same stock*, run the identical machinery, and see what those fakes produce.
If the real upgrades do not beat the 95th percentile of the fakes, the answer is **dead** — the
analyst knew nothing the stock wasn't already doing.

The reason this is the strictest instrument available: the fakes automatically inherit the stock's
momentum, seasonality, volatility and industry behaviour, because they are the same stock. So every
"maybe it's just X" objection is already inside the comparison.

---

## 4. THE ONE FINDING THAT CHANGES THE PLAN

Before writing any of this, I measured whether the data can even supply 750 events per broker.
Thirty large-cap tickers, via Yahoo's undocumented `upgradeDowngradeHistory`:

- **30 of 30** tickers answered. **175 distinct firms. 19,880 actions. 5,220 actual changes.**
- **Zero firms reached 300 changes.** The best was RBC Capital at 234.

**So the limit is how many tickers we look at, not how many years we cover.** Each firm generates
roughly 7–8 changes per ticker it covers. That means:

| Events needed | Tickers needed (top firms) |
|---|---|
| 300 | ~39 |
| 500 | ~55 |
| **750** | **~96** |

And a second consequence that inverts the obvious choice: on the same 30 names, **Goldman Sachs
produced 115 changes and Morgan Stanley 164, while RBC Capital produced 234 and Needham 211**. The
famous names most models nominated are the *least* productive in event count. Naming only Goldman,
Morgan Stanley and JPMorgan tests the hardest case twice and never tests the likeliest case.

---

## 5. EVERY ARTIFACT, AND HOW TO MAINTAIN IT

### `tracker/yahoo_ratings.py` — the data extractor
**What it does:** pulls one ticker's full analyst rating history from Yahoo's `quoteSummary`
`upgradeDowngradeHistory` module using a cookie+crumb handshake. No API key, no account.
**Run:** `python yahoo_ratings.py AAPL MSFT NVDA --out ratings.json`
**Output fields:** `epochGradeDate, firm, fromGrade, toGrade, action, priceTargetAction,
currentPriceTarget, priorPriceTarget`.
**Maintenance notes:**
- This is **unofficial and undocumented**. It can break without notice. If it starts returning
  empty results, check the cookie/crumb handshake first — that is the usual failure, not the data.
- Grade strings are **free text**. Any ordinal mapping is ours, not the provider's. Do not assume
  "Outperform" and "Overweight" are interchangeable across firms without recording the mapping.
- `action=main` means *reiterated*, not changed. Filter on `up`/`down`/`init`/`reit` for real moves.
- The firm universe is whoever chose to cover that ticker. It is not a census of the industry.

### `tracker/PREREG_ANALYST_UPGRADE_TEST.md` — the locked spec
**What it is:** the frozen design, written *before* any return is computed. Nine models across two
surfaces contributed; consensus is labelled as consensus, splits carry a stated reason, and two of
their arithmetic claims are corrected in-file.
**How to change it honestly:** you may add a clause only *before* running on real data. Once a run
exists, changes go in a new versioned file with the old one kept — otherwise the prereg stops being
a prereg and becomes a description of whatever you found.

### This file — the plain-language guide
Written so the reasons survive the people. If you change a rule in the prereg, change the matching
paragraph here in the same commit, or the two will drift and the explanation will start lying.

### What is NOT built yet
The backtest itself. There is no `run_upgrade_test.py`, because running it on 30 tickers would
produce a verdict about 30 large caps, not about brokers — the one thing §4 rules out.

---

## 6. WHAT I WOULD SAVE TO A FILE (and what is already saved)

**Already committed and on `origin/main`:**
| File | Why it matters |
|---|---|
| `tracker/yahoo_ratings.py` | the only working keyless source for firm-level analyst history; would take a day to rediscover |
| `tracker/PREREG_ANALYST_UPGRADE_TEST.md` | 9-model consensus + 2 arithmetic corrections + the feasibility measurement |
| `tracker/README_ANALYST_UPGRADE_TEST.md` | this file — the reasoning, in language a maintainer can act on |

**Worth saving next, in this order:**
1. **The ticker-breadth run.** ~100 tickers per broker, appended to a single CSV with
   `symbol, firm, date, from, to, action`. ~30 minutes of requests. Everything else is blocked on it.
2. **The firm-alias table.** `GS` vs `Goldman Sachs Group` vs `Goldman, Sachs & Co.`; `B of A` vs
   `Merrill Lynch`; the RBC spellings. Without it the counts in §4 are contaminated and merger-era
   history is silently spliced. Claude Opus flagged this and it is the least glamorous, most
   load-bearing piece of work here.
3. **The grade-ordinal map, per firm, frozen.** One row per (firm, label, ordinal). Every model said
   freeze it first; none of them produced it. It is a day of reading rating-scale pages.
4. **The placebo harness.** Draw 1,000 pseudo-dates per event, identical benchmark and cost, build
   the null distribution. This is the falsifier; without it the test cannot fail, which means it
   cannot succeed either.

**Not worth saving:** the model answers themselves. They are quoted inline where they changed a
decision, which is where they belong. Six opinions in a file add maintenance cost and no evidence.

---

## 7. GLOSSARY

| Term | ELI5 |
|---|---|
| **Lookahead bias** | using information you could not have had at the time; the #1 way backtests lie |
| **BHAR** | "buy-and-hold abnormal return" — how much the stock beat its matched look-alikes over the window |
| **DGTW** | the standard way to build "look-alike" bundles: same size, value, momentum |
| **ADV** | average daily volume — how much of the stock trades in a day; drives your cost |
| **Corwin–Schultz** | estimates the spread from high/low prices alone, when quotes aren't available |
| **Placebo / date-swap** | fake events drawn from the same stock, used to prove the real ones are special |
| **FWER** | family-wise error rate — controls the "test 40 things, report the winner" fraud |
| **MDE** | minimum detectable effect — the smallest edge your sample could have caught; publish it with every null |
| **Pre-registration** | writing the rules down before looking, so the result cannot be quietly redefined |

---

## 8. THE HONEST EXPECTATION

My prior is that this comes back **negative** — that a dated, public, widely-distributed rating
change carries no tradable information 21 days later after cost. If that is what the data says, it
is a real result and should be published as one: it would mean the follow-the-upgrade strategy that
our own pages implicitly lean on is not supported by its own best-available evidence.

What would change my mind: a broker whose net, characteristic-adjusted, placebo-beating result
survives on a holdout the design never touched, at n ≥ 750, with the MDE printed next to it.
