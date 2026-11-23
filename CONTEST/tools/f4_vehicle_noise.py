"""Falsification test for F4: is "an index fund beats its own ETF" a vehicle effect or noise?

The reviewer's structural criticism: if the measured gap is much larger than the fee gap, then either the
vehicles do not track the same index identically (sampling vs full replication, securities lending, share
class) or the difference is sampling error. The decisive cheap test is to compare the fund-vs-ETF gap with
the spread ACROSS several ETFs that all track the same index. If ETF-to-ETF spread is comparable, the claim
is about vehicle noise, not a fund edge.

Uses Yahoo adjusted close (dividends reinvested) so returns are total return.
"""
import json, ssl, urllib.request, datetime

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

# symbol -> (label, expense ratio %)
VEH = {
    "FXAIX": ("Fidelity 500 Index (MF)", 0.015),
    "VFIAX": ("Vanguard 500 Admiral (MF)", 0.040),
    "SPY":   ("SPDR S&P 500 ETF", 0.0945),
    "VOO":   ("Vanguard S&P 500 ETF", 0.030),
    "IVV":   ("iShares Core S&P 500 ETF", 0.030),
}


def series(sym):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=6y&interval=1d"
           "&events=div%%2Csplit" % sym)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    res = j["chart"]["result"][0]
    ts = res["timestamp"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    out = {}
    for t, a in zip(ts, adj):
        if a is None:
            continue
        d = datetime.datetime.utcfromtimestamp(t).date().isoformat()
        out[d] = float(a)
    return out


data = {}
for s in VEH:
    try:
        data[s] = series(s)
        ds = sorted(data[s])
        print("  %-6s %5d obs  %s .. %s" % (s, len(ds), ds[0], ds[-1]))
    except Exception as e:
        print("  %-6s FAILED %s" % (s, str(e)[:70]))

# common window across all
common = sorted(set.intersection(*[set(v) for v in data.values()]))
print("\ncommon window: %s .. %s  (%d sessions, %.2f years)"
      % (common[0], common[-1], len(common), len(common) / 252.0))

def stats(s):
    px = [data[s][d] for d in common]
    yrs = len(px) / 252.0
    cagr = (px[-1] / px[0]) ** (1 / yrs) - 1
    rets = [px[i] / px[i - 1] - 1 for i in range(1, len(px))]
    mu = sum(rets) / len(rets)
    sd = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5
    sharpe = (mu / sd) * (252 ** 0.5) if sd else 0.0
    peak = px[0]; mdd = 0.0
    for p in px:
        peak = max(peak, p)
        mdd = min(mdd, p / peak - 1)
    return cagr, sd * (252 ** 0.5), sharpe, mdd

S = {s: stats(s) for s in data}
print("\n%-6s %-30s %9s %9s %8s %9s %7s" % ("sym", "vehicle", "CAGR", "vol", "Sharpe", "maxDD", "ER%"))
for s in data:
    c, v, sh, m = S[s]
    print("%-6s %-30s %8.3f%% %8.3f%% %8.3f %8.2f%% %7.4f"
          % (s, VEH[s][0], c * 100, v * 100, sh, m * 100, VEH[s][1]))

print("\npairwise annualised return differences (bp/yr) — positive means row beat column")
print("%-6s %s" % ("", " ".join("%8s" % x for x in data)))
for a in data:
    cells = []
    for b in data:
        cells.append("%+8.1f" % ((S[a][0] - S[b][0]) * 1e4))
    print("%-6s %s" % (a, " ".join(cells)))

print("\nTHE DECISIVE COMPARISON")
etfs = ["SPY", "VOO", "IVV"]
etf_spread = max(S[e][0] for e in etfs) - min(S[e][0] for e in etfs)
mf = [s for s in data if s in ("FXAIX", "VFIAX")]
mf_best = max(mf, key=lambda s: S[s][0])
fund_vs_etf = S[mf_best][0] - S["SPY"][0]
print("  best fund minus SPY            : %+7.1f bp/yr" % (fund_vs_etf * 1e4))
print("  spread among SPY/VOO/IVV       : %7.1f bp/yr" % (etf_spread * 1e4))
print("  fee gap best-fund minus SPY    : %7.1f bp/yr"
      % ((VEH["SPY"][1] - VEH[mf_best][1]) * 10))
print("  unexplained residual           : %+7.1f bp/yr" % (fund_vs_etf * 1e4 - (VEH["SPY"][1] - VEH[mf_best][1]) * 10))
verdict = ("NOISE-DOMINATED: the fund-vs-ETF gap is within the spread across ETFs tracking the same index"
           if abs(fund_vs_etf) <= etf_spread * 1.5 else
           "LARGER THAN VEHICLE NOISE: the gap exceeds the ETF-to-ETF spread")
print("\n  VERDICT:", verdict)
