-- benchmark legs + 3x round-trip cost gate — reference SQL.
-- Needed so every forward pod card can show excess vs matched exposure and so emission is
-- blocked for classes whose average PnL cannot clear 3x their measured slippage.

-- 1. Benchmark reference table (matched-exposure legs per class)
CREATE TABLE IF NOT EXISTS benchmark_legs (
    class          VARCHAR(32) NOT NULL,
    benchmark       VARCHAR(16) NOT NULL,
    PRIMARY KEY (class)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO benchmark_legs (class, benchmark) VALUES
  ('CRYPTO','BTC-USD'), ('EQUITY','SPY'), ('ETF','SPY'),
  ('BOND','AGG'), ('COMMODITY','GSG'), ('FUTURES','GSG'),
  ('FOREX','DXY'), ('MUTUAL_FUND','SPY'), ('MEME','BTC-USD'), ('PENNY_STOCK','SPY');

-- 2. Per-class measured slippage as % of avg PnL (from slippage_validation).
--    A class fails the cost gate when slippage share >= 1/3 (i.e. avg PnL < 3x cost).
CREATE TABLE IF NOT EXISTS class_cost_gate (
    class               VARCHAR(32) NOT NULL PRIMARY KEY,
    measured_slippage_pct DECIMAL(10,4) NOT NULL,
    avg_pnl_pct         DECIMAL(10,4) NOT NULL,
    slippage_share_of_pnl DECIMAL(10,4) AS (measured_slippage_pct / NULLIF(avg_pnl_pct,0)) STORED,
    gate_pass           TINYINT(1) AS (avg_pnl_pct >= 3*measured_slippage_pct) STORED
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate from a fresh payload read of slippage_validation.asset_class_stats (illustrative):
-- INSERT IGNORE INTO class_cost_gate (class, measured_slippage_pct, avg_pnl_pct) VALUES
--   ('CRYPTO',0.0997,0.268),   -- share 37% -> gate_pass 1 (< 33%? NO -> 37% is > 33% => block)
--   ('ETF',0.05,0.021),        -- share 234% -> block
--   ('FUTURES',0.15,-0.199),   -- negative avg -> block
--   ('EQUITY',0.05,-0.373),    -- negative avg -> block (equity daily still marginal)
--   ('BOND',0.05,-0.189),      -- block
--   ('COMMODITY',0.15,-1.112), -- block
--   ('FOREX',0.02,-0.225);     -- block

-- 3. Emission gate: block any pick whose class does not pass the 3x cost gate.
--    Wire this into the emitter as a hard pre-emit filter (mirror money_ready_verdict).
-- SELECT p.* FROM picks p JOIN class_cost_gate g USING(class) WHERE g.gate_pass = 1;
