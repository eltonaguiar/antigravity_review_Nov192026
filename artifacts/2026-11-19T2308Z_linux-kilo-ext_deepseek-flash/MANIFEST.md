# Snapshot manifest — linux / kilo extension / deepseek-flash

- **Captured:** 2026-11-19T23:08Z
- **OS / agent:** Linux (`gx10-c9b9`) / Kilo extension / deepseek-flash
- **COMS seat:** `inbox/gx10-c9b9/vanilla-handsaw/kilo`
- **Source repo:** `eltonaguiar/findtorontoevents_antigravity.ca` @ main (all commits below are merged)
- **Conflict-free path:** everything I wrote lives in this folder, so parallel agents can read it without touching their own subfolders.

## What is here

| File | What it answers |
|---|---|
| `FINDINGS_MEASURED.md` | measured diagnosis of the financial-prediction system |
| `EVIDENCE_INDEX.md` | every claim → file → key path/value |
| `AUDIT_SURFACES_FULL_REVIEW_2026-11-19.md` | every section of /audit, /audit2, /audit3 + metric glossary |
| `WHAT_WORKS_PER_ASSET_CLASS.md` | per-class evidence review with A–D grades and sources |
| `ALLOCATION_2000_AND_LIVE_SIM_PLAN.md` | $2k = 90/0/10, friction math, sleeve architecture |
| `REAL_MONEY_READINESS_AND_PEER_FRAMEWORK.md` | honest readiness + the 5-test review framework |
| `NEXT_PHASE_PLAN.md` | measurement-integrity-first workstreams and owners |
| `DESIGN_DEBATE.md` | 16 elements, votes, my positions and falsifiers |
| `COMS_REVIEW_FEEDBACK.md` | per-entry response to every peer message |
| `WORK_PRESERVATION_AND_MERGE_POLICY.md` | backups, merge gate, incident post-mortem |
| `VOLUME_CONTEXT_APPROACH.md` | sidecar vs ALTER for volume context |
| `AUDIT2_VS_AUDIT3.md` | which surface is closer to money-ready, and which class |
| `VERIFICATION_P0P1.md` | verification of the P0/P1 correctness commit |
| `FEEDBACK_ON_CROSS_AGENT_PLAN.md` | review of the copilot money-maker plan |
| `README.md` | index of the older `10_KILO_VANILLA_HANDSAW` folder |

## Commits behind this snapshot (all on findtorontoevents main)

```
6abfa22364e G9 alpha at strategy scope, global DSR floor, family gates, forward ingest
1189ff4150d provenance triple on every rendered number
260df7f980f DSR trial counts on every bucket
1a36da257e2 unmatched-strategy diagnostics in the forward ingest
485b4e7c1b5 growth watchdog
ff884c4cb37 per-hypothesis watchdog + pod grace
33e41deca65 CANDIDATE falls back to global DSR
1238e16d086 four falsifier tests
6448b582fe0 core-beta sleeve live
57c1c0d11d2 ETF rotation + random control + daily marks
4ec5fd7089f sleeve aligned to the validated TAA spec
79b5de2be3f 9-month lag-1d thesis + exact-ETF test
032d88897d1 gitleaks gate re-enabled (P0)
8aee6f084fd volume_ratio migration + dry-run backfiller
5a26f9ac52b work-preservation policy + backup script
```

## Verify (one command each)

```bash
# 157 tests
python3 -m pytest tests/test_audit3_tribunal.py tests/test_audit3_expectancy_gates.py \
  tests/test_audit3_edge_hunt.py tests/test_audit3_selection_alpha.py \
  tests/test_forward_observations_ingest.py tests/test_audit3_cost_basis.py \
  tests/test_paper_sleeves.py tests/test_sleeve_daily_summary.py \
  tests/test_forward_growth_watchdog.py tests/test_audit3_falsifiers.py \
  tests/test_volume_ratio.py -q

# live provenance + DSR trials
curl -s https://findtorontoevents.ca/audit3/audit3_ledger.json | python3 -c \
 "import json,sys;d=json.load(sys.stdin);p=d['provenance'];c=d['cells'][0];\
print(p['id'],p['population'],c.get('dsr_n_trials'),c.get('provenance_id')==p['id'])"
```

## Status at capture

- Live ledger `22:47:15Z`, provenance `f323cc17d6fa8d1d`, canonical, 8,632 scored,
  **0 PROVEN / 0 CANDIDATE / 59 WEAK / 8 KILL / 292 INSUFFICIENT**, alpha **−0.2744**.
- My worktree clean; nothing uncommitted.
- **Not mine / not touched:** the restored WIP in `.kilo/worktrees/vanilla-handsaw`,
  PR #965, Windows code, COMS client.
- Open blockers: B1 emitter (pod has 0 forward rows), P0 credential branch still live,
  volume `--apply` awaiting approval.
