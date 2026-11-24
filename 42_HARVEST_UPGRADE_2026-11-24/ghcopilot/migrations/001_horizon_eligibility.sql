-- ============================================================================
-- 001_horizon_eligibility.sql
-- THE PUBLISH BLOCKER. Apply this before any win rate from this schema is shown
-- to anyone.
--
-- Measured problem it fixes (2026-11-24, live ejaguiar1_stocks):
--   picktrack_picks.horizon_min_days IS NULL on 3,992 / 3,992 rows
--   picktrack_picks.horizon_max_days IS NULL on 3,992 / 3,992 rows
--   picktrack_picks has neither pick_type nor horizon_code
--   horizon_ref (6 vocab rows) is referenced by NOTHING
--   pick_type_ref is referenced only by the empty trader_rating
--   => a pick cannot express which horizon it belongs to, so a days_held=3 mark
--      counts identically to days_held=300.
--   => v_pick_stats_by_source has no min_n gate and would publish
--      COMMODITY 75.00% on 8 marked picks beside CRYPTO 22.36% on 331.
--
-- Design choice: FAIL CLOSED. A pick with no horizon is INELIGIBLE, not
-- provisionally eligible. On a fresh apply every pick is NULL, so every
-- win_rate_pct becomes NULL. That is the honest state: nothing is publishable
-- until horizons are assigned. It is deliberately not a gradual rollout.
--
-- NOT EXECUTED. Owner applies. Run section 1 first and read the output.
-- ============================================================================


-- ============================================================================
-- 1. PRE-FLIGHT — read only, changes nothing. Run these and inspect.
-- ============================================================================

-- 1a. Confirm the horizon columns are unusable today.
SELECT COUNT(*)                                     AS picks_total,
       SUM(horizon_min_days IS NULL)                 AS min_days_null,
       SUM(horizon_max_days IS NULL)                 AS max_days_null
FROM picktrack_picks;

-- 1b. The horizon vocabulary that exists and is currently unused.
SELECT horizon_code, min_days, max_days, anchor FROM horizon_ref ORDER BY min_days;

-- 1c. What the win-rate view publishes RIGHT NOW, so the before/after is provable.
SELECT source, asset_class, picks, marked_picks, wins, win_rate_pct
FROM v_pick_stats_by_source ORDER BY marked_picks DESC;

-- 1d. How many marks fall inside each horizon if a horizon were assigned?
--     This is the feasibility check: if nothing is old enough, no horizon will
--     yield eligible rows and the view will publish all NULL.
SELECT h.horizon_code,
       SUM(m.days_held BETWEEN h.min_days AND h.max_days) AS marks_inside_window,
       MIN(m.days_held) AS min_days_held, MAX(m.days_held) AS max_days_held
FROM picktrack_marks m
CROSS JOIN horizon_ref h
GROUP BY h.horizon_code
ORDER BY h.min_days;


-- ============================================================================
-- 2. DDL — add the horizon pointer. Nullable on purpose (NULL = unclassified).
-- ============================================================================

ALTER TABLE picktrack_picks
  ADD COLUMN horizon_code VARCHAR(32) NULL
      COMMENT 'FK horizon_ref. NULL = unclassified => INELIGIBLE for published stats',
  ADD INDEX ix_picks_horizon (horizon_code);

ALTER TABLE picktrack_picks
  ADD CONSTRAINT fk_picks_horizon
      FOREIGN KEY (horizon_code) REFERENCES horizon_ref (horizon_code)
      ON UPDATE CASCADE ON DELETE RESTRICT;


-- ============================================================================
-- 3. BACKFILL — deliberately NOT automatic.
--
-- There is no per-pick source of truth for horizon (no pick_type column, no
-- horizon_code upstream). Inventing one here would fabricate the very number
-- this migration exists to protect. So the default is UNCLASSIFIED, and the
-- owner assigns horizons explicitly per rule/source with the queries below.
-- ============================================================================

-- 3a. Example assignment, ONLY after the owner approves the mapping.
--     Never blanket-assign a horizon to get a publishable n.
-- UPDATE picktrack_picks
--    SET horizon_code = '1M'
--  WHERE horizon_code IS NULL
--    AND source_detail LIKE 'signal_validation/%';

-- 3b. Coverage report to track classification progress.
SELECT COALESCE(horizon_code, '<UNCLASSIFIED>') AS horizon_code,
       COUNT(*) AS picks
FROM picktrack_picks
GROUP BY horizon_code
ORDER BY picks DESC;


-- ============================================================================
-- 4. VIEW REPLACEMENT — v_pick_level gains horizon_code passthrough.
--
-- Rebuilt from the live definition plus one column, so existing consumers of
-- v_pick_level (v_pick_stats_by_source) keep working. Do not fork this into a
-- parallel v_pick_level_v2: two views carrying numbers is how divergence starts.
-- ============================================================================

CREATE OR REPLACE VIEW v_pick_level AS
SELECT
    p.id                       AS pick_id,
    p.source                   AS source,
    p.asset_class              AS asset_class,
    p.direction                AS direction,
    p.status                   AS status,
    p.cost_bps                 AS cost_bps,
    p.benchmark                AS benchmark,
    p.published_at             AS published_at,
    p.horizon_min_days         AS horizon_min_days,
    p.horizon_max_days         AS horizon_max_days,
    p.horizon_code             AS horizon_code,
    lm.net_bps                 AS net_bps,
    lm.excess_bps              AS excess_bps,
    lm.days_held               AS days_held,
    CASE WHEN lm.net_bps IS NULL THEN NULL
         WHEN lm.net_bps > 0     THEN 1
         ELSE 0 END            AS is_win,
    CASE WHEN lm.net_bps IS NULL THEN 'UNMARKED'
         WHEN lm.net_bps > 0     THEN 'WIN'
         ELSE 'LOSS' END       AS outcome
FROM picktrack_picks p
LEFT JOIN v_pick_latest_mark lm ON lm.pick_id = p.id;


-- ============================================================================
-- 5. VIEW REPLACEMENT — v_pick_stats_by_source, gated.
--
-- Changes vs the live definition:
--   * win_rate_pct is over ELIGIBLE picks only, not all marked picks
--   * eligible means: has a mark, has a horizon, and days_held sits inside that
--     horizon's [min_days, max_days]
--   * win_rate_pct is NULL when eligible_picks < 30 (the repo's standing
--     "n < 30 is not a verdict" rule, enforced in SQL rather than in prose)
--   * immature_or_unclassified is published beside it so the funnel is visible:
--     a suppressed rate must never look like a missing rate
-- ============================================================================

CREATE OR REPLACE VIEW v_pick_stats_by_source AS
SELECT
    v.source                                                      AS source,
    v.asset_class                                                 AS asset_class,
    COUNT(*)                                                      AS picks,
    SUM(CASE WHEN v.net_bps IS NOT NULL THEN 1 ELSE 0 END)         AS marked_picks,
    SUM(CASE WHEN v.is_win = 1 THEN 1 ELSE 0 END)                  AS wins,
    SUM(CASE WHEN v.net_bps IS NOT NULL
              AND v.horizon_code IS NOT NULL
              AND v.days_held BETWEEN h.min_days AND h.max_days
             THEN 1 ELSE 0 END)                                   AS eligible_picks,
    SUM(CASE WHEN v.net_bps IS NOT NULL
              AND (v.horizon_code IS NULL
                   OR v.days_held NOT BETWEEN h.min_days AND h.max_days)
             THEN 1 ELSE 0 END)                                   AS immature_or_unclassified,
    CASE WHEN SUM(CASE WHEN v.net_bps IS NOT NULL
                         AND v.horizon_code IS NOT NULL
                         AND v.days_held BETWEEN h.min_days AND h.max_days
                        THEN 1 ELSE 0 END) >= 30
         THEN ROUND(100.0 * SUM(CASE WHEN v.is_win = 1
                                       AND v.horizon_code IS NOT NULL
                                       AND v.days_held BETWEEN h.min_days AND h.max_days
                                      THEN 1 ELSE 0 END)
                    / NULLIF(SUM(CASE WHEN v.net_bps IS NOT NULL
                                        AND v.horizon_code IS NOT NULL
                                        AND v.days_held BETWEEN h.min_days AND h.max_days
                                       THEN 1 ELSE 0 END), 0), 2)
         ELSE NULL END                                            AS win_rate_pct,
    ROUND(AVG(CASE WHEN v.net_bps IS NOT NULL
                    AND v.horizon_code IS NOT NULL
                    AND v.days_held BETWEEN h.min_days AND h.max_days
                   THEN v.net_bps END), 2)                        AS mean_net_bps_per_pick,
    ROUND(MIN(CASE WHEN v.net_bps IS NOT NULL
                    AND v.horizon_code IS NOT NULL
                    AND v.days_held BETWEEN h.min_days AND h.max_days
                   THEN v.net_bps END), 2)                        AS worst_pick_bps,
    ROUND(MAX(CASE WHEN v.net_bps IS NOT NULL
                    AND v.horizon_code IS NOT NULL
                    AND v.days_held BETWEEN h.min_days AND h.max_days
                   THEN v.net_bps END), 2)                        AS best_pick_bps
FROM v_pick_level v
LEFT JOIN horizon_ref h ON h.horizon_code = v.horizon_code
GROUP BY v.source, v.asset_class;


-- ============================================================================
-- 6. POST-CHECK — the acceptance test. Both must hold before publishing.
-- ============================================================================

-- 6a. On a fresh apply (all horizons NULL) every win_rate_pct must be NULL.
--     If any number survives here, the gate is not working.
SELECT source, asset_class, picks, marked_picks, eligible_picks,
       immature_or_unclassified, win_rate_pct
FROM v_pick_stats_by_source ORDER BY marked_picks DESC;

-- 6b. The specific number this migration exists to stop. Must be NULL.
SELECT * FROM v_pick_stats_by_source
WHERE asset_class = 'COMMODITY' AND source = 'audit';

-- 6c. Reconciliation: eligible + immature must equal marked, always.
SELECT source, asset_class, marked_picks, eligible_picks, immature_or_unclassified,
       (eligible_picks + immature_or_unclassified - marked_picks) AS must_be_zero
FROM v_pick_stats_by_source
HAVING must_be_zero <> 0;
-- Expect zero rows. Any row here is a counting bug in the gate itself.


-- ============================================================================
-- 7. ROLLBACK
-- ============================================================================
-- CREATE OR REPLACE VIEW v_pick_stats_by_source AS /* previous definition */;
-- CREATE OR REPLACE VIEW v_pick_level AS /* previous definition */;
-- ALTER TABLE picktrack_picks DROP FOREIGN KEY fk_picks_horizon;
-- ALTER TABLE picktrack_picks DROP INDEX ix_picks_horizon;
-- ALTER TABLE picktrack_picks DROP COLUMN horizon_code;
