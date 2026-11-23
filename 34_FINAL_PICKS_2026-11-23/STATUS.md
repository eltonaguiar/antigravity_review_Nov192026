# Filing status — 2026-11-23

Updated by the operator. An agent is **FILED** only when its file exists in this folder with the header block and
all ten class rows present (a row may say `none / DEAD / UNKNOWN` — it may not be missing).

| Agent | File | Status | Filed (UTC) | Endorsed | Headline it filed |
|---|---|---|---|---|---|
| GitHub Copilot | `GITHUB_COPILOT_DEEPSEEK/copilot.md` (+ `picks.json`, pointer at flat `copilot.md`) | **FILED** | 03:05Z | **0** | 0/10 investable as an edge; 1 vehicle (broad-market ETF buy-and-hold = beta, not alpha); FOREX unresolved at −0.68 bp; DSR N=90 **disputed** (6 values in circulation, 26.3× spread) |
| Zoo Code | `ZOOCODE_DEEPSEEK/` (5 files: README, PER_ASSET_CLASS_PICKS, OVERALL_TOP_PICKS, TESTING_AND_BACKTESTING, NEXT_STEPS) | **FILED** | — | **0** | 0 INVESTABLE / 11 NOT_INVESTABLE / 3 UNKNOWN; ranked list EMPTY by design — no class has a CI on net return on committed capital |
| Kilo Code | `KILOCODE_VSCODE/KILOCODE_VSCODE.md` (+ `picks.json`) | **FILED** | 02:33Z | **0** | 0/10 investable; 0/69 pass all gates; **11.36 bp crypto row RETRACTED** (flat 12.87 bp cost under-applied the 20–52 bp band); 49/69 picks now net ≤ 0 |
| buffy-freebuff | `buffy-freebuff.md` | **FILED** | 21:48Z | **0** | 0/10 classes pass all five gates |
| Antigravity swarm | `ag-swarm.md` | **NOT FILED** | — | — | expected: H-201 pod day 15/20, needs 77 for a verdict |
| Hermes (operator) | `hermes.md` | not filed — framework only | — | **0** | gate sheet + empty ranked list; text-conditioned PEAD the only live candidate |

**Audit:** `VETTING_ROUND2_2026-11-23.md`. **Cost rules:** `COST_OF_RECORD.md` (new — a `measured` label must match it
or carry a reconciliation).

### Flat-path resolution note

Three agents filed into subfolders rather than the flat `copilot.md` / `zoo.md` / `kilo.md` the README §1 prescribes.
Only **Copilot** left a flat pointer (deliberately number-free, so it cannot drift). `zoo.md` and `kilo.md` therefore
**do not exist** — tooling that resolves flat paths must be pointed at the subfolder, or treat the flat file as absent.

## What "final" means here

Not "the last thing I said in chat". A **filed pick** is a row with an instrument, an n, a net-of-measured-cost
number, the trial count it was deflated at, a cost basis marked measured-or-assumed, an execution style, and a frozen
kill rule — plus a path or sha where the measurement lives.

Anything less is a `CANDIDATE` with the missing measurement named.

## Known cross-agent agreements and disagreements (operator's record)

**Agreement (all four):** nothing in the estate is currently investable; every family measured on our own bars fails
net of cost; the ranked list is legitimately empty.

**Disagreement worth resolving in the files:**
- *Kilo* ranks by gates passed then net bp at a $25k ticket. *Zoo Code* ranks on the **CI lower bound**, and refuses to
  rank at all without a CI on net return. These are different orderings and both are documented — say which you use.
- *Copilot* measures equity round trip at 1–5 bp; *the protocol's* assumption table says 8–12 bp mega/large cap. Both
  are stated; the file must say which one its picks are costed at.
- *Value*: Copilot measured +0.11%/yr gross (net +0.02%). The literature's post-2007 consensus is −0.86%/yr. These
  agree in direction and both kill the family — no conflict, but state the one you used.

## Rule for the operator

Do not fill an agent's file on its behalf. If an agent has not filed by the window's end, that is the finding:
**not filed = no final picks**, and the reason goes in `NEXT_STEPS`, not in a guess.
