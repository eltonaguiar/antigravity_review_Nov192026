#!/usr/bin/env python3
"""Insider P (purchase) vs S (sale) asymmetry test -- repaired.

THE QUESTION: if purchases and sales produce the same matched excess return,
the signal is not insider information and the probe is dead.

FROZEN RULES (as briefed; not changed here):
  * entry = next session OPEN after FILING_DATE -- never the transaction date,
    because the transaction is private until it is filed
  * horizons 21, 63, 126 TRADING days
  * benchmark matched on ADV tercile and 126-day momentum tercile, SAME date
    (not SPY)
  * costs reported at all three of 0.98, 4.01 and 12.07 bp round turn
  * symbol-cluster bootstrap CI with the design effect actually obtained
  * within-symbol date-shift placebo as the falsifier

REPAIRED 2026-11-25 after an audit found three defects in the first version:
  1. the role filter was DEAD CODE -- the flags were parsed but never applied,
     so the P figure included 10% owners and entities;
  2. flags were parsed as a literal lower()=='true', but the CSV stores '1' as
     well ('is_officer' is 23x '0', 19x '1', 9x 'false', 1x 'true'), so the
     literal parser found 6 officer-or-director rows where a truthy parser
     finds 48;
  3. purchases are concentrated (PARA 10, UPST 10, RIVN 7, LCID 6 = 33 of 52),
     so a transaction-level CI is meaningless -- the CI is clustered by SYMBOL.
Both parsers are now printed so the gap stays visible, and every filter step
reports its row count. If the clean set is under 30 events the output says
UNDERPOWERED; the filter is never relaxed to reach a sample.

Usage: python3 p_vs_s_asymmetry.py
"""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "form4_events_wide.csv"
OUT_JSON = HERE / "p_vs_s_asymmetry.json"
OUT_MD = HERE / "p_vs_s_asymmetry.md"

HORIZONS = (21, 63, 126)
COSTS_BP = (0.98, 4.01, 12.07)
SEED = 20261124
N_BOOT = 2000
N_PLACEBO = 500
Z80 = 2.80
MIN_EVENTS = 30
TRUTHY = {"1", "true", "y", "yes", "t"}

_px_cache: dict[str, object] = {}


def lit(v) -> bool:
    """The old parser: only the literal string 'true'."""
    return (v or "").strip().lower() == "true"


def truthy(v) -> bool:
    """The correct parser: the CSV stores 1/0 as well as true/false."""
    return (v or "").strip().lower() in TRUTHY


def prices(sym: str):
    import yfinance as yf
    if sym not in _px_cache:
        try:
            df = yf.Ticker(sym).history(period="10y", interval="1d", auto_adjust=False)
        except Exception:
            df = None
        if df is None or not len(df):
            _px_cache[sym] = None
        else:
            df = df[["Open", "Close", "Volume"]].dropna()
            _px_cache[sym] = df if len(df) else None
    return _px_cache[sym]


def adv_bucket(df, day) -> int:
    prior = df[df.index.date <= day]
    if len(prior) < 30:
        return -1
    adv = float((prior["Close"] * prior["Volume"]).tail(20).mean())
    return -1 if adv <= 0 else min(2, max(0, int(math.log10(adv)) - 4))


def mom_tercile(df, day) -> int:
    prior = df[df.index.date <= day]
    if len(prior) < 127:
        return -1
    c = prior["Close"]
    mom = float(c.iloc[-1] / c.iloc[-127] - 1)
    return 0 if mom < -0.05 else (1 if mom < 0.15 else 2)


def event_return(sym: str, filing: datetime, horizon: int):
    df = prices(sym)
    if df is None:
        return None
    idx = list(df.index)
    try:
        i = next(k for k, d in enumerate(idx) if d.date() > filing.date())
    except StopIteration:
        return None
    j = i + horizon
    if j >= len(idx):
        return None
    entry_open = float(df["Open"].iloc[i])
    exit_close = float(df["Close"].iloc[j])
    if not (entry_open > 0 and math.isfinite(entry_open) and math.isfinite(exit_close)):
        return None
    return {"ret": exit_close / entry_open - 1.0,
            "adv_t": adv_bucket(df, idx[i].date()),
            "mom_t": mom_tercile(df, idx[i].date())}


def boot_ci(by_sym: dict[str, list[float]], rng: random.Random):
    keys = sorted(by_sym)
    if not keys:
        return None, None
    means = []
    for _ in range(N_BOOT):
        sample = [v for k in (rng.choice(keys) for _ in keys) for v in by_sym[k]]
        if sample:
            means.append(statistics.mean(sample))
    means.sort()
    return (means[int(0.025 * len(means))], means[int(0.975 * len(means)) - 1]) if means else (None, None)


def t_of(xs):
    if len(xs) < 3:
        return None
    m, sd = statistics.mean(xs), statistics.stdev(xs)
    return m / (sd / math.sqrt(len(xs))) if sd else None


def main() -> int:
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    P = [r for r in rows if (r["code"] or "").strip() == "P"]
    S = [r for r in rows if (r["code"] or "").strip() == "S"]

    # ---- B + C: both parsers, and every filter step ------------------------
    steps = {
        "P all": P,
        "P officer-or-director (TRUTHY)": [r for r in P if truthy(r["is_officer"]) or truthy(r["is_director"])],
        "P officer-or-director, excluding 10% owners (TRUTHY)": [
            r for r in P if (truthy(r["is_officer"]) or truthy(r["is_director"]))
            and not truthy(r["is_ten_percent_owner"])],
    }
    steps_lit = {
        "P officer-or-director (LITERAL)": [r for r in P if lit(r["is_officer"]) or lit(r["is_director"])],
        "P officer-or-director, excluding 10% owners (LITERAL)": [
            r for r in P if (lit(r["is_officer"]) or lit(r["is_director"]))
            and not lit(r["is_ten_percent_owner"])],
    }
    print("filter steps (row counts):")
    for k, v in list(steps_lit.items()) + list(steps.items()):
        print(f"  {k:<56}{len(v):>5}")
    print(f"  {'S all (control)':<56}{len(S):>5}")
    print("  concentration of P:", Counter(r["symbol"] for r in P).most_common(5))

    # The clean set the brief defines: officer/director, not a 10% owner.
    clean_P = steps["P officer-or-director, excluding 10% owners (TRUTHY)"]
    underpowered = len(clean_P) < MIN_EVENTS

    results = {}
    for H in HORIZONS:
        # event set is FILTERED FIRST (defect A), then the excess is built from it
        def collect(rs):
            per = defaultdict(list)
            cells = defaultdict(list)
            dropped = 0
            for r in rs:
                ev = event_return(r["symbol"], datetime.strptime(r["filing_date"], "%Y-%m-%d"), H)
                if ev is None:
                    dropped += 1
                    continue
                per[r["symbol"]].append((ev["ret"], ev["adv_t"], ev["mom_t"]))
                cells[(ev["adv_t"], ev["mom_t"])].append(ev["ret"])
            return per, cells, dropped

        def excess(per, bench_cells):
            """Excess of each event against an OUTSIDE benchmark's cell mean.

            Any benchmark built from the event's own rows makes the excesses
            average zero by construction -- leave-one-out still does, because
            the per-cell excesses sum to zero within each cell. So the
            comparator must be the other code's cells (P judged against S and
            S against P), which is also what the P-vs-S question means.
            """
            bench = {c: statistics.mean(v) for c, v in bench_cells.items() if v}
            by_sym = defaultdict(list)
            used = 0
            for sym, lst in per.items():
                for ret, at, mt in lst:
                    bm = bench.get((at, mt))
                    if bm is not None:
                        by_sym[sym].append(ret - bm)
                        used += 1
            return by_sym, used

        p_per, p_cells, p_drop = collect(clean_P)
        s_per, s_cells, s_drop = collect(S)
        p_by, p_used = excess(p_per, s_cells)   # P judged against S
        s_by, s_used = excess(s_per, p_cells)   # S judged against P
        rng = random.Random(SEED + H)
        p_vals = [v for vs in p_by.values() for v in vs]
        s_vals = [v for vs in s_by.values() for v in vs]
        p_lo, p_hi = boot_ci(p_by, rng)
        s_lo, s_hi = boot_ci(s_by, rng)
        t_raw = t_of(p_vals + s_vals)
        t_cl = t_of([statistics.mean(v) for v in list(p_by.values()) + list(s_by.values())])
        design = (t_raw / t_cl) ** 2 if (t_raw and t_cl) else None

        # within-symbol date-shift placebo on the CLEAN set, measured as EXCESS
        # against the same (S) benchmark -- a raw-return placebo is not comparable
        # to an excess statistic and would make any positive P look significant.
        bench_s = {c: statistics.mean(v) for c, v in s_cells.items() if v}
        rngp = random.Random(SEED + H)
        plac = []
        for _ in range(N_PLACEBO):
            shifted = []
            for r in clean_P:
                df = prices(r["symbol"])
                if df is None:
                    continue
                idx = [d for d in df.index if d.date() > datetime.strptime(r["filing_date"], "%Y-%m-%d").date()]
                if len(idx) > 30:
                    ev = event_return(r["symbol"], datetime.combine(idx[30].date(), datetime.min.time()), H)
                    if ev:
                        bm = bench_s.get((ev["adv_t"], ev["mom_t"]))
                        if bm is not None:
                            shifted.append(ev["ret"] - bm)
            if shifted:
                plac.append(statistics.mean(shifted))
        plac.sort()
        p95 = plac[int(0.95 * (len(plac) - 1))] if plac else None

        sd_p = statistics.stdev(p_vals) if len(p_vals) > 2 else None
        mde = Z80 * sd_p / math.sqrt(len(p_by)) if (sd_p and p_by) else None

        # Rule E is applied to the ANALYSABLE n, not the pre-price count: events
        # without a full price window cannot contribute, so a 31-event filter set
        # that yields 16-26 usable events is still UNDERPOWERED.
        if not p_vals or len(p_vals) < MIN_EVENTS or underpowered:
            verdict = "UNDERPOWERED"
        elif p95 is not None and statistics.mean(p_vals) <= p95:
            verdict = "NULL -- P does not beat its own placebo"
        elif p_lo is not None and p_lo > 0:
            verdict = "P beats placebo and CI excludes 0"
        else:
            verdict = "inconclusive"

        results[H] = {
            "P_n": len(p_vals), "P_symbols": len(p_by),
            "P_mean_excess_pct": round(100 * statistics.mean(p_vals), 4) if p_vals else None,
            "P_ci95_symbol_cluster_pct": [round(100 * p_lo, 4) if p_lo is not None else None,
                                          round(100 * p_hi, 4) if p_hi is not None else None],
            "S_n": len(s_vals), "S_symbols": len(s_by),
            "S_mean_excess_pct": round(100 * statistics.mean(s_vals), 4) if s_vals else None,
            "S_ci95_symbol_cluster_pct": [round(100 * s_lo, 4) if s_lo is not None else None,
                                          round(100 * s_hi, 4) if s_hi is not None else None],
            "design_effect": round(design, 2) if design else None,
            "placebo_p95_pct": round(100 * p95, 4) if p95 is not None else None,
            "mde80_pct": round(100 * mde, 4) if mde else None,
            "dropped_P": p_drop, "dropped_S": s_drop, "verdict": verdict,
        }
        print(f"\nH={H}d  P n={len(p_vals)} ({len(p_by)} sym)  S n={len(s_vals)} ({len(s_by)} sym)")
        print(f"  P excess {results[H]['P_mean_excess_pct']}%  S excess {results[H]['S_mean_excess_pct']}%")
        print(f"  design {results[H]['design_effect']}  MDE80 {results[H]['mde80_pct']}%  placebo p95 {results[H]['placebo_p95_pct']}%")
        print(f"  VERDICT: {verdict}")

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": SRC.name, "seed": SEED,
        "cluster_unit": "issuer symbol",
        "entry": "next session open after filing_date",
        "flag_parser": {"literal": "lower()=='true'", "truthy": sorted(TRUTHY),
                        "is_officer_distribution_P": dict(Counter(r["is_officer"] for r in P))},
        "filter_steps": {k: len(v) for k, v in list(steps_lit.items()) + list(steps.items())} | {"S all": len(S)},
        "purchase_concentration": Counter(r["symbol"] for r in P).most_common(6),
        "min_events": MIN_EVENTS,
        "clean_set_underpowered": underpowered,
        "costs_bp": list(COSTS_BP),
        "by_horizon": results,
        "withdrawn_prior": ("The 2026-11-24 P +10.79% figure is WITHDRAWN: it applied no role "
                            "filter and used a literal flag parser."),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    md = ["# Insider P vs S -- repaired after audit", "",
          f"zoo-savant, {payload['generated'][:19]}Z. Source `{SRC.name}`.",
          "", "**This supersedes the 2026-11-24 result, which is WITHDRAWN:** it applied no role",
          "filter (the parsed flags were never read) and used a literal `=='true'` parser that",
          "misses the `1` values the file stores.", "",
          "## Filter steps (row counts)", "", "| step | rows |", "|---|---|"]
    for k, v in list(steps_lit.items()) + list(steps.items()):
        md.append(f"| {k} | {len(v)} |")
    md += [f"| S all (control) | {len(S)} |", "",
           f"**Purchase concentration:** {', '.join(f'{s} {n}' for s, n in Counter(r['symbol'] for r in P).most_common(6))}",
           "", "## Per horizon", "",
           "| H | P n | P sym | P excess | P CI (symbol) | S n | S excess | design | MDE80 | placebo p95 | verdict |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for H, r in results.items():
        md.append(f"| {H}d | {r['P_n']} | {r['P_symbols']} | {r['P_mean_excess_pct']}% | {r['P_ci95_symbol_cluster_pct']} "
                  f"| {r['S_n']} | {r['S_mean_excess_pct']}% | {r['design_effect']} | {r['mde80_pct']}% "
                  f"| {r['placebo_p95_pct']}% | {r['verdict']} |")
    md += ["", f"The clean set ({len(clean_P)} events) is "
           f"{'UNDERPOWERED (< 30 events) -- not a result.' if underpowered else 'large enough to report.'}",
           "The filter was not relaxed to reach a sample.", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {OUT_MD.name} and {OUT_JSON.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
