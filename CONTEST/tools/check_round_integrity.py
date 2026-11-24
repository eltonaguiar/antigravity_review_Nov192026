#!/usr/bin/env python3
"""Preflight gate: refuse to score a round that has unrecorded submissions.

Runs the canonical verifier and exits:
  0  all submissions recorded with matching hashes
  1  any NOT RECORDED or MISMATCH (details on stdout + --json)

Usage: python3 CONTEST/tools/check_round_integrity.py [round_dir] [--json]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY = HERE / "verify_ledger.py"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    d = args[0] if args else "CONTEST/ROUND_01_2026-11-23"
    r = subprocess.run([sys.executable, str(VERIFY), d],
                       capture_output=True, text=True)
    out = r.stdout
    missing = []
    bad = []
    for line in out.splitlines():
        if line.startswith("NOT RECORDED:"):
            missing = [x.strip() for x in line.split(":", 1)[1].split(",") if x.strip()]
        elif line.startswith("MISMATCH"):
            bad = [x.strip() for x in line.split(":", 1)[1].split(",") if x.strip()]
    res = {"round": d, "ok": r.returncode == 0,
           "not_recorded": missing, "mismatched": bad}
    if as_json:
        print(json.dumps(res, indent=2))
    else:
        print(f"round={d} ok={res['ok']} not_recorded={len(missing)} mismatched={len(bad)}")
        for s in missing:
            print("  NOT RECORDED:", s)
        for s in bad:
            print("  MISMATCH:", s)
        if not res["ok"]:
            print("REFUSE TO SCORE until these are recorded (late-recorded) or removed.")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
