"""Can R01 publish a leaderboard? The arithmetic answer.

The panel crosscheck said R01 must not rank until the minimum detectable effect
(MDE) is computed against the observed top-two gap. Fills have not printed yet, so
the observed gap does not exist. But the MDE is a property of the BOOK, not the
result - it can be computed now, and it settles the question by construction.

For two entrants with n picks each and per-pick volatility sigma, the standard
error of the difference in mean return is

    SE = sigma * sqrt(2/n)

and the smallest difference distinguishable at t=2 is 2*SE.

Run: python contest_mde.py
"""
import math

ENTRANT_PICKS = {"R01 median entrant": 4, "R01 largest": 4, "hypothetical 10": 10,
                 "hypothetical 30": 30, "hypothetical 100": 100}


def mde(sigma, n, t=2.0):
    return t * sigma * math.sqrt(2.0 / n)


def main():
    print("=" * 74)
    print("1. MINIMUM DETECTABLE DIFFERENCE BETWEEN TWO ENTRANTS (t=2)")
    print("=" * 74)
    print("Every R01 entrant filed 4 picks. Per-pick volatility is the driver.\n")
    print("  %-8s %-14s %-14s %s" % ("sigma", "n=4 picks", "n=10 picks", "n=30 picks"))
    print("  " + "-" * 62)
    for sigma in (0.02, 0.05, 0.10, 0.20):
        row = "  %-8s" % ("%.0f%%" % (sigma * 100))
        for n in (4, 10, 30):
            row += " %-14s" % ("%.1f pp" % (mde(sigma, n) * 100))
        print(row)
    print("\n  At 5% per-pick vol and 4 picks, two entrants must differ by")
    print("  ~7.1 percentage points in mean return before the gap means anything.")
    print("  At 10% vol - normal for single names - it is ~14.1 pp.")
    print("\n  A 4-pick book spanning one week cannot produce a 7-14 pp gap")
    print("  except by luck. THE RANKING IS NOT PUBLISHABLE BY CONSTRUCTION,")
    print("  and that is true whatever the results turn out to be.")

    print()
    print("=" * 74)
    print("2. HOW MANY PICKS WOULD A RANKING ACTUALLY NEED?")
    print("=" * 74)
    print("  n needed to detect a true mean-return difference at t=2:\n")
    print("  %-10s %-12s %-12s %s" % ("gap to detect", "sigma 5%", "sigma 10%", "sigma 20%"))
    print("  " + "-" * 56)
    for gap in (0.01, 0.02, 0.05, 0.10):
        row = "  %-10s" % ("%.0f pp" % (gap * 100))
        for sigma in (0.05, 0.10, 0.20):
            n = 2 * (2.0 * sigma / gap) ** 2
            row += " %-12s" % ("{:,}".format(int(math.ceil(n))))
        print(row)
    print("\n  To separate a 2 pp edge at 10% vol you need ~200 picks per entrant.")
    print("  R01 has 4. That is a factor of 50 short.")

    print()
    print("=" * 74)
    print("3. WHAT THE CONTEST CAN LEGITIMATELY REPORT")
    print("=" * 74)
    print("  YES  - per-pick bracket validity (inside / void / fund NAV)")
    print("  YES  - the aggregate void rate and its cause")
    print("  YES  - the SPY anchor spread across entrants (a price-accuracy test)")
    print("  NO   - a ranking of entrants by return")
    print("  NO   - 'entrant X beat entrant Y'")
    print("  NO   - a winner")
    print()
    print("  The honest leaderboard has 18 rows and one column: 'not distinguishable'.")


if __name__ == "__main__":
    main()
