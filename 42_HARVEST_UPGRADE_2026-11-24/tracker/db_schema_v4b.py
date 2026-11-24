"""v4b: create trader_action and trader_rating WITHOUT inline FKs, then add each constraint
separately so a failure names itself instead of aborting the whole batch.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS trader_action (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      trader_id     BIGINT UNSIGNED NOT NULL,
      symbol        VARCHAR(32) NOT NULL,
      asset_class   VARCHAR(24) NOT NULL,
      side          VARCHAR(8)  NOT NULL,
      entry_ts      DATETIME    NOT NULL,
      entry_price   DECIMAL(20,6) NULL,
      exit_ts       DATETIME    NULL,
      exit_price    DECIMAL(20,6) NULL,
      hold_seconds  BIGINT      NULL,
      size          DECIMAL(20,6) NULL,
      fees_bps      DECIMAL(8,2) NULL,
      disclosed_at  DATETIME    NULL,
      source_url    VARCHAR(400) NULL,
      retrieved_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
      dedupe_key    VARCHAR(190) GENERATED ALWAYS AS
                    (CONCAT_WS('|', trader_id, symbol, entry_ts, side)) STORED,
      PRIMARY KEY (id),
      UNIQUE KEY uq_ta_action (dedupe_key),
      KEY idx_ta_trader (trader_id, entry_ts),
      KEY idx_ta_class (asset_class)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS trader_rating (
      id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      trader_id             BIGINT UNSIGNED NOT NULL,
      asset_class           VARCHAR(24) NOT NULL,
      horizon               VARCHAR(16) NOT NULL COMMENT 'intraday|short|swing|position|long',
      pick_type             VARCHAR(24) NOT NULL DEFAULT 'UNCLASSIFIED'
                            COMMENT 'DAY_TRADE|SWING_TRADE|POSITION|LONG_TERM|BUY_AND_HOLD',
      n                     INT NOT NULL,
      hit_rate              DECIMAL(6,4) NULL,
      hit_ci_lo             DECIMAL(6,4) NULL,
      hit_ci_hi             DECIMAL(6,4) NULL,
      expectancy_bps        DECIMAL(12,2) NULL,
      median_bps            DECIMAL(12,2) NULL,
      profit_factor         DECIMAL(10,4) NULL,
      payoff_ratio          DECIMAL(10,4) NULL,
      worst_trade_bps       DECIMAL(12,2) NULL,
      cvar_5pct_bps         DECIMAL(12,2) NULL,
      max_drawdown_pct      DECIMAL(10,4) NULL,
      longest_loss_streak   INT NULL,
      tail_ratio            DECIMAL(10,4) NULL,
      top3_dependency_pct   DECIMAL(6,2) NULL,
      periods_tested        INT NULL,
      periods_same_sign     INT NULL,
      regime_split          VARCHAR(120) NULL,
      trials_screened       INT NULL,
      dsr                   DECIMAL(8,4) NULL,
      bh_significant        TINYINT(1) NULL,
      profile_code          VARCHAR(32) NOT NULL DEFAULT 'UNCLASSIFIED',
      badge                 VARCHAR(24) NOT NULL DEFAULT 'INSUFFICIENT_DATA',
      computed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      UNIQUE KEY uq_tr_rating (trader_id, asset_class, horizon),
      KEY idx_tr_badge (badge)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS pick_type_ref (
      code        VARCHAR(24) NOT NULL,
      label       VARCHAR(60) NOT NULL,
      typical_hold VARCHAR(40) NOT NULL,
      horizon_bucket VARCHAR(16) NOT NULL,
      min_n       INT NOT NULL,
      description TEXT NOT NULL,
      PRIMARY KEY (code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]

PICK_TYPES = [
    ("DAY_TRADE", "Day trade", "minutes to hours, closed same session", "intraday", 100,
     "No overnight risk. Edge depends on microstructure and execution; costs dominate, so fees "
     "must be measured, never assumed."),
    ("SWING_TRADE", "Swing trade", "1 day to 2 weeks", "short", 60,
     "The 97.6%-hit-rate BTCUSDT profile lives here. High hit rate with small wins implies "
     "negative skew: one tail trade can erase the streak, so worst-trade and CVaR are mandatory."),
    ("POSITION", "Position trade", "2 weeks to 3 months", "swing", 40,
     "Earnings/events fit here. Requires checking results against sector, not just index."),
    ("LONG_TERM", "Long-term", "3 months to 2 years", "long", 20,
     "Fewer independent observations per year, so n accumulates slowly and a 2-year record can "
     "still be INSUFFICIENT_DATA."),
    ("BUY_AND_HOLD", "Buy and hold", "years, no defined exit", "long", 10,
     "Not really a pick: almost every sample is one regime. Treat as a vehicle decision with a "
     "cost comparison, not as skill."),
    ("UNCLASSIFIED", "Unclassified", "unknown", "swing", 999999,
     "Default. Never rendered as a rating."),
]

FKS = [
    ("trader_action", "fk_ta_trader",
     "FOREIGN KEY (trader_id) REFERENCES trader(id) ON DELETE CASCADE"),
    ("trader_rating", "fk_tr_trader",
     "FOREIGN KEY (trader_id) REFERENCES trader(id) ON DELETE CASCADE"),
    ("trader_rating", "fk_tr_profile",
     "FOREIGN KEY (profile_code) REFERENCES risk_profile(code)"),
    ("trader_rating", "fk_tr_picktype",
     "FOREIGN KEY (pick_type) REFERENCES pick_type_ref(code)"),
]


def main():
    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    cur = conn.cursor()
    for stmt in TABLES:
        cur.execute(stmt)
    for row in PICK_TYPES:
        cur.execute("INSERT IGNORE INTO pick_type_ref (code,label,typical_hold,horizon_bucket,min_n,"
                    "description) VALUES (%s,%s,%s,%s,%s,%s)", row)

    for table, name, clause in FKS:
        try:
            cur.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} {clause}")
            print(f"  OK   {name}")
        except Exception as e:
            print(f"  SKIP {name}: {str(e)[:110]}")

    cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                (None, "SCHEMA_V4B", "trader_action, trader_rating, pick_type_ref + 6 pick types"))
    cur.execute("SELECT code, typical_hold, horizon_bucket, min_n FROM pick_type_ref ORDER BY min_n")
    print("\npick types:")
    for r in cur.fetchall():
        print(f"   {r[0]:14} {r[1]:38} bucket={r[2]:9} min_n={r[3]}")
    conn.close()


if __name__ == "__main__":
    main()
