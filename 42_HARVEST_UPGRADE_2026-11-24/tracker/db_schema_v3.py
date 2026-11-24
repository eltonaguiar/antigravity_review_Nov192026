"""Schema v3 — adopt ghcopilot's three load-bearing deltas.

1. source_run       : one row per fetch (endpoint, http status, rows, error). Makes every BLOCKED
                      auditable, instead of burying a 403 in a free-text note.
2. rule_version     : the rule TEXT plus its hash, so a label can always be reproduced from the row
                      that carries label_rule_version. This is the direct fix for the measured
                      defect where the code rule reproduced 71/71 labels and the documented rule
                      only 60/71 on the same published feed.
3. instrument       : identifier crosswalk (symbol/figi/cusip/isin). N-PORT keys positions by CUSIP
                      and QQQ carries a ticker on 1 of 105, so joining on ticker silently returns 0.

Also: price_bar keyed by (instrument, date) with its source run, and pick_resolution as one row
per (pick, horizon) rather than three competing outcome tables.

Additive only. Nothing existing is renamed or dropped.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

DDL = [
    """
    CREATE TABLE IF NOT EXISTS source_run (
      id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      source_system VARCHAR(48) NOT NULL COMMENT 'harvest|finnhub|fmp|ssga|nport|polymarket|kalshi|yfinance',
      endpoint      VARCHAR(400) NULL,
      http_status   INT          NULL,
      rows_returned INT          NULL,
      error_text    TEXT         NULL,
      started_at    DATETIME     NULL,
      finished_at   DATETIME     NULL,
      PRIMARY KEY (id),
      KEY idx_sr_system (source_system, started_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS rule_version (
      rule_hash   CHAR(64)     NOT NULL COMMENT 'sha256 of the normalised rule text',
      rule_text   TEXT         NOT NULL,
      description VARCHAR(255) NULL,
      created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (rule_hash)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS instrument (
      id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      symbol          VARCHAR(32) NOT NULL,
      venue           VARCHAR(24) NOT NULL DEFAULT 'US',
      asset_class     VARCHAR(24) NULL,
      instrument_type VARCHAR(32) NULL COMMENT 'stock|etf|fund|bond|future|fx|crypto|index',
      currency        VARCHAR(8)  NULL,
      figi            VARCHAR(32) NULL,
      cusip           VARCHAR(16) NULL,
      isin            VARCHAR(16) NULL,
      name            VARCHAR(160) NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_instrument (symbol, venue),
      KEY idx_instr_cusip (cusip),
      KEY idx_instr_figi (figi)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS consensus_snapshot (
      id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      instrument_id      BIGINT UNSIGNED NULL,
      symbol_raw         VARCHAR(32) NOT NULL COMMENT 'as the vendor sent it, before crosswalk',
      period             DATE        NOT NULL,
      strong_buy         INT NULL, buy INT NULL, hold INT NULL, sell INT NULL, strong_sell INT NULL,
      analysts           INT NULL,
      share_buy_pct      DECIMAL(6,2) NULL,
      consensus_score    DECIMAL(10,4) NULL,
      consensus_label    VARCHAR(24)  NULL,
      label_rule_version CHAR(64)     NULL COMMENT 'REQUIRED: which rule produced consensus_label',
      source_run_id      BIGINT UNSIGNED NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_snapshot (symbol_raw, period),
      KEY idx_snap_instr (instrument_id, period),
      CONSTRAINT fk_snap_rule FOREIGN KEY (label_rule_version) REFERENCES rule_version(rule_hash)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS price_bar (
      instrument_id BIGINT UNSIGNED NOT NULL,
      d             DATE         NOT NULL,
      open          DECIMAL(20,6) NULL,
      high          DECIMAL(20,6) NULL,
      low           DECIMAL(20,6) NULL,
      close         DECIMAL(20,6) NULL,
      adj_close     DECIMAL(20,6) NULL,
      volume        BIGINT       NULL,
      source_run_id BIGINT UNSIGNED NULL,
      PRIMARY KEY (instrument_id, d)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS pick_resolution (
      id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      pick_id         VARCHAR(80) NOT NULL,
      horizon         VARCHAR(16) NOT NULL COMMENT '1M|3M|6M|12M|to_next_action|open_ended',
      resolved_at     DATETIME    NULL,
      exit_price      DECIMAL(20,6) NULL,
      exit_reason     VARCHAR(48) NULL,
      pnl_abs         DECIMAL(20,6) NULL,
      pnl_bps         DECIMAL(12,2) NULL,
      benchmark_symbol VARCHAR(24) NULL,
      bench_pnl_bps   DECIMAL(12,2) NULL,
      outcome         VARCHAR(16) NULL COMMENT 'win|loss|flat|open',
      PRIMARY KEY (id),
      UNIQUE KEY uq_resolution (pick_id, horizon)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]


def main():
    conn = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                           connect_timeout=15, autocommit=True, charset="utf8mb4")
    with conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)

        # mechanism NOT NULL: schema-level enforcement of "never publish a bare correlation".
        cur.execute("SELECT COUNT(*) FROM crowd_mappings")
        if cur.fetchone()[0] == 0:
            try:
                cur.execute("ALTER TABLE crowd_mappings MODIFY mechanism TEXT NOT NULL")
            except Exception as e:
                print("mechanism NOT NULL skipped:", str(e)[:80])

        # record the rule that is actually in force, so labels are reproducible from their row
        import hashlib
        rule = ("STRONG_BUY if score>=1.0 and buy_side>=0.75; BUY if score>=0.3 and buy_side>=0.50; "
                "STRONG_SELL if score<=-1.0 and buy_side<=0.15; SELL if score<=-0.3 and buy_side<=0.30; "
                "else HOLD. score=(2*strong_buy+buy-sell-2*strong_sell)/analysts; "
                "buy_side=(strong_buy+buy)/analysts")
        h = hashlib.sha256(rule.encode()).hexdigest()
        cur.execute("INSERT IGNORE INTO rule_version (rule_hash, rule_text, description) VALUES (%s,%s,%s)",
                    (h, rule, "harvest two-condition consensus rule, reproduces 71/71 published labels"))
        cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                    (None, "SCHEMA_V3", f"source_run, rule_version, instrument, consensus_snapshot, "
                                        f"price_bar, pick_resolution; rule_hash={h[:12]}"))
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema=%s
                       AND table_name IN ('source_run','rule_version','instrument','consensus_snapshot',
                                          'price_bar','pick_resolution') ORDER BY 1""", (DB,))
        print("ensured:", [r[0] for r in cur.fetchall()])
        print("rule_hash:", h)
    conn.close()


if __name__ == "__main__":
    main()
