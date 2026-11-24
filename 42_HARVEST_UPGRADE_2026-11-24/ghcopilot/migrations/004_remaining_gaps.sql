-- ============================================================================
-- 004_remaining_gaps.sql
-- The residue after 001 (fully applied) and 002/003 (partially applied) landed
-- upstream. Read 000_STATUS.md first.
--
-- Measured state at 2026-11-24 ~12:20Z, re-verified immediately before writing:
--   pick_resolution: 0 rows, HAS fk_res_pick + uq_res_pick_horizon,
--                    ALSO has a duplicate uq_resolution on the same columns
--   v_pick_level   : still derives outcome from sign(net_bps) of the latest MARK
--                    and does NOT reference pick_resolution (verified in the text)
--   screened_candidate: pick_id + decision + rule_hash char(64) exist,
--                    but ZERO foreign keys -> linkage is nominal, not enforced
--   v_resolution_mark_consistency : absent
--   v_trial_denominator           : absent
--
-- NOT EXECUTED. Owner applies.
-- ============================================================================


-- ============================================================================
-- 1. PRE-FLIGHT
-- ============================================================================

-- 1a. Confirm the two unique indexes really are duplicates before dropping one.
SELECT INDEX_NAME, NON_UNIQUE, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS cols
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND TABLE_NAME = 'pick_resolution'
GROUP BY INDEX_NAME, NON_UNIQUE;
-- Expect uq_res_pick_horizon and uq_resolution both listing pick_id,horizon.

-- 1b. Confirm the screened_candidate linkage is unenforced.
SELECT COLUMN_NAME, REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND TABLE_NAME = 'screened_candidate'
  AND REFERENCED_TABLE_NAME IS NOT NULL;
-- Expect zero rows. Any row here means someone added the FK; skip section 4.

-- 1c. Orphans that an FK would reject — must return zero rows or the ALTER fails.
SELECT COUNT(*) AS orphan_pick_ids FROM screened_candidate s
LEFT JOIN picktrack_picks p ON p.id = s.pick_id
WHERE s.pick_id IS NOT NULL AND p.id IS NULL;

SELECT COUNT(*) AS orphan_rule_hashes FROM screened_candidate s
LEFT JOIN rule_version r ON r.rule_hash = s.rule_hash
WHERE s.rule_hash IS NOT NULL AND r.rule_hash IS NULL;


-- ============================================================================
-- 2. DROP THE DUPLICATE UNIQUE INDEX
--    Same columns as uq_res_pick_horizon, identical uniqueness. It buys nothing
--    and doubles index maintenance on every resolution insert. Its presence is
--    evidence a migration was applied twice — worth noting in the change log.
-- ============================================================================

ALTER TABLE pick_resolution DROP INDEX uq_resolution;


-- ============================================================================
-- 3. RECONCILIATION VIEW — make resolution-vs-mark disagreement visible.
-- ============================================================================

CREATE OR REPLACE VIEW v_resolution_mark_consistency AS
SELECT
    r.pick_id                                       AS pick_id,
    r.horizon                                       AS horizon,
    r.pnl_bps                                       AS resolved_pnl_bps,
    m.net_bps                                       AS terminal_mark_bps,
    ROUND(r.pnl_bps - m.net_bps, 4)                 AS disagreement_bps,
    r.exit_reason                                   AS exit_reason,
    m.mark_date                                     AS terminal_mark_date,
    CASE WHEN m.net_bps IS NULL                  THEN 'NO_MARK'
         WHEN ABS(r.pnl_bps - m.net_bps) > 1.0   THEN 'DISAGREES_GT_1BP'
         ELSE 'CONSISTENT' END                      AS status
FROM pick_resolution r
LEFT JOIN v_pick_latest_mark m ON m.pick_id = r.pick_id;

-- A tolerance exists because a resolver may legitimately exit intrabar (TP touched
-- before the close a mark records). Beyond 1 bp the difference must be explained.


-- ============================================================================
-- 4. RESTORE THE screened_candidate FOREIGN KEYS
--    The columns were added without constraints, so today pick_id and rule_hash
--    are free text that merely resembles a link. This is what makes N_trials
--    scoped to a rule version rather than to a string that happens to match.
-- ============================================================================

ALTER TABLE screened_candidate
  ADD CONSTRAINT fk_screened_pick
      FOREIGN KEY (pick_id) REFERENCES picktrack_picks (id)
      ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE screened_candidate
  ADD CONSTRAINT fk_screened_rule
      FOREIGN KEY (rule_hash) REFERENCES rule_version (rule_hash)
      ON UPDATE CASCADE ON DELETE RESTRICT;


-- ============================================================================
-- 5. THE DENOMINATOR VIEW — N_trials becomes queryable.
-- ============================================================================

CREATE OR REPLACE VIEW v_trial_denominator AS
SELECT
    s.source                                                     AS source,
    s.rule_hash                                                  AS rule_hash,
    s.asset_class                                                AS asset_class,
    DATE(s.screened_at)                                          AS screened_date,
    COUNT(*)                                                     AS trials_screened,
    SUM(CASE WHEN s.decision = 'PROMOTED'     THEN 1 ELSE 0 END)  AS trials_promoted,
    SUM(CASE WHEN s.decision = 'NOT_SELECTED' THEN 1 ELSE 0 END)  AS trials_not_selected,
    SUM(CASE WHEN s.decision = 'REJECTED'     THEN 1 ELSE 0 END)  AS trials_rejected,
    COUNT(DISTINCT s.pick_id)                                    AS distinct_picks_linked,
    CASE WHEN SUM(CASE WHEN s.decision IN ('PROMOTED','NOT_SELECTED') THEN 1 ELSE 0 END) > 0
         THEN ROUND(100.0 * SUM(CASE WHEN s.decision = 'PROMOTED' THEN 1 ELSE 0 END)
                    / SUM(CASE WHEN s.decision IN ('PROMOTED','NOT_SELECTED') THEN 1 ELSE 0 END), 2)
         ELSE NULL END                                           AS promotion_rate_pct
FROM screened_candidate s
GROUP BY s.source, s.rule_hash, s.asset_class, DATE(s.screened_at);


-- ============================================================================
-- 6. RE-POINT v_pick_level AT THE RESOLUTION
--
-- This is the single most important statement in the file. It changes which
-- object defines an outcome. Rebuilt from the CURRENT live definition (which
-- exposes pick_type, horizon_code, profile_code, stop_pct, reward_risk) and
-- preserves every existing column, so v_pick_stats_by_source and v_pick_risk
-- keep working.
--
-- Every row now reports outcome_source, so a reader can never mistake a
-- mark-fallback for a resolved verdict. The fallback is kept deliberately:
-- 3,992 picks have no resolution and would otherwise vanish from every headline.
-- ============================================================================

CREATE OR REPLACE VIEW v_pick_level AS
SELECT
    p.id                                         AS pick_id,
    p.source                                     AS source,
    p.asset_class                                AS asset_class,
    p.direction                                  AS direction,
    p.status                                     AS status,
    p.cost_bps                                   AS cost_bps,
    p.benchmark                                  AS benchmark,
    p.published_at                               AS published_at,
    p.pick_type                                  AS pick_type,
    p.horizon_code                               AS horizon_code,
    p.horizon_min_days                           AS horizon_min_days,
    p.horizon_max_days                           AS horizon_max_days,
    p.profile_code                               AS profile_code,
    p.stop_pct                                   AS stop_pct,
    p.reward_risk                                AS reward_risk,
    COALESCE(r.pnl_bps, lm.net_bps)              AS net_bps,
    COALESCE(r.bench_pnl_bps, lm.excess_bps)     AS excess_bps,
    lm.days_held                                 AS days_held,
    CASE WHEN r.pick_id IS NOT NULL              THEN 'RESOLVED'
         WHEN lm.net_bps IS NOT NULL             THEN 'MARK_FALLBACK'
         ELSE 'UNMARKED' END                     AS outcome_source,
    r.exit_reason                                AS exit_reason,
    CASE WHEN COALESCE(r.pnl_bps, lm.net_bps) IS NULL THEN NULL
         WHEN COALESCE(r.pnl_bps, lm.net_bps) > 0     THEN 1
         ELSE 0 END                              AS is_win,
    CASE WHEN COALESCE(r.pnl_bps, lm.net_bps) IS NULL THEN 'UNMARKED'
         WHEN COALESCE(r.pnl_bps, lm.net_bps) > 0     THEN 'WIN'
         ELSE 'LOSS' END                         AS outcome,
    -- in_horizon is preserved verbatim from the live definition, because
    -- v_pick_stats_by_source and its n>=30 gate depend on it.
    CASE WHEN lm.net_bps IS NOT NULL
              AND p.horizon_code IS NOT NULL
              AND lm.days_held BETWEEN p.horizon_min_days AND p.horizon_max_days
         THEN 1 ELSE 0 END                       AS in_horizon
FROM picktrack_picks p
LEFT JOIN pick_resolution r
       ON r.pick_id = p.id
      AND r.horizon = p.horizon_code
LEFT JOIN v_pick_latest_mark lm
       ON lm.pick_id = p.id;


-- ============================================================================
-- 7. POST-CHECK — acceptance. Read every result before publishing anything.
-- ============================================================================

-- 7a. With pick_resolution still empty, EVERY marked pick must be MARK_FALLBACK.
SELECT outcome_source, COUNT(*) AS picks FROM v_pick_level GROUP BY outcome_source;
-- Expect RESOLVED absent, 494 MARK_FALLBACK, 3498 UNMARKED.

-- 7b. in_horizon must be unchanged by the re-point. Compare to 85 before applying.
SELECT in_horizon, COUNT(*) AS picks FROM v_pick_level GROUP BY in_horizon;

-- 7c. No pick may appear twice (the (pick_id, horizon) join plus the unique key).
SELECT COUNT(*) AS duplicate_pick_rows FROM (
    SELECT pick_id FROM v_pick_level GROUP BY pick_id HAVING COUNT(*) > 1
) t;
-- Expect 0.

-- 7d. The gated stats must still return exactly one publishable cell.
SELECT source, asset_class, horizon_code, picks, marked_in_horizon, wins, win_rate_pct
FROM v_pick_stats_by_source ORDER BY picks DESC;
-- Expect: only audit/CRYPTO/1M non-NULL (29.73% on 37). Anything else non-NULL means
-- the gate was weakened during the rebuild.

-- 7e. v_pick_risk must still resolve (it reads picktrack_picks, not v_pick_level —
--     confirm it was not broken by the change).
SELECT COUNT(*) AS risk_rows FROM v_pick_risk;

-- 7f. Denominator: 0 rows is the correct answer today, and is itself the finding.
SELECT COUNT(*) AS denominator_rows FROM v_trial_denominator;


-- ============================================================================
-- 8. ROLLBACK
-- ============================================================================
-- DROP VIEW v_trial_denominator;
-- DROP VIEW v_resolution_mark_consistency;
-- CREATE OR REPLACE VIEW v_pick_level AS /* previous definition from 000_STATUS.md */;
-- ALTER TABLE screened_candidate DROP FOREIGN KEY fk_screened_rule;
-- ALTER TABLE screened_candidate DROP FOREIGN KEY fk_screened_pick;
-- ALTER TABLE pick_resolution ADD UNIQUE KEY uq_resolution (pick_id, horizon);
