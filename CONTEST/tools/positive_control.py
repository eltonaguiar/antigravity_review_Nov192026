#!/usr/bin/env python3
"""positive_control.py — can the audit's gate RECOVER a known injected alpha?

POWER_ANALYSIS.md §5 names its own deepest defect: "there is no positive control."
This supplies it. We take REAL SPY monthly adjusted returns, remove their drift so the
0% case is a true null (mean≈0) while keeping the real month-to-month dispersion and
tails, then inject a known alpha of 0%, 1%, 2%, 3% per year (and 10% as a harness
sanity check). We run the SAME gate as power_analysis.py:

    SE(mean annual return) = vol / sqrt(years)
    t = mean / SE ;  significant iff |t| >= 2   (== 95% CI excludes 0)
    MDE(t=2) = 2 * vol / sqrt(years)

Correct outcome: 0% -> nothing (null honoured); 1/2/3% -> recovered at the RIGHT magnitude,
and SIGNIFICANT only if above the sample's MDE; 10% -> significant (proves the harness
is not simply broken). If 3%/yr is NOT recovered at this sample length, that is the power
statement, quantified on the same data the audit used.

Data: SPY monthly adjusted close from Yahoo (same source as dca_vs_lumpsum.py); falls back
to the local adjusted-close CSV (shorter, fewer years) with a printed warning.
"""
import json, math, statistics as st
from pathlib import Path
import sys

Z = 1.96
T_CRIT = 2.0


def se(vol, years):
    return vol / math.sqrt(years)


def ci95(mean, vol, years, z=Z):
    s = se(vol, years)
    return mean - z * s, mean + z * s


def mde(vol, years, t=T_CRIT):
    return t * vol / math.sqrt(years)


def load_spy_monthly():
    """Return list of monthly simple returns (decimals). Yahoo first, local CSV fallback."""
    try:
        import urllib.request, ssl
        UA = {"User-Agent": "Mozilla/5.0 (positive_control)"}
        ctx = ssl.create_default_context()
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/SPY"
               "?period1=725846400&period2=1795000000&interval=1mo&events=div%2Csplit")
        j = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=40, context=ctx).read().decode())
        res = j["chart"]["result"][0]
        adj = res["indicators"]["adjclose"][0]["adjclose"]
        px = [a for a in adj if a is not None]
        if len(px) > 120:
            return [px[i] / px[i - 1] - 1 for i in range(1, len(px))], "yahoo-monthly", len(px)
    except Exception as e:
        print(f"[warn] Yahoo fetch failed ({str(e)[:60]}); using local CSV", file=sys.stderr)
    # fallback: local daily SPY adjusted -> monthly
    import csv
    cand = Path("2026-11-15_AM_profitability-plan/copilot-financial-review/market_prices.csv")
    if not cand.exists():
        cand = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw/" + str(cand))
    rows = list(csv.DictReader(open(cand)))
    px, last = [], None
    for r in rows:
        try:
            v = float(r["SPY_adj"])
        except Exception:
            continue
        # crude monthly resample: take last obs of each YYYY-MM
        d = r["date"][:7]
        if last and d != last:
            px.append(prev)
        prev = v; last = d
    px.append(prev)
    return [px[i] / px[i - 1] - 1 for i in range(1, len(px))], "local-csv-monthly", len(px)


def diagnose(returns_monthly, injected_ann):
    """Demean real returns (true null), inject alpha/12/month, run the power gate."""
    n = len(returns_monthly)
    base = [r - st.mean(returns_monthly) for r in returns_monthly]  # zero-mean, real dispersion
    add = injected_ann / 12.0
    y = [b + add for b in base]
    years = n / 12.0
    ann_mean = st.mean(y) * 12.0
    ann_vol = st.pstdev(y) * math.sqrt(12.0)
    s = se(ann_vol, years)
    t = ann_mean / s if s else 0.0
    lo, hi = ci95(ann_mean, ann_vol, years)
    sig = abs(t) >= T_CRIT and (lo > 0 or hi < 0)
    return {"injected_ann_pct": round(injected_ann * 100, 3),
            "recovered_ann_pct": round(ann_mean * 100, 3),
            "ann_vol_pct": round(ann_vol * 100, 2), "years": round(years, 1),
            "se_pct": round(s * 100, 3), "t": round(t, 2),
            "ci95_pct": [round(lo * 100, 2), round(hi * 100, 2)],
            "significant": sig}


def main():
    rets, src, npx = load_spy_monthly()
    injections = [0.0, 0.01, 0.02, 0.03, 0.10]  # 0 null, 1/2/3%, 10% harness-sanity
    rows = [diagnose(rets, a) for a in injections]
    vol = rows[0]["ann_vol_pct"]
    years = rows[0]["years"]
    mde_here = mde(rows[0]["ann_vol_pct"] / 100, years) * 100
    out = {"source": src, "price_obs": npx, "spy_monthly_returns": len(rets),
           "spy_ann_vol_pct": vol, "years": years, "mde_t2_pct": round(mde_here, 2),
           "gate": "SE=vol/sqrt(T); t=mean/SE; significant iff |t|>=2", "rows": rows}
    Path("reports/positive_control.json").parent.mkdir(parents=True, exist_ok=True)
    Path("reports/positive_control.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"source={src} months={len(rets)} years={years} SPY vol={vol}% MDE(t=2)={mde_here:.2f}%/yr")
    print(f"{'injected/yr':>12}{'recovered/yr':>14}{'vol':>8}{'SE':>8}{'t':>7}{'95% CI':>20}{'sig?':>7}")
    for r in rows:
        print(f"{r['injected_ann_pct']:>11.2f}%{r['recovered_ann_pct']:>13.2f}%{r['ann_vol_pct']:>7.1f}%"
              f"{r['se_pct']:>7.2f}%{r['t']:>7.2f}   [{r['ci95_pct'][0]:+.2f},{r['ci95_pct'][1]:+.2f}]  {str(r['significant']):>6}")


if __name__ == "__main__":
    main()
