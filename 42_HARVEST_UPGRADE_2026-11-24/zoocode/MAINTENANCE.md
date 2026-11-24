# MAINTENANCE GUIDE — everything zoo-savant built, explained so anyone can keep it alive

Written 2026-11-24 by zoo-savant. Directory: `antigravity_review_Nov192026/42_HARVEST_UPGRADE_2026-11-24/zoocode/`.
Read this before changing anything here. Every file is listed with what it is, how to run it,
what it depends on, and how to update it safely.

---

## Part 0 — The whole thing in five sentences

1. We have a page that shows **what stock analysts think** about a company (buy / hold / sell).
2. I checked whether those opinions are **honest and useful**: are the labels computed correctly,
   and do they predict anything?
3. The labels are correct. The predictions are **not there**: when an analyst says "up", the stock does
   not do better than when they say "down".
4. The reason is that the same market move gets counted **hundreds of times**, so the numbers look
   far more confident than they are. Fixing that is most of my work.
5. Everything is built so a stranger can **re-run it and get the same answer**, and so a gap in the
   data is never quietly shown as a zero.

---

## Part 1 — File by file

### 1.1 The audit of the HARVEST page

| file | what |
|---|---|
`verify_harvest.py` | the checker: reads `docs/data/harvest_signals.json` and re-derives every number |
`results.json` | its full output (every row it examined, not just the failures) |
`REPORT.md` | the written findings |

**ELI5:** the page says "70 analysts, 95% of them say buy". This script re-adds the 70 opinions
itself and checks the page's arithmetic. It also asks: if analysts were just flipping coins, how
often would we see a month-to-month change this big by luck?

**How to run:** `python3 verify_harvest.py` (needs `numpy`).
**How to update:** if the page adds a column, add it to the extraction in `main()` and re-run; the
Monte Carlo seed is fixed (`SEED = 20261124`), so a changed result means changed data, not changed luck.
**Careful:** the feed it reads lives in a different repo (`docs/data/harvest_signals.json`), so it can
silently go stale. Check the file's `generated_at` before trusting an old `results.json`.

### 1.2 Database design (for Hermes, who owns the DB)

| file | what |
|---|---|
`suggested_tracking_schema.sql` | 14 tables: picks, observations, analyst actions, crowd markets, source health |
`quality_checks.sql` | SQL that finds bad data (duplicates, orphans, impossible timestamps, P/L stuck at 0) |
`free_data_sources_by_asset_class.md` | which free source actually covers which asset class, and which do not |

**ELI5:** a filing cabinet design. One drawer for every pick *ever made* (never overwritten), one for
what happened to it each day, one for analysts, one for prediction markets, one for "which source is
broken right now". The quality file is a checklist you run over the cabinet: "any two folders with the
same label?", "any folder stamped in the future?"

**How to verify:** the schema executes cleanly in sqlite3 (14 tables) and the 11 portable checks parse.
**How to update:** add a column rather than changing one; never drop a column that a check references.
**The one convention to keep:** **NULL means "we could not measure it"; 0 means "we measured zero".**
Conflating them is the single most common bug in this area.

### 1.3 The analyst track-record plan

| file | what |
|---|---|
`ANALYST_TRACK_RECORD_PLAN.md` | how to score an analyst's record honestly |
`HARVEST_ANALYST_VERDICT.md` | per-cell verdict table: what may be published and what may not |
`analyst_action_grid.json` | the 4 action classes × 3 horizons, machine-readable (raw, net, design effect) |
`ab_ledger_synthetic.jsonl` | a *made-up* example ledger, clearly labelled, used to demonstrate the maths |
`rate_two_axis_counterexample.py` | proves a "reliability AND magnitude" rating can still rank the wrong one first |

**ELI5 on why win rate is a trap:** imagine someone wins 97.6% of their bets but loses 18% whenever
they lose, against 0.8% gains. Their good trades are pocket change and their bad trade is a house.
One more loss wipes out twenty-two wins. Meanwhile someone winning only 49% with 6% wins and 3% losses
is quietly compounding. So **the rating has to look at both the average and the worst plausible
case**, never the win rate alone.

**How to run:** `python3 rate_two_axis_counterexample.py`.
**How to update:** the numbers live in `record(...)` calls at the bottom of `main()`. `wilson()` and
the tier thresholds are the parts to be careful with, not the printing.

### 1.4 The three backtests (the research)

| file | what it tests |
|---|---|
`backtest_analyst_actions.py` → `backtest_results.json` | 72,108 dated analyst actions: does the *action* predict the next 5/21/63 days? |
`block_bootstrap_significance.py` → `block_bootstrap_results.json` | is the one gap that looked real bigger than chance, resampling whole time blocks? |
`backtest_consensus_labels.py` → `consensus_label_backtest.json` | does a higher consensus *label* mean a higher return (monotonicity)? |

**ELI5 on the three traps these handle:**
- **Overlapping windows.** 63-day outcomes measured every day are 63 stories about almost the same
  price move. Counting them as 4,000 independent facts is like weighing yourself 63 times in one
  minute and concluding your weight is precise to the gram. We collapse to *one number per symbol*
  and call that the honest count (the "design effect" says how much we were over-counting: up to 951×).
- **Survivorship.** Only companies that still exist today have prices. If the bankrupt ones are
  missing, every strategy looks better than it was. That is why the only trustworthy comparison is
  *upgrade vs downgrade within the same symbol*: both share the same bias, so it cancels.
- **Costs.** A trade pays the spread twice. A "profit" of 0.05% with a 0.26% toll is a loss.

**How to run:** each script is standalone, needs `yfinance`, `pandas`, `numpy`, and reads dated
actions from `/home/eaguiar2015/findtorontoevents_antigravity.ca/ZOOCODE/harvest/*.json`.
**How to update:** change constants at the top (`SEED`, `N_BOOT`, `LEG_BPS`, `HORIZON`), never the
statistics mid-file. Seeds are fixed on purpose: a different p-value with the same data means you
changed the method, not that the answer is luck.
**Careful:** `yfinance` hits the network, so prices change between runs. The action dates do not.

### 1.5 The trial ledger union

| file | what |
|---|---|
`union_trial_ledgers.py` | merges the three forked `trial_ledger.db` copies into one JSONL |
`trials_union.jsonl` | the merged result: 19 trials, each row tagged with `source_file` |

**ELI5:** a lab notebook got photocopied into three notebooks that then drifted apart. Someone might
"clean up" by deleting two: that would throw away experiments nobody repeated anywhere else. So we
merge all 19 entries, keeping a note of which notebook each came from, and stop keeping notebooks in
a format that cannot be merged (SQLite binaries).
**How to run:** `python3 union_trial_ledgers.py --check` (must print `DISJOINT (nothing lost)` and `PASS`).
**How to update:** point `SOURCES` at the current files and re-run; if `--check` ever prints
`OVERLAP FOUND`, stop and reconcile by hand, because the same `trial_id` in two files means a real conflict.

### 5. The price-target sidecar

| file | what |
|---|---|
| `harvest_price_targets.py` | fetches last price + analyst target range per symbol from Yahoo |
| `harvest_targets.json` | its output (71 symbols) |

**ELI5:** a "strong buy" from 95% of analysts means little if the average target price is *below*
today's price. This adds that context. It needs an `A3` cookie from `fc.yahoo.com` exchanged for a
"crumb", which is why it does two GETs before the real request.
**How to run:** `python3 harvest_price_targets.py` (writes the JSON next to itself).
**Careful:** Yahoo's `n_yahoo` analyst count differs from the page's Finnhub count (BRK-B: 3 vs 10).
Both are stored rather than silently reconciled.

---

## Part 2 — The lessons worth keeping (this is the real deliverable)

1. **A signal that says both "buy" and "sell" with equal success is not a signal.** At 63 days,
   upgrades earned +2.188% and downgrades +1.739% over SPY. They both beat doing nothing, so what is
   being measured is *attention* (an analyst wrote something), not *direction*.
2. **Point-in-time beats a snapshot.** My consensus test used a label taken at the period's end to
   open a window starting at that same date: mild look-ahead. Kilo's rule (enter at the next open
   after publication) is the correct one. Use it.
3. **Report clustered n and a design effect next to every t.** Six independent backtests on this
   repo all produced large design effects; none of them was safe to read naively.
4. **A reproducible wrong label is still wrong.** The HARVEST labels reproduce 71/71 from a rule, but
   the ordering they create is inverted against returns (Spearman −0.0726). Reproducibility is not validity.
5. **NULL is not zero.** Unmarked positions written as `pnl_pct: 0.0` looked like flat trades for
   254 days. They were never priced at all.
6. **Count trials where they can't be lost.** DSR is arithmetic on how many things you tried; three
   forked ledgers made that number unknowable.

## Part 3 — What is worth saving, and what is not

**Worth saving (keep in git):** every script (so results are re-derivable), `results.json` and the
three backtest JSONs (the evidence), `HARVEST_ANALYST_VERDICT.md` and this guide (the conclusions and
how to maintain them), `trials_union.jsonl` (19 trials that exist nowhere else), and
`suggested_tracking_schema.sql` (the design Hermes will build from).

**Disposable / regenerate at will:** `analyst_action_grid.json` (a projection of
`backtest_results.json`), `harvest_targets.json` (live prices), `__pycache__/`, and
`ab_ledger_synthetic.jsonl` (it is a teaching example, not data, and is labelled as such on every row).

**Never commit:** credentials (`~/dbpasses.txt` holds 552 lines of them), raw multi-GB logs, or a
`.db` file that more than one agent writes to.

## Part 4 — Regenerating everything

```bash
cd 42_HARVEST_UPGRADE_2026-11-24/zoocode
python3 verify_harvest.py                    # -> results.json  (re-read REPORT.md after)
python3 backtest_analyst_actions.py           # -> backtest_results.json   (a few minutes)
python3 block_bootstrap_significance.py       # -> block_bootstrap_results.json
python3 backtest_consensus_labels.py          # -> consensus_label_backtest.json
python3 union_trial_ledgers.py --check        # must PASS
python3 rate_two_axis_counterexample.py       # prints the table
```
All are seeded, so two runs on the same data agree exactly. If they disagree, the data changed
(network prices, or a new harvest file) rather than the arithmetic.
