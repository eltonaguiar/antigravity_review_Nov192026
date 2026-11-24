# DSR_CORRECT proof -- pure noise must get HARSHER as N grows

Each trial is 1000 iid N(0,1) draws, so the TRUE Sharpe is 0. N trials per row, 5 seeds, DSR averaged across seeds.

| N | E[max] | mean DSR | min | max | reading |
|---|---|---|---|---|---|
| 10 | 1.5746 | 0.5854 | 0.0000 | 1.0000 | near chance |
| 30 | 2.0734 | 0.4331 | 0.0000 | 1.0000 | near chance |
| 100 | 2.5306 | 0.5595 | 0.0000 | 1.0000 | near chance |
| 300 | 2.8955 | 0.5926 | 0.0000 | 1.0000 | near chance |
| 1000 | 3.2551 | 0.7364 | 0.0094 | 1.0000 | near chance |
| 2000 | 3.4473 | 0.6938 | 0.0193 | 1.0000 | near chance |

**Monotone non-increasing in N: False**
**DSR at N=10: 0.5854**
**DSR at N=2000: 0.6938**
