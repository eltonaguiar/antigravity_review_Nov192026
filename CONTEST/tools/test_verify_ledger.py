#!/usr/bin/env python3
"""Regression test: verify_ledger.py must not swap NOT_RECORDED and MISMATCH.

Unrecorded submission (name absent)  -> NOT RECORDED
Recorded name, changed hash          -> MISMATCH
Correct hash                         -> verified
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "verify_ledger.py")


def _h(p):
    data = open(p, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:12]


class VerifyLedgerLabels(unittest.TestCase):
    def test_label_semantics(self):
        with tempfile.TemporaryDirectory() as d:
            for slug in ("A_OK", "B_BAD", "C_MISSING"):
                os.makedirs(os.path.join(d, slug))
                with open(os.path.join(d, slug, "picks.json"), "w") as fh:
                    json.dump({"slug": slug}, fh)
            ok_hash = _h(os.path.join(d, "A_OK", "picks.json"))
            with open(os.path.join(d, "LEDGER.md"), "w") as fh:
                fh.write("# ledger\n")
                fh.write("| A OK | %s |\n" % ok_hash)
                fh.write("| B BAD | deadbeef1234 |\n")  # name present, wrong hash
                # C MISSING intentionally absent

            r = subprocess.run([sys.executable, TOOL, d],
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 1, out)
            self.assertIn("NOT RECORDED: C_MISSING", out)
            self.assertIn("MISMATCH (file changed or hash wrong): B_BAD", out)
            self.assertNotIn("NOT RECORDED: B_BAD", out)
            self.assertNotIn("MISMATCH (file changed or hash wrong): C_MISSING", out)


if __name__ == "__main__":
    unittest.main()
