# <AGENT NAME> — final picks, 2026-11-23

```
filed_utc:       2026-11-23T00:00Z
filed_local:     2026-11-23T00:00 EST
repo_at:         <repo>:main@<sha>
ranked_list:     <path or sha>
honest_headline: <how many classes are investable, and why>
endorsed_count:  <number of picks you actually endorse — 0 is allowed and respectable>
```

## Per-class picks

| CLASS | VERDICT | PICK | n | EDGE (net) | DSR / N | PBO | COST | EXEC | KILL RULE | EVIDENCE |
|---|---|---|---|---|---|---|---|---|---|---|
| STOCKS | | | | | | | | | | |
| CRYPTO | | | | | | | | | | |
| BONDS | | | | | | | | | | |
| ETF | | | | | | | | | | |
| MUTUAL_FUND | | | | | | | | | | |
| FOREX | | | | | | | | | | |
| COMMODITY | | | | | | | | | | |
| OPTIONS | | | | | | | | | | |
| PREDICTION_MARKET | | | | | | | | | | |
| PRIVATE_CREDIT | | | | | | | | | | |

## Justification per ENDORSED pick (mandatory — see JUSTIFICATION_RULES.md)

One block per pick you actually endorse. **A pick with `n = 0` cannot appear here**; it is not a pick.

### <PICK> — <CLASS>
```
MECHANISM:       <one sentence: which friction or risk premium is being harvested>
COUNTERPARTY:    <who is on the other side, and why they keep losing>
WHY THIS SYMBOL: <why this instrument and not its obvious alternative>
WHY NOW:         <what is true today that was not true a month ago>
n / DSR / PBO:   <n=  , DSR=  at N_eff=  , PBO=  >
COST:            <measured | assumed> <number> <source>
SYMBOL VET:      listed <y/n> · spread measured <bp> · borrow <fee or n/a> · PIT-safe <y/n> · duplicate exposure <none | correlated with X>
EXEC:            <BUY AND HOLD | ENTRY + TP/SL>  turnover <x/yr>  cost consequence <bp/yr>
KILL RULE:       <numeric threshold + the measurement that produces it>
EVIDENCE:        <path or sha>
```

## Overall ranked list — YOUR endorsed picks, ranked per asset class

Rank on the **95% lower bound of net return**, not the point estimate.

| CLASS | YOUR RANK | PICK | NET (LB) | WHY IT SITS HERE | WHAT WOULD MOVE IT UP | WHAT KILLS IT |
|---|---|---|---|---|---|---|
| | 1 | | | | | |
| | 2 | | | | | |

**Across-class ranking** (only if you endorse two or more classes):

| # | PICK | CLASS | CRITERION SCORE | WHY |
|---|---|---|---|---|
| 1 | | | | |

Ranking criterion used: *(state it — default is risk-adjusted net return on committed capital, ranked on the CI lower
bound, not the point estimate)*. Tie-breaks: *(state them)*.

## Per live class — three lines each

### <CLASS>
- **Why it ranks here:** 
- **What would move it up:** 
- **What would kill it:** 

## Dead / unrankable classes — one line each

| CLASS | STATUS (DEAD / UNMEASURED / UNRANKABLE) | THE NUMBER, OR THE MISSING INPUT |
|---|---|---|
| | | |

`UNRANKABLE` is not `DEAD`: it means the measurement does not exist yet, and the missing input must be named.

## What is still unmeasured

| Item | Status | What it would take |
|---|---|---|
| commission (from fills, not tariff) | | |
| point-in-time universe | | |
| capacity / market impact at size | | |

## Contesting a verdict

If the operator's `VETTING_LEDGER.md` rejected a pick, you may contest it **only by supplying the missing number** —
n, DSR at honest N_eff, or the measured cost on that instrument. Restating the claim is not a contest, and a rejected
pick that reappears unchanged is struck from the file with the strike recorded in the ledger.

## Revisions

*(append here; never edit a previous block)*
