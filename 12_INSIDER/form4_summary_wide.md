# Form 4 collection summary

- generated: 2026-11-24
- tickers requested: 22  (unresolved: 0)
- distinct issuers with events: 22
- total transaction rows: 2640

## Rows by transaction code

| S | 927 | open-market sale (the CONTROL) |
| A | 609 | grant/award |
| M | 506 | option exercise |
| F | 468 | tax withholding |
| P | 52 | open-market purchase (the EVENT) |
| G | 32 | gift |
| C | 23 | conversion |
| J | 18 | other |
| X | 3 |  |
| H | 1 |  |
| D | 1 | disposition |

## Filing lag (business days, filing_date - transaction_date)

- median: 2
- p95: 3
- n with valid lag: 2640

A p95 above ~2 business days means the pipeline is reading a later date than the legal filing deadline, which is a look-ahead risk. Form 4 is due within 2 business days.

## Event counts for the probe

- code P (purchases): 52
- code P after officer-or-director filter: 48
- code S (sales, control): 927
