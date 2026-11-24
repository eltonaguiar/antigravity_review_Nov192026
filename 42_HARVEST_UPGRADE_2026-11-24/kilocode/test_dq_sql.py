"""Execute DQ_CHECKS.sql against a SQLite fixture seeded with one of each defect."""
import re, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SQL = (Path(__file__).resolve().parent / "DQ_CHECKS.sql").read_text()

SCHEMA = """
CREATE TABLE picks(pick_id TEXT, source TEXT, asset_class TEXT, direction TEXT, status TEXT,
  opened_at TEXT, closed_at TEXT, entry_px REAL, exit_px REAL, take_profit REAL, stop_loss REAL,
  pnl_pct REAL, exit_reason TEXT, symbol TEXT, integrity_excluded INT);
CREATE TABLE outcomes(pick_id TEXT, horizon_days INT);
CREATE TABLE consensus_snapshots(instrument_id TEXT, period TEXT, sb INT,b INT,h INT,s INT,ss INT,n INT,score REAL);
CREATE TABLE recommendations(rec_id TEXT, entity_id TEXT);
CREATE TABLE analyst_performance(entity_id TEXT,n_calls INT);
CREATE TABLE crowd_snapshots(market_id TEXT, ts TEXT, implied_prob REAL);
CREATE TABLE ingest_runs(source_id TEXT, started TEXT, status TEXT, http INT, error TEXT);
"""

def seed(db):
    db.executescript("""
    INSERT INTO picks VALUES
      ('p_ok','s','EQUITY','LONG','CLOSED','2026-11-01','2026-11-10',100,110,120,90,10,'TP','AAA',0),
      ('p_open_zero','s','EQUITY','LONG','OPEN','2026-10-01',NULL,100,0,120,90,0,NULL,'BBB',0),
      ('p_closed_zero','s','EQUITY','LONG','CLOSED','2026-11-01','2026-11-10',100,100,120,90,0,'TIME_EXIT','CCC',0),
      ('p_no_exit','s','EQUITY','LONG','CLOSED','2026-11-01','2026-11-10',100,NULL,120,90,5,'TP','DDD',0),
      ('p_bad_tp','s','CRYPTO','LONG','EXPIRED','2026-11-01','2026-11-10',100,0,90,110,-2,'EXPIRED','EEE',0),
      ('p_bad_px','s','CRYPTO','LONG','OPEN','2026-11-20',NULL,0,0,120,90,0,NULL,'FFF',0),
      ('p_outlier','s','CRYPTO','LONG','CLOSED','2026-11-01','2026-11-02',1,3,4,0.5,150,'TP','GGG',0),
      ('p_stale','s','FUTURES','LONG','OPEN','2026-01-01',NULL,100,0,120,90,0,NULL,'HHH',0),
      ('p_dup','s','EQUITY','LONG','OPEN','2026-11-20',NULL,100,0,120,90,0,NULL,'III',0),
      ('p_dup','s','EQUITY','LONG','OPEN','2026-11-20',NULL,100,0,120,90,0,NULL,'III',0),
      ('p_excl','s','EQUITY','LONG','CLOSED','2026-11-01','2026-11-02',100,90,120,80,-10,'SL','JJJ',1);
    INSERT INTO outcomes VALUES ('ghost',21),('p_ok',21),('p_ok',21);
    INSERT INTO consensus_snapshots VALUES ('AAA','2026-11-01',1,1,1,0,0,2,0.5),
                                             ('BBB','2026-11-01',1,1,1,0,0,9,0.0);
    INSERT INTO analyst_performance VALUES ('firmX',5);
    INSERT INTO crowd_snapshots VALUES ('m1','2020-01-01',1.5);
    INSERT INTO ingest_runs VALUES ('src','2026-11-24','failed',500,'boom');
    """)

def statements():
    parts, buf = [], ""
    for line in SQL.splitlines():
        if line.strip().startswith("--"): continue
        buf += line + "\n"
        if sqlite3.complete_statement(buf):
            parts.append(buf.strip()); buf = ""
    return [p for p in parts if p.strip()]

def test_dq_sql_executes_and_flags_defects():
    db = sqlite3.connect(":memory:"); db.executescript(SCHEMA); seed(db)
    nonempty = 0; errors = []
    for stmt in statements():
        try:
            rows = db.execute(stmt).fetchall()
            if rows: nonempty += 1
        except Exception as e:
            errors.append((stmt.splitlines()[0][:60], str(e)))
    assert not errors, errors
    assert nonempty >= 10, nonempty
