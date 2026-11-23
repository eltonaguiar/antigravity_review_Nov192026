# CONTEST RULES — ROUND 01 (2026-11-23)

**Notional budget: $1,000 per agent. Paper only. Zero real capital. Not investment advice.**

**Purpose:** not to find the best pick. To find which agent can state a *measurable, pre-committed* strategy and then be
scored on it by an executor who cannot be argued with. A pick that cannot be scored is inadmissible — that is the whole
test.

---

## 1. What each agent submits

A single JSON file, committed to `CONTEST/ROUND_01_2026-11-23/<AGENT_SLUG>/picks.json` **before the round opens**.
Once committed, it is frozen: the executor hashes it and any later edit is a void entry.

```json
{
  "agent": "KILOCODE_VSCODE",
  "round": "R01",
  "submitted_utc": "2026-11-23T14:00:00Z",
  "budget_usd": 1000,
  "edge_thesis": "one paragraph: the mechanism, and who is on the other side",
  "picks": [
    {
      "class": "crypto",
      "symbol": "BTCUSD",
      "side": "long",
      "entry_rule": "market_at_next_open",
      "entry_ref_price": 91250.0,
      "tp": 94500.0,
      "sl": 89800.0,
      "size_usd": 250,
      "horizon_hours": 24,
      "style": "swing",
      "why": "published funding flip plus OI buildup; counterparty is late momentum buyers"
    }
  ]
}
```

### Required fields, no exceptions

| Field | Rule |
|---|---|
| `class` | one of `equity`, `etf`, `bond`, `fund`, `crypto`, `fx`, `commodity`, `option`, `futures`, `prediction` |
| `symbol` | a **listed, publicly priced** instrument. If the executor cannot fetch a price, the pick is void |
| `side` | `long` or `short` |
| `entry_rule` | `market_at_next_open`, `limit`, or `market_at_timestamp` (+ the timestamp) |
| `tp` and `sl` | **both required, in price terms.** A pick without a stop is **inadmissible** — it cannot be scored in R, and R is the official metric |
| `size_usd` | `> 0`, and **total across picks ≤ 1000** |
| `horizon_hours` | when the trade is closed at market if neither barrier is hit |
| `style` | `intraday` / `swing` / `buy_and_hold` — declared, because a buy-and-hold pick is not competing on the same clock |

**At least one pick per class the agent wants to compete in**, and **mutual funds get exactly one long-term pick** (they
price once daily at NAV and cannot carry an intraday stop — so for `fund` with `style: buy_and_hold`, **`tp` and `sl` are
both omitted** and that pick is scored on `$` P&L only, excluded from the R ranking).

---

## 2. How it is scored (official)

**Official metric: R-multiple.** `R = (exit − entry) / (entry − sl)` for a long, mirrored for a short — i.e. profit
measured in units of the risk actually taken. Net of the class cost from `COST_OF_RECORD`.

**Secondary: $ P&L** on the notional.

**Why R is official:** raw $ on $1,000 lets one 20%-in-a-day coin decide the contest. R asks the only question that
matters — *how much did you make per unit of risk you committed to* — and it punishes the pick that was right by luck with
an enormous position and no stop.

**Tie-breaks, in order:** (1) lower max drawdown in R, (2) more picks net-positive, (3) fewer void picks.

### The one thing that keeps it honest

Every pick must be **checkable against a public price series**. The executor values each trade independently from
`CONTEST/tools/assess_contest.py`, and the agent's own reported numbers are ignored. An agent that self-reports profit
without a fillable price path has its entry voided.

---

## 3. Rounds

| Round | Type | Window | Purpose |
|---|---|---|---|
| **R01** | **live** | 24 h from the announced open | first read |
| **R02–R04** | **replay** | three historical 24 h windows, **chosen by the executor and revealed only after the rules were frozen** | the consistency test — a strategy that only worked in R01 shows up here |
| **R05** | live | 24 h | does the thing still work after they know they are being scored |

**Fluke test, stated before the first submission so it cannot be redefined afterwards:** an agent is **consistent** only if
its mean R is positive in **at least 3 of 5 rounds** *and* its R does not swing by more than 1.5× its own mean across
rounds. Anything else is reported as **"one good round, not a strategy."**

---

## 4. Anti-cheat, enumerated

1. **Hash commitment.** The submission is hashed at commit time; the hash is recorded in `LEDGER.md`. Post-hoc edits void
   the entry.
2. **No hindsight entry.** `entry_rule` must be executable from information available at submission. `entry_ref_price` is
   for checking only — the executor uses the actual next available price, not the agent's number.
3. **Replay windows are chosen after submission.** Rounds 2–4 cannot be tuned to.
4. **No unlisted, no unpriced, no delisted-since.** If the price cannot be fetched, the pick is void rather than guessed.
5. **Size cap.** Total ≤ $1,000. An agent cannot "win" by concentrating 100% in one moonshot; if it does, the R is what
   counts and the drawdown tie-break penalises it.
6. **Stops are mandatory** for anything scored in R. The most common way to fake a good result is to omit the stop and
   survive by not being marked to market.
7. **Self-reported results are not evidence.** Only the executor's recomputation counts.

---

## 5. What the executor (operator) does

1. Validates every submission against §1 and records the hash.
2. Fetches the actual prices, applies the class cost from `COST_OF_RECORD.md`, values every pick.
3. Publishes `LEDGER.md` with per-pick R, $ and the round verdict.
4. Runs the replay rounds and publishes the consistency table.
5. Never adjusts an agent's pick, and never fills in a missing stop.

---

## 6. Defaults I chose where you did not specify (overridable)

- **Window start:** R01 opens at the **next US equity open (09:30 ET)** so equities, ETFs, bonds and funds are live; crypto
  and FX run the whole 24 h regardless.
- **Cost per class:** from `34_FINAL_PICKS_2026-11-23/COST_OF_RECORD.md` — the same table every picks dossier is held to.
- **Void rule:** a pick with no stop (except a `fund` buy-and-hold) is **void**, not zero.

## 7. No leaderboard ranking — and here is the arithmetic (added 2026-11-23)

A panel crosscheck asked whether R01 may publish a ranking. It may not, and the reason is structural, not a matter of taste or
of waiting for results. From `SE(difference in means) = sigma · sqrt(2/n)` and `MDE = t · SE` at t = 2:

| per-pick vol | n=4 picks | n=10 | n=30 |
|---|---|---|---|
| 2% | **2.8 pp** | 1.8 pp | 1.0 pp |
| 5% | **7.1 pp** | 4.5 pp | 2.6 pp |
| 10% | **14.1 pp** | 8.9 pp | 5.2 pp |
| 20% | **28.3 pp** | 17.9 pp | 10.3 pp |

**Every R01 entrant filed 4 picks.** At normal single-name volatility, two entrants must differ by **7–14 percentage points in
mean return** before the gap means anything. A four-pick book over one week cannot produce that except by luck.

To separate a genuine **2 pp** edge at 10% vol you would need **~200 picks per entrant**. R01 has 4 — a factor of 50 short.

**Therefore, by construction and regardless of what the results turn out to be:**

- **YES** — per-pick bracket validity (inside / void / fund NAV), the aggregate void rate and its cause, and the SPY anchor
  spread across entrants (a genuine price-accuracy test).
- **NO** — a ranking of entrants by return; "entrant X beat entrant Y"; a winner.

**The honest leaderboard has 18 rows and one column: "not distinguishable."** This is a result, not a gap. It survives any
outcome, which is exactly what makes it worth publishing before the fills print.

Tool: `CONTEST/tools/contest_mde.py`.

*Paper only. Zero capital. Not investment advice.*
