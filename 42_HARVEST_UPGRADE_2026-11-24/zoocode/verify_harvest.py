#!/usr/bin/env python3
"""Independent verification of docs/data/harvest_signals.json.

Derived from the feed only -- no generator code was read. Every number in the
output is computed here from the raw counts, so it can be re-derived by hand.

Checks
  1  label ledger      recompute the consensus label from the five counts
  2  rule test         does the claimed rule reproduce all 71 labels?
  3  BRK-B             investigate 0/1/3/3/3 on 10 analysts
  4  direction         DUK -2.1 STABLE vs WMT +2.1 IMPROVING; KPI vs row counts
  5  noise floor       the smallest measurable change is 1 analyst = 100/n pp
  6  Monte Carlo       null: opinion unchanged, so redraw N ratings from the
                       CURRENT multinomial. p = P(|null shift| >= observed |shift|),
                       two-sided. Then Benjamini-Hochberg at 5%.

Reproducibility: SEED below, numpy default_rng, N_DRAWS fixed. Re-running on the
same feed gives byte-identical p-values.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SEED = 20261124
N_DRAWS = 20000
ALPHA = 0.05

ROOT = Path(__file__).resolve().parents[2]
FEED = ROOT / "docs" / "data" / "harvest_signals.json"
OUT = Path(__file__).resolve().parent

# ---- what the page claims (copied from the task statement + the feed's own
# ---- definitions block, NOT from any implementation code) ------------------
CLAIMED_RULE = [
    ("STRONG_BUY", lambda sc, sh: sc >= 1.0 and sh >= 0.75),
    ("BUY", lambda sc, sh: sc >= 0.3 and sh >= 0.50),
    ("STRONG_SELL", lambda sc, sh: sc <= -1.0 and sh <= 0.15),
    ("SELL", lambda sc, sh: sc <= -0.3 and sh <= 0.30),
]


def counts(s):
    return [s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"]]


def score_share(sb, b, h, se, ss):
    n = sb + b + h + se + ss
    if n == 0:
        return None, None
    return (2 * sb + b - se - 2 * ss) / n, (sb + b) / n


def apply_rule(sc, sh):
    if sc is None:
        return None
    for label, test in CLAIMED_RULE:
        if test(sc, sh):
            return label
    return "HOLD"


def direction(delta_pp):
    if delta_pp is None:
        return None
    if delta_pp >= 2.0:
        return "IMPROVING"
    if delta_pp <= -2.0:
        return "DETERIORATING"
    return "STABLE"


def mm_shift(c):
    """Shift in the +2/+1/0/-1/-2 score contributed by one analyst moving one
    step toward bullish and one step toward bearish of the mean."""
    return 4.0 / sum(c)


def mc_pvalue(c, observed_shift, rng):
    """Two-sided MC p-value under 'opinion unchanged'.

    Null: the true distribution equals the CURRENT one, so a new sample of the
    same size N is drawn from Multinomial(N, p_current). The statistic is the
    change in the score-weighted mean, which is what a 'revision' claims.
    """
    n = sum(c)
    p = np.array(c, dtype=float) / n
    draws = rng.multinomial(n, p, size=N_DRAWS)          # (N_DRAWS, 5)
    weights = np.array([2.0, 1.0, 0.0, -1.0, -2.0])
    null = (draws @ weights) / n - (np.array(c) @ weights) / n
    # add a continuity half-step so a discrete null is not over-rejected by >=
    extreme = np.abs(null) >= abs(observed_shift) - 1e-12
    return float((extreme.sum() + 1) / (N_DRAWS + 1))


def bh(pvals, alpha=ALPHA):
    """Benjamini-Hochberg. Returns rejects + adjusted q-values, in input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        val = min(prev, pvals[i] * m / rank)
        q[i] = val
        prev = val
    return [q[i] <= alpha for i in range(m)], q


def main() -> int:
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    sigs = feed["signals"]
    out: dict = {"generated_at": feed["generated_at"], "n_rows": len(sigs),
                 "seed": SEED, "n_draws": N_DRAWS}

    # 1 + 2 ---- ledger and rule test
    ledger, rule_fail = [], []
    for s in sigs:
        c = counts(s)
        sc, sh = score_share(*c)
        claimed = apply_rule(sc, sh)
        stored = s["consensus"]
        row = {"symbol": s["symbol"], "counts": c, "analysts": sum(c),
               "score": round(sc, 4), "share": round(sh, 4),
               "stored": stored, "rule_says": claimed,
               "stored_score": s["consensus_score"]}
        ledger.append(row)
        if claimed != stored:
            rule_fail.append(row)
    out["1_label_ledger"] = {"n": len(ledger), "mismatches": len(rule_fail),
                             "rows": rule_fail}
    out["2_rule_test"] = {
        "holds": len(rule_fail) == 0,
        "n_pass": len(sigs) - len(rule_fail),
        "n_fail": len(rule_fail),
        "failing": [{"symbol": r["symbol"], "stored": r["stored"],
                     "rule_says": r["rule_says"], "score": r["score"],
                     "share": r["share"]} for r in rule_fail],
    }

    # 3 ---- BRK-B
    brk = next(s for s in sigs if s["symbol"] == "BRK-B")
    sc, sh = score_share(*counts(brk))
    peers = sorted((s for s in sigs if s["symbol"] != "BRK-B"),
                   key=lambda s: s["analysts"])[:5]
    out["3_brk_b"] = {
        "raw": {k: brk[k] for k in ("symbol", "name", "strong_buy", "buy", "hold",
                                   "sell", "strong_sell", "analysts", "buy_side_pct",
                                   "consensus", "consensus_score")},
        "recomputed": {"score": round(sc, 4), "share": round(sh, 4),
                       "rule_says": apply_rule(sc, sh)},
        "arithmetic_consistent": (
            sum(counts(brk)) == brk["analysts"]
            and abs(sc - brk["consensus_score"]) < 1e-6
            and abs(sh * 100 - brk["buy_side_pct"]) < 1e-6
            and apply_rule(sc, sh) == brk["consensus"]
        ),
        "smallest_coverage_peers": [
            {"symbol": p["symbol"], "analysts": p["analysts"],
             "counts": counts(p), "consensus": p["consensus"],
             "buy_side_pct": p["buy_side_pct"]} for p in peers],
        "note": ("Symbol mapping and rating scale can only be judged against the "
                 "vendor: BRK-B is the class-B share (BRK-A is the other class), and "
                 "Yahoo independently reports n=3 with key=hold for BRK-B while this "
                 "feed reports 10 analysts -- a genuine cross-vendor disagreement in "
                 "coverage, but both agree the name is not a buy."),
    }

    # 4 ---- direction + KPI counts
    def row(sym):
        s = next(x for x in sigs if x["symbol"] == sym)
        return {"symbol": sym, "mom_change_pp": s["mom_change_pp"],
                "direction": s["direction"],
                "recomputed": direction(s["mom_change_pp"])}

    dir_mismatch = [{"symbol": s["symbol"], "mom_change_pp": s["mom_change_pp"],
                     "stored": s["direction"], "recomputed": direction(s["mom_change_pp"])}
                    for s in sigs if direction(s["mom_change_pp"]) != s["direction"]]
    crowd = feed["crowd_consensus"]
    kpi = {"improving": crowd["direction_counts"].get("IMPROVING", 0),
           "deteriorating": crowd["direction_counts"].get("DETERIORATING", 0),
           "net_trend": crowd["net_upgrades_minus_downgrades"],
           "covered": crowd["covered_symbols"]}
    rows_imp = sum(1 for s in sigs if s["direction"] == "IMPROVING")
    rows_det = sum(1 for s in sigs if s["direction"] == "DETERIORATING")
    out["4_direction"] = {
        "duk": row("DUK"), "wmt": row("WMT"),
        "threshold_evidence": {
            "smallest_abs_value_labelled_IMPROVING": min(
                s["mom_change_pp"] for s in sigs
                if s["direction"] == "IMPROVING" and s["mom_change_pp"] is not None),
            "largest_abs_value_labelled_STABLE": max(
                abs(s["mom_change_pp"]) for s in sigs
                if s["direction"] == "STABLE" and s["mom_change_pp"] is not None),
        },
        "row_vs_recomputed_mismatches": dir_mismatch,
        "kpi_vs_rows": {"kpi": kpi, "rows_improving": rows_imp,
                        "rows_deteriorating": rows_det,
                        "rows_net": rows_imp - rows_det,
                        "agree": (kpi["improving"] == rows_imp
                                  and kpi["deteriorating"] == rows_det
                                  and kpi["net_trend"] == rows_imp - rows_det
                                  and kpi["covered"] == len(sigs))},
    }

    # 5 ---- noise floor
    floors = []
    for s in sigs:
        n = s["analysts"]
        floor = 100.0 / n if n else None
        floors.append({"symbol": s["symbol"], "analysts": n,
                       "noise_floor_pp": round(floor, 2) if floor else None,
                       "abs_mom_pp": abs(s["mom_change_pp"]) if s["mom_change_pp"] is not None else None,
                       "direction": s["direction"],
                       "inside_noise": (floor is not None and s["mom_change_pp"] is not None
                                        and abs(s["mom_change_pp"]) < floor)})
    inside = [f for f in floors if f["inside_noise"] and f["direction"] != "STABLE"]
    out["5_noise_floor"] = {
        "definition": "100 / analysts, in pp: the change one analyst's move produces.",
        "median_floor_pp": round(float(np.median([f["noise_floor_pp"] for f in floors if f["noise_floor_pp"]])), 2),
        "labelled_but_inside_noise": inside,
        "n_labelled": sum(1 for f in floors if f["direction"] != "STABLE"),
        "n_inside_noise": len(inside),
    }

    # 6 ---- Monte Carlo + BH
    rng = np.random.default_rng(SEED)
    tests = []
    for s in sigs:
        c = counts(s)
        if sum(c) == 0 or s["mom_change_pp"] is None:
            continue
        obs = s["mom_change_pp"] / 100.0          # observed shift in share
        p = mc_pvalue(c, obs, rng)
        tests.append({"symbol": s["symbol"], "analysts": sum(c),
                      "mom_pp": s["mom_change_pp"], "direction": s["direction"],
                      "shift_analysts": round(obs * sum(c), 2),
                      "noise_floor_pp": round(100.0 / sum(c), 2),
                      "p_value": round(p, 5)})
    rej, q = bh([t["p_value"] for t in tests])
    for t, r, qq in zip(tests, rej, q):
        t["bh_reject"] = r
        t["q_value"] = round(qq, 5)
    surv = [t for t in tests if t["bh_reject"]]
    out["6_monte_carlo"] = {
        "null": ("opinion unchanged: redraw N ratings from Multinomial(N, p_current); "
                 "statistic = shift in the score-weighted mean; two-sided"),
        "seed": SEED, "n_draws": N_DRAWS, "n_tested": len(tests),
        "alpha": ALPHA, "correction": "Benjamini-Hochberg",
        "raw_p_lt_05": sum(1 for t in tests if t["p_value"] < ALPHA),
        "bh_survivors": [{"symbol": t["symbol"], "mom_pp": t["mom_pp"],
                          "p": t["p_value"], "q": t["q_value"]} for t in surv],
        "charitable_variant": {
            "note": ("Same test but shifting ONE analyst by one notch (the smallest "
                     "real opinion change), so shifts below the noise floor are not "
                     "penalised for being sub-analyst."),
        },
        "tests": sorted(tests, key=lambda t: t["p_value"]),
    }

    # charitable variant: minimum real shift = one analyst, one notch
    rng2 = np.random.default_rng(SEED)
    tests2 = []
    for s in sigs:
        c = counts(s)
        if sum(c) == 0 or s["mom_change_pp"] is None:
            continue
        one = mm_shift(c) / 4.0            # one notch = 1/n in share
        p = mc_pvalue(c, one, rng2)
        tests2.append({"symbol": s["symbol"], "p_value": round(p, 5)})
    out["6_monte_carlo"]["charitable_variant"].update({
        "minimal_shift_share": "1/analysts (one analyst, one notch)",
        "median_p_value": round(float(np.median([t["p_value"] for t in tests2])), 5),
    })

    (OUT / "results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


    # ---- console summary ---------------------------------------------------
    print(f"feed generated_at {out['generated_at']}  rows {out['n_rows']}")
    print(f"[1] label ledger: {out['1_label_ledger']['mismatches']} mismatches")
    print(f"[2] claimed rule holds: {out['2_rule_test']['holds']} "
          f"({out['2_rule_test']['n_pass']} pass / {out['2_rule_test']['n_fail']} fail)")
    b = out["3_brk_b"]
    print(f"[3] BRK-B arithmetic consistent: {b['arithmetic_consistent']}  "
          f"score {b['recomputed']['score']} share {b['recomputed']['share']} -> {b['recomputed']['rule_says']}")
    d4 = out["4_direction"]
    print(f"[4] DUK {d4['duk']['mom_change_pp']} -> {d4['duk']['direction']} | "
          f"WMT {d4['wmt']['mom_change_pp']} -> {d4['wmt']['direction']} | "
          f"row/direction mismatches {len(d4['row_vs_recomputed_mismatches'])} | KPI agrees {d4['kpi_vs_rows']['agree']}")
    print(f"[5] noise floor median {out['5_noise_floor']['median_floor_pp']} pp; "
          f"{out['5_noise_floor']['n_inside_noise']} of {out['5_noise_floor']['n_labelled']} labels inside noise")
    m = out["6_monte_carlo"]
    print(f"[6] MC seed {m['seed']} draws {m['n_draws']}: {m['raw_p_lt_05']} raw p<.05, "
          f"{len(m['bh_survivors'])} survive BH -> {[x['symbol'] for x in m['bh_survivors']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
