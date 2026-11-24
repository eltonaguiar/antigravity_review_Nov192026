"""Round-2 review fixes (2026-11-24). Copilot audited the v7 fix against information_schema and
VIEW_DEFINITION and found that the v7 fix moved the defect rather than removing it.

The five findings, and what each one breaks if left:

1. HORIZON-BLIND STATS. v_pick_level selects horizon_min_days/horizon_max_days but never uses them,
   and both are NULL on all picks. A mark at days_held=3 counts as a 3-month outcome. picks also had
   no pick_type and no horizon_code, so a pick could not even express which horizon it belongs to.
   Fix: add pick_type + horizon_code (FK to horizon_ref), backfill from the pick's own timeframe, and
   make the stats view count only marks whose days_held falls inside that horizon.

2. A RATE BELOW THE SAMPLE FLOOR, PUBLISHED AS AUTHORITATIVE. The view reported COMMODITY 75.00%
   on 8 marked picks. That is the n<30 rule violated inside a view that reads like a verdict.
   Fix: gate every rate on the applicable min_n and return NULL below it, with the reason exposed.

3. ONE-ROW-PER-PICK WAS UNENFORCED. 494 marks / 494 picks is true today, but nothing stopped a
   second mark on the same (pick_id, mark_date), which the MAX() join would return twice -
   re-introducing the exact weighting just fixed. Fix: UNIQUE (pick_id, mark_date).

4. pick_resolution HAD NO FOREIGN KEY AND NO UNIQUENESS. It is meant to become the authority on
   outcomes, so an orphan or duplicate resolution would silently win. Fix: FK to picktrack_picks
   plus UNIQUE (pick_id, horizon).

5. screened_candidate COULD NOT BE A MULTIPLE-TESTING DENOMINATOR. rule_hash was varchar(32) while
   rule_version.rule_hash is char(64), so the join that scopes a trial count to a published rule was
   impossible; there was no pick_id; and `passed` was two-valued so rule-rejection could not be told
   apart from passed-but-not-selected. Fix: widen to char(64), add nullable pick_id FK, add a
   three-state decision column, keep the index.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

TIMEFRAME_TO_TYPE = {
    "SCALP": "DAY_TRADE", "INTRADAY": "DAY_TRADE",
    "SWING": "SWING_TRADE", "POSITION": "POSITION", "LONG_TERM": "LONG_TERM",
}
TYPE_TO_HORIZON = {
    "DAY_TRADE": "1D", "SWING_TRADE": "1M", "POSITION": "3M",
    "LONG_TERM": "1Y", "BUY_AND_HOLD": "1Y",
}


def col(cur, table, column):
    cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=%s AND table_name=%s AND column_name=%s""",
                (DB, table, column))
    return cur.fetchone()[0] > 0


def idx(cur, table, name):
    cur.execute("""SELECT COUNT(*) FROM information_schema.statistics
                   WHERE table_schema=%s AND table_name=%s AND index_name=%s""", (DB, table, name))
    return cur.fetchone()[0] > 0


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    # ---- 1. horizon + pick type on the pick itself -------------------------------------
    for name, ddl in [
        ("pick_type",    "ALTER TABLE picktrack_picks ADD COLUMN pick_type VARCHAR(24) NULL"),
        ("horizon_code", "ALTER TABLE picktrack_picks ADD COLUMN horizon_code VARCHAR(32) NULL"),
    ]:
        if col(cur, "picktrack_picks", name):
            print(f"column {name:12} present")
        else:
            cur.execute(ddl)
            print(f"column {name:12} added")

    if not idx(cur, "picktrack_picks", "fk_pick_horizon"):
        cur.execute("""SELECT COUNT(*) FROM information_schema.table_constraints
                       WHERE table_schema=%s AND table_name='picktrack_picks'
                         AND constraint_name='fk_pick_horizon'""", (DB,))
        if not cur.fetchone()[0]:
            try:
                cur.execute("""ALTER TABLE picktrack_picks
                               ADD CONSTRAINT fk_pick_horizon FOREIGN KEY (horizon_code)
                               REFERENCES horizon_ref (horizon_code)""")
                print("FK fk_pick_horizon added")
            except pymysql.err.MySQLError as e:
                print("FK fk_pick_horizon skipped:", str(e)[:70])

    # backfill from the pick's own timeframe, which was always recorded in notes
    for tf, ptype in TIMEFRAME_TO_TYPE.items():
        cur.execute("""UPDATE picktrack_picks SET pick_type=%s
                       WHERE notes LIKE %s AND (pick_type IS NULL OR pick_type='')""",
                    (ptype, f"%timeframe={tf}%"))
    cur.execute("UPDATE picktrack_picks SET pick_type='UNCLASSIFIED' WHERE pick_type IS NULL")
    for ptype, hz in TYPE_TO_HORIZON.items():
        cur.execute("UPDATE picktrack_picks SET horizon_code=%s WHERE pick_type=%s AND horizon_code IS NULL",
                    (hz, ptype))
    cur.execute("UPDATE picktrack_picks SET horizon_code='1M' WHERE horizon_code IS NULL")
    cur.execute("SELECT pick_type, horizon_code, COUNT(*) FROM picktrack_picks GROUP BY pick_type, horizon_code")
    print("pick_type / horizon:", cur.fetchall())

    # ---- 3. one mark per pick per day, enforced ---------------------------------------
    if not idx(cur, "picktrack_marks", "uq_pt_mark"):
        try:
            cur.execute("ALTER TABLE picktrack_marks ADD UNIQUE KEY uq_pt_mark (pick_id, mark_date)")
            print("UNIQUE uq_pt_mark added")
        except pymysql.err.MySQLError as e:
            print("uq_pt_mark:", str(e)[:80])
    else:
        print("UNIQUE uq_pt_mark present")

    # ---- 4. pick_resolution gets identity ---------------------------------------------
    if not idx(cur, "pick_resolution", "uq_res_pick_horizon"):
        try:
            cur.execute("ALTER TABLE pick_resolution ADD UNIQUE KEY uq_res_pick_horizon (pick_id, horizon)")
            print("UNIQUE uq_res_pick_horizon added")
        except pymysql.err.MySQLError as e:
            print("uq_res_pick_horizon:", str(e)[:80])
    try:
        cur.execute("""ALTER TABLE pick_resolution
                       ADD CONSTRAINT fk_res_pick FOREIGN KEY (pick_id)
                       REFERENCES picktrack_picks (id)""")
        print("FK fk_res_pick added")
    except pymysql.err.MySQLError as e:
        print("fk_res_pick:", str(e)[:70])

    # ---- 5. screened_candidate becomes usable as a denominator -------------------------
    cur.execute("SHOW COLUMNS FROM screened_candidate")
    sc = {r[0]: r[1] for r in cur.fetchall()}
    if not sc.get("rule_hash", "").startswith("char(64)"):
        cur.execute("ALTER TABLE screened_candidate MODIFY COLUMN rule_hash CHAR(64) NULL")
        print("screened_candidate.rule_hash widened to char(64)")
    if "decision" not in sc:
        cur.execute("""ALTER TABLE screened_candidate
                       ADD COLUMN decision ENUM('REJECTED','NOT_SELECTED','PROMOTED')
                       NOT NULL DEFAULT 'REJECTED'""")
        print("screened_candidate.decision added")
    if "pick_id" not in sc:
        cur.execute("ALTER TABLE screened_candidate ADD COLUMN pick_id VARCHAR(80) NULL")
        print("screened_candidate.pick_id added")

    # ---- 2. stats view: horizon-aware and fail-closed ---------------------------------
    # Order matters: v_pick_stats_by_source reads columns that only the REBUILT v_pick_level has,
    # so the old stats view must go first, then the level view, then the stats view.
    cur.execute("DROP VIEW IF EXISTS v_pick_stats_by_source")
    cur.execute("DROP VIEW IF EXISTS v_pick_level")
    cur.execute("""
        CREATE VIEW v_pick_level AS
        SELECT p.id AS pick_id, p.source, p.asset_class, p.direction, p.status,
               p.cost_bps, p.benchmark, p.published_at,
               p.pick_type, p.horizon_code,
               p.horizon_min_days, p.horizon_max_days,
               p.profile_code, p.stop_pct, p.reward_risk,
               lm.net_bps, lm.excess_bps, lm.days_held,
               CASE WHEN lm.net_bps > 0 THEN 1 ELSE 0 END AS is_win,
               CASE WHEN lm.net_bps IS NULL THEN 'UNMARKED'
                    WHEN lm.net_bps > 0 THEN 'WIN' ELSE 'LOSS' END AS outcome,
               CASE WHEN lm.net_bps IS NOT NULL
                     AND (h.min_days IS NULL OR lm.days_held >= h.min_days)
                     AND (h.max_days IS NULL OR lm.days_held <= h.max_days)
                    THEN 1 ELSE 0 END AS in_horizon
        FROM picktrack_picks p
        LEFT JOIN v_pick_latest_mark lm ON lm.pick_id = p.id
        LEFT JOIN horizon_ref h ON h.horizon_code = p.horizon_code""")
    print("v_pick_level rebuilt with horizon_code + in_horizon")
    cur.execute("""
        CREATE VIEW v_pick_stats_by_source AS
        SELECT l.source, l.asset_class, l.horizon_code,
               COUNT(*) AS picks,
               SUM(CASE WHEN l.in_horizon = 1 THEN 1 ELSE 0 END) AS marked_in_horizon,
               SUM(CASE WHEN l.in_horizon = 1 AND l.is_win = 1 THEN 1 ELSE 0 END) AS wins,
               CASE WHEN SUM(CASE WHEN l.in_horizon = 1 THEN 1 ELSE 0 END) < 30 THEN NULL
                    ELSE ROUND(100.0 * SUM(CASE WHEN l.in_horizon = 1 AND l.is_win = 1 THEN 1 ELSE 0 END)
                               / NULLIF(SUM(CASE WHEN l.in_horizon = 1 THEN 1 ELSE 0 END), 0), 2)
               END AS win_rate_pct,
               ROUND(AVG(CASE WHEN l.in_horizon = 1 THEN l.net_bps END), 2) AS mean_net_bps,
               CASE WHEN SUM(CASE WHEN l.in_horizon = 1 THEN 1 ELSE 0 END) < 30
                    THEN 'INSUFFICIENT_N - rate suppressed' ELSE 'REPORTABLE' END AS status
        FROM v_pick_level l
        GROUP BY l.source, l.asset_class, l.horizon_code""")

    print("\nviews rebuilt: v_pick_level (horizon-aware), v_pick_stats_by_source (fail-closed)")

    # ---- verification: the 75%/n=8 row must now be suppressed -------------------------
    cur.execute("""SELECT asset_class, marked_in_horizon, wins, win_rate_pct, status
                   FROM v_pick_stats_by_source WHERE source='audit'
                   ORDER BY marked_in_horizon DESC""")
    print("\naudit stats after the fix:")
    for r in cur.fetchall():
        print("  ", r)
    cur.execute("""SELECT COUNT(*) FROM v_pick_stats_by_source WHERE win_rate_pct IS NOT NULL""")
    print("\nreportable rows:", cur.fetchone()[0])
    c.close()


if __name__ == "__main__":
    main()
