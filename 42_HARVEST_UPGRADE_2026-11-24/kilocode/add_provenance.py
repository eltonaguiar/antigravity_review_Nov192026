#!/usr/bin/env python3
"""Add tracker-required provenance to every published pick/consensus row."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data" / "harvest_signals.json"
SIM = ROOT / "docs" / "data" / "analyst_sim_demo.json"
RULE_ID = "two_condition_v1_" + hashlib.sha256(
    json.dumps(R.RULE, sort_keys=True).encode()).hexdigest()[:8]
COST_BPS = 6.7122

d = json.loads(DATA.read_text())
for s in d["signals"]:
    if not s.get("has_consensus"):
        continue
    s["source"] = s.get("source") or "finnhub:/stock/recommendation"
    s["published_at"] = (s.get("period") or "") + "T00:00:00Z"
    s["rule"] = RULE_ID
    s["cost_bps"] = COST_BPS
    s["benchmark"] = "SPY"
DATA.write_text(json.dumps(d, indent=2) + "\n")

if SIM.exists():
    sim = json.loads(SIM.read_text())
    sim["provenance"] = {"source": "synthetic", "published_at": sim.get("generated_utc", ""),
                         "rule": RULE_ID, "cost_bps": COST_BPS, "benchmark": "SPY"}
    SIM.write_text(json.dumps(sim, indent=2) + "\n")
print(f"provenance added: rule={RULE_ID} rows={sum(1 for s in d['signals'] if s.get('has_consensus'))}")
