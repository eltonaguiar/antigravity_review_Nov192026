"""Audit: (a) which tables in ejaguiar1_stocks were created today (by me) vs pre-existing,
(b) whether ejaguiar1_backups is writable, so the backup rule can actually be honoured.

Nothing here modifies anything.
"""
import sys

import pymysql

SRC = "ejaguiar1_stocks"
BAK = "ejaguiar1_backups"


def main():
    pw_stocks, pw_backups = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])

    c = pymysql.connect(host="mysql.50webs.com", user=SRC, password=pw_stocks, database=SRC,
                        connect_timeout=15)
    cur = c.cursor()
    cur.execute("""SELECT table_name, table_type, create_time, update_time
                   FROM information_schema.tables
                   WHERE table_schema=%s AND table_name LIKE %s
                   ORDER BY table_name""", (SRC, "picktrack%"))
    mine_a = cur.fetchall()

    names = ["analyst_registry", "analyst_actions", "fund_lookthrough", "crowd_markets",
             "crowd_mappings", "source_run", "rule_version", "instrument", "consensus_snapshot",
             "price_bar", "pick_resolution", "trader", "trader_action", "trader_rating",
             "risk_profile", "pick_type_ref"]
    q = ",".join(["%s"] * len(names))
    cur.execute(f"""SELECT table_name, create_time, update_time FROM information_schema.tables
                    WHERE table_schema=%s AND table_name IN ({q}) ORDER BY table_name""",
                (SRC, *names))
    mine_b = cur.fetchall()

    print(f"=== tables created by this work ({len(mine_a) + len(mine_b)}) ===")
    for r in list(mine_a) + list(mine_b):
        print(f"  {r[0]:24} created {r[1]}  updated {r[2]}")

    # any pre-existing table whose update_time is today would deserve scrutiny
    cur.execute("""SELECT table_name, table_rows, update_time FROM information_schema.tables
                   WHERE table_schema=%s AND update_time >= CURDATE()
                     AND table_name NOT LIKE %s
                   ORDER BY update_time DESC LIMIT 15""", (SRC, "picktrack%"))
    touched = [r for r in cur.fetchall()
               if r[0] not in names]
    print(f"\n=== pre-existing tables reporting an update today ({len(touched)}) ===")
    for r in touched:
        print(f"  {r[0]:34} ~{r[1]} rows  updated {r[2]}")
    print("  (update_time moves on DDL and on some bulk writes — row counts are the check, "
          "not the timestamp)")
    c.close()

    print(f"\n=== can we reach {BAK}? ===")
    for user in (BAK, SRC):
        try:
            b = pymysql.connect(host="mysql.50webs.com", user=user, password=pw_backups,
                                database=BAK, connect_timeout=12)
            cur2 = b.cursor()
            cur2.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s",
                         (BAK,))
            n = cur2.fetchone()[0]
            cur2.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s "
                         "ORDER BY create_time DESC LIMIT 5", (BAK,))
            print(f"  CONNECTED as {user} — {n} tables; newest: {[r[0] for r in cur2.fetchall()]}")
            b.close()
            break
        except Exception as e:
            print(f"  fail as {user}: {type(e).__name__}: {str(e)[:80]}")


if __name__ == "__main__":
    main()
