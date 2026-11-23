#!/usr/bin/env python3
"""
assess_contest.py -- the executor's scorer. Ignores everything an agent reports about itself.

Usage:
    python assess_contest.py --picks <picks.json> --prices <prices.json> [--out ledger.md] [--json]

prices.json format (executor supplies; one entry per symbol):
{
  "BTCUSD": [{"ts":"2026-11-23T09:30:00Z","open":91250,"high":92100,"low":90800,"close":91700}, ...],
  "SPY":    [...]
}

Rules implemented (from RULES.md):
  * pick must carry tp AND sl (except fund + buy_and_hold, scored on $ only)
  * entry is the FIRST bar's open at or after the round start -- never the agent's entry_ref_price
  * exit is the first touched barrier; on an ambiguous bar (both inside) the STOP wins
  * if neither barrier is touched by horizon_hours, exit at that bar's close
  * R = (exit-entry)/(entry-sl) for long, mirrored for short; net of the class cost in basis points
  * size caps are validated, not assumed

Exit code 1 on any invalid submission, so CI and the operator both see it.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone

# round-trip cost in basis points, per class -- mirrors COST_OF_RECORD.md
FILL_RELATIVE = False   # set by --fill-relative: clamp bracket geometry to the fill

COST_BP = {
    "bond": 0.6144, "etf": 6.7122, "equity": 12.0749, "fund": 0.0,
    "crypto": 52.0, "fx": 7.533, "commodity": 20.0,
    "option": 20.0, "futures": 20.0, "prediction": 175.0,
}
VALID_CLASSES = set(COST_BP)
VALID_SIDES = {"long", "short"}
VALID_RULES = {"market_at_next_open", "limit", "market_at_timestamp"}
VALID_STYLES = {"intraday", "swing", "buy_and_hold"}
REQUIRED = ("class", "symbol", "side", "entry_rule", "tp", "sl", "size_usd",
            "horizon_hours", "style")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def clamp_brackets(p):
    """Re-anchor the entrant's INTENDED risk geometry onto the actual fill.

    The defect this fixes (found by two independent models in a design review): voiding a pick whose
    fill already sits outside its bracket removes the only penalty for submitting an untradeable
    bracket, and it is exploitable in both directions — a near-zero-width bracket is almost always
    'inside' and is decided by the first tick, while a very wide bracket is never voided and is scored
    on the horizon-end price alone, i.e. a free one-shot directional option on every pick.

    Clamping keeps the entrant's own R multiple (their distance to stop and to target) but re-anchors
    it at the price that actually traded, so a stale anchor costs real R at the magnitude they chose
    instead of being laundered into a void.
    """
    stated = p.get("entry")
    if stated is None:
        stated = (float(p["tp"]) + float(p["sl"])) / 2.0
    stated = float(stated)
    risk = abs(stated - float(p["sl"]))
    reward = abs(float(p["tp"]) - stated)
    if risk <= 0 or reward <= 0:
        return None
    return risk, reward


def parse_ts(s):
    """Accept ISO-8601 strings, epoch seconds, or epoch milliseconds.

    Market feeds hand back all three: Yahoo and Binance give epoch numbers, a hand-written
    price file usually gives ISO. A scorer that only accepts one of them is a scorer that
    silently fails on the feed you actually have.
    """
    if isinstance(s, (int, float)):
        v = float(s)
        if v > 1e11:            # milliseconds
            v /= 1000.0
        return datetime.fromtimestamp(v, tz=timezone.utc)
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def validate(sub):
    errs, total = [], 0.0
    if not isinstance(sub.get("picks"), list) or not sub["picks"]:
        return ["no picks[] array"], 0.0
    for i, p in enumerate(sub["picks"]):
        tag = "picks[%d] %s" % (i, p.get("symbol", "?"))
        fund_long = (p.get("class") == "fund" and p.get("style") == "buy_and_hold")
        for f in REQUIRED:
            if f in ("tp", "sl") and fund_long:
                continue
            if p.get(f) in (None, ""):
                errs.append("%s: missing %s" % (tag, f))
        if p.get("class") not in VALID_CLASSES:
            errs.append("%s: unknown class %r" % (tag, p.get("class")))
        if p.get("side") not in VALID_SIDES:
            errs.append("%s: bad side %r" % (tag, p.get("side")))
        if p.get("entry_rule") not in VALID_RULES:
            errs.append("%s: bad entry_rule %r" % (tag, p.get("entry_rule")))
        if p.get("style") not in VALID_STYLES:
            errs.append("%s: bad style %r" % (tag, p.get("style")))
        if not fund_long:
            try:
                tp, sl = float(p["tp"]), float(p["sl"])
            except (KeyError, TypeError, ValueError):
                errs.append("%s: tp/sl not numeric" % tag)
                continue
            if p.get("side") == "long" and not (sl < tp):
                errs.append("%s: long needs sl < tp (sl=%s tp=%s)" % (tag, sl, tp))
            if p.get("side") == "short" and not (sl > tp):
                errs.append("%s: short needs sl > tp (sl=%s tp=%s)" % (tag, sl, tp))
        try:
            total += float(p.get("size_usd") or 0)
        except (TypeError, ValueError):
            errs.append("%s: size_usd not numeric" % tag)
    if total > 1000.0001:
        errs.append("size_usd total %.2f exceeds the $1000 budget" % total)
    return errs, total


def value_pick(p, bars):
    """Return dict with entry/exit/R/$ for one pick, or a void reason."""
    sym, side = p["symbol"], p["side"]
    if sym not in bars or not bars[sym]:
        return {"status": "VOID", "reason": "no price series for %s" % sym}
    series = sorted(bars[sym], key=lambda b: b["ts"])
    if p.get("entry_rule") == "limit":
        raise_ = "limit entry requires an explicit fill rule -- not implemented in R01"
        return {"status": "VOID", "reason": raise_}

    t0 = parse_ts(series[0]["ts"])
    entry = float(series[0]["open"])
    if entry <= 0:
        return {"status": "VOID", "reason": "non-positive entry price"}

    fund_long = (p["class"] == "fund" and p["style"] == "buy_and_hold")
    if fund_long:
        last = float(series[-1]["close"])
        pnl = (last - entry) / entry * float(p["size_usd"])
        return {"status": "OK", "entry": entry, "exit": last, "reason": "horizon",
                "R": None, "usd": round(pnl, 2), "note": "buy_and_hold: $ only"}

    tp, sl = float(p["tp"]), float(p["sl"])
    if FILL_RELATIVE:
        c = clamp_brackets(p)
        if c is None:
            return {"status": "VOID", "reason": "zero-width intended bracket"}
        risk, reward = c
        if side == "long":
            sl, tp = entry - risk, entry + reward
        else:
            sl, tp = entry + risk, entry - reward
    stop_width_pct = abs(entry - sl) / entry * 100.0
    # A bracket already violated at the fill price is not a trade; it is a mis-stated level.
    bad = None
    if side == "long" and entry <= sl:
        bad = "entry %.6f at/below stop %.6f" % (entry, sl)
    elif side == "long" and entry >= tp:
        bad = "entry %.6f at/above target %.6f" % (entry, tp)
    elif side == "short" and entry >= sl:
        bad = "entry %.6f at/above stop %.6f" % (entry, sl)
    elif side == "short" and entry <= tp:
        bad = "entry %.6f at/below target %.6f" % (entry, tp)
    if bad:
        return {"status": "PRETRIGGERED", "entry": entry, "reason": bad,
                "stop_width_pct": round(stop_width_pct, 2)}
    horizon = t0 + timedelta(hours=float(p["horizon_hours"]))
    exit_px, reason = None, "horizon"
    for b in series:
        ts = parse_ts(b["ts"])
        if ts < t0:
            continue
        if ts > horizon:
            break
        hi, lo = float(b["high"]), float(b["low"])
        if side == "long":
            hit_sl, hit_tp = lo <= sl, hi >= tp
        else:
            hit_sl, hit_tp = hi >= sl, lo <= tp
        if hit_sl and hit_tp:                 # ambiguous bar -> the stop wins
            exit_px, reason = sl, "sl"
            break
        if hit_sl:
            exit_px, reason = sl, "sl"
            break
        if hit_tp:
            exit_px, reason = tp, "tp"
            break
    if exit_px is None:
        exit_px = float(series[-1]["close"])

    risk_px = abs(entry - sl)
    if risk_px <= 0:
        return {"status": "VOID", "reason": "zero distance to stop"}
    gross_r = (exit_px - entry) / risk_px
    if side == "short":
        gross_r = -gross_r
    cost_r = (COST_BP[p["class"]] / 1e4) * entry / risk_px
    net_r = gross_r - cost_r
    direction = 1 if side == "long" else -1
    usd = direction * (exit_px - entry) / entry * float(p["size_usd"])
    return {"status": "OK", "entry": entry, "exit": exit_px, "reason": reason,
            "R": round(net_r, 4), "usd": round(usd, 2),
            "cost_bp": COST_BP[p["class"]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--picks", required=True)
    ap.add_argument("--prices", required=True)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fill-relative", action="store_true",
                    help="re-anchor each bracket onto the fill, preserving the entrant's R geometry "
                         "(removes the void rule and the two exploits it allows)")
    a = ap.parse_args()

    global FILL_RELATIVE
    FILL_RELATIVE = bool(a.fill_relative)
    sub = json.load(open(a.picks, encoding="utf-8"))
    bars = json.load(open(a.prices, encoding="utf-8"))
    errs, total = validate(sub)
    if errs:
        print("INVALID SUBMISSION (%d problem(s)):" % len(errs))
        for e in errs:
            print("  -", e)
        return 1

    rows = []
    for p in sub["picks"]:
        v = value_pick(p, bars)
        rows.append({"symbol": p["symbol"], "class": p["class"], "side": p["side"],
                     "size_usd": float(p["size_usd"]), **v})

    scored = [r for r in rows if r["status"] == "OK" and r.get("R") is not None]
    rs = [r["R"] for r in scored]
    summary = {
        "agent": sub.get("agent"), "round": sub.get("round"),
        "sha256": sha256_of(a.picks), "picks": len(rows),
        "void": sum(1 for r in rows if r["status"] != "OK"),
        "scored_in_R": len(scored),
        "mean_R": round(sum(rs) / len(rs), 4) if rs else None,
        "total_usd": round(sum(r.get("usd", 0.0) for r in rows), 2),
        "notional": total,
        "hits": sum(1 for r in scored if r["R"] > 0),
    }
    if a.json:
        print(json.dumps({"summary": summary, "rows": rows}, indent=2, default=str))
        return 0

    lines = ["# Round verdict — %s %s" % (summary["agent"], summary["round"]), "",
             "submission sha256: `%s`" % summary["sha256"], "",
             "| symbol | class | side | size | entry | exit | via | R | $ |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["status"] != "OK":
            lines.append("| %s | %s | %s | %.0f | — | — | **VOID: %s** | — | — |"
                         % (r["symbol"], r["class"], r["side"], r["size_usd"], r["reason"]))
        else:
            lines.append("| %s | %s | %s | %.0f | %.4f | %.4f | %s | %s | %+.2f |"
                         % (r["symbol"], r["class"], r["side"], r["size_usd"], r["entry"],
                            r["exit"], r["reason"],
                            "—" if r["R"] is None else "%+.4f" % r["R"], r["usd"]))
    lines += ["", "**mean R %.4f** · hits %d/%d · total $ %+.2f · void %d"
              % (summary["mean_R"] if summary["mean_R"] is not None else float("nan"),
                 summary["hits"], summary["scored_in_R"], summary["total_usd"], summary["void"])]
    out = "\n".join(lines)
    print(out)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
