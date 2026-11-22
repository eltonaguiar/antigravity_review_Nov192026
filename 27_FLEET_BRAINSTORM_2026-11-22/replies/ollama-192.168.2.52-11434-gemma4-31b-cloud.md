<!-- engine=ollama host=http://192.168.2.52:11434 model=gemma4:31b-cloud http=200 chars=1422 elapsed=1.4s error=None -->

VERDICT I1 | WEAK | PBO 0.18 is too low to justify "strongest" given the high DSR 21.4.
VERDICT I2 | WEAK | OOS 38 is an insufficient sample size to claim "consistent".
VERDICT I3 | WRONG | PBO 0.676 indicates extreme overfit, contradicting the "keeper" status.
VERDICT I4 | WEAK | "70%+" is a vague range, not a precise measurement.
VERDICT I5 | WEAK | Claimed Sharpe 4.96 is unsupported without the required minute data.
VERDICT I6 | SUPPORT | Alpha -0.44% vs hold justifies the "Avoid" label.
VERDICT I7 | WEAK | No alpha-vs-benchmark provided to justify the "conservative sleeve" label.
VERDICT I8 | WEAK | No alpha-vs-benchmark provided to justify the "conservative sleeve" label.
VERDICT I9 | WRONG | PF 1.06 is nearly break-even, contradicting the "#1 quick-win" label.
VERDICT I10 | WRONG | Zero measurements provided to support any "proposed" claim.
VERDICT E1 | SUPPORT | Direction-adjusted hold is the only valid way to measure alpha.
VERDICT E2 | SUPPORT | 21.4% slice is a sampling bias that invalidates the current book.
VERDICT E3 | SUPPORT | Flat n=100 ignores the variance of the underlying effect size.
VERDICT E5 | SUPPORT | Report-only costs allow overfitted strategies to pass the gate.
MISSING | A correlation matrix across all ten strategies to detect systemic risk.
NEW | Implement a walk-forward optimization with a shrinking window for crypto.
TOP3 | E2, E1, E5 | Fix data bias, then alpha gates.