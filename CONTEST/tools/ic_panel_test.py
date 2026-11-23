#!/usr/bin/env python3
"""ic_panel_test.py — cross-sectional IC test (t ~ IC*sqrt(n)) showing panel power.

Each month, score every symbol by a signal (prior 12-month momentum, skipping the
most recent month to avoid short-term reversal) and pair it with the next month's
return. Two tests are run:

1. TIME-SERIES PANEL (proper): IC per period = Pearson(signal, forward return)
   across symbols. t = mean_IC * sqrt(n_periods) / sd(IC). This is the honest test
   because observations inside a period share the same forward-return month, so they
   are not independent; the effective sample is n_periods.

2. POOLED (naive upper bound): treat all symbol-period pairs as independent, compute
   one IC across all n_obs = symbols * periods pairs, t = IC * sqrt(n_obs).

The gap between (2) and (1) shows the power that naive pooling CLAIMS — but it is
illusory because within-period observations are correlated. The honest answer is the
time-series panel t from (1).

Data: real Yahoo Finance monthly adjusted close. Exits non-zero if the universe
cannot be built.
"""
import json, math, ssl, sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
UA = {"User-Agent": "Mozilla/5.0 (ic_panel_test)"}
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
def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)
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
    n_periods = len(times)
    px_at = {sym: dict(rows) for sym, rows in series.items()}
    syms = [s for s in UNIVERSE if s in series]
    n_symbols = len(syms)
    years = n_periods / 12.0

    # Per-period ICs (proper time-series panel) + all pooled signal/forward pairs
    ics = []; period_labels = []; n_per_period = []
    pooled_sig = []; pooled_fwd = []
    for i in range(13, n_periods - 1):
        sig = []; fwd = []; used = 0
        for sym in syms:
            p_now = px_at[sym][times[i - 1]]
            p_12 = px_at[sym][times[i - 13]]
            p_next = px_at[sym][times[i + 1]]
            p_cur = px_at[sym][times[i]]
            if p_now > 0 and p_12 > 0 and p_next > 0 and p_cur > 0:
                v_sig = p_now / p_12 - 1.0
                v_fwd = p_next / p_cur - 1.0
                sig.append(v_sig); fwd.append(v_fwd)
                pooled_sig.append(v_sig); pooled_fwd.append(v_fwd)
                used += 1
        if used < 5:
            continue
        ic = pearson(sig, fwd)
        if ic != ic:
            continue
        ics.append(ic); period_labels.append(datetime.utcfromtimestamp(times[i]).strftime("%Y-%m")); n_per_period.append(used)
    if len(ics) < 2:
        print("FATAL: only %d periods with valid IC; need >= 2" % len(ics), file=sys.stderr)
        sys.exit(1)
    n_ic = len(ics)
    mean_ic = sum(ics) / n_ic
    sd_ic = math.sqrt(sum((ic - mean_ic) ** 2 for ic in ics) / n_ic)
    se_ic = sd_ic / math.sqrt(n_ic)
    t_panel = mean_ic / se_ic if se_ic else 0.0
    hit_rate = sum(1 for ic in ics if ic > 0) / n_ic
    t_single_equiv = mean_ic * math.sqrt(n_periods) / sd_ic if sd_ic else 0.0
    n_obs = sum(n_per_period)
    pooled_ic = pearson(pooled_sig, pooled_fwd)
    t_pooled = pooled_ic * math.sqrt(max(n_obs - 2, 1))
    power_gain_naive = (t_pooled / abs(t_panel)) if t_panel else float("inf")
    out = {
        "universe": syms,
        "n_symbols": n_symbols,
        "n_periods": n_periods,
        "years": round(years, 2),
        "n_ic_periods": n_ic,
        "n_observations": n_obs,
        "mean_ic": round(mean_ic, 4),
        "sd_ic": round(sd_ic, 4),
        "se_ic": round(se_ic, 4),
        "t_panel": round(t_panel, 2),
        "t_panel_significant": abs(t_panel) >= 2.0,
        "ic_hit_rate": round(hit_rate, 3),
        "t_single_series_equiv": round(t_single_equiv, 2),
        "pooled_ic": round(pooled_ic, 4),
        "t_pooled_naive": round(t_pooled, 2),
        "naive_pooling_t_power_gain": round(power_gain_naive, 2),
        "method": "panel IC/period = Pearson(signal, forward return) across symbols; t_panel = mean_IC*sqrt(n_periods)/sd(IC). pooled naive = one IC over all symbols*periods pairs, t = IC*sqrt(n_obs). Honest power is the panel t; naive pooling inflates it.",
        "ics": [round(v, 4) for v in ics],
        "periods": period_labels,
    }
    REPORTS_DIR = Path(__file__).resolve().parent / "reports"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "ic_panel_test.json").write_text(json.dumps(out, indent=2) + "\n")
    print("universe: %d symbols, %d months (%.1f yrs), %d valid IC periods" % (n_symbols, n_periods, years, n_ic))
    print("n_obs (symbols x periods) = %d" % n_obs)
    print("mean IC = %.4f   sd(IC) = %.4f   SE = %.4f" % (mean_ic, sd_ic, se_ic))
    print("panel t (time-series, n_periods) = %.2f  (%s)" % (t_panel, "SIGNIFICANT" if abs(t_panel) >= 2 else "not significant"))
    print("IC hit rate (positive IC months) = %.1f%%" % (hit_rate * 100))
    print("pooled naive IC = %.4f   t_pooled = %.2f  (t = IC*sqrt(n_obs))" % (pooled_ic, t_pooled))
    print("naive pooling claims %.1fx the panel t — illusory; within-period observations are correlated" % power_gain_naive)
    print("honest conclusion: the panel uses n_periods (%d), not n_obs (%d); cross-sectional breadth does not buy time-series power" % (n_periods, n_obs))
if __name__ == "__main__":
    main()
