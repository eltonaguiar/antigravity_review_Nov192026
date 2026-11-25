# Insider P vs S -- repaired after audit

zoo-savant, 2026-11-25T01:49:20Z. Source `form4_events_wide.csv`.

**This supersedes the 2026-11-24 result, which is WITHDRAWN:** it applied no role
filter (the parsed flags were never read) and used a literal `=='true'` parser that
misses the `1` values the file stores.

## Filter steps (row counts)

| step | rows |
|---|---|
| P officer-or-director (LITERAL) | 6 |
| P officer-or-director, excluding 10% owners (LITERAL) | 3 |
| P all | 52 |
| P officer-or-director (TRUTHY) | 48 |
| P officer-or-director, excluding 10% owners (TRUTHY) | 31 |
| S all (control) | 927 |

**Purchase concentration:** PARA 10, UPST 10, RIVN 7, LCID 6, CVNA 3, INTC 3

## Per horizon

| H | P n | P sym | P excess | P CI (symbol) | S n | S excess | design | MDE80 | placebo p95 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 21d | 26 | 10 | 5.885% | [1.4878, 10.4291] | 847 | -7.4942% | 20.66 | 8.5965% | -5.287% | UNDERPOWERED |
| 63d | 25 | 10 | 10.6088% | [4.3317, 15.4047] | 648 | -11.4073% | 40.28 | 21.2437% | 27.8514% | UNDERPOWERED |
| 126d | 16 | 7 | 29.2019% | [-2.9293, 81.8927] | 264 | -43.7956% | 41.35 | 59.6082% | 4.8861% | UNDERPOWERED |

The clean set (31 events) is large enough to report.
The filter was not relaxed to reach a sample.
