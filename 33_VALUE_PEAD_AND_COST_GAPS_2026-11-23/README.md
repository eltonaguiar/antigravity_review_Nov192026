# Round 33 - the binding constraint moved from strategy to MEASUREMENT (2026-11-23)

Three agents (GitHub Copilot, Zoo Code, Kilo) worked this round on the same programme. This folder
records what they produced, what they refused to produce, and the two families (value, PEAD) that were
never measured rather than measured and rejected.

## Headline

Nothing new is INVESTABLE. The programme tally is unchanged at **0 INVESTABLE / 11 NOT_INVESTABLE /
3 UNKNOWN (14 rows)**. What changed is that the *blockers are now specific*:

1. **HML (value) may be unrunnable on this repo's data** - it needs book equity and shares outstanding;
   `data/earnings/c7/` holds four quarterly EPS records and no fundamentals at all.
2. **The repo's Questrade cost model is wrong by ~30x** - it applies the 1.75% FX conversion spread
   *per trade*, making every US equity trade cost 175 bp. Slippage and spread are hardcoded guesses.
3. **Large-cap PEAD is dead and three independent models agree** - so the PEAD infrastructure, if
   large-cap and post-2006, should be expected to produce a null. A null is the finding, not a failure.

## Files

| File | What it holds |
|---|---|
| `2026-11-23-value-vs-pead-cross-model-evidence.md` | Three free models, same prompt, no shared numbers - and a 2x disagreement on the value premium |
| `2026-11-23-equity-cost-blocker.md` | Copilot's audit of the Questrade model and the missing fundamentals store |
| `2026-11-23-parity-and-provenance.md` | Kilo's parity items 1-3 (measured, mostly no-op) and Zoo Code's provenance/push record |
| `2026-11-23-open-pr-backlog.md` | Five open PRs on the main repo, four of them `mergeable: UNKNOWN` |
