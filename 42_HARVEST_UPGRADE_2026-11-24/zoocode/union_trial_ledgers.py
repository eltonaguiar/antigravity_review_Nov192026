#!/usr/bin/env python3
"""Union the three divergent trial ledgers into one, without destroying trials.

Why this exists: trial_log.py takes the db path from argv and dsr.py defaults to
a bare relative "trial_ledger.db", so cron runs from different directories each
created their OWN append-only ledger. The 19 trial_ids across the three files are
DISJOINT -- union 19 = sum 19 -- so deleting two copies (the tempting fix) would
destroy trials. This script merges them instead.

Output: trials_union.jsonl -- one JSON object per trial, append-only, with the
source file kept on every row so provenance survives. SQLite is deliberately not
rewritten: it is unmergeable binary and is what pushed the seats apart.

Usage:
  python3 union_trial_ledgers.py            # write trials_union.jsonl (dry report)
  python3 union_trial_ledgers.py --check    # verify the union equals the disjoint sum
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from hashlib import sha256
from pathlib import Path

ROOT = Path("/home/eaguiar2015/antigravity_review_Nov192026")
SOURCES = [
    ROOT / "CONTEST/trial_ledger.db",
    ROOT / "CONTEST/tools/trial_ledger.db",
    ROOT / "CONTEST/tools/reports/trial_ledger.db",
]
OUT = Path(__file__).resolve().parent / "trials_union.jsonl"
COLS = ["trial_id", "run_id", "family", "variant", "sharpe_is", "sharpe_oos",
        "kept", "ts_logged"]


def read(path: Path) -> list[dict]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        have = [r[1] for r in con.execute("pragma table_info(trials)")]
        cols = [c for c in COLS if c in have]
        rows = con.execute(f"select {', '.join(cols)} from trials").fetchall()
        return [dict(zip(cols, r)) for r in rows]
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)

    merged: list[dict] = []
    seen: dict[str, str] = {}
    per_source = {}
    for src in SOURCES:
        if not src.is_file():
            print(f"MISSING {src}")
            continue
        rows = read(src)
        per_source[str(src.relative_to(ROOT))] = len(rows)
        for r in rows:
            tid = r["trial_id"]
            if tid in seen:
                # same trial_id in two files: keep the first, report it
                print(f"DUPLICATE trial_id {tid} in {src} (already from {seen[tid]})")
                continue
            seen[tid] = str(src.relative_to(ROOT))
            r["source_file"] = str(src.relative_to(ROOT))
            merged.append(r)

    merged.sort(key=lambda r: (r.get("ts_logged") or "", r["trial_id"]))
    text = "\n".join(json.dumps(r, sort_keys=True) for r in merged) + "\n"
    digest = sha256(text.encode()).hexdigest()

    total_in = sum(per_source.values())
    print("rows per source:", per_source)
    print(f"rows read: {total_in}   rows merged: {len(merged)}   "
          f"{'DISJOINT (nothing lost)' if total_in == len(merged) else 'OVERLAP FOUND'}")
    print(f"sha256 of the union: {digest}")
    if len(merged):
        sh = [r["sharpe_oos"] for r in merged if r.get("sharpe_oos") is not None]
        print(f"sharpe_oos: n={len(sh)} min={min(sh)} max={max(sh)}")

    if a.check:
        ok = total_in == len(merged)
        print("CHECK:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
