#!/usr/bin/env python3
"""trial_log.py - append-only trial ledger for the `trials` table
(docs/experiment_schema.sql).

Columns, exactly the schema's trials table:
    trial_id     TEXT PRIMARY KEY
    run_id       TEXT NOT NULL
    family       TEXT NOT NULL
    variant      TEXT NOT NULL
    sharpe_is    REAL
    sharpe_oos   REAL
    kept         INTEGER NOT NULL DEFAULT 0   -- 1 = selected variant
    ts_logged    TEXT NOT NULL

Append-only: there is no delete path. That is the point - a trial log that can be
pruned is not a trial log, and a DSR computed on a pruned log is not deflated.
"""
import sqlite3
import sys
import uuid
import datetime as dt

DDL = """
CREATE TABLE IF NOT EXISTS trials (
    trial_id     TEXT PRIMARY KEY,
    run_id       TEXT NOT NULL,
    family       TEXT NOT NULL,
    variant      TEXT NOT NULL,
    sharpe_is    REAL,
    sharpe_oos   REAL,
    kept         INTEGER NOT NULL DEFAULT 0,
    ts_logged    TEXT NOT NULL
);
"""


def log_trial(db, run_id, family, variant, sharpe_is, sharpe_oos, kept=0):
    con = sqlite3.connect(db)
    try:
        con.executescript(DDL)
        trial_id = str(uuid.uuid4())
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        con.execute(
            "INSERT INTO trials (trial_id, run_id, family, variant, sharpe_is, "
            "sharpe_oos, kept, ts_logged) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (trial_id, run_id, family, variant, sharpe_is, sharpe_oos,
             int(kept), ts),
        )
        con.commit()
        n = con.execute("SELECT COUNT(*) FROM trials").fetchone()[0]
        return trial_id, n
    finally:
        con.close()


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("usage: python trial_log.py <db> <run_id> <family> <variant> "
              "<sharpe_is> <sharpe_oos> [kept=0]")
        sys.exit(2)
    db, run_id, family, variant = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    sharpe_is = float(sys.argv[5])
    sharpe_oos = float(sys.argv[6])
    kept = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    trial_id, n = log_trial(db, run_id, family, variant, sharpe_is, sharpe_oos, kept)
    print("logged trial_id=%s run_id=%s family=%s variant=%s sharpe_is=%s "
          "sharpe_oos=%s kept=%s" % (trial_id, run_id, family, variant,
                                     sharpe_is, sharpe_oos, kept))
    print("row_count=%d" % n)
