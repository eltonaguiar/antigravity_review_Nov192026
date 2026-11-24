-- ============================================================================
-- 002_pick_resolution_authority.sql
-- Makes pick_resolution the single authoritative outcome, and stops the view
-- layer from silently overriding it.
--
-- DEPENDS ON 001_horizon_eligibility.sql (needs picktrack_picks.horizon_code).
--
-- Measured problem it fixes (2026-11-24):
--   pick_resolution: 0 rows, NO foreign key, NO unique constraint.
--   v_pick_level derives outcome from sign(net_bps) of the latest MARK, and
--   never reads pick_resolution (verified: zero references in the view text).
--   => today the de facto outcome authority is a mark-derived view; the intended
--      authority is an empty table nobody queries. The moment a resolver starts
--      writing pick_resolution, two live outcome definitions exist and the page
--      keeps showing the mark-derived one. That is the diverging-win-rate bug,
--      one layer above where it was fixed.
--
-- REVISION OF MY OWN ROUND-1 ADVICE, stated plainly:
--   In R1 I recommended "populate pick_resolution from the 494 existing marks".
--   That was wrong and this file does NOT do it. A mark is a price observation at
--   an arbitrary date with no exit reason and no horizon. Copying marks into
--   pick_resolution would make pick_resolution a pure function of
--   picktrack_marks -- a derived duplicate, which is precisely the duplicate
--   outcome source the whole exercise is trying to avoid. R2 measured that
--   excess_bps is NULL on 494/494 marks and horizon was NULL on 3,992/3,992
--   picks, which is why the shortcut looked cheaper than it is.
--   pick_resolution must be written by a RESOLVER applying explicit exit rules
--   (TP hit / SL hit / time exit at the pick's own horizon), not by copying the
--   last mark.
--
-- NOT EXECUTED. Owner applies.
-- ============================================================================


-- ============================================================================
-- 1. PRE-FLIGHT — read only.
-- ============================================================================

-- 1a. Confirm empty, unconstrained, unreferenced.
SELECT COUNT(*) AS resolution_rows FROM pick_resolution;

SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
FROM information_schema.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks' AND TABLE_NAME = 'pick_resolution';
-- Expect only PRIMARY; no FOREIGN KEY, no UNIQUE beyond the PK.

-- 1b. Confirm the view layer currently ignores it.
SELECT TABLE_NAME
FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks'
  AND VIEW_DEFINITION LIKE '%pick_resolution%';
-- Expect ZERO rows. Any row here means something already reads it; re-read that
-- view's definition before applying, because its semantics change.

-- 1c. Column-width compatibility for the FK (both must be varchar(80)).
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'ejaguiar1_stocks'
  AND COLUMN_NAME = 'pick_id'
  AND TABLE_NAME IN ('picktrack_picks','pick_resolution','picktrack_entries','picktrack_marks')
ORDER BY TABLE_NAME;


-- ============================================================================
-- 2. DDL — one outcome per (pick, horizon), and a real referential constraint.
-- ============================================================================

-- 2a. Referential integrity: an outcome cannot exist for a pick that does not.
ALTER TABLE pick_resolution
  ADD CONSTRAINT fk_resolution_pick
      FOREIGN KEY (pick_id) REFERENCES picktrack_picks (id)
      ON UPDATE CASCADE ON DELETE CASCADE;

-- 2b. Exactly one resolution per (pick, horizon). Without this, a re-run of the
--     resolver silently creates a second verdict for the same pick and the
--     divergence has somewhere to live again.
ALTER TABLE pick_resolution
  ADD UNIQUE KEY uq_resolution_pick_horizon (pick_id, horizon);

-- 2c. Lookup path for the view re-point below.
ALTER TABLE pick_resolution
  ADD INDEX ix_resolution_pick (pick_id);


-- ============================================================================
-- 3. RECONCILIATION — make disagreement between the two sources DETECTABLE.
--
-- This is the guard that was missing. It does not force the numbers to agree;
-- it makes any disagreement visible instead of silent. Run it as a daily check.
-- ============================================================================

CREATE OR REPLACE VIEW v_resolution_mark_consistency AS
SELECT
    r.pick_id                                   AS pick_id,
    r.horizon                                   AS horizon,
    r.pnl_bps                                   AS resolved_pnl_bps,
    m.net_bps                                   AS terminal_mark_bps,
    ROUND(r.pnl_bps - m.net_bps, 4)             AS disagreement_bps,
    r.exit_reason                               AS exit_reason,
    m.mark_date                                 AS terminal_mark_date,
    CASE WHEN m.net_bps IS NULL            THEN 'NO_MARK'
         WHEN ABS(r.pnl_bps - m.net_bps) > 1.0 THEN 'DISAGREES_GT_1BP'
         ELSE 'CONSISTENT' END                  AS status
FROM pick_resolution r
LEFT JOIN v_pick_latest_mark m ON m.pick_id = r.pick_id;

-- Why a tolerance exists at all: the terminal mark and the resolution may
-- legitimately differ if the resolver exits intrabar (TP touched before the
-- close the mark records). Anything beyond 1 bp must be explained, not ignored.


-- ============================================================================
-- 4. VIEW REPLACEMENT — v_pick_level now prefers the resolution.
--
-- Every row reports where its outcome came from, so a reader can never mistake
-- a mark-fallback for a resolved verdict. The fallback is retained on purpose:
-- 3,992 picks have no resolution and would otherwise vanish from every headline.
-- ============================================================================

CREATE OR REPLACE VIEW v_pick_level AS
SELECT
    p.id                                   AS pick_id,
    p.source                               AS source,
    p.asset_class                          AS asset_class,
    p.direction                            AS direction,
    p.status                               AS status,
    p.cost_bps                             AS cost_bps,
    p.benchmark                            AS benchmark,
    p.published_at                         AS published_at,
    p.horizon_min_days                     AS horizon_min_days,
    p.horizon_max_days                     AS horizon_max_days,
    p.horizon_code                         AS horizon_code,
    COALESCE(r.pnl_bps, lm.net_bps)        AS net_bps,
    COALESCE(r.bench_pnl_bps, lm.excess_bps) AS excess_bps,
    lm.days_held                           AS days_held,
    CASE WHEN r.pick_id IS NOT NULL            THEN 'RESOLVED'
         WHEN lm.net_bps IS NOT NULL           THEN 'MARK_FALLBACK'
         ELSE 'UNMARKED' END               AS outcome_source,
    r.exit_reason                          AS exit_reason,
    CASE WHEN COALESCE(r.pnl_bps, lm.net_bps) IS NULL THEN NULL
         WHEN COALESCE(r.pnl_bps, lm.net_bps) > 0     THEN 1
         ELSE 0 END                        AS is_win,
    CASE WHEN COALESCE(r.pnl_bps, lm.net_bps) IS NULL THEN 'UNMARKED'
         WHEN COALESCE(r.pnl_bps, lm.net_bps) > 0     THEN 'WIN'
         ELSE 'LOSS' END                   AS outcome
FROM picktrack_picks p
LEFT JOIN pick_resolution r
       ON r.pick_id = p.id
      AND r.horizon = p.horizon_code
LEFT JOIN v_pick_latest_mark lm
       ON lm.pick_id = p.id;


-- ============================================================================
-- 5. POST-CHECK — acceptance.
-- ============================================================================

-- 5a. With pick_resolution empty, every marked pick must report MARK_FALLBACK.
--     A RESOLVED row appearing here before the resolver runs would be a bug.
SELECT outcome_source, COUNT(*) AS picks
FROM v_pick_level GROUP BY outcome_source ORDER BY picks DESC;

-- 5b. No pick may be counted twice. The join above is on (pick_id, horizon) and
--     the UNIQUE key guarantees one row; this proves it after the fact.
SELECT COUNT(*) AS duplicate_pick_rows FROM (
    SELECT pick_id FROM v_pick_level GROUP BY pick_id HAVING COUNT(*) > 1
) t;
-- Expect 0.

-- 5c. v_pick_stats_by_source must still resolve (it reads v_pick_level).
SELECT source, asset_class, picks, marked_picks, eligible_picks, win_rate_pct
FROM v_pick_stats_by_source ORDER BY marked_picks DESC;


-- ============================================================================
-- 6. ROLLBACK
-- ============================================================================
-- DROP VIEW v_resolution_mark_consistency;
-- CREATE OR REPLACE VIEW v_pick_level AS /* previous definition */;
-- ALTER TABLE pick_resolution DROP INDEX ix_resolution_pick;
-- ALTER TABLE pick_resolution DROP INDEX uq_resolution_pick_horizon;
-- ALTER TABLE pick_resolution DROP FOREIGN KEY fk_resolution_pick;
