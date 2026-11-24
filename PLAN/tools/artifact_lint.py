#!/usr/bin/env python3
"""artifact_lint - catch the defect class that produced every wrong number in
this programme that was not a typo.

WHY THIS EXISTS
    Twelve defects were found across the fund report, the cell sweep, and the
    PROVEIT scenarios. Not one was an arithmetic error. Every single one was a
    *labelling* error - the wrong quantity on one side of a comparison, or a
    field whose name invited the wrong reading:

      gross CAGR reported as net        (cagr_pct vs net_cagr_pct)
      distribution yield reported as YTM (bnd_yield_source: 'yield')
      Canadian bonds paired against US   (ZAG.TO vs BND)
      15-minute cells measured on daily  (requested 15m, served 1d, n identical)
      cash-over-ending-NAV read as cash-over-start
      trading days divided by 365        (9.18% becomes 13.58%)
      entry price of 374.84 replaced by  (437.19 -> 754.37 is a different pair)
        the window's first bar
      a two-size range used to describe three costs
      parameters accepted and silently ignored (rebal, merblend)
      absolute path recorded as provenance (artifact flagged STALE elsewhere)

    A reviewer cannot catch these by re-reading prose, because the prose is
    self-consistent. They surface only when the artifact is checked against its
    own numbers. That check is mechanical. This is it.

USAGE
    python3 PLAN/tools/artifact_lint.py ARTIFACT.json [ARTIFACT2.json ...]
    python3 PLAN/tools/artifact_lint.py ARTIFACT.json --claims README.md

EXIT
    0 = no HIGH findings, 1 = at least one HIGH finding.
"""

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

HIGH, MED, LOW = "HIGH", "MED", "LOW"
findings = []
CURRENT_FILE = ""


def add(sev, code, where, msg):
    findings.append((sev, code, f"{CURRENT_FILE}{where}", msg))


# ---------------------------------------------------------------- R1 duration
def check_duration(obj, path="$"):
    """A field called *_days whose denominator is unstated is a 4pp-sized trap."""
    if isinstance(obj, dict):
        window = obj.get("window")
        has_days = [k for k in obj if isinstance(k, str) and k.endswith("_days")]
        has_cal = any("calendar" in k for k in obj)
        has_trd = any("trading" in k for k in obj)
        if has_days and isinstance(window, (list, tuple)) and len(window) == 2:
            try:
                a = dt.date.fromisoformat(str(window[0]))
                b = dt.date.fromisoformat(str(window[1]))
                cal = (b - a).days
            except Exception:
                cal = None
            for k in has_days:
                v = obj[k]
                if not isinstance(v, (int, float)) or cal is None:
                    continue
                as_cal = v / 365.25
                as_trd = v / 252.0
                window_yrs = cal / 365.25
                if abs(as_trd - window_yrs) < 0.2 and abs(as_cal - window_yrs) > 0.5:
                    sev = LOW if (has_cal or has_trd) else HIGH
                    add(sev, "R1-DURATION", f"{path}.{k}",
                        f"{k}={v} matches the window only as TRADING days "
                        f"({as_trd:.2f}y vs {as_cal:.2f}y as calendar, window is "
                        f"{window_yrs:.2f}y). Field name implies calendar. "
                        f"Dividing by 365 instead of 252 inflates a CAGR by "
                        f"~4pp here. Rename to n_trading_days or emit "
                        f"n_calendar_days.")
        for k, v in obj.items():
            check_duration(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_duration(v, f"{path}[{i}]")


# ---------------------------------------------------------------- R2 CAGR
def _cagr(start, final, years):
    if not (start > 0 and final > 0 and years > 0):
        return None
    return ((final / start) ** (1.0 / years) - 1.0) * 100.0


def check_cagr(obj, path="$", window_years=None):
    """Reconcile a stored cagr_pct against start/final, under both conventions."""
    if isinstance(obj, dict):
        if {"start", "final"} <= set(obj) and any(
            isinstance(k, str) and k.endswith(("cagr_pct", "cagr")) for k in obj
        ):
            key = next(k for k in obj if isinstance(k, str) and k.endswith(("cagr_pct", "cagr")))
            stored = obj[key]
            if isinstance(stored, (int, float)) and window_years:
                got = _cagr(obj["start"], obj["final"], window_years)
                if got is not None:
                    d = abs(got - stored)
                    if d > 0.25:
                        add(HIGH, "R2-CAGR", f"{path}.{key}",
                            f"stored {stored} but start={obj['start']} "
                            f"final={obj['final']} over {window_years:.2f}y gives "
                            f"{got:.2f} (delta {d:.2f}pp). Either the duration or "
                            f"the return is mislabelled.")
        for k, v in obj.items():
            check_cagr(v, f"{path}.{k}", window_years)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_cagr(v, f"{path}[{i}]", window_years)


# ---------------------------------------------------------------- R3 scale
STEM_SCALE_TOL = 1.0  # a factor-of-100 (or inverse) is the hazard, not a 2x


def check_pct_scale(obj, path="$"):
    """X and X_pct in the same document, differing by ~100x, is a live 100x trap.

    An earlier version flagged any *_pct value <=1 as suspicious, which fired 12
    times on a clean artifact (cagr_pct: -0.92 is a legitimate -0.92%). A rule
    that cries wolf is worse than no rule, because it teaches reviewers to skip
    the output. This version only fires on a same-stem pair whose scales
    actually disagree.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.endswith("_pct") and isinstance(v, (int, float)) and v != 0:
                stem = k[:-4]
                for alt in (stem, f"{stem}_pct"):
                    if alt == k or alt not in obj or not isinstance(obj[alt], (int, float)):
                        continue
                    other = obj[alt]
                    if other == 0:
                        continue
                    ratio = abs(v / other)
                    if ratio > 50 or ratio < 0.02:
                        add(HIGH, "R3-SCALE", path,
                            f"{k}={v} and {alt}={other} differ by ~{ratio:.0f}x. "
                            f"One is a fraction, the other a percentage. Any prose "
                            f"quoting 'the' value has a 50/50 chance of being 100x wrong.")
        for k, v in obj.items():
            check_pct_scale(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_pct_scale(v, f"{path}[{i}]")


# ---------------------------------------------------------------- R7 estimand
# Field-name qualifiers that change WHAT is being measured, not just its size.
ESTIMAND_PAIRS = [
    ("gross", "net"),
    ("ytm", "yield"),
    ("yield", "distribution"),
    ("local", "usd"),
    ("nominal", "real"),
    ("price", "total_return"),
    ("arithmetic", "geometric"),
]


def check_estimand(obj, path="$"):
    """Two observably different quantities present under near-identical names.

    This is the rule that would have caught the two costliest defects in this
    programme: 'cagr_pct' (gross) quoted as 'net_cagr_pct', and a distribution
    yield quoted as a yield-to-maturity. Both artifacts held BOTH numbers. The
    bug was never missing data; it was choosing the wrong one.

    SEVERITY CALIBRATION: gross/net is the one pair where coexistence is normal -
    they differ by exactly the cost wedge, so an object holding both is correct
    design, not a hazard. Firing MED on all 60 affected cells would teach reviewers
    to ignore the rule. That pair is therefore LOW (informational: pick the right
    one), while genuinely incommensurable pairs stay MED.
    """
    if isinstance(obj, dict):
        keys = [k for k in obj if isinstance(k, str)]
        for a, b in ESTIMAND_PAIRS:
            ka = [k for k in keys if a in k.lower()]
            kb = [k for k in keys if b in k.lower()]
            for x in ka:
                for y in kb:
                    if x == y:
                        continue
                    if isinstance(obj[x], (int, float)) and isinstance(obj[y], (int, float)):
                        if obj[x] == obj[y]:
                            continue
                        vx, vy = obj[x], obj[y]
                        # arithmetic decomposition: same sign, and 'net' smaller in
                        # magnitude than 'gross' - that IS the cost model working.
                        cost_wedge = (
                            (a, b) == ("gross", "net")
                            and vx * vy > 0
                            and abs(vy) < abs(vx)
                        )
                        sev = LOW if cost_wedge else MED
                        note = (" (cost wedge - expected; quote the one you mean)"
                                if cost_wedge else " and disagree")
                        add(sev, "R7-ESTIMAND", path,
                            f"'{x}'={vx} and '{y}'={vy} measure different "
                            f"quantities{note}. State which one any quoted figure "
                            f"is, or the two will be conflated.")
        for k, v in obj.items():
            check_estimand(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_estimand(v, f"{path}[{i}]")


# ---------------------------------------------------------------- R4 identical
def check_identical_siblings(obj, path="$"):
    """Exactly equal returns across independently-sized scenarios is either a
    real structural result or a leak. Force the author to say which."""
    if isinstance(obj, dict):
        ratios = {}
        for k, v in obj.items():
            if isinstance(v, dict) and {"start", "final"} <= set(v):
                try:
                    ratios[k] = v["final"] / v["start"]
                except Exception:
                    pass
        if len(ratios) >= 3:
            sig = {}
            for k, r in ratios.items():
                sig.setdefault(round(r, 9), []).append(k)
            for r, ks in sig.items():
                if len(ks) >= 3:
                    add(LOW, "R4-IDENTICAL", path,
                        f"{len(ks)} scenarios share final/start = {r:.9f} "
                        f"({', '.join(ks)}). Not an error, but state why: whole-share "
                        f"granularity making the portfolio exactly proportional is a "
                        f"finding; a shared code path is a bug.")
        for k, v in obj.items():
            check_identical_siblings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_identical_siblings(v, f"{path}[{i}]")


# ---------------------------------------------------------------- R5 provenance
ABS_PATH = re.compile(r"^(?:/|[A-Za-z]:[\\/])")
PROV_KEYS = ("src", "source", "path", "file", "input", "script", "cmd", "origin")


def check_provenance(obj, path="$"):
    """An absolute path is provenance only on the machine that wrote it."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and any(p in k.lower() for p in PROV_KEYS) and ABS_PATH.match(v):
                add(MED, "R5-PROVENANCE", f"{path}.{k}",
                    f"absolute path {v!r}. On any other checkout this artifact "
                    f"looks stale or foreign. Record repo-relative paths.")
            else:
                check_provenance(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_provenance(v, f"{path}[{i}]")


# ---------------------------------------------------------------- R8 barsource
# The horizon the cell claims in its NAME, versus the resolution it was served.
# Two cells in the 149-cell ledger declared 15m and recorded binance:1d; one of
# them returned KILL. A strategy was demoted on a measurement of a different
# horizon. Nothing about the JSON's internal consistency reveals this - only the
# pairing of name against provenance does.
HZ_NAME = re.compile(r"_(15m|1h|4h|1d|1w)$")
HZ_INTRADAY = re.compile(r"(15m|1h|4h|min|minute|hour)")


def check_barsource(obj, stem, path="$"):
    if isinstance(obj, dict):
        src = obj.get("bar_source")
        if isinstance(src, str):
            m = HZ_NAME.search(stem or "")
            if m:
                hz = m.group(1)
                low = src.lower()
                served_intraday = bool(HZ_INTRADAY.search(low))
                if hz in ("15m", "1h", "4h") and not served_intraday:
                    add(HIGH, "R8-BARSOURCE", f"{path}.bar_source",
                        f"cell '{stem}' declares horizon {hz} but was served "
                        f"'{src}'. The measurement is of a different resolution "
                        f"than the one claimed, so any verdict names the wrong "
                        f"thing. A KILL here demotes a strategy using evidence it "
                        f"was never tested on.")
                elif hz in ("1d", "1w") and served_intraday and "resampled" not in low:
                    add(MED, "R8-BARSOURCE", f"{path}.bar_source",
                        f"cell '{stem}' declares {hz} but was served intraday "
                        f"'{src}' with no 'resampled' marker.")
        for k, v in obj.items():
            check_barsource(v, stem, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_barsource(v, stem, f"{path}[{i}]")


# ---------------------------------------------------------------- R9 cache age
# A cache file is a frozen window. Six cells were measured on a 90-day cache that
# ended 261 days before the ledger date, and four of them were KILLs - while every
# daily cell covered 2.7 years. Shorter, older windows bias toward false kills.
CACHE_RE = re.compile(r"cache:([^\s(]+)")


def check_cache_staleness(obj, cache_dir, today, path="$"):
    if cache_dir is None:
        return
    import datetime as _dt
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "bar_source" and isinstance(v, str):
                m = CACHE_RE.search(v)
                if m:
                    f = cache_dir / m.group(1)
                    if not f.exists():
                        add(MED, "R9-CACHE", f"{path}.{k}",
                            f"cites cache file {m.group(1)!r} which is not present; "
                            f"the measurement cannot be re-derived.")
                    else:
                        dates = []
                        for line in f.read_text(errors="ignore").splitlines():
                            mm = re.match(r"(\d{4}-\d{2}-\d{2})", line)
                            if mm:
                                dates.append(mm.group(1))
                        if dates:
                            span = (today - _dt.date.fromisoformat(dates[-1])).days
                            if span > 30:
                                add(HIGH, "R9-CACHE", f"{path}.{k}",
                                    f"cache {m.group(1)} spans "
                                    f"{dates[0]} -> {dates[-1]} and ends {span} "
                                    f"days ({span/30.44:.1f} months) before the "
                                    f"ledger date. Verdicts from it describe a "
                                    f"different regime and a much shorter window "
                                    f"than the rest of the ledger.")
            else:
                check_cache_staleness(v, cache_dir, today, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_cache_staleness(v, cache_dir, today, f"{path}[{i}]")


# ---------------------------------------------------------------- R6 claims
NUM = re.compile(r"(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?(?![\w])")


def _numbers_in(text):
    out = set()
    # Prose in this repo uses U+2212 MINUS and en/em dashes. Without folding them
    # to ASCII '-', "-1.11%" is read as +1.11 and reported as unsourced.
    text = (text.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-"))
    for m in NUM.findall(text):
        try:
            out.add(round(float(m.replace(",", "")), 2))
        except Exception:
            pass
    return out


def check_claims(doc, objs, doc_name):
    """Every number asserted in prose should exist somewhere in the artifacts."""
    blob = json.dumps(objs if isinstance(objs, list) else [objs])
    art_nums = _numbers_in(blob)
    # numbers appearing in window dates are legitimately absent as values
    claimed = _numbers_in(doc)
    missing = sorted(n for n in claimed if n not in art_nums and abs(n) >= 1)
    # ignore obvious prose constants
    ignore = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 12.0, 100.0, 252.0, 365.0, 2021.0, 2026.0}
    missing = [n for n in missing if n not in ignore]
    if missing:
        add(MED, "R6-UNSOURCED", doc_name,
            f"{len(missing)} number(s) in prose not present anywhere in the "
            f"artifact: {missing[:12]}{'...' if len(missing) > 12 else ''}. "
            f"Either the number is wrong or the artifact is incomplete.")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--claims", help="markdown/HTML file whose numbers are asserted from the artifacts")
    ap.add_argument("--cache-dir", help="directory holding cache: files, enables R9 staleness check")
    ap.add_argument("--baseline", help="JSON list of acknowledged findings; matching findings do not fail the run")
    ap.add_argument("--write-baseline", help="write the current findings to this path as an acknowledged baseline")
    args = ap.parse_args()

    loaded = []
    for path in args.artifacts:
        globals()["CURRENT_FILE"] = path + " "
        try:
            obj = json.load(open(path))
        except Exception as e:
            add(HIGH, "R0-PARSE", path, f"cannot parse JSON: {e}")
            continue
        loaded.append(obj)
        yrs = None
        w = obj.get("window")
        if isinstance(w, (list, tuple)) and len(w) == 2:
            try:
                a = dt.date.fromisoformat(str(w[0])); b = dt.date.fromisoformat(str(w[1]))
                yrs = (b - a).days / 365.25
            except Exception:
                pass

        check_duration(obj)
        check_cagr(obj, window_years=yrs)
        check_pct_scale(obj)
        check_estimand(obj)
        check_identical_siblings(obj)
        check_provenance(obj)
        check_barsource(obj, Path(path).stem)
        if args.cache_dir:
            check_cache_staleness(obj, Path(args.cache_dir), dt.date.today())

    if args.claims:
        try:
            doc = open(args.claims, encoding="utf-8", errors="ignore").read()
            check_claims(doc, loaded, args.claims)
        except Exception as e:
            add(MED, "R0-CLAIMS", args.claims, f"could not run claim check: {e}")

    if not findings:
        print("artifact_lint: no findings.")
        return 0

    # A acknowledged finding is one the author has documented elsewhere. CI must
    # fail on NEW findings only, otherwise a repo-scoped baseline of known
    # defects blocks every future change and the gate gets disabled.
    acked = set()
    if args.baseline:
        try:
            acked = {(f["code"], f["where"]) for f in json.load(open(args.baseline))}
        except Exception as e:
            print(f"artifact_lint: baseline unreadable ({e}); treating as empty")

    def is_acked(f):
        return (f[1], f[2]) in acked or (f[1], f[2].split(" $")[0].split()[0]) in acked

    new_findings = [f for f in findings if not is_acked(f)]
    suppressed = len(findings) - len(new_findings)

    if args.write_baseline:
        json.dump([{"code": f[1], "where": f[2]} for f in findings],
                  open(args.write_baseline, "w"), indent=2)
        print(f"artifact_lint: wrote baseline of {len(findings)} finding(s) to {args.write_baseline}")

    if not new_findings:
        print(f"artifact_lint: no NEW findings ({suppressed} acknowledged).")
        return 0

    order = {HIGH: 0, MED: 1, LOW: 2}
    new_findings.sort(key=lambda f: (order[f[0]], f[1]))
    counts = {s: sum(1 for f in new_findings if f[0] == s) for s in (HIGH, MED, LOW)}
    for sev, code, where, msg in new_findings:
        print(f"[{sev}] {code}  {where}\n        {msg}\n")
    print(f"artifact_lint: {counts[HIGH]} high, {counts[MED]} med, {counts[LOW]} low "
          f"({suppressed} acknowledged)")
    return 1 if counts[HIGH] else 0


if __name__ == "__main__":
    sys.exit(main())
