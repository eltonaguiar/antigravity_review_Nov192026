# RESULTS -- insider P vs S (repaired)

zoo-savant, 2026-11-25T01:49:20Z. Source `form4_events_wide.csv`. Cluster unit: **issuer symbol**.
Entry: **next session open after filing_date**.

## Verdict

**UNDERPOWERED at every horizon -- this is not a result.**

## Row count at every filter step

| step | rows |
|---|---|
| P officer-or-director (LITERAL) | 6 |
| P officer-or-director, excluding 10% owners (LITERAL) | 3 |
| P all | 52 |
| P officer-or-director (TRUTHY) | 48 |
| P officer-or-director, excluding 10% owners (TRUTHY) | 31 |
| S all | 927 |

The clean set is officer-or-director **and not** a 10% owner. The 10% exclusion is explicit:
large holders and entities trade for reasons unrelated to inside information.
The filter was **not** relaxed to reach a sample.

## Flag parser gap (kept visible)

Literal `lower()=='true'`: 6 officer-or-director rows. Truthy ['1', 't', 'true', 'y', 'yes']: **48**.
`is_officer` across the 52 purchases: {'0': 23, '1': 19, 'false': 9, 'true': 1}
-- the file stores both `1` and `true`, so the literal parser misses most of them.

Purchase concentration: PARA 10, UPST 10, RIVN 7, LCID 6, CVNA 3, INTC 3

## Per horizon

| H | P n | P sym | P excess | P CI (symbol) | S n | S excess | design | MDE80 | placebo p95 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 21d | 26 | 10 | 5.885% | [1.4878, 10.4291] | 847 | -7.4942% | 20.66 | 8.5965% | -5.287% | UNDERPOWERED |
| 63d | 25 | 10 | 10.6088% | [4.3317, 15.4047] | 648 | -11.4073% | 40.28 | 21.2437% | 27.8514% | UNDERPOWERED |
| 126d | 16 | 7 | 29.2019% | [-2.9293, 81.8927] | 264 | -43.7956% | 41.35 | 59.6082% | 4.8861% | UNDERPOWERED |

## What the numbers say, and what they do not

P excess exceeds S excess at every horizon (the asymmetry is in the right direction), but
the P sample is 16-26 events over 7-10 symbols, the design effect is 20-41 (so a
transaction-level CI would be meaningless), and the 80%-power MDE (8.6-59.6%) is
comparable to or larger than the measured effect. With fewer than 30 clean events per
horizon, none of these differences is distinguishable from noise.

The 2026-11-24 figure (+10.79% at 21d) is **WITHDRAWN**: it applied no role filter.

next_probe: collect more P events (the current file has 52 purchases, 31 in the clean set,
16-26 analyzable per horizon) before re-running -- no analysis change can fix an n this small.
