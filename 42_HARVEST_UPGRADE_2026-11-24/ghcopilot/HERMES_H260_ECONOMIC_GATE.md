# H-260 — the rank signal is real; the economic translation is not

**Hermes · 2026-11-24 20:35 EST** · script `h260_size_artifact.py` + `h260_stop_test.py`
**Data:** one leaderboard snapshot, `hl_leaderboard_snapshot_20261124T220111Z.json`, 46,603 rows,
8,820 eligible wallets (acct ≥ $10k, week and month volume > 0).

---

## 1. What I set out to break, and could not

I attacked H-260's ρ = +0.4493 on four fronts. It survived all four.

The snapshot stores **dollar PnL**, not returns (`prior = mo_pnl − wk_pnl`, `future = wk_pnl`). Rank
correlating two dollar quantities across wallets spanning $10k to $100M equity should be mostly a **size
correlation** — a big account makes bigger dollars in both windows mechanically. That was my strongest
objection.

| Test | Result | Reading |
|---|---:|---|
| ρ(prior, acct) | **+0.112** | size explains almost none of the prior ranking |
| ρ(future, acct) | **+0.117** | nor of the future ranking |
| ρ(prior, future) — dollars | +0.4493 | the headline |
| **partial ρ given acct** | **+0.4420** | size control removes 0.007 of 0.449 |
| **ρ on RETURNS** (prior/acct, future/acct) | **+0.4290** | survives the dollars→returns conversion |

And within equity deciles, on returns:

| acct decile | median equity | n | ρ |
|---|---:|---:|---:|
| 1 | $14k | 882 | +0.3631 |
| 2 | $24k | 882 | +0.3688 |
| 3 | $43k | 882 | +0.3420 |
| 4 | $75k | 882 | +0.3798 |
| 5 | $112k | 882 | +0.4246 |
| 6 | $149k | 882 | +0.4105 |
| 7 | $209k | 882 | +0.4577 |
| 8 | $331k | 882 | +0.5023 |
| 9 | $642k | 882 | +0.4903 |
| 10 | $2,327k | 882 | +0.5756 |

**Ten of ten deciles positive, monotone increasing with equity.** Combined with Copilot's leverage
conditioning (partial ρ +0.4374, negative control collapsing a pure-leverage fake to +0.015, gradient
*decreasing* with leverage) and its survivorship treatment (20.2% missing, 63% of them tied at zero),
this is the most robust statistical result in either programme.

**Conclusion 1: wallet rank persistence is real.** It is not size, not leverage, not ties, not
survivorship, and it holds on returns as well as dollars. That is a genuine finding and it should be
recorded as one.

---

## 2. What I got wrong, and caught before reporting it

The economic gate. Top decile by prior **return**, n = 882:

| | value |
|---|---:|
| mean future return | **−3.74%** |
| median future return | **+8.11%** |
| share profitable | 69.0% |
| worst | **−889.1%** |
| best | +513.6% |
| wallets losing >100% of equity | **42 of 882 (4.8%)** |
| their combined loss | **−12,172% of equity** |

A positive median with a negative mean: 4.8% of the cohort loses more than its entire equity, and that
tail alone exceeds everything the winners earn. **Copying the top decile unstoppered loses money even
though the ranking is genuinely informative.**

Then I capped the tail — a stop at −5%, −10%, −20%, −30%, −50%:

| stop | mean | net after 26 bp | verdict |
|---|---:|---:|---|
| −5% | +13.22% | +12.96% | CLEARS |
| −10% | +12.26% | +12.00% | CLEARS |
| −20% | +10.82% | +10.56% | CLEARS |
| −30% | +9.75% | +9.49% | CLEARS |
| −50% | +8.09% | +7.83% | CLEARS |

Every stop clears, monotonically, and adding a leverage filter makes it better still (+13.91% with
turnover ≤ 5×). **That is exactly the shape of a result I should not trust, and it took about ten seconds
of arithmetic to see why.**

### Why +12.96% is not an edge

A **median weekly return of +8.11%** is roughly 600× annualised. Nothing in public markets does that. The
number is arithmetically correct and economically meaningless, because **the denominator is wrong for a
copier**:

- `acct` is the wallet's equity *at snapshot time*.
- `wk_pnl` is PnL earned on the wallet's **traded notional**, which for these wallets runs to hundreds of
  times equity — median month-volume/equity in the top decile is **10.88**, mean 106, max 8,053.
- So `wk_pnl / acct` is not "what a copier with that equity would earn". It is "PnL on enormous notional,
  divided by a snapshot equity". A copier posting $10k cannot replicate $10M of volume.
- The 42 wallets at −889% prove the leverage: you cannot lose 889% of your equity without borrowing.

Capping that series at −5% doesn't model a stop; it models *making an impossible series survivable*. The
+12.96% is a cap applied to a return that no one could have earned in the first place.

**Conclusion 2: the economic translation is invalid as measured. H-260 is a real signal with an
unmeasured economic value — not an edge, and not a near-edge.**

---

## 3. What the correct test looks like

The fix is the denominator, not the statistic. Required before any economic number is quoted:

1. **Size on tradeable capital.** Position size as a fixed fraction of the *copier's* equity, scaled to the
   wallet's risk — not `wallet PnL / wallet equity`. The return must be on the capital a copier would
   actually commit.
2. **Honest stop fills.** A −5% stop on weekly PnL assumes an intra-week exit at exactly −5%. Model it as a
   fill at the stop price with slippage, and count how often the stop never fills because the position
   gapped — for these names that will be most of the losing tail.
3. **Capacity.** Copying concentrates in the same ~4 names that carry 63% of the event supply. Report the
   size at which a copy cohort moves the price.
4. **Pre-register the stop.** I tested five stops and all cleared. That is reassuring about fragility and
   damning about provenance: choosing −20% after seeing the answer is the same sin as lowering a gate. The
   stop must be fixed in advance and the trial count recorded.
5. **Four snapshot pairs.** There is exactly **one** on disk. Every number above, in both sections, is one
   draw. Replication is currently a wall-clock constraint, not a computing one.

---

## 4. Where this leaves the programme

**One robust positive, economically unmeasured:**

- **Wallet rank persistence** — ρ +0.43 to +0.45 across dollars, returns, size-control, leverage-control,
  ties, survivorship, and all ten equity deciles. Real. Not yet tradable.

**One candidate entering a forward test:**

- **Morgan Stanley** analyst excess +178.20 bp vs 109.6 threshold (Kilo `6383307`). One survivor of nine
  5% tests ≈ 0.45 expected false positives.

**Closed negatives:**

- Portfolio rank persistence: ρ −0.020, p 0.839, n 122.
- Insider P-vs-S: **withdrawn** — dead role filter, flag parser counting 1 of 20, 63% concentration.

**Capital deployed: $0.** Unchanged, and correct.

The programme's failure mode is now well characterised: five verdicts today printed a right number over a
wrong denominator. This document's section 2 is the sixth, caught by me rather than by a peer — which is
the only reason it is written down instead of published as an edge.
