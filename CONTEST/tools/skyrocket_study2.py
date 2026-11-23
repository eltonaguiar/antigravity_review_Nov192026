"""Skyrocket study v2 — same questions, but with the two controls v1 lacked.

v1 reported, honestly fetched but badly framed:
  Arm A: vol20 top decile hits P(+30% next month) at 5.28x base rate
  Arm B: gap-up events show mean +4.57% over 63 days, t=48.76
Both numbers are confounded:
  * NO MARKET BASELINE. 2020-2026 is a bull market; a +4.6% 63-day drift may be beta, not signal.
  * OVERLAPPING WINDOWS. 36,265 events with 63-day forward windows overlap heavily, so t=48.76 is
    inflated by roughly sqrt(overlap). It is not 48.76 standard errors of independent evidence.

v2 fixes both:
  Arm A -> EXCESS return: each row's forward month minus the cross-sectional mean forward month for that
           same date. This removes the market's drift and answers "does this stock beat its peers?".
  Arm B -> two baselines: (a) the same stock's mean forward return on all NON-event days, and (b) a
           non-overlapping event subset (one event per stock per horizon length), with t computed on that
           subset only.
Bars are cached to disk so re-runs take seconds instead of seven minutes.
"""
import json, re, ssl, sys, math, urllib.request, statistics, datetime, os, pickle

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
OUT = r"C:/Users/zerou/AppData/Local/hermes/cache/scratch"
CACHE = os.path.join(OUT, "bars_cache.pkl")
COST_BP = 12.07
EXCLUDE = {"BRK.B", "BF.B", "BRK-B", "BF-B"}


def get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=CTX).read()


def universe():
    html = get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies").decode("utf-8", "replace")
    syms = re.findall(r'<a rel="nofollow" class="external text" href="https://www\.nyse\.com/quote/[^"]*"[^>]*>([A-Z\.\-]{1,6})</a>', html)
    if len(syms) < 300:
        syms = re.findall(r'\b([A-Z]{2,5})\b', html)
    seen, out = set(), []
    for s in syms:
        s = s.replace(".", "-")
        if s in seen or s in EXCLUDE or len(s) > 6:
            continue
        seen.add(s); out.append(s)
    return out


def fetch(sym):
    u = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=12y&interval=1d&events=div%%2Csplit" % sym
    j = json.loads(get(u).decode("utf-8", "replace"))
    r = j["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose")
    rows = []
    for i, t in enumerate(r["timestamp"]):
        o, c, v = q["open"][i], q["close"][i], q["volume"][i]
        a = adj[i] if adj else c
        if None in (o, c, a) or not c or not a:
            continue
        rows.append((t, o, c, a, v or 0))
    return rows


def load_bars(syms):
    cache = {}
    if os.path.exists(CACHE):
        try:
            cache = pickle.load(open(CACHE, "rb"))
            print("cache: %d symbols" % len(cache))
        except Exception:
            cache = {}
    need = [s for s in syms if s not in cache]
    print("need to fetch: %d" % len(need))
    for n, s in enumerate(need):
        try:
            rows = fetch(s)
            cache[s] = rows if len(rows) > 400 else []
        except Exception:
            cache[s] = []
        if (n + 1) % 60 == 0:
            print("  fetched %d/%d" % (n + 1, len(need)))
            sys.stdout.flush()
            pickle.dump(cache, open(CACHE, "wb"))
    pickle.dump(cache, open(CACHE, "wb"))
    return {s: v for s, v in cache.items() if v}


def main():
    syms = universe()
    print("universe: %d" % len(syms))
    bars = load_bars(syms)
    print("usable symbols: %d" % len(bars))
    if len(bars) < 100:
        print("FATAL universe"); sys.exit(2)

    panel, events = [], []
    for s, rows in bars.items():
        closes = [r[3] for r in rows]; opens = [r[1] for r in rows]; vols = [r[4] for r in rows]; ts = [r[0] for r in rows]

        # ---- Arm B events
        for i in range(60, len(rows) - 64):
            if closes[i - 1] <= 0:
                continue
            gap = opens[i] / closes[i - 1] - 1.0
            av50 = sum(vols[i - 50:i]) / 50.0
            if gap >= 0.04 and av50 > 0 and vols[i] >= 2 * av50:
                c0 = closes[i]
                fwd = {h: closes[i + h] / c0 - 1.0 for h in (5, 21, 63) if i + h < len(closes)}
                if fwd:
                    events.append((s, ts[i], gap, fwd))

        # ---- Arm A month-ends
        for i in range(260, len(rows) - 22):
            d = datetime.datetime.utcfromtimestamp(ts[i]).date()
            d2 = datetime.datetime.utcfromtimestamp(ts[i + 1]).date()
            if d.month == d2.month:
                continue
            c = closes[i]
            m1, m3, m6 = c / closes[i - 21] - 1, c / closes[i - 63] - 1, c / closes[i - 126] - 1
            m12_1 = closes[i - 21] / closes[i - 252] - 1 if i - 252 >= 0 else None
            if m12_1 is None:
                continue
            dr = [closes[k] / closes[k - 1] - 1 for k in range(i - 20, i + 1)]
            mu = sum(dr) / len(dr)
            vol20 = statistics.stdev(dr) * math.sqrt(252)
            max5 = sum(sorted(dr)[-5:]) / 5.0
            dist_hi = c / max(closes[i - 251:i + 1]) - 1
            av20 = sum(vols[i - 19:i + 1]) / 20.0
            av100 = sum(vols[i - 99:i + 1]) / 100.0
            vr = av20 / av100 if av100 else 1.0
            j = min(i + 21, len(closes) - 1)
            panel.append({"sym": s, "date": str(d), "m1": m1, "m3": m3, "m6": m6, "m12_1": m12_1,
                          "vol20": vol20, "max5": max5, "dist_hi": dist_hi, "vr": vr,
                          "fwd1": closes[j] / c - 1.0})

    print("\npanel rows=%d  events=%d" % (len(panel), len(events)))

    # ---- cross-sectional baseline per date
    bydate = {}
    for r in panel:
        bydate.setdefault(r["date"], []).append(r["fwd1"])
    mkt = {d: sum(v) / len(v) for d, v in bydate.items()}
    for r in panel:
        r["ex"] = r["fwd1"] - mkt[r["date"]]

    base = sum(1 for r in panel if r["fwd1"] >= 0.30) / len(panel)
    base_ex = sum(1 for r in panel if r["ex"] >= 0.30) / len(panel)
    print("P(+30%% raw)=%.3f%%   P(+30%% vs peers)=%.3f%%   (n=%d)" % (base * 100, base_ex * 100, len(panel)))

    print("\n=== ARM A: does the screen pick names that BEAT THEIR PEERS? ===")
    print("%-10s %8s %8s %8s %9s %9s %10s %10s" % ("feature", "raw mean", "ex mean", "ex med", "hit%peer", "crash%peer", "net bp raw", "net bp ex"))
    table = []
    for f in ["m1", "m3", "m6", "m12_1", "vol20", "max5", "dist_hi", "vr"]:
        for direction in ("high", "low"):
            srt = sorted(panel, key=lambda r: r[f], reverse=(direction == "high"))
            k = max(1, len(srt) // 10)
            top = srt[:k]
            raw = sum(r["fwd1"] for r in top) / len(top)
            ex = sum(r["ex"] for r in top) / len(top)
            exm = statistics.median([r["ex"] for r in top])
            hit = sum(1 for r in top if r["ex"] > 0) / len(top)
            cr = sum(1 for r in top if r["ex"] <= -0.30) / len(top)
            table.append({"f": "%s(%s)" % (f, direction[0]), "raw": raw, "ex": ex, "ex_med": exm,
                          "hit": hit, "crash": cr, "net_raw": raw * 1e4 - COST_BP, "net_ex": ex * 1e4 - COST_BP})
            print("%-10s %7.2f%% %7.2f%% %7.2f%% %8.1f%% %9.2f%% %+9.0f %+10.0f"
                  % (table[-1]["f"], raw * 100, ex * 100, exm * 100, hit * 100, cr * 100,
                     table[-1]["net_raw"], table[-1]["net_ex"]))
    best = max(table, key=lambda r: r["ex"])
    print("\nbest BEATS-PEERS screen: %s  excess mean %+.2f%%  median %+.2f%%  net %+.0f bp"
          % (best["f"], best["ex"] * 100, best["ex_med"] * 100, best["net_ex"]))

    # ---- Arm B with baselines and non-overlap
    print("\n=== ARM B: gap-up continuation, vs the stock's own non-event days ===")
    for h in (5, 21, 63):
        # per-stock baseline: all non-event days, forward h from any day
        base_all = []
        for s, rows in bars.items():
            closes = [r[3] for r in rows]
            ev_idx = {e[1] for e in events if e[0] == s}
            for i in range(0, len(closes) - h):
                t = rows[i][0]
                if t in ev_idx:
                    continue
                base_all.append(closes[i + h] / closes[i] - 1.0)
        evs = [e for e in events if h in e[3]]
        raw = [e[3][h] for e in evs]
        bmu = sum(base_all) / len(base_all) if base_all else 0.0
        # non-overlapping subset: one event per stock per h sessions
        last = {}
        nonov = []
        for e in sorted(evs, key=lambda x: x[1]):
            if e[0] in last and e[1] - last[e[0]] < h * 86400:
                continue
            last[e[0]] = e[1]
            nonov.append(e[3][h])
        mu = sum(raw) / len(raw); med = statistics.median(raw)
        t_all = mu / (statistics.stdev(raw) / math.sqrt(len(raw))) if len(raw) > 2 else 0
        mnu = sum(nonov) / len(nonov)
        t_no = mnu / (statistics.stdev(nonov) / math.sqrt(len(nonov))) if len(nonov) > 2 else 0
        print("  %2dd  n=%-6d mean %+6.2f%%  median %+6.2f%%  |  non-overlap n=%-5d mean %+6.2f%%  t=%5.2f"
              % (h, len(raw), mu * 100, med * 100, len(nonov), mnu * 100, t_no))
        print("        stock baseline on non-event days: %+6.2f%%   EXCESS vs baseline: %+6.2f%%  net %+6.0f bp"
              % (bmu * 100, (mu - bmu) * 100, (mu - bmu) * 1e4 - COST_BP))
        print("        naive t on ALL events (v1's error): %.2f   vs honest t on non-overlapping: %.2f"
              % (t_all, t_no))

    json.dump({"panel": len(panel), "base_raw": base, "base_ex": base_ex, "screens": table,
               "events": len(events)}, open(os.path.join(OUT, "_skyrocket_results_v2.json"), "w"), indent=1)
    print("\nsaved _skyrocket_results_v2.json")


if __name__ == "__main__":
    main()
