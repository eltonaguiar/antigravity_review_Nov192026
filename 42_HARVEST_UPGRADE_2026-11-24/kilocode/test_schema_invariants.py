"""SQLite simulation proving deterministic latest-mark selection and denominators."""
import sqlite3

def build(deterministic: bool):
    db = sqlite3.connect(":memory:")
    db.executescript("""
      CREATE TABLE marks(pick_id INT, mark_id INT, mark_ts TEXT, net_bps REAL);
      INSERT INTO marks VALUES (1,1,'2026-11-24',100),(1,2,'2026-11-24',-100),(2,3,'2026-11-24',50);
    """)
    if deterministic:
        db.executescript("""
          CREATE VIEW latest AS
          SELECT pick_id, mark_id, mark_ts, net_bps FROM (
            SELECT m.*, ROW_NUMBER() OVER (PARTITION BY pick_id ORDER BY mark_ts DESC, mark_id DESC) rn
            FROM marks m) t WHERE rn=1;
        """)
    else:
        db.executescript("""
          CREATE VIEW latest AS
          SELECT m.* FROM marks m
          JOIN (SELECT pick_id, MAX(mark_ts) md FROM marks GROUP BY pick_id) d
            ON d.pick_id=m.pick_id AND d.md=m.mark_ts;
        """)
    return db

def test_old_view_double_counts_same_date_marks():
    db = build(False)
    assert db.execute("SELECT COUNT(*) FROM latest").fetchone()[0] == 3
    assert db.execute("SELECT AVG(net_bps) FROM latest").fetchone()[0] != -25.0

def test_deterministic_view_is_one_row_per_pick():
    db = build(True)
    assert db.execute("SELECT COUNT(*) FROM latest").fetchone()[0] == 2
    assert db.execute("SELECT AVG(net_bps) FROM latest").fetchone()[0] == -25.0
