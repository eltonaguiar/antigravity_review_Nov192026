#!/usr/bin/env python3
"""bootstrap_winner.py — is the contest ranking distinguishable, or does the winner vary?

Falsifier for RULES.md §7 ("no leaderboard ranking"). We resample each entrant's picks WITH
REPLACEMENT (same count) 2000 times and count how often each entrant finishes first.

CRITICAL CAVEAT: as of R01b there is NO realized R (the round has not filled - RESULTS.md
line 112). The only per-pick outcome the live snapshot supports is **bracket-fit**: does the
live price sit inside [sl, tp]? So the scored metric here is the INSIDE RATE (bracket fit),
NOT R. We say so plainly. A real R bootstrap can be run identically once fills exist.
"""
import json, glob, os, random, collections, sys

ROUND = "CONTEST/ROUND_01_2026-11-23"
LIVE = json.load(open(f"{ROUND}/_live_quotes.json"))["live"]


def norm_sym(s):
    s = str(s or "").upper().replace("-USD", "USD").replace("/", "")
    return s


def live_price(sym):
    for k in (sym, sym.replace("USD", "-USD"), sym + "=X"):
        if k in LIVE:
            return LIVE[k]
    return None


def inside(side, tp, sl, px):
    if tp is None or sl is None or px is None:
        return None
    side = (side or "long").lower()
    if side == "long":
        return sl < px < tp
    return tp < px < sl


def load_entrants():
    ents = {}
    for d in sorted(glob.glob(f"{ROUND}/*/")):
        name = os.path.basename(d.rstrip("/"))
        if name.startswith("_"):
            continue
        picks_path = os.path.join(d, "picks.json")
        if not os.path.exists(picks_path):
            continue
        try:
            pj = json.load(open(picks_path))
        except Exception:
            continue
        scored = []
        for p in pj.get("picks", []):
            px = live_price(norm_sym(p.get("symbol")))
            v = inside(p.get("side"), p.get("tp"), p.get("sl"), px)
            if v is not None:
                scored.append(1 if v else 0)
        if scored:  # entrants with 0 scorable picks cannot win
            ents[name] = scored
    return ents


def rank(scores):
    # mean inside-rate desc; tie-break: fewer voids (more picks with a hit) -> more picks; then name
    def key(item):
        name, vals = item
        rate = sum(vals) / len(vals) if vals else -1
        return (-rate, -sum(vals), -len(vals), name)
    return sorted(scores.items(), key=key)


def main():
    ents = load_entrants()
    N = len(ents)
    print(f"entrants with scorable picks: {N}")
    for n, v in sorted(ents.items()):
        print(f"  {n:28s} picks={len(v)} inside={sum(v)} rate={sum(v)/len(v):.2f}")

    base = rank({n: list(v) for n, v in ents.items()})
    print("\npoint-estimate order (INSIDE rate):")
    for i, (n, v) in enumerate(base, 1):
        print(f"  {i:2d}. {n:28s} {sum(v)/len(v):.2f}")

    reps = 2000
    rng = random.Random(20261123)
    top_tie = collections.Counter()      # entrant in the winning tie-set
    unique_wins = collections.Counter()  # entrant is the SOLE first place
    tie_sizes = collections.Counter()
    unique_rep = 0
    for _ in range(reps):
        rate = {}
        for n, v in ents.items():
            k = len(v)
            samp = [v[rng.randrange(k)] for _ in range(k)]
            rate[n] = sum(samp) / k
        mx = max(rate.values())
        winners = [n for n, r in rate.items() if abs(r - mx) < 1e-12]
        tie_sizes[len(winners)] += 1
        for w in winners:
            top_tie[w] += 1
        if len(winners) == 1:
            unique_wins[winners[0]] += 1
            unique_rep += 1

    print(f"\nbootstrap {reps} reps — TIE-AWARE first place:")
    print("  entrants in the winning tie-set (share of reps):")
    for n, c in top_tie.most_common():
        print(f"    {n:28s} {c:4d}  {100*c/reps:5.1f}%")
    print("  tie-set size distribution:", dict(sorted(tie_sizes.items())))
    print(f"  replicates with a UNIQUE winner: {unique_rep}/{reps} ({100*unique_rep/reps:.1f}%)")
    if unique_wins:
        print("  unique-win counts:", dict(unique_wins.most_common()))
    # distinguishable only if ONE entrant is the sole winner >=95% of the time
    top_unique = unique_wins.most_common(1)[0][1] / reps if unique_wins else 0
    wins = unique_wins
    winner_sets = tie_sizes
    top_share = top_unique
    distinct_winners = len(unique_wins)
    out = {"entrants": {n: {"picks": len(v), "inside": sum(v)} for n, v in ents.items()},
           "point_estimate_order": [n for n, _ in base], "replicates": reps,
           "unique_win_counts": dict(wins.most_common()),
           "top_tie_set_counts": dict(top_tie.most_common()),
           "tie_set_size_distribution": dict(sorted(tie_sizes.items())),
           "unique_winner_replicates": unique_rep,
           "top_winner_share": round(top_share, 4),
           "distinct_orderings": dict(sorted(tie_sizes.items())),
           "metric": "INSIDE rate (bracket fit) — NOT realized R (no fills yet)",
           "verdict": ("DISTINGUISHABLE — revise RULES §7" if top_share >= 0.95
                       else "NOT DISTINGUISHABLE — winner varies, §7 confirmed")}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/bootstrap_winner.json", "w"), indent=2)
    print(f"\ntop winner share {top_share:.1%}; distinct winners {distinct_winners}; distinct orderings {len(winner_sets)}")
    print("VERDICT:", out["verdict"])


if __name__ == "__main__":
    main()
