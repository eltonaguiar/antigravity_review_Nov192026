# HARVEST upgrade — look-through consensus, crowd layer, scorecard spec

**Owner:** `ghcopilot` · **Directory:** `42_HARVEST_UPGRADE_2026-11-24/ghcopilot/`
**Run:** 2026-11-24T11:06–11:08Z · **Base commit:** `178db50`

Everything in this directory is additive. No file outside it is modified. `docs/index.html` was
not touched. Every number below is reproduced by a script in this folder against a free, credential-
free endpoint; where an endpoint refused, the refusal is recorded verbatim rather than worked around.

## STEP DONE — what actually returned data

| Deliverable | Status | Returned data |
|---|---|---|
| (1) Look-through consensus for funds | **partial, 3 of 6 funds** | SPY, XLK, QQQ derived; JNK correct-but-not-applicable; VTI blocked; EEM blocked |
| (2) Crowd layer, Polymarket + Kalshi | **both venues OK** | Polymarket 100 markets, Kalshi 200 markets; Layer A 0 exact matches; Layer B 5 mechanism-carrying mappings |
| (3) Analyst-scorecard spec | **complete** | `ANALYST_SCORECARD_SPEC.md` |
| (4) Simulation design | **already delivered** | `../DESIGN_ANALYST_SIMULATION.md` (commit `ae831a8`) — not duplicated here |

### Look-through results — `out/lookthrough_consensus.json`

| fund | source | positions | matched | weight coverage | derived share Buy | status |
|---|---|---:|---:|---:|---:|---|
| SPY | SSGA holdings xlsx | 505 | 70 | **60.07%** | **77.35** | DERIVED_OK |
| XLK | SSGA holdings xlsx | 78 | 14 | **65.46%** | **77.44** | DERIVED_OK |
| QQQ | SEC N-PORT | 105 | 22 | **54.98%** | **75.95** | DERIVED_OK |
| JNK | SSGA holdings xlsx | 1117 | 0 | 0.00% | — | NOT_APPLICABLE_BOND_FUND |
| VTI | SEC N-PORT | 551 | 0 | 0.00% | — | BLOCKED_WRONG_SERIES |
| EEM | — | — | — | — | — | BLOCKED |

Read the coverage column as part of the number. A look-through built from 60% of SPY's weight is a
statement about that 60%, not about SPY. Nothing here is a published fund rating.

The three derived values land within 2.5 points of each other (77.35 / 77.44 / 75.95). That is
expected, not informative: all three funds are large-cap-dominated and the 71-symbol consensus
universe is itself large-cap-dominated, so the aggregate is close to the universe average. **The
number is not the interesting part — the coverage share is.**

### BLOCKED, with exact errors

- **EEM** — `https://www.ishares.com/us/products/239637/...EEM_holdings` returned
  `HTTP 200`, `content-type: text/csv`, and a body beginning `<!DOCTYPE html>` (an interstitial, not
  CSV). `https://www.invesco.com/.../holdings/0?action=download&ticker=QQQ` returned `HTTP 406`,
  0 bytes. `https://data.sec.gov/submissions/CIK0000872664.json` returned non-JSON. No
  credential-free holdings source for EEM was verified.
- **VTI** — the newest `NPORT-P` under Vanguard CIK `0000036405` (accession `0000036405-26-000483`)
  parses to 551 positions whose names are ExlService, Six Flags, Globalstar, Tempur Sealy, Outfront
  Media. Those are small/mid caps, not VTI's constituents. Vanguard files one N-PORT per series
  under one CIK, so the newest filing for the CIK is a sibling fund. Publishing this as "VTI: 0%
  coverage" would be false, so the figure is withheld and flagged.

### Crowd layer — `out/crowd_layer.json`

- Polymarket Gamma: `HTTP 200`, 100 markets.
- Kalshi public: `HTTP 200`, 200 markets.
- **Layer A direct matches: 0.** Both venues price events, not tickers. A first draft produced four
  matches and every one was a false positive: the ticker `DE` (Deere) matched inside the Spanish
  preposition in tennis market titles. Matching is now case-sensitive uppercase-token only, and the
  honest answer is zero.
- **Layer B: 5 mappings**, each with a written transmission mechanism, expected sign and confidence.
  Beta is `null` on all five with an explicit reason; no bare correlation is emitted.
- Sample Kalshi question returned: `"Xi Jinping out before 2027?"` — illustrative of how little
  overlap exists between event markets and equity endorsement.

## Reproduce

```bash
cd 42_HARVEST_UPGRADE_2026-11-24/ghcopilot
python3 lookthrough_consensus.py --feed ../../docs/data/harvest_signals.json
python3 crowd_layer.py           --feed ../../docs/data/harvest_signals.json
```

Both write only to `./out/`. Requests are serial with a 1.1 s gap; no pagination storms.

## Files

| File | What it is |
|---|---|
| `lookthrough_consensus.py` | Holdings-weighted fund consensus; stdlib xlsx + N-PORT parsing, no third-party deps |
| `crowd_layer.py` | Polymarket/Kalshi capture, Layer A matcher, Layer B mechanism table |
| `ANALYST_SCORECARD_SPEC.md` | Event-study maths, biases, and the free-vs-paid field matrix |
| `LOOKTHROUGH.md` | Methods and limits of the fund derivation |
| `CROWD.md` | Methods and limits of the crowd layer |
| `out/*.json` | Generated outputs |

## Deliberate non-goals

No invented ratings. No proxied fill for a blocked fund. No bare correlation. No P/L figure without a
stated method, horizon, benchmark and sample size. No touching `docs/index.html` or any page outside
this directory.
