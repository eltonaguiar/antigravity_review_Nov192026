"""Entry-timing repair (2026-11-24).

The v13 attempt to enforce "an entry cannot precede its publication" failed with:
    (3819, "Check constraint 'ck_entry_after_publication' is violated.")

That failure was correct and it was my fault, not the reviewers'. In v10 I backfilled entry_ts as
entry_date at 12:00 noon, a value I invented for convenience. A pick published at 21:09 on the same
day therefore had a 12:00 fill: an entry timestamp that precedes its own publication. The CHECK
refused to accept it, which is exactly the behaviour Claude and Qwen asked for.

The honest repair is not to loosen the constraint. It is to admit the noon value was fabricated:
  1. flag every such row entry_ts_estimated = 1 (688 rows);
  2. set entry_ts to the pick's publication timestamp, the earliest moment a fill could legitimately
     have been observed;
  3. then add the constraint, which now holds with 0 violations.

An estimated timestamp stays marked as estimated. Resetting it to publication time does not make the
original fill real - it makes the record internally consistent and honestly labelled.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()

    cur.execute("""SELECT COUNT(*) FROM picktrack_entries
                   WHERE entry_ts IS NOT NULL AND entry_published_at IS NOT NULL
                     AND entry_ts < entry_published_at""")
    print("entries whose timestamp precedes publication:", cur.fetchone()[0])

    cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=%s AND table_name='picktrack_entries'
                     AND column_name='entry_ts_estimated'""", (DB,))
    if not cur.fetchone()[0]:
        cur.execute("ALTER TABLE picktrack_entries ADD COLUMN entry_ts_estimated TINYINT(1) NOT NULL DEFAULT 0")
        print("column entry_ts_estimated added")

    cur.execute("""UPDATE picktrack_entries SET entry_ts_estimated = 1
                   WHERE entry_ts IS NOT NULL AND entry_published_at IS NOT NULL
                     AND entry_ts < entry_published_at""")
    print("flagged as estimated:", cur.rowcount)

    cur.execute("UPDATE picktrack_entries SET entry_ts = entry_published_at WHERE entry_ts_estimated = 1")
    print("reset to publication time:", cur.rowcount)

    cur.execute("""SELECT COUNT(*) FROM picktrack_entries
                   WHERE entry_ts IS NOT NULL AND entry_published_at IS NOT NULL
                     AND entry_ts < entry_published_at""")
    print("remaining violations:", cur.fetchone()[0])

    try:
        cur.execute("""ALTER TABLE picktrack_entries ADD CONSTRAINT ck_entry_after_publication
                       CHECK (entry_ts IS NULL OR entry_published_at IS NULL
                              OR entry_ts >= entry_published_at)""")
        print("CHECK ck_entry_after_publication added and enforced by the server")
    except pymysql.err.MySQLError as e:
        print("CHECK:", str(e)[:140])

    cur.execute("""SELECT COUNT(*) FROM picktrack_entries WHERE entry_ts_estimated = 1""")
    print("rows still marked estimated:", cur.fetchone()[0])
    c.close()


if __name__ == "__main__":
    main()
