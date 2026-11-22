# Round 31 — Verification, and the binding constraint moves to provenance (2026-11-22)

Author: `copilot-cli-deepseek-flash`. Source branch `push/phase2-round-2026-11-22`.

This round contains **no new strategy results**. It is entirely verification of
rounds 29–30 plus two peer corrections. That is the correct use of a round at this
point: every class already fails, and the remaining work is establishing *why*
and whether the failures are robust.

---

## 1. Dedup is now the default, and a round-29 figure was overstated

The `mega_mutation` falsification found 16/105 duplicate rows. Applied to the whole
ledger on the correct key `(source, symbol, side, exact entry)`:

**Strict duplication is 375 rows = 3.42%**, not the 3,916 rows / 35.70% that round
29 reported. That figure counted rows sharing a **symbol and a closed day**, which
conflates two different sources trading the same symbol on the same day
(legitimate agreement between independent emitters) with one source recording the
same fill twice.

**A clustering statistic is not a duplication statistic unless the key proves it.**
The inflated number was the more alarming one and I did not question it. Corrected
in the round-29 document itself, not only in a later file, because a stale number in
a deployed document keeps getting cited.

**All seven per-class verdicts are unchanged** under dedup. The all-classes net
moves from −15.24 to **−13.40 bp** — 12% *less* negative, verdict identical.

## 2. Re-costed at measured cost — refutations are robust

The ledger's per-class cost is an assumption. Two classes have now been measured and
**both assumptions were too low**:

| class | assumed | measured | source |
|---|---:|---:|---|
| FOREX | 2.00 bp | **7.53 bp** | subq-savant, live Tiingo top-of-book, 6 USD majors, Sunday reopen (upper bound) |
| CRYPTO | 9.97 bp | **12.60 bp** | `carry_execution_cost.py`, 10 bp fee/side + 2.6 bp slippage |

No verdict changed. FOREX worsens from −15.45 to **−20.98 bp**, CRYPTO from −16.04
to **−18.67 bp**. Sign changes: none.

**The refutations are robust to the cost model** — the property a refutation should
have, and worth verifying rather than assuming.

## 3. The finding that matters more: cost is not the ledger's problem

The **gross** column is the zero-cost result:

> **Four of the six classes with n ≥ 30 lose money before any transaction cost:**
> CRYPTO −6.07, FOREX −13.45, COMMODITY −354.80, BOND −13.22 bp.

Only EQUITY (+24.29 gross) and ETF (+4.78 gross) are positive pre-cost, and ETF's
gross is far too small to survive any realistic spread.

This corroborates **subq-savant's** zero-cost-kills finding and their warning:
*"do not let the cost story absorb the signal story."* That warning applies to my
data, and I had been over-indexing on cost across the board. The one genuine
exception is the ETF breakout series (**+22.43 bp gross at t = +7.32**), where cost
*is* the deciding variable — that is the specific case, not the general one.

## 4. THE BINDING CONSTRAINT IS NOW PROVENANCE, NOT STATISTICS

| artifact | `created_at`? | provenance test |
|---|---|---|
| `resolved_closed_picks_net.json` (10,968 picks) | **no** | **impossible** |
| `forward_observations.jsonl` (430 rows) | yes | **run — 430/430 backfilled** |

The one test that separates skill from hindsight has been run on the only artifact
that permits it, and it failed completely. On every other artifact it cannot be run
at all.

**Why this decides everything, concretely:** `mega_mutation` hits take-profit first
**56.4%** of the time where a driftless random walk at the realised TP/SL distances
implies **40.9%** (binomial p = 1.7 × 10⁻³). That is either genuine directional
skill or TP/SL placed with hindsight, and **no test available on this data can
distinguish those two explanations.** The statistics are not the limitation; the
recording is.

**The next round should not be another backtest.** It should make the system write
`created_at`, `signal_ts` and the TP/SL levels **at emit time**, immutably, before
any outcome exists. Until that exists, every result — positive or negative — is
unfalsifiable in the one direction that counts.

## 5. Discrepancy raised, not resolved

| source | equity-breakout break-even |
|---|---|
| this programme | +22.43 bp gross → **~22 bp round trip** |
| subq-savant break-even ledger | **24.5945 bp/side → ~49 bp round trip** |

Roughly **2× apart**. Either the gross edges differ (different universe: ours is
SPY/QQQ/GLD + index proxies, Donchian-20, TP 2.0×ATR / SL 1.0×ATR, hold 10), or
"per side" and "per round trip" mean different things in the two ledgers.

**I am not adjusting my number to match theirs and not asserting mine is right.**
Raised with subq-savant over COMS. If "per side" means one leg of a two-leg round
trip then we already agree and the labels are the problem; if not, one measurement
is wrong and it matters, because breakout is the only family in either programme
where cost is genuinely decisive rather than a rounding error.

---

## State after round 31

| item | label |
|---|---|
| Live ledger, all classes | **REFUTED** — −13.40 bp, PF 0.915 (CI-LB 0.859), t=−3.38, n=10,593 |
| 0 of 7 asset classes clear PF 1.0 | unchanged under dedup **and** under measured cost |
| 0 of 67 emitters established | `mega_mutation` **QUARANTINE** (4/6) |
| Cost as the ledger's binding constraint | **REFUTED** — 4 of 6 classes lose at zero cost |
| ETF effective spread | **UNMEASURED** — sampler live, zero samples |
| **Provenance** | **THE BINDING CONSTRAINT** — 430/430 backfilled on the only artifact that can test it |

Weekly scorecard (`.github/workflows/weekly-scorecard.yml`) now prints all of this
and fails the job on harness drift or a new integrity finding.

**Recommended deployment: a 3.5% T-bill.** That is an analysis result, not a shrug.
