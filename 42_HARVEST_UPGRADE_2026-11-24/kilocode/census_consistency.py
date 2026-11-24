#!/usr/bin/env python3
"""Check the 1000-cell census: unique keys, artifact completeness, rollup equality."""
import argparse, json, sys
from collections import Counter
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw")
ap.add_argument("--out", default="")
ap.add_argument("--rollup", default="", help="override rollup JSON path")
a = ap.parse_args()
root = Path(a.repo)
todos = json.loads((root / "1000_TODOS.json").read_text())
cells = todos.get("cells", [])
keys = [f"{c.get('symbol')}_{c.get('strategy')}_{c.get('horizon')}" for c in cells]
status = Counter(c.get("status") for c in cells)
files = {f.stem for f in (root / "results" / "cells").glob("*.json")}
missing = [k for k in keys if k not in files]
extra = sorted(files - set(keys))
roll_path = Path(a.rollup) if a.rollup else (root / "results" / "CENSUS_ROLLUP.json")
roll = json.loads(roll_path.read_text()) if roll_path.exists() else None
problems = []
if len(cells) != 1000: problems.append(f"cell count {len(cells)} != 1000")
if len(set(keys)) != len(keys): problems.append(f"duplicate keys: {len(keys)-len(set(keys))}")
bad_status = {s for s in status if s not in ("killed", "blocked_no_data")}
if bad_status: problems.append(f"unexpected statuses: {sorted(bad_status)}")
if missing: problems.append(f"missing artifacts: {len(missing)} (blocked={sum(1 for c in cells if f'{c.get(chr(115)+chr(121)+chr(109)+chr(98)+chr(111)+chr(108))}_{c.get(chr(115)+chr(116)+chr(114)+chr(97)+chr(116)+chr(101)+chr(103)+chr(121))}_{c.get(chr(104)+chr(111)+chr(114)+chr(105)+chr(122)+chr(111)+chr(110))}' in missing and c.get('status')=='blocked_no_data')})")
if extra: problems.append(f"extra artifacts: {len(extra)}")
if roll:
    cats = roll.get("categories", {})
    killed = cats.get("killed", cats.get("measured_kill"))
    if killed != status.get("killed"):
        problems.append(f"rollup killed {killed} != killed {status.get('killed')}")
    if cats.get("blocked") != status.get("blocked_no_data"):
        problems.append(f"rollup blocked {cats.get('blocked')} != blocked_no_data {status.get('blocked_no_data')}")
    if not ("cell_keys" in roll or "cells" in roll):
        problems.append("rollup has no cell list (unrecomputable)")
res = {"cells": len(cells), "unique_keys": len(set(keys)), "status": dict(status),
       "artifacts": len(files), "missing": len(missing), "missing_sample": missing[:10],
       "extra": len(extra), "rollup": roll.get("categories") if roll else None,
       "problems": problems, "ok": not problems}
print(json.dumps(res, indent=2))
if a.out: Path(a.out).write_text(json.dumps(res, indent=2) + "\n")
sys.exit(0 if not problems else 1)
