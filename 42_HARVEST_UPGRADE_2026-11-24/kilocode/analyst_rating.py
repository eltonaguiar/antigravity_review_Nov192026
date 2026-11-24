#!/usr/bin/env python3
"""Rate analysts on two axes: reliability (hit rate, CI-adjusted) and magnitude
(expectancy / payoff), plus specialisation and consistency.

Demo profiles:
  A: BTCUSDT 1-week specialist, 97.6% hit rate, tiny wins / rare big loss
  B: generalist, 49.4% hit rate, large wins / small losses, huge P/L
Run: python3 analyst_rating.py [--json out.json]
"""
import argparse, json, math, random, statistics

Z = 1.96


def wilson_lb(wins, n, z=Z):
    if n == 0: return None
    p = wins / n
    den = 1 + z*z/n
    centre = p + z*z/(2*n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (centre - half) / den


def boot_ci(vals, iters=3000, seed=3):
    if len(vals) < 3: return (None, None, None)
    rnd = random.Random(seed); n = len(vals); ms = []
    for _ in range(iters):
        ms.append(sum(vals[rnd.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return statistics.mean(vals), ms[int(0.025*iters)], ms[int(0.975*iters)]


def metrics(trades):
    rets = [t["ret_pct"]/100 for t in trades]
    n = len(rets); wins = [r for r in rets if r > 0]; losses = [r for r in rets if r <= 0]
    hit = len(wins)/n if n else None
    avg_w = statistics.mean(wins) if wins else 0
    avg_l = abs(statistics.mean(losses)) if losses else 0
    pf = (sum(wins)/abs(sum(losses))) if losses and sum(losses) != 0 else None
    m, lo, hi = boot_ci(rets)
    eq = 1.0; peak = 1.0; mdd = 0.0
    for r in rets:
        eq *= (1+0.01*r); peak = max(peak, eq); mdd = min(mdd, eq/peak-1)
    h = n//2
    e1, _, _ = boot_ci(rets[:h]); e2, _, _ = boot_ci(rets[h:])
    hit_lb = wilson_lb(len(wins), n)
    exp_worst = (hit_lb*avg_w + (1-hit_lb)*(-avg_l)) if hit_lb is not None else None
    return {"n": n, "hit_rate": hit, "wilson_lb": wilson_lb(len(wins), n),
            "mean_ret_pct": (m*100 if m is not None else None),
            "mean_ci_low_pct": (lo*100 if lo is not None else None),
            "mean_ci_high_pct": (hi*100 if hi is not None else None),
            "avg_win_pct": avg_w*100, "avg_loss_pct": -avg_l*100,
            "payoff": (avg_w/avg_l if avg_l else None), "profit_factor": pf,
            "total_return_pct": (eq-1)*100, "max_drawdown_pct": mdd*100,
            "expectancy_worst_pct": (exp_worst*100 if exp_worst is not None else None),
            "half1_positive": bool(e1 is not None and e1 > 0),
            "half2_positive": bool(e2 is not None and e2 > 0)}


def score(m):
    if not m["n"]:
        return {"score": None, "rating": "NO_DATA"}
    rel = (m["wilson_lb"] or 0) * 40
    mag = 0 if m["mean_ci_low_pct"] is None else 30 / (1 + math.exp(-m["mean_ci_low_pct"]/0.75))
    pay = min(m.get("profit_factor") or 0, 3) / 3 * 15
    cons = 10 if (m["half1_positive"] and m["half2_positive"]) else 0
    samp = min(m["n"]/100, 1) * 5
    total = rel + mag + pay + cons + samp
    if (m.get("expectancy_worst_pct") or -1) <= 0:
        total = max(0, total - 15)   # a record that dies under the tail bound cannot rank high
    if (m["n"] >= 30 and (m.get("expectancy_worst_pct") or -1) > 0
            and (m["mean_ci_low_pct"] or -1) > 0):
        rating = "A_SURVIVES_STRESS"
    elif m["n"] >= 30 and (m["mean_ci_low_pct"] or -1) > 0:
        rating = "B_POSITIVE_BUT_TAIL_UNPROVEN"
    elif m["n"] < 30:
        rating = "INSUFFICIENT_N"
    else:
        rating = "WATCH"
    return {"score": round(total, 1), "rating": rating,
            "parts": {"reliability": round(rel,1), "magnitude": round(mag,1),
                      "payoff": round(pay,1), "consistency": cons, "sample": round(samp,1)}}


def demo():
    rnd = random.Random(11)
    A = [{"symbol":"BTCUSDT","horizon":"1w","direction":"long","ret_pct": 0.8} for _ in range(40)]
    A += [{"symbol":"BTCUSDT","horizon":"1w","direction":"long","ret_pct": -18.0}]
    B = [{"symbol":rnd.choice(["AAPL","MSFT","NVDA","SPY","BTCUSDT"]),"horizon":"3m",
          "direction":"long","ret_pct": rnd.choice([6.5,7,6,6.5,7])} for _ in range(247)]
    B += [{"symbol":rnd.choice(["AAPL","MSFT","NVDA","SPY","BTCUSDT"]),"horizon":"3m",
           "direction":"long","ret_pct": rnd.choice([-3.2,-3,-3.5,-3.2,-3])} for _ in range(253)]
    out = {}
    for name, trades in (("A_btc_specialist", A), ("B_generalist", B)):
        m = metrics(trades); out[name] = {"metrics": m, **score(m)}
        # specialisation: slice vs overall (slice == all here)
        out[name]["specialisation"] = {
            "slice": "BTCUSDT/1w/long" if name.startswith("A") else "all",
            "slice_n": len(trades),
            "tag": "SPECIALIST" if name.startswith("A") else "GENERALIST"}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json")
    a = ap.parse_args(); out = demo()
    print(json.dumps(out, indent=2))
    if a.json:
        open(a.json, "w").write(json.dumps(out, indent=2)+"\n")


if __name__ == "__main__":
    main()
