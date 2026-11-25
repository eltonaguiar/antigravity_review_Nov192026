#!/usr/bin/env python3
"""Re-run Track B's design effect as a real bootstrap, not arithmetic.

DE = (SE_cluster / SE_iid)^2 from a 2000-replicate SYMBOL-CLUSTER bootstrap of
the mean EQUITY excess return. SE_iid is the analytic sqrt(var/n); SE_cluster
is the bootstrap SD of the resampled means.

Input: 42_HARVEST_UPGRADE_2026-11-24/tracker/CLASS_CALIBRATION_PRICE_PANEL.csv
       (included == 1 rows)
  excess = (exit_close/entry_close - 1) - (bench_exit_close/bench_entry_close - 1)
"""
from __future__ import annotations

import csv
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

SEED = 20261124
N_REP = 2000
PANEL = Path(__file__).resolve().parent / "CLASS_CALIBRATION_PRICE_PANEL.csv"


def main() -> int:
    rows = [r for r in csv.DictReader(open(PANEL, encoding="utf-8")) if r["included"] == "1"]
    by_sym: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        x = ((float(r["exit_close"]) / float(r["entry_close"]) - 1)
             - (float(r["bench_exit_close"]) / float(r["bench_entry_close"]) - 1))
        by_sym[r["symbol"]].append(x)
    vals = [v for vs in by_sym.values() for v in vs]
    n, k = len(vals), len(by_sym)
    m = statistics.mean(vals)
    se_iid = math.sqrt(statistics.variance(vals) / n)

    rng = random.Random(SEED)
    keys = sorted(by_sym)
    means = []
    for _ in range(N_REP):
        pick = [rng.choice(keys) for _ in keys]
        sample = [v for s in pick for v in by_sym[s]]
        if sample:
            means.append(statistics.mean(sample))
    se_cluster = statistics.stdev(means)
    de = (se_cluster / se_iid) ** 2
    print(f"n={n} symbols={k} mean_excess={m:.6f}")
    print(f"SE_iid={se_iid:.6f} SE_cluster={se_cluster:.6f} DE={de:.4f} ratio_to_0.3766={de/0.3766:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
