#!/usr/bin/env python3
"""momentum_gross.py — second positive control: 12-1 momentum GROSS of costs.

Classic 12-1 momentum (Jegadeesh & Titman / Carhart):
  formation = 12-month return ending one month ago  (skip the most recent month
              to avoid short-term reversal / microstructure),
  holding   = the following calendar month.
Each month-end, rank the universe by formation momentum into quintiles, go long
the top quintile and short the bottom quintile (equal weight), hold one month,
then re-rank. Report the long-short GROSS return (no transaction costs, no
borrow, no slippage) and its t-stat.

Reading:
  momentum gross > 0 and significant  -> the harness recovers a known anomaly,
                                          so it can be trusted on this sample.
  momentum gross ~= 0 / not significant -> power statement: either the sample is
                                          too short/noisy, or the harness cannot
                                          recover what it claims to test.

Data: Yahoo Finance monthly adjusted close (dividends/splits adjusted).
No fabricated output: exits non-zero if the universe cannot be built.
"""
import json, math, ssl, sys, statistics as st
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (momentum_gross positive control)"}
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
    print("universe: %d symbols, %d common months, %d skipped: %s"
          % (len(series), n, len(failed), [s for s, _ in failed]))
    if n < 40:
        print("FATAL: only %d common months; need >= 40" % n, file=sys.stderr)
        sys.exit(1)
    px_at = {sym: dict(rows) for sym, rows in series.items()}
    syms = [s for s in UNIVERSE if s in series]
    ls_returns, long_legs, short_legs = [], [], []
    formation_months = 0
    for i in range(13, n - 1):
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
        lr = st.mean(long_ret); sr = st.mean(short_ret)
        ls_returns.append(lr - sr); long_legs.append(lr); short_legs.append(sr)
        formation_months += 1
    if not ls_returns:
        print("FATAL: no holding months produced", file=sys.stderr)
        sys.exit(1)
    m_mean = st.mean(ls_returns); m_sd = st.pstdev(ls_returns); n_m = len(ls_returns)
    ann_mean = m_mean * 12.0
    ann_vol = m_sd * math.sqrt(12.0)
    ann_se = ann_vol / math.sqrt(n_m / 12.0)
    t = ann_mean / ann_se if ann_se else 0.0
    hit = sum(1 for r in ls_returns if r > 0) / n_m
    long_mean = st.mean(long_legs) * 12.0
    short_mean = st.mean(short_legs) * 12.0
    spy = [px_at["SPY"][t] for t in times]
    spy_years = n / 12.0
    spy_cagr = (spy[-1] / spy[0]) ** (1.0 / spy_years) - 1.0 if spy_years > 0 else 0.0
    out = {
        "symbols": syms, "n_symbols": len(syms), "n_months": n,
        "formation_months": formation_months, "skipped": failed,
        "ls_gross_monthly_mean_pct": round(m_mean * 100, 4),
        "ls_gross_annualized_pct": round(ann_mean * 100, 3),
        "ls_gross_ann_vol_pct": round(ann_vol * 100, 2),
        "ls_gross_t": round(t, 2),
        "ls_gross_hit_rate": round(hit, 3),
        "long_leg_ann_pct": round(long_mean * 100, 2),
        "short_leg_ann_pct": round(short_mean * 100, 2),
        "spy_cagr_pct": round(spy_cagr * 100, 2),
        "months": [datetime.utcfromtimestamp(t).strftime("%Y-%m") for t in times],
        "ls_monthly_pct": [round(r * 100, 4) for r in ls_returns],
    }
    Path("CONTEST/tools/reports").mkdir(parents=True, exist_ok=True)
    Path("CONTEST/tools/reports/momentum_gross.json").write_text(json.dumps(out, indent=2) + "\n")
    sig = abs(t) >= 2.0
    print("12-1 momentum GROSS of costs — %d formation months, %d symbols, %d common months"
          % (formation_months, len(syms), n))
    print("long-short gross: %.3f%%/yr  vol %.2f%%/yr  t=%.2f  hit=%.0f%%  %s"
          % (ann_mean * 100, ann_vol * 100, t, hit * 100, "SIGNIFICANT" if sig else "not significant"))
    print("long leg %.2f%%/yr | short leg %.2f%%/yr | SPY CAGR %.2f%%/yr over window"
          % (long_mean, short_mean, spy_cagr * 100))
    print("verdict: %s" % ("HARNESS RECOVERS KNOWN ANOMALY (momentum gross > 0, significant)"
                           if (ann_mean > 0 and sig) else "POWER STATEMENT (momentum gross not recovered as significant)"))

if __name__ == "__main__":
    main()
