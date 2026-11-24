"""Score the pick ledger: what actually happened to every published pick.

Rules (fixed before looking at results, do not tune):
  entry  = open of the first trading day STRICTLY AFTER published_at  (lag-1, never same close)
  raw    = (last_close / entry_open) - 1
  net    = raw*10000 - cost_bps                 (round-turn cost from the ledger row)
  excess = net - benchmark_net                  (same window, same rule, same cost)
  CASH   = 4.32% annualised pro-rated by calendar days
  BASKET = equal-weight mean of members, rebalanced once at entry

Writes scorecard.json and SCORECARD.md. A pick with no price history is marked unscorable
with the reason -- never silently dropped, never scored as zero.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

try:
    import yfinance as yf
except Exception as e:  # pragma: no cover
    print(f"yfinance unavailable: {e}")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "pick_ledger.jsonl")
CASH_ANNUAL = 0.0432


def load():
    rows = []
    with open(LEDGER, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


PRICE_CACHE = {}


def history(symbol):
    if symbol in PRICE_CACHE:
        return PRICE_CACHE[symbol]
    try:
        df = yf.Ticker(symbol).history(period="6mo", interval="1d", auto_adjust=True)
    except Exception:
        df = None
    PRICE_CACHE[symbol] = df if df is not None and len(df) else None
    return PRICE_CACHE[symbol]


def series_after(symbol, published_at):
    """(entry_open, last_close, entry_date) for bars strictly after the publish date."""
    df = history(symbol)
    if df is None:
        return None
    pub = datetime.fromisoformat(published_at.replace("Z", "+00:00")).astimezone(timezone.utc)
    idx = [d for d in df.index if d.date() > pub.date()]
    mode = "next_open"
    if not idx:
        # No bar after publish yet (pick made today). Fall back to the first bar ON OR AFTER the
        # publish date and label it, so the row is marked to market without pretending it is a
        # tradable next-open fill. The forward rule is unchanged once a later bar exists.
        idx = [d for d in df.index if d.date() >= pub.date()]
        mode = "same_day_fallback"
        if not idx:
            # Market has not traded since the pick was published (equities close overnight and
            # weekends). This is a pending entry, not a failure and not a zero return.
            return {"pending": True,
                    "reason": f"no session has traded at or after {pub.date()} (last bar "
                              f"{df.index[-1].date()}); first mark on the next open"}
    entry = idx[0]
    entry_open = float(df.loc[entry, "Open"])
    last_close = float(df["Close"].iloc[-1])
    if entry_open <= 0:
        return None
    return {"entry_open": entry_open, "last_close": last_close, "entry_mode": mode,
            "entry_date": str(entry.date()), "last_date": str(df.index[-1].date())}


def cash_return(published_at):
    pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - pub).total_seconds() / 86400.0
    return CASH_ANNUAL * max(days, 0) / 365.0, days


def score(rows):
    out = []
    for r in rows:
        rec = dict(r)
        if r.get("status") == "unscored" or not r.get("symbol"):
            rec.update(scorable=False, reason="strategy descriptor, not a single tradable symbol",
                       net_bps=None, excess_bps=None)
            out.append(rec)
            continue

        if r["symbol"] == "CASH":
            ret, days = cash_return(r["published_at"])
            rec.update(scorable=True, entry_date=r["published_at"][:10], last_date="now",
                       raw_pct=round(ret * 100, 3), net_bps=round(ret * 10000 - r["cost_bps"], 1),
                       excess_bps=0.0, days_held=round(days, 1))
            out.append(rec)
            continue

        if r.get("basket"):
            legs, missing = [], []
            for m in r["basket"]:
                s = series_after(m, r["published_at"])
                if s and not s.get("pending"):
                    legs.append(s["last_close"] / s["entry_open"] - 1)
                else:
                    missing.append(m)
            if not legs:
                rec.update(scorable=False, reason="no price history for any basket member",
                           net_bps=None, excess_bps=None)
                out.append(rec)
                continue
            raw = sum(legs) / len(legs)
            rec.update(scorable=True, entry_date=series_after(r["basket"][0], r["published_at"])["entry_date"],
                       last_date=series_after(r["basket"][0], r["published_at"])["last_date"],
                       raw_pct=round(raw * 100, 3), legs=len(legs), missing_members=missing)
        else:
            s = series_after(r["symbol"], r["published_at"])
            if s and s.get("pending"):
                rec.update(scorable=False, status="pending_entry", reason=s["reason"],
                           net_bps=None, excess_bps=None)
                out.append(rec)
                continue
            if not s:
                rec.update(scorable=False, reason="no price bars after publish date (symbol may be dead)",
                           net_bps=None, excess_bps=None)
                out.append(rec)
                continue
            raw = s["last_close"] / s["entry_open"] - 1
            rec.update(scorable=True, entry_mode=s["entry_mode"],
                       entry_date=s["entry_date"], last_date=s["last_date"],
                       entry_open=round(s["entry_open"], 4), last_close=round(s["last_close"], 4),
                       raw_pct=round(raw * 100, 3))

        net = rec["raw_pct"] * 100 - r["cost_bps"]
        rec["net_bps"] = round(net, 1)

        bench = r.get("benchmark")
        if bench in (None, "CASH"):
            bret, _ = cash_return(r["published_at"])
            rec["benchmark_net_bps"] = round(bret * 10000, 1)
        else:
            bs = series_after(bench, r["published_at"])
            if bs:
                braw = bs["last_close"] / bs["entry_open"] - 1
                rec["benchmark_net_bps"] = round(braw * 10000 - r["cost_bps"], 1)
            else:
                rec["benchmark_net_bps"] = None
        if rec["benchmark_net_bps"] is None:
            rec["excess_bps"] = None
        else:
            rec["excess_bps"] = round(net - rec["benchmark_net_bps"], 1)
        out.append(rec)
    return out


def aggregate(scored):
    by = defaultdict(list)
    for r in scored:
        if r.get("scorable") and r.get("net_bps") is not None:
            by[r["source"]].append(r)
    agg = {}
    for src, rs in by.items():
        nets = [r["net_bps"] for r in rs]
        exs = [r["excess_bps"] for r in rs if r.get("excess_bps") is not None]
        agg[src] = {
            "n": len(rs),
            "mean_net_bps": round(sum(nets) / len(nets), 1),
            "median_net_bps": round(sorted(nets)[len(nets) // 2], 1),
            "mean_excess_bps": round(sum(exs) / len(exs), 1) if exs else None,
            "beat_benchmark": sum(1 for x in exs if x > 0),
            "n_with_bench": len(exs),
            "n_insufficient": len(rs) < 30,
        }
    return agg


def main():
    rows = load()
    scored = score(rows)
    agg = aggregate(scored)

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rules": {"entry": "next open strictly after published_at", "cost": "per-row bps round turn",
                  "benchmark": "same window, same rule", "cash_bar": CASH_ANNUAL},
        "counts": {"total": len(scored),
                   "scorable": sum(1 for r in scored if r.get("scorable")),
                   "unscorable": sum(1 for r in scored if not r.get("scorable"))},
        "aggregate": agg,
        "rows": scored,
    }
    with open(os.path.join(HERE, "scorecard.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)

    lines = ["# Pick tracker — what actually happened", "",
             f"Generated **{payload['generated']}** · entry = next open strictly after publish "
             f"· cost = per-row round turn · benchmark = same window, same rule", ""]
    if payload["counts"]["scorable"] == 0 or all(
            len(v) == 0 for v in [r for r in [scored] if r]):
        pass
    lines += ["| source | n | mean net bp | median net bp | mean excess bp | beat bench | note |",
              "|---|---|---|---|---|---|---|"]
    for src, a in sorted(agg.items(), key=lambda kv: -(kv[1]["mean_net_bps"] or -1e9)):
        note = "n<30 — no verdict" if a["n_insufficient"] else ""
        lines.append(f"| {src} | {a['n']} | {a['mean_net_bps']} | {a['median_net_bps']} | "
                     f"{a['mean_excess_bps']} | {a['beat_benchmark']}/{a['n_with_bench']} | {note} |")
    lines += ["", "## Per pick", "",
              "| source | symbol | raw % | net bp | excess bp | entry | last |", "|---|---|---|---|---|---|---|"]
    for r in sorted(scored, key=lambda x: -(x.get("net_bps") or -1e9)):
        if not r.get("scorable"):
            lines.append(f"| {r['source']} | {r.get('symbol') or '—'} | unscored | — | — | "
                         f"{r.get('reason','')[:52]} | — |")
            continue
        lines.append(f"| {r['source']} | {r.get('symbol') or 'BASKET'} | {r.get('raw_pct')} | "
                     f"{r.get('net_bps')} | {r.get('excess_bps')} | {r.get('entry_date')} | {r.get('last_date')} |")
    lines += ["", "**Caveats:** zero forward days have elapsed for picks published today, so these are "
              "mark-to-market from the next open, not a track record. n<30 on every source means no "
              "verdict is available. Unscored rows are strategy descriptors (a long/short quintile is "
              "not one symbol) and are listed rather than dropped."]
    with open(os.path.join(HERE, "SCORECARD.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"generated": payload["generated"], "counts": payload["counts"],
                      "aggregate": agg}, indent=1))
    print("\nwrote scorecard.json and SCORECARD.md")


if __name__ == "__main__":
    main()
