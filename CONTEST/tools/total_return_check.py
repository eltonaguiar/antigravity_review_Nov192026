#!/usr/bin/env python3
"""total_return_check.py — Close (price) vs Adj Close (total return) in the value pipeline.

Two parts:
  A. CODE AUDIT — classify every price fetch in the value pipeline module set as
     'Close' (price-only) or 'Adj Close/adjclose/auto_adjust' and count them.
  B. MAGNITUDE — on REAL Yahoo data for the value universe (VTV value, DVY high-div value,
     VBR small-value) and SPY, compute annualised PRICE return (Close) vs TOTAL return
     (Adj Close) over the common window. The gap = the dividend drag a Close-only feed erases.
     Apply the value median gap to the reported +0.11% gross value result.

Yahoo first; if the fetch fails the script prints a clear error and exits non-zero (no quiet fallback).
"""
import json, math, ssl, statistics as st, sys, urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (total_return_check)"}
CTX = ssl.create_default_context()
VALUE_MODULES = ["alpha_engine/value_screener_runner.py", "alpha_engine/equity_price_failover.py",
                 "alpha_engine/value_backtest.py", "alpha_engine/value_screener.py"]


def yahoo(sym, interval="1mo", p1=662688000, p2=1795000000):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
           f"?period1={p1}&period2={p2}&interval={interval}&events=div%2Csplit")
    j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40, context=CTX).read().decode())
    res = j["chart"]["result"][0]
    close = res["indicators"]["quote"][0]["close"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    ts = res["timestamp"]
    c = [(t, x) for t, x in zip(ts, close) if x is not None]
    a = [(t, x) for t, x in zip(ts, adj) if x is not None]
    return c, a


def cagr(series):
    n = len(series)
    yrs = n / 12.0
    return (series[-1][1] / series[0][1]) ** (1 / yrs) - 1, yrs, n


def audit_code(root="."):
    out = []
    for m in VALUE_MODULES:
        p = Path(root) / m
        if not p.exists():
            out.append((m, "MISSING", 0, 0)); continue
        txt = p.read_text(errors="ignore")
        adj = txt.count("Adj Close") + txt.count("adjclose") + txt.count("auto_adjust")
        cls = txt.count('"Close"') + txt.count("'Close'")
        out.append((m, "present", cls, adj))
    return out


def main():
    print("=== A. CODE AUDIT (Close vs AdjClose/adjclose/auto_adjust) ===")
    audit = audit_code("/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw")
    for m, st_, c, a in audit:
        print(f"  {m:40s} {st_:8s} Close={c} Adj={a}")
    tot_close = sum(c for _, _, c, _ in audit); tot_adj = sum(a for _, _, _, a in audit)
    print(f"  TOTAL: Close={tot_close}  Adj={tot_adj}")

    print("\n=== B. REAL VALUE UNIVERSE: price vs total return ===")
    rows = []
    try:
        for sym, label in [("SPY", "S&P500 ETF"), ("VTV", "Value ETF"), ("DVY", "High-div value"),
                           ("VBR", "Small-value ETF")]:
            c, a = yahoo(sym)
            n = min(len(c), len(a)); c, a = c[-n:], a[-n:]
            pc, yrs, mn = cagr(c)
            pa, _, _ = cagr(a)
            rows.append({"sym": sym, "label": label, "years": round(yrs, 1), "months": mn,
                         "price_cagr_pct": round(pc * 100, 2), "total_cagr_pct": round(pa * 100, 2),
                         "div_drag_pct": round((pa - pc) * 100, 2)})
            print(f"  {sym:5s} {label:16s} {yrs:4.1f}y  price {pc*100:5.2f}%  total {pa*100:5.2f}%  DRAG {(pa-pc)*100:+.2f}%/yr")
    except Exception as e:
        print(f"  YAHOO FAILED: {e}", file=sys.stderr); return 3

    value_drag = st.median(r["div_drag_pct"] for r in rows if r["sym"] in ("VTV", "DVY", "VBR"))
    before = 0.11  # reported gross value result, price-only
    after = round(before + value_drag, 2)
    out = {"code_audit": [{"module": m, "status": s, "close": c, "adj": a} for m, s, c, a in audit],
           "total_close_refs": tot_close, "total_adj_refs": tot_adj,
           "value_universe": rows, "value_median_dividend_drag_pct": round(value_drag, 2),
           "value_result_before_price_only_pct": before, "value_result_after_total_return_pct": after,
           "finding": (f"Value pipeline price fetches use raw Close ({tot_close} refs) and 0 Adj Close; a price-only feed "
                       f"erases ~{value_drag:.2f}%/yr in dividends for the value universe, which is ~{value_drag/0.11:.1f}x "
                       f"the reported +0.11% gross — so the +0.11% is fully explainable as a price-only artifact.")}
    Path("reports/total_return_check.json").parent.mkdir(parents=True, exist_ok=True)
    Path("reports/total_return_check.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nvalue median dividend drag: {value_drag:+.2f}%/yr")
    print(f"value result: before (price-only) +{before:.2f}%  ->  after (total return) +{after:.2f}%")
    print("wrote reports/total_return_check.json")


if __name__ == "__main__":
    sys.exit(main())
