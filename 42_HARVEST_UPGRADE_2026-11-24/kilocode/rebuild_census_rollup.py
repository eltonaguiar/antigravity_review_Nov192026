#!/usr/bin/env python3
"""Rebuild the census rollup FROM 1000_TODOS + artifact presence, with a digest.

Does not overwrite main; writes a candidate to the review repo for approval.
"""
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw")
ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "census_rollup_candidate.json"))
a = ap.parse_args()
root = Path(a.repo)
todos = json.loads((root / "1000_TODOS.json").read_text())
cells = todos.get("cells", [])
keys = [f"{c.get('symbol')}_{c.get('strategy')}_{c.get('horizon')}" for c in cells]
files = {f.stem for f in (root / "results" / "cells").glob("*.json")}
status = Counter(c.get("status") for c in cells)
missing = [k for k in keys if k not in files]
digest = hashlib.sha256("\n".join(sorted(keys)).encode()).hexdigest()
out = {
    "schema": "census_rollup/2",
    "generated_at": todos.get("generated_at"),
    "source": "1000_TODOS.json + results/cells/*.json",
    "total": len(cells),
    "cell_keys_sha256": digest,
    "cell_keys": sorted(keys),
    "by_status": dict(status),
    "categories": {"killed": status.get("killed", 0),
                   "blocked": status.get("blocked_no_data", 0)},
    "artifacts": {"present": len(files), "missing": len(missing), "missing_keys": missing},
    "by_symbol": dict(Counter(c.get("symbol") for c in cells)),
    "by_horizon": dict(Counter(c.get("horizon") for c in cells)),
    "finding": "Derived from source; categories map directly to TODOS statuses.",
}
Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"total": out["total"], "by_status": out["by_status"],
                  "artifacts": out["artifacts"]["present"], "missing": out["artifacts"]["missing"],
                  "digest": digest, "out": a.out}, indent=2))
