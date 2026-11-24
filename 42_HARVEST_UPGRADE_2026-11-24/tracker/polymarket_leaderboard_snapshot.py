#!/usr/bin/env python3
"""Append one timestamped Polymarket leaderboard snapshot.

Why: trader persistence cannot be tested from a single leaderboard. This records
the same endpoint over time, with no later backfill, so the forward rank-IC test
in EDGE_SEARCH_PLAN.md has point-in-time inputs.

Usage:
  python3 polymarket_leaderboard_snapshot.py --out data/polymarket_leaderboard_snapshots.jsonl
"""
import argparse, datetime, json, pathlib, urllib.request

BASE = "https://data-api.polymarket.com/v2/leaderboard?limit={limit}&window={window}"
WINDOWS = ("1d", "1w", "1m", "3m", "all")
UA = {"User-Agent": "Mozilla/5.0 (compatible; kilo-research/1.0)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/polymarket_leaderboard_snapshots.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    a = ap.parse_args()
    now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    rec = {"retrieved_at": now, "source": BASE, "windows": {}}
    for w in WINDOWS:
        try:
            data = get(BASE.format(limit=a.limit, window=w)).get("data", [])
            rec["windows"][w] = [
                {k: x.get(k) for k in ("rank", "user_id", "user_name", "pnl", "volume")}
                for x in data
            ]
        except Exception as e:
            rec["windows"][w] = {"error": f"{type(e).__name__}: {e}"}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    counts = {w: (len(v) if isinstance(v, list) else "ERR") for w, v in rec["windows"].items()}
    print(f"appended {now} {counts} -> {out}")


if __name__ == "__main__":
    main()
