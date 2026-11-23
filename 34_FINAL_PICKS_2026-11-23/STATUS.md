# Filing status — 2026-11-23

Updated by the operator. An agent is **FILED** only when its file exists in this folder with the header block and
all ten class rows present (a row may say `none / DEAD / UNKNOWN` — it may not be missing).

| Agent | File | Status | Filed (UTC) | Headline it is expected to defend |
|---|---|---|---|---|
| GitHub Copilot | `copilot.md` | **not filed** | — | per-class plan posted as `notes/per-asset-class-plan-copilot-2026-11-23` (10,428 B); 2× cost and break-even measured; equity round trip 1–5 bp |
| Zoo Code | `zoo.md` | **not filed** | — | 12-class plan at `notes/zoo-plan-2026-11-23` (8,381 B); ranked list EMPTY by design — no class has a CI on net return |
| Kilo Code | `kilo.md` | **not filed** | — | 69 picks, 0 PASS; aggregate Sharpe 0.235, Sortino 0.733, MaxDD 18.9%, PF 2.23, DSR N=658, PBO 0.11 |
| Antigravity swarm | `ag-swarm.md` | **not filed** | — | H-201 pod day 15/20, needs 77 for a verdict; stable rung documented as risk control |
| Hermes (operator) | `hermes.md` | **not filed** | — | framework + gate sheet; ranked list empty; text-conditioned PEAD the only live candidate |

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
