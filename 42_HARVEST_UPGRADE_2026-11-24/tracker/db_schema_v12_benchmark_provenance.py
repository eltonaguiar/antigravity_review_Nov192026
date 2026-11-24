"""Benchmark provenance (2026-11-24), from GLM 5.3's round-1 finding.

GLM's point: picktrack_marks stores benchmark_net_bps and excess_bps, but the schema contains no
benchmark price series at all - picktrack_picks.benchmark is a bare ticker string with no statement
of return convention, no dividend adjustment, no version. So the headline metric, excess return, is
not reproducible from the data. For a SPY-benchmarked pick held a year it is inflated by the SPY
total-return gap of roughly 125-130 bps, and every such pick reads that much more skilled than it is.

GLM's framing is the useful part: "You fixed this exact disease for labels with rule_hash; your core
metric still has it." A label must be reproducible from its own row; excess return must be too.

This script cannot invent a price series. What it can do, and does:
  1. create benchmark_ref, stating each benchmark's return convention and dividend treatment;
  2. stamp every mark with the benchmark convention version that produced its excess number;
  3. expose v_excess_audit, which marks every excess figure written before that stamping as
     UNVERIFIABLE - so the number stays visible but stops masquerading as measured.

Marking existing rows unverifiable is the honest outcome. Backfilling a convention into them would
assert that the original computation used it, which nobody can know.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

BENCHMARKS = [
    ("SPY", "TOTAL_RETURN", 1,
     "S&P 500 ETF. Total return: dividends reinvested. A price-only series understates the benchmark "
     "by roughly 125-130 bps a year, which flatters every excess number computed against it."),
    ("BTC-USD", "PRICE", 0,
     "Bitcoin spot, price return only - no yield exists to reinvest."),
    ("CASH", "CARRY", 0,
     "Cash or T-bill carry. The bar, not an asset. Compared against at the stated yield, not at zero."),
    ("QQQ", "TOTAL_RETURN", 1, "Nasdaq-100 ETF, total return."),
    ("TLT", "TOTAL_RETURN", 1, "20+ year Treasuries, total return including coupon."),
]

DDL = [
    ("""CREATE TABLE IF NOT EXISTS benchmark_ref (
          ticker            VARCHAR(32) NOT NULL,
          return_convention ENUM('PRICE','TOTAL_RETURN','CARRY') NOT NULL,
          div_adjusted      TINYINT(1) NOT NULL DEFAULT 0,
          source            VARCHAR(64) NULL,
          convention_version VARCHAR(32) NOT NULL DEFAULT 'v1',
          notes             VARCHAR(400) NULL,
          PRIMARY KEY (ticker, convention_version)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""", "benchmark_ref"),
    ("""CREATE TABLE IF NOT EXISTS benchmark_series (
          ticker     VARCHAR(32) NOT NULL,
          bar_date   DATE NOT NULL,
          close_px   DECIMAL(18,6) NOT NULL,
          convention_version VARCHAR(32) NOT NULL DEFAULT 'v1',
          source     VARCHAR(64) NULL,
          PRIMARY KEY (ticker, bar_date, convention_version)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""", "benchmark_series"),
]


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()
    for ddl, name in DDL:
        cur.execute(ddl)
        print(f"table {name} ok")

    for ticker, conv, divadj, notes in BENCHMARKS:
        cur.execute("""INSERT INTO benchmark_ref
                       (ticker, return_convention, div_adjusted, source, convention_version, notes)
                       VALUES (%s,%s,%s,%s,'v1',%s)
                       ON DUPLICATE KEY UPDATE return_convention=VALUES(return_convention),
                         div_adjusted=VALUES(div_adjusted), notes=VALUES(notes)""",
                    (ticker, conv, divadj, "declared", notes))
    cur.execute("SELECT COUNT(*) FROM benchmark_ref")
    print("benchmark_ref rows:", cur.fetchone()[0])

    cur.execute("""SELECT COUNT(*) FROM information_schema.columns
                   WHERE table_schema=%s AND table_name='picktrack_marks'
                     AND column_name='benchmark_ref_version'""", (DB,))
    if not cur.fetchone()[0]:
        cur.execute("ALTER TABLE picktrack_marks ADD COLUMN benchmark_ref_version VARCHAR(32) NULL")
        print("column benchmark_ref_version added (NULL on every existing row - that is the point)")

    # every existing excess figure predates any stated convention
    cur.execute("""SELECT COUNT(*) FROM picktrack_marks
                   WHERE benchmark_net_bps IS NOT NULL OR excess_bps IS NOT NULL""")
    n_excess = cur.fetchone()[0]

    cur.execute("""CREATE OR REPLACE VIEW v_excess_audit AS
        SELECT m.pick_id, p.symbol, p.benchmark, m.mark_date,
               m.benchmark_net_bps, m.excess_bps, m.benchmark_ref_version,
               b.return_convention, b.div_adjusted,
               CASE WHEN m.excess_bps IS NULL THEN 'NO_EXCESS'
                    WHEN m.benchmark_ref_version IS NULL THEN 'UNVERIFIABLE - no stated benchmark convention'
                    WHEN b.return_convention = 'PRICE' AND p.asset_class IN ('EQUITY','ETF','STOCK')
                         THEN 'CONVENTION_MISMATCH - price-only benchmark for a dividend-paying asset'
                    ELSE 'VERIFIABLE' END AS excess_status
        FROM picktrack_marks m
        JOIN picktrack_picks p ON p.id = m.pick_id
        LEFT JOIN benchmark_ref b ON b.ticker = p.benchmark""")
    print("view v_excess_audit ok")

    cur.execute("""SELECT excess_status, COUNT(*) FROM v_excess_audit GROUP BY excess_status ORDER BY 2 DESC""")
    print("\nexcess figures by verifiability:")
    for r in cur.fetchall():
        print("  ", r[0], "->", r[1])
    print(f"\nrows carrying an excess figure: {n_excess}")
    print("benchmark price rows available:", end=" ")
    cur.execute("SELECT COUNT(*) FROM benchmark_series")
    print(cur.fetchone()[0], "(no series ingested yet, so nothing can be re-derived)")
    c.close()


if __name__ == "__main__":
    main()
