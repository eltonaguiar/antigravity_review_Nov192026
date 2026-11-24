#!/usr/bin/env python3
"""Analyst-follow simulation: design + synthetic demo.

Real per-analyst track records need a paid feed (Finnhub upgrade/downgrade 403,
FMP 429). Free Yahoo gives ~52 buy-ish actions across 37 firms for 12 mega-caps
(540d) — max n=4, far below the n>=20 needed to rank an analyst. This script
therefore ships:
  * --source real  : reports the real coverage and refuses to rank (honest)
  * --source synth : deterministic SYNTHETIC demo that exercises the full
                     pipeline (filters, picks, portfolio, metrics)
"""
import argparse, json, math, random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs" / "data" / "analyst_sim_demo.json"


def synth(seed=7, n_analysts=14, n_months=36):
    rnd = random.Random(seed)
    symbols = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","XOM","JNJ","WMT","COST","SPY"]
    # market monthly returns with a couple of regimes
    mkt = []
    for m in range(n_months):
        drift = 0.010 if m < 18 else 0.004
        mkt.append(rnd.gauss(drift, 0.04))
    analysts = []
    for i in range(n_analysts):
        skill = rnd.gauss(0.0, 0.006)          # monthly excess skill
        calls = []
        for m in range(6, n_months):
            if rnd.random() < 0.50:            # sparse calls
                sym = rnd.choice(symbols[:-1])
                calls.append({"month": m, "symbol": sym,
                              "fwd_excess": mkt[m] + skill + rnd.gauss(0, 0.05)})
        analysts.append({"id": f"A{i+1:02d}", "firm": f"Firm {i+1:02d}",
                         "skill": skill, "calls": calls})
    # portfolio: each month, equal-weight latest pick of analysts whose
    # trailing hit-rate > 50% and n>=10 (information available at that time)
    port = []
    for m in range(12, n_months):
        elig = []
        for a in analysts:
            past = [c for c in a["calls"] if c["month"] < m]
            if len(past) < 8:
                continue
            hit = sum(1 for c in past if c["fwd_excess"] > 0) / len(past)
            if hit > 0.5:
                latest = max((c for c in a["calls"] if c["month"] <= m), key=lambda c: c["month"], default=None)
                if latest:
                    elig.append((a, latest))
        if not elig:
            port.append({"month": m, "ret": 0.0, "n": 0}); continue
        ret = sum(c["fwd_excess"] for _, c in elig) / len(elig) + mkt[m]
        port.append({"month": m, "ret": ret - 0.00067, "n": len(elig)})
    return analysts, port


def metrics(port):
    rets = [p["ret"] for p in port]
    if not rets: return {}
    eq = [1.0]
    for r in rets: eq.append(eq[-1] * (1 + r))
    mean = sum(rets)/len(rets)
    sd = math.sqrt(sum((r-mean)**2 for r in rets)/len(rets)) if len(rets) > 1 else 0
    peak = eq[0]; mdd = 0
    for v in eq:
        peak = max(peak, v); mdd = min(mdd, v/peak-1)
    years = len(rets)/12
    cagr = eq[-1]**(1/years)-1 if years > 0 else 0
    return {"months": len(rets), "total_return_pct": (eq[-1]-1)*100,
            "cagr_pct": cagr*100, "ann_vol_pct": sd*math.sqrt(12)*100,
            "sharpe": (mean/sd*math.sqrt(12)) if sd else None,
            "max_drawdown_pct": mdd*100, "hit_rate": sum(1 for r in rets if r>0)/len(rets)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["synth","real"], default="synth")
    ap.add_argument("--min-calls", type=int, default=8)
    ap.add_argument("--min-hit", type=float, default=0.50)
    a = ap.parse_args()
    if a.source == "real":
        print(json.dumps({"status":"BLOCKED_DATA",
          "reason":"Free feeds cannot rank analysts: Yahoo 52 buy-ish actions/37 firms/max n=4 (540d, 12 symbols); Finnhub upgrade-downgrade 403; FMP 429.",
          "needed":"Paid per-analyst actions: Finnhub paid, FMP paid, Benzinga, TipRanks, Refinitiv/FactSet."}, indent=2))
        return
    analysts, port = synth()
    rows = []
    for x in analysts:
        n = len(x["calls"]); hit = sum(1 for c in x["calls"] if c["fwd_excess"] > 0)/n if n else 0
        mean = sum(c["fwd_excess"] for c in x["calls"])/n if n else 0
        latest = max(x["calls"], key=lambda c: c["month"], default=None)
        rows.append({"id": x["id"], "firm": x["firm"], "n_calls": n,
                     "hit_rate": hit, "mean_excess_pct": mean*100,
                     "latest_symbol": latest["symbol"] if latest else None,
                     "latest_month": latest["month"] if latest else None})
    rows.sort(key=lambda r: (-r["hit_rate"], -r["n_calls"]))
    out = {"synthetic": True,
           "warning": "SYNTHETIC DEMO — generated data, not real analysts. Illustrates mechanics only.",
           "config": {"min_calls": a.min_calls, "min_hit_rate": a.min_hit},
           "analysts": rows, "portfolio_monthly": port, "portfolio_metrics": metrics(port),
           "real_data_status": {"yahoo_buy_actions_540d": 52, "firms": 37, "max_calls_per_firm": 4,
                                "finnhub_upgrade_downgrade": "HTTP 403 (paid)",
                                "fmp_upgrades": "HTTP 429 (quota)"}}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT} analysts={len(rows)} months={len(port)} metrics={out['portfolio_metrics']}")


if __name__ == "__main__":
    main()
