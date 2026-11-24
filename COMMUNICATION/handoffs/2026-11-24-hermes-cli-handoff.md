# Hermes handoff: continue this work over COMS, drive coding by CLI (not VS Code SSH)

**From:** Kilo Code (Code mode) · **To:** Hermes Agent · **Date:** 2026-11-24

Host `gx10-c9b9`, worktree `findtorontoevents_antigravity.ca`. The user is on Windows
and wants to keep using Windows freely while work continues. They are right that a
VS Code Remote-SSH chat window dies when the SSH path closes -- the conversation
lives in the editor's client state, not on the server. The fix is to move the
*durable* state off the editor and onto disk + Git, and use COMS only to wake things up.

## 0 The one principle

> **Git is the durable drop; MQTT is only the wake-up.**

Never put chat history, todos, or code in an MQTT payload as the source of truth.
Put them in files (committed or at least on disk), then send a short COMS message
that says "new work at <path>, see <sha>". If the bus drops the message, nothing is
lost -- the next `git pull` recovers everything.

## 1 Where "your entire chat history" lives

A model's context window is not an archive. This session's durable record is:

| State | Where it lives | How Hermes gets it |
|---|---|---|
| Chat history (all of it, not one window) | The agent's own session logs / conversation store on disk, plus the committed artefacts each block produced | Read the session store, then read the repo: every block's output is a file or a commit |
| Todos / remaining work | The todo list (this session's reminders) **and** the `updates/*.md` notes | `git log --oneline` + the latest `updates/` note + the todo list |
| Code state | `origin/main` | `git fetch && git log --oneline origin/main -20` |
| Cross-agent messages | COMS topics (transient) + `COMMUNICATION/handoffs/*.md` (durable) | `coms check`, then read the handoff file |

**Rule:** if Hermes needs it after a restart, it must be a file. A summary of my
work that only exists in this chat is unrecoverable once the window closes -- so
the handoff is written down (this file) rather than spoken.

## 2 Identity on the bus

Inbox topic is `inbox/<host>/<worktree>/<agent>`:
- host = `gx10-c9b9`
- worktree = `findtorontoevents-antigravity-ca` (dots become dashes -- the client does this, do not hand-write it)
- agent = a seat unique within the worktree, e.g. `hermes-cli`

Check first, because the broker does **not** enforce unique seats:
```bash
coms roster                      # is "hermes-cli" free?
coms register --agent hermes-cli --goal "continue Kilo's work via CLI" \
  --todo "read handoff; run tests" --done ""
```

## 3 Running code so it survives a closed SSH window

The user closing the Windows terminal must not kill the job. Use a detached
multiplexer or a transient unit, then drive the agent inside it:

```bash
# durable session
tmux new-session -d -s work -c /home/eaguiar2015/findtorontoevents_antigravity.ca
tmux send-keys -t work 'codex' Enter        # or: claude / gemini / qwen / opencode
tmux capture-pane -pt work | tail -40       # read output without attaching

# or a transient systemd unit (survives logout, logs to journal)
systemd-run --user --unit=kilo-continue --collect \
  --working-directory=/home/eaguiar2015/findtorontoevents_antigravity.ca \
  codex exec "continue from COMMUNICATION/handoffs/2026-11-24-hermes-cli-handoff.md"
journalctl --user -u kilo-continue -n 50    # inspect later
```

CLI agents verified on this host: `codex`, `claude`, `gemini`, `qwen`, `opencode`
(all on PATH). Prefer their non-interactive/exec subcommands for automation and
`tmux capture-pane` when you need to read an interactive session.

## 4 The loop

1. `coms check --agent hermes-cli --wait 3` and `git fetch origin`.
2. Read the newest `COMMUNICATION/handoffs/*.md` and the newest `updates/*.md`.
3. Do the work in a detached session (section 3), committing each block before the next.
4. Push, then announce -- **retained**, because live-only `send` is discarded if nobody is listening:
   ```bash
   coms send --retain mentions/all "KILO->HERMES: block done, main @ $(git rev-parse --short origin/main); see updates/<file>.md"
   ```
5. Update `registry` with new `--todo`/`--done`.

## 5 What to watch for

- `coms send` without `--retain` prints `sent` even when dropped. Always `--retain` for handoffs.
- Retained topics are last-writer-wins: to correct an earlier message, republish on the same topic, and put the correction in a new note.
- Do not `inbox/gx10-c9b9/#` -- subscribe only to your inbox, `.../all`, and `mentions/all`.
- Do not run `check_active_picks.py` or `alpha_engine/smart_picks_engine.py` unless the user asks.
- Branch protection on `main` is OFF, so nothing enforces review: still use a clean branch + `--match-head-commit` merges.
- Never `git push` other agents' commits, and never `reset --hard` / `push --force` / `clean -fd`.
- Two agents writing to the same folder path will collide (it happened today with a `PROVEIT_...KILOCODE_AGENT` folder): check `git ls-tree origin/main` before choosing a path, and rebase rather than overwrite.

## 6 Current state at handoff

Main repo: coverage arc instrumented and labelled (`COVERAGE-LIMITED`); the excluded-row measurement is wired and awaiting the first live build -- check with
`python3 tools/check_excluded_summary.py --payload https://findtorontoevents.ca/audit/data/dashboard_data.json --ledger audit_dashboard/data/audit3_ledger.json`.
Review repo: `PROVEIT/PROVEIT_24-11-2026KILOCODE_AGENT_SIM/` pushed at `8a06a29`.
Programme tally (must not change): `0 INVESTABLE / 11 NOT_INVESTABLE / 3 UNKNOWN (14 rows)`.
