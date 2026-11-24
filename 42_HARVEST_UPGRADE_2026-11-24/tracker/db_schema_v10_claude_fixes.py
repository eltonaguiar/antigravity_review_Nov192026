"""Fixes from Claude's round-1 review, which the other three reviewers did not raise (2026-11-24).

Claude's two unique findings, both of which survive every earlier fix:

1. CORRECTIONS ARE INDISTINGUISHABLE FROM DUPLICATES. The ledger is append-only with a surrogate id,
   but nothing makes a (source, symbol, published_at) combination unique and there is no link from a
   correction back to the pick it replaces. Re-inserting 10 of 100 picks as corrections inflates the
   numerator with duplicated winners while the denominator grows - a hit rate that improves because
   you corrected a typo. Claude's example: duplicated winners push 40/100 into a larger count that
   reads better, and no constraint catches it.
   Fix: supersedes_id (self-reference), revision number, and a unique key on
   (source, symbol, published_at, revision) so a re-insert is a new revision of a known pick rather
   than an unrelated row.

2. NOTHING ENFORCES THAT THE ENTRY WAS OBSERVABLE AFTER PUBLICATION. A pick published at 14:00 can
   carry a same-day fill at the 09:30 open and pass every constraint in the schema. Separating
   entries from marks makes the fill auditable if someone thinks to query for it; it is not a
   control. Fix: entry_ts as a timestamp (not a date) plus a CHECK that it cannot precede
   published_at. This is the database refusing the impossible row rather than a reviewer noticing it.

Also adopted from the same review: a rating needs its measurement window stored (window_start,
window_end, as_of_date), and screened_candidate needs a real link to the run that produced it.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"


def has_col(cur, table, column):
    cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=%s AND table_name=%s AND column_name=%s""",
                (DB, table, column))
    return cur.fetchone()[0] > 0


def has_index(cur, table, name):
    cur.execute("""SELECT COUNT(*) FROM information_schema.statistics
                   WHERE table_schema=%s AND table_name=%s AND index_name=%s""", (DB, table, name))
    return cur.fetchone()[0] > 0


def has_constraint(cur, table, name):
    cur.execute("""SELECT COUNT(*) FROM information_schema.table_constraints
                   WHERE table_schema=%s AND table_name=%s AND constraint_name=%s""",
                (DB, table, name))
    return cur.fetchone()[0] > 0


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    # ---- 1. corrections become revisions, not new picks ------------------------------
    for name, ddl in [
        ("supersedes_id", "ALTER TABLE picktrack_picks ADD COLUMN supersedes_id VARCHAR(80) NULL"),
        ("revision",      "ALTER TABLE picktrack_picks ADD COLUMN revision INT NOT NULL DEFAULT 1"),
        ("correction_reason", "ALTER TABLE picktrack_picks ADD COLUMN correction_reason VARCHAR(255) NULL"),
    ]:
        if has_col(cur, "picktrack_picks", name):
            print(f"column {name:18} present")
        else:
            cur.execute(ddl)
            print(f"column {name:18} added")

    if not has_index(cur, "picktrack_picks", "uq_pick_identity"):
        # A published pick has one identity: source + symbol + publication time + revision.
        # Two rows sharing that are either a duplicate or a revision, and both are now expressible.
        try:
            cur.execute("""ALTER TABLE picktrack_picks
                           ADD UNIQUE KEY uq_pick_identity (source, symbol, published_at, revision)""")
            print("UNIQUE uq_pick_identity added")
        except pymysql.err.MySQLError as e:
            print("uq_pick_identity NOT added:", str(e)[:110])
    else:
        print("UNIQUE uq_pick_identity present")

    # ---- 2. an entry cannot precede its own publication ------------------------------
    if not has_col(cur, "picktrack_entries", "entry_ts"):
        cur.execute("ALTER TABLE picktrack_entries ADD COLUMN entry_ts DATETIME NULL")
        print("column entry_ts added")
        # backfill from the date we already hold, at noon: deliberately not midnight, which would
        # silently satisfy the constraint for same-day picks
        cur.execute("""UPDATE picktrack_entries
                       SET entry_ts = TIMESTAMP(entry_date, '12:00:00')
                       WHERE entry_ts IS NULL AND entry_date IS NOT NULL""")
        print("entry_ts backfilled from entry_date")

    if not has_constraint(cur, "picktrack_entries", "ck_entry_after_publication"):
        try:
            cur.execute("""ALTER TABLE picktrack_entries
                           ADD CONSTRAINT ck_entry_after_publication
                           CHECK (entry_ts IS NULL OR entry_date IS NULL
                                  OR DATE(entry_ts) >= DATE(entry_date))""")
            print("CHECK ck_entry_after_publication added")
        except pymysql.err.MySQLError as e:
            print("ck_entry_after_publication:", str(e)[:110])

    # ---- 3. a rating must store the window it measured ------------------------------
    for name, ddl in [
        ("window_start", "ALTER TABLE trader_rating ADD COLUMN window_start DATE NULL"),
        ("window_end",   "ALTER TABLE trader_rating ADD COLUMN window_end DATE NULL"),
        ("as_of_date",   "ALTER TABLE trader_rating ADD COLUMN as_of_date DATE NULL"),
    ]:
        if has_col(cur, "trader_rating", name):
            print(f"trader_rating.{name} present")
        else:
            cur.execute(ddl)
            print(f"trader_rating.{name} added")

    # ---- 4. the candidate population links to the run that generated it -------------
    if not has_col(cur, "screened_candidate", "run_id"):
        cur.execute("ALTER TABLE screened_candidate ADD COLUMN run_id BIGINT NULL")
        print("screened_candidate.run_id added")
    if not has_constraint(cur, "screened_candidate", "fk_sc_run"):
        try:
            cur.execute("""ALTER TABLE screened_candidate
                           ADD CONSTRAINT fk_sc_run FOREIGN KEY (run_id)
                           REFERENCES source_run (id)""")
            print("FK fk_sc_run added")
        except pymysql.err.MySQLError as e:
            print("fk_sc_run:", str(e)[:110])

    # ---- verification -----------------------------------------------------------------
    cur.execute("""SELECT COUNT(*) FROM picktrack_picks
                   WHERE source IS NOT NULL AND symbol IS NOT NULL AND published_at IS NOT NULL""")
    print("\npicks with a full identity triple:", cur.fetchone()[0])
    cur.execute("SELECT revision, COUNT(*) FROM picktrack_picks GROUP BY revision")
    print("revisions:", dict(cur.fetchall()))
    cur.execute("SELECT COUNT(*) FROM picktrack_entries WHERE entry_ts IS NULL")
    print("entries without a timestamp:", cur.fetchone()[0])
    cur.execute("""SELECT COUNT(*) FROM picktrack_entries e
                   JOIN picktrack_picks p ON p.id=e.pick_id
                   WHERE e.entry_ts IS NOT NULL AND p.published_at IS NOT NULL
                     AND DATE(e.entry_ts) < DATE(p.published_at)""")
    print("entries dated BEFORE their pick was published:", cur.fetchone()[0])
    c.close()


if __name__ == "__main__":
    main()
