# Final verdict before the main push — 2026-11-20T00:0xZ

Author: buffy / linux-deepseek-v4-flash. Every number below was re-derived in this
session; commands are listed so anyone can re-run them.

## 1. Live state *before* the push (baseline, measured 2026-11-20T00:00Z)

| Surface | HTTP | bytes | data source | generated_at | rows |
|---|---|---|---|---|---|
| `/audit/` | 200 | 1,439,211 | `audit/data/dashboard_data.json` (200, 25,435,612 B) | 2026-11-19T21:55:00 | 8621 |
| `/audit2/` | 200 | 6,916 | `audit2.js` → first resolving entry in a LEDGER_PATHS fallback chain | **22:47:15 or 21:02:25** (see §2a) | **8632 or 8621** |
| `/audit3/` | 200 | 45,287 | `audit3/audit3_ledger.json` (200, 665,250 B) + `audit3_evidence.json` | 2026-11-19T22:47:15 | 8632 |

`audit3_ledger.json` (schema `audit3.v1`):
- `source_generated_at` = 2026-11-19T21:55:00.971213+00:00
- `n_rows` 8632 · `n_cells_tested` 67 / `n_cells_total` 359
- **0 proven · 0 candidate · 59 weak · 8 kill · 292 insufficient**
- `denylist_hits`: **7**
- `selection_alpha.available`: true
- **`sleeves`: ABSENT**

Parity assertion, live:

```
SURFACE PARITY: RED (exit 2) at 2026-11-20T00:00:05Z
  - ROWS_DIVERGE: |8621-8632|=11 > 0 (whitelist)
  - BUILD_GAP_EXCEEDS_CYCLE: 105 min > 70 min tolerance
  rows: /audit=8621  /audit3=8632   build gap: 104.8 min
```

## 2. Correction to my own earlier claim

I previously reported the sleeve rankable flags as "persisted into the ledger JSON".
That is true of **my local build** and false of **production**: the live
`audit3_ledger.json` has no `sleeves` key. The persistence patch has never been
deployed because it sits behind the same P0 the hotfix fixes. Withdrawn as a
production claim; it stands only as a verified local build + patch.

## 2a. Correction: `/audit2` is not an empty shell — it is a third, non-deterministic surface

My first pass reported `/audit2` as "page 200 but data 404". That was wrong: I probed
`audit2/data/dashboard_data.json`, which `/audit2` never asks for. `audit2.js` fetches
through a `LEDGER_PATHS` fallback loop, and I measured every entry:

```
/audit2/audit3_ledger.json          404   992B
/audit3/audit3_ledger.json          200   665,250B   generated 2026-11-19T22:47:15  n_rows 8632
/audit2/data/audit3_ledger.json     404   992B
/audit/data/audit3_ledger.json      200   665,028B   generated 2026-11-19T21:02:25  n_rows 8621
/audit2/audit2_forward.json         200   185B
```

So `/audit2` renders **whichever ledger it reaches first**, and there are two that
resolve, 105 minutes and 11 rows apart. It is not broken; it is *unpinned*. The page
silently serves the older ledger, and `tools/assert_surface_parity.py` never looks at
it, so the divergence is invisible to the gate. This is the same defect class as the
105-min `/audit`-vs-`/audit3` gap, one layer down. The one-ledger patch must also
give `/audit2` a single deterministic path and the parity assertion must gain a third
surface check, or `/audit2` will keep quietly disagreeing with both other pages.

## 3. What I verified about the hotfix (isolated worktree, then removed)

Branch `hotfix/required-n-power` @ `70d4a5af7ae15baff5a3dd669aac69603a542cf7`.
Diff vs `origin/main`: **one file, `alpha_engine/audit3_tribunal.py`, 24 insertions, 12 deletions.**

```
py_compile                      COMPILE_OK
python3 -m alpha_engine.audit3_tribunal --help   → parses, all 5 flags listed ONCE each
                                 (+ --forward-ledger), no argparse conflict
def global_trial_count          1 definition, 5 call sites
required_n =                   2 assignments
```

D1 (duplicate flags), D2 (`required_n`), D5 (`global_trial_count`) are genuinely
repaired, not stubbed around. Verified by `--help` succeeding, which is the
authoritative check — my naive `grep add_argument('--history'` matched 0 on both
old and new because the flags are declared across multiple lines. Do not use that
grep as evidence.

D4 (`build_report(require_alpha=…)`) still needs the owner's semantics call; it is
not in this branch and I am not inventing one.

## 4. Verdict — push order

**GO, in this order:**

1. **`hotfix/required-n-power`** (70d4a5a). Verified above. Tag
   `archive/2026-11-19/hotfix-required-n-power` first.
2. **`feat/kilo-todo-sweep-clean`** (07b0204). Published on origin; not unreviewable.
3. **One-ledger deploy patch** (3 lines, maps `audit_dashboard/data/audit3_ledger.json`
   to `/audit`, `/audit2`, `/audit3`). Owner: Kilo Linux CLI. This is the *only*
   fix that turns parity GREEN; without it the 105-min gap returns on the next cron.

**HOLD:**

4. **PR #965** (`feat/audit3-p0-p1-correctness`) — kilo's own rebase aborted at 15
   conflicts in `alpha_engine/*`. Needs one owner in one worktree. I decline to
   author it: AGENTS.md forbids pushing files I did not author.
5. **My sleeve patch** (`2026-11-19-sleeve-implausible-pf.patch`, 197 lines) — must be
   replayed on top of the repaired tribunal, then the gate re-asserted. Do not merge
   it against the current broken file.
6. **`hotfix/audit3-merge-repair`** (7112829) — overlaps #1's file. Two hotfixes
   touching one file is how the last regression happened. Pick one.
7. **Hermes' `/audit2` mirror** — ships and works, but it is **unpinned**: its fallback
   chain resolves to two different ledgers (see §2a), so it can render either 8632
   rows at 22:47Z or 8621 rows at 21:02Z. It must be pinned to one path *and* added to
   the parity assertion before it can be called consistent. Not a reason to hold the
   hotfix.

## 5. How to test (copy-paste)

```bash
# after pushing the hotfix, before the ledger cron:
python3 -m py_compile alpha_engine/audit3_tribunal.py
python3 -m alpha_engine.audit3_tribunal --help          # must parse, no conflict
grep -cE "^def global_trial_count" alpha_engine/audit3_tribunal.py   # 1
python3 -m alpha_engine.audit3_tribunal --picks audit_dashboard/data/dashboard_data.json --out /tmp/ledger.json

# after the one-ledger deploy:
python3 tools/assert_surface_parity.py                  # expect exit 0, not 2
curl -sI https://findtorontoevents.ca/audit3/audit3_ledger.json | head -1
curl -s https://findtorontoevents.ca/audit3/audit3_ledger.json | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print(d['generated_at'],d['summary']['n_rows'],'sleeves' in d)"
curl -s https://findtorontoevents.ca/audit2/audit2.js | grep -oE "fetch\([^)]*\)|[\"'][^\"']*\.json"

# acceptance for all three surfaces:
#   /audit, /audit2, /audit3 → HTTP 200
#   all three ledgers share ONE generated_at within the 70-min tolerance
#   n_rows identical across all three
#   'sleeves' present in the audit3 ledger with FANTASY/TINY rankable=false
```

## 6. Peer review of others' work — what I actually read

**Hermes** (`review/hermes-2026-11-19`, packet in the review repo, read in full this
session) — the strongest analytical work in the fleet:
- **F1 CONFIRMED**: `crypto_intraday_sim.py::slot_guardrails()` L302–307 sums PnL
  arithmetically (`cum += p`) instead of compounding (`prod(1+p/100)`), so a "10%
  trailing drawdown" is percentage-points, not 10% of equity. They also note the
  forming-bar half was already fixed correctly in `completed_bars()` L333–335. This
  is a real gate bug in copilot's sim.
- **F2 OVERSTATED**: the comparison pits copilot's total cost floor (16/8/4/12/2 bp)
  against the ledger's `slippage_pct_by_class` (9.96/5/5/2/15/5 bp). Slippage is one
  component of a cost floor, not the whole of it, so the two tables are not the same
  quantity and a mismatch is not by itself a defect. The *demand* is right — pin one
  canonical base and state per-side vs round-trip — but "one of them is wrong" does
  not follow.
- **F3 CORRECT and load-bearing**: −0.276% CI[−0.506,−0.043] n=3,192 measures the
  legacy `at_pick_outcomes` cohort, not the pre-registered forward pods. It is the
  burden of proof, not a verdict that new pods are doomed.
- **One factual error**: their packet asserts `feat/kilo-todo-sweep-clean` is not on
  origin (0 matches). It is: `refs/heads/feat/kilo-todo-sweep-clean = 07b020459e1`.
- Seat resolved this session: `inbox/desktop-081g9oh/communication/hermes-deepseek-flash`.

**Kilo** — honest about its own failure (rebase aborted at 15 conflicts, asked for
help rather than forcing it), and its hotfix is real and verified. Correct merge
order. Its `audit3_tribunal.py` is also where the five D1 defects came from, and it
has not yet applied the repair patch.

**Copilot** — read their reports and the specific code Hermes cites, not their whole
sim. F1 lands on their engine.

**OpenCode, Swarm, FreeBuff, console seats** — no substantive artifacts read. Not
scoring them.

## 7. Stance

No real money into short-term trading. audit3 is a denylist (0/359 proven or
candidate, 7 denylist hits live), not a promotion engine. Promotion only via the
forward selection-alpha clock at n≥100 with CI lower bound > 0. The only defensible
real-money allocation today is low-cost index beta.
