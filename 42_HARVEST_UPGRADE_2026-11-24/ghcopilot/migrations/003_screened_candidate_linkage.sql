-- ============================================================================
-- 003_screened_candidate_linkage.sql
-- Makes a multiple-testing denominator reconstructible. Without this, no DSR,
-- no BH/BY correction and no SPA claim from this schema can be defended.
--
-- Measured problem it fixes (2026-11-24):
--   screened_candidate: 0 rows, NO foreign key in either direction, no pick_id.
--   rule_hash is VARCHAR(32) while rule_version.rule_hash is CHAR(64).
--   => a trial count cannot be scoped to the rule version whose label was
--      published, and a surviving pick cannot be attributed to its candidate row.
--      N_trials is bounded by COUNT(*) but never identified.
--   => `passed` is two-valued, so "rejected by rule" and "passed but lost the
--      ranking cutoff" are indistinguishable. Those are different statistical
--      objects: only the second is a selection-bias degree of freedom.
--
-- NOT EXECUTED. Owner applies. Safe to apply now: the table is empty, so every
-- ALTER below is a pure structural change with no data migration.
-- ============================================================================


-- ============================================================================
-- 1. PRE-FLIGHT — read only.
-- ============================================================================

-- 1a. Confirm empty and unconstrained.
SELECT COUNT(*) AS screened_rows FROM screened_candidate;

SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND TABLE_NAME = 'screened_candidate'
ORDER BY ORDINAL_POSITION;

SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
FROM information_schema.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND TABLE_NAME = 'screened_candidate';

-- 1b. The width mismatch, the decisive defect.
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND COLUMN_NAME = 'rule_hash'
ORDER BY TABLE_NAME;
-- Expect: rule_version.rule_hash char(64) | screened_candidate.rule_hash varchar(32)

-- 1c. Nothing may depend on the current shape; if anything does, stop.
SELECT TABLE_NAME, COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks'
  AND REFERENCED_TABLE_NAME = 'screened_candidate';
-- Expect zero rows.


-- ============================================================================
-- 2. DDL
-- ============================================================================

-- 2a. The missing link. Nullable because a rejected candidate never becomes a pick;
--     non-null exactly when the candidate was PROMOTED.
ALTER TABLE screened_candidate
  ADD COLUMN pick_id VARCHAR(80) NULL
      COMMENT 'set iff this candidate became a picktrack_picks row',
  ADD CONSTRAINT fk_screened_pick
      FOREIGN KEY (pick_id) REFERENCES picktrack_picks (id)
      ON UPDATE CASCADE ON DELETE SET NULL;

-- 2b. Three states, not two. REJECTED = rule said no. NOT_SELECTED = rule said yes
--     but a ranking/portfolio cap dropped it. PROMOTED = became a pick.
--     Default REJECTED is deliberate and conservative: an unclassified row counts
--     toward the trial denominator, which makes any significance claim HARDER,
--     never easier.
ALTER TABLE screened_candidate
  ADD COLUMN decision ENUM('REJECTED','NOT_SELECTED','PROMOTED')
      NOT NULL DEFAULT 'REJECTED'
      COMMENT 'REJECTED=rule no | NOT_SELECTED=passed but cut | PROMOTED=became a pick';

-- 2c. Widen so the trial count can be scoped to the rule version that produced
--     the published label. Same type as the rule_version primary key.
ALTER TABLE screened_candidate
  MODIFY COLUMN rule_hash CHAR(64) NULL
      COMMENT 'FK rule_version.rule_hash — required to scope a DSR denominator';

ALTER TABLE screened_candidate
  ADD CONSTRAINT fk_screened_rule
      FOREIGN KEY (rule_hash) REFERENCES rule_version (rule_hash)
      ON UPDATE CASCADE ON DELETE RESTRICT;

-- 2d. The denominator query's access path: trials per (source, time window).
ALTER TABLE screened_candidate
  ADD INDEX ix_screened_source_time (source, screened_at),
  ADD INDEX ix_screened_rule (rule_hash),
  ADD INDEX ix_screened_pick (pick_id);


-- ============================================================================
-- 3. THE DENOMINATOR — what becomes answerable once 2a-2d are applied.
--    This view is the point of the whole migration. It is the N_trials input
--    that DSR / BH / SPA require and that nothing in this schema can currently
--    produce.
-- ============================================================================

CREATE OR REPLACE VIEW v_trial_denominator AS
SELECT
    s.source                                                    AS source,
    s.rule_hash                                                 AS rule_hash,
    s.asset_class                                               AS asset_class,
    DATE(s.screened_at)                                         AS screened_date,
    COUNT(*)                                                    AS trials_screened,
    SUM(CASE WHEN s.decision = 'PROMOTED'     THEN 1 ELSE 0 END) AS trials_promoted,
    SUM(CASE WHEN s.decision = 'NOT_SELECTED' THEN 1 ELSE 0 END) AS trials_not_selected,
    SUM(CASE WHEN s.decision = 'REJECTED'     THEN 1 ELSE 0 END) AS trials_rejected,
    COUNT(DISTINCT s.pick_id)                                   AS distinct_picks_linked,
    -- The selection-bias term that was previously invisible: of everything the
    -- rule passed, what fraction actually reached the ledger?
    CASE WHEN SUM(CASE WHEN s.decision IN ('PROMOTED','NOT_SELECTED') THEN 1 ELSE 0 END) > 0
         THEN ROUND(100.0 * SUM(CASE WHEN s.decision = 'PROMOTED' THEN 1 ELSE 0 END)
                    / SUM(CASE WHEN s.decision IN ('PROMOTED','NOT_SELECTED') THEN 1 ELSE 0 END), 2)
         ELSE NULL END                                          AS promotion_rate_pct
FROM screened_candidate s
GROUP BY s.source, s.rule_hash, s.asset_class, DATE(s.screened_at);


-- ============================================================================
-- 4. POST-CHECK — acceptance.
-- ============================================================================

-- 4a. No promoted candidate may lack a pick link, and no unpromoted one may have one.
SELECT decision, SUM(pick_id IS NULL) AS without_pick, COUNT(*) AS row_count
FROM screened_candidate GROUP BY decision;

SELECT COUNT(*) AS violations FROM screened_candidate
WHERE (decision = 'PROMOTED' AND pick_id IS NULL)
   OR (decision <> 'PROMOTED' AND pick_id IS NOT NULL);
-- Expect 0.

-- 4b. The denominator view must execute (it will be empty — that is correct and
--     is itself the finding: N_trials is 0 today, so no DSR can be claimed yet).
SELECT COUNT(*) AS denominator_rows FROM v_trial_denominator;

-- 4c. Every rule_hash a candidate cites must exist as a published rule version.
SELECT s.rule_hash, COUNT(*) AS orphan_rows
FROM screened_candidate s
LEFT JOIN rule_version r ON r.rule_hash = s.rule_hash
WHERE s.rule_hash IS NOT NULL AND r.rule_hash IS NULL
GROUP BY s.rule_hash;
-- Expect zero rows (the FK enforces it; this proves it).


-- ============================================================================
-- 5. WHAT IS STILL MISSING AFTER THIS FILE
--
-- Structure is necessary, not sufficient. Until someone writes rows here, the
-- denominator is 0 and any DSR computed against it divides by zero or silently
-- defaults trials=1 -- which manufactures significance. The screen must be
-- logged by the scanner at decision time, not reconstructed after the fact.
-- ============================================================================


-- ============================================================================
-- 6. ROLLBACK
-- ============================================================================
-- DROP VIEW v_trial_denominator;
-- ALTER TABLE screened_candidate DROP INDEX ix_screened_pick;
-- ALTER TABLE screened_candidate DROP INDEX ix_screened_rule;
-- ALTER TABLE screened_candidate DROP INDEX ix_screened_source_time;
-- ALTER TABLE screened_candidate DROP FOREIGN KEY fk_screened_rule;
-- ALTER TABLE screened_candidate DROP FOREIGN KEY fk_screened_pick;
-- ALTER TABLE screened_candidate DROP COLUMN decision;
-- ALTER TABLE screened_candidate DROP COLUMN pick_id;
-- ALTER TABLE screened_candidate MODIFY COLUMN rule_hash VARCHAR(32) NULL;
