#!/usr/bin/env python3
"""
collect_form4.py - SEC Form 4 insider-transaction collector.

Spec: 12_INSIDER_EDGE_PROBE_2026-11-24.md (event definition and gates are frozen there).

Two operational facts, both learned the hard way and both load-bearing:
  1. data.sec.gov returns 403 without a User-Agent. Send one.
  2. The submissions JSON `primaryDocument` carries an `xslF345X06/` prefix and that path serves
     RENDERED HTML, not XML. Use os.path.basename() to get raw form4.xml.

Usage:
    python collect_form4.py --tickers AAPL,MSFT,NVDA --out form4_events.csv
    python collect_form4.py --tickers-file tickers.txt --max-filings 200

SEC fair-access: about 10 requests/second. We default to 8 with retries.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date

UA = {"User-Agent": "Hermes-Research research@example.com"}
TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}"
RATE = 8.0          # requests per second
_last = [0.0]


def _get(url, timeout=30, tries=3):
    """Rate-limited GET with retries. Returns bytes or None."""
    for attempt in range(tries):
        gap = 1.0 / RATE - (time.time() - _last[0])
        if gap > 0:
            time.sleep(gap)
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=timeout).read()
            _last[0] = time.time()
            return data
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            if e.code in (403, 429) or e.code >= 500:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None
        except Exception:
            _last[0] = time.time()
            time.sleep(1.0 * (attempt + 1))
    return None


def ticker_to_cik():
    raw = _get(TICKER_MAP_URL)
    if not raw:
        sys.exit("FATAL: could not fetch company_tickers.json (SEC rate limit or network)")
    d = json.loads(raw)
    return {v["ticker"].upper(): int(v["cik_str"]) for v in d.values()}


def _tag(xml, tag, many=False):
    hits = re.findall(rf"<{tag}>(.*?)</{tag}>", xml, re.S)
    out = [re.sub(r"<[^>]+>", "", h).strip() for h in hits]
    return out if many else (out[0] if out else "")


def _value_after(xml, parent):
    """Pull <value> inside a named parent block (transactionShares / transactionPricePerShare)."""
    m = re.search(rf"<{parent}>\s*<value>(.*?)</value>", xml, re.S)
    return m.group(1).strip() if m else ""


def _blocks(xml, tag):
    return re.findall(rf"<{tag}>(.*?)</{tag}>", xml, re.S)


def _truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y")


def _owner(block):
    return {
        "reporting_owner_id": _tag(block, "rptOwnerCik") or _tag(block, "rptOwnerName"),
        "owner": _tag(block, "rptOwnerName"),
        "officer_title": _tag(block, "officerTitle"),
        "is_officer": _tag(block, "isOfficer") or "false",
        "is_director": _tag(block, "isDirector") or "false",
        "is_ten_percent_owner": _tag(block, "isTenPercentOwner") or "false",
    }


def parse_form4(xml):
    """One row per reporting owner per non-derivative transaction.

    A Form 4 can list several reportingOwner blocks (e.g. an entity plus an
    individual officer). The old parser took the first owner's flags for every
    transaction, losing the officer and counting the entity as an insider.
    """
    if "<ownershipDocument" not in xml:
        return []
    issuer = _tag(xml, "issuerName")
    owners = [_owner(b) for b in _blocks(xml, "reportingOwner")]
    if not owners:
        owners = [{"reporting_owner_id": "", "owner": "", "officer_title": "",
                   "is_officer": "false", "is_director": "false",
                   "is_ten_percent_owner": "false"}]
    blocks = _blocks(xml, "nonDerivativeTransaction") or [xml]
    rows = []
    for b in blocks:
        code = _tag(b, "transactionCode")
        if not code:
            continue
        tx = {
            "transaction_date": _tag(b, "transactionDate"),
            "code": code,
            "shares": _value_after(b, "transactionShares"),
            "price": _value_after(b, "transactionPricePerShare"),
        }
        for o in owners:
            rows.append(dict({"issuer": issuer}, **o, **tx))
    return rows


def collect(tickers, max_filings=None, max_lookback=None):
    tmap = ticker_to_cik()
    rows, missing = [], []
    for tk in tickers:
        cik = tmap.get(tk.upper())
        if not cik:
            missing.append(tk)
            continue
        raw = _get(SUBMISSIONS.format(cik=cik))
        if not raw:
            missing.append(tk + "(submissions)")
            continue
        sub = json.loads(raw)
        rec = sub.get("filings", {}).get("recent", {})
        forms = rec.get("form", [])
        idx = [i for i, f in enumerate(forms) if f == "4"]
        if max_lookback:
            dates = rec.get("filingDate", [])
            idx = [i for i in idx if i < len(dates) and dates[i] >= max_lookback]
        if max_filings:
            idx = idx[:max_filings]
        for i in idx:
            acc = rec["accessionNumber"][i].replace("-", "")
            doc = os.path.basename(rec["primaryDocument"][i])   # strip xslF345X06/
            fdate = rec.get("filingDate", [""] * (i + 1))[i]
            xml = _get(ARCHIVE.format(cik=cik, acc=acc, doc=doc))
            if not xml:
                continue
            text = xml.decode("utf-8", "replace")
            for r in parse_form4(text):
                r.update(symbol=tk.upper(), cik=cik, filing_date=fdate)
                rows.append(r)
        print(f"  {tk.upper():<6} cik={cik:<10} form4_filings={len(idx):<5} rows_so_far={len(rows)}",
              flush=True)
    return rows, missing


def business_days(later, earlier):
    """Business-day difference; approximate, good enough to catch a look-ahead bug."""
    from datetime import datetime, timedelta
    try:
        a = datetime.strptime(later, "%Y-%m-%d").date()
        b = datetime.strptime(earlier, "%Y-%m-%d").date()
    except Exception:
        return None
    if a < b:
        return None
    n, d = 0, b
    while d < a:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default="")
    ap.add_argument("--tickers-file", default="")
    ap.add_argument("--max-filings", type=int, default=None,
                    help="cap Form 4 filings per ticker (most recent first)")
    ap.add_argument("--since", default=None, help="filingDate lower bound YYYY-MM-DD")
    ap.add_argument("--out", default="form4_events.csv")
    ap.add_argument("--summary", default="form4_summary.md")
    a = ap.parse_args()

    tickers = [t.strip() for t in a.tickers.split(",") if t.strip()]
    if a.tickers_file:
        tickers += [l.strip() for l in open(a.tickers_file) if l.strip()]
    if not tickers:
        sys.exit("no tickers supplied")

    print(f"collecting Form 4 for {len(tickers)} tickers ...")
    rows, missing = collect(tickers, a.max_filings, a.since)

    cols = ["symbol", "cik", "filing_date", "transaction_date", "reporting_owner_id",
            "owner", "officer_title", "is_officer", "is_director", "is_ten_percent_owner",
            "code", "shares", "price"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # summary
    from collections import Counter
    codes = Counter(r["code"] for r in rows)
    issuers = len({r["symbol"] for r in rows})
    lags = [business_days(r["filing_date"], r["transaction_date"]) for r in rows]
    lags = sorted(x for x in lags if x is not None)
    med = lags[len(lags) // 2] if lags else None
    p95 = lags[int(len(lags) * 0.95)] if lags else None

    with open(a.summary, "w", encoding="utf-8") as f:
        f.write("# Form 4 collection summary\n\n")
        f.write(f"- generated: {date.today().isoformat()}\n")
        f.write(f"- tickers requested: {len(tickers)}  (unresolved: {len(missing)})\n")
        f.write(f"- distinct issuers with events: {issuers}\n")
        f.write(f"- total transaction rows: {len(rows)}\n\n")
        f.write("## Rows by transaction code\n\n")
        meaning = {"P": "open-market purchase (the EVENT)",
                   "S": "open-market sale (the CONTROL)",
                   "A": "grant/award", "M": "option exercise", "F": "tax withholding",
                   "C": "conversion", "G": "gift", "D": "disposition", "J": "other"}
        for c, n in codes.most_common():
            f.write(f"| {c} | {n} | {meaning.get(c, '')} |\n")
        f.write("\n## Filing lag (business days, filing_date - transaction_date)\n\n")
        f.write(f"- median: {med}\n- p95: {p95}\n- n with valid lag: {len(lags)}\n\n")
        f.write("A p95 above ~2 business days means the pipeline is reading a later date than the "
                "legal filing deadline, which is a look-ahead risk. Form 4 is due within 2 business days.\n\n")
        f.write("## Event counts for the probe\n\n")
        p_rows = [r for r in rows if r["code"] == "P"]
        p_insiders = [r for r in p_rows if _truthy(r.get("is_officer")) or _truthy(r.get("is_director"))]
        f.write(f"- code P (purchases): {codes.get('P', 0)}\n")
        f.write(f"- code P after officer-or-director filter: {len(p_insiders)}\n")
        f.write(f"- code S (sales, control): {codes.get('S', 0)}\n")
        if missing:
            f.write(f"\n## Unresolved tickers\n\n{', '.join(missing[:40])}\n")

    print(f"\nwrote {a.out} ({len(rows)} rows) and {a.summary}")
    print("codes:", dict(codes.most_common()))
    print(f"filing lag: median={med} p95={p95}")


if __name__ == "__main__":
    main()
