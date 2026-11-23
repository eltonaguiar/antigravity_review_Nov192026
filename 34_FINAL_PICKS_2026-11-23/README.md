# 34 — FINAL PICKS PER ASSET CLASS · 2026-11-23

**Purpose:** one dated folder where every agent files its *final* picks per asset class, in a fixed schema, with an
auditable revision history. This is the deliverable the whole programme has been building toward: not another
methodology, not another backtest — **the ranked list, per class, with the numbers and the kill rules attached.**

---

## 1. Where your file goes

```
34_FINAL_PICKS_2026-11-23/
  README.md                 (this file)
  _TEMPLATE.md              (copy this)
  STATUS.md                 (filed / not filed, updated by the operator)
  copilot.md
  zoo.md
  kilo.md
  ag-swarm.md
  hermes.md
  <your-agent-slug>.md      (one file per agent, lowercase slug)
  OLD/                      (superseded versions live here — never delete)
```

One file per agent. Do not write into another agent's file. If you do not have a pick for a class, you still write
the row and say why — an absent class is a finding, not a blank.

## 2. Required header block (top of your file)

```
# <Agent name> — final picks, 2026-11-23
filed_utc:      2026-11-23T<HH:MM>Z
filed_local:    2026-11-23T<HH:MM> EST
repo_at:        <repo>:<branch>@<commit sha you ran against>
ranked_list:    <path or commit where your ranked list lives>
honest_headline: <one sentence: how many classes are investable, and why that number is what it is>
```

## 3. Per-class table — the schema (all ten classes, one row each)

| Column | Required content |
|---|---|
| **CLASS** | one of STOCKS, CRYPTO, BONDS, ETF, MUTUAL_FUND, FOREX, COMMODITY, OPTIONS, PREDICTION_MARKET, PRIVATE_CREDIT |
| **VERDICT** | `ALIVE` / `CANDIDATE` / `DEAD` / `UNKNOWN` / `PENDING` — nothing else |
| **PICK** | the specific instrument and direction (e.g. `XLE long`, `none`), or `none` |
| **n** | observations the verdict rests on, or `0` |
| **EDGE** | net of measured cost, in the unit you can defend (`bp/month`, `%/yr`, `bp/ticker`) |
| **DSR / N** | deflated Sharpe and the **trial count it was deflated at** |
| **PBO** | CSCV probability, reported against the **0.51 pure-noise baseline** |
| **COST** | `measured` or `assumed`, with the number and the source |
| **EXEC** | `BUY AND HOLD` or `ENTRY + TP/SL` — and the turnover consequence |
| **KILL RULE** | the frozen threshold that ends it, stated numerically |
| **EVIDENCE** | path or commit sha where the measurement lives |

Below the table, per live class, add three lines: **why this ranks here**, **what would move it up**, **what would
kill it**. For a DEAD class, one line is enough: the number and what killed it.

## 4. Revision rules (this is the part that keeps it auditable)

Two sanctioned ways to change a filed pick. Nothing else.

**(a) Append.** For a refinement that does not change earlier verdicts, append at the bottom:

```
## Revision 2026-11-23T<HH:MM>Z
changed:   <which rows>
why:       <new data / new measurement / corrected arithmetic>
impact:    <verdict changes, if any>
evidence:  <path or sha>
```

Earlier revision blocks are never edited. The file becomes a journal, newest at the bottom.

**(b) Supersede.** For a wholesale replacement, move the current file into `OLD/` renamed with its timestamp
(`OLD/copilot_2026-11-23T2130Z.md`) and write a fresh file at the normal path. `OLD/` is append-only — never delete,
never overwrite.

Silent edits to a filed verdict are the one thing that makes this folder worthless. If a number changes, the record
shows that it changed and why.

## 5. Admissibility rules (a pick that breaks these is not a pick)

1. **Every number carries n.** A 12 bp edge with no n is a rumour.
2. **Every cost is `measured` or explicitly `assumed`** — never presented as measured when it came from a table.
3. **The trial count is stated** and is the honest count of every configuration you scored, not the number of
   "strategies" you think you tried. If you cannot produce the ledger, write `N unknown → deflated at N=1000`.
4. **`UNMEASURED` is a valid value; invented precision is not.** A class with no data is `UNKNOWN`.
5. **Execution style is mandatory** because it decides the cost: buy-and-hold pays the round trip once; TP/SL pays it
   every cycle. At our measured costs the difference between the two is larger than most published edges.
6. **An empty list is a permitted and respectable answer.** `0 INVESTABLE` with reasons beats a ranked list that a
   cost test would destroy. Do not manufacture picks to fill the table.

## 6. Gates these picks are judged against

`PORTFOLIO_AND_SCREENCONTROL/03-trading-strategies/validation/strategy_validation_protocol.md` v1.0 §3.11 — 17 gates,
data integrity first, any mandatory fail = kill. In particular: DSR ≥ 0.95, PBO ≤ 0.10, WFE ≥ 0.60, alpha t ≥ 3.0
(3.5 at N_eff ≤ 100, 4.0 above), break-even cost multiple ≥ 4×, capacity ≥ 5× intended AUM, and MinTRL ≤ available
sample.

A pick that has not been measured on our own bars is not a pick; it is a hypothesis. Put it in the class row as
`CANDIDATE` with the measurement it still needs.
