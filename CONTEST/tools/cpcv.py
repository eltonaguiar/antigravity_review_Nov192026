#!/usr/bin/env python3
"""cpcv.py - Combinatorial Purged Cross-Validation over a price panel.

Lopez de Prado, "Advances in Financial Machine Learning", Ch. 7 (CPCV):
- Split the time axis into N contiguous groups.
- For each group used as the test set, train on the remaining groups.
- Purge: drop training samples whose forward label window overlaps the test window.
- Embargo: drop training samples immediately adjacent to the test window (both
  sides) so serial correlation cannot leak future information into training.
- Fit a trivial strategy on train (constant position = sign of train mean return),
  evaluate on test, record the annualised OOS Sharpe.
- Returns the distribution of OOS Sharpes across all paths.

Usage:
    python cpcv.py <csv> <date_col> <price_col> <n_groups> <embargo> <horizon>
"""
import csv
import math
import statistics as st
import sys


def load_monthly(path, date_col, price_col):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r[date_col][:7], float(r[price_col])))
    # Resample to monthly: last close of each YYYY-MM wins.
    monthly = {}
    for d, p in rows:
        monthly[d] = p
    months = sorted(monthly.keys())
    px = [monthly[m] for m in months]
    # Simple monthly return for month[i]; label month is months[i].
    rets = [px[i] / px[i - 1] - 1 for i in range(1, len(px))]
    labels = months[1:]
    return labels, rets


def sharpe(rets, periods_per_year=12):
    if len(rets) < 2:
        return float("nan")
    m = st.mean(rets)
    s = st.pstdev(rets)
    if s == 0:
        return float("nan")
    return m / s * math.sqrt(periods_per_year)


def cpcv(labels, rets, n_groups, embargo, horizon):
    T = len(rets)
    edges = [int(round(i * T / n_groups)) for i in range(n_groups + 1)]
    paths = []
    for g in range(n_groups):
        t0, t1 = edges[g], edges[g + 1]  # test window indices [t0, t1)
        # Train candidates: all indices outside the test window.
        train = [i for i in range(T) if i < t0 or i >= t1]
        # Embargo: drop indices within `embargo` of the test window (both sides).
        train = [i for i in train if not (t0 - embargo <= i < t1 + embargo)]
        # Purge: drop train index i whose forward label window [i, i+horizon)
        # overlaps the test window [t0, t1).
        train = [i for i in train if not (i < t1 and i + horizon > t0)]
        if not train:
            continue
        train_rets = [rets[i] for i in train]
        position = 1.0 if st.mean(train_rets) > 0 else -1.0
        test_rets = [rets[i] * position for i in range(t0, min(t1, T))]
        paths.append(sharpe(test_rets))
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("usage: python cpcv.py <csv> <date_col> <price_col> <n_groups> "
              "<embargo> <horizon>")
        sys.exit(2)
    path, date_col, price_col = sys.argv[1], sys.argv[2], sys.argv[3]
    n_groups = int(sys.argv[4])
    embargo = int(sys.argv[5])
    horizon = int(sys.argv[6])
    labels, rets = load_monthly(path, date_col, price_col)
    paths = cpcv(labels, rets, n_groups, embargo, horizon)
    paths = [p for p in paths if not math.isnan(p)]
    n_paths = len(paths)
    dist = {
        "n_paths": n_paths,
        "n_months": len(rets),
        "n_groups": n_groups,
        "embargo": embargo,
        "horizon": horizon,
        "mean": st.mean(paths) if paths else None,
        "std": st.pstdev(paths) if len(paths) > 1 else None,
        "min": min(paths) if paths else None,
        "max": max(paths) if paths else None,
        "median": st.median(paths) if paths else None,
    }
    if len(paths) >= 2:
        s = sorted(paths)
        dist["p5"] = s[max(0, int(round(0.05 * (len(s) - 1))))]
        dist["p95"] = s[min(len(s) - 1, int(round(0.95 * (len(s) - 1))))]
    print("CPCV source=%s months=%d groups=%d embargo=%d horizon=%d"
          % (path, len(rets), n_groups, embargo, horizon))
    print("n_paths=%d" % n_paths)
    print("OOS Sharpe distribution:", dist)
