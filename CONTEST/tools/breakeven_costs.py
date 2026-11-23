#!/usr/bin/env python3
"""breakeven_costs.py - breakeven trading cost per candidate."""
import json, math, ssl, sys, statistics as st
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
UA = {"User-Agent": "Mozilla/5.0 (breakeven_costs)"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UNIVERSE = ["AAPL","MSFT","AMZN","GOOG","META","TSLA","NVDA","JPM","V","UNH",
            "HD","PG","DIS","NFLX","ADBE","KO","PEP","COST","WMT","CSCO","TXN",
            "AVGO","QCOM","SPY"]
def fetch_monthly(sym, years=10):
    now = int(datetime.now(timezone.utc).timestamp())
    p1 = now - years * 365 * 86400
    p2 = now
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s"
           "?period1=%d&period2=%d&interval=1mo&events=div%%2Csplit" % (sym, p1, p2))
    req = urllib.request.Request(url, headers=UA)
    j = json.loads(urllib.request.urlopen(req, timeout=30, context=CTX).read().decode())
    res = j["chart"]["result"][0]
    ts = res["timestamp"]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose")
    close = res["indicators"]["quote"][0]["close"]
    out = []
    for t, a, c in zip(ts, adj, close):
        if a is not None:
            out.append((int(t), float(a)))
        elif c is not None:
            out.append((int(t), float(c)))
    out.sort()
    return out
def cagr(px_first, px_last, years):
    if years <= 0 or px_first <= 0 or px_last <= 0:
        return 0.0
    return (px_last / px_first) ** (1.0 / years) - 1.0
def annualize(monthly_returns):
    if not monthly_returns:
        return 0.0, 0.0
    m_mean = st.mean(monthly_returns)
    m_sd = st.pstdev(monthly_returns)
    return m_mean * 12.0, m_sd * math.sqrt(12.0)
def momentum_ls_monthly(px_at, times, syms):
    ls = []
    for i in range(13, len(times) - 1):
        mom = {}
        for sym in syms:
            p_now = px_at[sym][times[i - 1]]
            p_12 = px_at[sym][times[i - 13]]
            if p_now > 0 and p_12 > 0:
                mom[sym] = p_now / p_12 - 1.0
        if len(mom) < 5:
            continue
        ranked = sorted(mom.items(), key=lambda kv: kv[1])
        k = max(1, len(ranked) // 5)
        long_syms = [s for s, _ in ranked[-k:]]
        short_syms = [s for s, _ in ranked[:k]]
        long_ret = [px_at[s][times[i + 1]] / px_at[s][times[i]] - 1.0 for s in long_syms
                    if px_at[s][times[i]] > 0 and px_at[s][times[i + 1]] > 0]
        short_ret = [px_at[s][times[i + 1]] / px_at[s][times[i]] - 1.0 for s in short_syms
                     if px_at[s][times[i]] > 0 and px_at[s][times[i + 1]] > 0]
        if len(long_ret) < k // 2 or len(short_ret) < k // 2:
            continue
        ls.append(st.mean(long_ret) - st.mean(short_ret))
    return ls
def momentum_long_only_monthly(px_at, times, syms):
    out = []
    for i in range(13, len(times) - 1):
        mom = {}
        for sym in syms:
            p_now = px_at[sym][times[i - 1]]
            p_12 = px_at[sym][times[i - 13]]
            if p_now > 0 and p_12 > 0:
                mom[sym] = p_now / p_12 - 1.0
        if len(mom) < 5:
            continue
        ranked = sorted(mom.items(), key=lambda kv: kv[1])
        k = max(1, len(ranked) // 5)
        long_syms = [s for s, _ in ranked[-k:]]
        long_ret = [px_at[s][times[i + 1]] / px_at[s][times[i]] - 1.0 for s in long_syms
                    if px_at[s][times[i]] > 0 and px_at[s][times[i + 1]] > 0]
        if len(long_ret) < k // 2:
            continue
        out.append(st.mean(long_ret))
    return out
def main():
    series = {}
    failed = []
    for sym in UNIVERSE:
        try:
            series[sym] = fetch_monthly(sym)
        except Exception as e:
            failed.append((sym, str(e)[:80]))
            continue
    if len(series) < 5:
        print("FATAL: could not build universe (got %d symbols): %s" % (len(series), failed), file=sys.stderr)
        sys.exit(1)
    common = None
    for sym, rows in series.items():
        s = set(t for t, _ in rows)
        common = s if common is None else (common & s)
    times = sorted(common)
    n = len(times)
    px_at = {sym: dict(rows) for sym, rows in series.items()}
    syms = [s for s in UNIVERSE if s in series]
    years = n / 12.0
    candidates = []
    spy_px = [px_at["SPY"][t] for t in times]
    spy_gross = cagr(spy_px[0], spy_px[-1], years)
    candidates.append({
        "name": "SPY buy-and-hold",
        "gross_ann_pct": round(spy_gross * 100, 3),
        "round_trips_per_year": 0.5,
        "note": "buy once, hold ~10 yrs; turnover ~0 so breakeven not binding",
    })
    ls = momentum_ls_monthly(px_at, times, syms)
    ls_ann, _ = annualize(ls)
    candidates.append({
        "name": "12-1 momentum long-short quintile",
        "gross_ann_pct": round(ls_ann * 100, 3),
        "round_trips_per_year": 12.0,
        "note": "full long+short reconstitution monthly",
    })
    lon = momentum_long_only_monthly(px_at, times, syms)
    lon_ann, _ = annualize(lon)
    candidates.append({
        "name": "12-1 momentum long-only top quintile",
        "gross_ann_pct": round(lon_ann * 100, 3),
        "round_trips_per_year": 12.0,
        "note": "top quintile only, monthly reconstitution",
    })
    rows = []
    for c in candidates:
        gross = c["gross_ann_pct"] / 100.0
        rt = c["round_trips_per_year"]
        if gross <= 0:
            be_bps = 0.0
            be_pct = 0.0
            be_note = "gross already <= 0 (net-negative at zero cost)"
        else:
            be_cost = gross / rt
            be_bps = be_cost * 10000.0
            be_pct = be_cost * 100.0
            be_note = None
        rows.append({
            "name": c["name"],
            "gross_ann_pct": c["gross_ann_pct"],
            "round_trips_per_year": rt,
            "breakeven_cost_per_round_trip_bps": round(be_bps, 2),
            "breakeven_cost_per_round_trip_pct": round(be_pct, 3),
            "net_at_1bp_pct": round((gross - 0.0001 * rt) * 100, 3),
            "net_at_5bp_pct": round((gross - 0.0005 * rt) * 100, 3),
            "net_at_10bp_pct": round((gross - 0.0010 * rt) * 100, 3),
            "note": be_note or c["note"],
        })
    out = {
        "universe": syms,
        "n_symbols": len(syms),
        "n_months": n,
        "years": round(years, 2),
        "method": "breakeven cost per round trip (bps) = gross annual expectancy (bps) / round trips per year; net = gross - cost(bps)*round trips/10000",
        "rows": rows,
    }
    Path("reports").mkdir(parents=True, exist_ok=True)
    Path("reports/breakeven_costs.json").write_text(json.dumps(out, indent=2) + "\n")
    print("universe: %d symbols, %d months (%.1f yrs)" % (len(syms), n, years))
    print("%-38s %12s %14s %18s %11s %11s %11s" % (
        "candidate", "gross %/yr", "round trips/yr", "breakeven bps/rt", "net @1bp", "net @5bp", "net @10bp"))
    print("-" * 110)
    for r in rows:
        print("%-38s %12.3f %14.1f %18.2f %11.3f %11.3f %11.3f  %s" % (
            r["name"], r["gross_ann_pct"], r["round_trips_per_year"],
            r["breakeven_cost_per_round_trip_bps"],
            r["net_at_1bp_pct"], r["net_at_5bp_pct"], r["net_at_10bp_pct"], r["note"]))
if __name__ == "__main__":
    main()
