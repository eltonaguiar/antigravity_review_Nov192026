# Arena.ai harness — review (18th answer, the only one that shipped code)

**Verdict: the best-executed artefact of the eighteen, and it contains the defect this whole programme exists to catch.**

Files: `arena_workspace/README.md` (319 lines), `run_study.py` (190), `src/engine.py` (396). Copied verbatim for the record.

## 1. It runs, and every substantive claim reproduces

Once `out/` exists (see defect 1), `python run_study.py` completes in **29.4 s** — against its own claimed ~30 s.

| Its claim | Measured | Verdict |
|---|---|---|
| "Crypto long top-gainer: biggest point estimate (+91 bps/5d) but the **least reliable** — CI straddles zero" | +0.00912 (**+91.2 bp**), CI **[−0.00374, +0.02317]** | ✅ exact |
| "FX long: −12 bps, t = 4.4, survives BH-FDR" | −0.00119 (**−11.9 bp**), p 3e−5, BH 2.4e−4 significant | ✅ exact |
| "BTCUSD-long +0.165R vs BTCUSD-short −0.076R — same symbol, opposite sign" | **+0.165 / −0.076** | ✅ exact |
| "EURUSD reversal: +0.089R at 0bp → +0.067R at 2bp → 0.005R at 8bp → negative at 12bp" | **+0.0885 / +0.0675 / +0.0046 / −0.0374** | ✅ exact |
| "36 slices → 8 raw p<.05, expected ≈2, BH-FDR left 4" | **36 → 8 → 4** | ✅ exact |
| "Mutual funds are untestable at daily frequency" | MFUNDX IC = NaN, DSR = 0, excluded from the class table | ✅ correct handling |

**That is a real result.** Not one number it reported to the operator was inflated.

## 2. What it does right, and it is more than any other answer

- **Next-bar entry** (`entry = open[i+1]`), so no same-close trade.
- **Conservative intrabar resolution** — if both barriers sit inside one bar, **the stop wins** (line 180–182). That is the
  single most common inflator of TP/SL backtests, and it got it right by default.
- **Cross-sectional demeaning** (`excess = fwd − class_mean_fwd`) so class drift and market beta cannot masquerade as skill —
  which is also the correct answer to the BTC-beta problem Claude 5.1 Fable raised.
- **Block-bootstrap CIs**, not IID ones.
- **Non-overlapping IC** (`IC_nonoverlap` uses every 5th observation) and it prints the honest sample size beside the naive
  one: 427 vs 2,131.
- **BH-FDR across every slice it tested**, and it reports the raw-vs-adjusted gap explicitly.
- **Per-side split** with a planted edge on one side only, so the harness can be seen to distinguish them.
- **Mutual funds excluded** as untestable rather than fudged.

## 3. Three defects

### (1) It does not run out of the box — and that is why the shipped folder was empty

```
FileNotFoundError / OSError: Cannot save file into a non-existent directory: 'out'
```

`run_study.py` writes `out/1_top_gainer_slices.csv` before creating `out/`. It crashes at the first write. **That is why the
downloaded workspace contained no CSVs and no `out/study_charts.png`, although the hand-off message listed both as
delivered.** One-line fix: `os.makedirs(OUT, exist_ok=True)`.

### (2) `deflated_sharpe()` under-deflates — the serious one

```python
var_sr = (1 - skew*sr + (kurt-1)/4*sr**2) / max(n-1, 1)
sr0 = sqrt(var_sr) * ((1-emc)*z1 + emc*z2)
```

The DSR formula requires **`V[SR_n]` — the variance of the Sharpe estimates *across the trials***. The code substitutes the
**standard error of the single chosen series**. With n = 1,267 trades that quantity is tiny, so `sr0 → ~0` and the
"deflated" statistic collapses into the undeflated PSR.

Consequence: **DSR = 1.000 for BTCUSD (Sharpe 1.795), EURUSD, and AAA**, and `passes_DSR: True` on all three. The deflation
never bit. Those three passes are **not established** — at 24 trials with the Sharpes actually observed (range +1.795 to
−0.377), `V[SR_n]` is order 0.1–0.3, so `E[max SR | null]` is order 0.5–1.0, and BTCUSD's 1.795 would deflate to something
materially below 1.000 — plausibly below the pass mark once the honest dispersion is used.

**Same defect class as Kilo's `forex_rsi2_mean_reversion` row** (DSR 0.9987 at N=61 vs 0.876 at the honest N=4,987): in both
cases the deflation is computed against the wrong basis, and in both cases it fails **in the direction that flatters**.
Two repos, two agents, one bug class. That is now a pattern, and it is the single strongest argument for having exactly one
DSR implementation in the estate.

### (3) PBO is recommended but not implemented

README lists `PBO (CSCV) < 0.3` as a gate and cites López de Prado for PBO; `run_study.py` and `engine.py` contain **no PBO
or CSCV code at all** (`grep -i pbo` matches README lines 179, 250, 316 only). A gate that is recommended and not computed
is a gate that silently passes.

## 4. What it adds to the corpus

- **The controlled demonstration** nobody else produced: a planted edge that the harness *detects* (BTCUSD IC 0.166, t 3.47)
  and noise it *rejects* (equity long p 0.70), in the same run. That is a falsification test of the tool, not of a strategy.
- **The cost ladder as a table** rather than an assertion: the same edge dies between 5 and 8 bp.
- **`make_synthetic_universe()` as a swappable panel** — the honest way to ship a method: prove it on data whose answer is
  known, then point it at real data.

## 5. Rulings

| Item | Ruling |
|---|---|
| Copy the harness in | **yes** — archived under `arena_workspace/` |
| Its substantive numbers | **accepted**, reproduce exactly |
| Its three `passes_DSR: True` | **rejected** — under-deflated; must be recomputed with cross-trial dispersion |
| Its "PBO < 0.3" gate | **not computed** — must be implemented or removed from the README |
| Its demo as market evidence | **rejected** — synthetic data by construction; method proof only |

**Ruling in one line:** the harness is good enough to build on and not good enough to trust on trial count — which is
exactly the failure mode this folder documents seventeen times over, now with code attached.

*Paper only. Zero capital. Not investment advice.*
