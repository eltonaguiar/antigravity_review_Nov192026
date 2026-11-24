#!/usr/bin/env python3
"""CROWD LAYER — prediction-market signals, with a mandatory transmission mechanism.

Two layers, deliberately separate:

  Layer A  DIRECT PER-SYMBOL MATCH.  A market whose text names a specific ticker or company.
           Rare. Every row records the market id and a match_confidence of
           exact | ticker_mention | semantic. Nothing is matched by fuzzy guesswork.

  Layer B  EVENT-TO-ASSET MAPPING.  A curated table linking an event market to an asset class
           through a stated TRANSMISSION MECHANISM, with an expected SIGN, a CONFIDENCE, and a
           historical beta where one can be estimated.

RULE ENFORCED IN CODE: a Layer B row without a mechanism string is rejected. A bare correlation
is never emitted. Beta is null with an explicit reason when it cannot be estimated from data we
actually hold — see beta.status in the output.

Endpoints (free, no credential; verified 2026-11-24):
  Polymarket Gamma  https://gamma-api.polymarket.com/markets?limit=...
  Kalshi public     https://api.elections.kalshi.com/trade-api/v2/markets?limit=...&status=open

Rate limiting: serial requests, >=1.1 s apart, single-shot per run. No pagination storms.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "harvest-crowd/1.0 (research; contact ejaguiar1@gmail.com)"
POLY = "https://gamma-api.polymarket.com/markets"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2/markets"
PACE = 1.1

# ---------------------------------------------------------------- Layer B definition
# Every row MUST carry a mechanism. `beta` is None unless we can actually estimate it,
# in which case it carries {value, ci_low, ci_high, n, method}.
LAYER_B = [
    {
        "event_family": "Fed policy rate path",
        "example_market": '"Will the Fed cut rates at the December meeting?"',
        "mapped_asset_class": "BOND",
        "mapped_proxies": ["TLT", "IEF", "SHY"],
        "mechanism": ("A higher implied probability of a cut lowers expected front-end rates; "
                      "duration is the sensitivity of a bond's price to that path, so long-duration "
                      "Treasuries gain mechanically more than short-duration ones. Transmission is "
                      "direct via the discount rate, not via earnings."),
        "expected_sign": "probability(cut) up  =>  TLT price up",
        "confidence": "high",
        "beta": None,
        "beta_status": "not_estimable_here: needs a matched time series of market-implied "
                       "probabilities and bond returns; we hold neither, and inventing a number "
                       "would breach the no-fabrication rule.",
    },
    {
        "event_family": "CPI / inflation surprise",
        "example_market": '"Will CPI come in above 3.0%?"',
        "mapped_asset_class": "BOND",
        "mapped_proxies": ["TLT", "TIP", "GLD"],
        "mechanism": ("An inflation surprise raises the expected policy path and the inflation risk "
                      "premium, pushing nominal yields up and bond prices down; TIPS reprice partly "
                      "through the breakeven rather than the real rate, so the sign is smaller; gold "
                      "responds to the real-rate component."),
        "expected_sign": "probability(high CPI) up  =>  TLT down; TIP down less; GLD ambiguous",
        "confidence": "medium",
        "beta": None,
        "beta_status": "not_estimable_here: same missing series problem as the Fed row.",
    },
    {
        "event_family": "Recession probability",
        "example_market": '"Will there be a US recession declared before 2027?"',
        "mapped_asset_class": "EQUITY_FACTOR",
        "mapped_proxies": ["SPY", "XLP", "XLU"],
        "mechanism": ("Recession odds reprice the equity risk premium and the earnings path; "
                      "defensive sectors (staples, utilities) have lower earnings beta to the cycle, "
                      "so the long-short SPY vs XLP spread is the cleaner expression than SPY alone."),
        "expected_sign": "probability(recession) up  =>  SPY down relative to XLP",
        "confidence": "medium",
        "beta": None,
        "beta_status": "not_estimable_here.",
    },
    {
        "event_family": "Bitcoin price threshold",
        "example_market": '"Will BTC be above $100,000 on 2026-12-31?"',
        "mapped_asset_class": "CRYPTO",
        "mapped_proxies": ["BTC-USD"],
        "mechanism": ("A threshold market on the same underlying is a risk-neutral probability of "
                      "the terminal price; it transmits to spot only through the same underlying, so "
                      "it is a repricing of the same variable, not a leading indicator."),
        "expected_sign": "probability(BTC > K) up  =>  BTC spot up",
        "confidence": "high",
        "beta": None,
        "beta_status": "near-tautological: the market IS the underlying. A beta would mostly "
                       "measure the market's own settlement, not a causal transmission.",
    },
    {
        "event_family": "Equity index range / year-end level",
        "example_market": '"Will the S&P 500 close above 6500 this year?"',
        "mapped_asset_class": "EQUITY",
        "mapped_proxies": ["SPY"],
        "mechanism": ("Index level markets settle on the same index they reference, so the mapping "
                      "is definitional. Useful as a crowd-priced scenario distribution; not an "
                      "independent signal about the index."),
        "expected_sign": "probability(S&P > K) up  =>  SPY up (definitional)",
        "confidence": "high",
        "beta": None,
        "beta_status": "not meaningful - definitional identity, not a transmission.",
    },
]


def http_json(url: str, timeout: int = 40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), r.status, None
    except urllib.error.HTTPError as e:
        return None, e.code, f"HTTP {e.code}"
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}"


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def poly_rows(limit: int):
    payload, status, err = http_json(f"{POLY}?limit={limit}&closed=false&active=true")
    if status != 200 or not isinstance(payload, list):
        return [], {"source": "polymarket_gamma", "status": "UNAVAILABLE", "http": status,
                    "error": err, "url": f"{POLY}?limit={limit}&closed=false&active=true"}
    rows = []
    for m in payload:
        prices = m.get("outcomePrices")
        try:
            prices = json.loads(prices) if isinstance(prices, str) else prices
        except Exception:
            prices = None
        yes = None
        if isinstance(prices, list) and prices:
            yes = num(prices[0])
        rows.append({
            "venue": "polymarket",
            "market_id": m.get("id") or m.get("conditionId"),
            "question": m.get("question"),
            "slug": m.get("slug"),
            "implied_prob": yes,
            "bid": num(m.get("bestBid")),
            "ask": num(m.get("bestAsk")),
            "spread": (num(m.get("bestAsk")) - num(m.get("bestBid"))
                       if num(m.get("bestAsk")) is not None and num(m.get("bestBid")) is not None else None),
            "volume": num(m.get("volumeNum") or m.get("volume")),
            "liquidity": num(m.get("liquidityNum") or m.get("liquidity")),
            "open_interest": None,   # Polymarket Gamma does not expose OI on this endpoint
            "end_date": m.get("endDate"),
            "url": f"https://polymarket.com/event/{m.get('slug')}" if m.get("slug") else None,
        })
    return rows, {"source": "polymarket_gamma", "status": "OK", "http": status, "rows": len(rows)}


def kalshi_rows(limit: int):
    payload, status, err = http_json(f"{KALSHI}?limit={limit}&status=open")
    if status != 200 or not isinstance(payload, dict):
        return [], {"source": "kalshi", "status": "UNAVAILABLE", "http": status, "error": err,
                    "url": f"{KALSHI}?limit={limit}&status=open"}
    ms = payload.get("markets", [])
    rows = []
    for m in ms:
        # Kalshi renamed its fields (verified 2026-11-24): yes_bid -> yes_bid_dollars,
        # yes_ask -> yes_ask_dollars, volume -> volume_fp, open_interest -> open_interest_fp.
        # Reading only the old names produced 200 rows of NULLs. Accept both, prefer new.
        bid = num(m.get("yes_bid_dollars") if m.get("yes_bid_dollars") is not None else m.get("yes_bid"))
        ask = num(m.get("yes_ask_dollars") if m.get("yes_ask_dollars") is not None else m.get("yes_ask"))
        if bid is not None and bid > 1: bid = bid / 100.0
        if ask is not None and ask > 1: ask = ask / 100.0
        mid = ((bid + ask) / 2 / 100) if (bid is not None and ask is not None) else None
        rows.append({
            "venue": "kalshi",
            "market_id": m.get("ticker"),
            "question": m.get("title"),
            "implied_prob": mid,
            "bid": bid / 100 if bid is not None else None,
            "ask": ask / 100 if ask is not None else None,
            "spread": (ask - bid) if (bid is not None and ask is not None) else None,
            "volume": num(m.get("volume_fp") if m.get("volume_fp") is not None else m.get("volume")),
            "liquidity": num(m.get("liquidity")),
            "open_interest": num(m.get("open_interest_fp") if m.get("open_interest_fp") is not None else m.get("open_interest")),
            "end_date": m.get("close_time"),
            "url": f"https://kalshi.com/markets/{m.get('event_ticker','')}".rstrip("/"),
        })
    return rows, {"source": "kalshi", "status": "OK", "http": status, "rows": len(rows)}


def layer_a(rows, symbols):
    """Direct per-symbol matches. Conservative: exact ticker token, else explicit company name.

    Case-sensitive on purpose. A first draft matched lowercased substrings and produced four
    false positives, every one of them the ticker 'DE' (Deere) appearing inside the Spanish
    preposition in tennis market titles ("Alvarez Valdes, yes Luciano ..."). A ticker must match
    as an UPPERCASE token in the original text, or not at all.
    """
    import re
    tick_re = re.compile(r"(?<![A-Za-z0-9])([A-Z]{1,5})(?![A-Za-z0-9])")
    out = []
    for r in rows:
        q = (r.get("question") or "")
        if not q:
            continue
        tokens = set(tick_re.findall(q))
        hit = next((s for s in symbols if s in tokens), None)
        if hit:
            out.append({**r, "matched_symbol": hit, "match_confidence": "exact",
                        "match_basis": f"uppercase ticker token '{hit}' in market title"})
            continue
        ql = q.lower()
        for sym, name in symbols.items():
            nm = (name or "").strip()
            if len(nm) < 8:
                continue
            if re.search(rf"(?<![a-z0-9]){re.escape(nm.lower())}(?![a-z0-9])", ql):
                out.append({**r, "matched_symbol": sym, "match_confidence": "ticker_mention",
                            "match_basis": f"company name '{nm}' in market title"})
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default="docs/data/harvest_signals.json")
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parent / "out"))
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()

    feed = json.loads(Path(a.feed).read_text())
    symbols = {s["symbol"].upper(): s.get("name", "") for s in feed["signals"]}
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)

    poly, poly_src = poly_rows(a.limit)
    time.sleep(PACE)
    kal, kal_src = kalshi_rows(a.limit)

    all_rows = poly + kal
    la = layer_a(all_rows, symbols)

    # Enforce the mechanism rule rather than trusting the table.
    rejected = [r["event_family"] for r in LAYER_B if not r.get("mechanism")]
    lb = [r for r in LAYER_B if r.get("mechanism")]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "consensus_feed": a.feed,
        "sources": [poly_src, kal_src],
        "layer_a_direct_matches": la,
        "layer_a_count": len(la),
        "layer_b_event_mappings": lb,
        "layer_b_rejected_missing_mechanism": rejected,
        "rules": {
            "layer_a": "Only exact ticker tokens or explicit company names. No fuzzy matching. "
                       "match_confidence recorded per row.",
            "layer_b": "Every row carries a transmission mechanism, an expected sign and a "
                       "confidence. A row without a mechanism is rejected in code.",
            "beta": "null unless estimable from data actually held; beta_status states the reason. "
                    "Bare correlations are never emitted.",
        },
        "markets": all_rows,
        "market_count": len(all_rows),
        "sample_of_unmatched_markets": [
            {"venue": r["venue"], "question": r["question"]} for r in all_rows[:8]
        ],
    }
    (outdir / "crowd_layer.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(f"  polymarket: {poly_src['status']} rows={len(poly)}")
    print(f"  kalshi    : {kal_src['status']} rows={len(kal)}")
    print(f"  layer A direct matches: {len(la)}")
    for r in la[:8]:
        print(f"    {r['venue']:<10} {r['matched_symbol']:<8} {r['match_confidence']:<14} "
              f"p={r['implied_prob']}  {(r['question'] or '')[:52]}")
    print(f"  layer B mappings: {len(lb)}  rejected(no mechanism): {len(rejected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
