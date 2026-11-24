"""v5: adopt the two ideas from Kilo's rating vector that are strictly better than mine.

1. expectancy_worst_bps — recompute expectancy at the WILSON UPPER BOUND of the loss rate instead
   of the point estimate. This is a stronger tail test than my "remove the top 3 trades": a 97.6%
   record on n=41 has a loss-rate upper bound near 8%, not 2.4%, and that single change flips the
   verdict. It is the right way to stress a negative-skew profile.

2. tier — align my A/B/C badges with the survival-based tiers, which name the failure instead of
   grading it: A_SURVIVES_STRESS / B_POSITIVE_BUT_TAIL_UNPROVEN / C_NO_EDGE / INSUFFICIENT_N.

Both are additive columns on a table created today, so no pre-existing table is touched and no
backup is required under the standing rule. Recorded here so that reasoning is auditable.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

ALTERS = [
    ("ADD COLUMN loss_rate_upper DECIMAL(6,4) NULL "
     "COMMENT 'Wilson 95 upper bound on loss rate - the input to the stress test'", "loss_rate_upper"),
    ("ADD COLUMN expectancy_worst_bps DECIMAL(12,2) NULL "
     "COMMENT 'expectancy recomputed at loss_rate_upper; negative means the record dies under stress'",
     "expectancy_worst_bps"),
    ("ADD COLUMN tier VARCHAR(32) NOT NULL DEFAULT 'INSUFFICIENT_N' "
     "COMMENT 'A_SURVIVES_STRESS|B_POSITIVE_BUT_TAIL_UNPROVEN|C_NO_EDGE|INSUFFICIENT_N'", "tier"),
    ("ADD COLUMN tier_score DECIMAL(6,2) NULL COMMENT '0-100 composite; -15 when tail stress fails'",
     "tier_score"),
]


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=15, autocommit=True, charset="utf8mb4")
    cur = c.cursor()
    cur.execute("""SELECT column_name FROM information_schema.columns
                   WHERE table_schema=%s AND table_name='trader_rating'""", (DB,))
    have = {r[0] for r in cur.fetchall()}
    for clause, name in ALTERS:
        if name in have:
            print(f"  exists {name}")
            continue
        try:
            cur.execute("ALTER TABLE trader_rating " + clause)
            print(f"  ADDED  {name}")
        except Exception as e:
            print(f"  FAIL   {name}: {str(e)[:90]}")

    cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                (None, "SCHEMA_V5",
                 "trader_rating += loss_rate_upper, expectancy_worst_bps, tier, tier_score "
                 "(adopted from Kilo's survival-stress rating vector)"))
    cur.execute("""SELECT column_name, column_type FROM information_schema.columns
                   WHERE table_schema=%s AND table_name='trader_rating'
                     AND column_name IN ('loss_rate_upper','expectancy_worst_bps','tier','tier_score')
                   ORDER BY column_name""", (DB,))
    print("\ntrader_rating stress columns:")
    for r in cur.fetchall():
        print(f"   {r[0]:22} {r[1]}")
    c.close()


if __name__ == "__main__":
    main()
