"""Second schema pass: the three data layers the agent feedback proved out.

1. Analyst identity  - the hard dependency. Free consensus is a monthly distribution with NO
   analyst name and NO action date. Tracking a named analyst requires firm-level actions.
2. Fund look-through - derived consensus for funds, with the coverage share stored because a
   derived number without its coverage is meaningless.
3. Crowd layer       - Polymarket/Kalshi markets plus the explicit event -> asset mapping,
   because direct per-symbol matches measured zero out of 300.

Idempotent. Nothing here touches existing tables.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS analyst_registry (
      id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      firm           VARCHAR(80)  NOT NULL,
      analyst_name   VARCHAR(120) NULL COMMENT 'NULL when the vendor gives no name - never invent one',
      asset_class    VARCHAR(24)  NOT NULL DEFAULT 'STOCK',
      first_seen     DATE         NULL,
      last_seen      DATE         NULL,
      n_actions      INT          NOT NULL DEFAULT 0,
      hit_rate       DECIMAL(6,4) NULL,
      hit_rate_lo    DECIMAL(6,4) NULL COMMENT 'Wilson 95 lower',
      hit_rate_hi    DECIMAL(6,4) NULL COMMENT 'Wilson 95 upper',
      shrunk_alpha   DECIMAL(10,5) NULL,
      badge          VARCHAR(24)  NOT NULL DEFAULT 'INSUFFICIENT_DATA'
                     COMMENT 'A|B|C|INSUFFICIENT_DATA - gated on n AND significance',
      updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      UNIQUE KEY uq_analyst (firm, analyst_name, asset_class),
      KEY idx_badge (badge)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS analyst_actions (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      symbol        VARCHAR(24)  NOT NULL,
      firm          VARCHAR(80)  NULL,
      analyst_name  VARCHAR(120) NULL,
      action        VARCHAR(16)  NOT NULL COMMENT 'init|upgrade|downgrade|reiterate|maintain|pt_change',
      rating_from   VARCHAR(24)  NULL,
      rating_to     VARCHAR(24)  NULL,
      pt_from       DECIMAL(14,4) NULL,
      pt_to         DECIMAL(14,4) NULL,
      action_date   DATE         NOT NULL,
      action_time   DATETIME     NULL COMMENT 'UTC; NULL when the vendor gives date only',
      source        VARCHAR(48)  NOT NULL,
      retrieved_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
      dedupe_key    VARCHAR(190) GENERATED ALWAYS AS
                    (CONCAT_WS('|', symbol, COALESCE(firm,''), COALESCE(analyst_name,''),
                               action, action_date)) STORED,
      PRIMARY KEY (id),
      UNIQUE KEY uq_action (dedupe_key),
      KEY idx_action_symbol_date (symbol, action_date),
      KEY idx_action_firm (firm)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS fund_lookthrough (
      id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      fund_symbol         VARCHAR(24) NOT NULL,
      as_of               DATE        NOT NULL,
      holdings_count      INT         NULL,
      matched_count       INT         NULL,
      weight_coverage_pct DECIMAL(6,2) NULL COMMENT 'the informative column - a derived value without it is meaningless',
      derived_buy_side_pct DECIMAL(6,2) NULL,
      derived_score       DECIMAL(10,4) NULL,
      status              VARCHAR(32) NOT NULL
                          COMMENT 'DERIVED_OK|NOT_APPLICABLE_BOND_FUND|BLOCKED_WRONG_SERIES|BLOCKED',
      source_file         VARCHAR(255) NULL,
      method_note         TEXT        NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_lookthrough (fund_symbol, as_of),
      KEY idx_lt_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS crowd_markets (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      venue         VARCHAR(24)  NOT NULL COMMENT 'polymarket|kalshi|forecastex|manifold',
      market_id     VARCHAR(120) NOT NULL,
      title         VARCHAR(400) NULL,
      category      VARCHAR(64)  NULL,
      implied_prob  DECIMAL(8,5) NULL,
      bid           DECIMAL(8,5) NULL,
      ask           DECIMAL(8,5) NULL,
      spread        DECIMAL(8,5) NULL COMMENT 'wide spread = uninformed crowd, show it',
      volume        DECIMAL(20,2) NULL,
      liquidity     DECIMAL(20,2) NULL,
      open_interest DECIMAL(20,2) NULL,
      resolves_at   DATETIME     NULL,
      resolved      TINYINT(1)   NOT NULL DEFAULT 0,
      outcome       TINYINT(1)   NULL,
      fetched_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (id),
      UNIQUE KEY uq_crowd (venue, market_id),
      KEY idx_crowd_cat (category)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS crowd_mappings (
      id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      venue            VARCHAR(24)  NOT NULL,
      market_id        VARCHAR(120) NOT NULL,
      asset_symbol     VARCHAR(24)  NOT NULL,
      layer            VARCHAR(16)  NOT NULL COMMENT 'A_direct|B_event - direct measured 0 of 300, B is the workhorse',
      match_confidence VARCHAR(16)  NOT NULL COMMENT 'exact|ticker_mention|semantic|mechanism',
      mechanism        TEXT         NULL COMMENT 'required for layer B: never publish a bare correlation',
      expected_sign    VARCHAR(16)  NULL COMMENT 'positive|negative|scenario',
      strength         VARCHAR(16)  NULL COMMENT 'high|medium|low',
      historical_beta  DECIMAL(10,5) NULL,
      beta_ci_lo       DECIMAL(10,5) NULL,
      beta_ci_hi       DECIMAL(10,5) NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_map (venue, market_id, asset_symbol),
      KEY idx_map_asset (asset_symbol)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]


def main():
    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema=%s AND table_name IN
                       (%s,%s,%s,%s,%s) ORDER BY 1""",
                    (DB, "analyst_registry", "analyst_actions", "fund_lookthrough",
                     "crowd_markets", "crowd_mappings"))
        names = [r[0] for r in cur.fetchall()]
        cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                    (None, "SCHEMA_V2", "added " + ", ".join(names)))
    conn.close()
    print("ensured:", names)


if __name__ == "__main__":
    main()
