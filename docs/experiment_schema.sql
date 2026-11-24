-- Experiment registry: one schema for backtest, paper, live and Monte Carlo.
-- Operator spec, 2026-11-24. Append-only event log; never overwrite orders or fills.
-- SQLite-compatible; port to Postgres by swapping TEXT timestamps for TIMESTAMPTZ.

PRAGMA foreign_keys = ON;

-- One row per experiment / simulation. Nothing is ever deleted from this table.
CREATE TABLE IF NOT EXISTS runs (
    run_id            TEXT PRIMARY KEY,
    run_type          TEXT NOT NULL CHECK (run_type IN ('backtest','paper','live','monte_carlo')),
    parent_run_id     TEXT REFERENCES runs(run_id),   -- set for monte_carlo and re-runs
    strategy_name     TEXT NOT NULL,
    strategy_version  TEXT NOT NULL,
    git_commit        TEXT NOT NULL,                  -- full 40-char sha, never a prefix
    config_hash       TEXT NOT NULL,
    data_snapshot_id  TEXT NOT NULL,                  -- points at a frozen, immutable data file
    seed              INTEGER,
    n_simulations     INTEGER,                        -- monte_carlo only
    start_ts          TEXT NOT NULL,
    end_ts            TEXT NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('running','complete','failed','aborted')),
    env_lockfile_hash TEXT,                           -- requirements.txt / lockfile digest
    container_image   TEXT,
    notes             TEXT
);

-- Full parameterisation. One row per parameter, so runs are diffable without parsing JSON.
CREATE TABLE IF NOT EXISTS run_params (
    run_id      TEXT NOT NULL REFERENCES runs(run_id),
    param_name  TEXT NOT NULL,
    param_value TEXT,
    param_type  TEXT,
    PRIMARY KEY (run_id, param_name)
);

-- Raw / replayed input audit. Optional but required when a claim's realism is disputed.
CREATE TABLE IF NOT EXISTS market_events (
    event_id     TEXT PRIMARY KEY,
    run_id       TEXT NOT NULL REFERENCES runs(run_id),
    ts           TEXT NOT NULL,
    symbol       TEXT NOT NULL,
    event_type   TEXT NOT NULL CHECK (event_type IN ('bar','tick','news','fundamental')),
    payload_json TEXT
);

-- Strategy intent, BEFORE risk management and execution. Kept separate so you can prove
-- that what executed is what the strategy intended, and what the risk layer allowed.
CREATE TABLE IF NOT EXISTS signals (
    signal_id     TEXT PRIMARY KEY,
    run_id        TEXT NOT NULL REFERENCES runs(run_id),
    ts            TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    direction     TEXT CHECK (direction IN ('long','short','flat')),
    strength      REAL,
    target_weight REAL,
    reason        TEXT,
    features_json TEXT
);

-- Order lifecycle, append-only. A status change is a NEW row with a later ts.
CREATE TABLE IF NOT EXISTS orders (
    order_id        TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES runs(run_id),
    parent_signal_id TEXT REFERENCES signals(signal_id),
    ts_created      TEXT NOT NULL,
    symbol          TEXT NOT NULL,
    side            TEXT NOT NULL CHECK (side IN ('buy','sell')),
    qty             REAL NOT NULL,
    order_type      TEXT NOT NULL CHECK (order_type IN ('market','limit','stop','stop_limit')),
    limit_price     REAL,
    stop_price      REAL,
    tif             TEXT CHECK (tif IN ('day','gtc','ioc','fok')),
    status          TEXT NOT NULL,
    reject_reason   TEXT,
    -- latency decomposition, required for day-trading fidelity claims
    ts_submitted    TEXT,
    ts_ack          TEXT
);

-- What actually executed. Never updated, only inserted.
CREATE TABLE IF NOT EXISTS fills (
    fill_id        TEXT PRIMARY KEY,
    run_id         TEXT NOT NULL REFERENCES runs(run_id),
    order_id       TEXT NOT NULL REFERENCES orders(order_id),
    ts_filled      TEXT NOT NULL,
    symbol         TEXT NOT NULL,
    side           TEXT NOT NULL CHECK (side IN ('buy','sell')),
    qty            REAL NOT NULL,
    price          REAL NOT NULL,
    fee            REAL NOT NULL DEFAULT 0,
    slippage       REAL,
    liquidity_flag TEXT CHECK (liquidity_flag IN ('maker','taker','unknown')),
    venue          TEXT
);

-- Position snapshots over time (not deltas).
CREATE TABLE IF NOT EXISTS positions (
    run_id        TEXT NOT NULL REFERENCES runs(run_id),
    ts            TEXT NOT NULL,
    symbol        TEXT NOT NULL,
    qty           REAL NOT NULL,
    avg_price     REAL,
    market_price  REAL,
    unrealized_pnl REAL,
    realized_pnl  REAL,
    exposure      REAL,
    PRIMARY KEY (run_id, ts, symbol)
);

-- Account-level state over time.
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    run_id         TEXT NOT NULL REFERENCES runs(run_id),
    ts             TEXT NOT NULL,
    cash           REAL NOT NULL,
    equity         REAL NOT NULL,
    gross_exposure REAL,
    net_exposure   REAL,
    leverage       REAL,
    margin_used    REAL,
    drawdown       REAL,
    daily_pnl      REAL,
    PRIMARY KEY (run_id, ts)
);

-- Kill switches and limit breaches, with the observed value that tripped them.
CREATE TABLE IF NOT EXISTS risk_events (
    risk_event_id  TEXT PRIMARY KEY,
    run_id         TEXT NOT NULL REFERENCES runs(run_id),
    ts             TEXT NOT NULL,
    type           TEXT NOT NULL,
    threshold      REAL,
    observed_value REAL,
    action_taken   TEXT
);

-- Aggregated metrics. `scope` says whether a number is overall, out-of-sample, per-window
-- or per-regime -- a metric without a scope is not reportable.
CREATE TABLE IF NOT EXISTS metrics (
    run_id      TEXT NOT NULL REFERENCES runs(run_id),
    metric_name TEXT NOT NULL,
    value       REAL,
    scope       TEXT NOT NULL CHECK (scope IN ('overall','oos','window','regime')),
    window_id   TEXT,
    PRIMARY KEY (run_id, metric_name, scope, window_id)
);

-- Every experiment counts, including the failed ones. This is the trial log that makes
-- DSR meaningful: a trial ledger you can edit is not a trial ledger.
CREATE TABLE IF NOT EXISTS trials (
    trial_id     TEXT PRIMARY KEY,
    run_id       TEXT NOT NULL REFERENCES runs(run_id),
    family       TEXT NOT NULL,          -- the hypothesis family this trial belongs to
    variant      TEXT NOT NULL,          -- the specific configuration tried
    sharpe_is    REAL,
    sharpe_oos   REAL,
    kept         INTEGER NOT NULL DEFAULT 0,  -- 1 = this is the selected variant
    ts_logged    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    run_id        TEXT NOT NULL REFERENCES runs(run_id),
    artifact_type TEXT NOT NULL,
    path_or_uri   TEXT NOT NULL,
    checksum      TEXT NOT NULL,         -- sha256 of the artifact as written
    created_ts    TEXT NOT NULL,
    PRIMARY KEY (run_id, artifact_type, path_or_uri)
);

CREATE INDEX IF NOT EXISTS idx_orders_run   ON orders(run_id, ts_created);
CREATE INDEX IF NOT EXISTS idx_fills_run    ON fills(run_id, ts_filled);
CREATE INDEX IF NOT EXISTS idx_metrics_run  ON metrics(run_id, metric_name);
CREATE INDEX IF NOT EXISTS idx_trials_fam   ON trials(family);
