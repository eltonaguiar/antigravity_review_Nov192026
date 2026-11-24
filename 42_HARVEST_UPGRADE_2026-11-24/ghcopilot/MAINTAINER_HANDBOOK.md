# Maintainer handbook — what was built on 2026-11-24, and how to look after it

Written for someone who has never seen this work. Plain language first, exact detail after.
**If you read only one section, read §1 and §4.**

---

## §1. The one idea behind everything here

> **A number that cannot be valid must not be emitted.**

That is the whole theme. Everything below is a consequence of it.

Here is why it matters more than it sounds. A program that *crashes* is harmless — you know it
failed. A program that prints a confident number on garbage input is dangerous, because the number
travels: into a commit message, a dashboard, a tweet, a decision. Nobody downstream can tell that it
was meaningless.

Three times in one session, this repo produced a confident, meaningless number:

1. A **"Deflated Sharpe Ratio" of 0.99998** computed on four rows of test data. (A DSR is a
   statistic that says "you tried many things, so discount the winner." 0.99998 means "this is
   certainly real." On test data.)
2. A **view called `v_trial_census`** that looked like a count of real experiments, but counted test
   rows, so it reported "23 trials" when there were zero.
3. **Required-return figures** computed with the wrong arithmetic (adding costs up instead of
   compounding them), which understated crypto's hurdle by 63.9 percentage points.

Same disease each time: **something that was not a measurement was treated as one.** The fix is not
"be more careful" — it is to make the code refuse.

---

## §2. Plain-language glossary

You will need these six words.

| Term | What it actually means | Analogy |
|---|---|---|
| **Sharpe ratio** | Return divided by volatility. "How much reward per unit of wobble." | Miles per gallon |
| **DSR** (Deflated Sharpe Ratio) | A Sharpe *discounted for how many things you tried*. Try 1 strategy → no discount. Try 1,000 → heavy discount, because the best of 1,000 coin-flippers will look brilliant. | "You tried 100 keys; one opened the door — how impressed should I be?" |
| **Trial** | One strategy attempt that you recorded. The DSR needs to know how many there were. | One key you tried |
| **Fixture / dummy data** | Fake rows inserted so software can be tested. Never a measurement. | Crash-test dummy |
| **`n`** | How many trials/observations. Small `n` = can't conclude anything. | Sample size in a survey |
| **Cost bracket** | A range — floor / central / ceiling — instead of one number, because the honest answer is a range. | "The drive takes 3–5 hours" |
| **Publish path** | Only one folder of this repo becomes the website. Everything else is just files on GitHub. | Storefront vs stockroom |

---

## §3. Everything that was built — file by file

### 3.1 `CONTEST/tools/dsr.py` — the bouncer *(modified)*

**What it does now:** computes the DSR, **or refuses and says why.**

Before: it always returned a number. Four fake rows in, `0.999983991176608` out.

```
$ python3 CONTEST/tools/dsr.py CONTEST/tools/trial_ledger.db
REFUSED: 11 of 13 ledger rows are fixtures (e.g. run_id='run_dummy_1' family='momentum').
DSR=REFUSED source=... (no number emitted)     # exit code 2
```

**The two refusals, and why each exists:**

| Check | Constant / rule | Why |
|---|---|---|
| Fixture rows present | `_FIXTURE_RE` matches `dummy\|fixture\|fake\|synthetic\|placeholder\|sample`, or a name starting `test` | Test data can never support a statistical claim |
| Too few trials | `MIN_TRIALS_FOR_DSR = 30` | Below ~30 you cannot estimate the spread across trials, which is what the deflation needs. 30 matches this repo's existing `n<30 = INSUFFICIENT` convention |

**How to change it safely:**

- To change the threshold: edit `MIN_TRIALS_FOR_DSR`. Do **not** lower it to make a result pass —
  that is how the original defect arose. Then run `python3 CONTEST/tools/test_dsr_guard.py`.
- To teach it a new fake-data name: add the pattern to `_FIXTURE_RE`.
- **Never** set `allow_fixtures=True` in code that reports results. Its only legitimate use is
  testing the estimator. A grep for `allow_fixtures` should only ever find tests.
- The CLI exits **2** on refusal. Any cron/wrapper must treat non-zero as "no result", not as
  "error to ignore". If a job logs the DSR, it should log `REFUSED`, never 0.

### 3.2 `CONTEST/tools/test_dsr_guard.py` — the proof the bouncer works *(new)*

**How to run:** `python3 CONTEST/tools/test_dsr_guard.py` → prints `5/5 passed`, exits 0.

| Test | What it asserts, in words |
|---|---|
| `test_refuses_fixture_rows` | 40 rows of fake data get refused (so it isn't just a size check) |
| `test_refuses_below_min_trials` | 29 clean rows get refused |
| `test_computes_on_clean_ledger` | 40 clean rows still produce a number — the guard didn't break the happy path |
| `test_allow_fixtures_escape_hatch` | The testing override actually works |
| `test_cli_refusal_prints_no_numeric_dsr` | **The important one:** a refusal prints no number to stdout, so a wrapper cannot quote one |

**The technique worth copying** — *test the test.* A test that passes proves nothing until you know
it can fail. To re-run the proof:

```bash
rm -rf /tmp/dsr_mut && mkdir -p /tmp/dsr_mut
cp CONTEST/tools/dsr.py CONTEST/tools/test_dsr_guard.py /tmp/dsr_mut/
# neuter both refusals, then run the suite
```
Result: **3 of 5 fail**, and the two that don't depend on the guard still pass — exactly right. If
all 5 still passed, the tests would be worthless.

**When you add a check to `dsr.py`:** add a test that it fires, and confirm the new test fails when
you break the check.

### 3.3 `CONTEST/tools/DSR_GUARD.md` — why the bouncer exists *(new)*

Records the decision (**refuse below n_min**, not "drop DSR from commit messages"), the three
reasons, the verification table, and the known limitation. Read this before questioning the design.

The limitation, stated honestly: the fake-data detector matches *names*, so rows called `famA`,
`var_alpha` or `r01` slip past it (that's why the real ledger says "11 of 13", not 13 of 13). The
`n_min` floor catches that case anyway because the two checks are OR'd — but a 30+ row ledger of
plausibly-named fake rows would still pass. The durable fix is to stop writing fixtures in the first
place (`trial_log.py`).

### 3.4 `CONTEST/tools/DSR_VOID_9c9eda3.md` — the tombstone *(new)*

Commit `9c9eda3` published `DSR = 0.999983991176608` in its commit message. **A commit message cannot
be edited**, so the number cannot be deleted — only made findable-as-void.

This file exists so that someone who encounters the wrong number can find the correction three
different ways:

```bash
git log --oneline --grep=9c9eda3                  # mentions the commit
git log --oneline --grep=RETRACTION               # mentions the retraction
git log -S'0.999983991176608' --oneline           # where the digits were added/removed
```

All three were **tested against pushed history**, not assumed.

### 3.5 `CONTEST/tools/DSR_FORMULA_DEFECT.md` — the biggest finding *(new)*

**Read this one even if you skip the rest.** Short version: the DSR in this repo does not deflate.
On **pure noise** it reports **0.99986**. It rises as you add trials — the opposite of its purpose.

| N (all pure noise) | DSR |
|---:|---:|
| 50 | 0.994 |
| 500 | 0.991 |
| 2000 | **0.9999** |

**Consequence you must not miss:** the guard I added blocks *fake* data. A **clean** 30-row ledger
passes the guard and still gets an inflated number. **"No refusal" does not mean "valid."**

The file contains the correct formula, why the code differs, and the two honest remedies (fix the
estimator, or rename the function to what it actually computes). It needs an owner decision because
fixing it invalidates every DSR previously quoted.

### 3.6 `42_HARVEST_UPGRADE_2026-11-24/ghcopilot/ZOOCODE_ASKANYMODEL_REVIEW.md` — the banner *(modified)*

This review document printed two figures that its sibling file had already retracted. Fixed by
adding a warning banner at the top plus inline `SUPERSEDED` / `RETRACTED` markers.

**The rule to carry forward:** *a correction that lives in a different file is not a correction.*
Anyone who reads only the main document repeats the retracted number. If you retract something,
put the retraction **where the wrong claim is**, not in a sibling file.

### 3.7 The other 38 files in `42_HARVEST_UPGRADE_2026-11-24/ghcopilot/`

Landed earlier; listed here so you know what's there:

- **Cost work:** `cost_of_hurdle.py`, `compounded_drag.py`, `out/cost_of_hurdle.json`,
  `out/compounded_drag.json`, `out/cost_reclass_simulation.json`, `PROPOSED_cost_of_record.json`
- **Monte Carlo:** `monte_carlo.py`, `mc_on_published_aggregates.py`, `out/mc_published_aggregates.json`
- **Meme coins:** `meme_*.py`, `MEME_ENDORSEMENT_REVIEW.md`, `out/meme_*.json`
- **DB schema reviews:** `DB_SCHEMA_GAP_REVIEW.md`, `_R2.md`, `_R3.md`, `db_schema_audit.py`
- **Migrations:** `migrations/000_STATUS.md` … `004_remaining_gaps.sql` — **`004` is the only one
  never applied**; `000_STATUS.md` is the read-first reconciliation note
- **Data layers:** `lookthrough_consensus.py`, `crowd_layer.py`, `LOOKTHROUGH.md`, `CROWD.md`
- **Reviews:** `VERDICT_GATES_REVIEW.md`, `CORRECTIONS_ADDENDUM_2026-11-24.md`,
  `ANALYST_SCORECARD_SPEC.md`, `STEP_C_INGEST.md`

All 40 are on `origin/main`. **None of them appear on the website** — see §4.3.

---

## §4. Operating recipes — the things you will actually need

### 4.1 Pushing to this repo without destroying a colleague's work

This repo is edited by **several agents at once**. Pushes fail constantly, and a careless rebase can
delete someone's uncommitted work. The safe loop:

```bash
git push origin HEAD:main            # if rejected, do NOT force
git fetch -q origin/main
git status --porcelain               # what is dirty?
```

Now, for every file that blocks you (untracked files that origin now contains, or dirty files):

1. **Compare it to origin first.**
   ```bash
   git rev-parse origin/main:<path>     # what origin has
   git hash-object -- <path>            # what you have
   ```
2. **Identical?** Move it aside — it will come back as a tracked file.
3. **Different?** Copy it to `/tmp` **before** moving it, and say so out loud. It may be someone's
   only copy.
4. Only then rebase and push.

**Never** `git reset --hard`, `git push --force`, or `git clean -fd` here.

### 4.2 Verifying that something actually landed

Do **not** trust your working tree. A file being on disk proves nothing about the remote.

```bash
git fetch -q origin/main
git cat-file -e origin/main:<path> && echo "on origin" || echo "NOT on origin"
```

### 4.3 Checking whether something is on the website

The site publishes **one folder only**: `docs/`. Everything else is just files on GitHub.

```bash
# Is my file published? Look in docs/.
find docs -name '<my-file>'                      # present = published
grep -rln '<my-claim>' docs --include='*.html'    # is my claim on a live page?
```

Workflow: `.github/workflows/pages.yml`. It rebuilds when a push touches `docs/**`, `PROVEIT/**`,
`ZOOCODE/**`, `harvest/**` or the workflow itself. `PROVEIT/` is copied into `docs/PROVEIT/` **at
build time** — never commit a second copy under `docs/PROVEIT/`, that duplication caused a silent
revert once (commit `8277657`).

**Therefore:** files under `42_HARVEST_UPGRADE_2026-11-24/` are browsable on GitHub but will **never
appear on the site**. To publish one, copy it into `docs/`.

**Known gap (unfixed):** the build runs
`42_HARVEST_UPGRADE_2026-11-24/kilocode/render_legend.py`, which *writes* a file — but that path is
not in the workflow's `paths:` list. So editing the legend source does not redeploy the site; the
legend quietly refreshes the next time something unrelated triggers a build. Fix: add
`42_HARVEST_UPGRADE_2026-11-24/kilocode/**` to `paths:` (narrow — not the whole tree).

### 4.4 Reading and writing COMS messages

```bash
export PATH="$HOME/.local/bin:$PATH"
coms topics 'notes/<topic>'                                   # confirm it exists
mosquitto_sub -h 192.168.2.52 -t 'notes/<topic>' -W 4 --retained-only -C 1   # read it
coms send --retain notes/<author>-<subject>-<date> "$(cat /tmp/body.txt)"    # write it
```

Three traps that have already bitten:

- **`--retain` is last-writer-wins per topic**, not an append log. A second note to the same topic
  **destroys** the first. Always use a new topic name.
- **`*` is a literal character in MQTT**, not a wildcard. Use `+` (one level) or `#` (all below).
- **A failed publish leaves the old retained message readable.** Verify by reading the *content*
  back, not by checking the topic exists.
- The body must be written to a file first; backticks and `$` inside a double-quoted argument get
  expanded by bash.

---

## §5. Open decisions — not mine to make

These block publication and need a named owner:

| ID | The question | Why it matters |
|---|---|---|
| `DSR-FORMULA` | Fix the estimator, or rename it? | Every DSR quoted in the estate is affected (§3.5) |
| `BOND-NUMBER` | −17.29 (3 cells) or +9.6 (24 marked picks)? | Two different populations, one label |
| `WRAPPER-PER-CLASS` | Commodity at spot 20 bp or CL futures 3.23 bp? | Sets the cost of every commodity verdict |
| `SYSTEM-OF-RECORD` | `picktrack_picks` or `dashboard_data.json`? | The loser must be labelled a derived view |
| `PUBLIC-VERDICTS` | Publish the four "NO" verdicts? | `gates.html` is held pending this |
| `TRIAL-WRITES` | Stop writing dummy trials at source? | The guard blocks their *output*; the ledger still fills with them |

**Note on IDs:** earlier notes used bare `Q1`–`Q7`, and two different numbering schemes had come into
circulation (Q5 meant two different things). Use the names above, not numbers.

---

## §6. What was verified, and what was not

Verified with commands, not assumed:

- Every file listed in §3 is on `origin/main` (`git cat-file -e`).
- Refusals work, and the tests that check them can fail (§3.2).
- No published page carries the retracted cost figures — six numeric matches were checked in context
  and all were coincidental (a USDJPY price of 158.97, a DOGE return of +14.43%, a 21.2% stop).
- The three retraction-discovery commands find the tombstone on pushed history.

**Not** verified / not done:

- The DSR formula is **not** fixed — only documented (§3.5).
- The two trial ledgers (`CONTEST/trial_ledger.db` and `CONTEST/tools/trial_ledger.db`) are **still
  unreconciled**, so "N" still has no single value.
- `migrations/004_remaining_gaps.sql` is **still unapplied**.
- The Monte Carlo permutation test remains blocked (upstream HTTP 429; the observation vector was
  lost).
- The `kilocode/` deploy-trigger gap is **reported, not fixed** (§4.3).

---

## §7. If you have five minutes and want to do the most useful thing

1. Read `DSR_FORMULA_DEFECT.md`. Decide between fixing and renaming. That single decision affects
   more published numbers than everything else here combined.
2. Run `python3 CONTEST/tools/test_dsr_guard.py`. It should say `5/5 passed`.
3. Check that no job in your CI is treating DSR exit code 2 as a transient error.
