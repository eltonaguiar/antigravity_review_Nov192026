#!/usr/bin/env python3
"""Up-only breadth: the definition the deliberation settled on, finally measured.

Two columns, both UP-only:
  NO FILTER  -- every row with action == 'up'
  6-MONTH    -- an 'up' counts only if that broker-stock pair has had no prior
                'up' or 'down' in the preceding 182 days (the clean window the
                panel asked for; init/reit/main do not reset the window, because
                the rule is specifically "no prior up or down")

Reads tracker/analyst_actions.csv. Writes up_only_breadth.md and .json next to it.
No floor is changed: if nobody clears 750, the files say so.
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = Path("/home/eaguiar2015/antigravity_review/42_HARVEST_UPGRADE_2026-11-24/tracker/analyst_actions.csv")
MD = HERE / "up_only_breadth.md"
JS = HERE / "up_only_breadth.json"
WINDOW_DAYS = 182
FLOORS = (300, 500, 750)


def ts(epoch: str) -> datetime:
    return datetime.fromtimestamp(int(epoch), timezone.utc)


def main() -> int:
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    mix = Counter((r["action"] or "").strip().lower() for r in rows)

    ups = [r for r in rows if (r["action"] or "").strip().lower() == "up"]

    # column 1: no filter
    col1 = Counter(r["firm_norm"] for r in ups)
    pairs_up = {(r["firm_norm"], r["symbol"]) for r in ups}

    # column 2: 6-month clean window per broker-stock pair
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in ups:
        by_pair[(r["firm_norm"], r["symbol"])].append(r)
    # every up/down, per pair, to know what came before
    marks: dict[tuple[str, str], list[datetime]] = defaultdict(list)
    for r in rows:
        if (r["action"] or "").strip().lower() in ("up", "down"):
            marks[(r["firm_norm"], r["symbol"])].append(ts(r["date"]))

    col2 = Counter()
    pairs_surviving = set()
    for pair, rs in by_pair.items():
        prior = sorted(marks[pair])
        for r in sorted(rs, key=lambda x: int(x["date"])):
            d = ts(r["date"])
            earlier = [p for p in prior if p < d]
            if not earlier or (d - max(earlier)).days >= WINDOW_DAYS:
                col2[pair[0]] += 1
                pairs_surviving.add(pair)

    def summary(c: Counter) -> dict:
        return {
            "firms_above": {str(f): sum(1 for v in c.values() if v >= f) for f in FLOORS},
            "biggest": (c.most_common(1)[0] if c else (None, 0)),
            "n_firms": len(c),
            "total_events": sum(c.values()),
        }

    s1, s2 = summary(col1), summary(col2)
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": str(CSV),
        "rows_total": len(rows),
        "action_mix": dict(mix),
        "up_share_of_rows": round(len(ups) / len(rows), 4),
        "no_filter": {**s1,
                      "pairs_with_at_least_one_up": len(pairs_up)},
        "six_month": {**s2,
                      "pairs_with_a_surviving_up": len(pairs_surviving)},
        "window_days": WINDOW_DAYS,
        "floors_unchanged": True,
    }
    JS.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    def row(name: str, s: dict) -> str:
        return (f"| {name} | {s['total_events']:,} | {s['n_firms']} | "
                f"{s['firms_above']['300']} | {s['firms_above']['500']} | "
                f"{s['firms_above']['750']} | {s['biggest'][0]} ({s['biggest'][1]:,}) |")

    lines = [
        "# Up-only breadth -- the definition the deliberation settled on",
        "",
        "zoo-savant, 2026-11-24. Measured from `analyst_actions.csv`",
        f"({len(rows):,} rows, {len({r['symbol'] for r in rows})} tickers).",
        "",
        "**Why this needed running:** the deliberation unanimously rejected `init` and `reit`,",
        "so the defensible event is `up` only -- but every breadth table so far measured",
        "`up/down/init` (A), `+reit` (B) or `+main` (C), never up-only.",
        "",
        "**Context for reading it:** `up` is only "
        f"{mix['up']:,} of {len(rows):,} rows ({100*mix['up']/len(rows):.0f}%), while `main` is "
        f"{mix['main']:,}. Up-only is therefore far below the 28/18/11 measured for A.",
        "",
        "## Table",
        "",
        "| column | up events | firms | 300 | 500 | 750 | biggest firm |",
        "|---|---|---|---|---|---|---|",
        row("up only, no filter", s1),
        row(f"up only, {WINDOW_DAYS}-day clean window", s2),
        "",
        "**Pairs:** "
        f"{len(pairs_up):,} broker-stock pairs have at least one `up`; "
        f"{len(pairs_surviving):,} of them still have one after the {WINDOW_DAYS}-day window.",
        "",
        "No floor was changed to make the numbers look better.",
        "",
        "## Consequence for the prereg",
        "",
    ]
    if s2["firms_above"]["750"] == 0:
        lines.append(
            "The defensible definition is **not measurable at the current ticker count**: "
            f"nobody clears 750 clean events under the 6-month rule (the biggest firm has "
            f"{s2['biggest'][1]}), so it needs more tickers -- or the floor should be restated "
            "as an MDE, since even 750 events still resolves only about 19%/yr.")
    else:
        lines.append(
            f"The defensible definition **is** measurable: {s2['firms_above']['750']} firm(s) "
            "clear 750 clean events under the 6-month rule.")
    lines.append("")
    MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
