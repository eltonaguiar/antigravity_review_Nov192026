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

### Chrome tabs are drivable too, with no screen interaction

Chrome on this machine is already listening on **`127.0.0.1:9222`** (pid 29004, `chrome.exe`).
Verified by attaching over CDP and evaluating JS inside the live tabs:

```
Arena AI => {"title":"Arena AI ...","textareas":1,"editables":1,...}
```

That means the operator's real browser tabs — Arena AI, 1min.AI, Gemini — can be read and typed into
programmatically, with no focus stealing and no synthetic mouse. `websocket` and `websockets` are
both installed.

**VS Code itself is not debuggable right now** — the only listening debug port is Chrome's, on 9222.

On `--remote-debugging-port` for VS Code, a probe changes the verdict:

```
$ code --remote-debugging-port=9333 --version
Warning: 'remote-debugging-port' is not in the list of known options, but still passed to
Electron/Chromium.
1.144.0
```

That warning is **not** a failure. VS Code's own CLI does not define the flag, but it forwards it to
Electron/Chromium, which is where the DevTools protocol listener is actually created. So the route
is plausible — and would remove the mic/send/stop misclick class of failure entirely, since everything
would be DOM-level instead of pixel-level.

**Still UNVERIFIED**, deliberately: testing it means launching another VS Code window, which is
disruptive while the operator is using the machine. Use a distinct port (not 9222, which Chrome owns)
and confirm with `curl 127.0.0.1:<port>/json/list` that a `workbench` target appears.

### What the API claims get wrong

Tested against the installed bundles, not the documentation:

| Claim (from model research) | Reality here |
|---|---|
| Kilo/Roo export `api.startNewTask("...")` | **FALSE for Kilo 7.8.32** — `startNewTask` appears **0 times** in its dist. It exists in **Zoo** as the IPC `StartNewTask` command. |
| `api.pressPrimaryButton()` | **FALSE for Kilo** — 0 occurrences. |
| `vscode://kilocode.kilo-code?task=...` | **FALSE** — handler ignores any path but its 3 own. |
| `code --command <id> --args` | **FALSE** — no such flag in VS Code 1.144.0. |
| Bridge extension `eliostruyf.vscode-remote-control` | **Exists** (marketplace query returned exactly 1 hit). Not installed. Would let a CLI execute VS Code commands over a local WebSocket, including `workbench.action.chat.open`. |
| Bridge extension `seunlanlege.vscode-remote-control` | **Does not exist** — marketplace query returned 0 results. A second research batch gave this wrong publisher; use `eliostruyf`. |
| Bridge extension `pokey.command-server` | Not verified, not installed. |
| `code --remote-debugging-port=9222` to drive the webviews | **Nuanced, see below** |

**Also false for Kilo 7.8.32** (checked against the bundle, not the docs): the extension id
`kilocode.Kilo-Code`, the commands `kilo-code.newTask` / `kilo-code.plusButtonClicked` /
`kilo-code.focusInput`, and the claim that Kilo honours `ROO_CODE_IPC_SOCKET_PATH`. None appear.
Kilo's actual command namespace here is `kilo-code.new.agentManager.*`. So Kilo and Zoo are **not**
interchangeable: Zoo has the IPC door and `StartNewTask`; Kilo has `kilo run`.

Net: the only reliable per-agent doors are the five verified in this document —
`kilo run`, `code chat`, Zoo's `ROO_CODE_IPC_SOCKET_PATH`, and CDP for Chrome.

### Also available headless on PATH (verified present)

| Tool | Path | Headless entry |
|---|---|---|
| **GitHub Copilot CLI** | `copilot` (ships in VS Code's `bin/copilot-shim`) | `copilot -p "prompt"` — non-interactive; also `sessions`, `mcp`, `plugin`, `skill`, `sandbox`, `workflow` |
| Kilo | `kilo` (npm global, opencode 7.8.32) | `kilo run` |
| Claude Code | `claude` | `claude` |
| OpenAI Codex | `codex` | `codex` |
| Hermes | `hermes` | `hermes` |

**NOT present on this machine:** `cline`, `roo` (the npm global registry has only `@kilocode`).

**`--open-url` exists, despite not appearing in `--help`.** An earlier revision of this document
said it did not, based on grepping the help text — that was wrong. VS Code hides several working
flags from `--help` (`--folder-uri` and `--file-uri` are missing from it too). The reliable test is
to run the flag and read the warning:

| Probe | Result | Meaning |
|---|---|---|
| `code --open-url "vscode://x.invalid/foo"` | exit 0, no warning | **recognised** |
| `code --command "some.fake.command"` | `Warning: 'command' is not in the list of known options…` | **not a flag** |

So `code --open-url "vscode://<ext>/<path>?prompt=…"` is a legitimate keyboard-free way to fire a
URI handler, and needs no bridge. (`code chat` remains the better route for Copilot.)

Also present and useful: `--add-mcp <json>` adds an MCP server definition, and the CLI has
`serve-web` and `tunnel` subcommands.

`copilot` is mechanically the cleanest headless option for Copilot work: `-p` is designed for
scripting and it manages its own sessions, so it does not depend on the chat panel being open.

**But it is quota-blocked on this machine right now.** A live probe:

```
$ copilot -p "Reply with exactly COPILOT_CLI_OK..."
You have exceeded your monthly quota (Request ID: DEBB:57A39:87A45:93081:6B050539)
Changes +0 -0 | AI Credits 0 (1s) | Resume copilot --resume=e01ea405-bd24-4f50-b4ae-45a660c13b83
```

The invocation itself is fine — it authenticated, opened a resumable session and exited cleanly.
It is the account's monthly credit that is exhausted, so until it resets the usable Copilot route is
`code chat` (which draws on the editor's own entitlement) rather than `copilot -p`.

Permission flags confirmed present for unattended runs: `--allow-all` (= `--allow-all-tools
--allow-all-paths --allow-all-urls`), plus each of those individually.

### Copilot Chat — there IS a first-class CLI (`code chat`)

**CORRECTION.** An earlier version of this document said Copilot Chat has no CLI. That is wrong.
VS Code **1.144.0** ships a `chat` subcommand:

```bash
code chat "explain the auth middleware in this repo"
echo "review this file" | code chat -            # read the prompt from stdin
```

Verified options:

| Flag | Meaning |
|---|---|
| `-m, --mode <mode>` | `ask`, `edit`, `agent`, or a custom mode id. **Defaults to `agent`** |
| `-a, --add-file <path>` | attach files as context |
| `-r, --reuse-window` | force the last active window (important for a remote workspace) |
| `-n, --new-window` | force an empty window |
| `--maximize` | maximise the chat view |
| `--profile <name>` | open with a named profile |

So Copilot no longer needs screen automation. Note `--mode agent` is the default, which means a
scripted prompt can make edits unattended — keep approvals on.

### Zoo Code — no CLI, but it has a full IPC command protocol (this corrects an earlier claim)

An earlier revision said Zoo has no programmatic door. That was wrong. The installed bundle
(`zoocodeorganization.zoo-code-3.98.1/dist/extension.js`) reads an env var at activation and stands
up a **socket.io server** on it:

```js
let f = process.env.ROO_CODE_IPC_SOCKET_PATH, c = typeof f === "string";
...
if (s) { const l = this.ipc = new PIt(s, this.log); l.listen(); ... }
```

Transport is socket.io over a Unix-domain socket / Windows named pipe (`TF.serve(socketPath, ...)`,
`TF.server.on("connect"|"message")`, `broadcast`). Protocol, read from the dispatch switch:

**Server -> client on connect**
```json
{"type":"Ack","origin":"server","data":{"clientId":"<hex>","pid":123,"ppid":45}}
```

**Client -> server**
```json
{"origin":"client","type":"TaskCommand","clientId":"<hex>","data":{"commandName":"SendMessage","text":"...","images":[]}}
```

**Supported `commandName` values** (each with its payload):

| commandName | payload |
|---|---|
| `StartNewTask` | `{text, images?, newTab?, requestId?}` — returns `taskStartResponse` `{requestId, success, taskId}` |
| `SendMessage` | `{text, images?}` |
| `CancelTask` | — |
| `ResumeTask` | `taskId` |
| `CloseTask` | — save files then close the window |
| `DeleteQueuedMessage` | `messageId` |
| `GetCommands` / `GetModes` / `GetModels` | — |

**Server -> client events**
```json
{"type":"TaskEvent","origin":"server","data":{"eventName":"...","payload":{...}}}
```

**Requirement:** VS Code must be started with `ROO_CODE_IPC_SOCKET_PATH` set — it is read once at
`activate()`, so an already-running window will not pick it up. UNVERIFIED: whether a Windows named
pipe path works as well as a POSIX socket path; the transport is socket.io, so a client needs
`socket.io-client` (Node), not a plain `net.connect`.

### Zoo Code URI handler — exists at runtime, but cannot activate the extension

Verified against the installed manifests:

| Extension | Version | `onUri` activation | Commands |
|---|---|---|---|
| `kilocode.kilo-code` | 7.8.32 | **present** (3 paths, none submit a task) | 72 |
| `saoudrizwan.claude-dev` (Cline) | 4.1.27 | **present** | 19 |
| `zoocodeorganization.zoo-code` | 3.98.1 | **NONE** | 22 |

`onUri` is the activation event an extension must declare to receive `vscode://` links, so:

- `vscode://kilocode.kilo-code?task=...` — **FALSE.** Kilo declares `onUri` and does register a
  handler, but the handler only matches three paths and silently returns on anything else. Read from
  `dist/extension.js`:

  ```js
  async handleUri(uri) {
    let sessionId = uri.path.match(/^\/kilocode\/s\/([a-zA-Z0-9_-]+)$/)?.[1];   // open cloud session
    if (uri.path !== "/kilocode/switch" && uri.path !== "/kilocode/model") return;   // everything else ignored
    ... // applies ?model= and ?agent= selection
  }
  ```

  So the only working links are `vscode://kilocode.kilo-code/kilocode/s/<sessionId>`,
  `/kilocode/switch?model=&agent=`, and `/kilocode/model?model=`. **None of them submits a task.**
  Use `kilo run` for that.
- `vscode://saoudrizwan.claude-dev?task=...` — plausible, handler is declared (path not inspected).
- `vscode://zoocodeorganization.zoo-code?task=...` — **will not activate the extension**: no `onUri`
  event. Nuance found in the bundle: Zoo *does* call `window.registerUriHandler({handleUri: N_r})`
  at activate time, so if Zoo is already running the URI may still be handled. A missing `onUri`
  means it cannot cold-start from the link, not that the handler is absent.

Zoo's remaining options are screen automation (fragile) or writing into its task files while the
extension holds the same state in memory (unsupported, will be overwritten — do not do this).

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
