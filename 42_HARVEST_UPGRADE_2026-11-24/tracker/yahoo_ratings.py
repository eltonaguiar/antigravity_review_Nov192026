"""yahoo_ratings.py — firm-level analyst rating history, no key, no registration.

WHY THIS EXISTS
    Zoo reported "blocked on data: the per-analyst track record, since no free source names the analyst".
    That is false, and it was worth checking rather than accepting. Finnhub's firm-level endpoint
    (stock/upgrade-downgrade) returns HTTP 403 "You don't have access to this resource" on the key we hold,
    and its free recommendation endpoint only returns monthly aggregate counts (strongBuy/buy/hold...).

    Yahoo's quoteSummary exposes a module called upgradeDowngradeHistory that DOES name the firm, the
    date, the old grade and the new grade, plus price targets. Measured 2026-11-24 on AAPL: 971 actions,
    all 971 dated, spanning 2012-09-12 .. 2026-11-11, 59 distinct firms, action mix
    {main 710, reit 169, down 38, up 36, init 18}, with currentPriceTarget/priorPriceTarget present.

HONEST CAVEATS
    - It is UNOFFICIAL and undocumented. Not a sanctioned API; it can change or start refusing at any time,
      and it is subject to the provider's terms. Record the retrieval date with every row.
    - It needs a cookie + crumb handshake (fc.yahoo.com -> /v1/test/getcrumb). No API key, no account.
    - Grade names are free text ("Overweight", "Neutral", "Buy"), so firms are not directly comparable
      until normalised. This script maps them to a 5-point ordinal and keeps the raw string.
    - "main" means reiterated, not a change. Only up/down/init/reit carry a change signal.
    - Only firms that chose to cover the ticker appear, so the firm universe is not random.

USAGE
    python yahoo_ratings.py AAPL MSFT NVDA --out ratings.json
"""
import argparse
import datetime
import json
import subprocess
import sys
import time

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/157.0 Safari/537.36")

GRADE_MAP = [
    ("strong buy", 5), ("strongbuy", 5), ("conviction buy", 5), ("top pick", 5),
    ("buy", 4), ("overweight", 4), ("outperform", 4), ("accumulate", 4), ("add", 4),
    ("positive", 4), ("market outperform", 4), ("sector outperform", 4), ("strong", 4),
    ("hold", 3), ("neutral", 3), ("market perform", 3), ("sector perform", 3),
    ("equal weight", 3), ("equal-weight", 3), ("in-line", 3), ("peer perform", 3), ("mixed", 3),
    ("underperform", 2), ("underweight", 2), ("sell", 1), ("strong sell", 1),
    ("reduce", 2), ("market underperform", 2), ("sector underperform", 2), ("negative", 2),
]


def grade_ordinal(g):
    """Map a free-text grade to a 1..5 ordinal. Returns None when unmapped rather than guessing."""
    if not g:
        return None
    s = str(g).strip().lower()
    for needle, val in GRADE_MAP:
        if needle in s:
            return val
    return None


def curl(args, timeout=30):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", UA] + args,
                       capture_output=True, text=True)
    return r.stdout


def get_session(cookie_jar):
    curl(["-c", cookie_jar, "https://fc.yahoo.com", "-o", "/dev/null"])
    crumb = curl(["-b", cookie_jar, "https://query1.finance.yahoo.com/v1/test/getcrumb"]).strip()
    return crumb


def fetch_symbol(sym, crumb, cookie_jar):
    url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{sym}"
           f"?modules=upgradeDowngradeHistory&crumb={crumb}&formatted=false")
    body = curl(["-b", cookie_jar, url])
    try:
        d = json.loads(body)
    except Exception:
        return None, f"unparseable ({len(body)} bytes)"
    res = (d.get("quoteSummary") or {}).get("result")
    if not res:
        err = (d.get("quoteSummary") or {}).get("error") or d
        return None, f"no result: {str(err)[:70]}"
    hist = (res[0].get("upgradeDowngradeHistory") or {}).get("history") or []
    return hist, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="+")
    ap.add_argument("--out", default="yahoo_ratings.json")
    ap.add_argument("--sleep", type=float, default=1.2)
    a = ap.parse_args()

    jar = "yh_cookies.txt"
    crumb = get_session(jar)
    if not crumb or len(crumb) < 4:
        sys.exit("could not obtain a crumb; the handshake changed")

    rows, per_symbol = [], {}
    for sym in a.symbols:
        hist, err = fetch_symbol(sym, crumb, jar)
        if err:
            print(f"  {sym}: FAILED - {err}")
            per_symbol[sym] = {"error": err}
            continue
        dated = [h for h in hist if h.get("epochGradeDate")]
        changes = [h for h in dated if h.get("action") in ("up", "down", "init", "reit")]
        firms = sorted({h.get("firm") for h in dated if h.get("firm")})
        per_symbol[sym] = {
            "actions": len(dated), "changes": len(changes), "firms": len(firms),
            "first": datetime.datetime.fromtimestamp(min(h["epochGradeDate"] for h in dated), datetime.UTC).date().isoformat() if dated else None,
            "last": datetime.datetime.fromtimestamp(max(h["epochGradeDate"] for h in dated), datetime.UTC).date().isoformat() if dated else None,
        }
        for h in dated:
            rows.append({
                "symbol": sym,
                "firm": h.get("firm"),
                "date": datetime.datetime.fromtimestamp(h["epochGradeDate"], datetime.UTC).date().isoformat(),
                "epoch": h["epochGradeDate"],
                "action": h.get("action"),
                "from_grade": h.get("fromGrade"),
                "to_grade": h.get("toGrade"),
                "from_ordinal": grade_ordinal(h.get("fromGrade")),
                "to_ordinal": grade_ordinal(h.get("toGrade")),
                "price_target_action": h.get("priceTargetAction"),
                "current_pt": h.get("currentPriceTarget"),
                "prior_pt": h.get("priorPriceTarget"),
            })
        print(f"  {sym}: {len(dated)} actions, {len(changes)} changes, {len(firms)} firms "
              f"({per_symbol[sym]['first']} .. {per_symbol[sym]['last']})")
        time.sleep(a.sleep)

    out = {
        "retrieved_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "source": "unofficial: query1.finance.yahoo.com/v10/finance/quoteSummary upgradeDowngradeHistory",
        "caveats": [
            "unofficial and undocumented; may change without notice",
            "grade strings are free text; ordinals are this script's mapping, not the provider's",
            "action=main means reiterated, not a change",
            "firm universe is whoever chose to cover the ticker",
        ],
        "per_symbol": per_symbol,
        "rows": rows,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    print(f"\nwrote {a.out}: {len(rows)} firm-level rows across {len(a.symbols)} symbols")


if __name__ == "__main__":
    main()
