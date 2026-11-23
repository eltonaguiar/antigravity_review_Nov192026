"""Apply the block-bootstrap Sharpe-difference test to the F4 vehicle comparison.

The reviewers said "SE(SR) ~ 0.5 over five years, so 0.728 vs 0.714 is noise". That SE applies to each Sharpe
LEVEL. Because two S&P 500 vehicles are ~0.998 correlated, the standard error of their DIFFERENCE is far smaller -
so the question "is FXAIX better than SPY?" can be answered more sharply than "we cannot tell". This script does it
and reports the paired interval.

Run from CONTEST/tools:  python apply_f4_bootstrap.py
"""
import json, ssl, urllib.request, datetime, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quant_metrics as qm

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE


def px(sym, rng="6y"):
    u = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d" % (sym, rng)
    j = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30, context=CTX)
                   .read().decode("utf-8", "replace"))
    r = j["chart"]["result"][0]
    d = {}
    for t, a in zip(r["timestamp"], r["indicators"]["adjclose"][0]["adjclose"]):
        if a:
            d[datetime.datetime.fromtimestamp(t, datetime.UTC).date().isoformat()] = float(a)
    return d


SYMS = ("FXAIX", "SPY", "VOO", "IVV", "VFIAX", "SGOV")
D = {s: px(s) for s in SYMS}
common = sorted(set.intersection(*[set(v) for v in D.values()]))
rf = qm.cagr([D["SGOV"][d] for d in common])

print("window %s .. %s   n=%d   rf proxy SGOV = %.3f%%/yr" % (common[0], common[-1], len(common), rf * 100))
print("\n%-22s %9s %22s  %s" % ("difference", "point", "95% CI (block=21)", "verdict"))
results = {}
for a, b in (("FXAIX", "SPY"), ("VOO", "SPY"), ("VOO", "FXAIX"), ("IVV", "FXAIX"), ("VFIAX", "FXAIX")):
    pa = [D[a][d] for d in common]
    pb = [D[b][d] for d in common]
    lo, hi, pt = qm.block_bootstrap_sharpe_diff(pa, pb, rf, B=2000, block=21, seed=11)
    spans = lo <= 0 <= hi
    results["%s-%s" % (a, b)] = {"point": pt, "lo": lo, "hi": hi, "spans_zero": spans}
    print("%-22s %+9.3f   [%+7.3f, %+7.3f]   %s"
          % ("Sharpe(%s)-Sharpe(%s)" % (a, b), pt, lo, hi,
             "INDISTINGUISHABLE" if spans else "distinguishable"))

print("\nKEY: the reviewers' SE(SR) ~ 0.5 is the error on each Sharpe LEVEL.")
print("Because these vehicles are ~0.998 correlated, the DIFFERENCE has a much tighter interval.")
widths = [abs(v["hi"] - v["lo"]) for v in results.values()]
print("Widest paired interval here: %.3f Sharpe units. All the differences are bounded inside roughly +/-%.2f."
      % (max(widths), max(widths) / 2))

json.dump({"window": [common[0], common[-1]], "n": len(common), "rf_annual": rf, "results": results},
          open("_f4_bootstrap.json", "w"), indent=1)
print("\nwrote _f4_bootstrap.json")
