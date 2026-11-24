#!/usr/bin/env python3
"""Validate census cell artifacts: schema, verdict enum, BLOCKED bars==0, single sha."""
import argparse, json, sys
from collections import Counter
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw")
a = ap.parse_args()
d = Path(a.repo) / "results" / "cells"
REQ = {"cell": str, "symbol": str, "strategy": str, "horizon": str,
       "verdict": str, "bars": int, "git_sha": str, "generated_at": str}
VERDICTS = {"KILLED", "BLOCKED_NO_DATA", "INSUFFICIENT_TRADES", "CANDIDATE",
            "PROVEN", "PROVEN_T2", "WEAK"}
malformed, bad_bars, shas = [], [], Counter()
for f in sorted(d.glob("*.json")):
    try:
        x = json.load(open(f))
    except Exception as e:
        malformed.append((f.name, f"json: {e}")); continue
    miss = [k for k, t in REQ.items() if k not in x or not isinstance(x[k], t)]
    if miss:
        malformed.append((f.name, "missing/wrong: " + ",".join(miss))); continue
    if x["verdict"] not in VERDICTS:
        malformed.append((f.name, f"bad verdict {x['verdict']}")); continue
    if x["verdict"] == "BLOCKED_NO_DATA" and x["bars"] != 0:
        bad_bars.append((f.name, x["bars"]))
    shas[x["git_sha"]] += 1
problems = []
if malformed: problems.append(f"malformed={len(malformed)}")
if bad_bars: problems.append(f"blocked_with_bars={len(bad_bars)}")
man_path = d.parent / "census_manifest.json"
manifest = None
if man_path.exists():
    manifest = json.loads(man_path.read_text())
    declared = set(manifest.get("git_shas") or [])
    undeclared = set(shas) - declared
    if undeclared: problems.append(f"undeclared_shas={sorted(undeclared)[:3]}")
    keys = sorted(x["cell"] for x in (json.load(open(f)) for f in d.glob("*.json")) if isinstance(x, dict) and "cell" in x)
    import hashlib
    dig = hashlib.sha256("\n".join(keys).encode()).hexdigest()
    if manifest.get("n_cells") != len(keys): problems.append(f"manifest_n {manifest.get('n_cells')} != {len(keys)}")
    if manifest.get("cell_keys_sha256") != dig: problems.append("manifest_digest_mismatch")
elif len(shas) > 1:
    problems.append(f"distinct_git_sha={len(shas)} (no manifest)")
print(json.dumps({"files": sum(shas.values()) + len(malformed),
                  "malformed_sample": malformed[:8],
                  "blocked_with_bars_sample": bad_bars[:8],
                  "distinct_git_sha": len(shas), "sha_counts": dict(shas.most_common(8)),
                  "manifest": bool(manifest),
                  "problems": problems, "ok": not problems}, indent=2))
sys.exit(0 if not problems else 1)
