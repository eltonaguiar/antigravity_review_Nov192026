# audit2 vs audit3 — which surface is closer to a money-ready pick, and in what class

**Date:** 2026-11-19 · **Data:** live `findtorontoevents.ca/audit2/` and `/audit3/`,
`audit3_ledger.json` generated `2026-11-19T18:32:40Z`
**Short answer:** **audit2 is the surface most likely to produce a money-ready pick**, and
**EQUITY** is the asset class to work — with the caveat below that a single ETF cell is
nearer to a conclusive confidence interval than any EQUITY cell.

---

## 1. What each page actually is (verified live)

| | audit2 | audit3 |
|---|---|---|
| URL status | **200**, 6,916 B, `<title>audit2 — candidate & methodology library</title>` | **200**, 44,942 B, `<title>Audit3 — Quant Kill Tribunal</title>` |
| Role | presentation + curation: verdicts, candidate pods, forward clock, measures library, graveyard | the verdict engine: per-cell kill/promote tribunal |
| Data source | fetches `audit3_ledger.json` (with fallback paths) + `audit2_forward.json`; pod registry is a static snapshot because `reports/` is not web-served | generates `audit3_ledger.json` |
| Self-description | "The positive side of /audit3's kill tribunal… **Nothing here is money-ready.**" | "quantitative kill tribunal" |
| Can it create a pick? | It surfaces the pre-registered pods and the promotion clock, i.e. the *path* to sizing | No. It reports `n_proven=0`, `n_candidate=0` |

So they are not competitors. **audit3 decides; audit2 explains and tracks what is worth
forward-testing.** Asking which will "find money-ready picks" is asking which one is wired
to the promotion machinery — that is audit2. audit3 is the filter that keeps audit2 honest.

## 2. Live verdict state (audit3 ledger, 18:32:40Z)

`n_rows=8,613` · `n_cells_total=359` · `n_cells_tested=67` · **`n_proven=0` ·
`n_candidate=0`** · `n_weak=59` · `n_kill=8` · `n_insufficient=292`.

Class aggregates:

| Class | Verdict | n | Net/trade | 95% CI | required_n |
|---|---|---:|---:|---|---:|
| **EQUITY** | WEAK | 939 | **+0.184%** | [−0.395, +0.747] | 7,389 |
| ETF | WEAK | 586 | +0.006% | [−0.424, +0.480] | 1,745,345 |
| FOREX | WEAK | 258 | −0.024% | [−0.164, +0.119] | 8,734 |
| BOND | WEAK | 35 | −0.184% | [−0.384, +0.035] | 214 |
| CRYPTO | **KILL** | 6,740 | −0.309% | [−0.570, −0.046] | 1,652 |
| COMMODITY | **KILL** | 51 | −3.507% | [−5.363, −2.191] | 16 |
| FUTURES | INSUFFICIENT_N | 4 | +1.285% | [−2.948, +5.519] | 123 |

Every class CI includes zero (or is entirely negative). `q_value=1.0` on all of them:
nothing survives multiplicity at class level.

## 3. Where the money is *least implausible* — the pre-registered pod

There is exactly one pod with tested cells: **`POD-EQUITY-BREAKOUT`** (8 confirmatory
cells). All are `WEAK`; none passes the 2× cost gate; DSR ranges 0.0002–0.103 against a
0.95 requirement. Ranked by distance to a conclusive result:

| Cell | n | Net/trade | CI low | required_n | More rows needed | Split-half stable |
|---|---:|---:|---:|---:|---:|---|
| **ETF `rs-breakout-scout` LONG** | 80 | +0.577% | **−0.146** | **201** | **+121** | **yes** |
| ETF `adx-trend-scout` LONG | 43 | +0.386% | −0.195 | 141 | +98 | yes |
| EQUITY `donchian-stock-breakout` LONG | 45 | +1.890% | −0.677 | 162 | +117 | yes |
| EQUITY `rs-breakout-scout` LONG | 52 | +0.709% | −0.386 | 294 | +242 | no |
| EQUITY `vol-contraction-scout` LONG | 62 | +0.641% | −0.839 | 669 | +607 | no |
| EQUITY `adx-trend-scout` LONG | 52 | −0.410% | −1.670 | 1,414 | +1,362 | no |

## 4. Recommendation

**Surface: audit2.** It is the only one of the two wired to a promotion path — forward
clock, benchmark leg, 2× cost gate, per-cell `required_n`, and pre-registered pods. audit3
can only say no; audit2 is where a yes would be assembled.

**Asset class: EQUITY**, for three reasons:

1. It is the **only large class with positive net expectancy** (+0.184%/trade over 939
   rows) and PF > 1.05 (1.089). CRYPTO is KILL with a CI entirely below zero; FOREX,
   ETF and BOND are flat-to-negative.
2. All eight tested confirmatory cells are EQUITY/ETF breakout/momentum longs, and the
   pod they belong to is `POD-EQUITY-BREAKOUT` — the only pre-registered family with data.
3. The strongest single cell by mean is EQUITY `donchian-stock-breakout` (+1.890%/trade,
   n=45, stable halves, needs 162 rows against 45 today).

**One honest counter-point:** if the test is "which cell will reach a conclusive CI first",
it is **ETF `rs-breakout-scout`** — n=80, CI low −0.146 (closest to zero of any cell),
required_n 201, stable halves. That is a single-cell bet on a class whose aggregate edge
is ~0 (+0.006%), so it is a worse *class* answer and a better *experiment*.

**Neither justifies real money today.** No class meets Tier-2 (n≥100 clean, WR≥50%,
PF≥1.5, MDD<20); no pod has forward rows; every confirmatory cell fails the 2× cost gate.

## 5. The blocking fact: the forward clock is empty for this pod

`audit2_forward.json` (18:32:39Z) contains **430 rows, all `H-119`**, and its
`by_hypothesis` block for `H-119` reports `pods: []`. So `POD-EQUITY-BREAKOUT` has **zero**
forward observations. A pod cannot promote on back-scored history, so the EQUITY path is
currently blocked on registration/emission, not on statistics.

Suggested next step (not done here): register `POD-EQUITY-BREAKOUT` in the forward ingest's
`CONDITIONS` so `donchian-stock-breakout` and `rs-breakout-scout` accrue forward rows with
a same-symbol benchmark leg; then the 90-day clock measures something real instead of
re-scoring the rows that motivated the pod.

## 6. What would change this answer

- If forward rows arrive for `POD-EQUITY-BREAKOUT` and the hold-benchmark alpha CI clears
  zero, EQUITY becomes the first sizing candidate — at that point audit2's forward panel,
  not audit3's verdict table, is the page to watch.
- If ETF `rs-breakout-scout` reaches ~200 rows with CI low > 0, ETF becomes a single-cell
  sizing candidate even though its class average is flat.
- If neither happens, the correct conclusion stays "no deployable edge on available data",
  which is a successful result, not a failure.

*Not investment advice. Every figure above is from the live 18:32:40Z ledger.*
