# Findings — Measured verdicts (audit3 ledger, 2026-11-19 06:11 UTC)

Source: `audit_dashboard/data/audit3_ledger.json` (schema `audit3.v1`, generated
2026-11-19T06:11Z, source `/tmp/audit3/dashboard_data.json` generated 04:04Z).

## Headline

| Metric | Value |
|---|---|
| `n_rows` (scored) | 3,500 |
| `n_cells_tested` | 45 |
| `n_cells_total` | 171 |
| `n_confirmatory_cells` | 8 |
| `n_discovery_cells` | 163 |
| `n_proven` | **0** |
| `n_candidate` | **1** |
| `n_weak` | 34 |
| `n_kill` | 10 |
| `n_insufficient` | 126 |
| `kill_rate_pct` | 22.22 |
| `n_proven_symbols` | 0 |
| `n_kill_symbols` | 11 |
| `n_kill_classes` | 2 |
| `n_segment_cells` | 65 (`n_positive_segments` = 4, `n_harmful_segments` = 23) |

## The single candidate cell

```
assembly_class   CRYPTO
strategy        luxalgo_confluence
direction       SHORT
namespace       discovery        ← cannot promote from here
n               476
wr              0.5441   Wilson [0.4992, 0.5883]
pf              1.6105
net_expectancy  +0.7182%   CI [ +0.4022, +1.0143 ]   (2× slippage CI [+0.3022, +0.9143], ok)
p_value         0.0005
q_value         0.0065
dsr             0.9893
split_half      stable: +0.3917 → +1.0448
top_symbol_share 0.1008
top_source_share 0.9769  ← single source 98%
verdict         CANDIDATE
reasons         single source 98%; discovery namespace (needs pre-registered pod)
```

It is the strongest positive cell — and it is barred by (a) `single_source` 98% and
(b) being in `discovery`, not `confirmatory`. Both are correct discipline. It simply means
nothing can be promoted today.

## KILL tribunal (criteria)

`['net expectancy 95% CI entirely < 0', 'BH harm q <= 0.1 across killed cells', 'PF < 0.8 at n >= 50 is a WATCH flag', 'WR < 40% (diagnostic)']`

Sample kills: `luxalgo_confluence` CRYPTO LONG (n=754, WR 36.2%, PF 0.82, net −0.28%,
q=1.0), plus 10 strategies / 11 symbols / 2 classes.

## Class context (from evidence & earlier review)

- CRYPTO class aggregate: KILL (n=1,851, net −0.51%).
- EQUITY: WR 59–60% but PF 0.94 (net-negative) — the "WR but no PF" signature.
- Trend cells (WR ~35%, RR 2.5) can never pass G1 regardless of expectancy.
- `luxalgo_confluence SHORT` (the candidate) needs a BTC-regression + funding covariates
  and a second independent source; if its PnL correlates ≈ −0.8 with BTC it is short-beta,
  not alpha.
- `mega_mutation` family: n=19, WR 73.7%, PF 3.65 — INSUFFICIENT_N today; register as a
  hypothesis, observe, don't trade.
