# COMS — how Hermes Agent continues IDE-agent work without VS Code

**Purpose.** Let the operator use Windows freely while an agent keeps working: retrieve the full
conversation (not just the visible window), see remaining todos, and drive coding from a CLI
instead of the IDE.

**Status of this document's claims:** every path, size and command below was verified on this
machine on 2026-11-24, except where marked UNVERIFIED. Where something does not work yet, it says
so rather than describing an aspiration.

---

## 1. The core finding: chat state is per-host, not per-user

VS Code extensions run **on the machine that hosts the workspace**. For a window titled
`[SSH: eltonsGX10]`, Zoo Code, Kilo and Copilot Chat all run on **gx10**, and their state lives in
gx10's `~/.vscode-server/data/User/globalStorage/`. It is **not** in
`%APPDATA%\Code\User\globalStorage` on Windows.

Verified evidence:

| Check | Result |
|---|---|
| `~/.vscode-server` on this Windows box | **absent** — this box is not the SSH host |
| `globalStorage/github.copilot-chat/session-store.db` on Windows | **4,096 bytes, dated Sep 24** — stale/empty, not the live history |
| `globalStorage/kilocode.kilo-code/tasks` on Windows | **204 task dirs**, i.e. history from *local* windows only |
| `globalStorage/zoocodeorganization.zoo-code/tasks` on Windows | **0** — its tasks live in workspaceStorage instead |

So the operator's concern is correct in the important half and wrong in the other half:

- **Correct:** the chat will not be visible in the IDE once the SSH connection is gone, and nothing
  on the Windows side holds it.
- **Not correct:** the conversation is not destroyed. It is on gx10's disk, in the per-task
  directories below, and survives the window closing.

## 2. Where the history actually is (Roo-lineage: Kilo and Zoo Code)

Both Kilo and Zoo Code are Roo Code derivatives and use the same on-disk layout:

```
<globalStorage>/<extension-id>/tasks/<task-uuid>/
    api_conversation_history.json   # the full model-visible transcript
    ui_messages.json                # what the panel renders
    task_metadata.json              # model, provider, timestamps, cost
```

Measured on a real task dir (newest local Kilo task `019d2b38-c360-71d3-8458-0b9389d35530`):

| File | Bytes |
|---|---|
| `api_conversation_history.json` | 448,242 |
| `ui_messages.json` | 325,501 |
| `task_metadata.json` | 6,685 |

Extension IDs: `kilocode.kilo-code`, `zoocodeorganization.zoo-code`.
On the **remote** host the prefix is `~/.vscode-server/data/User/globalStorage/`.

## 3. Retrieving the history (run on the host that has it)

```bash
# newest task id
TASK=$(ls -t ~/.vscode-server/data/User/globalStorage/kilocode.kilo-code/tasks | head -1)

# full transcript as readable text (the model-visible history, not the truncated UI view)
python3 -c "
import json,sys
p='$HOME/.vscode-server/data/User/globalStorage/kilocode.kilo-code/tasks/$TASK/api_conversation_history.json'
for m in json.load(open(p)):
    c=m.get('content')
    if isinstance(c,list): c=' '.join(x.get('text','') for x in c if isinstance(x,dict))
    print(f\"[{m.get('role')}]\n{c}\n\")
"

# metadata: model, timestamps, cost, token counts
python3 -m json.tool ~/.vscode-server/data/User/globalStorage/kilocode.kilo-code/tasks/$TASK/task_metadata.json
```

**Copilot Chat is different.** It has no `tasks/` tree; its store is
`globalStorage/github.copilot-chat/session-store.db` (SQLite). Read it with
`sqlite3 <path> ".tables"` — **UNVERIFIED**, because the only copy reachable from Windows is stale
and the live remote copy is on gx10.

**Reading history from Windows today is not possible.** There is no mount and no SSH route
(see §6). Any instructions claiming otherwise would be wrong.

## 4. Seeing the remaining todos

Three independent sources, in order of reliability:

1. **The repo's own TODO files** — most reliable, because they are committed and reviewable:
   `04-investment-strategy/TODO_2026-11-23.md`, `03-trading-strategies/PROGRESS.md`,
   `NEXT_STEPS.md`, and the `1000_TODOS.json` ledger with `counts.open`.
2. **`task_metadata.json`** — per-task status, model, and timestamps.
3. **The last assistant message** in `api_conversation_history.json` — the agent's own statement of
   what it thinks is left. Treat this as a claim, not as state; agents have repeatedly declared
   queues "exhausted" while hundreds of items were open.

## 5. Driving coding from the CLI instead of the IDE

### Kilo — has a real headless CLI (verified working)

```bash
export PATH="/c/Program Files/Git/cmd:$PATH"   # REQUIRED: see gotcha below
kilo run "message"          # send a message, get the result, no GUI
kilo run -c "message"       # continue the last session
kilo run -s <session-id> "message"   # target a specific session
kilo run --fork -c "..."    # branch before continuing
kilo acp                    # ACP server for programmatic clients
```

Verified output:

```
$ kilo run --pure "Reply with exactly KILO_CLI_OK..."
> code · kilo-auto/free
KILO_CLI_OK
```

**Gotcha (cost one failed run):** `kilo` shells out to `git`. `/mingw64/bin/git` is blocked on this
machine, so it dies with `EPERM: operation not permitted, uv_spawn 'git'`. Prepending
`/c/Program Files/Git/cmd` to `PATH` fixes it. The `EPIPE: broken pipe` line at exit is cosmetic.

### Also available headless on PATH

| Tool | Command |
|---|---|
| Claude Code | `claude` |
| OpenAI Codex | `codex` |
| Hermes | `hermes` |

### Zoo Code and Copilot Chat — no CLI

Neither exposes a headless entry point. Their options are screen automation (fragile: webview
composers reject synthetic focus, and the circular button in Copilot is **send when idle, STOP when
running**) or writing into their task files while the extension holds the same state in memory
(unsupported, will be overwritten — do not do this).

**Recommended:** run the work through `kilo run` / `claude` / `codex` and treat the IDE panels as
optional read-only supervision. The output lands as commits and artifacts either way.

## 6. The blocker, stated plainly

**gx10 is unreachable from this Windows box:**

```
$ getent hosts gx10 eltonsGX10 eltonsgx10   -> no DNS, all three
$ ssh gx10                                  -> Could not resolve hostname gx10
$ cat ~/.ssh/config                         -> no Host entries
```

`E:` is a local drive (`net use` shows no network connections), so it is not a window onto gx10.
Nothing in this document can run against the remote history until SSH works.

**To unblock, one of:**

1. Add a `~/.ssh/config` Host entry with gx10's real address and key auth, then
   `ssh gx10 'cd ~/findtorontoevents_antigravity.ca && kilo run -c "..."'` — this single command
   gives headless control *and* access to the remote task history, with VS Code closed.
2. Mount/sync the remote `~/.vscode-server/data/User/globalStorage` to Windows.
3. Run Hermes on gx10 itself.

## 7. What this buys, concretely

| Goal | Today | After SSH |
|---|---|---|
| Full transcript, not just the window | only local windows | read any remote task dir |
| History survives closing the SSH window | already true on gx10's disk | readable and searchable |
| Agent keeps coding while operator uses Windows | screen automation only | `kilo run` / `claude` / `codex`, no GUI |
| Remaining todos | repo TODO files (reliable) | plus per-task metadata |
| No misclicks on send/stop/mic | not achievable | eliminated for Kilo |

Paper only. Zero capital. Not investment advice.
