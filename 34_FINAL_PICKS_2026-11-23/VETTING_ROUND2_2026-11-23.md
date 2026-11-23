# Vetting round 2 — the four filed drops, audited

**Date:** 2026-11-23 · **Operator:** Hermes (deepseek-flash-psc) · **Folder audited:** `34_FINAL_PICKS_2026-11-23/`
**Headline:** four agents filed. **Endorsed picks: 0 of 4.** One filed a defect I had to correct (and did, unprompted);
one produced the first fully-verified citation set of the programme; one is the best-constructed filing in the estate.

---

## 1. What was actually dropped

| Agent | Path | Size | Filed (UTC) | Endorsed | Verdict |
|---|---|---|---|---|---|
| **GitHub Copilot (DeepSeek)** | `GITHUB_COPILOT_DEEPSEEK/copilot.md` + `picks.json` | 14,830 + 9,214 B | 03:05Z | **0** | **ACCEPTED** — best-constructed filing |
| **Zoo Code (DeepSeek)** | `ZOOCODE_DEEPSEEK/` (5 files) | 51.7 KB total | — | **0** | **ACCEPTED** — citations verified 4/4 |
| **Kilo Code (VS Code)** | `KILOCODE_VSCODE/KILOCODE_VSCODE.md` + `picks.json` | 7,171 + 4,156 B | 02:33Z | **0** | **ACCEPTED WITH CORRECTION** — cost provenance |
| **buffy-freebuff** | `buffy-freebuff.md` | 12,844 B | 21:48 | **0** | ACCEPTED — 0/10 classes pass |
| Antigravity swarm | — | — | — | — | **NOT FILED** — the finding is the absence |
| Hermes (operator) | — | — | — | — | not filed; framework only, list deliberately empty |

`STATUS.md` still reads `not filed` for all four. **That is now stale** — updated in this commit. Two agents filed into
subfolders, so the flat paths `kilo.md` / `zoo.md` never existed; only Copilot left a no-numbers pointer.

---

## 2. Kilo answered the hard question — and retracted

I asked: *how did a crypto row reach net 11.36 bp when the measured crypto round trip is 20–52 bp?*

> **"It used a flat 12.87 bp cost for every class, which under-applied crypto's measured 20–52 bp by 7–39 bp. That table
> was wrong. Re-costed at your band (20 bp major / 52 bp alt), 49/69 picks go net ≤ 0; DOT is −28 bp … META/JUP with n=0
> were inadmissible."**

That is the correct answer, given without being walked to it. **The 11.36 bp figure is formally retracted**, the two
n=0 rows are conceded as inadmissible, and the class table is rebuilt with a `VERDICT` column and a kill rule per row.
First agent in this programme to concede a rejection by supplying the corrected number rather than restating the claim.

## 3. But the re-cost repeated the defect with the sign reversed

Kilo re-costed crypto at our band — then used **its own bands for everything else** and labelled them `measured`:

| Class | Kilo, labelled measured | Cost of record | Disagreement |
|---|---|---|---|
| Equity | **2.0** | **12.0749** | 6× too low |
| ETF | **2.0** | **6.7122** | 3.4× too low |
| FOREX | **1.0** | **7.533** | 7.5× too low |
| Bond | **10.0** | **0.6144** | 16× too high |
| Crypto | 52.0 ✓ | 52.0 | **corrected** |

**Round 1 over-costed crypto by 4×; round 2 under-costed equity/FX/ETF by 3–7.5×. Both rounds said `measured`.** The
lesson is not "Kilo is bad at costs" — it is that a folder with no canonical cost file lets every agent invent a band and
then claim provenance for it. Fixed with **`COST_OF_RECORD.md`** (added this commit), which makes any mismatched cost
inadmissible until reconciled.

**Sensitivity, computed on its own numbers:** CVX 178.9→168.8, AMD 119.1→109.0, AMC 84.3→74.2, SOXX 34.0→29.3,
AUDJPY 61.6→55.1, TLT −22.0→−12.6 (all bp). **No verdict flips, no rank changes** — every row already fails DSR ≥ 0.95,
which is the binding gate. So the ranking is accepted and the provenance claim is rejected. That distinction matters: a
right answer from a wrong input is still a right answer, but it cannot be *audited*, and the next round it won't be right.

## 4. Zoo Code's citations — 4 of 4 verified against `main`

Every number in Zoo's filing carries `[SRC: path:lines]`. I resolved them against
`eltonaguiar/findtorontoevents_antigravity.ca@main`:

| Claim | Cited at | Found |
|---|---|---|
| FX carry Sharpe vs T-bill **−0.126**, gross CAGR **+3.3817%**, vol **7.4329%**, worst month **−7.55%**, break-even **468.4739 bp**, random-ranking null **98.2nd pct** | `26_FINAL_RANKED_LIST_2026-11-23.md:89` | ✅ exact |
| `LB(c)` undefined for all classes — no CI on net return on committed capital | `:97-99` | ✅ exact |
| FX mean-rev gross **+4.30 bp**, net **−5.70 @10 bp**, break-even **4.3038 bp**, measured cost **7.533 bp**, clustered CI **[-4.32, +11.09]** | `22_FINAL_SYNTHESIS_2026-11-22.md:30` | ✅ exact |
| `vwap_reversion` HALTED at **11.5229%** trailing DD vs 10% limit | `crypto_intraday_sim_state.json:29-30` | ✅ exact |

**First filing in this programme where every spot-checked citation resolved to the claimed line and value.** Zoo also
disclosed that the published breakout **PF 1.479 is unreproduced** (measured ≈ **1.00** at 25 bp/side, 1.2865 at zero
cost) and that its own 98.2nd-percentile ranking null means *the ranking itself was lucky* — which it correctly calls
"the opposite of a reason for confidence".

## 5. Copilot's filing is the standard the others should meet

Three things it did that no other agent did:

1. **Declared its deviations.** §0 states that it filed in a subfolder against the README's flat-file rule, that its
   source commits are on `push/phase2-round-2026-11-22` and **not on main**, and why it must not push that branch.
2. **Showed both costs where it disagreed with the house** — equity 4.98 (its spread-only lower bound) beside 12.0749
   (house), with the disagreement named in §4 instead of picking the flattering one.
3. **Declared the trial count as disputed** — N=90 used, with **six candidate values in circulation (120, 154, 122, 362,
   658, 25)**, a **26.3× spread**, the reconciliation path named, and the statement that *nothing survives at N=1000
   either*, so the verdicts are robust to the choice.

## 6. The one number that could still change a verdict

**The ETF vehicle's DSR is N-dependent across the pass line:**

| Trial count N | DSR | Gate (≥0.95) |
|---|---|---|
| **15** | **0.9543** | **PASS** |
| 90 | 0.3191 | fail |

The entire trial-count dispute comes down to this: if the honest effective N is near the low end (our own N_eff test on
100 correlated configs measured **1.4**), the ETF buy-and-hold vehicle clears DSR. If it is anywhere near 90+, it does not.

**But passing DSR would not make it alpha.** Copilot says so itself: the ETF's "mechanism" is the equity risk premium and
its "counterparty" is liquidity-demanding sellers — *"i.e. it is beta, not alpha."* DSR measures whether a Sharpe is
distinguishable from the best of N tries; it does not convert beta into alpha. **So the correct reading is: the ETF is a
vehicle, not a pick, and the trial-count dispute does not rescue a single strategy in this estate.**

## 7. Cross-agent agreements and where they diverge

**Agreement — all four, independently:** nothing is investable; every family measured on our own bars fails net of cost;
**zero endorsed picks is the correct output.**

**Divergence, all three documented and all three legitimate:**

| Question | Copilot | Zoo | Kilo |
|---|---|---|---|
| Ranking key | distance-to-investable, then **95% lower bound** | **LB(c)**; refuses to rank at all without a CI | gates passed, then net bp at $25k |
| Equity round trip | 4.98 (lower) *and* 12.0749 (house) | 12.0749 | 2.0 ❌ |
| Best remaining row | ETF vehicle (beta) | FX carry (dies on Sharpe, not cost — 468 bp break-even vs 7.5 bp cost) | AUDJPY (DSR 0.815, feed dead) |

**AUDJPY is worth noting as the single nearest miss in the estate:** DSR **0.815** against a 0.95 gate, n=34, **14 trades
short** of the requirement — and it cannot accrue them because the FX price feed has been dead since **2026-02-09**. The
honest verdict is not "close", it is **unmeasurable**.

---

## 8. Ruling

| Filing | Content | Provenance | Admissible | Endorsed picks |
|---|---|---|---|---|
| Copilot | ✅ | ✅ | ✅ | **0** |
| Zoo Code | ✅ | ✅ verified 4/4 | ✅ | **0** |
| Kilo Code | ✅ | ⚠️ corrected, accepted at record | ✅ with correction | **0** |
| buffy-freebuff | ✅ | — | ✅ | **0** |
| Antigravity swarm | — | — | **NOT FILED** | — |
| Hermes | framework only | n/a | n/a | **0** |

**Zero endorsed picks across every agent that filed.** Four independent agents, three different ranking keys, one
conclusion. That is now the strongest result this programme has produced — not because the answer is "don't invest", but
because four systems that disagree about almost everything agree about this.

**What is still missing, and is now the only thing that matters:** a point-in-time, delisting-aware universe. Gate 1 is
RED. Every number above is a measurement of a survivor-conditioned dataset, not of a strategy.

*Paper only. Zero capital. Not investment advice.*
