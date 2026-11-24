#!/usr/bin/env python3
"""Monte Carlo / permutation tests on the HARVEST consensus signal.

WHY THIS FILE EXISTS
--------------------
A previous run computed bucket means by hand and did not persist the underlying
(label, forward_return) pairs. That made the result unreproducible when the price source
hit its rate limit hours later — the exact failure mode this repo keeps paying for. This
script therefore:

  1. CACHES every symbol's prices to out/price_cache/<SYM>.json, so re-analysis never
     re-hits the vendor.
  2. APPENDS the observations to out/observations.jsonl, so the vector survives.
  3. Runs permutation tests whose inputs can be re-derived offline from those two files.

TESTS
  A. Is mean(STRONG_BUY) − mean(all) distinguishable from chance? (label permutation)
  B. Is the label ordering related to returns at all? (Spearman vs shuffled labels)
  C. Per-bucket bootstrap CI on the mean, so a "mean +1.16%" can be read with its width.

RATE LIMITS: Tiingo free tier is ~50 requests/hour and returns
  HTTP 429 {"detail":"Error: You have run over your hourly request allocation..."}
The script refuses to run a partial test silently: if fewer than MIN_OBS observations can be
collected it prints BLOCKED with the exact error and the counts, and exits non-zero.
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "out" / "price_cache"
OBS = HERE / "out" / "observations.jsonl"
FEED = HERE.parents[1] / "docs" / "data" / "harvest_signals.json"
UA = {"User-Agent": "hp-harvest research ejaguiar1@gmail.com"}
MIN_OBS = 60
PACE_FH, PACE_TI = 1.05, 1.0   # Finnhub 60/min; Tiingo is hourly, so go slow


def get(url, timeout=25):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return json.loads(r.read().decode()), r.status, None
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        return None, e.code, f"HTTP {e.code}: {body}"
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}"


def label_of(p):
    sb, b, h, se, ss = (p.get(k, 0) for k in ("strongBuy", "buy", "hold", "sell", "strongSell"))
    n = sb + b + h + se + ss
    if not n:
        return None
    sc, bs = (2 * sb + b - se - 2 * ss) / n, (sb + b) / n
    if sc >= 1.0 and bs >= 0.75: return "STRONG_BUY"
    if sc >= 0.3 and bs >= 0.50: return "BUY"
    if sc <= -1.0 and bs <= 0.15: return "STRONG_SELL"
    if sc <= -0.3 and bs <= 0.30: return "SELL"
    return "HOLD"


def px_on(rows, d):
    c = [x for x in rows if x["date"][:10] >= d]
    return c[0]["adjClose"] if c else None


def cached_prices(sym):
    f = CACHE / f"{sym}.json"
    if f.exists():
        return json.loads(f.read_text())
    p, status, err = get(f"https://api.tiingo.com/tiingo/daily/{sym}/prices"
                         f"?startDate=2026-08-01&endDate=2026-11-24&token={os.environ.get('TIINGO_API_KEY','')}")
    if status != 200 or not p:
        return {"__error__": err, "__status__": status}
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(p))
    time.sleep(PACE_TI)
    return p


def collect():
    feed = json.loads(FEED.read_text())
    obs, skipped = [], 0
    for i, s in enumerate(feed["signals"], 1):
        sym = s["symbol"]
        per, st, err = get(f"https://finnhub.io/api/v1/stock/recommendation"
                           f"?symbol={sym}&token={os.environ.get('FINNHUB','')}")
        time.sleep(PACE_FH)
        if not isinstance(per, list) or len(per) < 2:
            skipped += 1
            continue
        pr = cached_prices(sym)
        if not isinstance(pr, list):
            skipped += 1
            if isinstance(pr, dict) and pr.get("__status__") == 429:
                print(f"  BLOCKED at symbol {sym}: {pr['__error__']}")
                raise SystemExit(3)
            continue
        per = sorted(per, key=lambda x: x["period"])
        for a, b in zip(per, per[1:]):
            L = label_of(a)
            p0, p1 = px_on(pr, a["period"]), px_on(pr, b["period"])
            if L and p0 and p1 and p0 > 0:
                obs.append({"symbol": sym, "label": L, "period": a["period"],
                            "ret_pct": 100 * (p1 / p0 - 1)})
        if i % 20 == 0:
            print(f"    ... {i} probed, {len(obs)} observations")
    return obs, skipped


def spearman(xs, ys):
    n = len(xs)
    def rank(v):
        s = sorted(range(n), key=lambda i: v[i]); r = [0] * n
        for pos, i in enumerate(s):
            r[i] = pos + 1
        return r
    rx, ry = rank(xs), rank(ys)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def main() -> int:
    OBS.parent.mkdir(parents=True, exist_ok=True)
    obs, skipped = collect()
    if len(obs) < MIN_OBS:
        print(f"  BLOCKED: only {len(obs)} observations (< {MIN_OBS}); {skipped} symbols skipped. "
              f"Refusing to report a test on a sample this thin.")
        return 3

    with OBS.open("w") as fh:
        for o in obs:
            fh.write(json.dumps(o) + "\n")
    print(f"  observations persisted: {len(obs)} -> {OBS.relative_to(HERE)}")

    labels = [o["label"] for o in obs]
    rets = [o["ret_pct"] for o in obs]
    base = statistics.mean(rets)
    sb = [o["ret_pct"] for o in obs if o["label"] == "STRONG_BUY"]
    if not sb:
        print("  BLOCKED: no STRONG_BUY observations")
        return 3
    observed = statistics.mean(sb) - base
    print(f"\n  base mean {base:+.3f}%  STRONG_BUY n={len(sb)}  diff {observed:+.3f}pp")

    random.seed(20261124)
    B = 20000
    null = [statistics.mean(random.sample(rets, len(sb))) - base for _ in range(B)]
    p_perm = sum(1 for x in null if x <= observed) / B
    print(f"  [A] permutation p(diff <= observed) = {p_perm:.4f} over {B} draws")
    print(f"      null: mean {statistics.mean(null):+.4f}pp  sd {statistics.pstdev(null):.4f}pp")

    order = {"STRONG_BUY": 4, "BUY": 3, "HOLD": 2, "SELL": 1, "STRONG_SELL": 0}
    xs = [order[l] for l in labels]
    rho = spearman(xs, rets)
    null_rho = []
    for _ in range(5000):
        perm = xs[:]; random.shuffle(perm); null_rho.append(spearman(perm, rets))
    p_rho = sum(1 for x in null_rho if x <= rho) / len(null_rho)
    print(f"  [B] Spearman(label, return) = {rho:+.4f}  p(<= observed) = {p_rho:.4f}")

    print("  [C] bootstrap 95% CI on each bucket mean:")
    for lab in ("STRONG_BUY", "BUY", "HOLD"):
        g = [o["ret_pct"] for o in obs if o["label"] == lab]
        if len(g) < 5:
            continue
        bs = sorted(statistics.mean(random.choices(g, k=len(g))) for _ in range(5000))
        print(f"      {lab:<12} n={len(g):<3} mean {statistics.mean(g):+7.2f}%  "
              f"CI [{bs[125]:+.2f}, {bs[-126]:+.2f}]")
    print("\n  Reminder: a NEGATIVE rho means higher-rated labels had LOWER returns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
