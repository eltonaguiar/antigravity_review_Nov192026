#!/usr/bin/env python3
"""bootstrap_winner_on_R.py — the RULES §7 falsifier on NET R (ready for when fills exist).

The bracket-fit bootstrap could not use R (no fills yet). This is the R version, and it is
CALIBRATED like a positive control before real data arrives:
  * --selftest A "clear winner": inject one entrant with a strongly higher mean net R and low
    variance -> the test MUST report that entrant unique-winning >=95% (so it CAN revise §7).
  * --selftest B "all equal": give every entrant the same distribution -> MUST report no >=95%
    unique winner (so it cannot fabricate one).
  * --fills FILE: JSON {"ENTRANT": [r1, r2, ...], ...} per-pick NET R -> real run.

Rule (same as RULES §3-4 and the §7 arithmetic): a leaderboard is allowed only if ONE entrant is
the unique best in >=95% of the bootstrap replicates; otherwise 'no ranking' stands.
"""
import json, random, collections, sys, statistics as st

REPS = 2000
THRESH = 0.95
EPS = 0.10  # R units: a winner must beat the runner-up by >0.10 R to count as unique


def bootstrap(ents, reps=REPS, seed=20261123):
    rng = random.Random(seed)
    unique = collections.Counter(); tie_sets = collections.Counter(); uniq_reps = 0
    for _ in range(reps):
        mean = {}
        for n, v in ents.items():
            k = len(v)
            s = [v[rng.randrange(k)] for _ in range(k)]
            mean[n] = sum(s) / k
        order = sorted(mean.items(), key=lambda kv: -kv[1])
        top_n, top_r = order[0]
        second_r = order[1][1] if len(order) > 1 else -1e18
        # count as a UNIQUE winner only if it beats the runner-up by more than EPS R (practical significance)
        if (top_r - second_r) > EPS:
            unique[top_n] += 1; uniq_reps += 1
            tie_sets[1] += 1
        else:
            w = [n for n, r in order if (top_r - r) <= EPS]
            tie_sets[len(w)] += 1
    top = unique.most_common(1)[0] if unique else ("none", 0)
    share = top[1] / reps
    return {"reps": reps, "unique_winner_reps": uniq_reps,
            "unique_win_counts": dict(unique.most_common()),
            "tie_set_size_distribution": dict(sorted(tie_sets.items())),
            "top_entrant": top[0], "top_share": round(share, 4),
            "leaderboard_allowed": share >= THRESH,
            "verdict": (f"LEADERBOARD ALLOWED — {top[0]} unique-wins {share:.1%} (revise §7)"
                        if share >= THRESH else
                        f"NO RANKING — best unique-win share {share:.1%} (<95%); §7 stands")}


def selftest():
    rng = random.Random(1)
    # A: clear winner (EntrantA mean 1.0 R, sd 0.5; others mean 0, sd 1) -> should be >=95%
    A = {f"E{i}": [rng.gauss(0, 1) for _ in range(30)] for i in range(17)}
    A["CLEAR_WINNER"] = [rng.gauss(1.0, 0.30) for _ in range(30)]
    ra = bootstrap(A)
    # B: TRULY identical arrays across all entrants -> no entrant can be >EPS better -> no ranking
    identical = [0.2, -0.1, 0.05, -0.15, 0.0] * 6
    B = {f"E{i}": list(identical) for i in range(10)}
    rb = bootstrap(B)
    ok = (ra["leaderboard_allowed"] and ra["top_entrant"] == "CLEAR_WINNER"
          and not rb["leaderboard_allowed"])
    print("SELFTEST A (clear winner injected):", ra["verdict"])
    print("SELFTEST B (all equal):", rb["verdict"])
    print("CALIBRATION", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        return selftest()
    if "--fills" in sys.argv:
        path = sys.argv[sys.argv.index("--fills") + 1]
        ents = json.load(open(path))
        ents = {k: [float(x) for x in v] for k, v in ents.items() if v}
        r = bootstrap(ents)
        print(json.dumps(r, indent=2))
        return 0
    print("usage: --selftest | --fills file.json", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
