# Vetting ledger — every pick we have actually seen, judged

Operator's record. Each row is a pick an agent has put its name to, with the verdict and the reason. **An endorsement
requires all six**: named mechanism, named counterparty, symbol vetting, `n ≥ 30`, measured cost, frozen kill rule.

Source for the rows below: Kilo's broadcast ranked-list draft (as printed in its own transcript, 2026-11-23 03:50Z
rung), and the class tables in Zoo Code's and Copilot's plan notes.

---

## Kilo — the six rows it actually published

| # | Pick | Class | Claimed net | n | Kilo's own verdict | VETTING VERDICT | Reason |
|---|---|---|---|---|---|---|---|
| 1 | **XLE LONG** | ETF (energy) | 12.40 bp @ $25k | 61 | FAIL G1,G2,G4,G5 · DSR 0.0068 (N=658) | **REJECT** | DSR 0.0068 against a 0.95 gate. n=61 is thin but the fatal number is the deflated Sharpe — the edge is indistinguishable from the best of 658 trials |
| 2 | **DOT SHORT** | CRYPTO | 11.36 bp | 13 | FAIL G1,G2,G4,G5 · DSR 0.000 | **REJECT (two reasons)** | (a) n=13 cannot support any estimate; (b) **the claimed 11.36 bp net is *below* our measured crypto round-trip band of 20–52 bp** — the figure is internally impossible unless cost was not applied. Also requires short borrow on a crypto perp, unmeasured |
| 3 | **META LONG** | STOCKS | 8.81 bp | **0** | FAIL G1,G2,G4,G5 | **REJECT — inadmissible** | **n = 0.** A pick with no observations is a preference, not evidence. This should never have been printed |
| 4 | **JUP SHORT** | CRYPTO | 7.46 bp | **0** | FAIL G1,G2 | **REJECT — inadmissible** | **n = 0**, and the same crypto cost-band contradiction as DOT. Short side on a small-cap token also needs borrow/liquidity vetting that does not exist |
| 5 | **MSTR LONG** | STOCKS | 6.38 bp | not stated | FAIL G1,G2 | **HOLD FOR EVIDENCE** | no n, no DSR; 6.38 bp against a measured 12.07 bp equity round trip means it is **negative net** even if gross-positive. Needs the gross figure and n |
| 6 | **ETH LONG / BTC LONG** | CRYPTO | 0.00 bp | — | — | **REJECT** | a 0.00 bp edge at 20–52 bp cost is −20 to −52 bp. Publishing a zero as a row is worse than publishing nothing |

**Kilo's own aggregate, which it reported honestly:** 69 picks, **0 PASS**, aggregate Sharpe 0.235, MaxDD 18.9%,
PF 2.23, DSR N=658, PBO 0.11. Its ranked rows are the output of a scan, not of a mechanism — no row states a
counterparty, and the two crypto rows contradict our own cost measurement. **Endorsed by the operator: none.**

### The question Kilo must answer

> **How did a crypto pick arrive at a *net* 11.36 bp when this programme has measured crypto round trip at 20–52 bp
> and carry at −11 bp/tick over 63 ticks?** Either cost is not being subtracted in that table, or the units are
> different from every other row. Until that is answered, **every crypto row in the file is suspect**, including the
> ones with larger n.

## Zoo Code — no rows to vet, and it says so

Its ranked list is **EMPTY by design**: *"no class has a CI on net return, so the LB ranking key is undefined for all
12."* Twelve classes, eleven marked DEAD/NOT_INVESTABLE with numbers, MEME/PENNY/SPORTS marked unmeasured for lack of
instruments, and one paper-only crypto observe pod.

**Verdict: no picks to endorse, no picks to reject — and that is the correct output.** It is also the only agent whose
per-class table distinguishes `unrankable` from `bad`, which is the distinction that stops a missing measurement being
read as a negative result.

## Copilot — none published yet; its evidence is class-level

It has measured rather than picked: equity round trip **1–5 bp** (191 names), turnover drag **ETF 0.99 bp/yr vs FOREX
56.93 bp/yr**, crypto carry killed at **3.32–4.53% gross annualised**, and the deflation correction **N=90 → DSR
0.3191, 0 of 6 classes survive**. Its own conclusion: *"proven edges remain 0."*

**Verdict: nothing to endorse.** Its `72.5 bp` vs `12.87 bp` cost gap and its surviving question — that the spread
sample covers ~5 sessions against multi-year return series — is a real defect in its own numbers and it flagged it
without being asked.

---

## What the operator endorses today

| Rank | Pick | Class | Why |
|---|---|---|---|
| 1 | **None** | — | no pick has yet produced a mechanism, a counterparty, `n ≥ 30`, a measured cost, and a surviving DSR |

**Zero endorsed picks across three agents and nine class tables.** That is the accountable answer, and it is not a
failure of the agents — it is what the gate sheet is for. The next thing that changes this table is not another scan;
it is either (a) a pick whose cost is measured on the same instrument, or (b) the transcript data purchase that makes
text-conditioned PEAD testable.

## Standing rule for this ledger

An agent may contest a `REJECT` by supplying the missing numbers in a `Revision` block in its own picks file. It may
not contest one by restating the same claim. A rejected pick that reappears unchanged gets struck from the file and
the strike recorded here with its date.
