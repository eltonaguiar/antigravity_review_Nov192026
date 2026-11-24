#!/usr/bin/env python3
"""PROVEIT — VERIFY the '5-pt drift band' rebalancing claim in MANAGED_PORTFOLIO_ALERTS.
Compare 60/40 SPY/BND: monthly, annual, +/-5pt band, +/-10pt band, and never rebalancing.
Reports CAGR, max drawdown, excess-of-cash Sharpe, and rebalance count. Total-return adjusted prices."""
import csv, json, math, statistics as st
from datetime import datetime, timezone
from pathlib import Path

F = Path(__file__).parent / "data/market_prices.csv"


def load():
    rows = list(csv.DictReader(open(F)))
    spy = [float(r["SPY_adj"]) for r in rows if r["SPY_adj"] not in ("", "NA")]
    bnd = [float(r["BND_adj"]) for r in rows if r["BND_adj"] not in ("", "NA")]
    cash = [float(r["SGOV_adj"]) for r in rows if r["SGOV_adj"] not in ("", "NA")]
    n = min(len(spy), len(bnd), len(cash))
    return spy[:n], bnd[:n], cash[:n]


def mdd(eq):
    pk = eq[0]; m = 0.0
    for v in eq:
        pk = max(pk, v); m = min(m, v / pk - 1)
    return m


def run(spy, bnd, cash, rule, band=0.05, reb=21):
    eq = [1.0]; sv = {"s": 0.6, "b": 0.4}; cnt = 0; day = 0
    for i in range(1, len(spy)):
        day += 1
        sv["s"] *= spy[i] / spy[i - 1]; sv["b"] *= bnd[i] / bnd[i - 1]
        tot = sv["s"] + sv["b"]; eq.append(tot)
        we = sv["s"] / tot
        do = (rule == "monthly" and day >= reb) or (rule == "annual" and day >= 252) or (rule == "band" and abs(we - 0.6) >= band)
        if do and rule != "never":
            sv = {"s": 0.6 * tot, "b": 0.4 * tot}; cnt += 1; day = 0
    yrs = len(eq) / 252.0
    r = [eq[i] / eq[i - 1] - 1 for i in range(1, len(eq))]
    rc = [cash[i] / cash[i - 1] - 1 for i in range(1, len(cash))]
    n = min(len(r), len(rc)); ex = [r[i] - rc[i] for i in range(n)]
    mu = st.mean(ex); sd = st.pstdev(ex)
    return {"cagr_pct": round((eq[-1] ** (1 / yrs) - 1) * 100, 2),
            "dd_pct": round(mdd(eq) * 100, 2),
            "sharpe": round(mu / sd * math.sqrt(252), 3) if sd else 0.0,
            "rebalances": cnt}


def main():
    spy, bnd, cash = load()
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "buyhold_equity_cagr_pct": round(((spy[-1] / spy[0]) ** (252 / len(spy)) - 1) * 100, 2),
           "rules": {}}
    out["rules"]["monthly"] = run(spy, bnd, cash, "monthly", reb=21)
    out["rules"]["annual"] = run(spy, bnd, cash, "annual")
    out["rules"]["band_5pt"] = run(spy, bnd, cash, "band", band=0.05)
    out["rules"]["band_10pt"] = run(spy, bnd, cash, "band", band=0.10)
    out["rules"]["never"] = run(spy, bnd, cash, "never")
    Path(__file__).parent.joinpath(f"REBALANCE_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%MZ')}.json").write_text(json.dumps(out, indent=2) + "\n")
    print("buy&hold equity CAGR%:", out["buyhold_equity_cagr_pct"])
    for k, v in out["rules"].items():
        print(f"  60/40 {k}:", v)


if __name__ == "__main__":
    main()
