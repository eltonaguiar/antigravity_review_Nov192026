"""Fixes for defects the reviewers found in MY OWN earlier fixes (2026-11-24, round 3).

Two of the round-3 answers are not about the original schema. They are about the corrections I made
in response to round 1, which is the more useful kind of finding.

1. QWEN: "DDL constraints must own temporal validity. Code-level checks permit backfill drift to
   inject impossible timestamps without constraint violations. Move the rule to SQL."
   Verified, and Qwen is right. The CHECK created in v10 reads:
       entry_ts IS NULL OR entry_date IS NULL OR DATE(entry_ts) >= DATE(entry_date)
   It compares a row against ITSELF. entry_date was populated from the pick's publication date, so
   the constraint is a tautology whenever the two agree, and says nothing at all about published_at.
   A same-day fill at the open of a 14:00 pick still passes. Fix: carry the pick's publication
   timestamp into the entry row (entry_published_at) and constrain entry_ts against that, so the
   database - not the ETL - refuses the impossible row.

2. CLAUDE: "A fixed NULL below n=30 conflicts with pick_type_ref (BUY_AND_HOLD minimum 10,
   LONG_TERM 20). Either BUY_AND_HOLD ratings are always NULL, or the ref table is ignored."
   Also right. I hard-coded 30 in the stats view while shipping a reference table that says 10, 20,
   40, 60, 100. Two contradictory floors in one schema. Fix: derive the threshold from pick_type_ref
   by the pick's own type, fall back to 30 only for UNCLASSIFIED, and expose the applied threshold so
   a reader can see which rule suppressed the number.

Also recorded, not changed: Qwen reads v_pick_latest_mark's ROW_NUMBER as "suppression of revision
history". Nothing is deleted - picktrack_marks retains every row; the view selects one. That is a
read-time projection, not evidence loss, and the raw table remains the audit trail.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"


def col(cur, table, column):
    cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=%s AND table_name=%s AND column_name=%s""",
                (DB, table, column))
    return cur.fetchone()[0] > 0


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    # ---- 1. the entry row must carry the publication it claims to follow --------------
    if not col(cur, "picktrack_entries", "entry_published_at"):
        cur.execute("ALTER TABLE picktrack_entries ADD COLUMN entry_published_at DATETIME NULL")
        print("column entry_published_at added")
        cur.execute("""UPDATE picktrack_entries e
                       JOIN picktrack_picks p ON p.id = e.pick_id
                       SET e.entry_published_at = p.published_at
                       WHERE e.entry_published_at IS NULL""")
        print("backfilled from picktrack_picks.published_at:", cur.rowcount)

    try:
        cur.execute("ALTER TABLE picktrack_entries DROP CHECK ck_entry_after_publication")
        print("dropped the tautological CHECK (it compared the row to itself)")
    except pymysql.err.MySQLError as e:
        print("drop CHECK:", str(e)[:90])

    try:
        cur.execute("""ALTER TABLE picktrack_entries
                       ADD CONSTRAINT ck_entry_after_publication
                       CHECK (entry_ts IS NULL OR entry_published_at IS NULL
                              OR entry_ts >= entry_published_at)""")
        print("CHECK rebuilt against entry_published_at - a real cross-field rule")
    except pymysql.err.MySQLError as e:
        print("rebuild CHECK:", str(e)[:140])

    # prove it now bites: try to insert an entry before its publication, expect a refusal
    cur.execute("SELECT id, published_at FROM picktrack_picks WHERE published_at IS NOT NULL LIMIT 1")
    sample = cur.fetchone()
    if sample:
        pid, pub = sample
        try:
            cur.execute("""INSERT INTO picktrack_entries
                           (pick_id, entry_mode, entry_date, entry_price, entry_ts, entry_published_at)
                           VALUES (%s,'CONSTRAINT_TEST',DATE(%s),1.0, DATE_SUB(%s, INTERVAL 1 DAY), %s)""",
                        (pid, pub, pub, pub))
            print("CONSTRAINT DID NOT BITE - a pre-publication entry was accepted (test row inserted)")
            cur.execute("DELETE FROM picktrack_entries WHERE entry_mode='CONSTRAINT_TEST'")
        except pymysql.err.MySQLError as e:
            print("constraint bites: pre-publication entry refused ->", str(e)[:80])

    # ---- 2. one threshold, taken from pick_type_ref -----------------------------------
    cur.execute("DROP VIEW IF EXISTS v_pick_stats_by_source")
    cur.execute("""
        CREATE VIEW v_pick_stats_by_source AS
        SELECT l.source, l.asset_class, l.horizon_code, l.pick_type,
               COALESCE(pt.min_n, 30) AS min_n_applied,
               COUNT(*) AS picks,
               SUM(l.in_horizon = 1) AS marked_in_horizon,
               SUM(CASE WHEN l.in_horizon = 1 AND l.is_win = 1 THEN 1 ELSE 0 END) AS wins,
               CASE WHEN SUM(l.in_horizon = 1) < COALESCE(pt.min_n, 30) THEN NULL
                    ELSE ROUND(100.0 * SUM(CASE WHEN l.in_horizon = 1 AND l.is_win = 1 THEN 1 ELSE 0 END)
                               / NULLIF(SUM(l.in_horizon = 1), 0), 2) END AS win_rate_pct,
               CASE WHEN SUM(l.in_horizon = 1) < COALESCE(pt.min_n, 30)
                    THEN CONCAT('INSUFFICIENT_N - needs ', COALESCE(pt.min_n, 30),
                                ' for ', l.pick_type, ', has ', SUM(l.in_horizon = 1))
                    ELSE 'REPORTABLE' END AS status
        FROM v_pick_level l
        LEFT JOIN pick_type_ref pt ON pt.code = l.pick_type
        GROUP BY l.source, l.asset_class, l.horizon_code, l.pick_type, pt.min_n""")
    print("\nv_pick_stats_by_source rebuilt with the threshold derived from pick_type_ref")

    cur.execute("""SELECT DISTINCT pick_type, min_n_applied FROM v_pick_stats_by_source
                   ORDER BY min_n_applied""")
    print("threshold now applied per pick type:", cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM v_pick_stats_by_source WHERE win_rate_pct IS NOT NULL")
    print("reportable cohorts:", cur.fetchone()[0])
    cur.execute("""SELECT asset_class, pick_type, min_n_applied, marked_in_horizon, win_rate_pct, status
                   FROM v_pick_stats_by_source WHERE source='audit' AND marked_in_horizon>0
                   ORDER BY marked_in_horizon DESC LIMIT 4""")
    print("\naudit cohorts:")
    for r in cur.fetchall():
        print("  ", r)
    c.close()


if __name__ == "__main__":
    main()
