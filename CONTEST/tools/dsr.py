#!/usr/bin/env python3
"""dsr.py - Deflated Sharpe Ratio from a trial log.

Reads the `trials` table (docs/experiment_schema.sql) from a SQLite database and
computes the Deflated Sharpe Ratio using the variance of the trial Sharpes as the
data-mining / multiple-trials deflation.

Formula source: Bailey & Lopez de Prado, "The Deflated Sharpe Ratio",
Journal of Investment Management, 2014.

    - PSR (Probabilistic Sharpe Ratio): P(true Sharpe > benchmark) for a single
      trial, adjusting the Sharpe standard error for return skew/kurtosis (Lo 2002).
    - DSR: PSR deflated for the fact that the reported Sharpe is the BEST of N
      trials. The deflation here uses the cross-trial variance of Sharpes: wider
      dispersion across trials = more opportunities to mine luck = lower DSR.

        DSR = Phi( (SR_best - SR_bench) / s_trials )

      where s_trials is the sample standard deviation of the trial Sharpes and
      Phi is the standard normal CDF.

Append-only contract: DSR is only meaningful on a complete, unpruned trial log
(see trial_log.py - there is no delete path).
"""
import math
import re
import sqlite3
import sys

# --- refusal guard (2026-11-24) -------------------------------------------------
# This module used to return DSR=0.999983991176608 for a ledger holding exactly four
# rows named dummy-A..dummy-D (run_id dummy-run-1 / cron-run, kept=0 on all four).
# The arithmetic was correct and the number was meaningless: with n=4 the cross-trial
# sd (0.3367) is tiny, so z=(1.4-0)/0.3367=4.16 and Phi(4.16)=0.99998.
# A metric that cannot be valid must not be EMITTED, because every downstream consumer
# (cron commit message, dashboard, report) cannot tell a refused metric from a real one.
# Callers get an exception instead of a number.
import dsr_guard  # shared refusal gate - ONE definition for every DSR module here
from dsr_guard import (  # re-exported so existing callers and tests keep working
    MIN_TRIALS_FOR_DSR,
    DSRNotComputable,
)


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def dsr_from_db(db, sr_bench=0.0, use_oos=True, allow_fixtures=False, min_trials=None):
    """Compute DSR, or RAISE rather than return a number that cannot be valid.

    Two refusals, both deliberate:
      1. fixture rows present  -> this is not a measurement (the observed defect)
      2. n < min_trials        -> cross-trial variance is unestimable and the
                                  expected-maximum deflation is undefined
    Sets `allow_fixtures=True` ONLY to unit-test the estimator itself. A reporting
    path must never set it.
    """
    con = sqlite3.connect(db)
    try:
        col = "sharpe_oos" if use_oos else "sharpe_is"
        rows = con.execute(
            "SELECT %s, run_id, family FROM trials WHERE %s IS NOT NULL" % (col, col)
        ).fetchall()
    finally:
        con.close()
    sharpes = [float(r[0]) for r in rows]
    n = len(sharpes)
    dsr_guard.check(n, [(r[1], r[2], None) for r in rows],
                    allow_fixtures=allow_fixtures, min_trials=min_trials,
                    source=db)
    if n == 0:
        return None, 0, None
    sr_best = max(sharpes)
    if n < 2:
        # No cross-trial variance available to deflate with -> plain PSR-like z.
        return norm_cdf((sr_best - sr_bench) / 1.0), n, sr_best
    mean_s = sum(sharpes) / n
    var_s = sum((s - mean_s) ** 2 for s in sharpes) / (n - 1)  # sample variance
    sd_s = math.sqrt(var_s)
    if sd_s == 0:
        return norm_cdf((sr_best - sr_bench) / 1e-12), n, sr_best
    z = (sr_best - sr_bench) / sd_s
    return norm_cdf(z), n, sr_best


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    db = args[0] if args else "trial_ledger.db"
    use_oos = "--is" not in flags
    allow_fixtures = "--allow-fixtures" in flags
    col = "sharpe_oos" if use_oos else "sharpe_is"
    try:
        dsr, n, sr_best = dsr_from_db(db, use_oos=use_oos, allow_fixtures=allow_fixtures)
    except DSRNotComputable as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.stderr.write("DSR=REFUSED source=%s (no number emitted)\n" % db)
        sys.exit(2)
    print("source=%s trials=%d column=%s best_sharpe=%s" % (db, n, col, sr_best))
    print("DSR=%s" % dsr)
