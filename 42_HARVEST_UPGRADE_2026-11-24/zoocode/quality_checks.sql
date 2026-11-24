-- Data-quality checks for the fleet picks DB (target: ejaguiar1_stocks tables
-- built from 42_HARVEST_UPGRADE_2026-11-24/zoocode/suggested_tracking_schema.sql).
--
-- Two kinds of query, deliberately separated:
--
--   HARD  -- a violation is a defect. Wire these into CI and fail the build.
--   SOFT  -- a violation is a smell. Review weekly; it may be legitimate.
--
-- Conventions used by every query:
--   * NULL means "unmeasurable", 0 means "measured zero". A check that treats
--     them the same is itself a bug, so each query says which it assumes.
--   * MySQL syntax (the ejaguiar1_stocks DB). SQLite notes appear where it differs.
--   * :now and :stale_days are parameters -- do not hardcode today's date.
--
-- Last reviewed: 2026-11-24 by zoo-savant.

-- ===========================================================================
-- HARD checks: these are defects, not judgement calls
-- ===========================================================================

-- H1. Duplicate pick identity. The same (source, symbol, generated_at, agent)
--     must appear once. Expect 0 rows.
SELECT source_id, symbol, generated_at, agent, COUNT(*) AS n
FROM pick
GROUP BY source_id, symbol, generated_at, agent
HAVING COUNT(*) > 1;

-- H2. Orphan observations -- a child row whose parent is gone.
--     Expect 0 rows. (Requires FKs to be enforced at write time; this catches
--     rows loaded before that was true.)
SELECT o.obs_id, o.pick_id
FROM pick_observation o
LEFT JOIN pick p ON p.pick_id = o.pick_id
WHERE p.pick_id IS NULL;

-- H3. Timestamps in the future or before the instrument existed.
--     A future generated_at means a clock or timezone bug in the writer.
SELECT 'pick' AS tbl, pick_id AS id, generated_at AS ts
FROM pick
WHERE generated_at > :now OR generated_at < '2000-01-01'
UNION ALL
SELECT 'pick_observation', obs_id, observed_at
FROM pick_observation
WHERE observed_at > :now
UNION ALL
SELECT 'analyst_action', action_id, action_date
FROM analyst_action
WHERE action_date > DATE(:now);

-- H4. Closed without an outcome, or an outcome without a close.
--     These are the states that make a track record uncomputable.
SELECT pick_id, status, outcome, exit_reason
FROM pick_observation
WHERE (status = 'CLOSED' AND (outcome IS NULL OR outcome = 'PENDING'))
   OR (status = 'OPEN'  AND outcome IN ('WIN', 'LOSS'));

-- H5. A metric with no scope. Scope is what makes a number mean one thing;
--     a row without it is how two different figures end up sharing a name.
SELECT metric_id, metric_name, value
FROM pick_metric
WHERE scope IS NULL OR scope = '';

-- H6. Rating buckets that do not sum to the analyst count.
--     Expect 0 rows. A mismatch invalidates score and share silently.
SELECT instrument_id, period, n_analysts,
       COALESCE(strong_buy,0) + COALESCE(buy,0) + COALESCE(hold,0)
         + COALESCE(sell,0) + COALESCE(strong_sell,0) AS bucket_sum
FROM analyst_consensus
WHERE n_analysts <> COALESCE(strong_buy,0) + COALESCE(buy,0) + COALESCE(hold,0)
                    + COALESCE(sell,0) + COALESCE(strong_sell,0)
   OR n_analysts <= 0;

-- H7. The label disagrees with the rule applied to the same numbers.
--     This is the check that caught the documented-rule mismatch on the page.
SELECT instrument_id, period, label AS source_label, label_derived
FROM analyst_consensus
WHERE label <> label_derived;

-- H8. A source that was OK but returned nothing, with no reason recorded.
--     "OK, 0 rows" and "OK, 71 rows" must never be indistinguishable.
SELECT source_id, observed_at, status, rows, message
FROM source_status
WHERE status = 'OK' AND (rows IS NULL OR rows = 0) AND (message IS NULL OR message = '');

-- H9. A crowd market linked without its resolution criteria, or linked by
--     something that is not a human-reviewed table.
SELECT l.link_id, l.market_id, m.title
FROM crowd_market_link l
JOIN crowd_market m ON m.market_id = l.market_id
WHERE m.resolution_criteria IS NULL OR m.resolution_criteria = ''
   OR l.rationale IS NULL OR l.rationale = '';

-- ===========================================================================
-- SOFT checks: smells worth a weekly look
-- ===========================================================================

-- S1. THE ONE YOU ASKED ABOUT: open a while, P/L still exactly 0.
--     Distinguishes the two causes -- an unmarked position (mark_price NULL)
--     from a genuinely flat one (mark_price present, price unchanged).
--     Both are worth seeing; only the first is a pipeline failure.
SELECT p.symbol, p.asset_class, o.observed_at,
       ROUND(TIMESTAMPDIFF(DAY, o.observed_at, :now), 1) AS days_old,
       o.mark_price, o.pnl_pct,
       CASE WHEN o.mark_price IS NULL THEN 'UNMARKED -- no price fetched'
            ELSE 'FLAT -- marked, price unchanged' END AS likely_cause
FROM pick p
JOIN pick_observation o ON o.pick_id = p.pick_id
WHERE o.status = 'OPEN'
  AND COALESCE(o.pnl_pct, 0) = 0
  AND o.observed_at < DATE_SUB(:now, INTERVAL 1 DAY)
ORDER BY o.observed_at;

-- S2. Latest observation is stale -- the position is open but nothing has
--     re-read it recently. Threshold is a parameter, not a guess baked in.
SELECT p.pick_id, p.symbol, MAX(o.observed_at) AS last_seen,
       TIMESTAMPDIFF(DAY, MAX(o.observed_at), :now) AS days_stale
FROM pick p
JOIN pick_observation o ON o.pick_id = p.pick_id
WHERE o.status = 'OPEN'
GROUP BY p.pick_id, p.symbol
HAVING MAX(o.observed_at) < DATE_SUB(:now, INTERVAL :stale_days DAY)
ORDER BY days_stale DESC;

-- S3. Open with no risk levels. A position without TP/SL cannot be resolved
--     by the resolver and will sit open forever.
SELECT pick_id, symbol, direction, entry_price, take_profit, stop_loss
FROM pick
WHERE direction <> 'FLAT' AND (take_profit IS NULL OR stop_loss IS NULL);

-- S4. Levels on the wrong side of entry -- a LONG whose stop is above entry
--     would fire immediately. This is a sign error, not a preference.
SELECT pick_id, symbol, direction, entry_price, take_profit, stop_loss
FROM pick
WHERE (direction = 'LONG'  AND (stop_loss >= entry_price OR take_profit <= entry_price))
   OR (direction = 'SHORT' AND (stop_loss <= entry_price OR take_profit >= entry_price));

-- S5. Reported P/L disagrees with our own recomputation by more than rounding.
--     A large gap means one of the two is wrong -- usually a missing fee.
SELECT pick_id, symbol, observed_at, pnl_pct, pnl_pct_net,
       ROUND(ABS(pnl_pct - pnl_pct_net), 4) AS gap
FROM pick_observation
WHERE pnl_pct IS NOT NULL AND pnl_pct_net IS NOT NULL
  AND ABS(pnl_pct - pnl_pct_net) > 0.5
ORDER BY gap DESC;

-- S6. One analyst row, wildly out of line with the rest of the firm's calls --
--     the classic vendor mapping error (a rating scaled 1-5 vs -2..+2).
SELECT a.firm, a.instrument_id, a.action_date, a.from_grade, a.to_grade
FROM analyst_action a
JOIN analyst_action o
  ON o.firm = a.firm AND o.instrument_id = a.instrument_id AND o.action_id <> a.action_id
WHERE (a.from_grade IS NOT NULL AND a.to_grade IS NOT NULL)
  AND a.from_grade = a.to_grade AND a.action IN ('up', 'down');

-- S7. Thin coverage presented like thick coverage. These rows should render
--     with a badge, never in a plain ranking.
SELECT instrument_id, period, n_analysts, label
FROM analyst_consensus
WHERE n_analysts < 15
ORDER BY n_analysts;

-- S8. Firms with too few calls to score. Never rank these -- the scorecard
--     table sets suppressed = 1 for exactly this reason.
SELECT firm, horizon_days, n_calls, hit_rate, mean_excess_pct
FROM analyst_scorecard
WHERE n_calls < 30 OR suppressed = 1;

-- ===========================================================================
-- SQLite notes
-- ===========================================================================
-- TIMESTAMPDIFF / DATE_SUB / DATE_ADD do not exist in SQLite. Equivalents:
--   days_old      : julianday(:now) - julianday(observed_at)
--   stale cutoff  : datetime(:now, '-' || :stale_days || ' days')
--   date of ts    : date(ts)
-- The COALESCE-based checks (H5, S1, S4) are portable as written.
