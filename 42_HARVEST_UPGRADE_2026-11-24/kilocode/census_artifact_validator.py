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
if len(shas) > 1: problems.append(f"distinct_git_sha={len(shas)}")
print(json.dumps({"files": sum(shas.values()) + len(malformed),
                  "malformed_sample": malformed[:8],
                  "blocked_with_bars_sample": bad_bars[:8],
                  "distinct_git_sha": len(shas), "sha_counts": dict(shas.most_common(8)),
                  "problems": problems, "ok": not problems}, indent=2))
sys.exit(0 if not problems else 1)
