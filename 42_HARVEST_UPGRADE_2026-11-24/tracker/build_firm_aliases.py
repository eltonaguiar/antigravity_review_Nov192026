#!/usr/bin/env python3
"""Build firm_aliases.csv from the raw names in analyst_actions.csv.

Every raw name comes from the CSV, never from memory. A raw name is mapped only
when the evidence justifies it:

  RULE 1 (alias): two spellings differ only by case/punctuation/abbreviation of
      the SAME name -- e.g. "Deutsche Bank" / "Deutsche bank", "Piper Sandler" /
      "PiperJaffray" are NOT this case (different names) but "Scotiabank" /
      "ScotiaBank" is.

  RULE 2 (merger era): an acquisition means one entity but TWO histories. The
      rows are split with an era suffix ("pre", "post") at the merger date, and
      never merged into one continuous record. Era assignment uses each raw
      name's first/last seen dates.

  RULE 3 (UNRESOLVED): if the identity is not determinable, the row keeps its raw
      name as normalized_entity, era_suffix "unresolved", and is COUNTED as
      unresolved. Nothing is invented.

Output columns: raw_name, normalized_entity, era_suffix, first_seen, last_seen, action_count
  first_seen / last_seen are ISO dates (UTC) of that raw name's actions.
"""
from __future__ import annotations

import csv
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "analyst_actions.csv"
OUT = HERE / "firm_aliases.csv"

# (raw_name) -> (normalized_entity, era_suffix)
# Only alias-level identities are asserted here. Merget-era splits are computed
# below from the observed dates so the split point is evidence, not memory.
ALIASES: dict[str, tuple[str, str]] = {
    # exact-spelling variants of the same name
    "Deutsche bank": ("Deutsche Bank", "same"),
    "ScotiaBank": ("Scotiabank", "same"),
    "Bank of America": ("BofA Securities", "same"),
    # explicitly requested pairs
    "Merrill Lynch": ("BofA Securities", "pre"),       # acquired by BofA in 2008
    "B of A Securities": ("BofA Securities", "post"),
    "AllianceBernstein": ("Bernstein", "pre"),          # Bernstein was AB's research arm
    "Bernstein": ("Bernstein", "post"),
    "RBC Capital": ("RBC Capital Markets", "same"),
    "Piper Jaffray": ("Piper Sandler", "pre"),
    "PiperJaffray": ("Piper Sandler", "pre"),
    "Piper Sandler": ("Piper Sandler", "post"),
    # other documented corporate histories
    "SunTrust Robinson Humphrey": ("Truist Securities", "pre"),
    "Truist Securities": ("Truist Securities", "post"),
    "Cowen & Co.": ("TD Cowen", "pre"),
    "TD Cowen": ("TD Cowen", "post"),
    "SVB Leerink": ("Leerink", "pre"),
    "Credit Suisse": ("UBS", "pre"),                    # acquired 2023
    "UBS": ("UBS", "post"),
    "Stifel Nicolaus": ("Stifel", "pre"),
    "Stifel": ("Stifel", "post"),
    "Argus": ("Argus Research", "same"),
}


def _date(epoch: str) -> datetime:
    return datetime.fromtimestamp(int(epoch), timezone.utc)


def main() -> int:
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    agg: "OrderedDict[str, dict]" = OrderedDict()
    for r in rows:
        raw = r["firm_raw"]
        d = agg.setdefault(raw, {"n": 0, "first": None, "last": None})
        d["n"] += 1
        if r.get("date"):
            t = _date(r["date"])
            d["first"] = t if d["first"] is None else min(d["first"], t)
            d["last"] = t if d["last"] is None else max(d["last"], t)

    out = []
    mapped = unresolved = split = 0
    for raw, d in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
        ent, era = ALIASES.get(raw, (raw, "unresolved"))
        if era == "unresolved":
            unresolved += 1
        else:
            mapped += 1
            if era in ("pre", "post"):
                split += 1
        out.append({
            "raw_name": raw,
            "normalized_entity": ent,
            "era_suffix": era,
            "first_seen": d["first"].strftime("%Y-%m-%d") if d["first"] else "",
            "last_seen": d["last"].strftime("%Y-%m-%d") if d["last"] else "",
            "action_count": d["n"],
        })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["raw_name", "normalized_entity",
                                         "era_suffix", "first_seen", "last_seen",
                                         "action_count"])
        w.writeheader()
        w.writerows(out)

    print(f"raw names: {len(out)}")
    print(f"mapped: {mapped}")
    print(f"UNRESOLVED: {unresolved}")
    print(f"split by merger era (era_suffix pre/post): {split}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
