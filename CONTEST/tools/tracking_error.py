"""Tracking-error decomposition — the test the reviewers kept asking for and nobody ran.

The FXAIX-vs-SPY argument IS a tracking-error argument: if two vehicles track the same index, their
return difference should be (a) systematically equal to the fee gap and (b) small relative to its own
dispersion. This script computes both halves for four pairs, including a same-fund control.

  tracking difference (TD) = annualised mean of (r_a - r_b)   <- should equal the fee gap
  tracking error     (TE) = annualised stdev of (r_a - r_b)   <- the noise the difference must clear
  information ratio (IR) = TD / TE                            <- |IR| > ~2 means systematic, not noise

Pair design:
  VTSAX vs VTI     share classes of ONE fund  -> the control: TD should be ~1 bp (the fee gap), TE tiny
  FXAIX vs SPY     same index, fees differ by 7.95 bp
  VOO   vs SPY     same index, fees differ by 6.45 bp
  FZROX vs VTI     DIFFERENT indexes (Fidelity proprietary vs CRSP) -> TD should NOT equal the 3 bp fee gap
"""
import json, ssl, urllib.request, datetime, sys, os, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quant_metrics as qm

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
ER = {"VTSAX": 0.04, "VTI": 0.03, "FXAIX": 0.015, "SPY": 0.0945, "VOO": 0.03, "FZROX": 0.0, "SGOV": 0.09}
ANN = 252


def px(sym):
    u = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=6y&interval=1d" % sym
    j = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30, context=CTX)
                   .read().decode("utf-8", "replace"))
    r = j["chart"]["result"][0]
    return {datetime.datetime.fromtimestamp(t, datetime.UTC).date().isoformat(): float(a)
            for t, a in zip(r["timestamp"], r["indicators"]["adjclose"][0]["adjclose"]) if a}


SYMS = ["VTSAX", "VTI", "FXAIX", "SPY", "VOO", "FZROX"]
D = {s: px(s) for s in SYMS}
common = sorted(set.intersection(*[set(v) for v in D.values()]))
R = {s: [D[s][common[i]] / D[s][common[i - 1]] - 1 for i in range(1, len(common))] for s in SYMS}
yrs = (len(common) - 1) / ANN
print("window %s .. %s   n=%d sessions (%.2f y)\n" % (common[0], common[-1], len(common), yrs))


def td_te(a, b):
    diff = [R[a][i] - R[b][i] for i in range(len(R[a]))]
    mu = sum(diff) / len(diff)
    sd = (sum((x - mu) ** 2 for x in diff) / (len(diff) - 1)) ** 0.5
    td = mu * ANN                      # annualised tracking difference
    te = sd * math.sqrt(ANN)           # annualised tracking error
    ir = td / te if te else float("nan")
    # t-stat on the mean daily difference, Newey-West-free (conservative for a benchmark pair)
    t = mu / (sd / math.sqrt(len(diff))) if sd else float("nan")
    return td, te, ir, t


PAIRS = [
    ("VTSAX", "VTI", "share classes of ONE fund — CONTROL"),
    ("FXAIX", "SPY", "same index, 7.95 bp fee gap"),
    ("VOO", "SPY", "same index, 6.45 bp fee gap"),
    ("FZROX", "VTI", "DIFFERENT indexes (Fidelity vs CRSP)"),
]

print("%-14s %-38s %10s %9s %7s %7s %9s" % ("pair", "design", "TD (bp/yr)", "TE (%)", "IR", "t", "fee gap bp"))
rows = []
for a, b, note in PAIRS:
    td, te, ir, t = td_te(a, b)
    fee = (ER[b] - ER[a]) * 100  # percent -> bp
    rows.append({"a": a, "b": b, "note": note, "td_bp": td * 1e4, "te_pct": te * 100,
                 "ir": ir, "t": t, "fee_gap_bp": fee})
    print("%-14s %-38s %+10.1f %9.3f %7.2f %7.1f %9.2f"
          % ("%s-%s" % (a, b), note, td * 1e4, te * 100, ir, t, fee))

print("\n=== READ IT AS THREE QUESTIONS ===")
for r in rows:
    verdict = []
    if abs(r["td_bp"] - r["fee_gap_bp"]) <= 2.5:
        verdict.append("TD matches the fee gap")
    else:
        verdict.append("TD does NOT match the fee gap (>= %.1f bp unexplained)" % (r["td_bp"] - r["fee_gap_bp"]))
    if abs(r["ir"]) >= 2.0:
        verdict.append("systematic (|IR| %.1f >= 2)" % abs(r["ir"]))
    else:
        verdict.append("NOT distinguishable from noise (|IR| %.1f)" % abs(r["ir"]))
    print("  %-13s %s" % ("%s-%s" % (r["a"], r["b"]), "; ".join(verdict)))

json.dump({"window": [common[0], common[-1]], "n": len(common), "years": yrs, "pairs": rows},
          open("_tracking_error.json", "w"), indent=1)
print("\nwrote _tracking_error.json")
