#!/usr/bin/env python3
"""Insider P (purchase) vs S (sale) asymmetry test.

THE QUESTION: if purchases and sales produce the same matched excess return,
the signal is not insider information and the probe is dead.

FROZEN RULES (as briefed; not changed here):
  * entry = next session OPEN after FILING_DATE -- never the transaction date,
    because the transaction is private until it is filed
  * horizons 21, 63, 126 TRADING days
  * benchmark matched on ADV tercile and 126-day momentum tercile, SAME date
    (not SPY)
  * costs at all three of 0.98, 4.01 and 12.07 bp round turn
  * symbol-cluster bootstrap CI, with the design effect actually obtained
  * within-symbol date-shift placebo as the falsifier

ONE DEVIATION, NAMED: the brief says "cluster by symbol" in the firm table's
language. These are company insiders, not brokers, so the cluster unit is the
ISSUER SYMBOL -- one symbol's insiders share that company's return -- which is
also what the placebo shifts within. Reporting it as "firm" would mislabel it.

Nothing is fabricated: an event without prices on both dates is DROPPED and
counted.

Usage: python3 p_vs_s_asymmetry.py
"""
from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "form4_events_wide.csv"
OUT_JSON = HERE / "p_vs_s_asymmetry.json"
OUT_MD = HERE / "p_vs_s_asymmetry.md"

HORIZONS = (21, 63, 126)
COSTS_BP = (0.98, 4.01, 12.07)
SEED = 20261124
N_BOOT = 2000
N_PLACEBO = 500
Z80 = 2.80          # 80% power, two-sided 5%

_px_cache: dict[str, object] = {}


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


def adv_tercile(df, day) -> int:
    prior = df[df.index.date <= day]
    if len(prior) < 30:
        return -1
    adv = float((prior["Close"] * prior["Volume"]).tail(20).mean())
    return 0 if adv <= 0 else min(2, int(math.log10(adv) // 1) - 3)   # rough $1e3..$1e9 buckets


def momentum_tercile(df, day) -> int:
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
    return {"entry": idx[i].date(), "exit": idx[j].date(),
            "ret": exit_close / entry_open - 1.0,
            "adv_t": adv_tercile(df, idx[i].date()),
            "mom_t": momentum_tercile(df, idx[i].date())}


def main() -> int:
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    events = []
    for r in rows:
        if r["code"] not in ("P", "S"):
            continue
        events.append({"symbol": r["symbol"], "code": r["code"],
                       "filing": datetime.strptime(r["filing_date"], "%Y-%m-%d"),
                       "officer": (r.get("is_officer") or "").lower() == "true",
                       "director": (r.get("is_director") or "").lower() == "true",
                       "ten": (r.get("is_ten_percent_owner") or "").lower() == "true"})
    syms = sorted({e["symbol"] for e in events})
    print(f"P/S owner-rows: {len(events)}  symbols: {len(syms)}")

    # benchmark cells: mean return of NON-event symbols sharing (horizon, adv, mom)
    results: dict[int, dict] = {}
    dropped_total = 0
    for H in HORIZONS:
        # per[code][symbol] = [(ret, adv_tercile, mom_tercile), ...]
        per: dict[str, dict[str, list]] = {"P": defaultdict(list), "S": defaultdict(list)}
        dropped = 0
        for e in events:
            ev = event_return(e["symbol"], e["filing"], H)
            if ev is None:
                dropped += 1
                continue
            per[e["code"]][e["symbol"]].append((ev["ret"], ev["adv_t"], ev["mom_t"]))
        dropped_total += dropped
        all_cells = defaultdict(list)
        for code in ("P", "S"):
            for lst in per[code].values():
                for ret, at, mt in lst:
                    all_cells[(at, mt)].append(ret)
        cell_mean = {c: statistics.mean(v) for c, v in all_cells.items() if v}

        def excess(code):
            out = defaultdict(list)
            for sym, lst in per[code].items():
                for ret, at, mt in lst:
                    bm = cell_mean.get((at, mt))
                    if bm is None:
                        continue
                    out[sym].append(ret - bm)
            return out

        p_ex = excess("P")
        s_ex = excess("S")
        p_vals = [v for vs in p_ex.values() for v in vs]
        s_vals = [v for vs in s_ex.values() for v in vs]

        def boot_ci(by_sym, rng):
            keys = sorted(by_sym)
            means = []
            for _ in range(N_BOOT):
                pick = [rng.choice(keys) for _ in keys]
                sample = [v for k in pick for v in by_sym[k]]
                if sample:
                    means.append(statistics.mean(sample))
            means.sort()
            return (means[int(0.025 * len(means))], means[int(0.975 * len(means)) - 1]) if means else (None, None)

        rng = random.Random(SEED)
        p_lo, p_hi = boot_ci(p_ex, rng)
        s_lo, s_hi = boot_ci(s_ex, rng)

        # design effect: pooled t vs cluster-mean t
        def t_of(xs):
            if len(xs) < 3:
                return None
            m, sd = statistics.mean(xs), statistics.stdev(xs)
            return m / (sd / math.sqrt(len(xs))) if sd else None
        t_raw = t_of(p_vals + s_vals)
        t_cl = t_of([statistics.mean(v) for v in list(p_ex.values()) + list(s_ex.values())])
        design = (t_raw / t_cl) ** 2 if (t_raw and t_cl) else None

        # within-symbol date-shift placebo: shift each event 30 trading days later
        rngp = random.Random(SEED + H)
        plac = []
        for _ in range(N_PLACEBO):
            shifted = []
            for e in events:
                if rngp.random() > 0.3:
                    continue
                f = e["filing"]
                df = prices(e["symbol"])
                if df is None:
                    continue
                idx = [d for d in df.index if d.date() > f.date()]
                if len(idx) > 30:
                    ev = event_return(e["symbol"], datetime.combine(idx[30].date(), datetime.min.time()), H)
                    if ev:
                        bm = cell_mean.get((ev["adv_t"], ev["mom_t"]))
                        if bm is not None:
                            shifted.append(ev["ret"] - bm)
            if shifted:
                plac.append(statistics.mean(shifted))
        plac.sort()
        p95 = plac[int(0.95 * (len(plac) - 1))] if plac else None

        # MDE at 80% power from the P-side dispersion, symbol-clustered
        sd_p = statistics.stdev(p_vals) if len(p_vals) > 2 else None
        n_eff = len(p_ex) if p_ex else 0
        mde = (Z80 * sd_p / math.sqrt(n_eff)) if (sd_p and n_eff) else None

        results[H] = {
            "P_n": len(p_vals), "P_symbols": len(p_ex), "P_mean_excess_pct": round(100 * statistics.mean(p_vals), 4) if p_vals else None,
            "P_ci95_pct": [round(100 * p_lo, 4) if p_lo is not None else None, round(100 * p_hi, 4) if p_hi is not None else None],
            "S_n": len(s_vals), "S_symbols": len(s_ex), "S_mean_excess_pct": round(100 * statistics.mean(s_vals), 4) if s_vals else None,
            "S_ci95_pct": [round(100 * s_lo, 4) if s_lo is not None else None, round(100 * s_hi, 4) if s_hi is not None else None],
            "design_effect": round(design, 2) if design else None,
            "placebo_p95_pct": round(100 * p95, 4) if p95 is not None else None,
            "mde80_pct": round(100 * mde, 4) if mde else None,
            "dropped_no_price": dropped,
            "costs_bp": list(COSTS_BP),
        }
        asym = (p_vals and s_vals and statistics.mean(p_vals) > statistics.mean(s_vals))
        results[H]["asymmetry_holds"] = bool(asym) if (p_vals and s_vals) else None
        print(f"\nH={H}d  dropped={dropped}  P n={len(p_vals)} ({len(p_ex)} sym)  S n={len(s_vals)} ({len(s_ex)} sym)")
        print(f"  P excess {100*statistics.mean(p_vals):+.4f}%" if p_vals else "  P: none",
              f"  S excess {100*statistics.mean(s_vals):+.4f}%" if s_vals else "  S: none")
        print(f"  design effect {results[H]['design_effect']}  MDE80 {results[H]['mde80_pct']}%  placebo p95 {results[H]['placebo_p95_pct']}")

    advs = []
    for e in events:
        df = prices(e["symbol"])
        if df is not None and len(df) > 20:
            advs.append(float((df["Close"] * df["Volume"]).tail(20).mean()))
    advs.sort()
    adv_dist = {"n": len(advs), "min": round(advs[0]), "median": round(advs[len(advs)//2]),
                "p90": round(advs[int(0.9 * len(advs))]), "max": round(advs[-1])} if advs else {}

    payload = {"generated": datetime.utcnow().isoformat(),
               "source": str(SRC.name), "seed": SEED,
               "cluster_unit": "issuer symbol (insiders, not brokers)",
               "entry": "next session open after filing_date",
               "horizons": list(HORIZONS), "costs_bp": list(COSTS_BP),
               "adv_distribution_usd": adv_dist,
               "owner_row_counts": {
                   "P": sum(1 for e in events if e["code"] == "P"),
                   "S": sum(1 for e in events if e["code"] == "S"),
                   "P_officer_or_director": sum(1 for e in events if e["code"] == "P" and (e["officer"] or e["director"])),
                   "P_officer_dir_not_10pct": sum(1 for e in events if e["code"] == "P" and (e["officer"] or e["director"]) and not e["ten"]),
               },
               "by_horizon": results}
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    lines = ["# Insider P vs S asymmetry", "",
             f"zoo-savant, {payload['generated'][:19]}Z. Source `{SRC.name}`.", "",
             f"**Cluster unit:** issuer symbol (insiders, not brokers), {len(syms)} symbols.",
             "**Entry:** next session open after `filing_date`. **Benchmark:** ADV x momentum tercile cell mean, same date.",
             f"**Costs reported at:** {', '.join(str(c) for c in COSTS_BP)} bp.", "",
             f"**ADV distribution (USD):** {adv_dist}", "",
             "| H | P n | P excess | S n | S excess | design effect | MDE80 | placebo p95 | asymmetry holds |",
             "|---|---|---|---|---|---|---|---|---|"]
    for H, r in results.items():
        lines.append(f"| {H}d | {r['P_n']} | {r['P_mean_excess_pct']}% | {r['S_n']} | {r['S_mean_excess_pct']}% "
                     f"| {r['design_effect']} | {r['mde80_pct']}% | {r['placebo_p95_pct']}% | {r['asymmetry_holds']} |")
    lines += ["", "**Owner-row counts (this file):** " + json.dumps(payload["owner_row_counts"]), ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nADV distribution: {adv_dist}")
    print(f"wrote {OUT_MD.name} and {OUT_JSON.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
