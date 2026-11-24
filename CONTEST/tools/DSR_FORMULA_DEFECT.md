# DEFECT: `CONTEST/tools/dsr.py` does not deflate — it inflates

**Found:** 2026-11-24 · **Severity:** higher than the fixture problem it was found next to
**Status:** measured, reproducible, NOT fixed (fixing it changes every DSR the estate quotes, so it
needs an owner decision) · **Guarded meanwhile:** `DSR_GUARD.md`

## The one-sentence version

A Deflated Sharpe Ratio must get **harsher** as you try more things. This one gets **more
confident**. On pure noise — where there is no edge at all — it reports **0.99986** once the trial
log is long enough.

## The measurement

Feed it trials drawn from a standard normal (true Sharpe = 0, i.e. **nothing**), and vary only how
many trials there are:

| N trials | DSR reported | best Sharpe seen | direction |
|---:|---:|---:|---|
| 10 | 0.931952 | 1.311 | — |
| 30 | 0.991424 | 2.336 | up |
| 50 | 0.994344 | 2.336 | up |
| 100 | 0.994558 | 2.336 | up |
| 200 | 0.991232 | 2.336 | down |
| 500 | 0.990755 | 2.375 | down |
| 1000 | 0.999364 | 3.214 | up |
| 2000 | **0.999858** | 3.646 | up |

Five independent seeds, N=50 vs N=500:

| seed | DSR(50) | DSR(500) | |
|---:|---:|---:|---|
| 1 | 0.996507 | 0.996477 | falls (barely) |
| 2 | 0.984491 | **0.997718** | rises |
| 3 | 0.984186 | **0.997214** | rises |
| 4 | 0.989656 | **0.999592** | rises |
| 5 | 0.976481 | **0.996061** | rises |

**A ratio that stays above 0.93 on pure noise is not a significance test.** And it never approaches
the 0.5 that "the best result is indistinguishable from luck" would deserve.

## Why it happens (the arithmetic)

The code computes:

```
z   = (SR_best − sr_bench) / sd_across_trials      # sr_bench defaults to 0
DSR = Φ(z)
```

Both terms move the wrong way as N grows:

1. **`SR_best` increases with N.** The best of N draws from a null distribution grows roughly like
   √(2·ln N). More trials ⇒ a bigger numerator ⇒ more confidence. Backwards.
2. **`sd_across_trials` is the wrong denominator.** It is the *dispersion of the trials*, not the
   *standard error of the Sharpe estimate*. It does not depend on how much data each trial had (the
   sample length `T`), and it is not the quantity the paper deflates by.

So `z` grows with N, and `Φ(z)` saturates at 1.

## What the cited paper actually specifies

Bailey & López de Prado (2014) deflate by the **expected maximum Sharpe under the null**:

```
DSR = Φ[ (SR_best − SR_0) · √(T−1) / √(1 − γ3·SR_best + ((γ4−1)/4)·SR_best²) ]

SR_0 = √Var(SR_trials) · [ (1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e)) ]
γ    = 0.5772…      (Euler–Mascheroni)
T    = number of return observations per trial
γ3, γ4 = skewness and kurtosis of the returns
```

Three things matter here that this module never does:

- **`SR_0` is subtracted.** `SR_0` *also grows with N*, and it is specifically constructed to cancel
  the mechanical growth of `SR_best`. The module subtracts a constant `0` instead, so nothing cancels.
- **`T` appears.** A Sharpe measured on 20 observations is far less certain than one measured on
  2,000. The module never reads `T` — the `trials` table does not even store it.
- **Skew/kurtosis appear** (`γ3`, `γ4`) — the Lo (2002) correction the module's own docstring cites
  but does not implement.

## Why this is worse than the fixture bug

The fixture bug (4 dummy rows ⇒ 0.99998) produces a wrong number on data that is obviously wrong.
This produces a wrong number on **clean** data.

Concretely: the guard I shipped refuses fixtures and `n < 30`. A **clean** 30-row ledger therefore
passes the guard and emits a DSR that is still inflated by this defect. **The guard is necessary but
not sufficient.** Do not read "no refusal" as "valid DSR".

## Recommendation (owner decision, not taken here)

Two honest options:

1. **Fix the estimator** — implement the real DSR: store `T`, `γ3`, `γ4` per trial, compute `SR_0`,
   subtract it, and divide by the Lo standard error. This invalidates every previously quoted DSR,
   which is the point.
2. **Rename the function** to what it is — e.g. `best_sharpe_over_dispersion()` — and stop calling it
   a Deflated Sharpe Ratio or quoting it as multiple-testing-corrected. Cheap, honest, and stops the
   number from being believed.

Option 2 is defensible as an interim: the name is the whole problem. But a rename must come with an
entry in `DSR_VOID_9c9eda3.md`, because the old name is already in published COMS notes.

**Do not** do what produced this situation: keep the name, keep the citation, and publish the number.

## How to re-verify in one command

```bash
python3 - <<'PY'
import sys, random, sqlite3, tempfile, os
sys.path.insert(0, "CONTEST/tools")
from dsr import dsr_from_db
def build(n, seed=42):
    p = os.path.join(tempfile.mkdtemp(), "t.db")
    c = sqlite3.connect(p)
    c.execute("create table trials(trial_id,run_id,family,variant,sharpe_is,sharpe_oos,kept,ts_logged)")
    r = random.Random(seed)
    for i in range(n):
        c.execute("insert into trials values(?,?,?,?,?,?,?,?)",
                  (f"t{i}", "live-run-1", "trend", f"v{i}",
                   round(r.gauss(0,1),4), round(r.gauss(0,1),4), 0, "now"))
    c.commit(); c.close(); return p
for n in (50, 500, 2000):
    print(n, dsr_from_db(build(n), min_trials=0)[0])
PY
```

If the printed values **rise** with `n`, the defect is present. `min_trials=0` is required because
the guard will otherwise refuse small `n` — which is itself correct behaviour.
