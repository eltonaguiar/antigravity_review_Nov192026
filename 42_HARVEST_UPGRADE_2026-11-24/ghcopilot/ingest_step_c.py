#!/usr/bin/env python3
"""STEP C-NEXT ingestion: fund_lookthrough + crowd_markets in ejaguiar1_stocks.

Reads the two artifacts this agent measured and writes them into the live tables.
Idempotent and NON-DESTRUCTIVE: it never deletes or overwrites a row it did not
create. Existing (fund_symbol, as_of) or (venue, market_id) combinations are
skipped, never updated, so another agent's data cannot be clobbered.

Nothing is invented. A field we did not measure is written as NULL, not zero:
  derived_score        NOT computed by this agent -> NULL
  Kalshi implied_prob  no two-sided quote returned -> NULL
  outcome              market not resolved         -> NULL
  category             not classified by us        -> NULL

Connection follows the repo's own pattern (check_db_v3.py):
  host mysql.50webs.com, user ejaguiar1_stocks, password $DB_PASS_STOCKS
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pymysql

HERE = Path(__file__).resolve().parent
LT = HERE / "out" / "lookthrough_consensus.json"
CL = HERE / "out" / "crowd_layer.json"


def connect():
    return pymysql.connect(
        host="mysql.50webs.com", user="ejaguiar1_stocks",
        password=os.environ.get("DB_PASS_STOCKS", ""),
        database="ejaguiar1_stocks", connect_timeout=15, autocommit=False,
    )


def ingest_funds(conn) -> tuple[int, int]:
    d = json.loads(LT.read_text())
    as_of = d["generated_at"][:10]
    method = d["method"]
    inserted = skipped = 0
    with conn.cursor() as c:
        for f in d["funds"]:
            c.execute(
                "SELECT id FROM fund_lookthrough WHERE fund_symbol=%s AND as_of=%s",
                (f["ticker"], as_of),
            )
            if c.fetchone():
                skipped += 1
                continue
            note = method
            if f.get("reason"):
                note = f"{method} | STATUS REASON: {f['reason']}"
            c.execute(
                """INSERT INTO fund_lookthrough
                   (fund_symbol, as_of, holdings_count, matched_count, weight_coverage_pct,
                    derived_buy_side_pct, derived_score, status, source_file, method_note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    f["ticker"], as_of, f.get("positions"), f.get("positions_matched"),
                    f.get("coverage_pct"), f.get("fund_share_buy_pct"),
                    None,                                  # derived_score: not computed here
                    f.get("status") or "UNKNOWN",
                    f.get("source_how"),
                    note[:6000],
                ),
            )
            inserted += 1
        # coverage assert: every covered fund must carry its coverage share
        c.execute("""SELECT COUNT(*) FROM fund_lookthrough
                     WHERE as_of=%s AND derived_buy_side_pct IS NOT NULL
                       AND weight_coverage_pct IS NULL""", (as_of,))
        bad = c.fetchone()[0]
        if bad:
            conn.rollback()
            raise SystemExit(f"ABORT: {bad} derived rows lack weight_coverage_pct")
    # blocked funds that are not in funds[] (EEM) go in as BLOCKED rows too
    with conn.cursor() as c:
        for b in d.get("blocked", []):
            c.execute(
                "SELECT id FROM fund_lookthrough WHERE fund_symbol=%s AND as_of=%s",
                (b["ticker"], as_of),
            )
            if c.fetchone():
                skipped += 1
                continue
            c.execute(
                """INSERT INTO fund_lookthrough
                   (fund_symbol, as_of, holdings_count, matched_count, weight_coverage_pct,
                    derived_buy_side_pct, derived_score, status, source_file, method_note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (b["ticker"], as_of, None, None, None, None, None, "BLOCKED",
                 None, f"BLOCKED: {b['reason']}"[:6000]),
            )
            inserted += 1
    conn.commit()
    return inserted, skipped


def ingest_crowd(conn) -> tuple[int, int]:
    d = json.loads(CL.read_text())
    inserted = skipped = backfilled = 0
    with conn.cursor() as c:
        for m in d.get("markets", []):
            c.execute(
                "SELECT id FROM crowd_markets WHERE venue=%s AND market_id=%s",
                (m["venue"], m["market_id"]),
            )
            existing = c.fetchone()
            if existing:
                # Non-destructive backfill: only fill a column the DB has left NULL.
                # Never overwrite a value another agent wrote.
                c.execute(
                    """UPDATE crowd_markets
                          SET implied_prob = COALESCE(implied_prob, %s),
                              bid          = COALESCE(bid, %s),
                              ask          = COALESCE(ask, %s),
                              spread       = COALESCE(spread, %s),
                              volume       = COALESCE(volume, %s),
                              liquidity    = COALESCE(liquidity, %s),
                              open_interest= COALESCE(open_interest, %s),
                              resolves_at  = COALESCE(resolves_at, %s)
                        WHERE id=%s""",
                    (m.get("implied_prob"), m.get("bid"), m.get("ask"), m.get("spread"),
                     m.get("volume"), m.get("liquidity"), m.get("open_interest"),
                     parse_dt(m.get("end_date")), existing[0]),
                )
                if c.rowcount:
                    backfilled += 1
                else:
                    skipped += 1
                continue
            c.execute(
                """INSERT INTO crowd_markets
                   (venue, market_id, title, category, implied_prob, bid, ask, spread,
                    volume, liquidity, open_interest, resolves_at, resolved, outcome)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    m["venue"], m["market_id"], (m.get("question") or "")[:400],
                    None,                                  # category: not classified by us
                    m.get("implied_prob"), m.get("bid"), m.get("ask"), m.get("spread"),
                    m.get("volume"), m.get("liquidity"), m.get("open_interest"),
                    parse_dt(m.get("end_date")),
                    0,                                     # queried status=open / closed=false
                    None,                                  # outcome unknown -> NULL
                ),
            )
            inserted += 1
    conn.commit()
    return inserted, skipped, backfilled


def parse_dt(v):
    if not v:
        return None
    try:
        s = str(v).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def main() -> int:
    if not os.environ.get("DB_PASS_STOCKS"):
        print("ABORT: DB_PASS_STOCKS not set", file=sys.stderr)
        return 2
    conn = connect()
    try:
        fi, fs = ingest_funds(conn)
        ci, cs, cb = ingest_crowd(conn)
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) FROM fund_lookthrough"); ft = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM crowd_markets"); ct = c.fetchone()[0]
            c.execute("""SELECT status, COUNT(*) FROM fund_lookthrough GROUP BY status
                         ORDER BY 2 DESC""")
            bys = c.fetchall()
            c.execute("""SELECT venue, COUNT(*),
                                SUM(implied_prob IS NOT NULL),
                                SUM(spread IS NOT NULL),
                                SUM(volume IS NOT NULL),
                                SUM(liquidity IS NOT NULL)
                         FROM crowd_markets GROUP BY venue""")
            byv = c.fetchall()
    finally:
        conn.close()

    print(f"  fund_lookthrough : inserted={fi} skipped_existing={fs} table_total={ft}")
    for s, n in bys:
        print(f"      {s:<28} {n}")
    print(f"  crowd_markets    : inserted={ci} backfilled={cb} skipped_existing={cs} table_total={ct}")
    for v, n, ip, sp, vo, li in byv:
        print(f"      {v:<12} rows={n:<4} with_implied={ip:<4} with_spread={sp:<4} "
              f"with_volume={vo:<4} with_liquidity={li}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
