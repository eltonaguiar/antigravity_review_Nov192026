#!/usr/bin/env python3
"""assert_quoted_numbers - every figure the published page rests on must exist
as a NUMBER in the artifacts, not as a substring.

WHY NOT grep
    The first version of this gate grepped the JSON for "226.80" and "1.50" and
    reported both as unsourced. Both are present - the artifact stores 226.8 and
    1.5, because JSON does not preserve trailing zeros. A gate that fails on
    formatting is a gate that gets deleted.

    So: parse the JSON, collect every numeric leaf, and compare as floats.

USAGE
    python3 PLAN/tools/assert_quoted_numbers.py ARTIFACT.json [MORE ...] -- 9.18 8.56 44.61

EXIT
    0 = every quoted number is present in at least one artifact, 1 = missing.
"""

import json
import sys


def numbers(obj, out):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.add(round(float(obj), 4))
    elif isinstance(obj, dict):
        for v in obj.values():
            numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            numbers(v, out)


def main(argv):
    if "--" not in argv:
        print("usage: assert_quoted_numbers.py ARTIFACT... -- NUM...")
        return 2
    cut = argv.index("--")
    artifacts, quoted = argv[:cut], argv[cut + 1:]

    have = set()
    for p in artifacts:
        numbers(json.load(open(p)), have)

    missing = []
    for q in quoted:
        try:
            want = round(float(q), 4)
        except ValueError:
            print(f"  SKIP  {q} (not a number)")
            continue
        if want in have:
            print(f"  ok    {q}")
        else:
            print(f"  MISS  {q}  <- quoted in prose, absent from every artifact")
            missing.append(q)

    if missing:
        print(f"\nFAIL: {len(missing)} quoted number(s) unsourced: {missing}")
        return 1
    print(f"\nok: all {len(quoted)} quoted numbers traced to an artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
