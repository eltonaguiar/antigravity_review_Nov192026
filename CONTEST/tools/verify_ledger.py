#!/usr/bin/env python3
"""verify_ledger.py -- recompute every entry's sha256 and compare it against LEDGER.md.

A commitment is only a commitment if it is recomputed at read time. Run this before quoting any entry,
and in CI if the contest ever grows. Exit 1 on any mismatch, so it can gate.

    python verify_ledger.py [round_dir]
"""
import hashlib
import os
import re
import sys


def canonical_hash(path):
    """sha256 of the LF-normalised content.

    On Windows, git's core.autocrlf rewrites LF to CRLF when it touches a file, so hashing the raw
    working-tree bytes changes after `git add`/checkout even though the content has not changed.
    Normalising first makes the commitment platform-stable and reproducible on any clone.
    """
    data = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "CONTEST/ROUND_01_2026-11-23"
    ledger_path = os.path.join(d, "LEDGER.md")
    if not os.path.isfile(ledger_path):
        print("no LEDGER.md at", ledger_path)
        return 1
    ledger = open(ledger_path, encoding="utf-8").read()

    rows, missing, bad = [], [], []
    for slug in sorted(os.listdir(d)):
        p = os.path.join(d, slug, "picks.json")
        if not os.path.isfile(p):
            continue
        actual = canonical_hash(p)
        rows.append((slug, actual[:12]))
        if actual[:12] not in ledger:
            # distinguish "not recorded" from "recorded under a different value":
            # name present but hash absent => the file changed (bad);
            # name absent entirely => the submission was never recorded (missing).
            named = bool(re.search(re.escape(slug.replace("_", " ")), ledger, re.I))
            (bad if named else missing).append(slug)

    print("%-20s %-14s %s" % ("agent", "actual sha256", "in ledger"))
    for slug, h in rows:
        print("%-20s %-14s %s" % (slug, h, "yes" if slug not in missing + bad else "NO"))

    print("\nentries verified: %d/%d" % (len(rows) - len(missing) - len(bad), len(rows)))
    if missing:
        print("NOT RECORDED:", ", ".join(missing))
    if bad:
        print("MISMATCH (file changed or hash wrong):", ", ".join(bad))
    return 1 if (missing or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
