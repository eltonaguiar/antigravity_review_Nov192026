# Follow-up verification — kilo's response to the Windows re-review

**Verified commit:** `eltonaguiar/findtorontoevents_antigravity.ca` `c4ec1ecb6b7d`
(“fix(audit3): address Windows peer review”), confirmed on `origin/main` @ `60b2dfc322fa`
at review time.
**Prior review:** `00_SUMMARY.md` / `01_proof.md` / `02_open_items.md` (commit `21328e7`).
**Windows suite at `c4ec1ecb6b7d`:** **111 passed in 7.36s** (the same six files; +2 tests).

## All three P1s are closed

| P1 from `02_open_items.md` | Verification |
|---|---|
| Ingest could stay green at `n_admissible == 0` | `forward-observations-ingest.yml:78` now asserts `rep["n_admissible"] > 0` and explicitly allows `added==0` with `admissible>0`. Correct. |
| Ingest did not pin `ref: main` | `:41` now has `ref: main          # never push a feature branch's files to main`, and the commit step is guarded by `github.ref == 'refs/heads/main'` (`:101`). Correct. |
| `audit3-ledger.yml` exported only `DB_PASS_STOCKS` | Both the price-backfill (`:104-107`) and selection-alpha (`:158-161`) steps now export `DB_PASSWORDS_JSON` too and skip only when both are empty. Correct. |

## Alpha status split is correct

`apply_selection_alpha_gate` now separates:

- `unmeasured` — no interval
- `unproven` — CI straddles zero
- `beta_dominant` — whole CI below zero (`hi < 0`)

The two new tests (`tests/test_audit3_selection_alpha.py`, `tests/test_audit3_tribunal.py`)
pin both cases. The live ledger regenerated at `18:32:40Z` (after the fix) now reports
`unproven=189`, `beta_dominant=168`, `proven=1`, `unmeasured=1` — so the previous
357/359 “beta” figure was mostly absence of proof, as claimed. Gate remains
`applied=true`, `tested=434`, `demoted=0`, with the same scope split
(`strategy=37`, `class_proxy=390`, `class=7`).

## Correction: zero CANDIDATE is not DSR-driven

Kilo's note says “0 CANDIDATE is DSR-driven, not alpha”. The live ledger does not support
the DSR attribution. Reason counts over all 359 cells:

```
292  n=<N> < 20: no statistical claim
 41  split-half unstable (one half mean <= 0)
 43  win rate < threshold (36 + 7)
 14  profit factor < threshold (8 + 6)
  8  net expectancy CI entirely below zero (KILL)
  5  single symbol share
  0  DSR ...
  0  BH q ...
  0  selection-alpha ...
  0  forward gate ...
```

No cell carries a DSR demotion reason, so the 658 floor is not the binding constraint on
this payload. The queue is empty because no cell clears the early floors (sample size,
split-half stability, win rate, profit factor) far enough to reach CANDIDATE. The
family-size/658 question is still a valid future policy question, but do not close it as
“DSR-driven” — that attribution is unsupported by the current ledger.

## Minor nits

- The two skip messages still say “no DB_PASS_STOCKS secret” although the guard now checks
  both variables. Cosmetic only.
- The corrected handoff (`AGENT_FOLDERFRAMEWORK` `269f121`) now states `send` is QoS 1 but
  non-retained, and that `--retain` exists on both platforms. Verified; no further action.

## Status

The three P1s are closed and the alpha split is right. The only new item is the
mis-attribution of the empty CANDIDATE queue (documentation/policy, not code).
