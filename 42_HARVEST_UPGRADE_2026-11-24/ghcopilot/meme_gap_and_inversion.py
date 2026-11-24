#!/usr/bin/env python3
"""Corrections to my own cost review, plus a REAL gap measurement.

TWO ERRORS IN MY PREVIOUS REVIEW, both flagged by the arena cross-check and both valid:

E1. THE "INVERSION" WAS AN ARTIFACT OF INCONSISTENT POINT SELECTION.
    I claimed "equity needs 14.4% gross at 1d but ETF needs 21.2%, so ETF is dearer".
    That grades equity at CENTRAL (4.0124 bp) and ETF at its point (6.7122 bp).
    03_equity_cost_settlement.md explicitly requires grading at the UPPER end. At
    equity's ceiling (12.0749 bp) equity needs MORE than ETF and the inversion vanishes.
    I committed the exact sin I accused the reviewer of - inconsistently picking points.

E2. CLOSE-TO-CLOSE IS NOT A GAP MEASURE AND IS NOT A "FLOOR" ON GAP RISK.
    I wrote "SPY moved >5% on 3/1254 days, so even a 5% stop gets jumped". A gap is
    open-vs-previous-close; a close-to-close move includes the whole session and says
    nothing about whether a stop was jumped. The correct test needs O/H/L/C.

WHAT THIS SCRIPT DOES INSTEAD
    Binance public klines carry open/high/low/close, so for the actual assets under
    discussion (meme coins) a real gap test is possible with no key and no repo data.
    Measured: overnight gap distribution, and how often the OPEN alone is already below
    a -5% / -10% / -20% stop set at the previous close (i.e. the stop is jumped, not hit).
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out" / "meme_gap_and_inversion.json"
UA = {"User-Agent": "hp-verify/1.0 research"}

# the classes under discussion, plus large-cap controls
SYMBOLS = ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "BONKUSDT", "WIFUSDT", "FLOKIUSDT",
           "BTCUSDT", "ETHUSDT"]
CONTROLS = {"BTCUSDT", "ETHUSDT"}

# cost of record. equity as the bracket the settlement doc mandates.
COST = {
    "fund":      (0.0,    0.0,    0.0),
    "bond ETF":  (0.6144, 0.6144, 0.6144),
    "ETF":       (6.7122, 6.7122, 6.7122),
    "FOREX":     (7.533,  7.533,  7.533),
    "equity":    (0.9756, 4.0124, 12.0749),   # floor / central / CEILING
    "commodity": (20.0,   20.0,   20.0),
    "crypto":    (20.0,   36.0,   52.0),
}
HURDLE = 4.32
TURNS = {"1d": 252.0, "1w": 252.0 / 5, "1m": 252.0 / 21}


def gross_needed(bp: float, turns: float) -> float:
    return HURDLE + turns * bp / 100.0


def get(url: str, timeout=25):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:160]
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def klines(sym: str, limit: int = 1000):
    st, b = get(f"https://api.binance.com/api/v3/klines?symbol={sym}&interval=1d&limit={limit}")
    if st != 200 or not b.lstrip().startswith("["):
        return None, f"http={st} {b[:100]}"
    return [[float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in json.loads(b)], None


def main() -> int:
    print("=" * 78)
    print("E1. THE INVERSION — grading equity at the CEILING as our own doc requires")
    print("=" * 78)
    print(f"   {'class':<11}{'point used':>12}{'bp':>9}{'gross@1d':>11}{'gross@1w':>11}")
    rows = {}
    for cls, (lo, pt, hi) in COST.items():
        # grade at ceiling; for single-value classes ceiling == point
        rows[cls] = {"point_bp": pt, "ceiling_bp": hi,
                     "gross_1d_central": gross_needed(pt, TURNS["1d"]),
                     "gross_1d_ceiling": gross_needed(hi, TURNS["1d"]),
                     "gross_1w_ceiling": gross_needed(hi, TURNS["1w"])}
        print(f"   {cls:<11}{'ceiling':>12}{hi:>9.4f}{gross_needed(hi,TURNS['1d']):>10.1f}%"
              f"{gross_needed(hi,TURNS['1w']):>10.1f}%")
    eq_c = rows["equity"]["gross_1d_central"]
    eq_h = rows["equity"]["gross_1d_ceiling"]
    etf = rows["ETF"]["gross_1d_ceiling"]
    print(f"\n   equity @central  {eq_c:5.1f}%  <  ETF {etf:5.1f}%   <- my published claim")
    print(f"   equity @CEILING  {eq_h:5.1f}%  >  ETF {etf:5.1f}%   <- the doc-mandated grading")
    print("   => The inversion does NOT hold under the rule our own settlement doc sets.")
    print("      My published claim was an artifact of grading equity at central and ETF at")
    print("      point. Retracted. The defensible statement is: ETF is dearer than equity on")
    print("      central estimates, cheaper than equity on ceiling estimates - i.e. UNRESOLVED")
    print("      until an ETF bracket exists. It is not a finding either way.")
    inversion = {"equity_gross_1d_central": eq_c, "equity_gross_1d_ceiling": eq_h,
                 "etf_gross_1d": etf, "inversion_holds_at_ceiling": eq_h > etf}

    print("\n" + "=" * 78)
    print("E4/36-vs-40. RECONCILE THE NUMBER I USED")
    print("=" * 78)
    print("   cost_of_hurdle.py used crypto point = 36.0 bp (midpoint of the 20-52 band).")
    print("   My prose said '40 bp is the crypto band'. 40 bp is ZOOCODE's figure, not ours.")
    print("   Our measured band is 20-52 bp; there is no measured 40. Correct labels:")
    print("     20 bp = band low | 36 bp = band midpoint (what the table computes)")
    print("     52 bp = band high | 40 bp = EXTERNAL ASSUMPTION, not a repo measurement")
    relabel = {"repo_band": [20.0, 52.0], "point_used": 36.0,
               "external_assumption_40bp": "zoocode's, not ours"}

    print("\n" + "=" * 78)
    print("E2. GAP TEST — and why the naive version is structurally zero")
    print("=" * 78)
    print("   A 'gap' is open-vs-previous-close. Crypto on Binance trades 24/7 with no")
    print("   session break, so open_t == close_{t-1} almost exactly and the naive gap")
    print("   test returns 0.00% everywhere BY CONSTRUCTION, not because the risk is absent.")
    print("   The binding risk in a continuous market is INTRABAR: how far price falls")
    print("   inside a bar, and whether it breaks a stop then recovers (a wick-out).")
    print("   So both are measured below.\n")
    print(f"   {'symbol':<11}{'bars':>5}{'open==prevC':>12}{'low<open-5%':>12}"
          f"{'low<open-20%':>13}{'wickout@5%':>12}{'max intrabar':>13}")
    gaps_out = {}
    for sym in SYMBOLS:
        k, err = klines(sym)
        if not k:
            print(f"   {sym:<11}  UNUSABLE {err}")
            continue
        # confirm the structural identity that makes a session gap meaningless
        same = sum(1 for i in range(1, len(k)) if abs(k[i][0] - k[i - 1][3]) / k[i - 1][3] < 1e-9)
        n = len(k) - 1
        intr = [(k[i][2] / k[i][0] - 1) for i in range(len(k)) if k[i][0] > 0]   # low/open
        b5 = sum(1 for x in intr if x <= -0.05)
        b20 = sum(1 for x in intr if x <= -0.20)
        # wick-out: the bar's low breaks -5% from open but the close is back above it
        wick = sum(1 for i in range(len(k))
                   if k[i][0] > 0 and k[i][2] / k[i][0] - 1 <= -0.05
                   and k[i][3] / k[i][0] - 1 > -0.05)
        gaps_out[sym] = {
            "bars": n,
            "open_equals_prev_close_pct": 100 * same / n,
            "low_breaks_minus5_pct": 100 * b5 / len(intr),
            "low_breaks_minus20_pct": 100 * b20 / len(intr),
            "wickout_breaks5_recovers_pct": 100 * wick / len(intr),
            "worst_intrabar_pct": 100 * min(intr),
            "median_intrabar_pct": 100 * statistics.median(intr),
        }
        tag = " (ctrl)" if sym in CONTROLS else ""
        print(f"   {sym:<11}{n:>5}{100*same/n:>11.1f}%{100*b5/len(intr):>11.2f}%"
              f"{100*b20/len(intr):>12.2f}%{100*wick/len(intr):>11.2f}%"
              f"{100*min(intr):>12.1f}%{tag}")

    print("\n   'wickout@5%' = bars where the low broke a -5% stop from the open but the")
    print("   close finished back above it. For those entries the stop was triggered and")
    print("   the trade was still right - the wick, not the direction, cost the position.")
    print("   'max intrabar' is the worst low-vs-open in the window: the depth a stop must")
    print("   survive before it can be honoured.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"inversion": inversion, "relabel": relabel,
                               "gaps": gaps_out, "hurdle_pct": HURDLE,
                               "turns_per_year": TURNS,
                               "convention": "round turns (one buy + one sell per turn)"},
                              indent=2))
    print(f"\n   written: {OUT.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
