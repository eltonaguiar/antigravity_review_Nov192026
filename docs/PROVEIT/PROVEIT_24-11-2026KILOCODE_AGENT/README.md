
---

# Extended scenarios — $10K / $20K / $50K (2026-11-24T0350Z)

Source: `sim_2026-11-24T0350Z.json` and `paramscan_2026-11-24T0350Z.json`

## Buy-and-hold converges: above ~$10K, size stops mattering

| start | final | CAGR | maxDD | fees+spread | size effect |
|---:|---:|---:|---:|---:|---|
| $300 | $286.50 | -0.92% | -6.98% | $0.05 | granularity binds |
| $500 | $473.01 | -1.11% | -8.37% | $0.09 | granularity binds |
| $2,000 | $3,030.04 | +8.70% | -13.51% | $0.93 | granularity binds |
| $10,000 | $15,489.06 | +9.18% | -14.20% | $4.99 | granularity stops binding |
| $20,000 | $30,978.12 | +9.18% | -14.20% | $9.99 | granularity stops binding |
| $50,000 | $77,445.30 | +9.18% | -14.20% | $24.97 | granularity stops binding |

**The $10K, $20K and $50K rows return the identical 9.18%.** That is the cleanest result in this study: once whole-share granularity stops binding, account size becomes irrelevant to the return — the same portfolio is simply scaled. Every size-dependent effect lives below $10K.

## Does a bigger account make a strategy work?

| start | hold CAGR | best variant | best CAGR | edge | variants |
|---:|---:|---|---:|---:|---:|
| $300 | -0.92% | trend_200 | +0.00% | +0.92pp | 4 |
| $500 | -1.11% | tp_sl | +11.88% | +12.99pp | 4 |
| $2,000 | +8.70% | trend_200 | +9.29% | +0.59pp | 4 |
| $10,000 | +9.18% | trend_200 | +10.49% | +1.31pp | 4 |
| $20,000 | +9.18% | trend_200 | +10.60% | +1.42pp | 4 |
| $50,000 | +9.18% | trend_200 | +10.68% | +1.50pp | 4 |

The 200-day trend edge creeps up with size (+1.31 / +1.42 / +1.50pp) but stays inside the noise band, and it is the same rule family the 1000-cell sweep killed across five asset classes — **0 PASS in 47 cells, every candidate failed walk-forward**. A larger account does not fix a rule that has no out-of-sample edge; it only makes the same artefact cost more.

## Costs scale linearly, which is the one size-dependent effect that persists

TP/SL costs $44.61 at $10K, $90.23 at $20K and $226.80 at $50K and returns 9.02–9.05% — statistically indistinguishable from holding, having paid 16 trades. **Trading activity scales with capital while its edge does not.**

## Verdict across all six sizes

No account size produces an investable edge. The recommendations are unchanged from the main README: at $300–$500 the constraint is instrument choice, not strategy; from ~$2K the 60/40 becomes expressible; above ~$10K size is irrelevant and only cost and holding discipline matter.
