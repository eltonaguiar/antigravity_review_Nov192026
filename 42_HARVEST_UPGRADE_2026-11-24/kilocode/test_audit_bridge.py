import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
B = json.loads((ROOT/"docs"/"data"/"audit_analyst_bridge.json").read_text())

def test_bridge_nonempty_and_provenanced():
    assert B["total_active"] == len(B["active_calls"]) == 71
    assert B["total_predictions"] == 71
    assert B["total_analysts"] > 0
    need = ("source", "published_at", "rule", "cost_bps", "benchmark")
    for c in B["active_calls"]:
        assert c["firm"] is None, c["symbol"]
        for k in need: assert c.get(k) not in (None, ""), (c["symbol"], k)
        assert c["entity_type"] == "sell_side_consensus"

def test_leaderboard_is_aggregate_not_fabricated():
    assert len(B["leaderboard"]) == 1
    e = B["leaderboard"][0]
    assert e["entity_type"] == "aggregate" and e["name"] == "SELL_SIDE_CONSENSUS"
    assert e["n_symbols"] == 71
