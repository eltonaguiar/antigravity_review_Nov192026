#!/usr/bin/env python3
"""dsr_guard.py - the single refusal gate for EVERY DSR implementation in this repo.

Why this file exists: the guard used to live only in `dsr.py`, which implemented the
WRONG formula. When `dsr_correct.py` arrived with the RIGHT formula it carried no
guard at all, so the module people should be using was the unguarded one. A guard
that lives beside the deprecated estimator protects the wrong thing.

Two independent refusals, because fixtures and small n fail for different reasons:

  1. FIXTURES - a synthetic row is not an observation. Four rows named dummy-A..D
     once produced DSR=0.999983991176608 and that number went into a commit message.
  2. n < MIN_TRIALS_FOR_DSR - below ~30 the cross-trial variance cannot be estimated
     and the expected-maximum deflation is undefined.

Both raise `DSRNotComputable` and callers must emit NO NUMBER. Zero is a value
someone will average; silence cannot be quoted.

Known limitation, deliberate: the fixture test is NAME-based, so rows called `famA`,
`var_alpha` or `r01` slip past it. The n_min floor is the real backstop; the two
checks are independent. The durable fix is to stop writing fixtures at all
(`trial_log.py`), not to broaden the regex.
"""
import re

# House convention: n < 30 is INSUFFICIENT (matches the estate's own gate).
MIN_TRIALS_FOR_DSR = 30

_FIXTURE_RE = re.compile(
    r"(dummy|fixture|fake|synthetic|placeholder|sample)", re.IGNORECASE
)


class DSRNotComputable(RuntimeError):
    """Raised instead of returning a DSR that cannot be a valid measurement."""


def is_fixture(label):
    """True if a run_id / family / variant name looks synthetic."""
    if not label:
        return False
    s = str(label)
    return bool(_FIXTURE_RE.search(s)) or s.lower().startswith("test")


def check(n_trials, fixture_rows=(), allow_fixtures=False, min_trials=None,
          source=""):
    """Raise DSRNotComputable unless a DSR may legitimately be computed.

    n_trials      : number of trials about to be used
    fixture_rows  : iterable of (run_id, family, variant) tuples for those trials
    allow_fixtures: ONLY for testing the estimator. A reporting path must never set it.
    min_trials    : override the floor (e.g. min_trials=0 to study the estimator)
    source        : label used in the error message (db path / description)
    """
    if not allow_fixtures:
        bad = [t for t in fixture_rows
               if is_fixture(t[0]) or (len(t) > 1 and is_fixture(t[1]))
               or (len(t) > 2 and is_fixture(t[2]))]
        if bad:
            raise DSRNotComputable(
                "%d of %d ledger rows are fixtures (e.g. run_id=%r family=%r)%s. "
                "DSR on synthetic trials is not a measurement - refusing to emit one."
                % (len(bad), n_trials, bad[0][0],
                   bad[0][1] if len(bad[0]) > 1 else None,
                   (" [" + source + "]") if source else "")
            )
    floor = MIN_TRIALS_FOR_DSR if min_trials is None else min_trials
    if n_trials < floor:
        raise DSRNotComputable(
            "n=%d trials < n_min=%d%s: cross-trial variance cannot be estimated and "
            "the expected-maximum deflation is undefined. House convention treats "
            "n<30 as INSUFFICIENT. Refusing to emit a DSR."
            % (n_trials, floor, (" [" + source + "]") if source else "")
        )
