import json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_rules as R

DATA = json.loads((ROOT / "docs" / "data" / "harvest_signals.json").read_text())
SIG = DATA["signals"]; COVERED = [s for s in SIG if s.get("has_consensus")]

def test_labels_recompute_71():
    bad = [(s["symbol"], s["consensus"], R.label_for_counts(s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"]))
           for s in COVERED if R.label_for_counts(s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"]) != s["consensus"]]
    assert not bad, bad
    assert len(COVERED) == 71

def test_scores_and_counts():
    for s in COVERED:
        assert abs(R.score_of(s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"]) - s["consensus_score"]) < 0.002, s["symbol"]
        assert abs(100*R.buy_side_of(s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"]) - s["buy_side_pct"]) < 0.11, s["symbol"]
        assert s["analysts"] == s["n_now"] == R.counts_total(s["strong_buy"], s["buy"], s["hold"], s["sell"], s["strong_sell"])

def test_direction_rule_and_kpi():
    for s in COVERED:
        if s.get("n_prior") is None:
            assert s["direction"] == "STABLE"; continue
        prior = {k: s["prior_"+k] for k in ("strong_buy","buy","hold","sell","strong_sell")}
        now = {k: s[k] for k in ("strong_buy","buy","hold","sell","strong_sell")}
        delta = 100*(R.buy_side_of(**now)-R.buy_side_of(**prior)); moves = R.bucket_moves(prior, now)
        assert abs(delta - s["delta_pp"]) < 0.11, s["symbol"]
        assert moves == s["bucket_moves"], s["symbol"]
        assert R.direction_for(delta, s["n_now"], moves) == s["direction"], s["symbol"]
        assert s["churn_flag"] in ("CLEAN","CHURN_CONTAMINATED")
    cnt = Counter(s["direction"] for s in COVERED); kpi = DATA["crowd_consensus"]["direction_counts"]
    for k in ("IMPROVING","DETERIORATING","STABLE"):
        assert kpi.get(k,0) == cnt.get(k,0), (k, kpi, cnt)
    assert DATA["crowd_consensus"]["net_upgrades_minus_downgrades"] == cnt.get("IMPROVING",0)-cnt.get("DETERIORATING",0)

def test_reason_codes_never_blank():
    codes = set(R.REASON_CODES)
    for s in SIG: assert s.get("reason_code") in codes, s["symbol"]
    for e in DATA["errors"]: assert e.get("reason_code") in codes, e.get("symbol")
    for u in DATA["uncovered"]: assert u.get("reason_code") in codes, u.get("symbol")
    for c in DATA["coverage_by_asset_class"].values(): assert c.get("reason_code") in codes

def test_legend_matches_constants():
    html = (ROOT/"docs"/"harvest.html").read_text()
    for key in ("strong_buy","buy"):
        assert f"buy-side ≥ {R.RULE[key]['buy_side_min']:.0%}" in html
    for key in ("sell","strong_sell"):
        assert f"buy-side ≤ {R.RULE[key]['buy_side_max']:.0%}" in html
    assert ">−0.3 HOLD</code>" not in html
    md = (ROOT/"docs"/"HARVEST_METHODOLOGY.md").read_text()
    assert "buy_side ≥ 50%" in md and "CHURN_CONTAMINATED" in md

def test_taxonomy_shape():
    tax = json.loads((ROOT/"universe"/"taxonomy.json").read_text())
    leaves = tax["leaves"]
    assert 250 <= len(leaves) <= 400, len(leaves)
    assert len({x["id"] for x in leaves}) == len(leaves)
    for x in leaves:
        av = x["signal_availability"]
        assert av["sell_side"] in ("none","look_through","direct")
        assert av["crowd"] and av["official_rating"]
