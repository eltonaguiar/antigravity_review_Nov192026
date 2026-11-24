#!/usr/bin/env python3
"""LOOK-THROUGH CONSENSUS for funds.

Sell-side analysts rate companies, not funds, so a fund shows zero "analyst coverage".
This computes fund-level values as HOLDINGS-WEIGHTED aggregates of the equity consensus
we already have:

    fund_share_buy  = sum(w_i * share_buy_i) / sum(w_i)        over COVERED holdings
    coverage_pct    = sum(w_i)                / sum(w_j)        covered / all holdings

Everything produced here is DERIVED. It is not a published fund rating and must never be
presented as one. The coverage share is part of the number: a look-through built from 25%
of a fund's weight is a statement about that 25%, not about the fund.

Sources, all free and credential-free (verified 2026-11-24, see SOURCES section in output):
  SPY, XLK, JNK  - SSGA daily holdings .xlsx   (parsed with stdlib zipfile + ElementTree)
  QQQ, VTI       - SEC EDGAR N-PORT primary_doc.xml
  EEM            - BLOCKED, see blocked[]
  iShares CSV   - returns an HTML interstitial, not CSV; recorded as blocked, not worked around

Inputs
  --feed   path to harvest_signals.json   (default docs/data/harvest_signals.json)
  --outdir directory for outputs          (default out/)

Nothing is written outside --outdir.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

UA = "harvest-lookthrough/1.0 (research; contact ejaguiar1@gmail.com)"
NS_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

SSGA = "https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us"
FUNDS = [
    # ticker, label, source, locator
    ("SPY", "SPDR S&P 500 ETF Trust",            "ssga_xlsx", f"{SSGA}/holdings-daily-us-en-spy.xlsx"),
    ("XLK", "Technology Select Sector SPDR",     "ssga_xlsx", f"{SSGA}/holdings-daily-us-en-xlk.xlsx"),
    ("JNK", "SPDR Bloomberg High Yield Bond ETF","ssga_xlsx", f"{SSGA}/holdings-daily-us-en-jnk.xlsx"),
    ("QQQ", "Invesco QQQ Trust",                 "nport",     "CIK0001067839"),
    ("VTI", "Vanguard Total Stock Market ETF",   "nport",     "CIK0000036405"),
    ("EEM", "iShares MSCI Emerging Markets ETF", "blocked",   ""),
]


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- xlsx (stdlib)
def xlsx_rows(path: Path) -> list[list[str]]:
    """Read the first worksheet of an xlsx with no third-party dependency."""
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{NS_MAIN}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{NS_MAIN}t")))
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        out: list[list[str]] = []
        for row in sheet.iter(f"{NS_MAIN}row"):
            cells: list[str] = []
            for c in row.findall(f"{NS_MAIN}c"):
                v = c.find(f"{NS_MAIN}v")
                val = "" if v is None else (v.text or "")
                if c.get("t") == "s" and val:
                    val = shared[int(val)]
                cells.append(val)
            out.append(cells)
        return out


def parse_ssga(path: Path) -> tuple[list[dict], str]:
    """Find the header row by content, not by a hardcoded offset."""
    rows = xlsx_rows(path)
    hdr = None
    for i, r in enumerate(rows[:40]):
        low = [str(c).strip().lower() for c in r]
        if ("ticker" in low or "identifier" in low) and "weight" in low:
            hdr = i
            break
    if hdr is None:
        raise ValueError("could not locate a header row containing 'Ticker' and 'Weight'")
    cols = {str(c).strip().lower(): j for j, c in enumerate(rows[hdr])}
    ti = cols.get("ticker", cols.get("identifier"))
    wi = cols["weight"]
    ni = cols.get("name")
    ci = cols.get("identifier")
    holdings = []
    for r in rows[hdr + 1:]:
        if len(r) <= max(ti, wi):
            continue
        tk = str(r[ti]).strip()
        wraw = str(r[wi]).strip().replace("%", "").replace(",", "")
        if not tk or not wraw:
            continue
        try:
            w = float(wraw)
        except ValueError:
            continue
        if w <= 0:
            continue
        holdings.append({"ticker": tk.upper(), "weight": w,
                         "cusip": str(r[ci]).strip() if ci is not None and len(r) > ci else "",
                         "name": str(r[ni]).strip() if ni is not None and len(r) > ni else ""})
    return holdings, f"xlsx header at row {hdr}"


# ---------------------------------------------------------------- N-PORT
def latest_nport_doc(cik: str) -> tuple[str, str]:
    """Return (accession, url) of the most recent NPORT-P primary document."""
    d = json.loads(fetch(f"https://data.sec.gov/submissions/{cik}.json"))
    r = d["filings"]["recent"]
    for i, form in enumerate(r["form"]):
        if form == "NPORT-P":
            acc = r["accessionNumber"][i]
            return acc, f"https://www.sec.gov/Archives/edgar/data/{int(d['cik'])}/{acc.replace('-','')}/primary_doc.xml"
    raise ValueError(f"no NPORT-P filing found for {cik}")


def parse_nport(url: str) -> tuple[list[dict], str]:
    xml = fetch(url)
    root = ET.fromstring(xml)

    def local(tag: str) -> str:
        return tag.split("}")[-1]

    holdings = []
    for el in root.iter():
        if local(el.tag) != "invstOrSec":
            continue
        pct = name = tick = cusip = None
        for ch in el.iter():
            lt = local(ch.tag)
            if lt == "pctVal" and pct is None:
                pct = ch.text
            elif lt == "name" and name is None:
                name = ch.text
            elif lt == "ticker" and tick is None:
                tick = ch.get("value")
            elif lt == "cusip" and cusip is None:
                cusip = (ch.text or "").strip()
        if pct is None:
            continue
        try:
            w = float(pct)
        except ValueError:
            continue
        if w <= 0:
            continue
        holdings.append({"ticker": (tick or "").upper(), "weight": w, "cusip": cusip or "",
                         "name": (name or "").strip()})
    return holdings, f"nport {len(holdings)} positions"


# ---------------------------------------------------------------- aggregation
def lookthrough(ticker: str, label: str, holdings: list[dict], cons: dict, how: str) -> dict:
    total_w = sum(h["weight"] for h in holdings)
    covered_w = 0.0
    acc = 0.0
    matched, unmatched_top = 0, []
    for h in holdings:
        sb = cons.get(h["ticker"])
        if sb is None:
            if len(unmatched_top) < 5:
                unmatched_top.append(h["ticker"] or h["name"][:16])
            continue
        covered_w += h["weight"]
        acc += h["weight"] * sb
        matched += 1
    cov = (covered_w / total_w) if total_w else 0.0
    derived = (acc / covered_w) if covered_w else None
    return {
        "ticker": ticker, "label": label, "derivation": "DERIVED_NOT_PUBLISHED",
        "source_how": how, "positions": len(holdings), "positions_matched": matched,
        "total_weight": round(total_w, 4),
        "covered_weight": round(covered_w, 4),
        "coverage_pct": round(100 * cov, 2),
        "fund_share_buy_pct": round(derived, 2) if derived is not None else None,
        "unmatched_top": unmatched_top,
        "note": ("Holdings-weighted mean of Share Buy/Strong Buy across COVERED holdings only. "
                 "Valid for the coverage share stated; not a statement about the whole fund."),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", default="docs/data/harvest_signals.json")
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parent / "out"))
    ap.add_argument("--cache", default="/tmp/lookthrough_cache")
    a = ap.parse_args()

    feed = json.loads(Path(a.feed).read_text())
    cons = {s["symbol"].upper(): s.get("buy_side_pct") for s in feed["signals"]
            if s.get("buy_side_pct") is not None}
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    cache = Path(a.cache); cache.mkdir(parents=True, exist_ok=True)

    results, blocked, sources = [], [], []
    crosswalk: dict[str, str] = {}   # CUSIP -> ticker, built from the SSGA files
    for ticker, label, kind, loc in FUNDS:
        try:
            if kind == "ssga_xlsx":
                p = cache / f"{ticker}.xlsx"
                p.write_bytes(fetch(loc))
                holdings, how = parse_ssga(p)
                sources.append({"ticker": ticker, "source": "SSGA daily holdings xlsx",
                                "url": loc, "status": "OK", "parsed": how})
                # N-PORT identifies positions by CUSIP, not ticker. Use the SSGA files
                # (which carry both) to build a free crosswalk instead of guessing.
                for hh in holdings:
                    if hh.get("ticker") and hh.get("cusip"):
                        crosswalk[hh["cusip"]] = hh["ticker"]
            elif kind == "nport":
                acc, url = latest_nport_doc(loc)
                holdings, how = parse_nport(url)
                # translate CUSIP -> ticker wherever N-PORT omitted a ticker
                translated = 0
                for hh in holdings:
                    if not hh.get("ticker") and hh.get("cusip") in crosswalk:
                        hh["ticker"] = crosswalk[hh["cusip"]]
                        translated += 1
                how = f"{how}; cusip->ticker translated {translated}"
                sources.append({"ticker": ticker, "source": "SEC EDGAR N-PORT",
                                "url": url, "accession": acc, "status": "OK", "parsed": how})
            else:
                blocked.append({"ticker": ticker,
                                "reason": "iShares daily CSV returned text/csv content-type but an HTML "
                                          "page body (interstitial); Invesco download endpoint returned "
                                          "HTTP 406. No credential-free holdings source verified.",
                                "attempted": [
                                    "https://www.ishares.com/us/products/239637/.../EEM_holdings (HTTP 200, text/csv, body=HTML)",
                                    "https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?... (HTTP 406, 0 bytes)",
                                    "https://data.sec.gov/submissions/CIK0000872664.json (non-JSON)",
                                ]})
                continue
            res = lookthrough(ticker, label, holdings, cons, how)
            # A zero-coverage N-PORT result is almost certainly the WRONG SERIES, not a fund with
            # no large caps: Vanguard/Invesco file one NPORT-P per series under one CIK, and the
            # newest filing for a CIK may belong to a sibling fund. Say so instead of printing 0%.
            if kind == "nport" and res["coverage_pct"] == 0.0:
                res["status"] = "BLOCKED_WRONG_SERIES"
                res["reason"] = ("Parsed document appears to describe a different fund series: "
                                 f"{res['positions']} positions, 0 of them in the {len(cons)}-symbol "
                                 "consensus universe, and the position names are not this fund's "
                                 "known constituents. Released as a zero-coverage figure would be "
                                 "wrong; it is withheld instead.")
            elif res["coverage_pct"] == 0.0:
                # Holdings parsed cleanly but none are equities we have ratings for. For a bond
                # fund that is the correct answer, not a failure - say which.
                res["status"] = "NOT_APPLICABLE_BOND_FUND"
                res["reason"] = ("This fund holds no equities, so an equity-analyst look-through is "
                                 "undefined for it by construction. The 0% is the right answer, not a "
                                 "data failure. Bond funds need credit ratings and yield data instead.")
            else:
                res["status"] = "DERIVED_OK"
            results.append(res)
        except Exception as e:
            blocked.append({"ticker": ticker, "reason": f"{type(e).__name__}: {e}", "attempted": [loc]})

    payload = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "consensus_feed": a.feed,
        "consensus_symbols": len(cons),
        "method": ("fund_share_buy = sum(w_i * share_buy_i) / sum(w_i) over covered holdings; "
                   "coverage_pct = sum(w_i covered) / sum(w_j all). DERIVED, never a published rating."),
        "sources": sources, "blocked": blocked, "funds": results,
        "crosswalk_cusip_to_ticker": len(crosswalk),
    }
    (outdir / "lookthrough_consensus.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(f"  consensus symbols available: {len(cons)}")
    print(f"  funds computed: {len(results)}   blocked: {len(blocked)}")
    for f in results:
        print(f"    {f['ticker']:<4} positions={f['positions']:<4} matched={f['positions_matched']:<4} "
              f"coverage={f['coverage_pct']:>5}%  derived share-buy="
              f"{f['fund_share_buy_pct'] if f['fund_share_buy_pct'] is not None else 'n/a'}")
    for b in blocked:
        print(f"    BLOCKED {b['ticker']}: {b['reason'][:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
