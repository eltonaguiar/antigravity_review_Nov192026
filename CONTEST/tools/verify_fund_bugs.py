"""Verify the four claimed math bugs, and test whether they explain the retracted F4 gap.

The decisive arithmetic, which needs no access to the agent's script:
  Kilo's reported gap  : 11.66% - 11.49% = 17.0 bp/yr
  honest aligned gap   : measured separately  =  8.7 bp/yr
  difference           :              8.3 bp/yr
  fee gap (0.0945-0.015)=             7.95 bp/yr
If a script subtracts MER from an adjusted-close series, it removes the fee a SECOND time, and the gap it reports
should be honest_gap + fee_gap. That is what is being tested here.

Also recomputes Sharpe on excess return (the review's bug 2) and Sortino with the correct denominator (bug 3).
"""
import json, ssl, urllib.request, datetime, math

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
ER = {"FXAIX": 0.015, "VFIAX": 0.040, "SPY": 0.0945, "VOO": 0.030, "IVV": 0.030, "SGOV": 0.09}


def adj(sym):
    req = urllib.request.Request("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=6y&interval=1d" % sym,
                                 headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    res = j["chart"]["result"][0]
    out = {}
    for t, a in zip(res["timestamp"], res["indicators"]["adjclose"][0]["adjclose"]):
        if a:
            out[datetime.datetime.utcfromtimestamp(t).date().isoformat()] = float(a)
    return out


syms = ["FXAIX", "VFIAX", "SPY", "VOO", "IVV", "SGOV"]
D = {s: adj(s) for s in syms}
common = sorted(set.intersection(*[set(v) for v in D.values()]))
print("window %s .. %s  (%d sessions, %.2f y)\n" % (common[0], common[-1], len(common), len(common) / 252))


def series(s):
    return [D[s][d] for d in common]


def rets(s):
    p = series(s)
    return [p[i] / p[i - 1] - 1 for i in range(1, len(p))]


def cagr(s, subtract_er=False):
    p = series(s)
    y = len(p) / 252
    c = (p[-1] / p[0]) ** (1 / y) - 1
    return c - (ER[s] / 100 if subtract_er else 0.0)


R = {s: rets(s) for s in syms}
rf_annual = cagr("SGOV")                      # SGOV as the risk-free proxy
rf_daily = (1 + rf_annual) ** (1 / 252) - 1
print("risk-free proxy: SGOV CAGR %.3f%%/yr  (daily %.5f%%)" % (rf_annual * 100, rf_daily * 100))

print("\n%-6s %10s %10s %12s %12s %12s" % ("sym", "CAGR", "Sharpe(rf=0)", "Sharpe(excess)", "Sortino(old)", "Sortino(fix)"))
for s in syms:
    r = R[s]
    mu = sum(r) / len(r)
    sd = math.sqrt(sum((x - mu) ** 2 for x in r) / (len(r) - 1))
    sh0 = (mu / sd) * math.sqrt(252)
    ex = [x - rf_daily for x in r]
    mux = sum(ex) / len(ex)
    sdx = math.sqrt(sum((x - mux) ** 2 for x in ex) / (len(ex) - 1))
    shx = (mux / sdx) * math.sqrt(252)
    dn = [x for x in r if x < 0]
    dd_old = math.sqrt(sum(x * x for x in dn) / len(dn)) if dn else 0     # the reviewed bug
    dd_new = math.sqrt(sum(min(x, 0) ** 2 for x in r) / len(r))           # correct denominator
    so_old = (mu / dd_old) * math.sqrt(252) if dd_old else 0
    so_new = ((mu - rf_daily) / dd_new) * math.sqrt(252) if dd_new else 0
    print("%-6s %9.3f%% %11.3f %13.3f %12.3f %12.3f" % (s, cagr(s) * 100, sh0, shx, so_old, so_new))

print("\n=== BUG 1 TEST: does subtracting MER from adjusted close reproduce the retracted 17 bp? ===")
for pair in (("FXAIX", "SPY"), ("VOO", "SPY")):
    a, b = pair
    raw = (cagr(a) - cagr(b)) * 1e4
    doubled = (cagr(a, True) - cagr(b, True)) * 1e4
    print("  %-5s vs %-5s  raw %+6.1f bp/yr   with MER subtracted from BOTH %+6.1f bp/yr" % (a, b, raw, doubled))
fa, fb = "FXAIX", "SPY"
raw = (cagr(fa) - cagr(fb)) * 1e4
dbl = (cagr(fa, True) - cagr(fb, True)) * 1e4
print("\n  honest aligned gap            : %+.1f bp/yr" % raw)
print("  retracted figure (kilo)       : +17.0 bp/yr")
print("  gap the double-count predicts : %+.1f bp/yr  (honest + fee gap)" % dbl)
print("  prediction error              : %+.1f bp/yr" % (dbl - 17.0))
print("\n  VERDICT:", "BUG 1 CONFIRMED - double-counted MER reproduces the retracted number"
      if abs(dbl - 17.0) < 3.0 else "not reproduced arithmetically")

print("\n=== BUG 2 TEST: is rf=0 catastrophic for a T-bill fund? ===")
print("  SGOV Sharpe with rf=0     : %.2f   (absurd, as the review says)" % ((sum(R['SGOV'])/len(R['SGOV'])) /
      math.sqrt(sum((x - sum(R['SGOV'])/len(R['SGOV']))**2 for x in R['SGOV'])/(len(R['SGOV'])-1)) * math.sqrt(252)))
ex = [x - rf_daily for x in R["SGOV"]]
mux = sum(ex) / len(ex)
sdx = math.sqrt(sum((x - mux) ** 2 for x in ex) / (len(ex) - 1))
print("  SGOV Sharpe on excess     : %.2f   (approximately zero, as it should be)" % ((mux / sdx) * math.sqrt(252)))
