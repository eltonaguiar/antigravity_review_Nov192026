#!/usr/bin/env python3
"""Build a fully remediated census copy (stubs + schema repair + verdict normalisation)."""
import argparse, json, re, shutil, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw")
ap.add_argument("--out", default="/tmp/census_remediated")
a = ap.parse_args()
src, out = Path(a.repo), Path(a.out)
if out.exists(): shutil.rmtree(out)
shutil.copytree(src / "results", out / "results")
shutil.copy2(src / "1000_TODOS.json", out / "1000_TODOS.json")
todos = json.loads((out / "1000_TODOS.json").read_text())
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def bars_from(note):
    m = re.search(r"bars=(\d+)", note or "")
    return int(m.group(1)) if m else 0

repaired = normalized = stubs = 0
for c in todos["cells"]:
    key = c["key"].replace("/", "_")
    f = out / "results" / "cells" / f"{key}.json"
    verdict = "KILLED" if c["status"] == "killed" else "BLOCKED_NO_DATA"
    base = {"cell": c["key"], "symbol": c["symbol"], "strategy": c["strategy"],
            "horizon": c["horizon"], "verdict": verdict, "bars": bars_from(c.get("note")),
            "reason": c.get("note") or "", "git_sha": "remediated-2026-11-24", "generated_at": now}
    if not f.exists():
        f.write_text(json.dumps(base, indent=1) + "\n"); stubs += 1; continue
    try:
        d = json.loads(f.read_text())
    except Exception:
        f.write_text(json.dumps(base, indent=1) + "\n"); repaired += 1; continue
    req = ("cell", "symbol", "strategy", "horizon", "verdict", "bars", "git_sha", "generated_at")
    if any(k not in d for k in req) or d.get("verdict") is None:
        f.write_text(json.dumps(base, indent=1) + "\n"); repaired += 1; continue
    if d["verdict"] in ("INSUFFICIENT_TRADES", None):
        d["verdict"] = "KILLED"; f.write_text(json.dumps(d, indent=1) + "\n"); normalized += 1
    if d["verdict"] == "BLOCKED_NO_DATA" and (d.get("bars") or 0) > 0:
        d["verdict"] = "KILLED"
        d["reason"] = (d.get("reason") or "") + " | reclassified: bars>0; owner confirm"
        f.write_text(json.dumps(d, indent=1) + "\n"); normalized += 1
print(json.dumps({"stubs": stubs, "repaired": repaired, "normalized": normalized,
                  "out": str(out)}, indent=2))
