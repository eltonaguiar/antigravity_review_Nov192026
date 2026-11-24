"""Fixes from the four-model review of the tracker schema (2026-11-24).

The reviewers converged on one defect and raised three more. Each fix below is tied to the
specific criticism, because a fix with no traceable reason gets reverted in the next round.

1. MARK-ROW WEIGHTING (all four reviewers, independently).
   AVG(net_bps) over picktrack_marks weights a pick by how many days it was held, not by one
   vote per pick. A 20-day pick contributes 16 rows from day 5 on and drowns a 5-day pick.
   ChatGPT's example: one pick with ten marks at +100 bps and another with one mark at -100 bps
   yields +81.8 bps, while the per-pick average is 0 bps.
   Fix: views v_pick_last_mark and v_pick_latest_mark give exactly one row per pick, and
   v_pick_stats_by_source aggregates over those. Hit rates come from pick-level rows only.

2. HORIZON AS A BARE STRING (ChatGPT, Qwen, GLM).
   'horizon VARCHAR' lets two ratings labelled "1 month" measure different intervals.
   Fix: horizon_min_days / horizon_max_days stored with the pick, and a horizon_ref table that
   gives each named horizon its bounds. A rating is only comparable within identical bounds.

3. NO REGISTRY OF SCREENED-AND-REJECTED CANDIDATES (ChatGPT, Qwen).
   trials_screened is an unverified scalar. Without the discarded candidates persisted, 5,000
   attempts can be presented as one, and no multiple-testing penalty can be defended.
   Fix: screened_candidate table - every candidate considered, passed or not, with a reason.

4. DERIVED COLUMNS CAN DRIFT (Qwen, GLM; ChatGPT partially).
   raw_pct, net_bps, excess_bps are computed at write time, so a later backfill with a different
   cost or benchmark leaves old rows inconsistent with new ones.
   Fix: keep them (they are auditable evidence of what was believed at write time) but add
   v_mark_recomputed that recomputes net from first principles, plus a drift view that flags any
   row where stored and recomputed disagree. Drift becomes measurable instead of invisible.

Note: no pre-existing table outside this schema is touched.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

DDL = [
    # ---- 1. one row per pick ------------------------------------------------------------
    ("v_pick_last_mark_date", """
        CREATE OR REPLACE VIEW v_pick_last_mark_date AS
        SELECT pick_id, MAX(mark_date) AS last_mark_date
        FROM picktrack_marks GROUP BY pick_id"""),
    ("v_pick_latest_mark", """
        CREATE OR REPLACE VIEW v_pick_latest_mark AS
        SELECT m.pick_id, m.mark_date, m.last_price, m.raw_pct, m.net_bps,
               m.benchmark_net_bps, m.excess_bps, m.days_held
        FROM picktrack_marks m
        JOIN v_pick_last_mark_date d
          ON d.pick_id = m.pick_id AND d.last_mark_date = m.mark_date"""),
    ("v_pick_level", """
        CREATE OR REPLACE VIEW v_pick_level AS
        SELECT p.id AS pick_id, p.source, p.asset_class, p.direction, p.status,
               p.cost_bps, p.benchmark, p.published_at,
               p.horizon_min_days, p.horizon_max_days,
               lm.net_bps, lm.excess_bps, lm.days_held,
               CASE WHEN lm.net_bps IS NULL THEN NULL
                    WHEN lm.net_bps > 0 THEN 1 ELSE 0 END AS is_win,
               CASE WHEN lm.net_bps IS NULL THEN 'UNMARKED'
                    WHEN lm.net_bps > 0 THEN 'WIN' ELSE 'LOSS' END AS outcome
        FROM picktrack_picks p
        LEFT JOIN v_pick_latest_mark lm ON lm.pick_id = p.id"""),
    ("v_pick_stats_by_source", """
        CREATE OR REPLACE VIEW v_pick_stats_by_source AS
        SELECT source, asset_class,
               COUNT(*) AS picks,
               SUM(CASE WHEN net_bps IS NOT NULL THEN 1 ELSE 0 END) AS marked_picks,
               SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END) AS wins,
               ROUND(100.0 * SUM(CASE WHEN is_win = 1 THEN 1 ELSE 0 END)
                     / NULLIF(SUM(CASE WHEN is_win IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS win_rate_pct,
               ROUND(AVG(CASE WHEN net_bps IS NOT NULL THEN net_bps END), 2) AS mean_net_bps_per_pick,
               ROUND(MIN(net_bps), 2) AS worst_pick_bps,
               ROUND(MAX(net_bps), 2) AS best_pick_bps
        FROM v_pick_level
        GROUP BY source, asset_class"""),

    # ---- 4. drift is measurable ---------------------------------------------------------
    ("v_mark_recomputed", """
        CREATE OR REPLACE VIEW v_mark_recomputed AS
        SELECT m.pick_id, m.mark_date, m.raw_pct AS stored_raw_pct,
               p.cost_bps,
               ROUND(m.raw_pct * 100 - p.cost_bps, 4) AS recomputed_net_bps,
               m.net_bps AS stored_net_bps,
               ROUND(m.net_bps - (m.raw_pct * 100 - p.cost_bps), 4) AS drift_bps
        FROM picktrack_marks m
        JOIN picktrack_picks p ON p.id = m.pick_id"""),
]

# ---- 2. horizon bounds ----------------------------------------------------------------
ALTERS = [
    ("picktrack_picks", "horizon_min_days", "ALTER TABLE picktrack_picks ADD COLUMN horizon_min_days INT NULL"),
    ("picktrack_picks", "horizon_max_days", "ALTER TABLE picktrack_picks ADD COLUMN horizon_max_days INT NULL"),
    ("picktrack_picks", "screened_by_run", "ALTER TABLE picktrack_picks ADD COLUMN screened_by_run BIGINT NULL"),
]

TABLES = [
    ("horizon_ref", """
        CREATE TABLE IF NOT EXISTS horizon_ref (
          horizon_code   VARCHAR(32) NOT NULL,
          label          VARCHAR(64) NOT NULL,
          min_days       INT NOT NULL,
          max_days       INT NOT NULL,
          anchor         VARCHAR(32) NOT NULL DEFAULT 'published_date',
          notes          VARCHAR(255) NULL,
          PRIMARY KEY (horizon_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""),
    ("screened_candidate", """
        CREATE TABLE IF NOT EXISTS screened_candidate (
          id            BIGINT NOT NULL AUTO_INCREMENT,
          source        VARCHAR(40) NOT NULL,
          screened_at   DATETIME NOT NULL,
          symbol        VARCHAR(32) NULL,
          asset_class   VARCHAR(24) NULL,
          strategy      VARCHAR(64) NULL,
          passed        TINYINT(1) NOT NULL DEFAULT 0,
          reject_reason VARCHAR(96) NULL,
          rule_hash     VARCHAR(32) NULL,
          source_run_id BIGINT NULL,
          notes         VARCHAR(255) NULL,
          PRIMARY KEY (id),
          KEY ix_sc_source (source, screened_at),
          KEY ix_sc_passed (passed)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""),
]

HORIZONS = [
    ("1D", "one day", 0, 1, "published_date"),
    ("1W", "one week", 1, 7, "published_date"),
    ("1M", "one month (~21 trading days)", 7, 31, "published_date"),
    ("3M", "three months (~63 trading days)", 31, 94, "published_date"),
    ("6M", "six months", 94, 190, "published_date"),
    ("1Y", "one year", 190, 370, "published_date"),
]


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()
    cur.execute("SELECT VERSION()")
    print("server:", cur.fetchone()[0])

    for name, ddl in TABLES:
        cur.execute(ddl)
        print(f"table {name:22} ok")

    for table, col, ddl in ALTERS:
        cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                       WHERE table_schema=%s AND table_name=%s AND column_name=%s""",
                    (DB, table, col))
        if cur.fetchone()[0]:
            print(f"column {table}.{col:18} already present")
        else:
            cur.execute(ddl)
            print(f"column {table}.{col:18} added")

    for code, label, lo, hi, anchor in HORIZONS:
        cur.execute("""INSERT INTO horizon_ref (horizon_code,label,min_days,max_days,anchor)
                       VALUES (%s,%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE label=VALUES(label), min_days=VALUES(min_days),
                         max_days=VALUES(max_days), anchor=VALUES(anchor)""",
                    (code, label, lo, hi, anchor))
    print(f"horizon_ref rows: {len(HORIZONS)}")

    for name, ddl in DDL:
        cur.execute(ddl)
        print(f"view  {name:22} ok")

    # prove the weighting fix on real data
    cur.execute("SELECT COUNT(*) FROM v_pick_latest_mark")
    n_latest = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM picktrack_marks")
    n_marks = cur.fetchone()[0]
    cur.execute("SELECT ROUND(AVG(net_bps),2) FROM picktrack_marks")
    mark_weighted = cur.fetchone()[0]
    cur.execute("SELECT ROUND(AVG(net_bps),2) FROM v_pick_level WHERE net_bps IS NOT NULL")
    pick_weighted = cur.fetchone()[0]
    print(f"\nmarks rows {n_marks} -> picks {n_latest}")
    print(f"mark-weighted mean {mark_weighted} bps  vs  pick-weighted mean {pick_weighted} bps")

    cur.execute("SELECT COUNT(*) FROM v_mark_recomputed WHERE ABS(drift_bps) > 0.01")
    print("rows with write-time drift:", cur.fetchone()[0])
    c.close()


if __name__ == "__main__":
    main()
