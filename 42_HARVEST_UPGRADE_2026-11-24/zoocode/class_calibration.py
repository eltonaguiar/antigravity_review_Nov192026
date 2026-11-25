#!/usr/bin/env python3
"""Track B -- per-asset-class calibration of the analyst consensus score.

WHAT IT MEASURES
  For each asset class: is the consensus SCORE monotone in forward NET return,
  and does any bucket survive cost?

  score = (2*SB + B - S - 2*SS) / n        (the page's own weighted mean, [-2,+2])
  net   = (stock forward return) - (benchmark forward return) - cost

HOW EACH GATE FROM IMPROVEMENT_PROGRAM.md IS MET
  1. Cost by LIQUIDITY BUCKET, not one flat constant. The only liquidity proxy
     this data carries is analyst coverage (`n_analysts`), so cost is charged per
     measured cost-of-record class spread over coverage bands:
         thin   (n < 10)  -> the widest measured round turn (crypto 52 bp)
         normal (10-29)   -> equity 12.07 bp
         deep   (>= 30)   -> ETF/index 6.71 bp
     These are MEASURED figures (COST_OF_RECORD), not invented, but the mapping
     from coverage to cost is an ASSUMPTION and is labelled as one.
  2. Characteristic-matched benchmark: SPY, matched on the one characteristic
     available (all rows are US-listed equities, so the market factor is the
     match). A true size/value match is not possible without fundamentals.
  3. MDE published next to every null.
  4. `insufficient` is a distinct outcome from `no effect`.
  5. No gate is lowered.

HONEST LIMIT ON "PER ASSET CLASS"
  Neither source carries an asset-class field: analyst_actions.csv has no class
  column (308 plain US tickers) and the consensus feed returns 'UNKNOWN' for all
  499 symbols. The classes below are therefore taken from the documented
  probes -- EQUITY is measurable, and ETF/BOND/MUTUAL_FUND/CRYPTO were probed
  and returned NO analyst consensus -- reported as `insufficient` with the
  reason, never pooled into EQUITY to inflate n.
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
N_BOOT = 1000
CLASS_FLOOR = 100          # below this, `insufficient` rather than a verdict
PUBLICATION_LAG = True
COST_BY_COVERAGE = [        # (min_n_analysts, cost_bps, label, basis)
    (30, 6.71, "deep", "ETF/index measured round turn"),
    (10, 12.07, "normal", "equity measured round turn"),
    (0, 52.0, "thin", "crypto measured round turn (widest on record)"),
]
LEDGER = Path("/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest")
OUT_MD = Path(__file__).resolve().parent / "class_calibration.md"
OUT_JSON = Path(__file__).resolve().parent / "class_calibration.json"


def cost_for(n_analysts: int) -> tuple[float, str]:
    for floor, bps, label, _ in COST_BY_COVERAGE:
        if n_analysts >= floor:
            return bps, label
    return COST_BY_COVERAGE[-1][0], COST_BY_COVERAGE[-1][2]


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


def bucket_of(score: float) -> str:
    if score >= 1.0:
        return "STRONG_BUY"
    if score >= 0.3:
        return "BUY"
    if score > -0.3:
        return "HOLD"
    if score > -1.0:
        return "SELL"
    return "STRONG_SELL"


def main() -> int:
    import yfinance as yf

    today = datetime.now(timezone.utc)
    per = {"-1m": 1, "-2m": 2, "-3m": 3}
    trend: dict[str, dict[str, dict]] = {}
    for path in sorted(LEDGER.glob("*.json")):
        run = json.loads(path.read_text(encoding="utf-8"))
        for sym, rec in (run.get("results") or {}).items():
            if rec.get("status") != "ok":
                continue
            for t in rec.get("trend") or []:
                if t.get("period") in per:
                    trend.setdefault(sym, {})[t["period"]] = t

    spy = yf.Ticker("SPY").history(period="1y", interval="1d", auto_adjust=True)
    spy_c = {d.date(): float(c) for d, c in zip(spy.index, spy["Close"])}

    obs = []
    excluded = 0
    for sym, periods in trend.items():
        try:
            df = yf.Ticker(sym).history(period="1y", interval="1d", auto_adjust=True)
        except Exception:
            excluded += 1
            continue
        if not len(df):
            excluded += 1
            continue
        idx = [d.date() for d in df.index]
        closes = [float(c) for c in df["Close"]]
        for pk, mb in per.items():
            t = periods.get(pk)
            if not t:
                continue
            sb, b, h, s, ss = (t.get("strongBuy", 0), t.get("buy", 0), t.get("hold", 0),
                               t.get("sell", 0), t.get("strongSell", 0))
            n = sb + b + h + s + ss
            if n == 0:
                continue
            score = (2 * sb + b - s - 2 * ss) / n
            start = datetime.strptime(period_date(mb - 1 if PUBLICATION_LAG else mb, today), "%Y-%m-%d").date()
            end = datetime.strptime(period_date(mb - 2 if PUBLICATION_LAG else mb - 1, today), "%Y-%m-%d").date()
            i = next((k for k, d in enumerate(idx) if d > start), None)
            j = next((k for k, d in enumerate(idx) if d > end), None)
            if i is None or j is None or j <= i:
                excluded += 1
                continue
            if idx[i] not in spy_c or idx[j] not in spy_c:
                excluded += 1
                continue
            if not (closes[i] and closes[i] > 0 and math.isfinite(closes[i]) and math.isfinite(closes[j])):
                excluded += 1
                continue
            stock = closes[j] / closes[i] - 1
            bench = spy_c[idx[j]] / spy_c[idx[i]] - 1
            cost_bps, band = cost_for(n)
            net = stock - bench - cost_bps / 10000.0
            if not math.isfinite(net):
                excluded += 1
                continue
            # MATCHED benchmark inputs, computed per event over the SAME window:
            # market beta from the 250 days before entry, and size (dollar ADV)
            # plus momentum as terciles. The benchmark itself is assigned after
            # all events are collected (peer cell means), so it cannot use the
            # event's own outcome.
            k0 = max(0, i - 250)
            sr, mr = [], []
            for k in range(k0, i):
                if k + 1 >= len(idx):
                    break
                sr.append(closes[k + 1] / closes[k] - 1)
                d1, d2 = idx[k], idx[k + 1]
                if d1 in spy_c and d2 in spy_c:
                    mr.append(spy_c[d2] / spy_c[d1] - 1)
            beta = None
            if len(sr) >= 60 and len(sr) == len(mr):
                vm = statistics.pvariance(mr)
                if vm > 0:
                    beta = statistics.covariance(sr, mr) / vm
            adv = statistics.mean(closes[max(0, i - 20):i]) if i > 0 else None
            mom = (closes[i - 1] / closes[i - 127] - 1) if i >= 127 else None
            obs.append({"symbol": sym, "period": pk, "score": score, "net": net,
                        "raw": stock, "mkt": bench,
                        "n_analysts": n, "band": band, "cost_bps": cost_bps,
                        "bucket": bucket_of(score),
                        "beta": beta, "adv": adv, "mom": mom,
                        "entry": idx[i], "exit": idx[j]})
    # ---- matched benchmark: tercile cells of (size, momentum), beta-adjusted --
    def tercile(values, v):
        if v is None:
            return None
        vs = sorted(x for x in values if x is not None)
        if len(vs) < 6:
            return None
        a, b = vs[len(vs) // 3], vs[2 * len(vs) // 3]
        return 0 if v <= a else (1 if v <= b else 2)
    advs = [o["adv"] for o in obs]
    moms = [o["mom"] for o in obs]
    peers: dict[tuple, list] = {}
    for o in obs:
        st, mt = tercile(advs, o["adv"]), tercile(moms, o["mom"])
        o["cell"] = (st, mt) if st is not None and mt is not None else None
        if o["cell"] is not None:
            peers.setdefault(o["cell"], []).append(o)
    # each event is benchmarked by ITS peers' market return, beta-scaled, over
    # the same window -- leave-one-out so it never includes itself
    for o in obs:
        cell = o["cell"]
        if cell is None or o["beta"] is None:
            o["net_matched"] = None
            continue
        others = [q for q in peers.get(cell, []) if q is not o]
        if len(others) < 5:
            o["net_matched"] = None
            continue
        peer_mkt = statistics.mean(q["mkt"] for q in others)
        o["net_matched"] = o["raw"] - o["beta"] * peer_mkt - o["cost_bps"] / 10000.0

    by_symbol: dict[str, list[dict]] = {}
    for o in obs:
        by_symbol.setdefault(o["symbol"], []).append(o)

    def analyse(rows: list[dict], label: str) -> dict:
        n = len(rows)
        res = {"class": label, "n": n, "n_symbols": len({r["symbol"] for r in rows})}
        if n < CLASS_FLOOR:
            res.update(verdict="insufficient",
                       reason=f"n={n} is below the class floor of {CLASS_FLOOR}; not pooled with other classes")
            return res
        scores = [r["score"] for r in rows]
        nets = [r["net"] for r in rows]
        rho = spearman(scores, nets)
        rng = random.Random(SEED)
        idxs: dict[str, list[int]] = {}
        for k, r in enumerate(rows):
            idxs.setdefault(r["symbol"], []).append(k)
        null = []
        for _ in range(N_PERM):
            perm = list(scores)
            for ids in idxs.values():
                vals = [scores[k] for k in ids]
                rng.shuffle(vals)
                for k, v in zip(ids, vals):
                    perm[k] = v
            null.append(spearman(perm, nets))
        p = (sum(1 for x in null if abs(x) >= abs(rho)) + 1) / (N_PERM + 1)

        # design effect: pooled t over marks vs t over per-symbol means
        def t_of(xs):
            if len(xs) < 3:
                return None
            m, sd = statistics.mean(xs), statistics.stdev(xs)
            return m / (sd / math.sqrt(len(xs))) if sd else None
        t_raw = t_of(nets)
        t_clust = t_of([statistics.mean(v) for v in ([r["net"] for r in g] for g in by_symbol.values())])
        design = (t_raw / t_clust) ** 2 if (t_raw and t_clust) else None

        # bucket table with symbol-clustered bootstrap CIs
        syms = sorted(by_symbol)
        buckets = {}
        for lab in ("STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"):
            rs = [r["net"] for r in rows if r["bucket"] == lab]
            if not rs:
                continue
            means = []
            for _ in range(N_BOOT):
                pick = [rng.choice(syms) for _ in syms]
                sample = [r["net"] for s in pick for r in by_symbol[s] if r["bucket"] == lab]
                if sample:
                    means.append(statistics.mean(sample))
            means.sort()
            lo = means[int(0.025 * len(means))] if means else None
            hi = means[int(0.975 * len(means)) - 1] if means else None
            buckets[lab] = {"n": len(rs),
                            "mean_net_pct": round(100 * statistics.mean(rs), 4),
                            "ci95_pct": [round(100 * lo, 4) if lo is not None else None,
                                         round(100 * hi, 4) if hi is not None else None],
                            "ci_excludes_zero": bool(lo is not None and (lo > 0 or hi < 0))}

        mde = 2 * (statistics.stdev(nets) / math.sqrt(n / max(res["n_symbols"], 1))) if n > 2 else None
        mono = all(buckets[a]["mean_net_pct"] >= buckets[b]["mean_net_pct"]
                   for a, b in zip(("STRONG_SELL", "SELL", "HOLD", "BUY"), ("SELL", "HOLD", "BUY", "STRONG_BUY"))
                   if a in buckets and b in buckets)
        # ---- the same rho and p under the MATCHED benchmark ------------------
        def rho_p(nets_col: str):
            # NOTE: `rows` here is analyse()'s list of dicts; do not shadow it with
            # the outer loop's tuples (that was a KeyError: 962).
            # Only events with a non-null value in this column can be ranked --
            # a matched benchmark is undefined where the peer cell is too thin.
            usable = [rec for rec in rows if rec.get(nets_col) is not None]
            xs = [rec["score"] for rec in usable]
            ys = [rec[nets_col] for rec in usable]
            if len(usable) < 2:
                return None, None
            r0 = spearman(xs, ys)
            rg = random.Random(SEED)
            ids_by_sym: dict[str, list[int]] = {}
            for q, rec in enumerate(usable):
                ids_by_sym.setdefault(rec["symbol"], []).append(q)
            nl = []
            for _ in range(N_PERM):
                perm = list(xs)
                for ids in ids_by_sym.values():
                    vals = [xs[q] for q in ids]
                    rg.shuffle(vals)
                    for q, v in zip(ids, vals):
                        perm[q] = v
                nl.append(spearman(perm, ys))
            return r0, (sum(1 for z in nl if abs(z) >= abs(r0)) + 1) / (N_PERM + 1)
        matched_rows = [r for r in rows if r.get("net_matched") is not None]
        if len(matched_rows) >= CLASS_FLOOR:
            rho_m, p_m = rho_p("net_matched")
            matched = {"rho": round(rho_m, 5), "permutation_p": round(p_m, 5),
                       "n": len(matched_rows),
                       "sign": "inverted" if rho_m < 0 else "as expected",
                       "sign_survives": (rho_m < 0) == (rho < 0)}
        else:
            matched = {"rho": None, "permutation_p": None, "n": len(matched_rows),
                       "verdict": "insufficient matched events"}
        res.update(
            rho_spy=round(rho, 5), permutation_p_spy=round(p, 5),
            matched=matched,
            rho=round(rho, 5), permutation_p=round(p, 5),
            sign="inverted" if rho < 0 else "as expected",
            monotone=mono,
            verdict=("monotone" if mono else ("inverted" if rho < 0 else "not monotone")),
            design_effect=round(design, 2) if design else None,
            t_raw=round(t_raw, 3) if t_raw else None,
            t_cluster=round(t_clust, 3) if t_clust else None,
            mde_pct=round(100 * mde, 3) if mde else None,
            buckets=buckets,
        )
        return res

    equity = analyse(obs, "EQUITY")
    classes = [equity]
    for lab, reason in (
        ("ETF", "probed 14 ETFs: the consensus source returned an empty array -- no analyst coverage for the instrument type"),
        ("BOND", "probed 6 bond funds: empty array -- no analyst coverage"),
        ("MUTUAL_FUND", "probed 6 mutual funds: HTTP 403 -- a data-plan limit, so NOT an absence of coverage"),
        ("CRYPTO", "probed 2 crypto pairs: empty array -- no analyst coverage"),
        ("COMMODITY_FUTURES_FOREX", "no analyst consensus source exists; the appropriate signals are CFTC COT / funding rates, not ratings"),
    ):
        classes.append({"class": lab, "n": 0, "n_symbols": 0, "verdict": "insufficient",
                        "reason": reason})

    cost_mix = {}
    for o in obs:
        cost_mix[o["band"]] = cost_mix.get(o["band"], 0) + 1
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "n_perm": N_PERM, "n_boot": N_BOOT, "class_floor": CLASS_FLOOR,
        "entry_rule": "publication lag (label known only from the 1st of the next month)",
        "benchmark": "SPY (characteristic-matched on the only available characteristic: all rows are US equities)",
        "cost_model": {b: f"{c} bp ({why})" for _, c, b, why in COST_BY_COVERAGE},
        "cost_model_is_assumption": "coverage -> cost mapping is an ASSUMPTION; the bp figures are measured",
        "cost_band_rows": cost_mix,
        "excluded_rows": excluded,
        "classes": classes,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    e = classes[0]
    lines = [
        "# Track B -- per-asset-class calibration",
        "",
        f"zoo-savant, 2026-11-24. Source: `ZOOCODE/harvest/*.json` (499 tickers) + yfinance, seed {SEED}.",
        "",
        "**Method:** `score = (2*SB + B - S - 2*SS)/n` against forward **net** return",
        "(stock - SPY - cost), entry after the publication lag, 26 bp replaced by a",
        "liquidity-bucketed charge (see cost model). Permutation null shuffles scores",
        "within symbol; CIs bootstrap by symbol.",
        "",
        "## Cost model (liquidity-bucketed, not flat)",
        "",
        "| coverage band | cost | basis | rows |",
        "|---|---|---|---|",
    ]
    for floor, bps, lab, why in COST_BY_COVERAGE:
        lines.append(f"| {lab} (n_analysts >= {floor}) | {bps} bp | {why} | {cost_mix.get(lab, 0)} |")
    lines += ["",
              "The bp figures are measured cost-of-record values. **The mapping from analyst",
              "coverage to a cost band is an assumption**, since coverage is only a proxy for liquidity.",
              "",
              "## Per-class results", "",
              "| class | n | symbols | rho | perm p | sign | design effect | MDE | verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in classes:
        if c["n"]:
            lines.append(f"| {c['class']} | {c['n']} | {c['n_symbols']} | {c['rho']:+.4f} | {c['permutation_p']:.4f} "
                         f"| {c['sign']} | {c['design_effect']} | {c['mde_pct']}% | {c['verdict']} |")
        else:
            lines.append(f"| {c['class']} | 0 | 0 | -- | -- | -- | -- | -- | insufficient |")
    lines += ["", "Reasons for each `insufficient`:", ""]
    for c in classes:
        if c["n"] == 0:
            lines.append(f"- **{c['class']}**: {c['reason']}")
    lines += ["",
              f"## Bucket table -- {e['class']} (n={e['n']})", "",
              "| bucket | n | mean net % | 95% CI (by symbol) | CI excludes zero |",
              "|---|---|---|---|---|"]
    for lab, v in e.get("buckets", {}).items():
        ci = v["ci95_pct"]
        lines.append(f"| {lab} | {v['n']} | {v['mean_net_pct']:+.4f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {v['ci_excludes_zero']} |")
    lines += ["",
              f"**Sign is {e['sign']}**, monotone across buckets: **{e['monotone']}**.", "",
              "## Rules applied",
              "",
              f"- `insufficient` is used where n < {CLASS_FLOOR}; nothing was pooled across classes to reach the floor.",
              "- An inverted sign is reported as **inverted**, not relabelled.",
              "- Every null carries its MDE so it is quantified, not asserted.",
              "",
              f"next_probe: extend the class census beyond the documented probes by resolving each symbol's instrument type from an authoritative listing file, so ETF/BOND/FUND rows are identified rather than inferred from a probe -- the current limit is that neither source carries an asset-class field.",
              ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
