# Tracking the forward test

The point of PROVEIT is not one backtest -- it is a record that accumulates. Every
time you re-run a simulation you append a row instead of overwriting it, so drift
becomes visible.

```bash
# 1. run a simulation (writes a stamped file)
python3 sim/proveit.py --sims 1000 --out results/run_$(date -u +%Y-%m-%dT%H%MZ).json

# 2. record it
python3 TRACKING/tracker.py --record results/run_<stamp>.json

# 3. later, compare
python3 TRACKING/tracker.py --check
```

Files:
- `forward_log.jsonl` -- append-only history, one JSON row per run.
- `state.json` -- the last seen scenario values, used to compute the delta.

## What counts as progress

A scenario is only interesting if it moves from `INCONCLUSIVE` to `PROVEN_EDGE`
across **multiple** runs with **different seeds**, not one lucky draw. A single run
moving is noise (see README §6: ~1.2 false positives expected in 24 trials).

## When to stop

If after several runs every verdict is still `INCONCLUSIVE` or `KILLED`, that IS the
answer: the philosophy is not provably better than cash, and the honest action is to
hold T-bills or a broad index and not trade it. Stopping is a result.
