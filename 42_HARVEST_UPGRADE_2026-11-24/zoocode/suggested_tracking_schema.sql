-- Suggested tracking schema for the fleet picks DB. Hermes owns the real DB;
-- this is my recommendation (zoo-savant, 2026-11-24), meant to be reviewed, not applied blind.
--
-- Design rules:
--   * one row per OBSERVATION, never one row per current state -- history is the asset
--   * every table carries source + observed_at, so a number can always be traced back
--   * gaps are ROWS with a status, never missing rows: "no analyst covers this ETF"
--     and "our key got a 403" must stay distinguishable forever
--   * nothing is deleted; corrections are new rows that supersede old ones
--   * post-hoc analysis tables (performance) are DERIVED and recomputable

-- ---------------------------------------------------------------------------
-- A. OUR OWN PICKS: /audit, /audit2, /audit3 and the AI tournament
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pick_source (
  source_id    TEXT PRIMARY KEY,          -- 'audit', 'audit2', 'audit3', 'ai_challenge_antigravity', 'harvest'
  surface      TEXT NOT NULL,            -- public URL or repo path that publishes it
  description  TEXT,
  first_seen   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pick (
  pick_id       TEXT PRIMARY KEY,        -- stable across re-publication
  source_id     TEXT NOT NULL REFERENCES pick_source(source_id),
  agent         TEXT,                   -- emitting system/agent/model
  symbol        TEXT NOT NULL,
  asset_class   TEXT NOT NULL,
  direction     TEXT NOT NULL CHECK (direction IN ('LONG','SHORT','FLAT')),
  signal_type   TEXT,
  strategy      TEXT,
  entry_price   REAL, take_profit REAL, stop_loss REAL,
  confidence    REAL,                   -- 0..1, exactly as emitted
  score         REAL,                   -- the system's own score, not normalised
  generated_at  TEXT NOT NULL,
  UNIQUE (source_id, symbol, generated_at, agent)
);

-- Appended every time a pick's state is re-read; the latest row per pick is the state.
CREATE TABLE IF NOT EXISTS pick_observation (
  obs_id          INTEGER PRIMARY KEY,
  pick_id         TEXT NOT NULL REFERENCES pick(pick_id),
  observed_at     TEXT NOT NULL,
  status          TEXT NOT NULL CHECK (status IN ('OPEN','CLOSED','EXPIRED','CANCELLED')),
  outcome         TEXT,                 -- 'WIN','LOSS','BREAKEVEN','PENDING', as the source says
  mark_price      REAL,
  pnl_pct         REAL,                 -- as reported by the source
  pnl_pct_net     REAL,                 -- recomputed by us, after COST_OF_RECORD
  exit_reason     TEXT,
  raw_json        TEXT,
  UNIQUE (pick_id, observed_at)
);

-- Every backtest/forward metric a surface claims, with its scope. A metric without
-- a scope is the classic way a number ends up meaning two things at once.
CREATE TABLE IF NOT EXISTS pick_metric (
  metric_id   INTEGER PRIMARY KEY,
  pick_id     TEXT,                     -- NULL = aggregate over a group
  scope       TEXT NOT NULL CHECK (scope IN ('pick','strategy','class','system','overall','is','oos','forward')),
  metric_name TEXT NOT NULL,            -- 'sharpe', 'wr_pct', 'pf', 'n_trades', 'max_dd_pct'
  value       REAL,                    -- NULL allowed: unmeasurable is not zero
  n           INTEGER,
  ci_low      REAL, ci_high REAL,
  source_id   TEXT REFERENCES pick_source(source_id),
  observed_at TEXT NOT NULL,
  UNIQUE (pick_id, scope, metric_name, observed_at)
);

-- ---------------------------------------------------------------------------
-- B. HARVEST: analyst consensus and dated actions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instrument (
  instrument_id TEXT PRIMARY KEY,       -- the symbol as the source spells it
  symbol        TEXT NOT NULL,
  name          TEXT,
  asset_class   TEXT NOT NULL,           -- STOCK, ETF, BOND, MUTUAL_FUND, CRYPTO, FOREX, FUTURES, OPTION
  instrument_type TEXT,                 -- 'common stock', 'etf', 'bond fund', 'perp', ...
  exchange      TEXT,
  venue         TEXT,                   -- 'Kalshi', 'Polymarket', 'Yahoo', ...
  currency      TEXT,
  underlying_id TEXT REFERENCES instrument(instrument_id),   -- an ETF's index, a future's spot
  tags          TEXT,                   -- csv: 'penny','meme','leveraged','OTC'
  first_seen    TEXT NOT NULL
);

-- Consensus snapshots (the page's current table). Monthly, one row per period.
CREATE TABLE IF NOT EXISTS analyst_consensus (
  consensus_id  INTEGER PRIMARY KEY,
  instrument_id TEXT NOT NULL REFERENCES instrument(instrument_id),
  period        TEXT NOT NULL,          -- '2026-11-01'
  n_analysts    INTEGER NOT NULL,
  strong_buy INTEGER, buy INTEGER, hold INTEGER, sell INTEGER, strong_sell INTEGER,
  score         REAL,                   -- (2*SB + B - S - 2*SS)/n
  buy_share     REAL,                   -- (SB + B)/n
  label         TEXT,                   -- what the SOURCE says
  label_derived TEXT,                   -- what the RULE says -- store both, compare in a test
  source_id     TEXT NOT NULL,
  fetched_at    TEXT NOT NULL,
  UNIQUE (instrument_id, period, source_id)
);

-- Dated per-firm actions. `firm` is the finest identity any free source gives:
-- Yahoo's upgradeDowngradeHistory returns firm, fromGrade, toGrade, action,
-- priceTargetAction, currentPriceTarget, priorPriceTarget -- and NO analyst name.
CREATE TABLE IF NOT EXISTS analyst_action (
  action_id       INTEGER PRIMARY KEY,
  instrument_id   TEXT NOT NULL REFERENCES instrument(instrument_id),
  action_date     TEXT NOT NULL,        -- date only: the source gives a timestamp, the market gives a close
  firm            TEXT NOT NULL,
  analyst_name    TEXT,                 -- NULL when the source does not name one (almost always)
  analyst_id      TEXT,                 -- FK to analyst, when resolvable
  from_grade      TEXT, to_grade TEXT,
  action          TEXT,                 -- 'up','down','main','reit','init'
  pt_action       TEXT,                 -- 'Raises','Lowers','Announces',...
  price_target    REAL, pt_prior REAL,
  source_id       TEXT NOT NULL,
  fetched_at      TEXT NOT NULL
);
-- NOT an inline UNIQUE: SQLite (and Postgres) treat NULLs as DISTINCT in a UNIQUE
-- constraint, so a row with a NULL price_target would be stored twice. Verified by
-- test: the inline version accepted a duplicate. COALESCE closes that hole.
CREATE UNIQUE INDEX IF NOT EXISTS ux_analyst_action
  ON analyst_action (instrument_id, firm, action_date,
                     COALESCE(from_grade,''), COALESCE(to_grade,''),
                     COALESCE(price_target,-1));

-- One row per firm (and per named analyst when a source ever provides one).
CREATE TABLE IF NOT EXISTS analyst (
  analyst_id  TEXT PRIMARY KEY,
  firm        TEXT NOT NULL,
  name        TEXT,                     -- NULL: no free source names individuals
  source_id   TEXT,
  first_seen  TEXT NOT NULL,
  UNIQUE (firm, name)
);

-- ---------------------------------------------------------------------------
-- C. CROWD / PREDICTION MARKETS (Kalshi, Polymarket)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crowd_market (
  market_id      TEXT PRIMARY KEY,       -- venue:ticker or venue:questionID
  venue          TEXT NOT NULL,          -- 'kalshi' | 'polymarket'
  title          TEXT NOT NULL,
  resolution_criteria TEXT,             -- must be stored: a mapped market without its criteria is a trap
  category       TEXT,
  opens_at TEXT, closes_at TEXT,
  status         TEXT
);

CREATE TABLE IF NOT EXISTS crowd_quote (
  quote_id     INTEGER PRIMARY KEY,
  market_id    TEXT NOT NULL REFERENCES crowd_market(market_id),
  observed_at  TEXT NOT NULL,
  yes_price    REAL,                    -- implied probability
  yes_bid REAL, yes_ask REAL, no_bid REAL, no_ask REAL,
  volume       REAL, open_interest REAL, liquidity REAL,
  UNIQUE (market_id, observed_at)
);

-- Explicit, reviewable symbol<->market links. NEVER fuzzy-match titles at runtime:
-- the mapping is a judgement call and has to be auditable.
CREATE TABLE IF NOT EXISTS crowd_market_link (
  link_id        INTEGER PRIMARY KEY,
  market_id      TEXT NOT NULL REFERENCES crowd_market(market_id),
  instrument_id  TEXT REFERENCES instrument(instrument_id),
  asset_class    TEXT,                  -- for macro markets that map to a class, not a symbol
  confidence     REAL,                  -- 0..1
  rationale      TEXT NOT NULL,
  linked_by      TEXT NOT NULL,
  linked_at      TEXT NOT NULL,
  UNIQUE (market_id, instrument_id, asset_class)
);

-- ---------------------------------------------------------------------------
-- D. SOURCE HEALTH: the table that keeps "no coverage" honest
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS source_status (
  status_id   INTEGER PRIMARY KEY,
  source_id   TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('OK','NOT_APPLICABLE','PLAN_LIMITED','SOURCE_ERROR','STALE','RATE_LIMITED')),
  http_code   INTEGER,
  rows        INTEGER,
  message     TEXT,
  UNIQUE (source_id, observed_at)
);

-- ---------------------------------------------------------------------------
-- E. DERIVED: recomputable, never hand-edited
-- ---------------------------------------------------------------------------
-- Forward outcome of an analyst action, one row per horizon.
CREATE TABLE IF NOT EXISTS analyst_action_outcome (
  action_id        INTEGER NOT NULL REFERENCES analyst_action(action_id),
  horizon_days     INTEGER NOT NULL,     -- 21, 63, 126
  entry_px         REAL, exit_px REAL,   -- entry = next open after action_date
  ret_pct          REAL,
  benchmark_ret_pct REAL,                -- same window, same class benchmark (SPY for equity)
  excess_pct       REAL,
  computed_at      TEXT NOT NULL,
  PRIMARY KEY (action_id, horizon_days)
);

-- Firm-level scorecard: what "high-performing analyst" means, with its uncertainty.
CREATE TABLE IF NOT EXISTS analyst_scorecard (
  scorecard_id   INTEGER PRIMARY KEY,
  firm           TEXT NOT NULL,
  horizon_days   INTEGER NOT NULL,
  window_start   TEXT NOT NULL, window_end TEXT NOT NULL,
  n_calls        INTEGER NOT NULL,
  hit_rate       REAL,
  mean_excess_pct REAL,
  ci_low         REAL, ci_high REAL,
  suppressed     INTEGER NOT NULL DEFAULT 0,   -- 1 when n < 30: shown as "insufficient", not ranked
  computed_at    TEXT NOT NULL,
  UNIQUE (firm, horizon_days, window_start, window_end)
);
