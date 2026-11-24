-- Data-quality checks for ejaguiar1_stocks pick tracking (SQLite/Postgres-friendly).
-- Convention: tables picks, outcomes, prices, consensus_snapshots, analyst_performance,
-- crowd_snapshots, ingest_runs. Every check is read-only and returns offending rows.

-- 1) Feed staleness: newest pick older than 2 hours (crypto) / 30 hours (others)
SELECT 'STALE_FEED' AS check_name, asset_class,
       MAX(COALESCE(closed_at, opened_at)) AS newest,
       ROUND((julianday('now') - julianday(MAX(COALESCE(closed_at, opened_at)))) * 24, 1) AS age_hours
FROM picks
GROUP BY asset_class
HAVING age_hours > CASE WHEN asset_class='CRYPTO' THEN 2 ELSE 30 END;

-- 2) Active pick with P/L exactly 0 and older than 7 days (stuck resolver)
SELECT 'OPEN_ZERO_PNL_AGED', pick_id, symbol, opened_at, pnl_pct
FROM picks
WHERE status='OPEN' AND COALESCE(pnl_pct,0)=0
  AND opened_at < datetime('now','-7 day');

-- 3) Closed pick with P/L exactly 0 (time exit but no P/L written)
SELECT 'CLOSED_ZERO_PNL', pick_id, symbol, closed_at, exit_px, exit_reason
FROM picks
WHERE status IN ('CLOSED','WON','LOST') AND COALESCE(pnl_pct,0)=0;

-- 4) Closed without exit price, or open with an exit price
SELECT 'STATUS_INCONSISTENT', pick_id, status, closed_at, exit_px
FROM picks
WHERE (status IN ('CLOSED','WON','LOST') AND exit_px IS NULL)
   OR (status='OPEN' AND (exit_px IS NOT NULL OR closed_at IS NOT NULL));

-- 5) TP/SL on the wrong side of entry
SELECT 'TPSL_WRONG_SIDE', pick_id, symbol, direction, entry_px, take_profit, stop_loss
FROM picks
WHERE entry_px > 0
  AND ((direction='LONG'  AND NOT (take_profit > entry_px AND stop_loss < entry_px))
    OR (direction='SHORT' AND NOT (take_profit < entry_px AND stop_loss > entry_px)));

-- 6) Duplicate pick ids and duplicate natural keys
SELECT 'DUP_PICK_ID', pick_id, COUNT(*) c FROM picks GROUP BY pick_id HAVING c > 1;
SELECT 'DUP_NATURAL', symbol, direction, opened_at, COUNT(*) c
FROM picks GROUP BY symbol, direction, opened_at HAVING c > 1;

-- 7) Non-positive prices and absurd P/L
SELECT 'BAD_PRICE', pick_id, entry_px, exit_px FROM picks
WHERE entry_px <= 0 OR (exit_px IS NOT NULL AND exit_px <= 0);
SELECT 'PNL_OUTLIER', pick_id, symbol, pnl_pct FROM picks
WHERE ABS(pnl_pct) > 100;

-- 8) Unresolved past horizon (open older than 30 days)
SELECT 'UNRESOLVED_PAST_HORIZON', pick_id, symbol, opened_at
FROM picks WHERE status='OPEN' AND opened_at < datetime('now','-30 day');

-- 9) Outcomes without a pick, or a pick with two outcomes for the same horizon
SELECT 'ORPHAN_OUTCOME', o.pick_id FROM outcomes o
LEFT JOIN picks p ON p.pick_id=o.pick_id WHERE p.pick_id IS NULL;
SELECT 'DUP_OUTCOME', pick_id, horizon_days, COUNT(*) c
FROM outcomes GROUP BY pick_id, horizon_days HAVING c > 1;

-- 10) Consensus arithmetic: counts must equal n and score must match
SELECT 'CONSENSUS_BAD_N', instrument_id, period
FROM consensus_snapshots WHERE sb+b+h+s+ss <> n;
SELECT 'CONSENSUS_BAD_SCORE', instrument_id, period
FROM consensus_snapshots
WHERE ABS((2.0*sb + b - s - 2.0*ss)/NULLIF(n,0) - score) > 0.002;

-- 11) Analyst bridge emptiness: HARVEST rows but no per-firm actions
SELECT 'ANALYST_BRIDGE_EMPTY', r.c AS recommendation_rows, c.c AS consensus_rows
FROM (SELECT COUNT(*) c FROM recommendations) r,
     (SELECT COUNT(*) c FROM consensus_snapshots) c
WHERE r.c = 0 AND c.c > 0;

-- 12) Analyst performance with n but no underlying recommendations
SELECT 'PERF_WITHOUT_RECS', ap.entity_id, ap.n_calls
FROM analyst_performance ap
LEFT JOIN recommendations r ON r.entity_id = ap.entity_id
GROUP BY ap.entity_id, ap.n_calls HAVING COUNT(r.rec_id) = 0;

-- 13) Crowd market snapshots stale (> 24h) or probability outside [0,1]
SELECT 'CROWD_STALE', market_id, MAX(ts) newest
FROM crowd_snapshots GROUP BY market_id
HAVING julianday('now') - julianday(MAX(ts)) > 1;
SELECT 'CROWD_BAD_PROB', market_id, ts, implied_prob
FROM crowd_snapshots WHERE implied_prob < 0 OR implied_prob > 1;

-- 14) Ingest failures / silent sources
SELECT 'INGEST_FAILED', source_id, started, status, http, error
FROM ingest_runs WHERE status <> 'ok' OR error IS NOT NULL;

-- 15) Coverage ratio: share of closed picks excluded from headline
SELECT 'COVERAGE_LOW',
       SUM(CASE WHEN integrity_excluded=1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS excluded_share
FROM picks WHERE status IN ('CLOSED','WON','LOST')
HAVING excluded_share > 0.30;
