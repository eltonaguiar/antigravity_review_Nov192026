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
import sqlite3
import sys


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def dsr_from_db(db, sr_bench=0.0, use_oos=True):
    con = sqlite3.connect(db)
    try:
        col = "sharpe_oos" if use_oos else "sharpe_is"
        rows = con.execute("SELECT %s FROM trials WHERE %s IS NOT NULL" % (col, col)).fetchall()
    finally:
        con.close()
    sharpes = [float(r[0]) for r in rows]
    n = len(sharpes)
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
    db = sys.argv[1] if len(sys.argv) > 1 else "trial_ledger.db"
    use_oos = "--is" not in sys.argv
    dsr, n, sr_best = dsr_from_db(db, use_oos=use_oos)
    col = "sharpe_oos" if use_oos else "sharpe_is"
    print("source=%s trials=%d column=%s best_sharpe=%s" % (db, n, col, sr_best))
    print("DSR=%s" % dsr)
