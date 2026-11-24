# HERMES → continue KILO's work (CLI, headless, SSH-survivable)

**Goal:** Hermes Agent picks up KILO CODE's work with **full chat history + remaining todos**, and controls the coding
**via the `kilo` CLI** (not the VS Code chat), so a busy Windows user can close the SSH/VS Code window without killing the run.
Written 2026-11-24 by KILO CODE. Paper only, zero capital, not investment advice.

## 0. Facts (verified on this host)
- CLI: `/home/eaguiar2015/.hermes/node/bin/kilo` (also `kilocode`), version **7.8.27**.
- Full chat history store: **`/home/eaguiar2015/.local/share/kilo/kilo.db`** (SQLite, ~4.3 GB, WAL). Read it **read-only**.
  Tables: `session`, `message`, `part`, `todo`, `project`, `session_message`, `kilo_board_message`, `kilo_continuation_intent`.
- Session-turn spool: `/home/eaguiar2015/.local/state/kilo/session-turn/`.
- KILO's worktree: `/home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw`.
- KILO main session id (this thread): **`ses_dfa45921fffe4a9cuWq0t7OS41`** (newer related sessions exist; pick by newest message — see §1).
- Detachers available: `tmux`, `screen`, `systemctl --user`.

## 1. Retrieve the ENTIRE chat history (all turns, not just a window)
**Simplest — official exporter (full JSON transcript):**
```bash
kilo export ses_dfa45921fffe4a9cuWq0t7OS41 --sanitize > /tmp/kilo_transcript.json
```
Find the right session id if unsure (read-only SQL — never lock the live DB):
```bash
sqlite3 "file:$HOME/.local/share/kilo/kilo.db?mode=ro" \
 "select id,title,directory,time_updated from session
  where directory like '%vanilla-handsaw%' order by time_updated desc limit 10;"
```
Or list sessions via CLI: `kilo session list` (see `kilo session --help`).
**Raw DB reconstruction** (message→part, ordered):
```bash
sqlite3 "file:$HOME/.local/share/kilo/kilo.db?mode=ro" \
 "select m.id, m.time_created, json_extract(m.data,'\$.role'), substr(m.data,1,400)
    from message m where m.session_id='ses_dfa45921fffe4a9cuWq0t7OS41'
   order by m.time_created;"
```
`message.data`/`part.data` are JSON blobs (role, text, tool calls, file diffs). Prefer `kilo export` for a clean transcript.

## 2. See KILO's remaining todos
**Live todo table (state=open/claimed/extended):**
```bash
sqlite3 "file:$HOME/.local/share/kilo/kilo.db?mode=ro" \
 "select content,status,priority,position from todo
   where session_id='ses_dfa45921fffe4a9cuWq0t7OS41' and status!='completed'
   order by position;"
```
**File-backed todos / plans (also authoritative):**
- `findtorontoevents_antigravity.ca/TODOS_ACTIVE.json`, `.todo_wakeup_state.json`
- `findtorontoevents_antigravity.ca/plans/*.json`
- `findtorontoevents_antigravity.ca/1000_TODOS.json`  (the 1000-cell backlog; current: 106 killed / 891 blocked / 0 open)
- Review repo: `antigravity_review_Nov192026/34_FINAL_PICKS_2026-11-23/KILOCODE_VSCODE/FINAL_FINDINGS_AND_RANKING.md`,
  `PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT/`, `CONTEST/_incoming/KILOCODE_VSCODE/`.

## 3. Control coding autonomously via CLI (not VS Code)
**One-shot prompt into the existing session (headless):**
```bash
cd /home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw
kilo run -s ses_dfa45921fffe4a9cuWq0t7OS41 \
  --agent orchestrator --model <provider>/<model> \
  "Continue: take the next unblocked item that needs no new market data; commit each block; push; then post a COMS update (plan/achievements/repos+sha/test-plan)."
```
- `-c` continues the last session; `-s <id>` continues a specific one; `--fork` forks before continuing.
- `--format json` → machine-parseable event stream (for orchestration/parsing).
- `--agent <name>` selects the agent; `--model provider/model` pins the model; `--variant high` for reasoning effort.
- Headless server mode (persistent, multi-attach): `kilo serve --port 4096 &` then
  `kilo run --attach http://localhost:4096 -s <id> "..."`.

## 4. Survive SSH / Windows disconnect (the core requirement)
The agent must run on the **Linux host** as a detached process; the Windows/SSH/VS Code window is only a viewport.
**Closing the SSH path does NOT stop a tmux/systemd process.** (VS Code *integrated* chat will not persist — that's why we use CLI.)

**tmux (simplest):**
```bash
tmux new -d -s kilo 'cd /home/eaguiar2015/findtorontoevents_antigravity.ca/.kilo/worktrees/vanilla-handsaw && \
  kilo run -s ses_dfa45921fffe4a9cuWq0t7OS41 --agent orchestrator "resume; continue to completion"'
tmux ls; tmux attach -t kilo      # reattach from any SSH session; Ctrl-b d to detach
```
**systemd user service (survives logout; auto-restart):**
```bash
systemd-run --user --unit=kilo-hermes --setenv=HOME=$HOME -d \
  /home/eaguiar2015/.hermes/node/bin/kilo run -s ses_dfa45921fffe4a9cuWq0t7OS41 --agent orchestrator "resume"
# or a ~/.config/systemd/user/kilo-hermes.service with Restart=always + `loginctl enable-linger $USER`
```

## 5. Autonomy loop pattern (bounded, safe)
A wrapper that re-invokes the CLI every N minutes (or after each block), each call doing ONE unit then reporting:
```
while open_work; do
  kilo run -s <id> --agent orchestrator --format json "do the next unblocked item; commit+push; post COMS 15-min status"
  sleep 900
done
```
Prefer `schedule_wakeup`/`cron` inside a Kilo session over a raw shell loop, so the goal suspends instead of spinning. Run the
whole loop in tmux/systemd so SSH closure is irrelevant. Enforce the **15-min COMS cadence** the user set.

## 6. Safety rails (carry these over — non-negotiable)
- **Only push your own changes**; never push a branch containing other authors'/agents' commits; no `--force`; no `git reset --hard`/`clean -fd` without explicit user approval.
- **Commit each block before starting the next.** Every fix gets a matching `.MD` in `updates/`.
- **Never read or expose `/home/eaguiar2015/dbpasses.txt`.**
- **Verify before citing:** `git ls-remote` == local sha after every push; units (percent vs fraction), population (ALL vs dated), and window alignment on every comparison.
- **A KILL / recorded BLOCKED is a valid completion** for the 1000-cell backlog; do not fabricate n to pass.
- Main repo pushes race (multiple agents) → use per-cell union merge + retry; land small additive files via the GitHub API to avoid clobbering.

## 7. Continuity snapshot (pinned by KILO at handoff)
- **Main repo** `eltonaguiar/findtorontoevents_antigravity.ca`: census on `main` `1000_TODOS` (106 killed / 891 blocked / 0 open), data-aware generator; branches `feat/coms-final-notes-2026-11-20`, `research/honest-read-2026-11-23`, `research/us-vs-cad-wrapper-2026-11-24`, `research/sweep-genfix`, `fix/insufficient-vs-blocked`.
- **Review repo** `eltonaguiar/antigravity_review_Nov192026` `main`: `34_FINAL_PICKS_2026-11-23/KILOCODE_VSCODE/FINAL_FINDINGS_AND_RANKING.md`, `PROVEIT/PROVEIT_24-11-2026_KILOCODE_AGENT/`, `CONTEST/_incoming/KILOCODE_VSCODE/picks.json`, `docs/PROVEIT_KILOCODE.html`.
- **Answer (stable):** 0 investable — CAD-listed low-cost index ETF (or 60/40) is the only defensible real-money action; 891 cells blocked pending operator bars/fills.

## 8. One-command bootstrap for Hermes
```bash
bash /home/eaguiar2015/antigravity_review_Nov192026/hermes_start_kilo.sh
```
(exports the transcript, prints remaining todos, and launches a detached tmux `kilo run` loop on the KILO session.)

*Paper only. Not investment advice.*
