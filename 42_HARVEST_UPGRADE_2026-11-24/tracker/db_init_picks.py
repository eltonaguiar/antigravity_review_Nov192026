"""Create the pick-tracking schema in ejaguiar1_stocks and load the current ledger.

Design: picks are immutable (append-only). Entries, marks and scores are separate tables so a
re-score never rewrites history, and an event log records every change. Every money figure is
stored with the cost basis and benchmark it was measured against, because the estate's recurring
failure is a number published without its assumptions.

Idempotent: safe to re-run. Tables use IF NOT EXISTS; picks are inserted with INSERT IGNORE so
an existing record is never silently overwritten by a later edit.
"""
import json
import os
import sys

import pymysql

DB = "ejaguiar1_stocks"
LEDGER = os.path.expanduser("~/pick_ledger.jsonl")

DDL = [
    """
    CREATE TABLE IF NOT EXISTS picktrack_picks (
      id             VARCHAR(80)  NOT NULL,
      source         VARCHAR(32)  NOT NULL COMMENT 'harvest|copilot|kilo|zoo|buffy|bar|audit|audit2|audit3',
      source_detail  VARCHAR(512) NULL,
      published_at   DATETIME     NOT NULL COMMENT 'UTC, when the pick was published',
      symbol         VARCHAR(24)  NULL COMMENT 'NULL for a strategy with no single tradable symbol',
      basket_json    JSON         NULL COMMENT 'equal-weight member list when the pick is a basket',
      asset_class    VARCHAR(24)  NOT NULL,
      direction      VARCHAR(12)  NOT NULL,
      rule           VARCHAR(64)  NULL COMMENT 'the pre-registered rule that produced the pick',
      conviction     DECIMAL(12,4) NULL COMMENT 'the agent reported metric, units vary by source',
      entry_rule     VARCHAR(32)  NULL COMMENT 'next_open|immediate|unscored',
      cost_bps       DECIMAL(8,2) NULL COMMENT 'round-turn cost assumed for this pick',
      benchmark      VARCHAR(24)  NULL COMMENT 'SPY|CASH|sector ETF|BTC-USD',
      status         VARCHAR(16)  NOT NULL DEFAULT 'open' COMMENT 'open|closed|unscored',
      notes          TEXT         NULL,
      created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      KEY idx_pt_source (source),
      KEY idx_pt_published (published_at),
      KEY idx_pt_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS picktrack_entries (
      id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      pick_id      VARCHAR(80) NOT NULL,
      entry_mode   VARCHAR(24) NOT NULL COMMENT 'next_open|same_day_fallback|immediate',
      entry_date   DATE        NOT NULL,
      entry_price  DECIMAL(20,6) NOT NULL,
      recorded_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      UNIQUE KEY uq_pt_entry (pick_id),
      CONSTRAINT fk_pt_entry FOREIGN KEY (pick_id) REFERENCES picktrack_picks(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS picktrack_marks (
      id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      pick_id            VARCHAR(80) NOT NULL,
      mark_date          DATE        NOT NULL,
      last_price         DECIMAL(20,6) NULL,
      raw_pct            DECIMAL(12,4) NULL,
      net_bps            DECIMAL(12,2) NULL,
      benchmark_net_bps  DECIMAL(12,2) NULL,
      excess_bps         DECIMAL(12,2) NULL,
      days_held          INT         NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_pt_mark (pick_id, mark_date),
      KEY idx_marks_pick (pick_id),
      CONSTRAINT fk_pt_mark FOREIGN KEY (pick_id) REFERENCES picktrack_picks(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS picktrack_scores (
      id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      as_of            DATE        NOT NULL,
      source           VARCHAR(32) NOT NULL,
      n_picks          INT         NOT NULL,
      mean_net_bps     DECIMAL(12,2) NULL,
      median_net_bps   DECIMAL(12,2) NULL,
      mean_excess_bps  DECIMAL(12,2) NULL,
      beat_benchmark   INT         NULL,
      n_with_bench     INT         NULL,
      verdict          VARCHAR(24) NOT NULL DEFAULT 'INSUFFICIENT_N'
                       COMMENT 'PASS|FAIL|INSUFFICIENT_N — n<30 is never a verdict',
      PRIMARY KEY (id),
      UNIQUE KEY uq_score (as_of, source)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS picktrack_events (
      id        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      pick_id   VARCHAR(80) NULL,
      event     VARCHAR(32) NOT NULL,
      detail    TEXT        NULL,
      at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      KEY idx_events_pick (pick_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE OR REPLACE VIEW v_picktrack_latest AS
    SELECT p.id, p.source, p.symbol, p.asset_class, p.direction, p.rule,
           p.published_at, e.entry_date, e.entry_mode, e.entry_price,
           m.mark_date, m.raw_pct, m.net_bps, m.benchmark_net_bps, m.excess_bps, m.days_held
    FROM picktrack_picks p
    LEFT JOIN picktrack_entries e ON e.pick_id = p.id
    LEFT JOIN picktrack_marks m ON m.id = (
        SELECT m2.id FROM picktrack_marks m2 WHERE m2.pick_id = p.id
        ORDER BY m2.mark_date DESC LIMIT 1)
    """,
]


def main():
    pw = sys.argv[1]
    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=pw, database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    created = []
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
            name = stmt.split("TABLE IF NOT EXISTS")[-1].split("(")[0].strip() if "TABLE IF" in stmt else "v_picktrack_latest"
            created.append(name)

        rows = []
        with open(LEDGER, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))

        ins = """INSERT IGNORE INTO picktrack_picks
                 (id, source, source_detail, published_at, symbol, basket_json, asset_class,
                  direction, rule, conviction, entry_rule, cost_bps, benchmark, status, notes)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        n = 0
        for r in rows:
            cur.execute(ins, (
                r.get("id"), r.get("source"), r.get("source_detail"),
                r.get("published_at", "").replace("T", " ").replace("Z", "")[:19],
                r.get("symbol"), json.dumps(r["basket"]) if r.get("basket") else None,
                r.get("asset_class"), r.get("direction"), r.get("rule"), r.get("conviction"),
                r.get("entry_rule"), r.get("cost_bps"), r.get("benchmark"),
                r.get("status", "open"), r.get("notes"),
            ))
            n += cur.rowcount

        cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                    (None, "SCHEMA_INIT", f"created {len(created)} objects; ledger load inserted {n}"))

        cur.execute("SELECT COUNT(*) FROM picktrack_picks")
        total = cur.fetchone()[0]
        cur.execute("SELECT source, COUNT(*) FROM picktrack_picks GROUP BY source ORDER BY 2 DESC")
        by_src = cur.fetchall()

    conn.close()
    print(f"objects ensured: {created}")
    print(f"picks inserted this run: {n} | total in table: {total}")
    for s, c in by_src:
        print(f"  {s:10} {c}")


if __name__ == "__main__":
    main()
