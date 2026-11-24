#!/usr/bin/env bash
# hermes_start_kilo.sh — bootstrap Hermes to continue KILO CODE's work via the CLI.
# Usage: bash hermes_start_kilo.sh [--loop] [sessionID]
#   default: export transcript + show remaining todos + start a DETACHED tmux resume (one block).
#   --loop : keep re-invoking the CLI every 15 min (15-min COMS cadence) inside tmux.
set -euo pipefail
KILO="/home/eaguiar2015/.hermes/node/bin/kilo"
DB="$HOME/.local/share/kilo/kilo.db"
WT="/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw"
AGENT="${KILO_AGENT:-orchestrator}"
MODEL="${KILO_MODEL:-}"           # e.g. deepseek/deepseek-flash ; empty = inherit default
LOOP=0; SID=""
for a in "$@"; do case "$a" in --loop) LOOP=1;; *) SID="$a";; esac; done

# find newest session for this worktree if not given
if [ -z "$SID" ]; then
  SID="$(sqlite3 "file:${DB}?mode=ro" "select id from session where directory like '%vanilla-handsaw%' order by time_updated desc limit 1;" 2>/dev/null || true)"
fi
[ -z "$SID" ] && { echo "ERROR: no session id found; pass one explicitly." >&2; exit 2; }
echo "KILO session: $SID"

TS="$(date -u +%Y-%m-%dT%H%MZ)"
mkdir -p "$HOME/kilo_handoff"
echo "Exporting full transcript -> $HOME/kilo_handoff/transcript_${TS}.json"
"$KILO" export "$SID" --sanitize > "$HOME/kilo_handoff/transcript_${TS}.json" 2>/dev/null || echo "(export failed; use direct SQL fallback)"

echo "=== Remaining todos (from kilo.db) ==="
sqlite3 "file:${DB}?mode=ro" \
 "select status||' | '||priority||' | '||content from todo where session_id='${SID}' and status!='completed' order by position;" 2>/dev/null || echo "(no todos in DB for this session)"

PROMPT="Continue KILO's work: read HERMES_HANDOFF_KILO_RUNBOOK_2026-11-24.md; take the next unblocked item that needs no new market data; commit each block; push; then post a COMS 15-min status (plan/achievements/repos+sha/test-plan). Only push your own changes; verify remote sha==local."

if [ -n "$MODEL" ]; then MODELARG=(--model "$MODEL"); else MODELARG=(); fi

run_once() { cd "$WT"; "$KILO" run -s "$SID" --agent "$AGENT" "${MODELARG[@]}" "$PROMPT"; }

if [ "$LOOP" -eq 1 ]; then
  echo "Starting DETACHED tmux loop (every 15 min). Reattach: tmux attach -t kilo"
  tmux kill-session -t kilo 2>/dev/null || true
  tmux new -d -s kilo "while :; do ( cd '$WT' && '$KILO' run -s '$SID' --agent '$AGENT' ${MODEL:+(--model '$MODEL')} \"$PROMPT\" ); sleep 900; done"
  echo "tmux session 'kilo' started. Close SSH/VS Code freely; it keeps running on this host."
else
  echo "Starting DETACHED one-block resume in tmux (session 'kilo')."
  tmux kill-session -t kilo 2>/dev/null || true
  tmux new -d -s kilo "cd '$WT' && '$KILO' run -s '$SID' --agent '$AGENT' ${MODEL:+(--model '$MODEL')} \"$PROMPT\""
  echo "Attach to watch: tmux attach -t kilo  (Ctrl-b d to detach). SSH closure will NOT kill it."
fi
