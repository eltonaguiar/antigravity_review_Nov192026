#!/usr/bin/env python3
"""Forward-testing tracker -- append every run, never overwrite, compare over time.

Two modes:
  --record <results.json>   append a row summarising a proveit run
  --check                   print the history and whether any scenario has moved
                            from INCONCLUSIVE toward PROVEN (or away)

The log is JSON-lines: one row per run, each with a timestamp, so the forward
test is an accumulating record rather than a series of overwritten snapshots.
Stdlib only.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).parent / "forward_log.jsonl"
STATE = Path(__file__).parent / "state.json"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(results_path: str) -> int:
    d = json.loads(Path(results_path).read_text())
    row = {"ts": now(), "source": results_path,
           "cost_bp": d["meta"]["cost_bp"], "hurdle": d["meta"]["hurdle_apr"],
           "scenarios": {k: {"median_apr": v["median_apr"], "ci": v["ci_apr"],
                            "verdict": v["verdict"], "beat_hurdle": v["share_beating_hurdle"]}
                         for k, v in d["scenarios"].items()}}
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    print(f"appended {row['ts']} -> {LOG}")
    return 0


def check() -> int:
    if not LOG.exists():
        print("no history yet -- run --record first")
        return 0
    rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    prev = {}
    if STATE.exists():
        prev = json.loads(STATE.read_text())
    print(f"{len(rows)} recorded run(s)\n")
    print("%-22s %-16s %9s %22s %7s %s" % ("ts", "scenario", "medAPR", "ci", "beatH", "verdict"))
    for r in rows:
        for k, v in r["scenarios"].items():
            ci = v["ci"]
            print("%-22s %-16s %8.2f%% [%7.2f%%,%7.2f%%] %6.1f%% %s" % (
                r["ts"], k, v["median_apr"] * 100, ci[0] * 100, ci[1] * 100,
                v["beat_hurdle"] * 100, v["verdict"]))
    latest = rows[-1]["scenarios"]
    print("\nchange vs previous recorded state:")
    for k, v in latest.items():
        old = prev.get(k, {}).get("median_apr")
        if old is None:
            print(f"  {k:<16} new: {v['median_apr']*100:+.2f}%")
        else:
            delta = (v["median_apr"] - old) * 100
            flag = "  <-- MOVED" if abs(delta) > 0.5 else ""
            print(f"  {k:<16} {old*100:+.2f}% -> {v['median_apr']*100:+.2f}%  ({delta:+.2f} pp){flag}")
    STATE.write_text(json.dumps(latest, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--record", metavar="RESULTS_JSON")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    return record(a.record) if a.record else check()


if __name__ == "__main__":
    raise SystemExit(main())
