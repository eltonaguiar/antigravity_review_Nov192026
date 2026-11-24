#!/usr/bin/env python3
"""Regression tests for the DSR refusal guard (see DSR_GUARD.md).

Why this file exists: the guard's whole value is that it REFUSES to emit a number.
A guard that silently stops firing is indistinguishable from a working one until a
wrong number is published, so these tests assert the refusal itself - not just that
correct inputs work.

Run:  python3 CONTEST/tools/test_dsr_guard.py    (exit 0 = pass, 1 = fail)
Also pytest-compatible: every check is a `test_*` function.
"""
import os
import random
import sqlite3
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dsr import DSRNotComputable, MIN_TRIALS_FOR_DSR, dsr_from_db  # noqa: E402

COLS = "trial_id,run_id,family,variant,sharpe_is,sharpe_oos,kept,ts_logged"


def _make_db(n, run_prefix, family, seed=7):
    """Build a temp ledger with n rows."""
    path = os.path.join(tempfile.mkdtemp(), "t_%s_%d.db" % (run_prefix, n))
    con = sqlite3.connect(path)
    con.execute("create table trials(%s)" % COLS)
    rnd = random.Random(seed)
    for i in range(n):
        con.execute(
            "insert into trials values(?,?,?,?,?,?,?,?)",
            ("t%d" % i, "%s-run-1" % run_prefix, family, "%s-%d" % (run_prefix, i),
             round(rnd.uniform(-1, 2), 3), round(rnd.uniform(-1, 2), 3), i % 2, "now"),
        )
    con.commit()
    con.close()
    return path


def _refuses(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except DSRNotComputable:
        return True
    return False


# --- 1. the guard fires on fixture rows -----------------------------------------
def test_refuses_fixture_rows():
    db = _make_db(40, "dummy", "dummy")          # enough rows, but fabricated
    assert _refuses(dsr_from_db, db), "40 fixture rows were NOT refused"


# --- 2. the guard fires below n_min --------------------------------------------
def test_refuses_below_min_trials():
    db = _make_db(MIN_TRIALS_FOR_DSR - 1, "live", "trend")   # clean names, too few
    assert _refuses(dsr_from_db, db), "n=%d was NOT refused" % (MIN_TRIALS_FOR_DSR - 1)


# --- 3. a legitimate ledger still computes --------------------------------------
def test_computes_on_clean_ledger():
    db = _make_db(40, "live", "trend")
    dsr, n, sr_best = dsr_from_db(db)
    assert n == 40, "expected n=40, got %r" % (n,)
    assert 0.0 <= dsr <= 1.0, "DSR out of range: %r" % (dsr,)
    assert sr_best is not None


# --- 4. the escape hatch is real (and is the ONLY way past the fixture check) ---
def test_allow_fixtures_escape_hatch():
    db = _make_db(40, "dummy", "dummy")
    dsr, n, _ = dsr_from_db(db, allow_fixtures=True)
    assert n == 40 and 0.0 <= dsr <= 1.0


# --- 5. the invariant that actually matters: refusal emits NO number -----------
def test_cli_refusal_prints_no_numeric_dsr():
    db = _make_db(4, "dummy", "dummy")           # reproduces the 9c9eda3 shape
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "dsr.py"), db],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2, "expected exit 2, got %d" % proc.returncode
    assert "DSR=" in proc.stderr, "refusal reason missing from stderr"
    # a number must not reach stdout, or a caller will quote it
    leaked = [ln for ln in proc.stdout.splitlines()
              if ln.startswith("DSR=") and ln[4:5].isdigit()]
    assert not leaked, "a numeric DSR escaped on stdout: %r" % (leaked,)


def main():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("  PASS  %s" % name)
        except AssertionError as exc:
            failed += 1
            print("  FAIL  %s -> %s" % (name, exc))
    print("\n  %d/%d passed" % (len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
