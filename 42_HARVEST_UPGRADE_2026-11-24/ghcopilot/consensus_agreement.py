#!/usr/bin/env python3
"""consensus_agreement.py - Track C: does ANALYST/CROWD AGREEMENT add information?

Difference test ONLY. A positive mean excess in the AGREE bucket says nothing; the
question is whether AGREE beats DISAGREE, so this script reports the DELTA with a CI
and a permutation placebo, and refuses to call a level a finding.

Legs
  analyst : docs/data/harvest_symbol_history.json - monthly consensus label per
            symbol (4 periods: 2026-08-01..2026-11-01). Joined AS-OF the pick's
            entry_date, never to the current snapshot (that would be lookahead).
  user    : 42_HARVEST_UPGRADE_2026-11-24/kilocode/picks_now_resolved_2026-11-24.json
            - 585 resolved picks with direction, entry_date, exit_pnl_pct.

Buckets (picks are long-only in this file, so direction is constant)
  AGREE    : pick long AND analyst label in {STRONG_BUY, BUY}
  DISAGREE : pick long AND analyst label in {SELL, STRONG_SELL}
  EXCLUDED : analyst HOLD/neutral - cannot agree or disagree, so it is not a bucket

Cost/benchmark treatment
  `exit_pnl_pct` is used as published. A UNIFORM cost or benchmark subtraction
  cancels exactly in (mean_agree - mean_disagree), so the delta is invariant to it.
  That is NOT true of the LEVELS, and it is not true of the delta either if the two
  buckets sit in different date ranges - so the date balance is measured and printed.

Run: python3 consensus_agreement.py [--reps 4000]
Reads from /tmp where the origin blobs were staged; no writes outside stdout.
"""
import argparse
import collections
import json
import math
import random
import statistics

PICKS = "/tmp/pnr.json"
HIST = "/tmp/hsh.json"

BULL = {"STRONG_BUY", "BUY"}
BEAR = {"SELL", "STRONG_SELL"}


def load():
    picks = json.load(open(PICKS))
    hist = json.load(open(HIST))
    label = {}
    for s in hist["symbols"]:
        for pp in s["periods"]:
            label[(s["symbol"], pp["period"])] = pp["label"]
    syms = {s["symbol"] for s in hist["symbols"]}
    return picks, label, syms


def asof_period(label, sym, date):
    """Latest analyst period at or before the pick date. None if none exists."""
    cand = [p for (s, p) in label if s == sym and p <= date[:10]]
    return max(cand) if cand else None


def bucketise(picks, label, syms):
    b = collections.defaultdict(list)
    drop_nosym = drop_noperiod = 0
    for pk in picks:
        sym, d = pk["symbol"], pk["entry_date"]
        if sym not in syms:
            drop_nosym += 1
            continue
        per = asof_period(label, sym, d)
        if per is None:
            drop_noperiod += 1
            continue
        L = label[(sym, per)]
        row = {"symbol": sym, "entry": d, "period": per, "label": L,
               "pnl": float(pk["exit_pnl_pct"]), "exit_reason": pk["exit_reason"]}
        if L in BULL:
            b["AGREE"].append(row)
        elif L in BEAR:
            b["DISAGREE"].append(row)
        else:
            b["EXCLUDED_HOLD"].append(row)
    return b, drop_nosym, drop_noperiod


def mean(xs):
    return statistics.mean(xs) if xs else float("nan")


def boot_ci(xs, reps, seed=7, lo=2.5, hi=97.5):
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rnd = random.Random(seed)
    n = len(xs)
    ms = sorted(mean([xs[rnd.randrange(n)] for _ in range(n)]) for _ in range(reps))
    return (ms[int(lo / 100 * reps)], ms[min(reps - 1, int(hi / 100 * reps))])


def boot_delta(a, d, reps, seed=11):
    if len(a) < 2 or len(d) < 2:
        return (float("nan"), float("nan")), float("nan")
    rnd = random.Random(seed)
    ds = []
    for _ in range(reps):
        ma = mean([a[rnd.randrange(len(a))] for _ in range(len(a))])
        md = mean([d[rnd.randrange(len(d))] for _ in range(len(d))])
        ds.append(ma - md)
    ds.sort()
    return (ds[int(.025 * reps)], ds[int(.975 * reps)]), statistics.stdev(ds)


def placebo(picks, label, syms, observed_delta, reps, seed=23):
    """Shuffle analyst LABELS within each period, keeping dates/symbols aligned.

    This destroys the symbol->label link while preserving the label mix and the
    calendar, so it tests agreement specifically rather than market direction.
    """
    rnd = random.Random(seed)
    by_region = collections.defaultdict(list)
    for pk in picks:
        per = asof_period(label, pk["symbol"], pk["entry_date"])
        if per is None:
            continue
        by_region[per].append((pk, label[(pk["symbol"], per)]))
    lab_pool = collections.defaultdict(list)
    for per, rows in by_region.items():
        lab_pool[per] = [L for _, L in rows]
    hits = 0
    valid = 0
    for _ in range(reps):
        a, d = [], []
        for per, rows in by_region.items():
            pool = list(lab_pool[per])
            rnd.shuffle(pool)
            for (pk, _), L in zip(rows, pool):
                v = float(pk["exit_pnl_pct"])
                if L in BULL:
                    a.append(v)
                elif L in BEAR:
                    d.append(v)
        if len(a) >= 2 and len(d) >= 2:
            valid += 1
            if abs(mean(a) - mean(d)) >= abs(observed_delta):
                hits += 1
    return (hits / valid if valid else float("nan")), valid


def mde(a, d, alpha_z=1.96, power_z=0.84):
    if len(a) < 2 or len(d) < 2:
        return float("nan")
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(d) / len(d))
    return (alpha_z + power_z) * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=4000)
    args = ap.parse_args()

    picks, label, syms = load()
    b, drop_nosym, drop_noperiod = bucketise(picks, label, syms)
    A = [r["pnl"] for r in b["AGREE"]]
    D = [r["pnl"] for r in b["DISAGREE"]]
    H = [r["pnl"] for r in b["EXCLUDED_HOLD"]]

    print("INPUTS")
    print("  picks total: %d" % len(picks))
    print("  dropped, symbol not in analyst feed: %d" % drop_nosym)
    print("  dropped, no analyst period at/before entry: %d" % drop_noperiod)
    print("  directions present: %s" % sorted({p["direction"] for p in picks}))
    print()

    print("BUCKETS  (net excess = exit_pnl_pct as published; see header on invariance)")
    for name, xs in (("AGREE", A), ("DISAGREE", D), ("EXCLUDED_HOLD", H)):
        if xs:
            lo, hi = boot_ci(xs, args.reps)
            print("  %-14s n=%4d mean=%8.3f%%  CI95=[%7.3f, %7.3f]  sd=%6.3f"
                  % (name, len(xs), mean(xs), lo, hi,
                     statistics.stdev(xs) if len(xs) > 1 else float("nan")))
        else:
            print("  %-14s n=   0  (no rows)" % name)
    print()

    if len(A) >= 2 and len(D) >= 2:
        delta = mean(A) - mean(D)
        (dlo, dhi), _ = boot_delta(A, D, args.reps)
        p_placebo, valid = placebo(picks, label, syms, delta, max(200, args.reps // 4))
        m = mde(A, D)
        ca = [r["entry"] for r in b["AGREE"]]
        cd = [r["entry"] for r in b["DISAGREE"]]
        print("DIFFERENCE TEST (the only claim Track C permits)")
        print("  delta = mean(AGREE) - mean(DISAGREE) = %+.3f pp" % delta)
        print("  CI95 = [%+.3f, %+.3f]" % (dlo, dhi))
        print("  excludes zero: %s" % ("YES" if (dlo > 0 or dhi < 0) else "NO"))
        print("  placebo p (label shuffle): %.4f over %d valid shuffles" % (p_placebo, valid))
        print("  MDE (80%% power, a=.05): %.3f pp" % m)
        print("  date balance: AGREE %s..%s  DISAGREE %s..%s"
              % (min(ca), max(ca), min(cd), max(cd)))
    else:
        print("DIFFERENCE TEST")
        print("  NOT COMPUTABLE: need n>=2 in BOTH buckets; got AGREE=%d DISAGREE=%d"
              % (len(A), len(D)))
        print("  This is INSUFFICIENT SAMPLE, which is a different outcome from")
        print("  NO EFFECT. It is not evidence that agreement does not work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
