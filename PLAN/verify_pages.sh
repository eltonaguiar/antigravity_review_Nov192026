#!/usr/bin/env bash
# Verify that every path the PROVEIT deliverable claims is actually served by
# GitHub Pages.
#
# WHY THIS EXISTS
#   The Pages workflow publishes `path: docs` ONLY. Everything under PROVEIT/
#   sits outside that tree and returns 404 no matter what the README says. A
#   reviewer clicking a README link gets a 404 and concludes the work is fake;
#   the work was real, the publishing contract was simply ignored. This script
#   makes that gap impossible to miss, and - just as importantly - does not
#   pretend files are live before they are.
#
# THREE CLASSES, NOT TWO
#   ALREADY_LIVE  served from main today; must stay 200
#   NEW_IN_PR     added by this PR inside docs/; 404 before merge, 200 after
#   NEVER_SERVED  outside docs/; 404 forever by design
#
# USAGE
#   ./PLAN/verify_pages.sh        # after merge: everything in NEW_IN_PR must be 200
#   ./PLAN/verify_pages.sh --pre  # before merge: NEW_IN_PR must still be 404
#
# EXIT
#   0 = every expectation met, 1 = at least one mismatch.

set -uo pipefail

BASE="https://eltonaguiar.github.io/antigravity_review_Nov192026"
MODE="${1:-}"

ALREADY_LIVE=(
  "index.html"
  "PROVEIT_KILOCODE.html"
)

NEW_IN_PR=(
  "PROVEIT/index.html"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/README.md"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_2026-11-24T0350Z.json"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/paramscan_2026-11-24T0350Z.json"
)

# Outside docs/ -> unreachable by the current workflow. Listed so nobody
# "fixes" a broken link by pointing it at a path that can never serve.
NEVER_SERVED=(
  "PROVEIT/README.md"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/README.md"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/sim_2026-11-24T0350Z.json"
  "PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT/paramscan_2026-11-24T0350Z.json"
)

fail=0
check () {
  local path="$1" want="$2" what="$3"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 -L "$BASE/$path?_=$(date +%s)")
  local verdict="ok"
  [[ "$code" != "$want" ]] && { verdict="MISMATCH"; fail=1; }
  printf '  %-9s %-12s want %s  got %s  %s\n' "$verdict" "$what" "$want" "$code" "$path"
}

echo "Pages root : $BASE"
echo "Publish    : docs/ only  (.github/workflows/pages.yml -> path: docs)"
if [[ "$MODE" == "--pre" ]]; then
  echo "Mode       : PRE-MERGE - NEW_IN_PR must still be 404"
else
  echo "Mode       : POST-MERGE - NEW_IN_PR must be 200"
fi
echo

echo "--- ALREADY_LIVE (main, expected 200) ---"
for p in "${ALREADY_LIVE[@]}"; do check "$p" "200" "live"; done

echo
if [[ "$MODE" == "--pre" ]]; then
  echo "--- NEW_IN_PR (expected 404 until merge) ---"
  for p in "${NEW_IN_PR[@]}"; do check "$p" "404" "pending"; done
else
  echo "--- NEW_IN_PR (expected 200) ---"
  for p in "${NEW_IN_PR[@]}"; do check "$p" "200" "served"; done
fi

echo
echo "--- NEVER_SERVED (expected 404 by design) ---"
for p in "${NEVER_SERVED[@]}"; do check "$p" "404" "by-design"; done

echo
if [[ $fail -eq 0 ]]; then
  echo "RESULT: all expectations met."
else
  echo "RESULT: MISMATCH - do not claim these files are published."
fi
exit $fail
