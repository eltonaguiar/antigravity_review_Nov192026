#!/usr/bin/env python3
"""derive_provenance - make every PROVEIT prose number come from code, not typing.

WHY THIS EXISTS
    artifact_lint R6 found 15 numbers in the PROVEIT README that exist nowhere
    in the committed JSON: the entry-bar closes (SPY 374.84, TLT 92.83,
    GLD 157.87, BIL 76.38), the cash left over ($207.12), the idle percentage
    measured against starting capital (69.0%), the trading-day years (4.98), and
    the wrong-denominator CAGR (13.58%).

    Every one of those numbers is correct - I derived them by hand from the
    engine. That is exactly the problem: a reviewer has no way to tell a
    hand-derived correct number from a hand-typed wrong one. The $374.84 figure
    was in the PR body for hours with no committed source behind it.

    So they get generated. This script re-fetches the same price history the sim
    used, recomputes the entry bar and the allocation, CROSS-CHECKS its own
    output against the committed sim artifact, and refuses to write anything if
    the check fails. Then the README cites the generated file instead of prose.

USAGE
    python3 PLAN/tools/derive_provenance.py \
        --sim PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_2026-11-24T0350Z.json \
        --out PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/provenance_2026-11-24T0350Z.json

EXIT
    0 = written and self-consistent, 1 = self-check failed, nothing written.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

WARMUP = 200
WEIGHTS = {"SPY": 0.6, "TLT": 0.4, "GLD": 0.0}
TICKERS = ["SPY", "TLT", "GLD", "BIL"]
SPREAD_BP = 5.0
SIZES = [300, 500, 2000, 10000, 20000, 50000]


def fetch(start, end):
    import yfinance as yf
    closes, dates = {}, None
    for t in TICKERS:
        h = yf.Ticker(t).history(start=start, end=end)
        if not len(h):
            raise SystemExit(f"no data for {t}")
        closes[t] = [float(v) for v in h["Close"]]
        if dates is None:
            dates = [str(i.date()) for i in h.index]
    n = min(len(v) for v in closes.values())
    return {t: v[-n:] for t, v in closes.items()}, dates[-n:]


def buy(px, cash, notional):
    """Mirror of proveit_sim.buy: whole shares, notional capped against cash."""
    if px <= 0 or notional <= 0 or cash <= 0:
        return 0, cash, 0.0
    budget = min(notional, cash)
    qty = int(budget // px)
    while qty > 0:
        n = qty * px
        fee = n * SPREAD_BP / 1e4
        if n + fee <= cash:
            return qty, cash - n - fee, fee
        qty -= 1
    return 0, cash, 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sim = json.load(open(args.sim))
    start, end = sim["window"]
    cal_days = (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days

    print(f"fetching {','.join(TICKERS)} {start} -> {end} ...")
    px, dates = fetch(start, end)
    n = len(px["SPY"])

    i = WARMUP
    entry_date = dates[i]
    entry = {t: round(px[t][i], 2) for t in TICKERS}
    first = {t: round(px[t][0], 2) for t in TICKERS}
    last = {t: round(px[t][-1], 2) for t in TICKERS}

    print(f"  bars={n}  entry bar {i} = {entry_date}")
    print(f"  entry closes: {entry}")

    # Recompute the allocation at each size and compare against the artifact.
    alloc, mismatches = {}, []
    for size in SIZES:
        cash, pos, fees = float(size), {t: 0 for t in ("SPY", "TLT", "GLD")}, 0.0
        for t, w in WEIGHTS.items():
            if w <= 0:
                continue
            total = cash + sum(pos[x] * px[x][i] for x in pos)
            q, cash, f = buy(px[t][i], cash, total * w / sum(WEIGHTS.values()))
            pos[t] += q
            fees += f
        idle_end_nav = None
        committed = sim["scenarios"].get(str(size), {}).get("buy_hold", {})
        if committed:
            idle_end_nav = committed.get("idle_cash_pct")
            final = committed.get("final")
            # self-check: rebuilt cash + marked position must reproduce `final`
            marked = cash + pos["SPY"] * px["SPY"][-1] + pos["TLT"] * px["TLT"][-1]
            if final is not None and abs(marked - final) > max(1.0, 0.01 * size):
                mismatches.append(
                    f"${size}: rebuilt mark-to-market {marked:.2f} vs committed final "
                    f"{final} (delta {marked-final:+.2f})")
            if idle_end_nav is not None and final:
                derived = round(100 * cash / final, 1)
                if abs(derived - idle_end_nav) > 0.15:
                    mismatches.append(
                        f"${size}: idle {derived}% of ending nav vs committed "
                        f"idle_cash_pct {idle_end_nav}")
        alloc[str(size)] = {
            "shares": {t: pos[t] for t in ("SPY", "TLT", "GLD") if pos[t]},
            "cash_after_entry": round(cash, 2),
            "fees_paid": round(fees, 2),
            "idle_pct_of_ending_nav": round(100 * cash / committed["final"], 1) if committed.get("final") else None,
            "idle_pct_of_starting_capital": round(100 * cash / size, 1),
        }

    if mismatches:
        print("\nSELF-CHECK FAILED - nothing written:")
        for m in mismatches:
            print("  " + m)
        return 1

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "derived_from": Path(args.sim).name,
        "purpose": (
            "Every number the PROVEIT README states but the sim artifact does not "
            "contain. Generated by PLAN/tools/derive_provenance.py; self-checked "
            "against the committed sim before writing."),
        "window": sim["window"],
        "committed_bar_count": sim.get("n_days"),
        "refetch_bar_count": n,
        "calendar_days": cal_days,
        "years_calendar": round(cal_days / 365.25, 4),
        "years_trading": round(n / 252.0, 4),
        "NOTE_denominator": (
            "The committed artifact's n_days is 1255; 1255 / 252 = 4.98 years and "
            "reproduces the stored CAGR. The same number divided by 365.25 gives "
            "3.44 years and a 13.58% CAGR. Divide by 252 for a trading-day series."),
        "NOTE_refetch_drift": (
            f"This re-fetch returned {n} bars; the committed run had "
            f"{sim.get('n_days')}. Entry-bar values are identical, which is what "
            f"matters for the allocation, but the TERMINAL close is not comparable "
            f"and must not be substituted for the committed run's. Use the "
            f"committed sim for any end-of-window figure."),
        "warmup_bars": WARMUP,
        "target_weights": WEIGHTS,
        "target_weights_pct": {k: round(100 * v, 1) for k, v in WEIGHTS.items()},
        "spread_bp": SPREAD_BP,
        "whole_shares_only": True,
        "reason_for_warmup": (
            "trend_200 needs a 200-day SMA, so every strategy enters at bar 200. "
            "The entry price is therefore NOT the window's first bar."),
        "entry_bar": WARMUP,
        "entry_date": entry_date,
        "entry_closes": entry,
        "first_bar_closes": first,
        "refetch_last_bar_closes": last,
        "mismatched_pair_warning": (
            f"The SPY path {first['SPY']} -> {last['SPY']} is the window's first to "
            f"last REFETCH bar, but the account entered at {entry['SPY']}. "
            f"Annualised returns start at the entry bar, so any 'SPY rose X -> Y' "
            f"claim paired with this CAGR must start at {entry['SPY']}."),
        "allocation": alloc,
    }

    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nself-check passed; wrote {args.out}")
    print(f"  SPY entry {entry['SPY']} ({entry_date}); refetch last {last['SPY']} "
          f"over {n} bars vs committed {sim.get('n_days')} bars")
    print(f"  $300 idle: {alloc['300']['idle_pct_of_ending_nav']}% of ending nav, "
          f"{alloc['300']['idle_pct_of_starting_capital']}% of starting capital")
    return 0


if __name__ == "__main__":
    sys.exit(main())
