"""Schema v4 — trader/analyst attribution split by risk profile.

The rating problem: a 97.6% hit-rate 1-week BTC trader and a 49.4% win-rate trader with large P/L
are different products, not better and worse. Averaging them into one score produces a number that
ranks the wrong profile first. So the rating is keyed on (trader, asset_class, horizon) and carries
five separate dimensions, with the risk profile as its own table rather than a label in a comment.

Kept separate from analyst_registry/analyst_actions (sell-side, named, paid) because a leaderboard
trader has different biases: self-selection and survivorship rather than coverage termination.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS risk_profile (
      code        VARCHAR(32) NOT NULL,
      label       VARCHAR(80) NOT NULL,
      description TEXT        NOT NULL,
      primary_failure VARCHAR(120) NOT NULL COMMENT 'how this profile loses money',
      PRIMARY KEY (code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS trader (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      source_type   VARCHAR(24) NOT NULL
                    COMMENT 'leaderboard|onchain|sell_side|13f|insider|prediction',
      source        VARCHAR(48) NOT NULL COMMENT 'hyperliquid|dydx|bybit|benzinga|sec_13f|kalshi',
      external_id   VARCHAR(120) NOT NULL COMMENT 'venue wallet, analyst id, CIK',
      display_name  VARCHAR(120) NULL,
      firm          VARCHAR(80)  NULL,
      survivorship_flag TINYINT(1) NOT NULL DEFAULT 0
                    COMMENT '1 = history only exists because they are currently winning',
      first_seen    DATE NULL,
      last_seen     DATE NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_trader (source, external_id),
      KEY idx_trader_type (source_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS trader_action (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      trader_id     BIGINT UNSIGNED NOT NULL,
      symbol        VARCHAR(32) NOT NULL,
      asset_class   VARCHAR(24) NOT NULL,
      side          VARCHAR(8)  NOT NULL COMMENT 'long|short',
      entry_ts      DATETIME    NOT NULL,
      entry_price   DECIMAL(20,6) NULL,
      exit_ts       DATETIME    NULL,
      exit_price    DECIMAL(20,6) NULL,
      hold_seconds  BIGINT      NULL COMMENT 'derived; drives horizon bucketing',
      size          DECIMAL(20,6) NULL,
      fees_bps      DECIMAL(8,2) NULL,
      disclosed_at  DATETIME    NULL COMMENT '13F: when it hit the wire, not when traded',
      source_url    VARCHAR(400) NULL,
      retrieved_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
      dedupe_key    VARCHAR(190) GENERATED ALWAYS AS
                    (CONCAT_WS('|', trader_id, symbol, entry_ts, side)) STORED,
      PRIMARY KEY (id),
      UNIQUE KEY uq_action (dedupe_key),
      KEY idx_ta_trader (trader_id, entry_ts),
      KEY idx_ta_class (asset_class),
      CONSTRAINT fk_ta_trader FOREIGN KEY (trader_id) REFERENCES trader(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS trader_rating (
      id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      trader_id             BIGINT UNSIGNED NOT NULL,
      asset_class           VARCHAR(24) NOT NULL,
      horizon               VARCHAR(16) NOT NULL
                            COMMENT 'intraday|<1d|short|1d-1w|swing|1w-1m|position|1m-3m|long|>3m',
      n                     INT NOT NULL,
      -- dimension 1: reliability
      hit_rate              DECIMAL(6,4) NULL,
      hit_ci_lo             DECIMAL(6,4) NULL,
      hit_ci_hi             DECIMAL(6,4) NULL,
      -- dimension 2: magnitude
      expectancy_bps        DECIMAL(12,2) NULL,
      median_bps            DECIMAL(12,2) NULL,
      profit_factor         DECIMAL(10,4) NULL,
      payoff_ratio          DECIMAL(10,4) NULL COMMENT 'avg win / avg loss',
      -- dimension 3: skew and tail
      worst_trade_bps       DECIMAL(12,2) NULL,
      cvar_5pct_bps         DECIMAL(12,2) NULL,
      max_drawdown_pct      DECIMAL(10,4) NULL,
      longest_loss_streak   INT NULL,
      tail_ratio            DECIMAL(10,4) NULL,
      top3_dependency_pct   DECIMAL(6,2) NULL COMMENT 'share of total P/L from best 3 trades; >60 is a red flag',
      -- dimension 4: stability
      periods_tested        INT NULL,
      periods_same_sign     INT NULL,
      regime_split          VARCHAR(120) NULL,
      -- dimension 5: sample power and correction
      trials_screened       INT NULL COMMENT 'candidates ranked to find this one; the DSR penalty input',
      dsr                   DECIMAL(8,4) NULL,
      bh_significant        TINYINT(1) NULL,
      -- verdict
      profile_code          VARCHAR(32) NOT NULL DEFAULT 'UNCLASSIFIED',
      badge                 VARCHAR(24) NOT NULL DEFAULT 'INSUFFICIENT_DATA'
                            COMMENT 'A|B|C|INSUFFICIENT_DATA - gated on n AND significance',
      computed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      UNIQUE KEY uq_rating (trader_id, asset_class, horizon),
      KEY idx_rating_badge (badge),
      CONSTRAINT fk_tr_trader FOREIGN KEY (trader_id) REFERENCES trader(id) ON DELETE CASCADE,
      CONSTRAINT fk_tr_profile FOREIGN KEY (profile_code) REFERENCES risk_profile(code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]

PROFILES = [
    ("HIGH_RELIABILITY_NEG_SKEW",
     "High hit rate, small wins, negative skew",
     "Most trades win but wins are small relative to losses. Typically mean-reversion or premium "
     "selling. A 97.6% hit rate on 1-week BTC calls looks flawless until the single tail trade "
     "removes months of gains.",
     "one tail event; the loss is many multiples of the average win"),
    ("LOW_RELIABILITY_POS_SKEW",
     "Low hit rate, large wins, positive skew",
     "Fewer winning trades but wins are much larger than losses. At a 49.4% hit rate the payoff "
     "ratio must exceed roughly 2.1 for expectancy to be positive. Records of this shape often "
     "depend on a handful of trades.",
     "patience; the record collapses if the top 3 trades are removed"),
    ("BALANCED",
     "Hit rate and payoff roughly symmetric",
     "Neither tail dominates. The most robust shape, and the easiest to shrink toward the universe "
     "mean when n is small.",
     "being unremarkable; small n hides whether the edge is real"),
    ("UNCLASSIFIED",
     "Not enough data to classify",
     "Assigned by default. Never rendered as a rating.",
     "being mistaken for a rating"),
]


def main():
    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
        for code, label, desc, failure in PROFILES:
            cur.execute("INSERT IGNORE INTO risk_profile (code, label, description, primary_failure) "
                        "VALUES (%s,%s,%s,%s)", (code, label, desc, failure))
        cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                    (None, "SCHEMA_V4",
                     "trader, trader_action, trader_rating (5 dimensions, keyed on class+horizon), "
                     "risk_profile with 4 seeded profiles"))
        cur.execute("SELECT code, label FROM risk_profile ORDER BY code")
        print("risk profiles:", cur.fetchall())
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema=%s
                       AND table_name IN ('trader','trader_action','trader_rating','risk_profile')
                       ORDER BY 1""", (DB,))
        print("ensured:", [r[0] for r in cur.fetchall()])
    conn.close()


if __name__ == "__main__":
    main()
