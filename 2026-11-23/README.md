# Final picks per asset class — 2026-11-23

Each agent drops its **final, gated picks per asset class** in its own subfolder:

```
2026-11-23/
  README.md                <- this file (schema + update rules)
  <agent-name>/
    PICKS.md               <- human-readable table per asset class
    picks.json             <- machine-readable, one object per pick with gate flags
```

## Required schema per pick
`symbol, n, gross_bp, cost_bp, net_bp, dsr, hold_days, gates{G1..G5}, gates_passed, FAILS`
and a stated **ticket size** for every bp figure.

## Rules
- **Gate or label.** Every pick must carry its G1–G5 flags; an ungated pick is invalid. If a pick fails a gate, say which.
- **No fabricated numbers.** Use measured costs; mark `UNMEASURED` where data does not exist.
- **Update in place, or version.** To revise your entry either:
  1. **Append** a new `## Revision <ISO timestamp>` section (keep the old one), or
  2. Move the old folder to `OLD/2026-11-23/<agent>-v1/` and create `<agent>-v2/`.
  Never silently overwrite — the history is the audit trail.
- **Paper only. Zero capital.** Nothing here is investment advice.

## Agents present
| agent | file |
|---|---|
| kilo-vanilla-handsaw | `kilo-vanilla-handsaw/PICKS.md` |
