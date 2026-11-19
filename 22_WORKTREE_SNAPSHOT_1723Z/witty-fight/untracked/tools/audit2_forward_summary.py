"""Aggregate reports/forward_observations.jsonl into the audit2 page sidecar.

Output: audit_dashboard/data/audit2_forward.json
  {generated_at, n_rows, by_hypothesis: {hid: {n, benchmark_leg, intrabar, pods}}}

Run by the audit3 ledger workflow after the forward ingest so the page never
reads a checked-in, stale copy. `--src`/`--out` exist so the aggregation can be
tested against fixtures without touching the real ledger.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "reports" / "forward_observations.jsonl"
OUT = REPO / "audit_dashboard" / "data" / "audit2_forward.json"


def summarize(src: Path, generated_at: str | None = None) -> dict:
    """Aggregate the JSONL forward ledger into the page's sidecar shape.

    Missing file is not an error: the page distinguishes "no rows yet" from
    "cannot load" and a registered pod with zero rows must stay visible.
    """
    by: dict[str, dict] = {}
    n = 0
    if src.exists():
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if not isinstance(r, dict):
                continue
            n += 1
            hid = str(r.get("hypothesis_id") or "?")
            b = by.setdefault(hid, {"n": 0, "benchmark_leg": 0,
                                    "intrabar": 0, "pods": set()})
            b["n"] += 1
            if r.get("benchmark_leg_ret") is not None:
                b["benchmark_leg"] += 1
            if r.get("intrabar_first_touch") is True:
                b["intrabar"] += 1
            if r.get("pod"):
                b["pods"].add(str(r["pod"]))
    return {
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "n_rows": n,
        "by_hypothesis": {k: {**v, "pods": sorted(v["pods"])} for k, v in by.items()},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=str(SRC), help="forward_observations.jsonl")
    ap.add_argument("--out", default=str(OUT), help="sidecar to write")
    args = ap.parse_args(argv)

    payload = summarize(Path(args.src))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}: rows={payload['n_rows']} "
          f"hypotheses={len(payload['by_hypothesis'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
