#!/usr/bin/env python3
"""Audit Kilo's frozen grade->ordinal map (`tracker/grade_ordinals_draft.csv`).

Read-only. Never edits the source CSV. Answers five questions:

  1. how many distinct raw_grade values
  2. how many rows leave proposed_ordinal blank or non-numeric
  3. raw grades whose ordinal contradicts the STATED convention
  4. raw grades that carry DIFFERENT ordinals under different firms
  5. firms whose own label->ordinal mapping is not monotone

Design note: check 3 uses the STATED convention only (the five buckets given to me).
Synonym inference beyond those five (e.g. "Reduce" -> Sell) is reported separately as
EXTENDED and labelled as my inference, so nobody mistakes my extrapolation for the spec.

Run:  python3 grade_ordinal_audit.py [path-to-csv]
"""
import collections
import csv
import sys

STATED = {
    1: {"strong sell", "strongsell"},
    2: {"sell", "underperform"},
    3: {"hold", "neutral", "equal-weight", "equal weight", "equalweight"},
    4: {"buy", "outperform", "overweight"},
    5: {"strong buy", "strongbuy"},
}

# Extra synonyms, MY inference, not the stated spec. Used only for the secondary view.
EXTENDED = {
    1: set(),
    2: {"underweight", "reduce", "negative", "cautious", "sector underperform",
        "market underperform", "underperformer"},
    3: {"market perform", "sector perform", "peer perform", "perform", "in-line",
        "average", "fair value", "sector weight", "market weight", "mixed",
        "hold neutral", "inline"},
    4: {"market outperform", "sector outperform", "outperformer", "accumulate",
        "positive", "above average", "long-term buy"},
    5: {"conviction buy", "action list buy", "top pick"},
}


def norm(s):
    return " ".join(str(s).strip().lower().split())


def bucket_of(label, table):
    for b, labels in table.items():
        if label in labels:
            return b
    return None


def to_int(v):
    v = str(v).strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        return None


def main(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    out = {}
    exact = collections.Counter(r["raw_grade"] for r in rows)
    norms = collections.Counter(norm(r["raw_grade"]) for r in rows)
    out["rows"] = len(rows)
    out["distinct_exact"] = len(exact)
    out["distinct_norm"] = len(norms)
    out["firms"] = len({r["firm_norm"] for r in rows})

    # ---- 2. blank / non-numeric ordinals -------------------------------------
    bad = [r for r in rows if to_int(r["proposed_ordinal"]) is None]
    out["blank_or_nonnumeric"] = len(bad)
    out["bad_examples"] = sorted({r["proposed_ordinal"] for r in bad})

    # ---- ordinal range guard -------------------------------------------------
    ints = [to_int(r["proposed_ordinal"]) for r in rows]
    out["out_of_range"] = sum(1 for i in ints if i is not None and not 1 <= i <= 5)

    # ---- 3. contradictions vs STATED and vs EXTENDED ------------------------
    def contradictions(table):
        hits = []
        for r in rows:
            o = to_int(r["proposed_ordinal"])
            if o is None:
                continue
            b = bucket_of(norm(r["raw_grade"]), table)
            if b is not None and o != b:
                hits.append((r["firm_norm"], r["raw_grade"], o, b))
        return hits

    c_stated = contradictions(STATED)
    merged = {b: set(STATED[b]) | set(EXTENDED[b]) for b in STATED}
    c_ext = contradictions(merged)
    out["contra_stated"] = len(c_stated)
    out["contra_extended"] = len(c_ext)
    out["contra_stated_table"] = c_stated
    out["contra_extended_table"] = c_ext

    # ---- 4. same grade, different ordinal across firms ----------------------
    def cross(keyset):
        by = collections.defaultdict(lambda: collections.defaultdict(set))
        for r in rows:
            o = to_int(r["proposed_ordinal"])
            if o is None:
                continue
            by[keyset(r["raw_grade"])][o].add(r["firm_norm"])
        return {g: v for g, v in by.items() if len(v) > 1}

    s4 = cross(lambda g: g)
    n4 = cross(norm)
    out["conflict_exact"] = s4
    out["conflict_norm"] = n4

    # ---- 5. per-firm monotonicity -------------------------------------------
    # A firm is non-monotone if, among ITS OWN labels that the convention can
    # bucket, a "more bullish" label (higher stated bucket) gets a LOWER ordinal.
    nonmono = []
    for firm, frs in collections.defaultdict(list, {
            f: [r for r in rows if r["firm_norm"] == f] for f in {r["firm_norm"] for r in rows}}).items():
        pairs = []
        for r in frs:
            o = to_int(r["proposed_ordinal"])
            b = bucket_of(norm(r["raw_grade"]), merged)
            if o is not None and b is not None:
                pairs.append((b, o, r["raw_grade"]))
        for i in range(len(pairs)):
            for j in range(len(pairs)):
                bi, oi, gi = pairs[i]
                bj, oj, gj = pairs[j]
                if bi < bj and oi > oj:
                    nonmono.append((firm, gi, oi, gj, oj))
    # de-duplicate mirrored pairs
    seen, dedup = set(), []
    for f, g1, o1, g2, o2 in nonmono:
        k = tuple(sorted([(g1, o1), (g2, o2)])) + (f,)
        if k not in seen:
            seen.add(k)
            dedup.append((f, g1, o1, g2, o2))
    out["nonmono"] = dedup

    # ---- context: labels outside the stated convention ----------------------
    out["outside_stated"] = sorted(
        {r["raw_grade"] for r in rows if bucket_of(norm(r["raw_grade"]), STATED) is None})
    out["outside_extended"] = sorted(
        {r["raw_grade"] for r in rows if bucket_of(norm(r["raw_grade"]), merged) is None})
    out["ordinal_counts"] = collections.Counter(
        str(to_int(r["proposed_ordinal"])) for r in rows)
    return out


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else (
        "42_HARVEST_UPGRADE_2026-11-24/tracker/grade_ordinals_draft.csv")
    r = main(p)
    print("rows                              :", r["rows"])
    print("distinct raw_grade (exact)        :", r["distinct_exact"])
    print("distinct raw_grade (normalised)   :", r["distinct_norm"])
    print("distinct firms                    :", r["firms"])
    print("blank/non-numeric ordinal rows    :", r["blank_or_nonnumeric"], r["bad_examples"])
    print("ordinals outside 1..5             :", r["out_of_range"])
    print("ordinal distribution              :", dict(r["ordinal_counts"]))
    print("contradictions vs STATED          :", r["contra_stated"])
    print("contradictions vs EXTENDED (mine) :", r["contra_extended"])
    print("grades with >1 ordinal (exact)    :", len(r["conflict_exact"]))
    print("grades with >1 ordinal (norm)     :", len(r["conflict_norm"]))
    print("non-monotone firms/pairs          :", len(r["nonmono"]))
    print("grades outside STATED convention  :", len(r["outside_stated"]), r["outside_stated"])
    print("grades outside EXTENDED too       :", len(r["outside_extended"]), r["outside_extended"])
