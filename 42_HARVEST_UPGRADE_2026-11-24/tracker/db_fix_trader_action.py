"""Replace the STORED generated dedupe column with a plain composite unique key.

A generated column cannot be part of the referenced key set, and MySQL 8 refuses the FK on this
table while it exists. The uniqueness it provided is reproduced exactly by a UNIQUE KEY over
(trader_id, symbol, entry_ts, side), which the constraint engine accepts.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"
c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                    connect_timeout=15, autocommit=True)
cur = c.cursor()


def step(sql, label):
    try:
        cur.execute(sql)
        print(f"  OK   {label}")
        return True
    except Exception as e:
        print(f"  SKIP {label}: {str(e)[:100]}")
        return False


step("ALTER TABLE trader_action DROP INDEX uq_ta_action", "drop generated-column unique key")
step("ALTER TABLE trader_action DROP COLUMN dedupe_key", "drop generated column")
step("ALTER TABLE trader_action ADD UNIQUE KEY uq_ta_action (trader_id, symbol, entry_ts, side)",
     "composite unique key")
ok = step("ALTER TABLE trader_action ADD CONSTRAINT fk_ta_trader "
          "FOREIGN KEY (trader_id) REFERENCES trader(id) ON DELETE CASCADE", "fk_ta_trader")

cur.execute("""SELECT constraint_name FROM information_schema.key_column_usage
               WHERE table_schema=%s AND table_name='trader_action'
                 AND referenced_table_name IS NOT NULL""", (DB,))
print("\ntrader_action FKs now:", [r[0] for r in cur.fetchall()])
cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
            (None, "SCHEMA_V4C",
             "trader_action: generated dedupe column replaced by composite unique key "
             f"(trader_id,symbol,entry_ts,side); fk_ta_trader added={ok}"))
c.close()
