#!/usr/bin/env python3
"""Build the /audit analyst bridge fragment from HARVEST signals (no firm/person invention)."""
import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "data" / "harvest_signals.json"
OUT = ROOT / "docs" / "data" / "audit_analyst_bridge.json"

d = json.loads(SRC.read_text())
rows = [s for s in d["signals"] if s.get("has_consensus")]
map_dir = {"STRONG_BUY": "LONG", "BUY": "LONG", "HOLD": "NEUTRAL", "SELL": "SHORT", "STRONG_SELL": "SHORT"}
calls = []
for s in rows:
    calls.append({
        "symbol": s["symbol"], "entity_type": "sell_side_consensus", "firm": None,
        "direction": map_dir.get(s["consensus"], "NEUTRAL"),
        "consensus": s["consensus"], "consensus_score": s["consensus_score"],
        "buy_side_pct": s["buy_side_pct"], "analysts": s["analysts"],
        "period": s["period"], "source": s.get("source"), "published_at": s.get("published_at"),
        "rule": s.get("rule"), "cost_bps": s.get("cost_bps"), "benchmark": s.get("benchmark"),
    })
cnt = Counter(s["consensus"] for s in rows)
total_analysts = sum(s["analysts"] for s in rows)
out = {
    "updated_at": max(s.get("published_at") or "" for s in rows),
    "total_active": len(calls),
    "total_predictions": len(rows),
    "total_analysts": total_analysts,
    "active_calls": calls,
    "leaderboard": [{
        "name": "SELL_SIDE_CONSENSUS", "entity_type": "aggregate",
        "n_symbols": len(rows), "n_observations": len(rows),
        "avg_buy_side_pct": round(sum(s["buy_side_pct"] for s in rows) / len(rows), 1),
        "pct_strong_buy": round(100 * cnt["STRONG_BUY"] / len(rows), 1),
        "pct_hold": round(100 * cnt["HOLD"] / len(rows), 1),
        "pct_sell": round(100 * (cnt["SELL"] + cnt["STRONG_SELL"]) / len(rows), 1),
        "improved": sum(1 for s in rows if s.get("direction") == "IMPROVING"),
        "deteriorated": sum(1 for s in rows if s.get("direction") == "DETERIORATING"),
        "last_period": max(s["period"] for s in rows),
        "source": "finnhub:/stock/recommendation", "rule": rows[0].get("rule"),
    }],
    "note": "No firm/person attribution exists in the free feed; firm is null and the leaderboard is an aggregate.",
}
OUT.write_text(json.dumps(out, indent=2) + "\n")
print(f"bridge active_calls={len(calls)} total_analysts={total_analysts} total_predictions={len(rows)} -> {OUT}")
