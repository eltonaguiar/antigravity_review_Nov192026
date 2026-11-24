#!/usr/bin/env python3
"""Does the consensus LABEL order forward returns? Permutation null + Spearman.

The harvest raw JSONs carry 4 monthly recommendationTrend periods per symbol
(0m, -1m, -2m, -3m). For each period with a complete forward window we:
  * derive the label from that period's counts with the page's own two-condition rule
  * measure forward EXCESS return vs SPY from the first trading day strictly after
    the period date to the first trading day strictly after the next period date
  * test monotonicity: Spearman between label rank (SS=1 ... SB=5) and excess return,
    with a permutation p-value (labels shuffled WITHIN symbol, which preserves each
    symbol's own volatility while destroying the label-return link)
  * report mean excess per label with a symbol-clustered bootstrap CI

Coverage note: consensus exists for STOCK only in this feed, so ETF/BOND/FUND/
CRYPTO are absent BY CONSTRUCTION, not by choice.

Seed fixed; re-running reproduces the p-values.
"""
from __future__ import annotations

import glob
import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path

SEED = 20261124
N_PERM = 2000
N_BOOT = 2000
LEDGER = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest")
OUT = Path(__file__).resolve().parent / "consensus_label_backtest.json"

LABELS = ["STRONG_SELL", "SELL", "HOLD", "BUY", "STRONG_BUY"]
RANK = {name: i + 1 for i, name in enumerate(LABELS)}


def label_from_counts(sb, b, h, s, ss):
    n = sb + b + h + s + ss
    if n == 0:
        return None, None
    score = (2 * sb + b - s - 2 * ss) / n
    share = (sb + b) / n
    if score >= 1.0 and share >= 0.75:
        lab = "STRONG_BUY"
    elif score >= 0.3 and share >= 0.50:
        lab = "BUY"
    elif score <= -1.0 and share <= 0.15:
        lab = "STRONG_SELL"
    elif score <= -0.3 and share <= 0.30:
        lab = "SELL"
    else:
        lab = "HOLD"
    return lab, round(score, 4)


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def period_date(months_back: int, today: datetime) -> str:
    y, m = today.year, today.month - months_back
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}-01"


def main() -> int:
    import yfinance as yf

    today = datetime.now(timezone.utc)
    # period key -> months back
    per = {"0m": 0, "-1m": 1, "-2m": 2, "-3m": 3}

    # ---- collect consensus periods per symbol -------------------------------
    trend_by_symbol: dict[str, dict[str, dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok":
                continue
            for t in rec.get("trend") or []:
                if t.get("period") in per:
                    trend_by_symbol.setdefault(sym, {})[t["period"]] = t

    spy = yf.Ticker("SPY").history(period="1y", interval="1d", auto_adjust=True)
    spy_c = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    obs = []   # (symbol, period, rank, excess)
    non_finite = []   # (symbol, period, a, b) -- excluded and REPORTED, never averaged
    for sym, periods in trend_by_symbol.items():
        try:
            df = yf.Ticker(sym).history(period="1y", interval="1d", auto_adjust=True)
        except Exception:
            continue
        if not len(df):
            continue
        idx = [d.date() for d in df.index]
        closes = [float(c) for c in df["Close"]]
        for pk, months_back in per.items():
            if pk not in periods or months_back == 0:
                continue   # 0m has no complete forward window yet
            t = periods[pk]
            lab, _ = label_from_counts(t.get("strongBuy", 0), t.get("buy", 0),
                                       t.get("hold", 0), t.get("sell", 0),
                                       t.get("strongSell", 0))
            if lab is None:
                continue
            start = datetime.strptime(period_date(months_back, today), "%Y-%m-%d").date()
            end = datetime.strptime(period_date(months_back - 1, today), "%Y-%m-%d").date()
            i = next((k for k, d in enumerate(idx) if d > start), None)
            j = next((k for k, d in enumerate(idx) if d > end), None)
            if i is None or j is None or j <= i:
                continue
            if idx[i] not in spy_c or idx[j] not in spy_c:
                continue
            if not (closes[i] and closes[i] > 0 and math.isfinite(closes[i])
                    and math.isfinite(closes[j])):
                non_finite.append((sym, pk, closes[i], closes[j]))
                continue
            stock = closes[j] / closes[i] - 1
            bench = spy_c[idx[j]] / spy_c[idx[i]] - 1
            ex = stock - bench
            if not math.isfinite(ex):
                non_finite.append((sym, pk, stock, bench))
                continue
            obs.append((sym, pk, RANK[lab], ex, lab))

    print(f"observations: {len(obs)}  symbols: {len({o[0] for o in obs})}"
          f"  excluded_non_finite: {len(non_finite)}")
    for nf in non_finite[:10]:
        print(f"  EXCLUDED (non-finite return): {nf}")
    if len(obs) < 30:
        print("insufficient observations")
        return 1
    ranks = [o[2] for o in obs]
    rets = [o[3] for o in obs]
    rho = spearman(ranks, rets)
    print(f"Spearman(label rank, excess return) = {rho:+.4f}")

    # ---- permutation within symbol ----------------------------------------
    rng = random.Random(SEED)
    by_sym: dict[str, list[int]] = {}
    for k, o in enumerate(obs):
        by_sym.setdefault(o[0], []).append(k)
    null = []
    for _ in range(N_PERM):
        perm_r = list(ranks)
        for idxs in by_sym.values():
            vals = [ranks[k] for k in idxs]
            rng.shuffle(vals)
            for k, v in zip(idxs, vals):
                perm_r[k] = v
        null.append(spearman(perm_r, rets))
    p = (sum(1 for x in null if abs(x) >= abs(rho)) + 1) / (N_PERM + 1)
    print(f"permutation p (two-sided, within-symbol shuffle, {N_PERM} draws, seed {SEED}) = {p:.4f}")

    # ---- per label, with a symbol-clustered bootstrap ---------------------
    print(f"\n{'label':<12}{'n':>6}{'symbols':>9}{'mean excess %':>16}{'95% CI (by symbol)':>24}")
    per_label = {}
    syms = sorted(by_sym)
    for lab in LABELS:
        rs = [o[3] for o in obs if o[4] == lab]
        if not rs:
            continue
        m = statistics.mean(rs)
        means = []
        for _ in range(N_BOOT):
            pick = [rng.choice(syms) for _ in syms]
            sample = [o[3] for s in pick for o in obs if o[0] == s and o[4] == lab]
            if sample:
                means.append(statistics.mean(sample))
        means.sort()
        lo = means[int(0.025 * len(means))] if means else None
        hi = means[int(0.975 * len(means)) - 1] if means else None
        per_label[lab] = {"n": len(rs), "mean_excess_pct": round(100 * m, 4),
                          "ci95_pct": [round(100 * lo, 4), round(100 * hi, 4)]}
        print(f"{lab:<12}{len(rs):>6}{len({o[0] for o in obs if o[4]==lab}):>9}"
              f"{100*m:>16.3f}{f'[{100*lo:+.3f}, {100*hi:+.3f}]':>24}")

    OUT.write_text(json.dumps({
        "generated": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "n_perm": N_PERM, "n_boot": N_BOOT,
        "n_obs": len(obs), "n_symbols": len(by_sym),
        "coverage_note": "consensus exists for STOCK only; other classes absent by construction",
        "spearman_rho": round(rho, 5), "permutation_p": round(p, 5),
        "per_label": per_label,
        "kilo_reference": {"STRONG_BUY": {"mean_excess_pct": 1.325,
                                         "ci95_pct": [-0.329, 3.109]}},
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
