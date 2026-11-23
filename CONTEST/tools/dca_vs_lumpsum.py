"""DCA versus lump-sum, and the "missing the best days" claim. SPY, 1993-2026.

Both are measured on real adjusted-close data, no assumptions.

  python dca_vs_lumpsum.py

Fetches SPY monthly adjusted close from Yahoo, then:

  1. Compares lump-sum (all capital at month 0) against DCA ($total/n per month
     for n months), for every monthly start date, at several hold lengths.
     Reports P(DCA > lump-sum) and the median terminal-value ratio.

  2. Recomputes the 1993-2026 compounded return with the best N months removed,
     which is the standard "missing the best days" argument.

Caveat stated up front: monthly bars, SPY only, one market. This measures what
DCA does to terminal wealth, not what it does to behaviour - and behaviour is
where DCA earns its keep.
"""
import datetime
import json
import ssl
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

URL = ("https://query1.finance.yahoo.com/v8/finance/chart/SPY"
       "?range=max&interval=1d&events=div%2Csplit")


def load():
    """Return {month_index: adj_close}, month-indexed, newest last."""
    req = urllib.request.Request(URL, headers=UA)
    j = json.loads(urllib.request.urlopen(req, timeout=40, context=CTX).read().decode())
    r = j["chart"]["result"][0]
    ts = r["timestamp"]
    adj = r["indicators"]["adjclose"][0]["adjclose"]
    month_end = {}
    for t, a in zip(ts, adj):
        if a is None:
            continue
        d = datetime.datetime.fromtimestamp(t, datetime.UTC).date()
        month_end[(d.year, d.month)] = float(a)
    keys = sorted(month_end)
    return [month_end[k] for k in keys], keys


def terminal(px, i, hold_years, kind, dca_months=12, total=12000.0):
    """Terminal value at month i + hold*12, or None if it runs off the data."""
    end = i + hold_years * 12
    if end >= len(px):
        return None
    if kind == "LS":
        return total * px[end] / px[i]
    per = total / dca_months
    val = 0.0
    for k in range(dca_months):
        if i + k >= len(px):
            return None
        val += per * px[end] / px[i + k]
    return val


def compare(px, hold, dca_months):
    ratios = []
    for i in range(len(px)):
        a = terminal(px, i, hold, "LS")
        b = terminal(px, i, hold, "DCA", dca_months)
        if a and b:
            ratios.append(b / a)
    if not ratios:
        return None
    ratios.sort()
    wins = sum(1 for x in ratios if x > 1)
    return {
        "n": len(ratios),
        "p_win": wins / len(ratios),
        "median": ratios[len(ratios) // 2],
        "worst": ratios[0],
        "best": ratios[-1],
    }


def missing_best(px, k):
    rets = [px[i + 1] / px[i] - 1 for i in range(len(px) - 1)]
    full = 1.0
    for x in rets:
        full *= 1 + x
    drop = set(sorted(range(len(rets)), key=lambda i: rets[i], reverse=True)[:k])
    kept = [r for i, r in enumerate(rets) if i not in drop]
    v = 1.0
    for x in kept:
        v *= 1 + x
    return {
        "k": k,
        "full_mult": full,
        "kept_mult": v,
        "full_cagr": full ** (12.0 / len(rets)) - 1,
        "kept_cagr": v ** (12.0 / len(kept)) - 1,
    }


def main():
    px, keys = load()
    print("SPY monthly adjusted close: %d months, %s -> %s\n"
          % (len(px), keys[0], keys[-1]))

    print("=" * 66)
    print("1. LUMP-SUM vs DCA (12 months), same $12,000")
    print("=" * 66)
    print("  %-8s %-8s %-20s %s" % ("hold", "starts", "P(DCA > lump-sum)", "median DCA/LS"))
    print("  " + "-" * 58)
    for hold in (5, 10, 20, 30):
        r = compare(px, hold, 12)
        if r:
            print("  %-8s %-8d %-20s %.4f"
                  % ("%dy" % hold, r["n"], "%.1f%%" % (100 * r["p_win"]), r["median"]))

    print("\n  longer DCA windows, 30-year hold:")
    for dca in (12, 24, 36):
        r = compare(px, 30, dca)
        if r:
            print("    DCA over %2dm: P(DCA>LS)=%5.1f%%  median=%.4f  n=%d"
                  % (dca, 100 * r["p_win"], r["median"], r["n"]))

    print()
    print("=" * 66)
    print("2. 'MISSING THE BEST DAYS' - compounded, best N months removed")
    print("=" * 66)
    base = missing_best(px, 0)
    print("  full sample: %.2fx  -> CAGR %.2f%%" % (base["full_mult"], 100 * base["full_cagr"]))
    for k in (5, 10, 20, 40):
        r = missing_best(px, k)
        print("  remove best %2d months (%.1f%% of sample): %.2fx -> CAGR %.2f%%"
              % (k, 100.0 * k / (len(px) - 1), r["kept_mult"], 100 * r["kept_cagr"]))

    print("\n  Read this as concentration of returns in a few periods - which is")
    print("  why neither timing nor this statistic is reliable. The up-months")
    print("  cluster inside the drawdowns, so you cannot dodge one without the other.")


if __name__ == "__main__":
    main()
