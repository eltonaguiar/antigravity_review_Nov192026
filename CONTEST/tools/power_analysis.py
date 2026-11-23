"""Power analysis for the strategy audit.

Three reviewers asked for the same thing: a power statement. This computes it.

Nothing here is a market claim. Every number is arithmetic from
    SE(mean annual return) = vol / sqrt(T)
on an annualised basis, which is the standard approximation for i.i.d. annual
returns. It answers one question: how long a sample does a gate need before a
real effect of size X can clear it?

Run: python power_analysis.py
"""
import math

HURDLE = 0.0432  # T-bill, 2026-11, for reference only - not used as a threshold here


def se(vol, years):
    return vol / math.sqrt(years)


def ci95(mean, vol, years, z=1.96):
    s = se(vol, years)
    return mean - z * s, mean + z * s


def years_for_t(effect, vol, t=2.0):
    """Sample length needed for `effect` to be t standard errors from zero."""
    return (t * vol / effect) ** 2


def mde(vol, years, t=2.0):
    """Smallest effect detectable at t standard errors given the sample."""
    return t * vol / math.sqrt(years)


def main():
    print("=" * 78)
    print("1. HOW WIDE IS THE INTERVAL ON +0.11%?")
    print("=" * 78)
    print("The page said the value strategy 'lost because the effect was not there'.")
    print("Measured gross effect: +0.11%/yr. Here is what that actually supports.\n")
    print("  %-8s %-9s %-28s %s" % ("vol", "years", "95% CI on +0.11%", "interpretation"))
    print("  " + "-" * 72)
    for vol in (0.06, 0.10, 0.15):
        for yrs in (3, 5, 10, 20):
            lo, hi = ci95(0.0011, vol, yrs)
            spread = hi - lo
            verdict = "cannot distinguish from 0" if lo < 0 < hi else "resolves"
            print("  %-8s %-9d [%+.1f%%, %+.1f%%]  width %.1f pp   %s"
                  % ("%.0f%%" % (vol * 100), yrs, lo * 100, hi * 100, spread * 100, verdict))
    print("\n  A 10%-vol book over 10 years cannot resolve a 3%/yr premium, let alone 0.11%.")
    print("  The interval is ~13 percentage points wide. 'Not there' is not supportable.")

    print()
    print("=" * 78)
    print("2. HOW LONG WOULD YOU NEED? (years for effect to reach t=2)")
    print("=" * 78)
    print("  %-10s %-9s %-9s %-9s %-9s" % ("effect/yr", "vol 6%", "vol 10%", "vol 15%", "vol 20%"))
    print("  " + "-" * 56)
    for eff in (0.005, 0.01, 0.02, 0.03, 0.05):
        row = "  %-10s" % ("%.1f%%" % (eff * 100))
        for vol in (0.06, 0.10, 0.15, 0.20):
            y = years_for_t(eff, vol)
            row += " %-9s" % ("%.0f y" % y)
        print(row)
    print("\n  Academic HML is ~3-5%/yr. At 10% vol that needs 11-44 years of data")
    print("  just to reach t=2. A few-year sample CANNOT pronounce a factor dead.")

    print()
    print("=" * 78)
    print("3. WHAT COULD THIS SAMPLE HAVE DETECTED? (MDE at t=2)")
    print("=" * 78)
    print("  %-9s %-12s %s" % ("years", "vol 10% MDE", "vol 15% MDE"))
    print("  " + "-" * 44)
    for yrs in (2, 3, 5, 10, 20, 44):
        print("  %-9d %-12s %s"
              % (yrs, "%.1f%%/yr" % (mde(0.10, yrs) * 100), "%.1f%%/yr" % (mde(0.15, yrs) * 100)))
    print("\n  If the sample is 5 years at 10% vol, the gate can only see effects")
    print("  bigger than ~9%/yr. Everything smaller is invisible, valid or not.")

    print()
    print("=" * 78)
    print("4. THE 9 bp GROSS->NET GAP IMPLIES WHAT TURNOVER?")
    print("=" * 78)
    print("  value strategy: +0.11%/yr gross -> +0.02%/yr net = 9 bp/yr of cost.")
    print("  Implied round trips per year at each measured cost:\n")
    gap = 0.0011 - 0.0002
    print("  %-22s %-14s %s" % ("cost per round trip", "round trips/yr", "annual turnover"))
    print("  " + "-" * 56)
    for name, c in (("1 bp (mega-cap)", 0.0001), ("6.71 bp (ETF)", 0.000671),
                    ("12.07 bp (equity)", 0.001207), ("52 bp (crypto)", 0.0052)):
        rt = gap / c
        print("  %-22s %-14.1f %.0f%%" % (name, rt, rt * 2 * 100))
    print("\n  At 1 bp that is 9 round trips/yr = 1800% turnover.")
    print("  A 1800%-turnover book is not a value strategy. Either the cost")
    print("  assumption is far too low, or the implementation is not value.")

    print()
    print("=" * 78)
    print("5. THE ALTERNATIVE: TEST THE SIGNAL, NOT THE PORTFOLIO")
    print("=" * 78)
    print("  A cross-sectional IC test uses every name on every day.")
    print("  t ~ IC * sqrt(n), so for t=3 at a given IC:\n")
    print("  %-10s %-16s %s" % ("IC", "obs needed", "vs one equity curve"))
    print("  " + "-" * 60)
    for ic in (0.01, 0.02, 0.03, 0.05, 0.10):
        n = (3.0 / ic) ** 2
        print("  %-10.2f %-16s %s" % (ic, "{:,}".format(int(n)),
                                      "~%.1f y at 250 names/day" % (n / 250)))
    print("\n  191 names x 250 days = 47,750 observations per year. That is")
    print("  ~40x the statistical power of a single portfolio's annual return.")
    print("  The harness is testing the least powerful statistic available.")


if __name__ == "__main__":
    main()
