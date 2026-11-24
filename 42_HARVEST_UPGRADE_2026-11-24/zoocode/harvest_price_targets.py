#!/usr/bin/env python3
"""Price context for the HARVEST page: last price + analyst price-target range.

Why: a consensus of STRONG_BUY means little without knowing whether the mean
target sits 50% above or 5% below the current price. This fetches, for every
symbol already in docs/data/harvest_signals.json:

    currentPrice, targetMeanPrice, targetHighPrice, targetLowPrice,
    numberOfAnalystOpinions, recommendationKey

from Yahoo's quoteSummary `financialData` module, and writes a sidecar
docs/data/harvest_targets.json that harvest.html reads. It is deliberately a
SEPARATE file from the Finnhub feed so a failure here degrades one column, not
the whole page.

Auth: Yahoo needs a crumb. GET https://fc.yahoo.com for the A3 cookie (404 is
expected), then exchange it at /v1/test/getcrumb.

Honesty rules:
  * A missing value is written as null, never 0 and never carried forward.
  * `n_yahoo` is kept separate from the page's Finnhub analyst count, because
    the two genuinely differ (measured: BRK-B is 3 at Yahoo vs 10 on the page).

Usage: python3 tools/harvest_price_targets.py [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEED = ROOT / "docs" / "data" / "harvest_signals.json"
OUT = ROOT / "docs" / "data" / "harvest_targets.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--throttle", type=float, default=0.4)
    a = ap.parse_args(argv)

    import requests

    feed = json.loads(FEED.read_text(encoding="utf-8"))
    symbols = [s["symbol"] for s in feed["signals"]]
    if a.limit:
        symbols = symbols[: a.limit]

    s = requests.Session()
    h = {"User-Agent": UA}
    try:
        s.get("https://fc.yahoo.com", headers=h, timeout=10)
    except requests.RequestException:
        pass
    r = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=h, timeout=10)
    r.raise_for_status()
    crumb = r.text.strip()

    out: dict[str, dict] = {}
    for i, sym in enumerate(symbols, 1):
        url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{sym}"
               f"?modules=financialData&crumb={crumb}")
        rec: dict = {"symbol": sym}
        try:
            resp = s.get(url, headers=h, timeout=15)
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            rec.update(error=f"{type(exc).__name__}: {exc}")
            out[sym] = rec
            print(f"  [{i}/{len(symbols)}] {sym:<8} ERROR {rec['error']}", file=sys.stderr)
            time.sleep(a.throttle)
            continue
        qs = payload.get("quoteSummary") or {}
        res = qs.get("result")
        if not res:
            rec["error"] = (qs.get("error") or {}).get("description") or "no result"
            out[sym] = rec
            print(f"  [{i}/{len(symbols)}] {sym:<8} NONE  {rec['error']}", file=sys.stderr)
            time.sleep(a.throttle)
            continue
        m = res[0].get("financialData") or {}

        def raw(k):
            v = m.get(k)
            return v.get("raw") if isinstance(v, dict) else v

        rec.update(
            price=raw("currentPrice"),
            target_mean=raw("targetMeanPrice"),
            target_high=raw("targetHighPrice"),
            target_low=raw("targetLowPrice"),
            n_yahoo=raw("numberOfAnalystOpinions"),
            key=m.get("recommendationKey"),
        )
        up = None
        if rec["price"] and rec["target_mean"]:
            up = round(100.0 * (rec["target_mean"] / rec["price"] - 1.0), 1)
        rec["upside_pct"] = up
        out[sym] = rec
        print(f"  [{i}/{len(symbols)}] {sym:<8} price={rec['price']} target={rec['target_mean']} upside={up}%",
              file=sys.stderr)
        time.sleep(a.throttle)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Yahoo Finance quoteSummary financialData (crumb auth)",
        "note": ("upside_pct = targetMeanPrice/currentPrice - 1, in percent. "
                 "n_yahoo is Yahoo's analyst count and can differ from the page's "
                 "Finnhub count; both are shown rather than reconciled silently."),
        "targets": out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    ok = sum(1 for v in out.values() if v.get("target_mean") is not None)
    print(f"wrote {OUT}  ({ok}/{len(out)} with a mean target)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
