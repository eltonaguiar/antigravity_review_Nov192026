#!/usr/bin/env python3
"""
collect_analyst_history.py - build the firm-level analyst-action dataset that the
pre-registered test in PREREG_ANALYST_UPGRADE_TEST.md requires.

WHY THIS EXISTS
---------------
The prereg needs >=750 clean events per brokerage. Measured on 30 mega-caps, the best
firm produced 234 changes and ZERO firms reached 300, because a firm only generates
~7-8 changes per ticker it covers. So the binding constraint is TICKER BREADTH, not
history length: ~96 tickers are needed to reach 750 events for a high-cadence firm.

This script collects that breadth. It is resumable, rate-limited, and writes one
append-only CSV so a partial run is still useful.

SOURCE
------
Yahoo quoteSummary module `upgradeDowngradeHistory`, behind a cookie + crumb handshake.
No API key, no account, no paid tier. It is UNOFFICIAL and undocumented: it can change
or disappear without notice. If it starts returning empty `result`, suspect the
handshake first, not the data.

FIELDS EMITTED
--------------
  symbol, firm_raw, firm_norm, date, action, from_grade, to_grade,
  target_action, current_target, prior_target

  action is one of: up, down, init, reit, main  (main = reiterated, NOT a change)

USAGE
-----
  # one-off
  python collect_analyst_history.py --symbols AAPL MSFT NVDA --out analyst_actions.csv

  # breadth run from a file (one ticker per line); resumable - safe to re-run
  python collect_analyst_history.py --symbol-file sp500.txt --out analyst_actions.csv

  # per-firm counts vs the prereg floors
  python collect_analyst_history.py --report --out analyst_actions.csv

DESIGN NOTES
------------
- Resumable: symbols already present in the CSV are skipped, so a long run can be
  split across sessions or hosts. Use --force to re-fetch.
- Rate-limited to 0.25s by default. Yahoo will throttle hard if pushed; do not lower
  this without reason.
- firm_norm applies ALIAS below. Alias handling is a CONSENSUS REQUIREMENT from the
  model review (Claude Opus 5.5 and the arena agent raised it independently): without
  it, one research operation is counted as several firms, or a merger silently splices
  two different research desks into one history.
- Merger rule from the prereg: do NOT treat a firm's history as continuous across an
  acquisition. Where a name changed because of a merger, the alias map keeps the era
  suffix so the split is recoverable. Extend ALIAS as you find new spellings; the map
  is intentionally a seeded starting point, not a finished table.
"""

import argparse
import collections
import csv
import http.cookiejar
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CSV_FIELDS = [
    "symbol", "firm_raw", "firm_norm", "date", "action",
    "from_grade", "to_grade", "target_action", "current_target", "prior_target",
]

# --- Seeded alias map -------------------------------------------------------
# Keys are lowercased raw strings as they appear in the feed. Values are the
# normalised entity. Add entries as you encounter them; never invent an entity.
ALIAS = {
    "b of a securities": "BofA Securities",
    "bofa securities": "BofA Securities",
    "bofa": "BofA Securities",
    "bank of america": "BofA Securities",
    "b of a": "BofA Securities",
    "merrill lynch": "BofA Securities (Merrill, pre-2019)",  # era suffix: not spliced
    "rbc capital": "RBC Capital Markets",
    "rbc capital markets": "RBC Capital Markets",
    "rbc": "RBC Capital Markets",
    "jpmorgan": "J.P. Morgan",
    "j.p. morgan": "J.P. Morgan",
    "jp morgan": "J.P. Morgan",
    "goldman sachs": "Goldman Sachs",
    "goldman": "Goldman Sachs",
    "morgan stanley": "Morgan Stanley",
    "bernstein": "Bernstein",
    "alliancebernstein": "Bernstein",
    "sanford c. bernstein": "Bernstein",
    "needham": "Needham & Company",
    "needham & company": "Needham & Company",
    "wedbush": "Wedbush",
    "cantor fitzgerald": "Cantor Fitzgerald",
    "jefferies": "Jefferies",
    "wolfe research": "Wolfe Research",
    "citigroup": "Citi",
    "citi": "Citi",
    "ubs": "UBS",
    "deutsche bank": "Deutsche Bank",
    "barclays": "Barclays",
    "piper sandler": "Piper Sandler",
    "piper jaffray": "Piper Sandler (pre-2020)",  # era suffix
    "oppenheimer": "Oppenheimer",
    "guggenheim": "Guggenheim",
    "jmp securities": "JMP Securities",
    "bmo capital": "BMO Capital Markets",
    "bmo capital markets": "BMO Capital Markets",
    "stifel": "Stifel",
    "raymond james": "Raymond James",
    "truist": "Truist",
    "wells fargo": "Wells Fargo",
}

FLOORS = [300, 500, 750]


def norm_firm(raw):
    if not raw:
        return "unknown"
    return ALIAS.get(raw.strip().lower(), raw.strip())


class Yahoo:
    def __init__(self):
        cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.op.addheaders = [(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/150.0 Safari/537.36",
        )]
        self.crumb = None

    def _get(self, url, timeout=25):
        return self.op.open(url, timeout=timeout).read().decode("utf-8", "replace")

    def handshake(self):
        try:
            self.op.open("https://fc.yahoo.com", timeout=15).read()
        except Exception:
            pass  # expected: it sets the cookie then errors
        self.crumb = self._get("https://query2.finance.yahoo.com/v1/test/getcrumb").strip()
        if not self.crumb:
            raise RuntimeError("crumb handshake returned empty; Yahoo may have changed the flow")
        return self.crumb

    def history(self, symbol):
        if not self.crumb:
            self.handshake()
        url = (
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/%s"
            "?modules=upgradeDowngradeHistory&crumb=%s"
            % (symbol, urllib.parse.quote(self.crumb))
        )
        data = json.loads(self._get(url))
        res = (data.get("quoteSummary") or {}).get("result") or []
        if not res:
            return []
        return ((res[0].get("upgradeDowngradeHistory") or {}).get("history")) or []


def existing_symbols(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["symbol"].upper() for row in csv.DictReader(fh) if row.get("symbol")}


def collect(symbols, out, sleep_s=0.25, force=False):
    done = set() if force else existing_symbols(out)
    todo = [s for s in symbols if s.upper() not in done]
    if done:
        print(f"  resuming: {len(done)} symbols already in {out}, {len(todo)} to fetch")

    y = Yahoo()
    y.handshake()
    new_file = not os.path.exists(out) or force
    written = 0
    errors = []

    with open(out, "a" if not force else "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if new_file:
            w.writeheader()
        for i, sym in enumerate(todo, 1):
            sym = sym.strip().upper()
            if not sym:
                continue
            try:
                hist = y.history(sym)
            except Exception as exc:
                errors.append((sym, type(exc).__name__))
                print(f"  [{i}/{len(todo)}] {sym}: ERROR {type(exc).__name__}")
                time.sleep(sleep_s)
                continue
            for r in hist:
                w.writerow({
                    "symbol": sym,
                    "firm_raw": (r.get("firm") or "").strip(),
                    "firm_norm": norm_firm(r.get("firm")),
                    "date": r.get("epochGradeDate") or "",
                    "action": r.get("action") or "",
                    "from_grade": r.get("fromGrade") or "",
                    "to_grade": r.get("toGrade") or "",
                    "target_action": r.get("priceTargetAction") or "",
                    "current_target": r.get("currentPriceTarget") or "",
                    "prior_target": r.get("priorPriceTarget") or "",
                })
                written += 1
            fh.flush()
            print(f"  [{i}/{len(todo)}] {sym}: {len(hist)} rows")
            time.sleep(sleep_s)

    print(f"\n  wrote {written} rows to {out}")
    if errors:
        print(f"  {len(errors)} symbols errored: {errors[:10]}")


def report(path):
    if not os.path.exists(path):
        sys.exit(f"  no such file: {path}")
    all_c = collections.Counter()
    chg_c = collections.Counter()
    per_sym = collections.defaultdict(set)
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            f = row.get("firm_norm") or "unknown"
            all_c[f] += 1
            if row.get("action") in ("up", "down", "init", "reit"):
                chg_c[f] += 1
            per_sym[f].add(row.get("symbol"))

    n_sym = len(set().union(*per_sym.values())) if per_sym else 0
    print(f"\n  {sum(all_c.values())} rows | {len(all_c)} firms | {n_sym} tickers")
    print(f"  {'firm':<30}{'all':>7}{'changes':>9}{'tickers':>9}{'chg/tkr':>9}   floors")
    for f, c in chg_c.most_common(20):
        t = len(per_sym[f]) or 1
        hits = [str(x) for x in FLOORS if c >= x]
        print(f"  {f[:29]:<30}{all_c[f]:>7}{c:>9}{t:>9}{c/t:>9.1f}   "
              f"{'hits ' + '/'.join(hits) if hits else 'below 300'}")
    print(f"\n  firms reaching each floor: "
          + "  ".join(f"{x}={sum(1 for c in chg_c.values() if c >= x)}" for x in FLOORS))
    print("  NOTE: floors are per broker over its FULL universe. If nothing reaches 300,")
    print("        the fix is more tickers, not a longer history - see PREREG section 0.")


def main():
    ap = argparse.ArgumentParser(description="Collect firm-level analyst rating actions.")
    ap.add_argument("--symbols", nargs="*", default=[], help="tickers to fetch")
    ap.add_argument("--symbol-file", help="file with one ticker per line")
    ap.add_argument("--out", default="analyst_actions.csv", help="append-only CSV")
    ap.add_argument("--sleep", type=float, default=0.25, help="seconds between requests")
    ap.add_argument("--force", action="store_true", help="re-fetch symbols already in CSV")
    ap.add_argument("--report", action="store_true", help="print per-firm counts and exit")
    args = ap.parse_args()

    if args.report:
        report(args.out)
        return

    syms = list(args.symbols)
    if args.symbol_file:
        with open(args.symbol_file, encoding="utf-8") as fh:
            syms += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if not syms:
        sys.exit("  nothing to do: pass --symbols or --symbol-file (or --report)")

    collect(syms, args.out, sleep_s=args.sleep, force=args.force)
    report(args.out)


if __name__ == "__main__":
    main()
