"""v6: the drill-down the user asked for — one named analyst, one symbol, all their picks.

Two views, because the two source classes have different biases and must never be blended:

  v_analyst_symbol_history  named sell-side analyst (firm + analyst_name) on one instrument
  v_trader_symbol_history   a leaderboard/on-chain trader (no firm) on one symbol

Each returns the full action list with dates and ratings, plus the realised outcome when a
resolution exists, so "show me everything this person said about X" is a single SELECT rather than
a join written from memory under time pressure.

Honest state: analyst_actions is empty because the free feed returns no analyst names. The views are
correct and return zero rows until a firm-level feed is licensed. trader_action will fill from
crypto leaderboards, which is the only class where per-person history is obtainable today.
"""
import sys

import pymysql

DB = "ejaguiar1_stocks"

VIEWS = [
    ("v_analyst_symbol_history", """
    CREATE OR REPLACE VIEW v_analyst_symbol_history AS
    SELECT
        a.firm,
        a.analyst_name,
        a.symbol,
        a.action,
        a.rating_from,
        a.rating_to,
        a.pt_from,
        a.pt_to,
        a.action_date,
        a.action_time,
        a.source,
        -- filled when a resolution row exists; NULL means "not yet measured", never zero
        r.horizon,
        r.pnl_bps,
        r.bench_pnl_bps,
        (r.pnl_bps - COALESCE(r.bench_pnl_bps, 0)) AS excess_bps,
        r.outcome
    FROM analyst_actions a
    LEFT JOIN pick_resolution r
           ON r.pick_id = CONCAT('analyst:', a.symbol, ':', a.action_date, ':', a.action)
    """),

    ("v_trader_symbol_history", """
    CREATE OR REPLACE VIEW v_trader_symbol_history AS
    SELECT
        t.display_name,
        t.source,
        t.source_type,
        t.survivorship_flag,
        ta.symbol,
        ta.asset_class,
        ta.side,
        ta.entry_ts,
        ta.entry_price,
        ta.exit_ts,
        ta.exit_price,
        ta.hold_seconds,
        ROUND(TIMESTAMPDIFF(SECOND, ta.entry_ts, ta.exit_ts) / 86400.0, 2) AS hold_days,
        CASE WHEN ta.exit_price IS NOT NULL AND ta.entry_price > 0 THEN
             ROUND(((ta.exit_price - ta.entry_price) / ta.entry_price) * 10000
                   * CASE WHEN ta.side = 'short' THEN -1 ELSE 1 END, 2)
        END AS pnl_bps
    FROM trader_action ta
    JOIN trader t ON t.id = ta.trader_id
    """),

    ("v_trader_symbol_stats", """
    CREATE OR REPLACE VIEW v_trader_symbol_stats AS
    SELECT
        t.display_name,
        t.source,
        t.survivorship_flag,
        ta.symbol,
        ta.asset_class,
        COUNT(*)                                        AS n_closed,
        SUM(CASE WHEN
              ((ta.exit_price - ta.entry_price) / ta.entry_price)
              * CASE WHEN ta.side = 'short' THEN -1 ELSE 1 END > 0
            THEN 1 ELSE 0 END)                          AS n_wins,
        ROUND(AVG(((ta.exit_price - ta.entry_price) / ta.entry_price) * 10000
              * CASE WHEN ta.side = 'short' THEN -1 ELSE 1 END), 2) AS mean_bps,
        ROUND(AVG(ta.hold_seconds) / 3600.0, 1)         AS avg_hold_hours
    FROM trader_action ta
    JOIN trader t ON t.id = ta.trader_id
    WHERE ta.exit_price IS NOT NULL AND ta.entry_price > 0
    GROUP BY t.display_name, t.source, t.survivorship_flag, ta.symbol, ta.asset_class
    """),
]


def main():
    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=15, autocommit=True, charset="utf8mb4")
    cur = c.cursor()
    for name, sql in VIEWS:
        try:
            cur.execute(sql)
            cur.execute(f"SELECT COUNT(*) FROM {name}")
            print(f"  OK   {name:28} {cur.fetchone()[0]} rows")
        except Exception as e:
            print(f"  FAIL {name}: {str(e)[:110]}")

    cur.execute("INSERT INTO picktrack_events (pick_id, event, detail) VALUES (%s,%s,%s)",
                (None, "SCHEMA_V6",
                 "drill-down views: v_analyst_symbol_history, v_trader_symbol_history, "
                 "v_trader_symbol_stats (one person x one symbol, all picks)"))

    # show the exact query a reader would run, so the shape is documented not implied
    print("\nexample: all of one analyst's calls on one symbol")
    print("  SELECT * FROM v_analyst_symbol_history WHERE analyst_name = ? AND symbol = ? "
          "ORDER BY action_date;")
    print("example: one trader's record on one symbol")
    print("  SELECT * FROM v_trader_symbol_stats WHERE display_name = ? AND symbol = ?;")
    c.close()


if __name__ == "__main__":
    main()
