#!/usr/bin/env python3
"""Independent audit of the picktracking schema in ejaguiar1_stocks.

Reads the LIVE catalogue rather than the design document, because the document is
written by the same agent that wrote the DDL and therefore cannot falsify it.

For every object it reports: column list with types/nullability, primary key,
foreign keys, unique indexes, and exact row count. It then checks the specific
properties a tracking schema must have to be trustworthy:

  P1  every fact row carries provenance to the fetch that produced it
  P2  the outcome for a pick is defined in exactly ONE place
  P3  a label is reproducible from its own row (rule version stored)
  P4  a derived consensus carries its coverage
  P5  the source dimension is referenced, not free-texted

Read-only. No DDL. No writes.
"""
from __future__ import annotations

import os
import sys

import pymysql

DB = "ejaguiar1_stocks"
OBJECTS = [
    "picktrack_picks", "picktrack_entries", "picktrack_marks", "picktrack_scores",
    "picktrack_events", "analyst_registry", "analyst_actions", "fund_lookthrough",
    "crowd_markets", "crowd_mappings", "source_run", "rule_version", "instrument",
    "consensus_snapshot", "price_bar", "pick_resolution", "trader", "trader_action",
    "trader_rating", "risk_profile", "pick_type_ref",
]
VIEWS = ["v_picktrack_latest"]


def connect():
    pw = os.environ.get("DB_PASS_STOCKS")
    if not pw:
        sys.exit("DB_PASS_STOCKS not set")
    return pymysql.connect(host="mysql.50webs.com", user="ejaguiar1_stocks",
                           password=pw, database=DB, charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor, connect_timeout=25)


def q(cur, sql, args=None):
    cur.execute(sql, args or ())
    return cur.fetchall()


def main() -> int:
    cn = connect()
    cur = cn.cursor()

    print("=" * 78)
    print("LIVE CATALOGUE")
    print("=" * 78)
    live_t = {r["TABLE_NAME"] for r in q(cur,
        "SELECT TABLE_NAME FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA=%s AND TABLE_TYPE='BASE TABLE'", (DB,))}
    live_v = {r["TABLE_NAME"] for r in q(cur,
        "SELECT TABLE_NAME FROM information_schema.VIEWS WHERE TABLE_SCHEMA=%s", (DB,))}

    missing = [o for o in OBJECTS if o not in live_t]
    print(f"declared tables {len(OBJECTS)}, live base tables named: "
          f"{len([o for o in OBJECTS if o in live_t])}")
    print(f"MISSING vs your list: {missing or 'none'}")
    print(f"views present: {sorted(live_v)}")

    schema: dict[str, dict] = {}
    for t in OBJECTS:
        if t not in live_t:
            continue
        cols = q(cur, "SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_KEY,COLUMN_DEFAULT "
                      "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s "
                      "ORDER BY ORDINAL_POSITION", (DB, t))
        n = q(cur, f"SELECT COUNT(*) c FROM `{t}`")[0]["c"]
        fks = q(cur, "SELECT COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME "
                     "FROM information_schema.KEY_COLUMN_USAGE "
                     "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL",
                (DB, t))
        schema[t] = {"cols": cols, "n": n, "fks": fks}
        pk = [c["COLUMN_NAME"] for c in cols if c["COLUMN_KEY"] == "PRI"]
        print(f"\n-- {t}  rows={n}  pk={pk or 'NONE'}")
        print("   " + ", ".join(f"{c['COLUMN_NAME']}:{c['COLUMN_TYPE']}"
                                + ("" if c["IS_NULLABLE"] == "NO" else "?") for c in cols))
        if fks:
            print("   FK: " + "; ".join(f"{f['COLUMN_NAME']}->{f['REFERENCED_TABLE_NAME']}."
                                        f"{f['REFERENCED_COLUMN_NAME']}" for f in fks))
        else:
            print("   FK: none")

    def has(t, *cands):
        return [c for c in cands if t in schema and
                any(x["COLUMN_NAME"] == c for x in schema[t]["cols"])]

    print("\n" + "=" * 78)
    print("PROPERTY CHECKS")
    print("=" * 78)

    # P5 — is the source dimension a real table?
    print(f"\nP5 source dimension as a table : "
          f"{'source_system EXISTS' if 'source_system' in live_t else 'ABSENT - no source_system table'}")
    for t in ("picktrack_picks", "picktrack_entries", "consensus_snapshot"):
        print(f"   {t} source columns: {has(t, 'source_system', 'source_system_id', 'source_id')}")

    # P1 — provenance
    print("\nP1 provenance on fact rows:")
    for t in ("picktrack_picks", "picktrack_entries", "consensus_snapshot", "fund_lookthrough"):
        print(f"   {t}: {has(t,'source_run_id','run_id','fetch_id') or 'NONE'}")

    # P2 — how many places define an outcome
    print("\nP2 outcome-defining objects:")
    for t in ("pick_resolution", "picktrack_marks", "picktrack_scores", "picktrack_entries"):
        if t in schema:
            out = has(t, "outcome", "result", "status", "pnl", "pnl_pct", "won", "exit_reason")
            print(f"   {t}: rows={schema[t]['n']} outcome-ish cols={out}")

    # P3 — label reproducibility
    print("\nP3 label reproducibility:")
    print(f"   consensus_snapshot: {has('consensus_snapshot','label','label_rule_version','rule_version_id','raw_counts')}")

    # P4 — coverage
    print("\nP4 derived-consensus coverage:")
    print(f"   fund_lookthrough: {has('fund_lookthrough','weight_coverage_pct','holdings_count','matched_count')}")

    print("\n" + "=" * 78)
    print("VIEW DEFINITIONS")
    print("=" * 78)
    for v in sorted(live_v):
        d = q(cur, "SELECT VIEW_DEFINITION d FROM information_schema.VIEWS "
                   "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", (DB, v))
        if d:
            print(f"\n-- {v}\n   {d[0]['d'].strip()[:600]}")

    cn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
