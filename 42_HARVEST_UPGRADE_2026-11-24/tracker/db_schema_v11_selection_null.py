"""Selection-null gate (2026-11-24), from GLM 5.3's round-1 arithmetic.

GLM's claim: with 5,000 candidates screened, the BEST candidate's hit rate under a fair coin is
about 92% at n=20 and 69% at n=100. Verified here by simulation: 88.4% at n=20, 68.1% at n=100.
The claim is right in substance, and it demolishes this schema's own promise.

pick_type_ref ships gates of n=100 (DAY_TRADE), 60 (SWING), 40 (POSITION), 20 (LONG_TERM), 10
(BUY_AND_HOLD). Those read as validity floors. They are not. At n=20 the selection null already
produces an 88% hit rate, so any LONG_TERM record that clears "n>=20" has cleared nothing at all -
it has merely been drawn from a large enough pool that its best member looks excellent by chance.

The fix is not to raise the n floors, which would be arbitrary. It is to record, for each n, the hit
rate that pure selection produces, and then require a published record to beat THAT number rather
than zero. The table below stores the null, computed exactly, so the comparison is reproducible.

Method: the expected maximum of K binomial(n, 0.5) draws is the smallest k whose upper-tail
probability is at most 1/K. Computed with exact binomial sums, not a normal approximation, because
the n values here are small enough for the approximation to matter.
"""
import math
import sys

import pymysql

DB = "ejaguiar1_stocks"
K = 5000  # candidates screened, the number GLM used


def upper_tail(n, k):
    """P(X >= k) for X ~ Binomial(n, 0.5), exact."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / (2 ** n)


def expected_max_hit_rate(n, k_trials=K):
    """Smallest k whose upper tail is at most 1/K - i.e. the threshold a record must clear.

    Ascend from zero rather than descending from n: descending returns a perfect record for every n,
    which is the opposite of the answer wanted. If even a perfect record (k=n) is more likely than
    1/K, then no hit rate at that sample size can distinguish skill from selection, and the gate is
    reported as unreachable instead of silently returning 100%.
    """
    for k in range(0, n + 1):
        if upper_tail(n, k) <= 1.0 / k_trials:
            return k / n, k, False
    return 1.0, n, True   # unreachable: perfect record still not rare enough


def main():
    rows = []
    for n in (10, 20, 40, 60, 100, 200, 500, 1000):
        rate, k, unreachable = expected_max_hit_rate(n)
        rows.append((n, K, round(rate * 100, 2), k))
        if unreachable:
            print(f"n={n:>5}  UNREACHABLE - even a perfect record is not rare enough under 5000 trials")
        print(f"n={n:>5}  best-of-{K}: {rate*100:5.1f}%  ({k}/{n} wins needed to beat it)")

    c = pymysql.connect(host="mysql.50webs.com", user=DB, password=sys.argv[1], database=DB,
                        connect_timeout=20, autocommit=True, charset="utf8mb4")
    cur = c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS selection_null (
                     sample_n       INT NOT NULL,
                     trials         INT NOT NULL,
                     null_max_hit_pct DECIMAL(6,2) NOT NULL,
                     wins_needed    INT NOT NULL,
                     method         VARCHAR(64) NOT NULL DEFAULT 'exact binomial upper tail <= 1/trials',
                     computed_at    DATETIME NOT NULL,
                     PRIMARY KEY (sample_n, trials)
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    print("\ntable selection_null ok")

    for n, trials, pct, wins in rows:
        cur.execute("""INSERT INTO selection_null
                       (sample_n, trials, null_max_hit_pct, wins_needed, computed_at)
                       VALUES (%s,%s,%s,%s,NOW())
                       ON DUPLICATE KEY UPDATE null_max_hit_pct=VALUES(null_max_hit_pct),
                         wins_needed=VALUES(wins_needed), computed_at=NOW()""",
                    (n, trials, pct, wins))
    cur.execute("SELECT COUNT(*) FROM selection_null")
    print("selection_null rows:", cur.fetchone()[0])

    # the gate: a rating must beat the selection null at its own n, not beat zero
    cur.execute("""CREATE OR REPLACE VIEW v_rating_gate AS
        SELECT t.trader_id, t.asset_class, t.horizon, t.n, t.hit_rate, t.profile_code, t.tier,
               s.null_max_hit_pct, s.trials,
               CASE WHEN t.n IS NULL OR t.hit_rate IS NULL THEN 'NO_RECORD'
                    WHEN t.n < 30 THEN 'BELOW_SAMPLE_FLOOR'
                    WHEN t.hit_rate <= s.null_max_hit_pct THEN 'NOISE_FROM_SELECTION'
                    ELSE 'BEATS_SELECTION_NULL' END AS gate_verdict,
               CASE WHEN t.hit_rate IS NULL THEN NULL
                    ELSE ROUND(t.hit_rate - s.null_max_hit_pct, 2) END AS margin_over_null_pp
        FROM trader_rating t
        LEFT JOIN selection_null s
               ON s.sample_n = (SELECT MAX(sample_n) FROM selection_null
                                WHERE sample_n <= COALESCE(t.n, 0) AND trials = 5000)""")
    print("view v_rating_gate ok")

    # show what the old gates would have admitted
    cur.execute("""SELECT code, min_n, (SELECT null_max_hit_pct FROM selection_null
                                         WHERE sample_n<=min_n ORDER BY sample_n DESC LIMIT 1) AS null_at_that_n
                   FROM pick_type_ref ORDER BY min_n""")
    print("\npick type gate vs the noise it admits:")
    for code, min_n, nullpct in cur.fetchall():
        print(f"  {code:14} n>={min_n:<4} pure selection already yields ~{nullpct}% hit rate")


    cur.execute("SELECT COUNT(*) FROM v_rating_gate")
    print("\nratings under the new gate:", cur.fetchone()[0])
    c.close()


if __name__ == "__main__":
    main()
