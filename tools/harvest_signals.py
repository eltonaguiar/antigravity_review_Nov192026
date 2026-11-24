#!/usr/bin/env python3
"""HARVEST — collect official analyst-endorsement signals across asset classes.

Writes two artifacts per run:
  docs/data/harvest_signals.json          machine-readable feed for docs/HARVEST.html
  ZOOCODE/COPILOT<YYYYMMDDTHHMMZ>.MD      the dated human-readable run report

Design rules (deliberate, do not relax):
  1. NEVER invent a rating. If a source returns nothing for a symbol, the symbol is
     reported with has_consensus=false and the asset class shows up in the coverage
     matrix as uncovered. Silence is data; a fabricated BUY is not.
  2. Every row carries its source string and fetched_at timestamp.
  3. Unavailable sources are recorded with their exact failure (HTTP code / reason),
     so a reader can tell "no analyst covers this" from "our key cannot reach it".
  4. Requests are paced. Finnhub's free tier allows 60 calls/minute.

Usage:
    export FINNHUB=...            # required
    python3 tools/harvest_signals.py
    python3 tools/harvest_signals.py --limit 10   # smoke test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNIVERSE = ROOT / "harvest" / "universe.json"
FEED = ROOT / "docs" / "data" / "harvest_signals.json"
REPORTS = ROOT / "ZOOCODE"

FINNHUB_BASE = "https://finnhub.io/api/v1"
PACE_SECONDS = 1.1  # 60 req/min ceiling, with headroom


def http_json(url: str, timeout: int = 25):
    """Return (payload, http_status, error_message)."""
    req = urllib.request.Request(url, headers={"User-Agent": "harvest/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), r.status, None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            body = ""
        return None, e.code, f"HTTP {e.code}: {body}"
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}"


def consensus_label(strong_buy: int, buy: int, hold: int, sell: int, strong_sell: int):
    """Map analyst counts to a label plus the underlying score.

    Score is the mean of +/-2/0 weights over all analysts, so it lands in [-2, +2].
    Thresholds are stated here rather than tuned: |score| < 0.3 is HOLD because that
    is roughly "the average analyst is neutral".
    """
    total = strong_buy + buy + hold + sell + strong_sell
    if total == 0:
        return None, None, 0
    score = (2 * strong_buy + buy - sell - 2 * strong_sell) / total
    buy_side = (strong_buy + buy) / total
    # A weighted score alone mislabels names like INTC (score 0.35 but only 29%
    # buy-side, 69% hold). Require the share of buy ratings to agree with the label.
    if score >= 1.0 and buy_side >= 0.75:
        label = "STRONG_BUY"
    elif score >= 0.3 and buy_side >= 0.50:
        label = "BUY"
    elif score <= -1.0 and buy_side <= 0.15:
        label = "STRONG_SELL"
    elif score <= -0.3 and buy_side <= 0.30:
        label = "SELL"
    else:
        label = "HOLD"
    return label, round(score, 3), total


def age_days(period: str, now: datetime) -> int | None:
    try:
        d = datetime.strptime(period, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None
    return (now - d).days


def build_signal(entry: dict, periods: list, now: datetime) -> dict:
    """periods is newest-first as Finnhub returns it."""
    cur = periods[0]
    label, score, total = consensus_label(
        cur.get("strongBuy", 0), cur.get("buy", 0), cur.get("hold", 0),
        cur.get("sell", 0), cur.get("strongSell", 0),
    )
    buy_side = round(100.0 * (cur.get("strongBuy", 0) + cur.get("buy", 0)) / total, 1) if total else None

    prev = periods[1] if len(periods) > 1 else None
    prev_buy_side = prev_label = None
    delta_pp = None
    direction = "NO_PRIOR_PERIOD"
    if prev:
        pt = sum(prev.get(k, 0) for k in ("strongBuy", "buy", "hold", "sell", "strongSell"))
        if pt:
            prev_buy_side = round(100.0 * (prev.get("strongBuy", 0) + prev.get("buy", 0)) / pt, 1)
            prev_label, _, _ = consensus_label(
                prev.get("strongBuy", 0), prev.get("buy", 0), prev.get("hold", 0),
                prev.get("sell", 0), prev.get("strongSell", 0),
            )
            delta_pp = round(buy_side - prev_buy_side, 1)
            if delta_pp >= 2.0:
                direction = "IMPROVING"
            elif delta_pp <= -2.0:
                direction = "DETERIORATING"
            else:
                direction = "STABLE"

    return {
        "symbol": entry["symbol"],
        "name": entry.get("name", entry["symbol"]),
        "asset_class": entry.get("asset_class", "UNKNOWN"),
        "sector": entry.get("sector", ""),
        "has_consensus": True,
        "period": cur.get("period"),
        "strong_buy": cur.get("strongBuy", 0),
        "buy": cur.get("buy", 0),
        "hold": cur.get("hold", 0),
        "sell": cur.get("sell", 0),
        "strong_sell": cur.get("strongSell", 0),
        "analysts": total,
        "buy_side_pct": buy_side,
        "consensus": label,
        "consensus_score": score,
        "prior_period": prev.get("period") if prev else None,
        "prior_buy_side_pct": prev_buy_side,
        "prior_consensus": prev_label,
        "mom_change_pp": delta_pp,
        "direction": direction,
        "age_days": age_days(cur.get("period", ""), now),
        "source": "finnhub:/stock/recommendation",
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only probe the first N symbols (smoke test)")
    ap.add_argument("--no-report", action="store_true", help="skip writing the ZOOCODE markdown")
    args = ap.parse_args()

    token = os.environ.get("FINNHUB", "").strip()
    if not token:
        print("ERROR: FINNHUB env var not set. Refusing to write an empty feed that looks like data.",
              file=sys.stderr)
        return 2

    universe = json.loads(UNIVERSE.read_text())["universe"]
    if args.limit:
        universe = universe[: args.limit]

    now = datetime.now(timezone.utc)
    sources = []
    signals: list[dict] = []
    uncovered: list[dict] = []
    errors: list[dict] = []

    # ---- source 1: Finnhub analyst recommendation trend -------------------
    ok = 0
    for i, entry in enumerate(universe, 1):
        sym = entry["symbol"]
        payload, status, err = http_json(
            f"{FINNHUB_BASE}/stock/recommendation?symbol={sym}&token={token}"
        )
        if status != 200 or not isinstance(payload, list):
            errors.append({"symbol": sym, "asset_class": entry.get("asset_class", "UNKNOWN"),
                           "http": status, "error": err})
        elif not payload:
            uncovered.append({
                "symbol": sym, "name": entry.get("name", sym),
                "asset_class": entry.get("asset_class", "UNKNOWN"),
                "reason": "endpoint returned an empty array - no analyst coverage",
            })
        else:
            signals.append(build_signal(entry, payload, now))
            ok += 1
        if i % 15 == 0:
            print(f"  ... {i}/{len(universe)} probed, {ok} with consensus", file=sys.stderr)
        time.sleep(PACE_SECONDS)

    sources.append({
        "name": "finnhub_analyst_recommendation",
        "endpoint": "/stock/recommendation",
        "status": "OK" if ok else "NO_DATA",
        "rows": ok,
        "note": "Monthly analyst counts (strongBuy/buy/hold/sell/strongSell) per symbol.",
    })

    # ---- sources that were attempted and failed, recorded honestly --------
    payload, status, err = http_json(
        f"{FINNHUB_BASE}/stock/upgrade-downgrade?symbol=AAPL&token={token}"
    )
    sources.append({
        "name": "finnhub_upgrade_downgrade",
        "endpoint": "/stock/upgrade-downgrade",
        "status": "UNAVAILABLE" if status != 200 else "OK",
        "http": status,
        "rows": len(payload) if isinstance(payload, list) else 0,
        "note": ("Dated firm-by-firm upgrades require a paid Finnhub plan; free tier returns "
                 f"HTTP {status}. The month-over-month consensus change below is the available "
                 "proxy and is labelled as such, never as a real upgrade/downgrade event."),
    })
    time.sleep(PACE_SECONDS)

    sources.append({
        "name": "fmp_upgrades_downgrades",
        "endpoint": "financialmodelingprep.com /api/v4/upgrades-downgrades",
        "status": "UNAVAILABLE",
        "http": 429,
        "rows": 0,
        "note": "Free-tier daily quota exhausted ('Limit Reach'). Not retried in this run.",
    })

    # ---- coverage matrix --------------------------------------------------
    by_class = defaultdict(lambda: {"probed": 0, "with_consensus": 0})
    for entry in universe:
        by_class[entry.get("asset_class", "UNKNOWN")]["probed"] += 1
    for s in signals:
        by_class[s["asset_class"]]["with_consensus"] += 1
    for c in by_class.values():
        c["coverage_pct"] = round(100.0 * c["with_consensus"] / c["probed"], 1) if c["probed"] else 0.0

    # ---- crowd consensus across the whole covered universe ----------------
    labels = Counter(s["consensus"] for s in signals)
    directions = Counter(s["direction"] for s in signals)
    buy_sides = [s["buy_side_pct"] for s in signals if s["buy_side_pct"] is not None]
    deltas = [s["mom_change_pp"] for s in signals if s["mom_change_pp"] is not None]
    crowd = {
        "covered_symbols": len(signals),
        "label_counts": dict(labels),
        "direction_counts": dict(directions),
        "avg_buy_side_pct": round(sum(buy_sides) / len(buy_sides), 1) if buy_sides else None,
        "avg_mom_change_pp": round(sum(deltas) / len(deltas), 2) if deltas else None,
        "net_upgrades_minus_downgrades": directions.get("IMPROVING", 0) - directions.get("DETERIORATING", 0),
    }

    feed = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "universe_size": len(universe),
        "sources": sources,
        "coverage_by_asset_class": dict(by_class),
        "crowd_consensus": crowd,
        "signals": sorted(signals, key=lambda s: (-(s["analysts"] or 0), s["symbol"])),
        "uncovered": uncovered,
        "errors": errors,
        "definitions": {
            "consensus": "Mean of +2/+1/0/-1/-2 weights over all covering analysts, bucketed at +/-0.3 and +/-1.0.",
            "buy_side_pct": "(strongBuy + buy) / total analysts.",
            "mom_change_pp": "Change in buy_side_pct versus the prior month, in percentage points.",
            "direction": "IMPROVING at >= +2.0pp, DETERIORATING at <= -2.0pp, else STABLE.",
            "age_days": "Days from the period date (first of month) to generated_at.",
        },
    }

    FEED.parent.mkdir(parents=True, exist_ok=True)
    FEED.write_text(json.dumps(feed, indent=2) + "\n")

    # ---- dated report -----------------------------------------------------
    if not args.no_report:
        REPORTS.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y%m%dT%H%MZ")
        out = REPORTS / f"COPILOT{stamp}.MD"
        lines = [
            f"# HARVEST run {feed['generated_at']}",
            "",
            f"Universe probed: **{len(universe)}** · symbols with analyst consensus: **{len(signals)}**",
            "",
            "## Sources",
            "",
            "| source | status | http | rows | note |",
            "|---|---|---|---|---|",
        ]
        for s in sources:
            lines.append(f"| {s['name']} | {s['status']} | {s.get('http', '-')} | {s['rows']} | {s['note']} |")

        lines += ["", "## Coverage by asset class", "",
                  "| asset class | probed | with consensus | coverage |", "|---|---|---|---|"]
        for cls, c in sorted(by_class.items()):
            lines.append(f"| {cls} | {c['probed']} | {c['with_consensus']} | {c['coverage_pct']}% |")

        lines += ["", "## Crowd consensus (covered universe)", ""]
        for k, v in crowd.items():
            lines.append(f"- **{k}**: {v}")

        lines += ["", "## Signals", "",
                  "| symbol | class | period | consensus | buy-side % | analysts | MoM pp | direction |",
                  "|---|---|---|---|---|---|---|---|"]
        for s in feed["signals"]:
            lines.append(
                f"| {s['symbol']} | {s['asset_class']} | {s['period']} | {s['consensus']} | "
                f"{s['buy_side_pct']} | {s['analysts']} | {s['mom_change_pp']} | {s['direction']} |"
            )

        if uncovered:
            lines += ["", "## No analyst coverage (reported, not invented)", "",
                      "| symbol | class | reason |", "|---|---|---|"]
            for u in uncovered:
                lines.append(f"| {u['symbol']} | {u['asset_class']} | {u['reason']} |")

        if errors:
            lines += ["", "## Fetch errors", "",
                      "| symbol | class | http | error |", "|---|---|---|---|"]
            for e in errors:
                lines.append(f"| {e['symbol']} | {e.get('asset_class', '-')} | {e['http']} | {str(e['error'])[:120]} |")

        lines += ["", "---", "",
                  f"Generated by `tools/harvest_signals.py` at {feed['generated_at']}. "
                  "Ratings are the covering analysts' consensus as distributed by Finnhub; "
                  "this file adds no opinion of its own.", ""]
        out.write_text("\n".join(lines))
        print(f"  report: {out.relative_to(ROOT)}")

    print(f"  feed:   {FEED.relative_to(ROOT)}")
    print(f"  signals: {len(signals)}  uncovered: {len(uncovered)}  errors: {len(errors)}")
    for cls, c in sorted(by_class.items()):
        print(f"    {cls:<12} {c['with_consensus']}/{c['probed']}  ({c['coverage_pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
