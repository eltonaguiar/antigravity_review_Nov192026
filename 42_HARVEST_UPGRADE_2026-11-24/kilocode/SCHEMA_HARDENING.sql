-- MySQL 8.4 hardening for the pick tracker. Apply in order; pre-checks first.

-- 0) PRE-CHECK: duplicates that would block the unique constraint
SELECT pick_id, mark_ts, COUNT(*) c FROM picktrack_marks
GROUP BY pick_id, mark_ts HAVING c > 1;

-- 1) Deterministic latest mark (one row per pick)
CREATE OR REPLACE VIEW v_pick_latest_mark AS
SELECT pick_id, mark_id, mark_ts, raw_pct, net_bps, excess_bps, days_held
FROM (
  SELECT m.*,
         ROW_NUMBER() OVER (PARTITION BY m.pick_id ORDER BY m.mark_ts DESC, m.mark_id DESC) AS rn
  FROM picktrack_marks m
) t
WHERE rn = 1;

ALTER TABLE picktrack_marks
  ADD CONSTRAINT uq_pick_mark_ts UNIQUE (pick_id, mark_ts);

-- 2) Level with explicit denominators
CREATE OR REPLACE VIEW v_pick_level AS
SELECT p.id AS pick_id, p.source, p.asset_class, p.direction, p.status,
       p.cost_bps, p.benchmark, lm.net_bps, lm.excess_bps, lm.days_held,
       CASE WHEN lm.net_bps IS NULL THEN NULL WHEN lm.net_bps > 0 THEN 1 ELSE 0 END AS is_win
FROM picktrack_picks p
LEFT JOIN v_pick_latest_mark lm ON lm.pick_id = p.id;

CREATE OR REPLACE VIEW v_pick_stats_by_source AS
SELECT source, asset_class,
       COUNT(*) AS picks_total,
       SUM(net_bps IS NOT NULL) AS picks_scored,
       SUM(is_win = 1) AS wins,
       ROUND(100.0 * SUM(is_win = 1) / NULLIF(SUM(net_bps IS NOT NULL), 0), 2) AS win_rate_pct,
       ROUND(AVG(net_bps), 2) AS mean_net_bps_per_pick
FROM v_pick_level
GROUP BY source, asset_class;

-- 3) Write-time consistency (cannot be a cross-table CHECK)
DELIMITER //
CREATE TRIGGER trg_marks_before_insert BEFORE INSERT ON picktrack_marks
FOR EACH ROW
BEGIN
  DECLARE c DECIMAL(10,4);
  SELECT cost_bps INTO c FROM picktrack_picks WHERE id = NEW.pick_id;
  IF NEW.days_held < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'days_held must be >= 0';
  END IF;
  SET NEW.net_bps = ROUND(NEW.raw_pct * 100 - c, 4);
END//

CREATE TRIGGER trg_marks_no_update BEFORE UPDATE ON picktrack_marks
FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'marks are append-only';
CREATE TRIGGER trg_marks_no_delete BEFORE DELETE ON picktrack_marks
FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'marks are append-only';
DELIMITER ;

-- 4) Horizon registry is the only source of horizon length
ALTER TABLE picktrack_picks
  ADD CONSTRAINT fk_pick_horizon FOREIGN KEY (horizon_code) REFERENCES horizon_ref(horizon_code);
ALTER TABLE horizon_ref
  ADD CONSTRAINT chk_horizon_range CHECK (min_days <= max_days);

-- 5) Screened-candidate integrity
ALTER TABLE screened_candidate
  ADD CONSTRAINT chk_screen_reason
  CHECK ((passed = 1 AND reject_reason IS NULL) OR (passed = 0 AND reject_reason IS NOT NULL));

-- 6) Drift is a gate, not a view: this must return zero rows
SELECT m.pick_id, m.mark_date, r.drift_bps
FROM v_mark_recomputed r
JOIN picktrack_marks m ON m.pick_id = r.pick_id AND m.mark_date = r.mark_date
WHERE ABS(r.drift_bps) > 0.01;
