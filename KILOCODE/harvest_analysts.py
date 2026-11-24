#!/usr/bin/env python3
"""Harvest official analyst endorsements (consensus + upgrades) across asset classes.

Sources (public, no API key):
  * Yahoo Finance quoteSummary: recommendationTrend, upgradeDowngradeHistory,
    financialData (needs a crumb from fc.yahoo.com -> /v1/test/getcrumb).
  * Nasdaq public analyst endpoints: /api/analyst/<sym>/ratings and /targetprice.

Outputs:
  KILOCODE/HARVEST_<UTC>.MD   human report
  docs/harvest.json           data for the Pages HARVEST table

Honesty rules: missing coverage is emitted as status="no_coverage"; dates are the
sources' own timestamps; analyst ratings are opinions, not advice.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import time
from pathlib import Path

from curl_cffi import requests as creq

ROOT = Path(__file__).resolve().parent.parent
OUT_MD_DIR = ROOT / "KILOCODE"
OUT_JSON = ROOT / "docs" / "harvest.json"

UNIVERSE = [
    ("AAPL", "Stocks"), ("MSFT", "Stocks"), ("NVDA", "Stocks"), ("GOOGL", "Stocks"),
    ("AMZN", "Stocks"), ("META", "Stocks"), ("TSLA", "Stocks"), ("JPM", "Stocks"),
    ("XOM", "Stocks"), ("JNJ", "Stocks"), ("WMT", "Stocks"), ("COST", "Stocks"),
    ("SPY", "ETF"), ("QQQ", "ETF"), ("IWM", "ETF"), ("XLE", "ETF"),
    ("GLD", "Commodity ETF"), ("TLT", "Bond ETF"), ("BND", "Bond ETF"), ("SMH", "ETF"),
    ("VTSAX", "Mutual fund"), ("FXAIX", "Mutual fund"), ("FZROX", "Mutual fund"),
    ("BTC-USD", "Crypto"), ("ETH-USD", "Crypto"), ("EURUSD=X", "FX"),
]


def _num(v, default=None):
    if isinstance(v, dict):
        v = v.get("raw")
    return v if isinstance(v, (int, float)) else default


def yahoo_session():
    s = creq.Session(impersonate="chrome")
    s.get("https://fc.yahoo.com", timeout=20)
    crumb = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=20).text.strip()
    return s, crumb


def yahoo_data(session, crumb, symbol):
    u = ("https://query1.finance.yahoo.com/v10/finance/quoteSummary/"
         f"{symbol}?modules=recommendationTrend,upgradeDowngradeHistory,financialData&crumb={crumb}")
    r = session.get(u, timeout=30)
    if r.status_code != 200:
        return {}
    try:
        res = (r.json().get("quoteSummary", {}).get("result") or [{}])[0]
    except Exception:
        return {}
    out = {}
    trend = (res.get("recommendationTrend", {}) or {}).get("trend") or []
    if trend:
        out["trend"] = trend[0]
    fd = res.get("financialData", {}) or {}
    out.update({
        "current_price": _num(fd.get("currentPrice")),
        "target_mean": _num(fd.get("targetMeanPrice")),
        "target_high": _num(fd.get("targetHighPrice")),
        "target_low": _num(fd.get("targetLowPrice")),
        "recommendation_mean": _num(fd.get("recommendationMean")),
        "recommendation_key": fd.get("recommendationKey"),
        "n_analysts": _num(fd.get("numberOfAnalystOpinions")),
    })
    hist = (res.get("upgradeDowngradeHistory", {}) or {}).get("history") or []
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=180)
    actions = []
    for h in hist:
        try:
            when = dt.datetime.fromtimestamp(int(h["epochGradeDate"]), dt.timezone.utc)
        except Exception:
            continue
        if when < cutoff:
            continue
        actions.append({
            "date": when.date().isoformat(),
            "firm": h.get("firm"),
            "action": h.get("action"),
            "from": h.get("fromGrade"),
            "to": h.get("toGrade"),
            "target": h.get("currentPriceTarget") or None,
            "target_action": h.get("priceTargetAction"),
        })
    actions.sort(key=lambda a: a["date"], reverse=True)
    out["actions"] = actions
    return out


def nasdaq_data(symbol):
    base = "https://api.nasdaq.com/api/analyst"
    h = {"Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.9"}
    out = {}
    try:
        r = creq.get(f"{base}/{symbol}/ratings", impersonate="chrome", headers=h, timeout=30)
        if r.status_code == 200:
            out["ratings"] = (r.json().get("data") or {})
    except Exception:
        pass
    try:
        r = creq.get(f"{base}/{symbol}/targetprice", impersonate="chrome", headers=h, timeout=30)
        if r.status_code == 200:
            d = (r.json().get("data") or {})
            out["target"] = d.get("consensusOverview") or {}
            out["history"] = (d.get("historicalConsensus") or [])[:6]
    except Exception:
        pass
    return out


def build_row(symbol, cls, y, n):
    t = y.get("trend") or {}
    nb = int(t.get("strongBuy", 0)); b = int(t.get("buy", 0)); hd = int(t.get("hold", 0))
    s_ = int(t.get("sell", 0)); ss = int(t.get("strongSell", 0))
    total = nb + b + hd + s_ + ss
    y_score = ((2 * nb + b - s_ - 2 * ss) / total) if total else None
    tg = n.get("target") or {}
    nbuy, nhold, nsell = tg.get("buy"), tg.get("hold"), tg.get("sell")
    ntotal = sum(x for x in (nbuy, nhold, nsell) if isinstance(x, int))
    n_score = ((nbuy - nsell) / ntotal) if ntotal else None
    scores = [x for x in (y_score, n_score) if x is not None]
    composite = sum(scores) / len(scores) if scores else None
    price = y.get("current_price")
    target = y.get("target_mean") or tg.get("priceTarget")
    upside = ((target / price - 1) * 100) if (price and target) else None
    actions = y.get("actions") or []
    status = "ok" if (total or ntotal) else "no_coverage"
    return {
        "symbol": symbol, "asset_class": cls, "status": status,
        "yahoo_trend": t or None, "yahoo_total": total or None,
        "yahoo_mean": y.get("recommendation_mean"), "yahoo_key": y.get("recommendation_key"),
        "nasdaq_consensus": n.get("ratings", {}).get("meanRatingType"),
        "nasdaq_counts": {"buy": nbuy, "hold": nhold, "sell": nsell},
        "price": price, "target_mean": target,
        "target_low": y.get("target_low") or tg.get("lowPriceTarget"),
        "target_high": y.get("target_high") or tg.get("highPriceTarget"),
        "upside_pct": upside, "composite": composite,
        "recent_actions": actions[:12],
        "latest_action_date": actions[0]["date"] if actions else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(OUT_JSON))
    ap.add_argument("--symbols", default="")
    ap.add_argument("--delay", type=float, default=0.6)
    a = ap.parse_args()
    universe = UNIVERSE
    if a.symbols:
        want = {x.strip().upper() for x in a.symbols.split(",") if x.strip()}
        universe = [(s, c) for s, c in UNIVERSE if s.upper() in want]

    s, crumb = yahoo_session()
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for sym, cls in universe:
        y = yahoo_data(s, crumb, sym)
        n = nasdaq_data(sym)
        row = build_row(sym, cls, y, n)
        rows.append(row)
        print(f"{sym:<9} {cls:<12} {row['status']:<12} composite={row['composite']} "
              f"actions={len(row['recent_actions'])}")
        time.sleep(a.delay)

    stamp = now.strftime("%Y-%m-%dT%H%MZ")
    payload = {
        "generated_utc": now.isoformat(),
        "window_days": 180,
        "sources": ["Yahoo Finance quoteSummary (crumb)", "Nasdaq analyst API"],
        "disclaimer": "Analyst ratings are opinions, not investment advice. Dates are source timestamps.",
        "rows": rows,
    }
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = [f"# HARVEST — analyst endorsements ({stamp})", "",
          "Sources: Yahoo Finance (`recommendationTrend`, `upgradeDowngradeHistory`, "
          "`financialData`) and Nasdaq public analyst endpoints. Window: last 180 days.",
          "Ratings are opinions, not advice. `no_coverage` is reported, not guessed.", "",
          "## Consensus by asset class", "",
          "| Symbol | Class | Composite (-1..1) | Yahoo trend (SB/B/H/S/SS) | Nasdaq (B/H/S) | Target | Upside | Latest action |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        t = r["yahoo_trend"] or {}
        trend = (f"{t.get('strongBuy',0)}/{t.get('buy',0)}/{t.get('hold',0)}/"
                 f"{t.get('sell',0)}/{t.get('strongSell',0)}") if t else "—"
        nc = r["nasdaq_counts"]
        ncs = f"{nc['buy'] or 0}/{nc['hold'] or 0}/{nc['sell'] or 0}" if any(
            isinstance(nc[k], int) for k in nc) else "—"
        comp = "—" if r["composite"] is None else f"{r['composite']:+.2f}"
        up = "—" if r["upside_pct"] is None else f"{r['upside_pct']:+.1f}%"
        tgt = "—" if r["target_mean"] is None else f"${r['target_mean']:.2f}"
        md.append(f"| {r['symbol']} | {r['asset_class']} | {comp} | {trend} | {ncs} | {tgt} | {up} | {r['latest_action_date'] or '—'} |")
    md += ["", "## Recent rating actions (last 180 days)", ""]
    for r in rows:
        if not r["recent_actions"]:
            continue
        md.append(f"### {r['symbol']} ({r['asset_class']})")
        for x in r["recent_actions"][:6]:
            md.append(f"- {x['date']} — {x['firm']}: {x['action']} "
                      f"{x['from'] or '?'} → {x['to'] or '?'}"
                      + (f" (PT {x['target']})" if x.get("target") else ""))
        md.append("")
    md += ["## Coverage gaps", ""]
    gaps = [r["symbol"] for r in rows if r["status"] == "no_coverage"]
    md.append(", ".join(gaps) if gaps else "none")
    out_md = OUT_MD_DIR / f"HARVEST_{now.strftime('%Y-%m-%dT%H%MZ')}.MD"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"\nwrote {out_md.name} and {a.json} | ok={ok}/{len(rows)}")


if __name__ == "__main__":
    main()
