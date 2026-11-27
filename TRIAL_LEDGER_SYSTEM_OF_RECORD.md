# Trial Ledger System of Record

## Surviving path

`./trial_ledger.db` (repository root) is declared the system of record.

## Per-copy inventory

| Path | Raw file sha256 | Git blob sha | `trials` row count | Schema sha256 | Last-modified commit |
|---|---|---|---|---|---|
| `./trial_ledger.db` | `b8efa50a5d20a398d76b0e79e14614c9a5650a20eb2958e3503449ca59839ccb` | `657e8acb78f6a0e6a0510876d4618dcc62778e31` | 2 | `c381a1f8530a76d5e93431c5717d435adce6f5647a30b518c781b85e5fe541b7` | `7e36abc5e1c3db7ffbf4d6f76ce0f10558eb44b3` |
| `./CONTEST/tools/reports/trial_ledger.db` | `49c1069035a878412ff9b739e0b41700df9538d44b62385d2429ec3a432e8d2f` | `35b1b1da72101ddf182d5691114d43f31cbb1ffb` | 6 | `c381a1f8530a76d5e93431c5717d435adce6f5647a30b518c781b85e5fe541b7` | `1b54f2595a7bcf503232f95b2032a86572c0fb60` |
| `./CONTEST/tools/trial_ledger.db` | `f8aa543a19b7ab556354793b9c11d2a3f8eff06df16abbb6ad5470d55a8deece` | `f9ef3b18eb8a70f8d6b5fa2bea72e2da94f0d466` | 8 | `c381a1f8530a76d5e93431c5717d435adce6f5647a30b518c781b85e5fe541b7` | `e76ba5054396da3902921b1d507eda20e94b3c2c` |
| `./CONTEST/trial_ledger.db` | `9409793da26e5284aa07256ed3dbc87cab7bb8e1af3463e58a08061c3345c95f` | `c68a78c081ed459ad1295e629f3907703fb6e86a` | 6 | `c381a1f8530a76d5e93431c5717d435adce6f5647a30b518c781b85e5fe541b7` | `be9d3ce6f625e3b10b30bea4639edbe7e0cb7aa9` |

## Divergence summary

All copies share an identical `trials` schema (same sha256). They diverge in data rows of the `trials` table:

| Copy | `trials` row count |
|---|---|
| `./trial_ledger.db` | 2 |
| `./CONTEST/tools/reports/trial_ledger.db` | 6 |
| `./CONTEST/tools/trial_ledger.db` | 8 |
| `./CONTEST/trial_ledger.db` | 6 |

The copies differ in raw file bytes (different sha256), so none are byte-identical duplicates. Per consolidation rules, no copy was deleted: divergent copies must all be retained.

## Authoritative choice

Root-level `./trial_ledger.db` is retained as the system of record because:
- It lives at the repository root on the default branch (`main`).
- Its last-modified commit `7e36abc5e1c3db7ffbf4d6f76ce0f10558eb44b3` ("cron 2026-11-24T22:10 EST: task2 dummy-ledger verification (2 rows...)") is the most recent commit touching any trial_ledger.db copy on default branch.
- The other three copies live under `CONTEST/` or `CONTEST/tools/`, where they serve as forensics/working-draft artifacts.

## Verification against GitHub API

Verified via `gh api repos/eltonaguiar/antigravity_review_Nov192026/git/trees/main?recursive=1` (blob shas and sizes), `git log -1 -- <path>` per path (last-modified commit), and local row-count/schema comparison via Python's sqlite3 module (read-only URI connections).
