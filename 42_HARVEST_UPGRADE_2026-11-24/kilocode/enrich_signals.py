#!/usr/bin/env python3
import json, os, sys, time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R
import requests
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data" / "harvest_signals.json"
RAW = Path(__file__).resolve().parent / "evidence" / "finnhub_recommendation_raw.jsonl"
TOKEN = os.environ.get("FINNHUB", "").strip()
if not TOKEN:
    print("BLOCKED: FINNHUB env var not set"); raise SystemExit(2)
d = json.loads(DATA.read_text()); RAW.write_text("")
ok = 0; fails = []
def fetch(sym):
    url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={sym}&token={TOKEN}"
    for attempt in range(4):
        r = requests.get(url, timeout=25)
        if r.status_code == 200: return r.json()
        if r.status_code == 429: time.sleep(8*(attempt+1)); continue
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:100]}")
    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:100]}")
for s in d["signals"]:
    if not s.get("has_consensus"):
        s["reason_code"] = "EMPTY_RESPONSE"; continue
    try:
        rows = sorted(fetch(s["symbol"]), key=lambda x: x["period"], reverse=True)
        RAW.write_text(RAW.read_text() + json.dumps({"symbol": s["symbol"], "rows": rows}) + "\n")
        now = next((x for x in rows if x["period"] == s["period"]), rows[0])
        prior = next((x for x in rows if x["period"] < now["period"]), None)
        conv = lambda x: {"strong_buy": x["strongBuy"], "buy": x["buy"], "hold": x["hold"],
                          "sell": x["sell"], "strong_sell": x["strongSell"]}
        now_c = conv(now); s.update(now_c); n_now = R.counts_total(**now_c); s["n_now"] = n_now
        if prior:
            p = conv(prior)
            for k, v in p.items(): s[f"prior_{k}"] = v
            s["n_prior"] = R.counts_total(**p)
            s["prior_buy_side_pct"] = round(100 * R.buy_side_of(**p), 1)
            delta = 100 * (R.buy_side_of(**now_c) - R.buy_side_of(**p))
            moves = R.bucket_moves(p, now_c)
            s["delta_pp"] = round(delta, 1)
            s["threshold_pp"] = round(max(R.RULE["trend"]["min_abs_pp"], 100.0/n_now), 2)
            s["bucket_moves"] = moves
            s["churn_flag"] = "CLEAN" if s["n_prior"] == n_now else "CHURN_CONTAMINATED"
            s["direction"] = R.direction_for(delta, n_now, moves)
        else:
            s.update({"n_prior": None, "delta_pp": None, "threshold_pp": None,
                      "bucket_moves": None, "churn_flag": "UNKNOWN", "direction": "STABLE"})
        s["analysts"] = n_now
        s["buy_side_pct"] = round(100 * R.buy_side_of(**now_c), 1)
        s["consensus_score"] = round(R.score_of(**now_c), 3)
        s["consensus"] = R.label_for_counts(**now_c)
        s["reason_code"] = "STALE_OK"
        ok += 1; time.sleep(1.05)
    except Exception as e:
        fails.append((s["symbol"], str(e)[:90]))
        s["reason_code"] = "RATE_LIMITED_429" if "429" in str(e) else "NO_COVERAGE_VENDOR"
        s["churn_flag"] = "UNKNOWN"
for e in d.get("errors", []):
    e["reason_code"] = ("ACCESS_DENIED_403" if e.get("http") == 403 else
                        "RATE_LIMITED_429" if e.get("http") == 429 else "EMPTY_RESPONSE")
for cls, c in d["coverage_by_asset_class"].items():
    c["reason_code"] = ("STALE_OK" if c["with_consensus"] else
                        "ACCESS_DENIED_403" if cls == "MUTUAL_FUND" else "NO_COVERAGE_STRUCTURAL")
cnt = Counter(s["direction"] for s in d["signals"] if s.get("has_consensus"))
lc = Counter(s["consensus"] for s in d["signals"] if s.get("has_consensus"))
d["crowd_consensus"]["label_counts"] = dict(lc)
d["crowd_consensus"]["direction_counts"] = dict(cnt)
d["crowd_consensus"]["net_upgrades_minus_downgrades"] = cnt.get("IMPROVING",0)-cnt.get("DETERIORATING",0)
d["rule"] = R.RULE; d["reason_codes"] = list(R.REASON_CODES)
d["enriched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
DATA.write_text(json.dumps(d, indent=2)+"\n")
print(f"enriched={ok} fails={len(fails)} counts={dict(cnt)}")
