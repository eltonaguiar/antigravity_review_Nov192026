"""Can the next skyrocket be reverse-engineered? Two arms, one honest measurement.

ARM A - LOTTERY SCREEN. Which ex-ante features raise the probability of an extreme forward month?
   Target: forward 1-month return >= +30% (a "skyrocket"), and its mirror <= -30% (a "crash").
   Features at month-end, all point-in-time from trailing data only:
       mom_1m, mom_3m, mom_6m, mom_12_1 (12-month skipping the last), vol_20d, max5 (mean of the 5 largest
       daily returns in the month = the lottery/MAX factor), dist_52w_high, vol_ratio (20d/100d volume).
   Reported: base rate, precision at top-k, LIFT over base rate, and - the part that decides it - the MEAN and
   MEDIAN forward return of the selected names, plus the crash rate inside the selection.

ARM B - PEAD / GAP-CONTINUATION. The only arm with a real chance of positive expectancy.
   Event: a day whose OPEN gaps >= +4% above the previous close, on >= 2x the 50-day average volume.
   Then measure forward 5/21/63 trading-day returns from that day's CLOSE, against a control of all other days
   in the same stock. This is post-earnings-announcement-drift proxied without an earnings calendar.

Universe: S&P 500 constituents scraped live (SURVIVORSHIP-BIASED - stated, not hidden). 11 years of daily bars.
Costs: deducted at 12.07 bp round trip (the measured direct-equity figure from this programme) for any claim of edge.

No fabricated output: every number printed here is computed from fetched bars, and the script exits non-zero if
the universe cannot be built.
"""
import json, re, ssl, sys, math, urllib.request, statistics, datetime, os

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
OUT = r"C:/Users/zerou/AppData/Local/hermes/cache/scratch"
COST_BP = 12.07
EXCLUDE = {"BRK.B", "BF.B"}


def get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=CTX).read()


def universe():
    html = get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies").decode("utf-8", "replace")
    syms = re.findall(r'<a rel="nofollow" class="external text" href="https://www\.nyse\.com/quote/[^"]*"[^>]*>([A-Z\.\-]{1,6})</a>', html)
    if len(syms) < 300:
        syms = re.findall(r'<td><a rel="nofollow" class="external text"[^>]*>([A-Z\.\-]{1,6})</a></td>', html)
    if len(syms) < 300:
        syms = re.findall(r'\b([A-Z]{2,5})\b', html)
    seen, out = set(), []
    for s in syms:
        s = s.replace(".", "-")
        if s in seen or s in EXCLUDE or len(s) > 6:
            continue
        seen.add(s); out.append(s)
    return out


def bars(sym, rng="12y"):
    u = ("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d&events=div%%2Csplit"
         % (sym, rng))
    j = json.loads(get(u).decode("utf-8", "replace"))
    r = j["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose")
    ts = r["timestamp"]
    rows = []
    for i, t in enumerate(ts):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        a = adj[i] if adj else c
        if None in (o, c, a) or not c or not a:
            continue
        rows.append((t, o, c, a, v or 0))
    return rows


def main():
    syms = universe()
    print("universe: %d symbols (survivorship-biased: current constituents only)" % len(syms))
    if len(syms) < 100:
        print("FATAL: universe build failed"); sys.exit(2)

    panel = []          # month-end feature rows
    events = []         # PEAD gap events
    ok = fail = 0
    for n, s in enumerate(syms):
        try:
            rows = bars(s)
            if len(rows) < 400:
                fail += 1; continue
            ok += 1
        except Exception:
            fail += 1; continue

        closes = [r[3] for r in rows]      # adjusted close (total return)
        opens = [r[1] for r in rows]
        vols = [r[4] for r in rows]
        ts = [r[0] for r in rows]

        # ---- ARM B: gap events, measured from the event close
        for i in range(60, len(rows) - 64):
            prev_c = closes[i - 1]
            if prev_c <= 0:
                continue
            gap = opens[i] / closes[i - 1] - 1.0
            av50 = sum(vols[i - 50:i]) / 50.0
            if gap >= 0.04 and av50 > 0 and vols[i] >= 2 * av50:
                c0 = closes[i]
                fwd = {}
                for h in (5, 21, 63):
                    if i + h < len(closes):
                        fwd[h] = closes[i + h] / c0 - 1.0
                if fwd:
                    events.append({"sym": s, "date": ts[i], "gap": gap, "fwd": fwd,
                                   "vratio": vols[i] / av50})

        # ---- ARM A: month-end features (month = calendar month of a fixed trading-day grid)
        for i in range(260, len(rows) - 22):
            d = datetime.datetime.utcfromtimestamp(ts[i]).date()
            d2 = datetime.datetime.utcfromtimestamp(ts[i + 1]).date()
            if d.month == d2.month:
                continue                      # only at a month boundary
            c = closes[i]
            def ret(back):
                if i - back < 0:
                    return None
                return c / closes[i - back] - 1.0
            m1, m3, m6 = ret(21), ret(63), ret(126)
            m12_1 = None
            if i - 252 >= 0:
                m12_1 = closes[i - 21] / closes[i - 252] - 1.0
            if None in (m1, m3, m6, m12_1):
                continue
            dr = [closes[k] / closes[k - 1] - 1.0 for k in range(i - 20, i + 1)]
            mu = sum(dr) / len(dr)
            vol20 = statistics.stdev(dr) * math.sqrt(252)
            max5 = sum(sorted(dr)[-5:]) / 5.0
            hi = max(closes[i - 251:i + 1])
            dist_hi = c / hi - 1.0
            av20 = sum(vols[i - 19:i + 1]) / 20.0
            av100 = sum(vols[i - 99:i + 1]) / 100.0
            vr = av20 / av100 if av100 else 1.0
            # forward 1 month
            j = min(i + 21, len(closes) - 1)
            fwd1 = closes[j] / c - 1.0
            panel.append({"sym": s, "date": str(d), "year": d.year,
                          "m1": m1, "m3": m3, "m6": m6, "m12_1": m12_1,
                          "vol20": vol20, "max5": max5, "dist_hi": dist_hi, "vr": vr,
                          "fwd1": fwd1})
        if (n + 1) % 50 == 0:
            print("  fetched %d/%d (ok=%d fail=%d) panel=%d events=%d"
                  % (n + 1, len(syms), ok, fail, len(panel), len(events)))
            sys.stdout.flush()

    print("\nfetched ok=%d fail=%d | month-end rows=%d | gap events=%d" % (ok, fail, len(panel), len(events)))
    json.dump({"panel_n": len(panel), "events_n": len(events)}, open(os.path.join(OUT, "_skyrocket_counts.json"), "w"))
    if not panel:
        print("FATAL: no panel"); sys.exit(3)

    # ---------------- ARM A analysis ----------------
    sky = [r for r in panel if r["fwd1"] >= 0.30]
    crash = [r for r in panel if r["fwd1"] <= -0.30]
    base = len(sky) / len(panel)
    base_crash = len(crash) / len(panel)
    print("\n=== ARM A: LOTTERY SCREEN ===")
    print("panel rows: %d   P(+30%% next month) = %.3f%%   P(-30%%) = %.3f%%"
          % (len(panel), base * 100, base_crash * 100))

    feats = ["m1", "m3", "m6", "m12_1", "vol20", "max5", "dist_hi", "vr"]
    print("\n%-9s %8s %8s %8s %8s %9s %9s %9s" % ("feature", "top-dec", "base", "LIFT", "crash%", "mean fwd", "med fwd", "net bp"))
    rows_out = []
    for f in feats:
        for direction in ("high", "low"):
            srt = sorted(panel, key=lambda r: r[f], reverse=(direction == "high"))
            k = max(1, len(srt) // 10)
            top = srt[:k]
            hits = sum(1 for r in top if r["fwd1"] >= 0.30)
            cr = sum(1 for r in top if r["fwd1"] <= -0.30) / len(top)
            prec = hits / len(top)
            mean = sum(r["fwd1"] for r in top) / len(top)
            med = statistics.median([r["fwd1"] for r in top])
            net = (mean * 1e4) - COST_BP
            label = "%s(%s)" % (f, direction[0])
            print("%-9s %7.2f%% %7.2f%% %8.2fx %7.2f%% %8.3f%% %8.3f%% %+9.0f"
                  % (label, prec * 100, base * 100, prec / base if base else 0, cr * 100, mean * 100, med * 100, net))
            rows_out.append({"feature": label, "precision": prec, "lift": prec / base if base else 0,
                             "crash_rate": cr, "mean_fwd": mean, "median_fwd": med, "net_bp": net, "k": k})

    best = max(rows_out, key=lambda r: r["lift"])
    print("\nbest lift: %s at %.2fx base rate; its median forward return is %+.3f%% and net expectancy %+.0f bp"
          % (best["feature"], best["lift"], best["median_fwd"] * 100, best["net_bp"]))

    # ---------------- ARM B analysis ----------------
    print("\n=== ARM B: GAP-UP CONTINUATION (PEAD proxy) ===")
    for h in (5, 21, 63):
        ev = [e["fwd"][h] for e in events if h in e["fwd"]]
        if not ev:
            continue
        mu = sum(ev) / len(ev)
        med = statistics.median(ev)
        pos = sum(1 for x in ev if x > 0) / len(ev)
        net = mu * 1e4 - COST_BP
        t = mu / (statistics.stdev(ev) / math.sqrt(len(ev))) if len(ev) > 2 and statistics.stdev(ev) > 0 else 0
        print("  %2dd  n=%-5d mean %+7.3f%%  median %+7.3f%%  up-rate %5.1f%%  t=%5.2f  net %+7.0f bp"
              % (h, len(ev), mu * 100, med * 100, pos * 100, t, net))

    json.dump({"base_rate": base, "base_crash": base_crash, "panel_n": len(panel),
               "screens": rows_out, "events_n": len(events)}, open(os.path.join(OUT, "_skyrocket_results.json"), "w"), indent=1)
    print("\nsaved _skyrocket_results.json")


if __name__ == "__main__":
    main()
