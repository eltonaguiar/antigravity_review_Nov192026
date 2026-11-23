# Panel cross-check cycles against agent claims

Running log. Each cycle puts the agents' live claims to `askpollinationsandothers` (local router aliases) and/or
`ask4ais` (browser multi-model panels), then replies on COMS with what changed. A failed source is recorded as a
result, not dropped.

---

## Cycle 1 — 2026-11-23T07:30Z

**Resources used:** `askpollinationsandothers` → router `ULTRA_FREE_CLOUD_LARGE` **[200, 18.7 s, 3,766 chars]**;
local `ollama:qwen3:8b` **[200, 74.5 s, 4,326 chars]**. Earlier in the same window: `ask4ais` →
ChatPlayground 4-panel ask on the scorer's test design (harvested into `DESIGN_REVIEW_2026-11-23.md`).

**Claims tested (all three are Kilo's live claims):**
1. *"The canonical engine's alpha gate rejects 100% of 362 cells across 69 symbols, therefore there is zero alpha
   anywhere in the estate."*
2. *"A single-symbol bucket showed a positive CI, but the broad population was negative, so the bucket was a
   selection artifact."*
3. *"One module publishes a t-statistic under the name deflated Sharpe; a second calls it canonical while deferring
   to a third that is canonical."*

### What the panel returned that matters — claim 1 is not a null result, it may be a power statement

Verbatim from the router:

> *"The gate is correctly implemented but has **near-zero power at the actual alpha magnitudes present**. If the true
> alphas are 0.1% per period and the gate requires 2% to reject, it will reject nothing while alpha exists. **The claim
> is a power statement masquerading as a null result.**"*

and the falsifying test it proposed:

> *"Run the same engine on synthetic data with a **known injected alpha** (a deterministic drift of known magnitude
> added to a random walk). If the gate fails to detect the known alpha at a rate consistent with its stated power, the
> gate is miscalibrated. Alternatively bootstrap the cell selection: if cells were selected post-hoc from a larger
> search space, the '362' may already be a filtered set, and the correct test is to apply a multiple-testing correction
> to the **original** candidate pool before the gate was applied."*

**This is a real gap in the claim as stated.** "0 of 362 cells pass" is compatible with three very different worlds:
(a) there is no alpha anywhere; (b) there is alpha but the gate cannot see it at this sample size; (c) the 362 cells
were already filtered before the gate ran. Only a **power check** separates them: inject a known alpha and confirm the
gate detects it. Kilo's claim is a statement about the gate, and needs one more measurement before it is a statement
about the market.

**Claim 2 — accepted, with the test named.** Falsification the panel gave: compare the bucket to the broader population
with a meta-analysis, and require the bucket to be a *documented subset with its selection rule stated*. This matches
what Kilo concluded independently (AUDJPY n=282 broad population, mean −0.37%) and matches the error I made myself in
the contest leaderboard (ranking on mean R from partial books).

**Claim 3 — not disputed.** The panel's ranking put the circular-deprecation claim lowest on consequence, which agrees
with Kilo's own downgrade of it to P2 once `risk_metrics` was shown to have zero importers.

**Action taken:** posted to COMS asking Kilo for the power check + whether the 362 cells are the original candidate pool
or a post-selection set.

**Failures recorded:** `ollama:qwen3:8b` answered but slowly (74.5 s); no source returned 402 this cycle.
