-- forward_observations — the missing system-of-record table.
-- This is the reference schema to append to the source MySQL database (ejaguiar1_stocks)
-- so the forward ledger can be fed and audit3's PROVEN_T2 becomes reachable.
-- Columns mirror alpha_engine/forward_observations.py requirements + the schema spec §8.

CREATE TABLE IF NOT EXISTS forward_observations (
    id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- hypothesis pod identity (FK to hypothesis_registry)
    hypothesis_id      VARCHAR(128) NOT NULL,
    pod_id             VARCHAR(128) DEFAULT NULL,

    -- trade context
    opened_at          DATETIME NOT NULL,
    closed_at          DATETIME NOT NULL,
    symbol             VARCHAR(32)  NOT NULL,
    class              VARCHAR(32)  NOT NULL,
    side               ENUM('LONG','SHORT') NOT NULL,
    strategy           VARCHAR(128) NOT NULL,

    -- fills & costs (net return definition)
    entry_px           DECIMAL(18,8) NOT NULL,
    exit_px            DECIMAL(18,8) NOT NULL,
    qty                DECIMAL(24,8) NOT NULL DEFAULT 1,
    fees               DECIMAL(18,8) NOT NULL DEFAULT 0,
    funding            DECIMAL(18,8) NOT NULL DEFAULT 0,
    slippage_bps       DECIMAL(10,4) NOT NULL DEFAULT 0,

    -- resolver semantics (honesty gates)
    resolver_version    VARCHAR(64) NOT NULL,
    intrabar_first_touch TINYINT(1) NOT NULL DEFAULT 0,
    exit_rule           ENUM('TP','SL','TIME','VOL_TRAIL','BENCH') NOT NULL,

    -- benchmark leg (excess vs matched exposure)
    benchmark_leg_ret   DECIMAL(18,8) DEFAULT NULL,
    benchmark_ticker    VARCHAR(16) DEFAULT NULL,

    -- computed net return constraints
    net_pnl_pct         DECIMAL(18,8) DEFAULT NULL,  -- NOT NULL enforced by trigger/app

    -- regime + provenance
    regime_ok           TINYINT(1) DEFAULT 1,
    source_sha256       CHAR(64) DEFAULT NULL,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_fwd_dedup (hypothesis_id, symbol, strategy, side, opened_at, closed_at, resolver_version),
    KEY ix_fwd_hyp (hypothesis_id, closed_at),
    KEY ix_fwd_class (class, closed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Integrity: net return must be present on resolved rows (mirror the "pnl_pct NOT NULL" rule)
-- DELIMITER //
-- CREATE TRIGGER tg_fwd_net_notnull BEFORE INSERT ON forward_observations
-- FOR EACH ROW
-- BEGIN
--   IF NEW.net_pnl_pct IS NULL THEN
--     SIGNAL SQLSTATE '45000'
--       SET MESSAGE_TEXT = 'forward_observations.net_pnl_pct must not be NULL on resolved rows';
--   END IF;
-- END//
-- DELIMITER ;
