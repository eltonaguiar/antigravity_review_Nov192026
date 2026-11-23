# Buffy (freebuff) — independent review of the R01 contest and the 2026-11-23 final picks

**Date:** 2026-11-23 · **Reviewer:** buffy, Freebuff, worktree `findtorontoevents_antigravity-ca`
**Subject:** `CONTEST/ROUND_01_2026-11-23/` and `34_FINAL_PICKS_2026-11-23/`
**Stance:** my own numbers are marked MEASURED with the command that produced them; everything else
is marked READ. Paper only. Zero capital. Not investment advice.

---

## 0. Verdicts

| Artifact | Verdict |
|---|---|
| `CONTEST/RULES.md` (pre-commitment, hash freeze, executor recomputes, R official) | **ENDORSE** — this is the right instrument and it is why R01 is publishable at all |
| `RESULTS.md` inside/outside table | **RECONCILES** — 48 picks = 15 inside + 26 outside + 7 fund; per-entrant columns sum to 48. MEASURED by hand |
| `CONTEST/tools/assess_contest.py` | **THREE DEFECTS** (§2). The published "void rule flatters by 0.57 R" figure is **not valid as measured** |
| `FINAL_PICKS/COST_OF_RECORD.md` | **ENDORSE**, with one conflict still open (§4) |
| `FINAL_PICKS/STATUS.md` "DSR N=90 disputed, 6 values, 26.3× spread" | **EXPLAINED** — it is a pointer inversion, not six opinions (§3) |
| `audit2` per-class denominator | **FIXED AND FILED** (§5) — not a prose review, a reproduced defect |

---

## 1. What the contest actually measured, and it is not forecasting

The results doc already says this (Findings 1, 11, 12b), so I will only add the part that is
measurable from the field itself: **26 of 48 picks were already outside their own bracket before a
bar printed.** With the stop mandatory and the bracket frozen, R01's leaderboard is therefore
mostly a ranking of *anchor accuracy*, not of prediction. That is a legitimate thing to measure —
it is just not the thing the folder's title promises. Keep the contest; retitle the round as
"who knows where the market is", and let θ = anchor error be a first-class column in R02.

The two entrants that "won" the structural filter (Arena, Gemini 4 Neon) did so partly because
their brackets were *wide*, which is the same geometry attack `DESIGN_REVIEW` §1 identified from
the other direction. A wide bracket brackets reality more easily. That confound is unaddressed.

---

## 2. The scorer: three defects, measured

Probe (`/tmp`, round start `2026-11-23T14:30Z`, SPY trading at 690 with a valid 675/730 bracket,
one 8-hour fund):

```
SPY   PRETRIGGERED  entry=500.0  reason: entry 500.000000 at/below stop 675.000000
VTSAX OK            entry=100.0  exit=150.0  usd=+250.0  reason=horizon
summary: {"picks":2,"void":1,"scored_in_R":0,"total_usd":250.0}
```

**D1 — the entry ignores the round start.** The docstring says *"entry is the FIRST bar's open at
or after the round start"*. `value_pick()` takes `series[0]["open"]`, and `main()` has no
round-start argument at all (`--picks --prices --out --json --fill-relative`). The probe filled a
690-priced SPY at the **2026-08-01** bar (500) and voided a perfectly good pick as
`PRETRIGGERED`.

This is not cosmetic: `DESIGN_REVIEW` §1's demonstration on Arena's picks used a **3-month panel**
and says so ("the fills are old bars"). So the headline sensitivity — *"the void rule flatters
this entry by ~0.57 R per pick"* — is a property of D1, not of the void rule. **Withdraw that
number**, or re-run it on a panel that starts at the round open. The design conclusion (clamp onto
the fill rather than void) survives on its own reasoning; the magnitude does not.

**D2 — a fund ignores its horizon.** `VTSAX` had `horizon_hours: 8` and exited at 150.0, the last
close in the file (`2026-12-31`), for `+50%` and `+$250`. Every `buy_and_hold` fund is valued at
whatever the end of the supplied series is, so the one class that "cannot be scored in R" is also
the one whose $ figure is unanchored in time.

**D3 — $ P&L is gross while R is net.** `usd = direction * (exit-entry)/entry * size_usd` has no
cost term; `net_r = gross_r - cost_r` does. `total_usd` and the "secondary: $ P&L" metric
therefore never pay the cost line that Finding 10 is entirely about — 52 bp on a $300 BTC pick is
$1.56 of real money that the $ column reports as profit. (`hits` uses `R > 0`, so the
"net-positive" tie-break *is* net; the $ column is not.)

**Fix:** add `--round-start`, value funds at the horizon bar, and compute `usd` from the net exit.

None of this touches the anti-cheat machinery, which is sound.

---

## 3. The "6 DSR values, 26.3× spread" is a pointer inversion, not six opinions

`STATUS.md` records the dispute and leaves it unresolved. I measured the cause on 2026-11-23 with
`tools/dsr_conformance.py` (battery: H-244's real cell, n=2514, per-period Sharpe 0.04735; trial
counts N ∈ {1, 26, 121, 4987}).

| implementation | file:line | N=1 | N=121 | N=4987 | verdict |
|---|---|---|---|---|---|
| `validation.sharpe_metrics` — **the file the others call canonical** | `alpha_engine/validation/sharpe_metrics.py:83` | 31.0548 | **31.0548** | 31.0548 | **IGNORES_N** |
| `statistical_rigor` | `alpha_engine/statistical_rigor.py:339` | 0.9912 | 0.4118 | — | DEFLATES |
| `audit3_tribunal` | `alpha_engine/audit3_tribunal.py:399` | — | 0.4120 | — | DEFLATES |
| `anti_overfit_validator` | `alpha_engine/anti_overfit_validator.py:418` | 0.9912 | 0.4125 | — | DEFLATES |
| `deflated_sharpe` (self-deprecated) | `alpha_engine/deflated_sharpe.py:179` | 0.9912 | 0.4113 | — | DEFLATES |
| `crypto_ml_edge` | `crypto_ml_edge/validation.py:301` | 0.9912 | **0.0000** | — | DEFLATES, disagrees |

Two facts the dispute needs:

1. **Four independent implementations agree to three decimal places** (0.4113 / 0.4118 / 0.4120 /
   0.4125). That is not a 26× spread — that is one measurement with a rounding difference.
2. **The wide disagreement is two specific files.** `sharpe_metrics.py:83` takes **no trial count**
   and returns a t-statistic (31.05) published under a probability's name; any gate of the form
   `dsr >= 0.95` fed this value passes **everything**. `crypto_ml_edge` disagrees by the entire
   range because it uses raw kurtosis (`3.0`) where the others use excess kurtosis and feeds the
   observed Sharpe directly — 0.0000 against a peer-agreed 0.412.

So the honest statement for the record is not "N=90 is disputed". It is: **at N=121 the
deflating implementations say 0.41, and the one labelled canonical cannot respond to N at all.**
Recommendation, which is a decision and not mine to make silently: repoint the deprecation note in
`deflated_sharpe.py:179` to `statistical_rigor.py:339`, and rename the `sharpe_metrics` output to
`sharpe_t_stat` so nothing can mistake it for a deflated probability. Full battery:
`reports/dsr_conformance_2026-11-23.{json,md}`.

---

## 4. Cost of record: right instrument, one conflict left open

Endorsed as written: my `12.0749 bp` is correctly labelled an **upper bound superseded for EQUITY
by the 191-name measurement**, and `4.98` is correctly labelled a **lower bound**. That is the
honest pattern and it is the reason `COST_OF_RECORD.md` is an improvement on the prose it
replaced.

The open conflict: Copilot's own todo-20 measurement records **0.9756 bp** round trip (Corwin-
Schultz 0.7696 + SEC 0.206, zero commission/ECN, 191 names, 356,271 one-minute bars), recomposed
from components. That is **12.4× below** the 12.0749 row and **5.1× below** the 4.98 "spread only"
lower bound, and it is not in the table. Cost decides verdicts near the floor, so this needs an
owner and a line: either a fourth row, or a retraction of one of the three. Right now the estate
holds three measured equity costs and the "only admissible input" table contains two of them.

---

## 5. `/audit2` — the `flat` denominator (fixed, filed)

Not a review of prose. `tests/test_audit2_per_class_panel.py::test_panel_matches_golden_snapshot`
was failing (`CRYPTO.flat: panel 0 != golden 1`). Root cause: `is_performance_scored_row()` in
`alpha_engine/resolved_closed_view.py` quarantined **every** zero-PnL row, so a trade that
genuinely resolved at breakeven left `n` and `mean_net_pct` entirely, and the panel's published
`flat` count was structurally unreachable. The bias had a direction: deleting a flat row removes
its cost from the mean, so the old figure **flattered** the class (golden fixture CRYPTO: 0.4003
wrong → 0.2336 right, with n 2 → 3).

Fixed by admitting only zero rows whose exit reason proves resolution (`TIME_EXIT`/`TIME`, which
`audit_trail/universal_pick_resolver.py:1567` writes); `EXPIRED` placeholders stay quarantined.
`win_rate_pct` and PF do not move (WR excludes flat by definition; PF sums gross win/loss sums and
a flat row contributes 0 to neither). Measured blast radius: 567 rows quarantined as zero-PnL in
the canonical sidecar; in the 3,500-row scored slice, 29 of 40 zero rows become `flat` and 11 stay
out. 36 + 53 tests green; golden **not** regenerated. Details:
`updates/2026-11-23-audit2-flat-denominator-fix.md` in the research tree.

---

## 6. What I did not verify

- **Kilo's DSR values** (0.815 at N=658, etc.). Not recomputed. They are plausible and consistent
  with a deflating implementation, but "plausible" is not verification and I am not recording them
  as checked.
- **The live prices in `RESULTS.md`** (Yahoo/Binance at 04:0xZ). Not refetched, so the
  inside/outside classification is theirs, not mine — only its arithmetic is verified.
- **Zoo Code's CI-lower-bound ranking.** Read, not recomputed.

---

## 7. Two things worth keeping, said plainly

1. **The executor recomputes and the entrants' own numbers are ignored.** That single invariant is
   why a 12-model panel produced a reportable result instead of 12 press releases.
2. **The self-correction record** (the recomputed hash that caught a carried-over value, the A3
   retraction, the retraction of the 88%-synthetic alarm). In this estate, published retractions
   are rarer than findings, and they are the reason the rest is believable.

*Paper only. Zero capital. Not investment advice.*
