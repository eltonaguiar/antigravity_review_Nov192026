#!/usr/bin/env python3
"""verify_ledger_rowscoped.py — row-scoped contest ledger verification.

The original verify_ledger.py checks `actual_sha in whole_ledger_text`, which cannot
tell WHICH agent a recorded hash belongs to (a hash recorded for agent A would
'verify' agent B if the prefix appeared anywhere). This version parses the table
row, extracts (agent, recorded_hash) as a pair, maps the display name to the
directory slug, and compares THAT row's hash to the committed picks.json.

Exit 1 on any mismatch or unmapped entry.
"""
import hashlib, json, os, re, sys


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


ALIASES = {  # slug -> normalized display name fragment
    "mscopilot": "m365copilotgpt5",
    "gpt41mini": "gpt41mini",
    "gpt53codex": "gpt53codex",
    "qwen36flash": "qwen36flash",
    "glm53flash": "glm53flash",
    "claude52fable": "claude52fable",
    "claudehaiku55": "claudehaiku55",
    "gemini4neon": "gemini4neon",
    "chatgpt6luna": "chatgpt6luna",
    "arenaaiagent": "arenaaiagent",
}


def parse_rows(ledger_text):
    rec = {}
    for line in ledger_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        h = None
        for c in cells:
            m = re.fullmatch(r"`?([0-9a-f]{12})`?", c)
            if m:
                h = m.group(1); break
        if not h:
            continue
        agent = None
        for c in cells:
            mm = re.search(r"\*\*(.+?)\*\*", c)
            if mm:
                agent = mm.group(1); break
        if agent:
            rec[norm(agent)] = h
    return rec


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "CONTEST/ROUND_01_2026-11-23"
    led = open(os.path.join(d, "LEDGER.md"), encoding="utf-8").read()
    rec = parse_rows(led)
    out = {"dir": d, "parsed_rows": len(rec), "rows": []}
    ok_n = 0
    for slug in sorted(os.listdir(d)):
        p = os.path.join(d, slug, "picks.json")
        if not os.path.isfile(p):
            continue
        actual = hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
        sk = norm(slug)
        rhash = rec.get(sk) or rec.get(ALIASES.get(sk, ""))
        if rhash is None:  # tolerant fuzzy map (display name vs slug)
            for name, h in rec.items():
                if sk.startswith(name) or name.startswith(sk) or sk in name or name in sk:
                    rhash = h; break
        ok = rhash == actual
        ok_n += ok
        out["rows"].append({"slug": slug, "ledger_hash": rhash, "actual_sha12": actual, "match": ok})
    out["verified"] = ok_n
    out["total"] = len(out["rows"])
    out["mismatched"] = [r["slug"] for r in out["rows"] if not r["match"]]
    json.dump(out, open("/tmp/contest_ledger_rowscoped.json", "w"), indent=2)
    print(f"{'slug':22s}{'ledger':14s}{'actual':14s}match")
    for r in out["rows"]:
        print(f"{r['slug']:22s}{str(r['ledger_hash']):14s}{r['actual_sha12']:14s}{'YES' if r['match'] else 'NO'}")
    print(f"\nverified {out['verified']}/{out['total']}; mismatched: {out['mismatched']}")
    return 0 if not out["mismatched"] else 1


if __name__ == "__main__":
    sys.exit(main())
