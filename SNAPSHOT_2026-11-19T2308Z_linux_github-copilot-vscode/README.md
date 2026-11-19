# Snapshot — GitHub Copilot (VS Code/CLI) · linux · gx10-c9b9 · 2026-11-19T23:08Z

**Agent:** GitHub Copilot (VS Code), COMS seat `copilot-cli-moneyresearch`
**OS/host:** linux / gx10-c9b9 · worktree `.kilo/worktrees/moneyresearch`
**Status at capture:** done-sharing: YES (rollcall 23:01Z answered); worktree clean; all work merged or in open PRs.

## What this folder contains (all MINE — conflict-free by construction)

| Dir | Contents |
|---|---|
| `reports/` | money_maker_per_asset_class (research + $2k verdict), TAA_LAGGED_REPRODUCTION (.md + full .json grid) |
| `docs/` | debate position (votes 7/8/9 + addendum), cross-check request (attack surface), original PLAN, external edge research (cited), updates fix-doc, buffy's peer review of my plan (context) |
| `code/` | review copies of: crypto_intraday_sim.py (3 pre-registered paper slots + guardrails + cost floor + forming-bar fix), pilot_forward_bridge.py, crypto_bars.py (failover chain), taa_lagged_reproduction.py (the written lag spec), etf_dual_momentum_pilot.py (monthly segment closes), agent_worktree_snapshot.sh (P2 backup tool, PR #969) |
| `tests/` | test_crypto_intraday_sim.py (18 cases) |
| `session/` | plan.md (session plan incl. execution status), watch_log.md (20-min monitor digests) |

## Source of truth (main repo eltonaguiar/findtorontoevents_antigravity.ca)

- **Merged:** PR #959 (sleeve audit3 cross-mark + sim + bridge), #962 (TAA lagged reproduction), #964 (debate position + forming-bar fix + round-2 cross-check).
- **Open:** PR #969 (snapshot tool), PR #968 (buffy findings preservation, opened on their behalf).
- Key commits: ee8e18d853a, c11f796dd3f, 45dc5c25105, 017b66cf0dc. Backup ref: `backup/copilot-cli-moneyresearch/20261119T225306Z`.

## Verify commands

```bash
python3 -m pytest tests/test_crypto_intraday_sim.py -q        # 18 passed
python3 tools/taa_lagged_reproduction.py                      # reproduces the lag grid
python3 tools/pilot_forward_bridge.py --json                  # dry-run, idempotent
```

## Headline findings (as of capture)

1. 0/359 tribunal cells proven; CRYPTO+COMMODITY KILL; selection alpha −0.27%/trade (CI excl. 0).
2. /audit headline sleeves (PF 10–12) were post-hoc MySQL selection, never tribunal-scored → UNVERIFIED badge shipped.
3. TAA: headline 0.89/−19.1 was unlagged; 1-day lag 0.82 vs SPY 0.69 (MDD −20.9 vs −52.9) — drawdown control, not edge; buffy accepted.
4. $2k: low-fee index beta (FXAIX/FSKAX/SWPPX, $0 min) ≻ everything we generate; penny/sub-$5 = strongest NO (own ledger + Kumar 2009 −7.1%/yr).
5. Live paper sim on 30-min cron with prop-firm guardrails + per-class cost floor; promotion gated by audit3 forward rules (n≥100, PF CI-LB>1.0).

## Explicitly NOT mine (do not attribute)

kilo's tribunal/gate stack, provenance, watchdogs, TODO sweep (#965 / clean branch); buffy's settle sweep + capital doc; opencode's P0 security find (I only verified it); the audit3/audit2 pages themselves.
